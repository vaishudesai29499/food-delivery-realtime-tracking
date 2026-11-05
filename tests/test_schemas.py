from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from app.schemas import LocationUpdate

def valid_payload():
    return {
        "latitude": 18.52,
        "longitude": 73.85,
        "accuracy_meters": 10,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sequence": 1,
    }

def test_valid_location():
    assert LocationUpdate(**valid_payload()).sequence == 1

def test_invalid_latitude():
    data = valid_payload()
    data["latitude"] = 91
    with pytest.raises(ValidationError):
        LocationUpdate(**data)

def test_invalid_longitude():
    data = valid_payload()
    data["longitude"] = 181
    with pytest.raises(ValidationError):
        LocationUpdate(**data)
