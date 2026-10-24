"""Clock orchestration (K11).

Advances the simulated clock and processes every event that occurs in the
interval, in chronological order.
"""

import heapq
from dataclasses import dataclass
from datetime import datetime, timedelta
from itertools import count

from yazilim_lab_project.interface.reservation import (
    exit_reservation,
    no_show_reservation,
)
from yazilim_lab_project.interface.waiting import process_waiting_list_for_resource
from yazilim_lab_project.models import reservation
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.event import (
    AutoAssign,
    Completed,
    Event,
    NoShow,
    WeeklyReset,
)
from yazilim_lab_project.models.reservation import Reservation

# Grace period: a reservation is a no-show 15 minutes after its start (K8).
NO_SHOW_GRACE = timedelta(minutes=15)

# K11 same-instant ordering: weekly -> completed -> no-show.
PRIORITY_WEEKLY, PRIORITY_COMPLETED, PRIORITY_NOSHOW = 0, 1, 2


@dataclass(frozen=True)
class _Job:
    """One thing that must happen at one instant.

    Kept as a plain record so collection can describe *what and when* without
    mutating anything. The reservation is optional because a weekly reset is
    not attached to any reservation.
    """

    time: datetime
    priority: int
    kind: str
    reservation: Reservation | None = None


def _reservation_order(res: Reservation | None) -> int:
    # IDs look like "r10". Parsing to int avoids lexicographic ordering where
    # "r10" would sort before "r2". Weekly jobs have no reservation, so 0.
    return int(res.id.removeprefix("r")) if res else 0


def _user(state: AppState, user_id: str):
    return next(u for u in state.config.users if u.id == user_id)


def _weekly_reset_times(old: datetime, new: datetime) -> list[datetime]:
    # Start from the midnight after `old`: events at `old` itself were already
    # handled by a previous advance, and re-processing them would repeat the
    # reset. Walk day by day and keep only Mondays (K11 weekly boundary).
    day = old.replace(hour=0, minute=0, second=0, microsecond=0)
    if day <= old:
        day += timedelta(days=1)

    times = []
    while day <= new:
        if day.weekday() == 0:  # Monday
            times.append(day)
        day += timedelta(days=1)
    return times


def _collect_jobs(state: AppState, old: datetime, new: datetime) -> list[_Job]:
    # One sweep over everything that *could* produce an event, producing a
    # sorted list of jobs. Collecting first (instead of mutating while we walk)
    # means the decisions are made against one consistent snapshot, and the
    # sort happens once instead of per-trigger-time.
    jobs = [_Job(t, PRIORITY_WEEKLY, "weekly") for t in _weekly_reset_times(old, new)]

    for res in state.reservations:
        # Only IN_USE reservations can *complete*; an approved-but-never-entered
        # one is handled below as a no-show. Using `old < end <= new` excludes
        # ends already handled before this advance and includes one exactly at
        # the new time (K11: "tam yeni saatte gerçekleşen olay da dahildir").
        if res.state == reservation.State.IN_USE and old < res.end <= new:
            jobs.append(_Job(res.end, PRIORITY_COMPLETED, "completed", res))

        # Only APPROVED reservations can *no-show*. IN_USE means they showed up;
        # CANCELLED/no-show already reached a terminal state, so re-checking
        # them would double-penalise reliability.
        elif res.state == reservation.State.APPROVED:
            no_show = res.start + NO_SHOW_GRACE
            if old < no_show <= new:
                jobs.append(_Job(no_show, PRIORITY_NOSHOW, "noshow", res))

    # Sort by time first, then K11 priority, then reservation number ascending
    # ("rezervasyon numarası küçükten büyüğe"). Sorting once here means the
    # processing loop can just consume the list in order.
    jobs.sort(key=lambda j: (j.time, j.priority, _reservation_order(j.reservation)))
    return jobs


def _apply_weekly_reset(state: AppState, t: datetime) -> WeeklyReset:
    # Set to the quota, do not add it: unused allowance must not carry over
    # ("Kullanılmayan KP sonraki haftaya aktarılmaz"). Adding would let users
    # bank unlimited credit.
    for user in state.config.users:
        user.balance = state.config.roles[user.role].weekly_quota
    return WeeklyReset(time=t)


