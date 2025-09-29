import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';

// Auth hooks
export function useCurrentUser() {
  return useQuery({
    queryKey: ['currentUser'],
    queryFn: () => apiClient.getCurrentUser(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Products hooks
export function useProducts(params?: Record<string, any>) {
  return useQuery({
    queryKey: ['products', params],
    queryFn: () => apiClient.getProducts(params),
  });
}

export function useProduct(id: number) {
  return useQuery({
    queryKey: ['product', id],
    queryFn: () => apiClient.getProduct(id),
    enabled: !!id,
  });
}

export function useProductFolders() {
  return useQuery({
    queryKey: ['productFolders'],
    queryFn: () => apiClient.getProductFolders(),
  });
}

// Inventory hooks
export function useStock(params?: Record<string, any>) {
  return useQuery({
    queryKey: ['stock', params],
    queryFn: () => apiClient.getStock(params),
  });
}

export function useStores() {
  return useQuery({
    queryKey: ['stores'],
    queryFn: () => apiClient.getStores(),
  });
}

// Analytics hooks
export function useDashboardMetrics() {
  return useQuery({
    queryKey: ['dashboardMetrics'],
    queryFn: () => apiClient.getDashboardMetrics(),
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });
}

export function useSalesReport(params: Record<string, any>) {
  return useQuery({
    queryKey: ['salesReport', params],
    queryFn: () => apiClient.getSalesReport(params),
    enabled: !!params.period_type,
  });
}

export function useInventoryReport() {
  return useQuery({
    queryKey: ['inventoryReport'],
    queryFn: () => apiClient.getInventoryReport(),
  });
}

// Organizations hooks
export function useOrganizations(params?: Record<string, any>) {
  return useQuery({
    queryKey: ['organizations', params],
    queryFn: () => apiClient.getOrganizations(params),
  });
}

export function useEmployees(params?: Record<string, any>) {
  return useQuery({
    queryKey: ['employees', params],
    queryFn: () => apiClient.getEmployees(params),
  });
}

export function useProjects(params?: Record<string, any>) {
  return useQuery({
    queryKey: ['projects', params],
    queryFn: () => apiClient.getProjects(params),
  });
}

export function useContracts(params?: Record<string, any>) {
  return useQuery({
    queryKey: ['contracts', params],
    queryFn: () => apiClient.getContracts(params),
  });
}

export function useCurrencies() {
  return useQuery({
    queryKey: ['currencies'],
    queryFn: () => apiClient.getCurrencies(),
  });
}

// Reports hooks
export function useSalesDashboard() {
  return useQuery({
    queryKey: ['salesDashboard'],
    queryFn: () => apiClient.getSalesDashboard(),
  });
}

export function useOrdersDashboard() {
  return useQuery({
    queryKey: ['ordersDashboard'],
    queryFn: () => apiClient.getOrdersDashboard(),
  });
}

export function useMoneyDashboard() {
  return useQuery({
    queryKey: ['moneyDashboard'],
    queryFn: () => apiClient.getMoneyDashboard(),
  });
}

export function useProfitByProduct(dateFrom: string, dateTo: string) {
  return useQuery({
    queryKey: ['profitByProduct', dateFrom, dateTo],
    queryFn: () => apiClient.getProfitByProduct(dateFrom, dateTo),
    enabled: !!dateFrom && !!dateTo,
  });
}

export function useTurnoverReport(dateFrom?: string, dateTo?: string) {
  return useQuery({
    queryKey: ['turnoverReport', dateFrom, dateTo],
    queryFn: () => apiClient.getTurnoverReport(dateFrom, dateTo),
  });
}

export function useStockReport(storeId?: string) {
  return useQuery({
    queryKey: ['stockReport', storeId],
    queryFn: () => apiClient.getStockReport(storeId),
  });
}

// Admin hooks
export function useUsers(params?: Record<string, any>) {
  return useQuery({
    queryKey: ['users', params],
    queryFn: () => apiClient.getUsers(params),
  });
}

export function useIntegrations() {
  return useQuery({
    queryKey: ['integrations'],
    queryFn: () => apiClient.getIntegrations(),
  });
}

export function useSystemHealth() {
  return useQuery({
    queryKey: ['systemHealth'],
    queryFn: () => apiClient.getSystemHealth(),
    refetchInterval: 30 * 1000, // Refetch every 30 seconds
  });
}

export function useSyncStatistics() {
  return useQuery({
    queryKey: ['syncStatistics'],
    queryFn: () => apiClient.getSyncStatistics(),
  });
}

// Mutations
export function useUpdateIntegration() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ serviceName, data }: { serviceName: string; data: Record<string, any> }) =>
      apiClient.updateIntegration(serviceName, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
      toast.success('Интеграция обновлена');
    },
    onError: () => {
      toast.error('Ошибка обновления интеграции');
    },
  });
}

export function useTestIntegration() {
  return useMutation({
    mutationFn: (serviceName: string) => apiClient.testIntegration(serviceName),
    onSuccess: (data) => {
      if (data.success) {
        toast.success('Соединение успешно');
      } else {
        toast.error('Ошибка соединения');
      }
    },
    onError: () => {
      toast.error('Ошибка тестирования');
    },
  });
}

export function useStartSync() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      serviceName,
      jobType,
      forceFullSync,
    }: {
      serviceName: string;
      jobType?: string;
      forceFullSync?: boolean;
    }) => apiClient.startSync(serviceName, jobType, forceFullSync),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['syncStatistics'] });
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
      toast.success('Синхронизация запущена');
    },
    onError: () => {
      toast.error('Ошибка запуска синхронизации');
    },
  });
}