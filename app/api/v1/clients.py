from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.users import User
from app.schemas.clients import CommercialClientSummary
from app.schemas.common import ResponseModel
from app.services.order_service import OrderService
from app.services.payment_service import PaymentService
from app.services.shipment_service import ShipmentService

router = APIRouter()


@router.get(
    "/clients/{client_id}",
    response_model=ResponseModel[CommercialClientSummary],
)
async def get_commercial_client(
    client_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Resumen del cliente comercial GAC vinculado a una cuenta Nexus.

    El client_id coincide con el account_id de siscom-admin-api (misma raíz comercial).
    """
    orders = await OrderService(db).get_orders_by_client(client_id)
    payments = await PaymentService(db).get_payments_by_client(client_id)
    shipments = await ShipmentService(db).get_shipments_by_client(client_id)

    summary = CommercialClientSummary(
        client_id=client_id,
        account_id=client_id,
        orders_count=len(orders),
        payments_count=len(payments),
        shipments_count=len(shipments),
    )
    return ResponseModel(
        message="Commercial client summary retrieved",
        data=summary,
    )
