from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payments import Payment
from app.schemas.payments import PaymentCreate


class PaymentService:
    """Operaciones de negocio sobre pagos."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_payment(self, payment_in: PaymentCreate) -> Payment:
        db_payment = Payment(
            order_id=payment_in.order_id,
            client_id=payment_in.client_id,
            amount=payment_in.amount,
            method=payment_in.method,
            transaction_ref=payment_in.transaction_ref,
            status="pending",
        )
        self.db.add(db_payment)
        await self.db.commit()
        await self.db.refresh(db_payment)
        return db_payment

    async def get_payment(self, payment_id: UUID) -> Optional[Payment]:
        stmt = select(Payment).where(Payment.payment_id == payment_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_payments_by_client(self, client_id: UUID) -> List[Payment]:
        stmt = (
            select(Payment)
            .where(Payment.client_id == client_id)
            .order_by(Payment.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_payments(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> List[Payment]:
        stmt = select(Payment).order_by(Payment.created_at.desc())
        if status:
            stmt = stmt.where(Payment.status == status)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_payments(self, status: Optional[str] = None) -> int:
        stmt = select(func.count()).select_from(Payment)
        if status:
            stmt = stmt.where(Payment.status == status)
        result = await self.db.execute(stmt)
        return int(result.scalar() or 0)
