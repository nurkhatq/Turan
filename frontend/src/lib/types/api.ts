// Auth types
export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  last_login_at: string | null;
  created_at: string;
  roles: Role[];
  permissions: string[];
}

export interface Role {
  id: number;
  name: string;
  description: string | null;
  permissions: string[];
  is_system_role: boolean;
  created_at: string;
}

// Product types
export interface Product {
  id: number;
  name: string;
  code: string | null;
  article: string | null;
  description: string | null;
  sale_price: number | null;
  buy_price: number | null;
  min_price: number | null;
  weight: number | null;
  volume: number | null;
  archived: boolean;
  folder: ProductFolder | null;
  unit: UnitOfMeasure | null;
  variants: ProductVariant[];
  external_id: string | null;
  last_sync_at: string | null;
}

export interface ProductFolder {
  id: number;
  name: string;
  code: string | null;
  description: string | null;
  path_name: string | null;
  archived: boolean;
  parent_external_id: string | null;
  external_id: string | null;
}

export interface UnitOfMeasure {
  id: number;
  name: string;
  code: string | null;
  description: string | null;
  external_id: string | null;
}

export interface ProductVariant {
  id: number;
  name: string;
  code: string | null;
  sale_price: number | null;
  buy_price: number | null;
  characteristics: Record<string, any> | null;
  external_id: string | null;
}

// Inventory types
export interface Store {
  id: number;
  name: string;
  code: string | null;
  description: string | null;
  address: string | null;
  archived: boolean;
  external_id: string | null;
}

export interface Stock {
  id: number;
  stock: number;
  in_transit: number;
  reserve: number;
  available: number;
  store: Store;
  external_id: string | null;
  last_sync_at: string | null;
}

// Analytics types
export interface DashboardMetrics {
  today_revenue: number;
  today_orders: number;
  today_customers: number;
  month_revenue: number;
  month_orders: number;
  month_new_customers: number;
  revenue_growth: number;
  orders_growth: number;
  customers_growth: number;
  low_stock_products: number;
  out_of_stock_products: number;
  top_products: TopProduct[];
  top_customers: TopCustomer[];
}

export interface TopProduct {
  id: number;
  name: string;
  revenue: number;
}

export interface TopCustomer {
  id: number;
  name: string;
  revenue: number;
}

// Organization types
export interface Organization {
  id: number;
  name: string;
  code: string | null;
  description: string | null;
  legal_title: string | null;
  legal_address: string | null;
  actual_address: string | null;
  inn: string | null;
  kpp: string | null;
  ogrn: string | null;
  okpo: string | null;
  email: string | null;
  phone: string | null;
  fax: string | null;
  bank_accounts: Record<string, any> | null;
  archived: boolean;
  shared: boolean;
  external_id: string | null;
  last_sync_at: string | null;
}

export interface Employee {
  id: number;
  first_name: string | null;
  middle_name: string | null;
  last_name: string;
  full_name: string;
  position: string | null;
  code: string | null;
  email: string | null;
  phone: string | null;
  archived: boolean;
  organization_id: number | null;
  external_id: string | null;
  last_sync_at: string | null;
}

export interface Project {
  id: number;
  name: string;
  code: string | null;
  description: string | null;
  archived: boolean;
  shared: boolean;
  external_id: string | null;
  last_sync_at: string | null;
}

export interface Contract {
  id: number;
  name: string;
  code: string | null;
  number: string | null;
  description: string | null;
  moment: string;
  contract_date: string | null;
  contract_type: string;
  sum_amount: number;
  reward_percent: number | null;
  reward_type: string | null;
  archived: boolean;
  counterparty_id: number | null;
  organization_id: number | null;
  project_id: number | null;
  external_id: string | null;
  last_sync_at: string | null;
}

export interface Currency {
  id: number;
  name: string;
  full_name: string | null;
  code: string;
  iso_code: string | null;
  is_default: boolean;
  multiplicity: number;
  rate: number;
  archived: boolean;
  external_id: string | null;
}

// Admin types
export interface IntegrationConfig {
  id: number;
  service_name: string;
  is_enabled: boolean;
  sync_interval_minutes: number;
  last_sync_at: string | null;
  next_sync_at: string | null;
  sync_status: string;
  error_message: string | null;
}

export interface SystemHealth {
  status: string;
  timestamp: string;
  database_status: string;
  redis_status: string;
  celery_status: string;
  integrations_status: Record<string, string>;
  active_users: number;
  pending_jobs: number;
  failed_jobs: number;
  avg_response_time_ms: number;
  memory_usage_percent: number | null;
  cpu_usage_percent: number | null;
  disk_usage_percent: number | null;
}

export interface SyncStatistics {
  statistics: Record<string, number>;
  total_records: number;
  last_sync: {
    job_id: string | null;
    status: string | null;
    started_at: string | null;
    completed_at: string | null;
  } | null;
}

// Pagination types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

// Report types
export interface ReportDashboard {
  status: string;
  data: any;
  timestamp: string;
}