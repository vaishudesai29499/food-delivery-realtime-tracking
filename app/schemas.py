from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator

class LocationUpdate(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    accuracy_meters: float = Field(gt=0, le=1000)
    timestamp: datetime
    sequence: int = Field(ge=0)

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_be_aware_and_fresh(cls, value: datetime):
        if value.tzinfo is None:
            raise ValueError("timestamp must include timezone")
        age = (datetime.now(timezone.utc) - value.astimezone(timezone.utc)).total_seconds()
        if age < -5:
            raise ValueError("timestamp is too far in the future")
        if age > 30:
            raise ValueError("location update is stale (older than 30 seconds)")
        return value
