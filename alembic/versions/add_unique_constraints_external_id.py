# Add unique constraints for external_id fields
# This migration adds unique constraints to external_id columns for ON CONFLICT operations

from alembic import op
import sqlalchemy as sa

def upgrade():
    """Add unique constraints to external_id fields."""
    
    # Add unique constraints for all external_id fields
    tables_with_external_id = [
        'currency',
        'country', 
        'organization',
        'employee',
        'project',
        'contract',
        'counterparty',
        'product',
        'product_folder',
        'unit_of_measure',
        'service',
        'store',
        'stock',
        'sales_document',
        'purchase_document'
    ]
    
    for table in tables_with_external_id:
        try:
            # Check if the table exists and has external_id column
            connection = op.get_bind()
            result = connection.execute(sa.text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table}' 
                AND column_name = 'external_id'
            """))
            
            if result.fetchone():
                # Add unique constraint if it doesn't exist
                try:
                    op.create_unique_constraint(
                        f'uq_{table}_external_id',
                        table,
                        ['external_id']
                    )
                    print(f"✅ Added unique constraint for {table}.external_id")
                except Exception as e:
                    print(f"⚠️  Unique constraint for {table}.external_id might already exist: {e}")
            else:
                print(f"⚠️  Table {table} does not have external_id column")
                
        except Exception as e:
            print(f"❌ Error processing table {table}: {e}")

def downgrade():
    """Remove unique constraints from external_id fields."""
    
    tables_with_external_id = [
        'currency',
        'country', 
        'organization',
        'employee',
        'project',
        'contract',
        'counterparty',
        'product',
        'product_folder',
        'unit_of_measure',
        'service',
        'store',
        'stock',
        'sales_document',
        'purchase_document'
    ]
    
    for table in tables_with_external_id:
        try:
            op.drop_constraint(f'uq_{table}_external_id', table, type_='unique')
            print(f"✅ Removed unique constraint for {table}.external_id")
        except Exception as e:
            print(f"⚠️  Could not remove constraint for {table}.external_id: {e}")
