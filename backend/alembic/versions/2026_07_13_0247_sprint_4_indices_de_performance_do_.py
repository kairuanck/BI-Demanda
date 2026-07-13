"""sprint 4 - indices de performance do dashboard

Revision ID: 4ccef2784c6d
Revises: 7a8767356031
Create Date: 2026-07-13 02:47:10.968351

Índices para as colunas de filtro/junção mais usadas pelas consultas
agregadas do Dashboard Executivo (DashboardService, ver docs/DECISIONS.md,
seção 19), nas tabelas de fato/dimensão que crescem com a base real:
`clientes.uf_sigla`, `carteiras.promotor_id`, `carteiras_avert.promotor_id`,
`carteiras_avert.cliente_id`, `faturamentos.laboratorio_id` e
`visitas.cliente_id`.
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4ccef2784c6d"
down_revision: str | Sequence[str] | None = "7a8767356031"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("carteiras", schema=None) as batch_op:
        batch_op.create_index("ix_carteiras_promotor", ["promotor_id"], unique=False)

    with op.batch_alter_table("carteiras_avert", schema=None) as batch_op:
        batch_op.create_index("ix_carteiras_avert_cliente", ["cliente_id"], unique=False)
        batch_op.create_index("ix_carteiras_avert_promotor", ["promotor_id"], unique=False)

    with op.batch_alter_table("clientes", schema=None) as batch_op:
        batch_op.create_index("ix_clientes_uf", ["uf_sigla"], unique=False)

    with op.batch_alter_table("faturamentos", schema=None) as batch_op:
        batch_op.create_index("ix_faturamentos_laboratorio", ["laboratorio_id"], unique=False)

    with op.batch_alter_table("visitas", schema=None) as batch_op:
        batch_op.create_index("ix_visitas_cliente", ["cliente_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("visitas", schema=None) as batch_op:
        batch_op.drop_index("ix_visitas_cliente")

    with op.batch_alter_table("faturamentos", schema=None) as batch_op:
        batch_op.drop_index("ix_faturamentos_laboratorio")

    with op.batch_alter_table("clientes", schema=None) as batch_op:
        batch_op.drop_index("ix_clientes_uf")

    with op.batch_alter_table("carteiras_avert", schema=None) as batch_op:
        batch_op.drop_index("ix_carteiras_avert_promotor")
        batch_op.drop_index("ix_carteiras_avert_cliente")

    with op.batch_alter_table("carteiras", schema=None) as batch_op:
        batch_op.drop_index("ix_carteiras_promotor")
