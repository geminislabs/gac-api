"""Fichas comerciales de los accesos de demo de Nexus

Guarda solo lo comercial. El ciclo de vida (estado, vigencia, fecha de canje)
vive en la base del entorno de demo y se consulta por API: replicarlo aquí
crearía dos verdades sobre si una demo sigue viva.

Revision ID: b7c3d9e14f20
Revises: ee38a850524a
Create Date: 2026-08-10

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b7c3d9e14f20'
down_revision: Union[str, Sequence[str], None] = 'ee38a850524a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists() -> bool:
    bind = op.get_bind()
    return sa.inspect(bind).has_table("nexus_demos", schema="gac")


def upgrade() -> None:
    """Upgrade schema.

    Idempotente a propósito. La base de gac ha recibido cambios a mano, así que
    no se puede dar por hecho que alembic_version refleje su estado real: esta
    migración puede acabar ejecutándose sobre una base donde la tabla ya exista.
    Repetirla no debe romper nada.
    """
    if _table_exists():
        return

    op.create_table(
        'nexus_demos',
        sa.Column(
            'demo_id',
            sa.UUID(),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column('tenant_id', sa.String(length=64), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('recipient_email', sa.String(length=255), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column(
            'scenario',
            sa.String(length=32),
            server_default=sa.text("'normal'"),
            nullable=False,
        ),
        sa.Column(
            'ttl_hours', sa.Integer(), server_default=sa.text('168'), nullable=False
        ),
        sa.Column('created_by', sa.UUID(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ['created_by'],
            ['gac.users.user_id'],
            # RESTRICT y no CASCADE: borrar un usuario no debe llevarse por
            # delante el historial de a qué clientes se les demostró el producto.
            ondelete='RESTRICT',
        ),
        sa.PrimaryKeyConstraint('demo_id'),
        sa.UniqueConstraint('tenant_id'),
        schema='gac',
    )
    op.create_index(
        'ix_gac_nexus_demos_created_by',
        'nexus_demos',
        ['created_by'],
        unique=False,
        schema='gac',
    )
    op.create_index(
        'ix_gac_nexus_demos_created_at',
        'nexus_demos',
        ['created_at'],
        unique=False,
        schema='gac',
    )


def downgrade() -> None:
    """Downgrade schema."""
    if not _table_exists():
        return
    op.drop_index('ix_gac_nexus_demos_created_at', table_name='nexus_demos', schema='gac')
    op.drop_index('ix_gac_nexus_demos_created_by', table_name='nexus_demos', schema='gac')
    op.drop_table('nexus_demos', schema='gac')
