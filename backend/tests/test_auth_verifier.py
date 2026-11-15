import pytest

from app.config import Settings
from app.core.auth import FirebaseTokenVerifier


def test_emulator_refused_in_production() -> None:
    with pytest.raises(RuntimeError, match="production"):
        FirebaseTokenVerifier(
            project_id="demo-nexora", emulator_host="localhost:9099", environment="production"
        )


def test_project_id_required() -> None:
    with pytest.raises(RuntimeError, match="FIREBASE_PROJECT_ID"):
        FirebaseTokenVerifier(project_id="", emulator_host="", environment="development")


def test_emulator_refused_for_uppercase_production_environment() -> None:
    with pytest.raises(RuntimeError, match="production"):
        FirebaseTokenVerifier(
            project_id="demo-nexora",
            emulator_host="localhost:9099",
            environment=Settings(ENVIRONMENT="PRODUCTION").ENVIRONMENT,
        )
