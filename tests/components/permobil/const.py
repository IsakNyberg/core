"""Constants for Permobil tests."""
from datetime import datetime, timedelta

from homeassistant.const import CONF_CODE, CONF_EMAIL, CONF_REGION, CONF_TOKEN, CONF_TTL

# Valid data
MOCK_REGIONS = {"region_name": "http://region.com"}
MOCK_REGION = "region_name"
MOCK_TOKEN = "a" * 256
MOCK_DATE = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
MOCK_TOKEN_RESPONSE = (MOCK_TOKEN, MOCK_DATE)
MOCK_CODE = "012345                      "
MOCK_EMAIL = "valid@email.com            "
DATA = {
    CONF_EMAIL: MOCK_EMAIL,
    CONF_REGION: MOCK_REGIONS[MOCK_REGION],
    CONF_CODE: MOCK_CODE,
    CONF_TOKEN: MOCK_TOKEN,
    CONF_TTL: MOCK_DATE,
}
# Valid second data
DATA2 = {
    CONF_EMAIL: "second.valid@email.net         ",
    CONF_REGION: "http://region2.com",
    CONF_CODE: "654321              ",
    CONF_TOKEN: "b" * 256,
    CONF_TTL: (datetime.now() + timedelta(days=123)).strftime("%Y-%m-%d"),
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
}
