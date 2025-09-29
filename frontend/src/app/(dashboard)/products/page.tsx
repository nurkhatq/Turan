'use client';

import { useState } from 'react';
import { useProducts, useProductFolders } from '@/lib/hooks/use-api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input-badge';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/input-badge';
import { formatCurrency, formatDate } from '@/lib/utils';
import { Search, Package, Filter, Loader2 } from 'lucide-react';
import Link from 'next/link';

export default function ProductsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  
  const { data: productsData, isLoading } = useProducts({
    page,
    limit: 20,
    search: debouncedSearch,
  });

  const { data: folders } = useProductFolders();

  // Debounce search
  const handleSearch = (value: string) => {
    setSearch(value);
    const timer = setTimeout(() => {
      setDebouncedSearch(value);
      setPage(1);
    }, 500);
    return () => clearTimeout(timer);
  };

  const products = productsData?.items || [];
  const totalPages = productsData?.pages || 1;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Товары</h1>
        <p className="text-muted-foreground">Управление каталогом товаров</p>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Всего товаров</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{productsData?.total || 0}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Категорий</CardTitle>
            <Filter className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{folders?.length || 0}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Фильтры</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Поиск товаров..."
                value={search}
                onChange={(e) => handleSearch(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Products list */}
      <Card>
        <CardHeader>
          <CardTitle>Список товаров</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
            </div>
          ) : products.length === 0 ? (
            <div className="text-center py-12">
              <Package className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-semibold">Товары не найдены</h3>
              <p className="mt-1 text-sm text-gray-500">Попробуйте изменить параметры поиска</p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Desktop table */}
              <div className="hidden md:block overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-4 font-medium">Наименование</th>
                      <th className="text-left p-4 font-medium">Артикул</th>
                      <th className="text-left p-4 font-medium">Код</th>
                      <th className="text-right p-4 font-medium">Цена продажи</th>
                      <th className="text-left p-4 font-medium">Категория</th>
                      <th className="text-left p-4 font-medium">Статус</th>
                    </tr>
                  </thead>
                  <tbody>
                    {products.map((product: any) => (
                      <tr key={product.id} className="border-b hover:bg-muted/50">
                        <td className="p-4">
                          <Link
                            href={`/products/${product.id}`}
                            className="font-medium text-blue-600 hover:text-blue-800"
                          >
                            {product.name}
                          </Link>
                        </td>
                        <td className="p-4 text-sm text-muted-foreground">
                          {product.article || '—'}
                        </td>
                        <td className="p-4 text-sm text-muted-foreground">
                          {product.code || '—'}
                        </td>
                        <td className="p-4 text-right font-medium">
                          {product.sale_price ? formatCurrency(product.sale_price) : '—'}
                        </td>
                        <td className="p-4 text-sm text-muted-foreground">
                          {product.folder?.name || '—'}
                        </td>
                        <td className="p-4">
                          <Badge variant={product.archived ? 'secondary' : 'success'}>
                            {product.archived ? 'Архивный' : 'Активный'}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Mobile cards */}
              <div className="md:hidden space-y-4">
                {products.map((product: any) => (
                  <Card key={product.id}>
                    <CardContent className="p-4">
                      <div className="space-y-2">
                        <div className="flex items-start justify-between">
                          <Link
                            href={`/products/${product.id}`}
                            className="font-medium text-blue-600"
                          >
                            {product.name}
                          </Link>
                          <Badge variant={product.archived ? 'secondary' : 'success'}>
                            {product.archived ? 'Архивный' : 'Активный'}
                          </Badge>
                        </div>
                        
                        {product.article && (
                          <p className="text-sm text-muted-foreground">
                            Артикул: {product.article}
                          </p>
                        )}
                        
                        {product.sale_price && (
                          <p className="text-lg font-semibold">
                            {formatCurrency(product.sale_price)}
                          </p>
                        )}
                        
                        {product.folder && (
                          <p className="text-sm text-muted-foreground">
                            Категория: {product.folder.name}
                          </p>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
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