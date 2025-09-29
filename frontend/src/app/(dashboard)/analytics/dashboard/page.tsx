'use client';

import { useSalesDashboard, useOrdersDashboard, useMoneyDashboard } from '@/lib/hooks/use-api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, TrendingUp, ShoppingCart, DollarSign, Users } from 'lucide-react';
import { formatCurrency, formatNumber, formatDate } from '@/lib/utils';

export default function AnalyticsDashboardPage() {
  const { data: salesData, isLoading: salesLoading } = useSalesDashboard();
  const { data: ordersData, isLoading: ordersLoading } = useOrdersDashboard();
  const { data: moneyData, isLoading: moneyLoading } = useMoneyDashboard();

  const isLoading = salesLoading || ordersLoading || moneyLoading;

  if (isLoading) {
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
        <h1 className="text-3xl font-bold tracking-tight">Аналитика</h1>
        <p className="text-muted-foreground">Детальная аналитика по продажам и финансам</p>
      </div>

      {/* Sales Dashboard */}
      {salesData?.data && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="mr-2 h-5 w-5" />
              Показатели продаж
            </CardTitle>
            <CardDescription>Данные из МойСклад</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {salesData.data.series && salesData.data.series.map((item: any, index: number) => (
                <div key={index} className="space-y-2">
                  <p className="text-sm text-muted-foreground">
                    {item.name || `Показатель ${index + 1}`}
                  </p>
                  <p className="text-2xl font-bold">
                    {typeof item.value === 'number' 
                      ? formatCurrency(item.value / 100) 
                      : item.value}
                  </p>
                </div>
              ))}
            </div>

            {salesData.data.context && (
              <div className="mt-4 pt-4 border-t text-sm text-muted-foreground">
                <p>Период: {salesData.data.context.period || 'Текущий'}</p>
                {salesData.data.context.lastUpdate && (
                  <p>Обновлено: {formatDate(salesData.data.context.lastUpdate)}</p>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Orders Dashboard */}
      {ordersData?.data && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <ShoppingCart className="mr-2 h-5 w-5" />
              Показатели заказов
            </CardTitle>
            <CardDescription>Статистика заказов</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {ordersData.data.series && ordersData.data.series.map((item: any, index: number) => (
                <div key={index} className="space-y-2">
                  <p className="text-sm text-muted-foreground">
                    {item.name || `Показатель ${index + 1}`}
                  </p>
                  <p className="text-2xl font-bold">
                    {typeof item.value === 'number' && item.name?.toLowerCase().includes('сумма')
                      ? formatCurrency(item.value / 100)
                      : formatNumber(item.value)}
                  </p>
                </div>
              ))}
            </div>

            {ordersData.data.context && (
              <div className="mt-4 pt-4 border-t text-sm text-muted-foreground">
                <p>Период: {ordersData.data.context.period || 'Текущий'}</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Money Dashboard */}
      {moneyData?.data && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <DollarSign className="mr-2 h-5 w-5" />
              Движение денежных средств
            </CardTitle>
            <CardDescription>Финансовые показатели</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {moneyData.data.series && moneyData.data.series.map((item: any, index: number) => (
                <div key={index} className="space-y-2">
                  <p className="text-sm text-muted-foreground">
                    {item.name || `Показатель ${index + 1}`}
                  </p>
                  <p className="text-2xl font-bold">
                    {typeof item.value === 'number'
                      ? formatCurrency(item.value / 100)
                      : item.value}
                  </p>
                </div>
              ))}
            </div>

            {moneyData.data.balance && (
              <div className="mt-4 pt-4 border-t">
                <h4 className="text-sm font-medium mb-3">Остатки на счетах</h4>
                <div className="space-y-2">
                  {Object.entries(moneyData.data.balance).map(([key, value]: [string, any]) => (
                    <div key={key} className="flex justify-between text-sm">
                      <span className="text-muted-foreground">{key}</span>
                      <span className="font-medium">
                        {typeof value === 'number' ? formatCurrency(value / 100) : value}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* No data message */}
      {!salesData?.data && !ordersData?.data && !moneyData?.data && (
        <Card>
          <CardContent className="py-12 text-center">
            <TrendingUp className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-semibold">Нет данных аналитики</h3>
            <p className="mt-1 text-sm text-gray-500">
              Проверьте интеграцию с МойСклад
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}