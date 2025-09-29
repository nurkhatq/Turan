'use client';

import { useState } from 'react';
import { useTurnoverReport, useStockReport, useStores } from '@/lib/hooks/use-api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input-badge';
import { Badge } from '@/components/ui/input-badge';
import { formatCurrency, formatNumber, formatDate } from '@/lib/utils';
import { FileText, Download, Calendar, Warehouse, Loader2, TrendingUp } from 'lucide-react';

export default function AnalyticsReportsPage() {
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [selectedStore, setSelectedStore] = useState<string | undefined>();
  const [activeReport, setActiveReport] = useState<'turnover' | 'stock'>('turnover');

  const { data: turnoverData, isLoading: turnoverLoading } = useTurnoverReport(
    dateFrom || undefined,
    dateTo || undefined
  );

  const { data: stockData, isLoading: stockLoading } = useStockReport(selectedStore);
  const { data: stores } = useStores();

  const isLoading = activeReport === 'turnover' ? turnoverLoading : stockLoading;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Отчеты</h1>
        <p className="text-muted-foreground">Детальные отчеты по товарообороту и остаткам</p>
      </div>

      {/* Report type selector */}
      <Card>
        <CardHeader>
          <CardTitle>Тип отчета</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Button
              variant={activeReport === 'turnover' ? 'default' : 'outline'}
              onClick={() => setActiveReport('turnover')}
            >
              <TrendingUp className="mr-2 h-4 w-4" />
              Товарооборот
            </Button>
            <Button
              variant={activeReport === 'stock' ? 'default' : 'outline'}
              onClick={() => setActiveReport('stock')}
            >
              <Warehouse className="mr-2 h-4 w-4" />
              Остатки товаров
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Filters */}
      {activeReport === 'turnover' && (
        <Card>
          <CardHeader>
            <CardTitle>Фильтры</CardTitle>
            <CardDescription>Выберите период для отчета</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <label htmlFor="date-from" className="text-sm font-medium flex items-center">
                  <Calendar className="mr-2 h-4 w-4" />
                  Дата начала
                </label>
                <Input
                  id="date-from"
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <label htmlFor="date-to" className="text-sm font-medium flex items-center">
                  <Calendar className="mr-2 h-4 w-4" />
                  Дата окончания
                </label>
                <Input
                  id="date-to"
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {activeReport === 'stock' && (
        <Card>
          <CardHeader>
            <CardTitle>Фильтры</CardTitle>
            <CardDescription>Выберите склад для отчета</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              <Button
                variant={selectedStore === undefined ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedStore(undefined)}
              >
                Все склады
              </Button>
              {stores?.map((store: any) => (
                <Button
                  key={store.id}
                  variant={selectedStore === store.id.toString() ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedStore(store.id.toString())}
                >
                  {store.name}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Turnover Report */}
      {activeReport === 'turnover' && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Отчет по товарообороту</CardTitle>
                <CardDescription>
                  {dateFrom && dateTo
                    ? `Период: ${formatDate(dateFrom)} - ${formatDate(dateTo)}`
                    : 'Выберите период для отчета'}
                </CardDescription>
              </div>
              <Button variant="outline" size="sm">
                <Download className="mr-2 h-4 w-4" />
                Экспорт
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
              </div>
            ) : !turnoverData?.data ? (
              <div className="text-center py-12">
                <FileText className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-semibold">Нет данных</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Выберите период или проверьте интеграцию с МойСклад
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Summary */}
                {turnoverData.data.summary && (
                  <div className="grid gap-4 md:grid-cols-3">
                    {Object.entries(turnoverData.data.summary).map(([key, value]) => (
                      <Card key={key}>
                        <CardContent className="p-4">
                          <p className="text-sm text-muted-foreground capitalize">{key}</p>
                          <p className="text-2xl font-bold">
                            {typeof value === 'number'
                              ? formatCurrency(value / 100)
                              : String(value)}
                          </p>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}

                {/* Details */}
                {turnoverData.data.rows && Array.isArray(turnoverData.data.rows) && (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left p-4 font-medium">Товар</th>
                          <th className="text-right p-4 font-medium">Приход</th>
                          <th className="text-right p-4 font-medium">Расход</th>
                          <th className="text-right p-4 font-medium">Остаток</th>
                        </tr>
                      </thead>
                      <tbody>
                        {turnoverData.data.rows.slice(0, 20).map((row: any, index: number) => (
                          <tr key={index} className="border-b hover:bg-muted/50">
                            <td className="p-4">{row.product || row.name || `Товар ${index + 1}`}</td>
                            <td className="p-4 text-right text-green-600 font-medium">
                              {formatNumber(row.income || 0)}
                            </td>
                            <td className="p-4 text-right text-red-600 font-medium">
                              {formatNumber(row.outcome || 0)}
                            </td>
                            <td className="p-4 text-right font-semibold">
                              {formatNumber(row.balance || 0)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Stock Report */}
      {activeReport === 'stock' && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Отчет по остаткам</CardTitle>
                <CardDescription>
                  {selectedStore
                    ? `Склад: ${stores?.find((s: any) => s.id.toString() === selectedStore)?.name}`
                    : 'Все склады'}
                </CardDescription>
              </div>
              <Button variant="outline" size="sm">
                <Download className="mr-2 h-4 w-4" />
                Экспорт
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
              </div>
            ) : !stockData?.data ? (
              <div className="text-center py-12">
                <FileText className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-semibold">Нет данных</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Проверьте интеграцию с МойСклад
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Summary */}
                {stockData.data.summary && (
                  <div className="grid gap-4 md:grid-cols-4">
                    {Object.entries(stockData.data.summary).map(([key, value]) => (
                      <Card key={key}>
                        <CardContent className="p-4">
                          <p className="text-sm text-muted-foreground capitalize">
                            {key === 'total_products' && 'Всего товаров'}
                            {key === 'total_quantity' && 'Общее количество'}
                            {key === 'total_value' && 'Общая стоимость'}
                            {key === 'low_stock' && 'Низкий запас'}
                          </p>
                          <p className="text-2xl font-bold">
                            {key === 'total_value'
                              ? formatCurrency((value as number) / 100)
                              : formatNumber(value as number)}
                          </p>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}

                {/* Stock items */}
                {stockData.data.items && Array.isArray(stockData.data.items) && (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left p-4 font-medium">Товар</th>
                          <th className="text-left p-4 font-medium">Склад</th>
                          <th className="text-right p-4 font-medium">Количество</th>
                          <th className="text-right p-4 font-medium">Резерв</th>
                          <th className="text-right p-4 font-medium">Доступно</th>
                          <th className="text-left p-4 font-medium">Статус</th>
                        </tr>
                      </thead>
                      <tbody>
                        {stockData.data.items.slice(0, 50).map((item: any, index: number) => {
                          const available = item.available || 0;
                          const status = available <= 0 ? 'out' : available <= 10 ? 'low' : 'ok';

                          return (
                            <tr key={index} className="border-b hover:bg-muted/50">
                              <td className="p-4">{item.product || item.name}</td>
                              <td className="p-4 text-muted-foreground">{item.store || '—'}</td>
                              <td className="p-4 text-right">{formatNumber(item.stock || 0)}</td>
                              <td className="p-4 text-right text-muted-foreground">
                                {formatNumber(item.reserve || 0)}
                              </td>
                              <td className="p-4 text-right font-semibold">
                                {formatNumber(available)}
                              </td>
                              <td className="p-4">
                                {status === 'out' && (
                                  <Badge variant="destructive">Нет</Badge>
                                )}
                                {status === 'low' && (
                                  <Badge variant="warning">Мало</Badge>
                                )}
                                {status === 'ok' && (
                                  <Badge variant="success">Есть</Badge>
                                )}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}