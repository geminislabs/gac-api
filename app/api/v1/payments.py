from uuid import UUID
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.users import User
from app.schemas.common import ResponseModel
from app.schemas.payments import PaymentCreate, PaymentResponse
from app.services.payment_service import PaymentService

router = APIRouter()


@router.post(
    "/payments",
    response_model=ResponseModel[PaymentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_payment(
    payment_in: PaymentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    service = PaymentService(db)
    payment = await service.create_payment(payment_in)
    return ResponseModel(
        message="Payment created successfully",
        data=PaymentResponse.model_validate(payment),
    )


@router.get(
    "/payments",
    response_model=ResponseModel[List[PaymentResponse]],
)
async def list_payments(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status_filter: Optional[str] = Query(None, alias="status"),
):
    """Lista paginada de pagos con filtro opcional por estado."""
    service = PaymentService(db)
    payments = await service.list_payments(skip=skip, limit=limit, status=status_filter)
    return ResponseModel(
        message="Payments retrieved successfully",
        data=[PaymentResponse.model_validate(p) for p in payments],
    )


@router.get("/payments/{payment_id}", response_model=ResponseModel[PaymentResponse])
async def get_payment(
    payment_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    service = PaymentService(db)
    payment = await service.get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return ResponseModel(
        message="Payment retrieved successfully",
        data=PaymentResponse.model_validate(payment),
    )


@router.get(
    "/clients/{client_id}/payments",
    response_model=ResponseModel[List[PaymentResponse]],
)
async def get_client_payments(
    client_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    service = PaymentService(db)
    payments = await service.get_payments_by_client(client_id)
    return ResponseModel(
        message="Payments retrieved successfully",
        data=[PaymentResponse.model_validate(p) for p in payments],
    )
