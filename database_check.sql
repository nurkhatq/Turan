# database_check.sql
-- Database verification queries
-- Run these in your PostgreSQL database to verify synced data

-- Check overall sync status
SELECT 
    'Products' as entity,
    COUNT(*) as total_count,
    COUNT(CASE WHEN external_id IS NOT NULL THEN 1 END) as synced_count,
    MAX(last_sync_at) as last_sync
FROM product
UNION ALL
SELECT 
    'Counterparties' as entity,
    COUNT(*) as total_count,
    COUNT(CASE WHEN external_id IS NOT NULL THEN 1 END) as synced_count,
    MAX(last_sync_at) as last_sync
FROM counterparty
UNION ALL
SELECT 
    'Stores' as entity,
    COUNT(*) as total_count,
    COUNT(CASE WHEN external_id IS NOT NULL THEN 1 END) as synced_count,
    MAX(last_sync_at) as last_sync
FROM store;

-- Check recent sync jobs
SELECT 
    service_name,
    job_type,
    status,
    started_at,
    completed_at,
    total_items,
    processed_items,
    failed_items,
    error_message
FROM sync_job 
ORDER BY created_at DESC 
LIMIT 10;

-- Check sample products with details
SELECT 
    id,
    name,
    code,
    sale_price,
    external_id,
    last_sync_at,
    sync_status
FROM product 
WHERE external_id IS NOT NULL
ORDER BY created_at DESC 
LIMIT 10;

-- Check sample counterparties
SELECT 
    id,
    name,
    email,
    is_customer,
    is_supplier,
    external_id,
    last_sync_at
FROM counterparty 
WHERE external_id IS NOT NULL
ORDER BY created_at DESC 
LIMIT 10;

-- Check stock levels
SELECT 
    s.id,
    p.name as product_name,
    st.name as store_name,
    s.stock,
    s.available,
    s.last_sync_at
FROM stock s
JOIN product p ON s.product_id = p.id
JOIN store st ON s.store_id = st.id
ORDER BY s.created_at DESC 
LIMIT 10;