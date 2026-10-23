from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import QueryUserCommand
from yazilim_lab_project.models.generic import Err, Ok, Result
from yazilim_lab_project.models.results import QueryResult


class QueryUserData(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)
    balance: int = Field(validation_alias="bakiye", serialization_alias="bakiye")
    reliability: int = Field(
        validation_alias="guvenilirlik", serialization_alias="guvenilirlik"
    )
    reservations: list[QueryResult.ReservationRow] = Field(
        default_factory=list,
        validation_alias="rezervasyonlar",
        serialization_alias="rezervasyonlar",
    )


def rule_query_user_not_found(
    cmd: QueryUserCommand, state: AppState
) -> QueryUserData | None:
    """Find user, Get sorted reservations that are put in by this user by their reserved time then their ID,
    Lastly return all these datas
    """
    user = next((user for user in state.config.users if user.id == cmd.id), None)
    if user is None:
        return None
    rows = sorted(
        (r for r in state.reservations if r.user == user.id),
        key=lambda r: (r.start, r.id),
    )
    return QueryUserData(
        balance=user.balance,
        reliability=user.reliability,
        reservations=[
            QueryResult.ReservationRow(
                id=r.id,
                resource=r.resource,
                start=r.start,
                end=r.end,
                status=r.state,
                price=r.price,
            )
            for r in rows
        ],
    )


def all_rules_query_user(
    cmd: QueryUserCommand, state: AppState
) -> Result[QueryUserData, QueryResult.Error]:
    data = rule_query_user_not_found(cmd, state)
    if data is None:
        return Err(QueryResult.Error.NOT_FOUND)
    return Ok(data)
