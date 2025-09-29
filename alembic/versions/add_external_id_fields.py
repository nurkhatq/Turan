# alembic/versions/add_external_id_fields.py
"""Add external ID fields for MoySklad relationships

Revision ID: add_external_id_fields
Revises: 48c32546632d
Create Date: 2025-09-28 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_external_id_fields'
down_revision: Union[str, None] = '48c32546632d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add external ID fields for product folder relationships
    op.add_column('product_folder', sa.Column('path_name', sa.String(500), nullable=True))
    op.add_column('product_folder', sa.Column('parent_external_id', sa.String(255), nullable=True))
    op.create_index('ix_product_folder_parent_external_id', 'product_folder', ['parent_external_id'])
    
    # Add external ID fields for products
    op.add_column('product', sa.Column('folder_external_id', sa.String(255), nullable=True))
    op.add_column('product', sa.Column('unit_external_id', sa.String(255), nullable=True))
    op.add_column('product', sa.Column('supplier_external_id', sa.String(255), nullable=True))
    op.create_index('ix_product_folder_external_id', 'product', ['folder_external_id'])
    op.create_index('ix_product_unit_external_id', 'product', ['unit_external_id'])
    op.create_index('ix_product_supplier_external_id', 'product', ['supplier_external_id'])
    
    # Add external ID fields for services
    op.add_column('service', sa.Column('folder_external_id', sa.String(255), nullable=True))
    op.add_column('service', sa.Column('unit_external_id', sa.String(255), nullable=True))
    op.create_index('ix_service_folder_external_id', 'service', ['folder_external_id'])
    op.create_index('ix_service_unit_external_id', 'service', ['unit_external_id'])
    
    # Add external ID fields for product variants
    op.add_column('product_variant', sa.Column('product_external_id', sa.String(255), nullable=False))
    op.create_index('ix_product_variant_product_external_id', 'product_variant', ['product_external_id'])
    
    # Add external ID fields for stock
    op.add_column('stock', sa.Column('product_external_id', sa.String(255), nullable=True))
    op.add_column('stock', sa.Column('variant_external_id', sa.String(255), nullable=True))
    op.add_column('stock', sa.Column('store_external_id', sa.String(255), nullable=False))
    op.add_column('stock', sa.Column('price', sa.Numeric(15, 2), nullable=True))
    op.add_column('stock', sa.Column('sale_price', sa.Numeric(15, 2), nullable=True))
    op.create_index('ix_stock_product_external_id', 'stock', ['product_external_id'])
    op.create_index('ix_stock_variant_external_id', 'stock', ['variant_external_id'])
    op.create_index('ix_stock_store_external_id', 'stock', ['store_external_id'])


def downgrade() -> None:
    # Remove indexes first
    op.drop_index('ix_stock_store_external_id', 'stock')
    op.drop_index('ix_stock_variant_external_id', 'stock')
    op.drop_index('ix_stock_product_external_id', 'stock')
    op.drop_index('ix_product_variant_product_external_id', 'product_variant')
    op.drop_index('ix_service_unit_external_id', 'service')
    op.drop_index('ix_service_folder_external_id', 'service')
    op.drop_index('ix_product_supplier_external_id', 'product')
    op.drop_index('ix_product_unit_external_id', 'product')
    op.drop_index('ix_product_folder_external_id', 'product')
    op.drop_index('ix_product_folder_parent_external_id', 'product_folder')
    
    # Remove columns
    op.drop_column('stock', 'sale_price')
    op.drop_column('stock', 'price')
    op.drop_column('stock', 'store_external_id')
    op.drop_column('stock', 'variant_external_id')
    op.drop_column('stock', 'product_external_id')
    op.drop_column('product_variant', 'product_external_id')
    op.drop_column('service', 'unit_external_id')
    op.drop_column('service', 'folder_external_id')
    op.drop_column('product', 'supplier_external_id')
    op.drop_column('product', 'unit_external_id')
    op.drop_column('product', 'folder_external_id')
    op.drop_column('product_folder', 'parent_external_id')
    op.drop_column('product_folder', 'path_name')