"""Add_unique_constraints_for_external_id_fields

Revision ID: 48c32546632d
Revises: 7a1611250a78
Create Date: 2025-09-28 10:52:33.628115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '48c32546632d'
down_revision: Union[str, None] = '7a1611250a78'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add unique constraints for external_id fields
    op.create_unique_constraint('uq_store_external_id', 'store', ['external_id'])
    op.create_unique_constraint('uq_product_external_id', 'product', ['external_id'])
    op.create_unique_constraint('uq_product_folder_external_id', 'product_folder', ['external_id'])
    op.create_unique_constraint('uq_unit_of_measure_external_id', 'unit_of_measure', ['external_id'])
    op.create_unique_constraint('uq_counterparty_external_id', 'counterparty', ['external_id'])
    op.create_unique_constraint('uq_stock_external_id', 'stock', ['external_id'])


def downgrade() -> None:
    # Drop unique constraints for external_id fields
    op.drop_constraint('uq_stock_external_id', 'stock', type_='unique')
    op.drop_constraint('uq_counterparty_external_id', 'counterparty', type_='unique')
    op.drop_constraint('uq_unit_of_measure_external_id', 'unit_of_measure', type_='unique')
    op.drop_constraint('uq_product_folder_external_id', 'product_folder', type_='unique')
    op.drop_constraint('uq_product_external_id', 'product', type_='unique')
    op.drop_constraint('uq_store_external_id', 'store', type_='unique')

