from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import require_roles
from app.models.users import User
from app.schemas.products import (
    CatalogProductCreate,
    CatalogProductOut,
    CatalogProductUpdate,
)
from app.schemas.common import ResponseModel

router = APIRouter(prefix="/internal", tags=["internal-catalog"])
_catalog: List[dict] = []


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _seed_if_empty() -> None:
    if _catalog:
        return
    now = _now()
    _catalog.append(
        {
            "id": uuid4(),
            "code": "nexus",
            "name": "Nexus",
            "description": "GPS Tracking Device",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
    )


def _to_out(row: dict) -> CatalogProductOut:
    return CatalogProductOut(
        id=row["id"],
        code=row["code"],
        name=row["name"],
        description=row.get("description"),
        is_active=row.get("is_active", True),
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
    )


@router.get(
    "/products",
    response_model=ResponseModel[List[CatalogProductOut]],
)
async def list_catalog_products(
    current_user: Annotated[User, Depends(require_roles(["admin"]))],
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    is_active: Optional[bool] = Query(None),
):
    _seed_if_empty()
    rows = list(_catalog)
    if is_active is not None:
        rows = [r for r in rows if bool(r.get("is_active")) == is_active]
    rows = sorted(rows, key=lambda r: r.get("code", ""))
    slice_rows = rows[offset : offset + limit]
    return ResponseModel(
        message="Products retrieved successfully",
        data=[_to_out(r) for r in slice_rows],
    )


@router.get(
    "/products/{product_id}",
    response_model=ResponseModel[CatalogProductOut],
)
async def get_catalog_product(
    product_id: UUID,
    current_user: Annotated[User, Depends(require_roles(["admin"]))],
):
    _seed_if_empty()
    for row in _catalog:
        if row["id"] == product_id:
            return ResponseModel(
                message="Product retrieved successfully",
                data=_to_out(row),
            )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
    )


@router.post(
    "/products",
    response_model=ResponseModel[CatalogProductOut],
    status_code=status.HTTP_201_CREATED,
)
async def create_catalog_product(
    body: CatalogProductCreate,
    current_user: Annotated[User, Depends(require_roles(["admin"]))],
):
    _seed_if_empty()
    code_norm = body.code.strip().lower()
    if any(r["code"].lower() == code_norm for r in _catalog):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product code already exists",
        )
    now = _now()
    row = {
        "id": uuid4(),
        "code": code_norm,
        "name": body.name.strip(),
        "description": body.description,
        "is_active": body.is_active,
        "created_at": now,
        "updated_at": now,
    }
    _catalog.append(row)
    return ResponseModel(
        message="Product created successfully",
        data=_to_out(row),
    )


@router.patch(
    "/products/{product_id}",
    response_model=ResponseModel[CatalogProductOut],
)
async def update_catalog_product(
    product_id: UUID,
    body: CatalogProductUpdate,
    current_user: Annotated[User, Depends(require_roles(["admin"]))],
):
    _seed_if_empty()
    for row in _catalog:
        if row["id"] != product_id:
            continue
        if body.name is not None:
            row["name"] = body.name.strip()
        if body.description is not None:
            row["description"] = body.description
        if body.is_active is not None:
            row["is_active"] = body.is_active
        row["updated_at"] = _now()
        return ResponseModel(
            message="Product updated successfully",
            data=_to_out(row),
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
    )


@router.delete("/products/{product_id}", response_model=ResponseModel[bool])
async def delete_catalog_product(
    product_id: UUID,
    current_user: Annotated[User, Depends(require_roles(["admin"]))],
):
    """Baja lógica (is_active = false)."""
    _seed_if_empty()
    for row in _catalog:
        if row["id"] == product_id:
            row["is_active"] = False
            row["updated_at"] = _now()
            return ResponseModel(message="Product deactivated successfully", data=True)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
    )
