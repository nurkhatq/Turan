'use client';

import { useState } from 'react';
import {
  useIntegrations,
  useSystemHealth,
  useSyncStatistics,
  useTestIntegration,
  useStartSync,
  useUpdateIntegration,
} from '@/lib/hooks/use-api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/input-badge';
import { formatDateTime, getStatusColor } from '@/lib/utils';
import {
  RefreshCw,
  Check,
  X,
  Loader2,
  Settings,
  Activity,
  Database,
  Cloud,
} from 'lucide-react';
import { toast } from 'sonner';

export default function AdminIntegrationsPage() {
  const { data: integrations, isLoading: integrationsLoading } = useIntegrations();
  const { data: health } = useSystemHealth();
  const { data: stats } = useSyncStatistics();
  
  const testIntegration = useTestIntegration();
  const startSync = useStartSync();
  const updateIntegration = useUpdateIntegration();

  const [testingService, setTestingService] = useState<string | null>(null);
  const [syncingService, setSyncingService] = useState<string | null>(null);

  const handleTestConnection = async (serviceName: string) => {
    setTestingService(serviceName);
    try {
      await testIntegration.mutateAsync(serviceName);
    } finally {
      setTestingService(null);
    }
  };

  const handleStartSync = async (serviceName: string, forceFullSync: boolean = false) => {
    setSyncingService(serviceName);
    try {
      await startSync.mutateAsync({
        serviceName,
        jobType: forceFullSync ? 'full_sync' : 'incremental_sync',
        forceFullSync,
      });
    } finally {
      setSyncingService(null);
    }
  };

  const handleToggleIntegration = async (serviceName: string, currentStatus: boolean) => {
    try {
      await updateIntegration.mutateAsync({
        serviceName,
        data: { is_enabled: !currentStatus },
      });
    } catch (error) {
      toast.error('Ошибка обновления интеграции');
    }
  };

  if (integrationsLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Администрирование</h1>
        <p className="text-muted-foreground">Управление интеграциями и системой</p>
      </div>

      {/* System health */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">База данных</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center">
              {health?.database_status === 'healthy' ? (
                <Check className="h-5 w-5 text-green-600 mr-2" />
              ) : (
                <X className="h-5 w-5 text-red-600 mr-2" />
              )}
              <span className="font-medium">
                {health?.database_status === 'healthy' ? 'Работает' : 'Ошибка'}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Redis</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center">
              {health?.redis_status === 'healthy' ? (
                <Check className="h-5 w-5 text-green-600 mr-2" />
              ) : (
                <X className="h-5 w-5 text-red-600 mr-2" />
              )}
              <span className="font-medium">
                {health?.redis_status === 'healthy' ? 'Работает' : 'Ошибка'}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Celery</CardTitle>
            <Settings className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center">
              {health?.celery_status === 'healthy' ? (
                <Check className="h-5 w-5 text-green-600 mr-2" />
              ) : (
                <X className="h-5 w-5 text-red-600 mr-2" />
              )}
              <span className="font-medium">
                {health?.celery_status === 'healthy' ? 'Работает' : 'Ошибка'}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Sync statistics */}
      {stats && (
        <Card>
          <CardHeader>
            <CardTitle>Статистика синхронизации</CardTitle>
            <CardDescription>Данные синхронизированные из МойСклад</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-5">
              {Object.entries(stats.statistics || {}).map(([key, value]) => (
                <div key={key} className="space-y-1">
                  <p className="text-sm text-muted-foreground capitalize">
                    {key === 'organizations' && 'Организации'}
                    {key === 'employees' && 'Сотрудники'}
                    {key === 'projects' && 'Проекты'}
                    {key === 'contracts' && 'Договоры'}
                    {key === 'currencies' && 'Валюты'}
                    {key === 'countries' && 'Страны'}
                    {key === 'products' && 'Товары'}
                    {key === 'services' && 'Услуги'}
                    {key === 'counterparties' && 'Контрагенты'}
                    {key === 'stores' && 'Склады'}
                    {key === 'stock_records' && 'Остатки'}
                  </p>
                  <p className="text-2xl font-bold">{value as number}</p>
                </div>
              ))}
            </div>

            {stats.last_sync && (
              <div className="mt-4 pt-4 border-t">
                <h4 className="text-sm font-medium mb-2">Последняя синхронизация</h4>
                <div className="grid gap-2 md:grid-cols-2 text-sm">
                  <div>
                    <span className="text-muted-foreground">Статус:</span>
                    <Badge className={`ml-2 ${getStatusColor(stats.last_sync.status || 'inactive')}`}>
                      {stats.last_sync.status}
                    </Badge>
                  </div>
                  {stats.last_sync.completed_at && (
                    <div>
                      <span className="text-muted-foreground">Завершена:</span>
                      <span className="ml-2 font-medium">
                        {formatDateTime(stats.last_sync.completed_at)}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Integrations */}
      <div className="space-y-4">
        {integrations?.map((integration: any) => (
          <Card key={integration.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="p-2 rounded-lg bg-blue-50 dark:bg-blue-900">
                    <Cloud className="h-6 w-6 text-blue-600 dark:text-blue-300" />
                  </div>
                  <div>
                    <CardTitle className="capitalize">{integration.service_name}</CardTitle>
                    <CardDescription>
                      Интервал синхронизации: {integration.sync_interval_minutes} минут
                    </CardDescription>
                  </div>
                </div>
                <Badge className={getStatusColor(integration.sync_status)}>
                  {integration.sync_status}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Status info */}
                <div className="grid gap-4 md:grid-cols-2 text-sm">
                  <div>
                    <span className="text-muted-foreground">Включена:</span>
                    <span className="ml-2 font-medium">
                      {integration.is_enabled ? 'Да' : 'Нет'}
                    </span>
                  </div>
                  {integration.last_sync_at && (
                    <div>
                      <span className="text-muted-foreground">Последняя синхронизация:</span>
                      <span className="ml-2 font-medium">
                        {formatDateTime(integration.last_sync_at)}
                      </span>
                    </div>
                  )}
                  {integration.next_sync_at && (
                    <div>
                      <span className="text-muted-foreground">Следующая синхронизация:</span>
                      <span className="ml-2 font-medium">
                        {formatDateTime(integration.next_sync_at)}
                      </span>
                    </div>
                  )}
                  {integration.error_message && (
                    <div className="md:col-span-2">
                      <span className="text-red-600">Ошибка:</span>
                      <span className="ml-2 text-sm">{integration.error_message}</span>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex flex-wrap gap-2">
                  <Button
                    variant={integration.is_enabled ? 'destructive' : 'default'}
                    size="sm"
                    onClick={() =>
                      handleToggleIntegration(integration.service_name, integration.is_enabled)
                    }
                    disabled={updateIntegration.isPending}
                  >
                    {integration.is_enabled ? 'Отключить' : 'Включить'}
                  </Button>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleTestConnection(integration.service_name)}
                    disabled={testingService === integration.service_name}
                  >
                    {testingService === integration.service_name ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Тестирование...
                      </>
                    ) : (
                      'Проверить соединение'
                    )}
                  </Button>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleStartSync(integration.service_name, false)}
                    disabled={
                      syncingService === integration.service_name || !integration.is_enabled
                    }
                  >
                    {syncingService === integration.service_name ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Синхронизация...
                      </>
                    ) : (
                      <>
                        <RefreshCw className="mr-2 h-4 w-4" />
                        Инкрементальная синхронизация
                      </>
                    )}
                  </Button>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleStartSync(integration.service_name, true)}
                    disabled={
                      syncingService === integration.service_name || !integration.is_enabled
                    }
                  >
                    Полная синхронизация
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}