import axios, { AxiosInstance, AxiosError } from 'axios';
import { useAuthStore } from '@/lib/store/auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_URL}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor - add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = useAuthStore.getState().token;
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - handle errors
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired, logout user
          useAuthStore.getState().logout();
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async login(email: string, password: string) {
    const response = await this.client.post('/auth/login', { email, password });
    return response.data;
  }

  async logout() {
    const response = await this.client.post('/auth/logout');
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.client.get('/auth/me');
    return response.data;
  }

  // Products
  async getProducts(params?: Record<string, any>) {
    const response = await this.client.get('/products/', { params });
    return response.data;
  }

  async getProduct(id: number) {
    const response = await this.client.get(`/products/${id}`);
    return response.data;
  }

  async getProductFolders() {
    const response = await this.client.get('/products/folders/');
    return response.data;
  }

  // Inventory
  async getStock(params?: Record<string, any>) {
    const response = await this.client.get('/inventory/stock', { params });
    return response.data;
  }

  async getStores() {
    const response = await this.client.get('/inventory/stores');
    return response.data;
  }

  // Analytics
  async getDashboardMetrics() {
    const response = await this.client.get('/analytics/dashboard');
    return response.data;
  }

  async getSalesReport(params: Record<string, any>) {
    const response = await this.client.get('/analytics/sales/report', { params });
    return response.data;
  }

  async getInventoryReport() {
    const response = await this.client.get('/analytics/inventory/report');
    return response.data;
  }

  // Organizations
  async getOrganizations(params?: Record<string, any>) {
    const response = await this.client.get('/organizations', { params });
    return response.data;
  }

  async getEmployees(params?: Record<string, any>) {
    const response = await this.client.get('/employees', { params });
    return response.data;
  }

  async getProjects(params?: Record<string, any>) {
    const response = await this.client.get('/projects', { params });
    return response.data;
  }

  async getContracts(params?: Record<string, any>) {
    const response = await this.client.get('/contracts', { params });
    return response.data;
  }

  async getCurrencies() {
    const response = await this.client.get('/currencies');
    return response.data;
  }

  // Reports
  async getSalesDashboard() {
    const response = await this.client.get('/reports/dashboard/sales');
    return response.data;
  }

  async getOrdersDashboard() {
    const response = await this.client.get('/reports/dashboard/orders');
    return response.data;
  }

  async getMoneyDashboard() {
    const response = await this.client.get('/reports/dashboard/money');
    return response.data;
  }

  async getProfitByProduct(dateFrom: string, dateTo: string) {
    const response = await this.client.get('/reports/profit/by-product', {
      params: { date_from: dateFrom, date_to: dateTo },
    });
    return response.data;
  }

  async getTurnoverReport(dateFrom?: string, dateTo?: string) {
    const response = await this.client.get('/reports/turnover', {
      params: { date_from: dateFrom, date_to: dateTo },
    });
    return response.data;
  }

  async getStockReport(storeId?: string) {
    const response = await this.client.get('/reports/stock/all', {
      params: { store_id: storeId },
    });
    return response.data;
  }

  // Admin
  async getUsers(params?: Record<string, any>) {
    const response = await this.client.get('/admin/users', { params });
    return response.data;
  }

  async getIntegrations() {
    const response = await this.client.get('/admin/integrations');
    return response.data;
  }

  async updateIntegration(serviceName: string, data: Record<string, any>) {
    const response = await this.client.put(`/admin/integrations/${serviceName}`, data);
    return response.data;
  }

  async testIntegration(serviceName: string) {
    const response = await this.client.post('/admin/integrations/test', null, {
      params: { service_name: serviceName },
    });
    return response.data;
  }

  async startSync(serviceName: string, jobType: string = 'full_sync', forceFullSync: boolean = false) {
    const response = await this.client.post('/admin/sync/start', {
      service_name: serviceName,
      job_type: jobType,
      force_full_sync: forceFullSync,
    });
    return response.data;
  }

  async getSystemHealth() {
    const response = await this.client.get('/admin/health');
    return response.data;
  }

  async getSyncStatistics() {
    const response = await this.client.get('/admin/sync/statistics');
    return response.data;
  }

  // Generic request method
  async request(method: string, url: string, data?: any, config?: any) {
    const response = await this.client.request({
      method,
      url,
      data,
      ...config,
    });
    return response.data;
  }
}

export const apiClient = new APIClient();