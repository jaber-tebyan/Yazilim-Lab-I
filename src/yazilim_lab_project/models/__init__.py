from datetime import datetime
from typing import Annotated
from pydantic import Field, PlainSerializer
from yazilim_lab_project.models.results import (
    AddResourceResult,
    AddUserResult,
    PriceResult,
    QueryResult,
    ReservationResult,
    WaitingResult,
    CancelResult,
    ClockResult,
    EntryResult,
    ExitResult,
    PackageResult,
)

# I removed descriminator because of QueryResult's object's having the same status for OkUser and OkResource
AnyResult = (
    AddUserResult.Any
    | AddResourceResult.Any
    | PriceResult.Any
    | ReservationResult.Any
    | CancelResult.Any
    | ClockResult.Any
    | EntryResult.Any
    | ExitResult.Any
    | PackageResult.Any
    | QueryResult.Any
    | WaitingResult.Any
)
