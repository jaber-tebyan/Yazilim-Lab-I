import math
from datetime import timedelta
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from yazilim_lab_project.models import reservation
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import CancelCommand
from yazilim_lab_project.models.generic import Err, Ok, Result
from yazilim_lab_project.models.reservation import Reservation
from yazilim_lab_project.models.results import CancelResult


class CancelData(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)
    reservation: Reservation
    actual_refund: int = Field(validation_alias="iade", serialization_alias="iade")
    new_balance: int = Field(
        validation_alias="bakiye", serialization_alias="bakiye"
    )
    new_reliability: int = Field(
        validation_alias="guvenilirlik", serialization_alias="guvenilirlik"
    )


# Reservation not found
def rule_cancel_not_found(cmd: CancelCommand, state: AppState) -> bool:
    return not any(r.id == cmd.reservation for r in state.reservations)


# Reservation is not in APPROVED state
def rule_cancel_state_error(res: Reservation) -> bool:
    return res.state != reservation.State.APPROVED


def all_rules_cancel(
    cmd: CancelCommand, state: AppState
) -> Result[CancelData, CancelResult.Error]:
    if rule_cancel_not_found(cmd, state):
        return Err(CancelResult.Error.NOT_FOUND)

    res = next(r for r in state.reservations if r.id == cmd.reservation)

    if rule_cancel_state_error(res):
        return Err(CancelResult.Error.STATE_ERROR)

    user = next(u for u in state.config.users if u.id == res.user)
    role = state.config.roles[user.role]

    remaining_time = res.start - state.config.time

    if remaining_time >= timedelta(hours=24):
        refund_amount = res.price
        new_reliability = user.reliability
    elif remaining_time >= timedelta(hours=2):
        refund_amount = math.floor(res.price * 0.5)
        new_reliability = user.reliability
    else:
        refund_amount = 0
        new_reliability = max(0, user.reliability - 5)

    # Balance cannot exceed role's weekly quota and cannot go below current balance if above quota
    new_balance = max(user.balance, min(role.weekly_quota, user.balance + refund_amount))
    actual_refund = max(0, new_balance - user.balance)

    return Ok(
        CancelData(
            reservation=res,
            actual_refund=actual_refund,
            new_balance=new_balance,
            new_reliability=new_reliability,
        )
    )
