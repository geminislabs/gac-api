from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.orders import Order, OrderItem
from app.schemas.orders import OrderCreate


class OrderService:
    """Operaciones de negocio sobre órdenes de compra GAC."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(
        self, order_in: OrderCreate, created_by: Optional[UUID] = None
    ) -> Order:
        db_order = Order(
            client_id=order_in.client_id,
            notes=order_in.notes,
            created_by=created_by,
            status="pending",
            total_amount=Decimal("0.00"),
        )
        self.db.add(db_order)
        await self.db.flush()  # Necesario para tener order_id

        total_amount = Decimal("0.00")
        for item in order_in.items:
            db_item = OrderItem(
                order_id=db_order.order_id,
                device_id=item.device_id,
                product_key=item.product_key,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            self.db.add(db_item)
            total_amount += Decimal(item.quantity) * Decimal(item.unit_price)

        db_order.total_amount = total_amount
        await self.db.commit()
        order = await self.get_order(db_order.order_id)
        assert order is not None
        return order

    async def get_order(self, order_id: UUID) -> Optional[Order]:
        stmt = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.order_id == order_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_orders_by_client(self, client_id: UUID) -> List[Order]:
        stmt = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.client_id == client_id)
            .order_by(Order.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_orders(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> List[Order]:
        """Devuelve un listado paginado de órdenes ordenadas por fecha desc."""
        stmt = (
            select(Order)
            .options(selectinload(Order.items))
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        if status:
            stmt = stmt.where(Order.status == status)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_orders(self, status: Optional[str] = None) -> int:
        stmt = select(func.count()).select_from(Order)
        if status:
            stmt = stmt.where(Order.status == status)
        result = await self.db.execute(stmt)
        return int(result.scalar() or 0)
