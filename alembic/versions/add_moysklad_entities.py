"""Add MoySklad organizations, employees, projects and reference entities

Revision ID: add_moysklad_entities
Revises: 7a1611250a78
Create Date: 2025-09-29 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_moysklad_entities'
down_revision: Union[str, None] = '7a1611250a78'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create currency table
    op.create_table('currency',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=500), nullable=True),
        sa.Column('code', sa.String(length=3), nullable=False),
        sa.Column('iso_code', sa.String(length=3), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False),
        sa.Column('is_indirect', sa.Boolean(), nullable=False),
        sa.Column('multiplicity', sa.Integer(), nullable=False),
        sa.Column('rate', sa.Numeric(precision=20, scale=10), nullable=False),
        sa.Column('minor_units', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('archived', sa.Boolean(), nullable=False),
        sa.Column('last_sync_at', sa.DateTime(), nullable=True),
        sa.Column('sync_status', sa.String(length=50), nullable=True),
        sa.Column('external_meta', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('external_id')
    )
    op.create_index(op.f('ix_currency_code'), 'currency', ['code'], unique=True)
    op.create_index(op.f('ix_currency_external_id'), 'currency', ['external_id'], unique=False)
    
    # Create country table
    op.create_table('country',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('code', sa.String(length=10), nullable=True),
        sa.Column('external_code', sa.String(length=10), nullable=True),
        sa.Column('last_sync_at', sa.DateTime(), nullable=True),
        sa.Column('sync_status', sa.String(length=50), nullable=True),
        sa.Column('external_meta', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('external_id')
    )
    op.create_index(op.f('ix_country_code'), 'country', ['code'], unique=True)
    op.create_index(op.f('ix_country_external_id'), 'country', ['external_id'], unique=False)
    
    # Create organization table
    op.create_table('organization',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('code', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('legal_title', sa.String(length=500), nullable=True),
        sa.Column('legal_address', sa.Text(), nullable=True),
        sa.Column('actual_address', sa.Text(), nullable=True),
        sa.Column('inn', sa.String(length=12), nullable=True),
        sa.Column('kpp', sa.String(length=9), nullable=True),
        sa.Column('ogrn', sa.String(length=15), nullable=True),
        sa.Column('okpo', sa.String(length=10), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('fax', sa.String(length=50), nullable=True),
        sa.Column('bank_accounts', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('archived', sa.Boolean(), nullable=False),
        sa.Column('shared', sa.Boolean(), nullable=False),
        sa.Column('chief_accountant_external_id', sa.String(length=255), nullable=True),
        sa.Column('last_sync_at', sa.DateTime(), nullable=True),
        sa.Column('sync_status', sa.String(length=50), nullable=True),
        sa.Column('external_meta', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id')
    )
    op.create_index(op.f('ix_organization_code'), 'organization', ['code'], unique=False)
    op.create_index(op.f('ix_organization_external_id'), 'organization', ['external_id'], unique=False)
    op.create_index(op.f('ix_organization_inn'), 'organization', ['inn'], unique=False)
    op.create_index(op.f('ix_organization_name'), 'organization', ['name'], unique=False)
    
    # Create project table
    op.create_table('project',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('code', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('archived', sa.Boolean(), nullable=False),
        sa.Column('shared', sa.Boolean(), nullable=False),
        sa.Column('last_sync_at', sa.DateTime(), nullable=True),
        sa.Column('sync_status', sa.String(length=50), nullable=True),
        sa.Column('external_meta', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id')
    )
    op.create_index(op.f('ix_project_code'), 'project', ['code'], unique=False)
    op.create_index(op.f('ix_project_external_id'), 'project', ['external_id'], unique=False)
    op.create_index(op.f('ix_project_name'), 'project', ['name'], unique=False)
    
    # Create employee table
    op.create_table('employee',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('middle_name', sa.String(length=255), nullable=True),
        sa.Column('last_name', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=500), nullable=False),
        sa.Column('position', sa.String(length=255), nullable=True),
        sa.Column('code', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('permissions_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('archived', sa.Boolean(), nullable=False),
        sa.Column('shared', sa.Boolean(), nullable=False),
        sa.Column('retail_store_external_id', sa.String(length=255), nullable=True),
        sa.Column('cashier_inn', sa.String(length=12), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('organization_external_id', sa.String(length=255), nullable=True),
        sa.Column('last_sync_at', sa.DateTime(), nullable=True),
        sa.Column('sync_status', sa.String(length=50), nullable=True),
        sa.Column('external_meta', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id')
    )
    op.create_index(op.f('ix_employee_code'), 'employee', ['code'], unique=False)
    op.create_index(op.f('ix_employee_email'), 'employee', ['email'], unique=False)
    op.create_index(op.f('ix_employee_external_id'), 'employee', ['external_id'], unique=False)
    op.create_index(op.f('ix_employee_full_name'), 'employee', ['full_name'], unique=False)
    
    # Create price_type table
    op.create_table('price_type',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('external_code', sa.String(length=255), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False),
        sa.Column('currency_external_id', sa.String(length=255), nullable=True),
        sa.Column('currency_id', sa.Integer(), nullable=True),
        sa.Column('last_sync_at', sa.DateTime(), nullable=True),
        sa.Column('sync_status', sa.String(length=50), nullable=True),
        sa.Column('external_meta', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['currency_id'], ['currency.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_price_type_external_id'), 'price_type', ['external_id'], unique=False)
    
    # Create contract table
    op.create_table('contract',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('code', sa.String(length=255), nullable=True),
        sa.Column('number', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('moment', sa.DateTime(), nullable=False),
        sa.Column('contract_date', sa.DateTime(), nullable=True),
        sa.Column('contract_type', sa.String(length=50), nullable=False),
        sa.Column('sum_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('reward_percent', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('reward_type', sa.String(length=50), nullable=True),
        sa.Column('archived', sa.Boolean(), nullable=False),
        sa.Column('shared', sa.Boolean(), nullable=False),
        sa.Column('counterparty_external_id', sa.String(length=255), nullable=True),
        sa.Column('counterparty_id', sa.Integer(), nullable=True),
        sa.Column('organization_external_id', sa.String(length=255), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('project_external_id', sa.String(length=255), nullable=True),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('last_sync_at', sa.DateTime(), nullable=True),
        sa.Column('sync_status', sa.String(length=50), nullable=True),
        sa.Column('external_meta', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['counterparty_id'], ['counterparty.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id')
    )
    op.create_index(op.f('ix_contract_code'), 'contract', ['code'], unique=False)
    op.create_index(op.f('ix_contract_external_id'), 'contract', ['external_id'], unique=False)
    op.create_index(op.f('ix_contract_name'), 'contract', ['name'], unique=False)
    op.create_index(op.f('ix_contract_number'), 'contract', ['number'], unique=False)
    
    # Create employee_project table (many-to-many)
    op.create_table('employee_project',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employee.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add foreign key to counterparty for contracts
    op.add_column('counterparty', sa.Column('default_contract_id', sa.Integer(), nullable=True))
    

def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_column('counterparty', 'default_contract_id')
    op.drop_table('employee_project')
    op.drop_table('contract')
    op.drop_table('price_type')
    op.drop_table('employee')
    op.drop_table('project')
    op.drop_table('organization')
    op.drop_table('country')
    op.drop_table('currency')