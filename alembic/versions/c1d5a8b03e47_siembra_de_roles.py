"""Siembra los roles que el código exige por nombre

`require_roles(["admin"])` aparece en 26 sitios y `require_roles(["admin",
"vendedor"])` en los endpoints de demos. Son nombres escritos literalmente en el
código: si no existen en la base, esos endpoints devuelven 403 a todo el mundo y
no hay forma de arreglarlo desde la interfaz, porque administrar roles también
exige ser admin.

Hasta ahora ninguno de los dos se creaba de forma reproducible: `admin` solo
aparecía si alguien ejecutaba `scripts/create_test_user.py` a mano, y `vendedor`
se creó directamente contra producción. Un entorno nuevo nacía sin ninguno.

Revision ID: c1d5a8b03e47
Revises: b7c3d9e14f20
Create Date: 2026-08-10

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c1d5a8b03e47"
down_revision: Union[str, Sequence[str], None] = "b7c3d9e14f20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Roles de los que depende el código. Añadir aquí cualquier nombre nuevo que
# aparezca en un require_roles(...).
ROLES = ("admin", "vendedor")


def upgrade() -> None:
    """Crea los roles que falten.

    Idempotente: gac.roles tiene UNIQUE(name), así que ON CONFLICT DO NOTHING es
    exacto. En producción, donde ambos ya existen, no hace nada.
    """
    for name in ROLES:
        op.execute(
            sa.text(
                "INSERT INTO gac.roles (name) VALUES (:name) ON CONFLICT (name) DO NOTHING"
            ).bindparams(name=name)
        )


def downgrade() -> None:
    """Borra los roles sembrados, pero solo si nadie los tiene asignados.

    gac.user_roles referencia roles con ON DELETE CASCADE: borrar un rol en uso
    dejaría a personas sin permisos sin que nada lo indique. Ante la duda, se
    conserva — revertir una migración no debe quitarle el acceso a nadie.
    """
    for name in ROLES:
        op.execute(
            sa.text(
                "DELETE FROM gac.roles r "
                "WHERE r.name = :name "
                "  AND NOT EXISTS (SELECT 1 FROM gac.user_roles ur WHERE ur.role_id = r.role_id)"
            ).bindparams(name=name)
        )
