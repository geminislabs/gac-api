from uuid import UUID
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.users import User
from app.schemas.common import ResponseModel
from app.schemas.orders import OrderCreate, OrderResponse
from app.services.order_service import OrderService

router = APIRouter()


@router.post(
    "/orders",
    response_model=ResponseModel[OrderResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    order_in: OrderCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Crea una nueva orden vinculada al usuario autenticado."""
    service = OrderService(db)
    order = await service.create_order(order_in, current_user.user_id)
    return ResponseModel(
        message="Order created successfully",
        data=OrderResponse.model_validate(order),
    )


@router.get(
    "/orders",
    response_model=ResponseModel[List[OrderResponse]],
)
async def list_orders(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status_filter: Optional[str] = Query(None, alias="status"),
):
    """Lista paginada de órdenes con filtro opcional por estado."""
    service = OrderService(db)
    orders = await service.list_orders(skip=skip, limit=limit, status=status_filter)
    return ResponseModel(message="Orders retrieved successfully", data=orders)


@router.get("/orders/{order_id}", response_model=ResponseModel[OrderResponse])
async def get_order(
    order_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    service = OrderService(db)
    order = await service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return ResponseModel(
        message="Order retrieved successfully",
        data=OrderResponse.model_validate(order),
    )


@router.get(
    "/clients/{client_id}/orders",
    response_model=ResponseModel[List[OrderResponse]],
)
async def get_client_orders(
    client_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    service = OrderService(db)
    orders = await service.get_orders_by_client(client_id)
    return ResponseModel(message="Orders retrieved successfully", data=orders)
