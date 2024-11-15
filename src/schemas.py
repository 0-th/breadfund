from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict, model_validator


def convert_datetime_to_utc(dt: datetime) -> str:
    """Add UTC as timezone for datetime objects"""
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


class CustomModel(BaseModel):
    model_config = ConfigDict(
        json_encoders={datetime: convert_datetime_to_utc}, populate_by_name=True
    )

    @model_validator(mode="before")
    @classmethod
    def set_null_microseconds(cls, data: dict[str, Any]) -> dict[str, object]:
        datetime_fields = {
            k: v.replace(microsecond=0)
            for k, v in data.items()
            if isinstance(k, datetime)
        }
        return {**data, **datetime_fields}

    def serializable_dict(self) -> dict[Any, Any]:
        """Return a serializable dict that only contains json serializable objects"""
        default_dict = self.model_dump()

        return jsonable_encoder(default_dict)
