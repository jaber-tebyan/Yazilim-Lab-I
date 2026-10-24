"""Shared command execution engine.

The engine is the only place that connects a parsed command to the rule layer,
the state-mutating interface functions and the result models. It deliberately
does not read or write files: callers (CLI, desktop app, tests) own all I/O.
"""

from yazilim_lab_project.interface import (
    AddResource,
    AddUser,
    generate_reservation_id,
    get_user,
)
from yazilim_lab_project.interface.clock import advance_clock
from yazilim_lab_project.interface.price import get_price
from yazilim_lab_project.interface.reservation import (
    cancel_reservation,
    entry_reservation,
    exit_reservation,
)
from yazilim_lab_project.interface.waiting import add_waiting_entry
from yazilim_lab_project.models import AnyResult, reservation
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import (
    AddResourceCommand,
    AddUserCommand,
    AnyCommand,
    CancelCommand,
    ClockCommand,
    EntryCommand,
    ExitCommand,
    PackageCommand,
    PriceCommand,
    QueryResourceCommand,
    QueryUserCommand,
    ReservationCommand,
    WaitingCommand,
)
from yazilim_lab_project.models.generic import Err, Ok
from yazilim_lab_project.models.initial_data import Resource, User
from yazilim_lab_project.models.reservation import Reservation
from yazilim_lab_project.models.results import (
    AddResourceResult,
    AddUserResult,
    CancelResult,
    ClockResult,
    EntryResult,
    ExitResult,
    PackageResult,
    PriceResult,
    QueryResult,
    ReservationResult,
    WaitingResult,
)
from yazilim_lab_project.rules.add_resource_rules import all_rules_resource_add
from yazilim_lab_project.rules.add_user_rules import all_rules_user_add
from yazilim_lab_project.rules.cancel_rules import all_rules_cancel
from yazilim_lab_project.rules.clock_rules import all_rules_clock
from yazilim_lab_project.rules.entry_rules import all_rules_entry
from yazilim_lab_project.rules.exit_rules import all_rules_exit
from yazilim_lab_project.rules.package_rules import all_rules_package
from yazilim_lab_project.rules.price_rules import all_rules_price
from yazilim_lab_project.rules.query_resource_rules import all_rules_query_resource
from yazilim_lab_project.rules.query_user_rules import all_rules_query_user
from yazilim_lab_project.rules.reservation_rules import all_rules_reservation
from yazilim_lab_project.rules.waiting_rules import all_rules_waiting


def _next_package_id(state: AppState) -> str:
    """Return the next free package id.

    Package ids are derived from the state instead of an engine counter so a
    fresh engine created around an existing state cannot reuse an id.
    """
    numbers = [
        int(res.package[1:])
        for res in state.reservations
        if res.package is not None
        and res.package.startswith("p")
        and res.package[1:].isdigit()
    ]
    return f"p{max(numbers, default=0) + 1}"


