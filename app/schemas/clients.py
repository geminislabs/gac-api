from uuid import UUID

from pydantic import BaseModel, Field


class CommercialClientSummary(BaseModel):
    """
    Cliente comercial en GAC.

    Convención: client_id es el mismo UUID que accounts.id en siscom-admin-api.
    """

    client_id: UUID
    account_id: UUID = Field(
        description="ID de cuenta Nexus (siscom-admin-api); igual a client_id"
    )
    orders_count: int = 0
    payments_count: int = 0
    shipments_count: int = 0
