"""sprint 5 - indice de busca de clientes

Revision ID: 9553c7d8fa31
Revises: 4ccef2784c6d
Create Date: 2026-07-13 10:36:50.150440

Índice para `clientes.cnpj_cpf`, usado pela busca global da Visão 360º do
Cliente (`ClienteService.buscar_clientes`, ver docs/DECISIONS.md, seção 22).
`razao_social`/`nome_fantasia` não ganham índice: a busca usa `ILIKE
'%termo%'` sem âncora à esquerda, padrão que um índice B-tree não acelera.
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9553c7d8fa31"
down_revision: str | Sequence[str] | None = "4ccef2784c6d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("clientes", schema=None) as batch_op:
        batch_op.create_index("ix_clientes_cnpj_cpf", ["cnpj_cpf"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("clientes", schema=None) as batch_op:
        batch_op.drop_index("ix_clientes_cnpj_cpf")
