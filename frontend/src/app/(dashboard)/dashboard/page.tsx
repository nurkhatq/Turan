'use client';

import { useDashboardMetrics } from '@/lib/hooks/use-api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/input-badge';
import { formatCurrency, formatNumber, formatPercent, getGrowthColor } from '@/lib/utils';
import {
  TrendingUp,
  TrendingDown,
  ShoppingCart,
  Users,
  DollarSign,
  AlertTriangle,
  Package,
  ArrowUp,
  ArrowDown,
} from 'lucide-react';
import { Loader2 } from 'lucide-react';

export default function DashboardPage() {
  const { data: metrics, isLoading, error } = useDashboardMetrics();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="mx-auto h-12 w-12 text-red-500" />
        <h3 className="mt-2 text-sm font-semibold">Ошибка загрузки данных</h3>
        <p className="mt-1 text-sm text-gray-500">Попробуйте обновить страницу</p>
      </div>
    );
  }

  const stats = [
    {
      name: 'Выручка за сегодня',
      value: formatCurrency(metrics?.today_revenue || 0),
      change: metrics?.revenue_growth || 0,
      icon: DollarSign,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      name: 'Заказов сегодня',
      value: formatNumber(metrics?.today_orders || 0),
      change: metrics?.orders_growth || 0,
      icon: ShoppingCart,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      name: 'Клиентов',
      value: formatNumber(metrics?.today_customers || 0),
      change: metrics?.customers_growth || 0,
      icon: Users,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      name: 'Низкий запас',
      value: formatNumber(metrics?.low_stock_products || 0),
      change: null,
      icon: Package,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Page header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Панель управления</h1>
        <p className="text-muted-foreground">Обзор ключевых показателей вашего бизнеса</p>
      </div>

      {/* Stats grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.name}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{stat.name}</CardTitle>
                <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`h-4 w-4 ${stat.color}`} />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                {stat.change !== null && (
                  <p className={`text-xs flex items-center mt-1 ${getGrowthColor(stat.change)}`}>
                    {stat.change > 0 ? (
                      <ArrowUp className="h-3 w-3 mr-1" />
                    ) : stat.change < 0 ? (
                      <ArrowDown className="h-3 w-3 mr-1" />
                    ) : null}
                    {formatPercent(Math.abs(stat.change))} {stat.change !== 0 ? 'от прошлого месяца' : ''}
                  </p>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Monthly overview */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Месячная выручка</CardTitle>
            <CardDescription>Общая выручка за текущий месяц</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{formatCurrency(metrics?.month_revenue || 0)}</div>
            <div className="mt-4 space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Заказов</span>
                <span className="font-medium">{formatNumber(metrics?.month_orders || 0)}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Новых клиентов</span>
                <span className="font-medium">{formatNumber(metrics?.month_new_customers || 0)}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Складские предупреждения</CardTitle>
            <CardDescription>Товары требующие внимания</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="p-2 rounded-lg bg-orange-50 mr-3">
                    <Package className="h-4 w-4 text-orange-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">Низкий запас</p>
                    <p className="text-xs text-muted-foreground">Требуется пополнение</p>
                  </div>
                </div>
                <Badge variant="warning">{metrics?.low_stock_products || 0}</Badge>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="p-2 rounded-lg bg-red-50 mr-3">
                    <AlertTriangle className="h-4 w-4 text-red-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">Нет в наличии</p>
                    <p className="text-xs text-muted-foreground">Отсутствует на складе</p>
                  </div>
                </div>
                <Badge variant="destructive">{metrics?.out_of_stock_products || 0}</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top performers */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Топ товаров</CardTitle>
            <CardDescription>Самые продаваемые товары</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {metrics?.top_products && metrics.top_products.length > 0 ? (
                metrics.top_products.map((product: any, index: number) => (
                  <div key={product.id} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-sm font-semibold text-blue-600 mr-3">
                        {index + 1}
                      </div>
                      <span className="text-sm font-medium">{product.name}</span>
                    </div>
                    <span className="text-sm text-muted-foreground">
                      {formatCurrency(product.revenue)}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">
                  Нет данных о продажах
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Топ клиентов</CardTitle>
            <CardDescription>Лучшие клиенты по выручке</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {metrics?.top_customers && metrics.top_customers.length > 0 ? (
                metrics.top_customers.map((customer: any, index: number) => (
                  <div key={customer.id} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center text-sm font-semibold text-purple-600 mr-3">
                        {index + 1}
                      </div>
                      <span className="text-sm font-medium">{customer.name}</span>
                    </div>
                    <span className="text-sm text-muted-foreground">
                      {formatCurrency(customer.revenue)}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">
                  Нет данных о клиентах
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}