from uuid import UUID
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.users import User
from app.schemas.common import ResponseModel
from app.schemas.shipments import (
    ShipmentCreate,
    ShipmentResponse,
    ShipmentUpdateStatus,
)
from app.services.shipment_service import ShipmentService

router = APIRouter()


@router.post(
    "/shipments",
    response_model=ResponseModel[ShipmentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_shipment(
    shipment_in: ShipmentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    service = ShipmentService(db)
    shipment = await service.create_shipment(shipment_in)
    return ResponseModel(message="Shipment created successfully", data=shipment)


@router.get(
    "/shipments",
    response_model=ResponseModel[List[ShipmentResponse]],
)
async def list_shipments(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status_filter: Optional[str] = Query(None, alias="status"),
):
    """Lista paginada de envíos con filtro opcional por estado."""
    service = ShipmentService(db)
    shipments = await service.list_shipments(skip=skip, limit=limit, status=status_filter)
    return ResponseModel(message="Shipments retrieved successfully", data=shipments)


@router.get(
    "/shipments/{shipment_id}",
    response_model=ResponseModel[ShipmentResponse],
)
async def get_shipment(
    shipment_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    service = ShipmentService(db)
    shipment = await service.get_shipment(shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return ResponseModel(message="Shipment retrieved successfully", data=shipment)


@router.patch(
    "/shipments/{shipment_id}/status",
    response_model=ResponseModel[ShipmentResponse],
)
async def update_shipment_status(
    shipment_id: UUID,
    status_in: ShipmentUpdateStatus,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    service = ShipmentService(db)
    shipment = await service.update_status(shipment_id, status_in.status)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return ResponseModel(
        message="Shipment status updated successfully", data=shipment
    )


@router.get(
    "/clients/{client_id}/shipments",
    response_model=ResponseModel[List[ShipmentResponse]],
)
async def get_client_shipments(
    client_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    service = ShipmentService(db)
    shipments = await service.get_shipments_by_client(client_id)
    return ResponseModel(message="Shipments retrieved successfully", data=shipments)
