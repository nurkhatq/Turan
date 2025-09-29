'use client';

import { useProduct, useStock } from '@/lib/hooks/use-api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/input-badge';
import { Button } from '@/components/ui/button';
import { formatCurrency, formatNumber, formatDate } from '@/lib/utils';
import { ArrowLeft, Package, Warehouse, DollarSign, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { useParams } from 'next/navigation';

export default function ProductDetailPage() {
  const params = useParams();
  const productId = Number(params.id);

  const { data: product, isLoading, error } = useProduct(productId);
  const { data: stockData } = useStock({ product_id: productId });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="space-y-6">
        <Link href="/products">
          <Button variant="outline">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Назад к товарам
          </Button>
        </Link>
        <Card>
          <CardContent className="py-12 text-center">
            <Package className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-semibold">Товар не найден</h3>
            <p className="mt-1 text-sm text-gray-500">
              Запрашиваемый товар не существует
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const stockItems = stockData?.items || [];
  const totalStock = stockItems.reduce((sum: number, item: any) => sum + parseFloat(item.available || 0), 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Link href="/products">
          <Button variant="outline">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Назад к товарам
          </Button>
        </Link>
        
        <Badge variant={product.archived ? 'secondary' : 'success'}>
          {product.archived ? 'Архивный' : 'Активный'}
        </Badge>
      </div>

      {/* Product info */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-2xl">{product.name}</CardTitle>
              {product.code && (
                <p className="text-sm text-muted-foreground mt-1">Код: {product.code}</p>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-2">
            {/* Basic info */}
            <div className="space-y-4">
              <h3 className="font-semibold">Основная информация</h3>
              
              <div className="space-y-2 text-sm">
                {product.article && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Артикул:</span>
                    <span className="font-medium">{product.article}</span>
                  </div>
                )}
                
                {product.folder && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Категория:</span>
                    <span className="font-medium">{product.folder.name}</span>
                  </div>
                )}
                
                {product.unit && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Единица измерения:</span>
                    <span className="font-medium">{product.unit.name}</span>
                  </div>
                )}
                
                {product.weight && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Вес:</span>
                    <span className="font-medium">{formatNumber(product.weight)} кг</span>
                  </div>
                )}
                
                {product.volume && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Объем:</span>
                    <span className="font-medium">{formatNumber(product.volume)} м³</span>
                  </div>
                )}

                {product.last_sync_at && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Последняя синхронизация:</span>
                    <span className="font-medium">{formatDate(product.last_sync_at)}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Pricing */}
            <div className="space-y-4">
              <h3 className="font-semibold">Ценообразование</h3>
              
              <div className="space-y-3">
                {product.sale_price !== null && (
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <DollarSign className="h-5 w-5 text-green-600 mr-2" />
                          <span className="text-sm text-muted-foreground">Цена продажи</span>
                        </div>
                        <span className="text-lg font-bold text-green-600">
                          {formatCurrency(product.sale_price)}
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                )}
                
                {product.buy_price !== null && (
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <DollarSign className="h-5 w-5 text-blue-600 mr-2" />
                          <span className="text-sm text-muted-foreground">Цена закупки</span>
                        </div>
                        <span className="text-lg font-bold text-blue-600">
                          {formatCurrency(product.buy_price)}
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                )}
                
                {product.min_price !== null && (
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <DollarSign className="h-5 w-5 text-orange-600 mr-2" />
                          <span className="text-sm text-muted-foreground">Минимальная цена</span>
                        </div>
                        <span className="text-lg font-bold text-orange-600">
                          {formatCurrency(product.min_price)}
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
          </div>

          {/* Description */}
          {product.description && (
            <div className="mt-6 pt-6 border-t">
              <h3 className="font-semibold mb-2">Описание</h3>
              <p className="text-sm text-muted-foreground">{product.description}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Variants */}
      {product.variants && product.variants.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Модификации</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {product.variants.map((variant: any) => (
                <Card key={variant.id}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="space-y-2 flex-1">
                        <h4 className="font-medium">{variant.name}</h4>
                        {variant.code && (
                          <p className="text-sm text-muted-foreground">Код: {variant.code}</p>
                        )}
                        {variant.characteristics && (
                          <div className="text-xs text-muted-foreground">
                            {JSON.stringify(variant.characteristics)}
                          </div>
                        )}
                      </div>
                      <div className="text-right space-y-1">
                        {variant.sale_price && (
                          <p className="font-semibold text-green-600">
                            {formatCurrency(variant.sale_price)}
                          </p>
                        )}
                        {variant.buy_price && (
                          <p className="text-sm text-muted-foreground">
                            Закупка: {formatCurrency(variant.buy_price)}
                          </p>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Stock by warehouse */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Остатки по складам</CardTitle>
            <div className="flex items-center">
              <Warehouse className="h-5 w-5 mr-2 text-muted-foreground" />
              <span className="text-lg font-bold">{formatNumber(totalStock)}</span>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {stockItems.length === 0 ? (
            <div className="text-center py-8">
              <Warehouse className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-2 text-sm text-muted-foreground">
                Нет данных об остатках
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {stockItems.map((item: any) => {
                const available = parseFloat(item.available || 0);
                const status = available <= 0 ? 'out' : available <= 10 ? 'low' : 'ok';

                return (
                  <Card key={item.id}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="space-y-1">
                          <h4 className="font-medium">{item.store?.name || 'Неизвестный склад'}</h4>
                          <div className="grid grid-cols-3 gap-4 text-sm">
                            <div>
                              <span className="text-muted-foreground">Остаток:</span>
                              <span className="ml-2 font-medium">{formatNumber(item.stock)}</span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">Резерв:</span>
                              <span className="ml-2 font-medium">{formatNumber(item.reserve)}</span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">Ожидание:</span>
                              <span className="ml-2 font-medium">{formatNumber(item.in_transit)}</span>
                            </div>
                          </div>
                        </div>
                        <div className="text-right space-y-2">
                          <p className="text-2xl font-bold">
                            {formatNumber(available)}
                          </p>
                          {status === 'out' && (
                            <Badge variant="destructive">Нет в наличии</Badge>
                          )}
                          {status === 'low' && (
                            <Badge variant="warning">Низкий запас</Badge>
                          )}
                          {status === 'ok' && (
                            <Badge variant="success">В наличии</Badge>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}