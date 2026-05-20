"""Validación de schemas de órdenes."""

from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.orders import OrderCreate, OrderItemCreate


def test_order_create_requires_unit_price():
    with pytest.raises(ValidationError):
        OrderCreate(
            client_id=uuid4(),
            items=[OrderItemCreate(product_key="nexus", quantity=1)],
        )


def test_order_create_valid():
    order = OrderCreate(
        client_id=uuid4(),
        items=[
            OrderItemCreate(
                product_key="nexus",
                quantity=2,
                unit_price=Decimal("199.50"),
            )
        ],
        notes="Prueba",
    )
    assert order.items[0].unit_price == Decimal("199.50")
