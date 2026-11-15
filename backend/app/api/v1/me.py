from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.schemas.identity import MeResponse

router = APIRouter(prefix="/me", tags=["me"])


@router.get("", response_model=MeResponse)
async def get_me(user: CurrentUser) -> MeResponse:
    return MeResponse.model_validate(user)