class Engine:
    """Execute commands against one in-memory :class:`AppState`."""

    def __init__(self, state: AppState) -> None:
        self.state = state
        self._history: list[tuple[AnyCommand, AnyResult]] = []

    @property
    def history(self) -> list[tuple[AnyCommand, AnyResult]]:
        """Executed commands and their results, in execution order."""
        return self._history

    def execute(self, cmd: AnyCommand, *, record: bool = True) -> AnyResult:
        """Run one command and return its result.

        ``record=False`` is for calls that are not part of the session log,
        such as a price preview. Such results get ``no=0``.
        """
        no = len(self._history) + 1 if record else 0
        result = self._dispatch(cmd, no)
        if record:
            self._history.append((cmd, result))
        return result

    def _dispatch(self, cmd: AnyCommand, no: int) -> AnyResult:
        match cmd:
            case AddUserCommand():
                return self._add_user(cmd, no)
            case AddResourceCommand():
                return self._add_resource(cmd, no)
            case ReservationCommand():
                return self._reserve(cmd, no)
            case PriceCommand():
                return self._price(cmd, no)
            case PackageCommand():
                return self._package(cmd, no)
            case WaitingCommand():
                return self._wait(cmd, no)
            case ClockCommand():
                return self._clock(cmd, no)
            case EntryCommand():
                return self._entry(cmd, no)
            case ExitCommand():
                return self._exit(cmd, no)
            case CancelCommand():
                return self._cancel(cmd, no)
            case QueryUserCommand():
                return self._query_user(cmd, no)
            case QueryResourceCommand():
                return self._query_resource(cmd, no)
            case _:
                raise TypeError(f"Unsupported command type: {type(cmd).__name__}")

    def _add_user(self, cmd: AddUserCommand, no: int) -> AddUserResult.Any:
        error = all_rules_user_add(cmd, self.state)
        if error is not None:
            return AddUserResult.new(no, error)

        AddUser(
            self.state,
            User(
                id=cmd.id,
                name=cmd.name,
                role=cmd.role,
                certificates=cmd.certificates,
                balance=cmd.balance,
                reliability=cmd.reliability,
            ),
        )
        return AddUserResult.new(no)

    def _add_resource(
        self, cmd: AddResourceCommand, no: int
    ) -> AddResourceResult.Any:
        error = all_rules_resource_add(cmd, self.state)
        if error is not None:
            return AddResourceResult.new(no, error)

        AddResource(
            self.state,
            Resource(
                id=cmd.id,
                name=cmd.name,
                type=cmd.type,
                allowed_roles=cmd.allowed_roles,
            ),
        )
        return AddResourceResult.new(no)

    def _reserve(
        self, cmd: ReservationCommand, no: int
    ) -> ReservationResult.Any:
        rule_result = all_rules_reservation(cmd, self.state)

        match rule_result:
            case Err(error):
                return ReservationResult.Red(no=no, error_code=error)
            case Ok((price, balance)):
                get_user(self.state, cmd.user).balance = balance
                reservation_id = generate_reservation_id(self.state)

                self.state.reservations.append(
                    Reservation(
                        id=reservation_id,
                        user=cmd.user,
                        resource=cmd.resource,
                        start=cmd.start,
                        end=cmd.end,
                        price=price,
                        state=reservation.State.APPROVED,
                        package=None,
                    )
                )
                return ReservationResult.Ok(
                    no=no,
                    reservation_id=reservation_id,
                    price=price,
                    balance=balance,
                )

    def _price(self, cmd: PriceCommand, no: int) -> PriceResult.Any:
        error = all_rules_price(cmd, self.state)
        if error is not None:
            return PriceResult.Red(no=no, error_code=error)

        return PriceResult.Ok(no=no, price=get_price(cmd, self.state))

    def _package(self, cmd: PackageCommand, no: int) -> PackageResult.Any:
        rule_result = all_rules_package(cmd, self.state)

        match rule_result:
            case Err((error, items)):
                return PackageResult.Red(no=no, error_code=error, items=items)
            case Ok((prices, total)):
                user = get_user(self.state, cmd.user)
                user.balance -= total
                package_id = _next_package_id(self.state)
                reservation_ids: list[str] = []

                for index, item in enumerate(cmd.items):
                    reservation_id = generate_reservation_id(self.state)
                    self.state.reservations.append(
                        Reservation(
                            id=reservation_id,
                            user=cmd.user,
                            resource=item.resource,
                            start=item.start,
                            end=item.end,
                            price=prices[index],
                            state=reservation.State.APPROVED,
                            package=package_id,
                        )
                    )
                    reservation_ids.append(reservation_id)

                return PackageResult.Ok(
                    no=no,
                    package_id=package_id,
                    reservations=reservation_ids,
                    prices=prices,
                    total=total,
                    balance=user.balance,
                )

    def _wait(self, cmd: WaitingCommand, no: int) -> WaitingResult.Any:
        rule_result = all_rules_waiting(cmd, self.state)

        match rule_result:
            case Err(error):
                return WaitingResult.Red(no=no, error_code=error)
            case Ok(data):
                add_waiting_entry(self.state, data.entry)
                return WaitingResult.Ok(
                    no=no,
                    waitlist_id=data.waitlist_id,
                    position=data.position,
                )

    def _clock(self, cmd: ClockCommand, no: int) -> ClockResult.Any:
        rule_result = all_rules_clock(cmd, self.state)

        match rule_result:
            case Err(error):
                return ClockResult.Red(no=no, error_code=error)
            case Ok(new_time):
                events = advance_clock(self.state, new_time)
                return ClockResult.Ok(no=no, events=events)

    def _entry(self, cmd: EntryCommand, no: int) -> EntryResult.Any:
        rule_result = all_rules_entry(cmd, self.state)

        match rule_result:
            case Err(error):
                return EntryResult.Red(no=no, error_code=error)
            case Ok(res):
                entry_reservation(res)
                return EntryResult.Ok(no=no, new_status=res.state)

    def _exit(self, cmd: ExitCommand, no: int) -> ExitResult.Any:
        rule_result = all_rules_exit(cmd, self.state)

        match rule_result:
            case Err(error):
                return ExitResult.Red(no=no, error_code=error)
            case Ok((res, new_reliability)):
                events = exit_reservation(res, self.state, new_reliability)
                return ExitResult.Ok(
                    no=no,
                    new_status=res.state,
                    reliability=new_reliability,
                    events=events,
                )

    def _cancel(self, cmd: CancelCommand, no: int) -> CancelResult.Any:
        rule_result = all_rules_cancel(cmd, self.state)

        match rule_result:
            case Err(error):
                return CancelResult.Red(no=no, error_code=error)
            case Ok(cancel_data):
                events = cancel_reservation(
                    cancel_data.reservation, self.state, cancel_data
                )
                return CancelResult.Ok(
                    no=no,
                    refund=cancel_data.actual_refund,
                    balance=cancel_data.new_balance,
                    reliability=cancel_data.new_reliability,
                    events=events,
                )

    def _query_user(self, cmd: QueryUserCommand, no: int) -> QueryResult.Any:
        rule_result = all_rules_query_user(cmd, self.state)

        match rule_result:
            case Err(error):
                return QueryResult.Red(no=no, error_code=error)
            case Ok(data):
                return QueryResult.OkUser(
                    no=no,
                    balance=data.balance,
                    reliability=data.reliability,
                    reservations=data.reservations,
                )

    def _query_resource(
        self, cmd: QueryResourceCommand, no: int
    ) -> QueryResult.Any:
        rule_result = all_rules_query_resource(cmd, self.state)

        match rule_result:
            case Err(error):
                return QueryResult.Red(no=no, error_code=error)
            case Ok(occupancy):
                return QueryResult.OkResource(no=no, occupancy=occupancy)
