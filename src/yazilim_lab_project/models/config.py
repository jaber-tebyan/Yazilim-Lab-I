from datetime import datetime
from typing import Annotated

from pydantic import PlainSerializer

Timestamp = Annotated[
    datetime,
    PlainSerializer(lambda d: d.strftime("%Y-%m-%dT%H:%M"), return_type=str),
]
