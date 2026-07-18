from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.users import User
from app.schemas.common import ResponseModel

router = APIRouter()


@router.get("/devices", response_model=ResponseModel[list])
async def get_devices(current_user: User = Depends(get_current_user)):
    # Placeholder: In reality this would proxy to siscom-admin-api or query a local cache
    return ResponseModel(message="Devices retrieved successfully", data=[])
