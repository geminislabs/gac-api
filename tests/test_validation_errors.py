"""Respuestas 422 con formato message + detail."""

from uuid import UUID


def test_validation_error_format_on_invalid_order_body(client, monkeypatch):
    """422 por body inválido incluye message y detail estructurado."""
    from app.api.deps import get_current_user
    from app.main import app
    from app.models.users import User

    mock_user = User(
        user_id=UUID("00000000-0000-0000-0000-000000000099"),
        email="test@test.com",
        password_hash="x",
        full_name="Test",
        is_active=True,
    )
    mock_user.roles = []

    async def override_user():
        return mock_user

    app.dependency_overrides[get_current_user] = override_user
    try:
        response = client.post(
            "/api/v1/orders",
            json={
                "client_id": "not-a-uuid",
                "items": [
                    {"product_key": "nexus", "quantity": 1, "unit_price": "10.00"}
                ],
            },
        )
        assert response.status_code == 422
        body = response.json()
        assert body["error"] == "validation_error"
        assert "message" in body
        assert isinstance(body["detail"], list)
        assert len(body["detail"]) >= 1
        assert "field" in body["detail"][0]
    finally:
        app.dependency_overrides.clear()


def test_payment_create_invalid_amount_returns_422(client, monkeypatch):
    from app.api.deps import get_current_user
    from app.main import app
    from app.models.users import User

    mock_user = User(
        user_id=UUID("00000000-0000-0000-0000-000000000099"),
        email="test@test.com",
        password_hash="x",
        full_name="Test",
        is_active=True,
    )
    mock_user.roles = []

    async def override_user():
        return mock_user

    app.dependency_overrides[get_current_user] = override_user
    try:
        response = client.post(
            "/api/v1/payments",
            json={
                "client_id": "00000000-0000-0000-0000-000000000001",
                "amount": 0,
                "method": "card",
            },
        )
        assert response.status_code == 422
        body = response.json()
        assert body["error"] == "validation_error"
        assert "amount" in body["message"].lower() or any(
            "amount" in str(d.get("field", "")) for d in body["detail"]
        )
    finally:
        app.dependency_overrides.clear()
