'use client';

import { useSystemHealth } from '@/lib/hooks/use-api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/input-badge';
import { formatDate, getStatusColor } from '@/lib/utils';
import {
  Activity,
  Database,
  HardDrive,
  Cpu,
  Server,
  Users,
  Clock,
  AlertCircle,
  CheckCircle,
  Loader2,
  RefreshCw,
} from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function AdminHealthPage() {
  const { data: health, isLoading, refetch } = useSystemHealth();

  const getHealthIcon = (status: string) => {
    if (status === 'healthy' || status === 'ok') {
      return <CheckCircle className="h-5 w-5 text-green-600" />;
    }
    return <AlertCircle className="h-5 w-5 text-red-600" />;
  };

  const getHealthBadgeVariant = (status: string) => {
    if (status === 'healthy' || status === 'ok') return 'success';
    if (status === 'degraded' || status === 'warning') return 'warning';
    return 'destructive';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Состояние системы</h1>
          <p className="text-muted-foreground">Мониторинг работоспособности компонентов</p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => refetch()}
          disabled={isLoading}
        >
          {isLoading ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <RefreshCw className="mr-2 h-4 w-4" />
          )}
          Обновить
        </Button>
      </div>

      {isLoading && !health ? (
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
        </div>
      ) : (
        <>
          {/* Overall status */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Общее состояние</CardTitle>
                  <CardDescription>
                    {health?.timestamp && `Обновлено: ${formatDate(health.timestamp, 'long')}`}
                  </CardDescription>
                </div>
                <Badge
                  variant={getHealthBadgeVariant(health?.status || 'unknown')}
                  className="text-lg px-4 py-2"
                >
                  {health?.status === 'healthy' && 'Работает нормально'}
                  {health?.status === 'degraded' && 'Частичный сбой'}
                  {health?.status === 'unhealthy' && 'Критическая ошибка'}
                  {!health?.status && 'Неизвестно'}
                </Badge>
              </div>
            </CardHeader>
          </Card>

          {/* Core components */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">База данных</CardTitle>
                <Database className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  {getHealthIcon(health?.database_status || 'unknown')}
                  <Badge variant={getHealthBadgeVariant(health?.database_status || 'unknown')}>
                    {health?.database_status || 'unknown'}
                  </Badge>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Redis</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  {getHealthIcon(health?.redis_status || 'unknown')}
                  <Badge variant={getHealthBadgeVariant(health?.redis_status || 'unknown')}>
                    {health?.redis_status || 'unknown'}
                  </Badge>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Celery</CardTitle>
                <RefreshCw className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  {getHealthIcon(health?.celery_status || 'unknown')}
                  <Badge variant={getHealthBadgeVariant(health?.celery_status || 'unknown')}>
                    {health?.celery_status || 'unknown'}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* System metrics */}
          <Card>
            <CardHeader>
              <CardTitle>Системные метрики</CardTitle>
              <CardDescription>Использование ресурсов сервера</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {/* CPU */}
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <Cpu className="h-4 w-4 text-blue-600 mr-2" />
                        <span className="text-sm font-medium">CPU</span>
                      </div>
                    </div>
                    <p className="text-2xl font-bold">
                      {health?.cpu_usage_percent !== null && health?.cpu_usage_percent !== undefined
                        ? `${health.cpu_usage_percent.toFixed(1)}%`
                        : 'N/A'}
                    </p>
                  </CardContent>
                </Card>

                {/* Memory */}
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <Server className="h-4 w-4 text-purple-600 mr-2" />
                        <span className="text-sm font-medium">Память</span>
                      </div>
                    </div>
                    <p className="text-2xl font-bold">
                      {health?.memory_usage_percent !== null && health?.memory_usage_percent !== undefined
                        ? `${health.memory_usage_percent.toFixed(1)}%`
                        : 'N/A'}
                    </p>
                  </CardContent>
                </Card>

                {/* Disk */}
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <HardDrive className="h-4 w-4 text-orange-600 mr-2" />
                        <span className="text-sm font-medium">Диск</span>
                      </div>
                    </div>
                    <p className="text-2xl font-bold">
                      {health?.disk_usage_percent !== null && health?.disk_usage_percent !== undefined
                        ? `${health.disk_usage_percent.toFixed(1)}%`
                        : 'N/A'}
                    </p>
                  </CardContent>
                </Card>

                {/* Response time */}
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 text-green-600 mr-2" />
                        <span className="text-sm font-medium">Отклик</span>
                      </div>
                    </div>
                    <p className="text-2xl font-bold">
                      {health?.avg_response_time_ms !== null && health?.avg_response_time_ms !== undefined
                        ? `${health.avg_response_time_ms.toFixed(0)}ms`
                        : 'N/A'}
                    </p>
                  </CardContent>
                </Card>
              </div>
            </CardContent>
          </Card>

          {/* Activity metrics */}
          <Card>
            <CardHeader>
              <CardTitle>Активность</CardTitle>
              <CardDescription>Текущая нагрузка на систему</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <Users className="h-4 w-4 text-blue-600 mr-2" />
                        <span className="text-sm font-medium">Активные пользователи</span>
                      </div>
                    </div>
                    <p className="text-2xl font-bold">
                      {health?.active_users !== null && health?.active_users !== undefined
                        ? health.active_users
                        : 0}
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 text-yellow-600 mr-2" />
                        <span className="text-sm font-medium">Задачи в очереди</span>
                      </div>
                    </div>
                    <p className="text-2xl font-bold">
                      {health?.pending_jobs !== null && health?.pending_jobs !== undefined
                        ? health.pending_jobs
                        : 0}
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <AlertCircle className="h-4 w-4 text-red-600 mr-2" />
                        <span className="text-sm font-medium">Ошибки</span>
                      </div>
                    </div>
                    <p className="text-2xl font-bold">
                      {health?.failed_jobs !== null && health?.failed_jobs !== undefined
                        ? health.failed_jobs
                        : 0}
                    </p>
                  </CardContent>
                </Card>
              </div>
            </CardContent>
          </Card>

          {/* Integrations status */}
          {health?.integrations_status && Object.keys(health.integrations_status).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Статус интеграций</CardTitle>
                <CardDescription>Состояние внешних сервисов</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(health.integrations_status).map(([name, status]) => (
                    <div key={name} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center">
                        <div className="flex items-center mr-4">
                          {getHealthIcon(status as string)}
                        </div>
                        <span className="font-medium capitalize">{name}</span>
                      </div>
                      <Badge variant={getHealthBadgeVariant(status as string)}>
                        {status as string}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Status legend */}
          <Card>
            <CardHeader>
              <CardTitle>Легенда статусов</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 text-sm">
                <div className="flex items-center">
                  <Badge variant="success" className="mr-2">healthy</Badge>
                  <span className="text-muted-foreground">Работает нормально</span>
                </div>
                <div className="flex items-center">
                  <Badge variant="warning" className="mr-2">degraded</Badge>
                  <span className="text-muted-foreground">Частичный сбой</span>
                </div>
                <div className="flex items-center">
                  <Badge variant="destructive" className="mr-2">unhealthy</Badge>
                  <span className="text-muted-foreground">Критическая ошибка</span>
                </div>
                <div className="flex items-center">
                  <Badge variant="secondary" className="mr-2">unknown</Badge>
                  <span className="text-muted-foreground">Неизвестно</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}