"""Constants for Permobil tests."""
from datetime import datetime, timedelta

from homeassistant.const import (
    CONF_CODE,
    CONF_DEVICE_ID,
    CONF_EMAIL,
    CONF_REGION,
    CONF_TOKEN,
    CONF_TTL,
    CONF_UNIT_OF_MEASUREMENT,
)

KM = "kilometers"
MILES = "miles"
# Valid data
MOCK_REGIONS = {"region_name": "http://region.com"}
MOCK_REGION = "region_name"
MOCK_TOKEN = "a" * 256
MOCK_DATE = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
MOCK_TOKEN_RESPONSE = (MOCK_TOKEN, MOCK_DATE)
MOCK_CODE = "012345                      "
MOCK_EMAIL = "valid@email.com            "
MOCK_DEVICE_ID = "1234567890AB1234567890AB"
MOCK_UNIT_OF_MEASUREMENT = KM
DATA = {
    CONF_EMAIL: MOCK_EMAIL,
    CONF_REGION: MOCK_REGIONS[MOCK_REGION],
    CONF_CODE: MOCK_CODE,
    CONF_TOKEN: MOCK_TOKEN,
    CONF_TTL: MOCK_DATE,
    CONF_UNIT_OF_MEASUREMENT: MOCK_UNIT_OF_MEASUREMENT,
    CONF_DEVICE_ID: MOCK_DEVICE_ID,
}
# Valid second data
DATA2 = {
    CONF_EMAIL: "second.valid@email.net         ",
    CONF_REGION: "http://region2.com",
    CONF_CODE: "654321              ",
    CONF_TOKEN: "b" * 256,
    CONF_TTL: (datetime.now() + timedelta(days=123)).strftime("%Y-%m-%d"),
    CONF_UNIT_OF_MEASUREMENT: MILES,
    CONF_DEVICE_ID: "BA0987654321BA0987654321",
}


# Invalid data
EMPTY = ""
INVALID_EMAIL = "this is not a valid email"
INVALID_REGION = "this is not a valid region"
INVALID_CODE = "this is not a valid code"

INVALID_DATA = {
    CONF_EMAIL: INVALID_EMAIL,
    CONF_REGION: MOCK_REGIONS[MOCK_REGION],
    CONF_CODE: MOCK_CODE,
    CONF_TOKEN: MOCK_TOKEN,
    CONF_TTL: MOCK_DATE,
    CONF_UNIT_OF_MEASUREMENT: "invalid",
    CONF_DEVICE_ID: "123",
}
