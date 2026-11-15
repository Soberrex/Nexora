import pytest
from pydantic import ValidationError

from app.config import Settings


@pytest.mark.parametrize("raw", ["Production", "prod", " PROD "])
def test_environment_normalized_to_production(raw: str) -> None:
    assert Settings(ENVIRONMENT=raw).ENVIRONMENT == "production"


def test_dev_alias() -> None:
    assert Settings(ENVIRONMENT="dev").ENVIRONMENT == "development"


def test_unknown_environment_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(ENVIRONMENT="banana")
