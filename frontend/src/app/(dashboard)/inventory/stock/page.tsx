'use client';

import { useState } from 'react';
import { useStock, useStores } from '@/lib/hooks/use-api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/input-badge';
import { Button } from '@/components/ui/button';
import { formatNumber } from '@/lib/utils';
import { Package, Warehouse, AlertTriangle, Loader2, TrendingDown } from 'lucide-react';

export default function StockPage() {
  const [page, setPage] = useState(1);
  const [selectedStore, setSelectedStore] = useState<number | undefined>();

  const { data: stockData, isLoading } = useStock({
    page,
    limit: 50,
    store_id: selectedStore,
  });

  const { data: stores } = useStores();

  const stockItems = stockData?.items || [];
  const totalPages = stockData?.pages || 1;

  // Calculate stats
  const totalProducts = stockData?.total || 0;
  const lowStockCount = stockItems.filter((item: any) => item.available > 0 && item.available <= 10).length;
  const outOfStockCount = stockItems.filter((item: any) => item.available <= 0).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Складские остатки</h1>
        <p className="text-muted-foreground">Управление запасами товаров</p>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Всего позиций</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalProducts}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Складов</CardTitle>
            <Warehouse className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stores?.length || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Низкий запас</CardTitle>
            <TrendingDown className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{lowStockCount}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Нет в наличии</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{outOfStockCount}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Фильтры</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-center gap-2">
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
                variant={selectedStore === store.id ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedStore(store.id)}
              >
                {store.name}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Stock table */}
      <Card>
        <CardHeader>
          <CardTitle>Остатки на складах</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
            </div>
          ) : stockItems.length === 0 ? (
            <div className="text-center py-12">
              <Package className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-semibold">Остатки не найдены</h3>
              <p className="mt-1 text-sm text-gray-500">
                Попробуйте выбрать другой склад
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Desktop table */}
              <div className="hidden md:block overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-4 font-medium">Товар</th>
                      <th className="text-left p-4 font-medium">Склад</th>
                      <th className="text-right p-4 font-medium">Остаток</th>
                      <th className="text-right p-4 font-medium">Резерв</th>
                      <th className="text-right p-4 font-medium">Ожидание</th>
                      <th className="text-right p-4 font-medium">Доступно</th>
                      <th className="text-left p-4 font-medium">Статус</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stockItems.map((item: any) => {
                      const available = parseFloat(item.available);
                      const status = 
                        available <= 0 ? 'out' : 
                        available <= 10 ? 'low' : 
                        'ok';

                      return (
                        <tr key={item.id} className="border-b hover:bg-muted/50">
                          <td className="p-4 font-medium">
                            {item.product?.name || item.variant?.name || 'Неизвестный товар'}
                          </td>
                          <td className="p-4 text-sm text-muted-foreground">
                            {item.store?.name || '—'}
                          </td>
                          <td className="p-4 text-right">
                            {formatNumber(item.stock)}
                          </td>
                          <td className="p-4 text-right text-muted-foreground">
                            {formatNumber(item.reserve)}
                          </td>
                          <td className="p-4 text-right text-muted-foreground">
                            {formatNumber(item.in_transit)}
                          </td>
                          <td className="p-4 text-right font-semibold">
                            {formatNumber(available)}
                          </td>
                          <td className="p-4">
                            {status === 'out' && (
                              <Badge variant="destructive">Нет в наличии</Badge>
                            )}
                            {status === 'low' && (
                              <Badge variant="warning">Низкий запас</Badge>
                            )}
                            {status === 'ok' && (
                              <Badge variant="success">В наличии</Badge>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Mobile cards */}
              <div className="md:hidden space-y-4">
                {stockItems.map((item: any) => {
                  const available = parseFloat(item.available);
                  const status = 
                    available <= 0 ? 'out' : 
                    available <= 10 ? 'low' : 
                    'ok';

                  return (
                    <Card key={item.id}>
                      <CardContent className="p-4">
                        <div className="space-y-2">
                          <div className="flex items-start justify-between">
                            <h4 className="font-medium">
                              {item.product?.name || item.variant?.name}
                            </h4>
                            {status === 'out' && (
                              <Badge variant="destructive">Нет</Badge>
                            )}
                            {status === 'low' && (
                              <Badge variant="warning">Мало</Badge>
                            )}
                            {status === 'ok' && (
                              <Badge variant="success">Есть</Badge>
                            )}
                          </div>
                          
                          <p className="text-sm text-muted-foreground">
                            Склад: {item.store?.name}
                          </p>
                          
                          <div className="grid grid-cols-2 gap-2 text-sm">
                            <div>
                              <span className="text-muted-foreground">Остаток:</span>
                              <span className="ml-2 font-medium">{formatNumber(item.stock)}</span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">Доступно:</span>
                              <span className="ml-2 font-semibold">{formatNumber(available)}</span>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between pt-4">
                  <Button
                    variant="outline"
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                  >
                    Назад
                  </Button>
                  
                  <span className="text-sm text-muted-foreground">
                    Страница {page} из {totalPages}
                  </span>
                  
                  <Button
                    variant="outline"
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                  >
                    Вперёд
                  </Button>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}