import pytest

from app.core.auth import FirebaseTokenVerifier


def test_emulator_refused_in_production() -> None:
    with pytest.raises(RuntimeError, match="production"):
        FirebaseTokenVerifier(
            project_id="demo-nexora", emulator_host="localhost:9099", environment="production"
        )


def test_project_id_required() -> None:
    with pytest.raises(RuntimeError, match="FIREBASE_PROJECT_ID"):
        FirebaseTokenVerifier(project_id="", emulator_host="", environment="development")