def _apply_completion(state: AppState, res: Reservation, t: datetime) -> Completed:
    user = _user(state, res.user)
    # Delegate the actual state change to the shared interface function so the
    # clock and the exit command cannot develop two different definitions of
    # "completed". +2 is capped so reliability never exceeds 100.
    exit_reservation(res, state, min(100, user.reliability + 2), scan=False)
    # Read back from the user so the event reports the value the interface
    # actually applied, not a second copy of the formula.
    return Completed(
        time=t, reservation=res.id, user=res.user, reliability=user.reliability
    )


def _apply_no_show(state: AppState, res: Reservation, t: datetime) -> NoShow:
    user = _user(state, res.user)
    # Same principle: the penalty lives in no_show_reservation, not here.
    # Reading the user afterwards keeps the event consistent with the state.
    no_show_reservation(res, state)
    return NoShow(
        time=t, reservation=res.id, user=res.user, reliability=user.reliability
    )


def _apply_auto_assign(state: AppState, resources: list[str]) -> list[AutoAssign]:
    # Deduplicate while preserving first-seen order. If two no-shows in the same
    # instant free the same resource, scanning it twice could promote two people
    # into overlapping slots.
    events: list[AutoAssign] = []
    for resource in dict.fromkeys(resources):
        events.extend(process_waiting_list_for_resource(state, resource))
    return events


def advance_clock(state: AppState, new_time: datetime) -> list[Event]:
    """Advance the simulated clock to ``new_time`` and process all events.

    Returns the events in ``(old_time, new_time]``, each stamped with its own
    occurrence time, in processing order.
    """
    # Refuse backwards movement. Undoing completed/no-show/reset transitions
    # would require records we don't keep, so this must never proceed.
    if new_time < state.config.time:
        return []

    old_time = state.config.time
    events: list[Event] = []

    # A heap keyed by (time, priority, sequence) so events are always popped in
    # chronological order, with K11's priority breaking ties. The sequence is a
    # tie-break that keeps equal (time, priority) jobs in the order they were
    # collected, and stops heapq from ever comparing Reservation objects.
    heap: list[tuple[datetime, int, int, str, Reservation | None]] = []
    sequence = count()

    for job in _collect_jobs(state, old_time, new_time):
        heapq.heappush(
            heap, (job.time, job.priority, next(sequence), job.kind, job.reservation)
        )

    while heap and heap[0][0] <= new_time:
        t = heap[0][0]
        # Move the simulated clock to this instant *before* applying anything:
        # the waitlist scan timestamps its events from the clock and filters
        # expired entries against it. A stale clock would give wrong timestamps
        # and wrong eligibility.
        state.config.time = t
        freed: list[str] = []

        # Drain every job at this instant. Heap order gives weekly -> completed
        # -> no-show, so the waitlist scan below sees slots already freed.
        while heap and heap[0][0] == t:
            _, _, _, kind, res = heapq.heappop(heap)
            if kind == "weekly":
                events.append(_apply_weekly_reset(state, t))
            elif kind == "completed":
                events.append(_apply_completion(state, res, t))
            else:
                events.append(_apply_no_show(state, res, t))
                freed.append(res.resource)

        # Auto-assignment only exists because a slot just freed, so it runs
        # after the whole instant. Any reservation it creates did not exist
        # during _collect_jobs, so put its own no-show back into the timeline:
        # that no-show may still fall inside this same advance window.
        before = len(state.reservations)
        events.extend(_apply_auto_assign(state, freed))

        for res in state.reservations[before:]:
            no_show = res.start + NO_SHOW_GRACE
            # start >= t (the scan drops stale entries), so no_show > t always.
            if no_show <= new_time:
                heapq.heappush(
                    heap,
                    (no_show, PRIORITY_NOSHOW, next(sequence), "noshow", res),
                )

    # Drop entries whose start has already passed; leaving them would let stale
    # requests linger and be re-evaluated in a later advance.
    state.waiting_list = [w for w in state.waiting_list if w.start >= new_time]

    # The clock finally lands on the requested time. Events were already stamped
    # with their own occurrence time, so this is only the clock's final position.
    state.config.time = new_time
    return events
