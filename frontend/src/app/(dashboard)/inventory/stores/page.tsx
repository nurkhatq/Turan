'use client';

import { useStores } from '@/lib/hooks/use-api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/input-badge';
import { Warehouse, MapPin, Loader2 } from 'lucide-react';

export default function StoresPage() {
  const { data: stores, isLoading } = useStores();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Склады</h1>
        <p className="text-muted-foreground">Управление складами и локациями</p>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Всего складов</CardTitle>
            <Warehouse className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stores?.length || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Активных</CardTitle>
            <Warehouse className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {stores?.filter((s: any) => !s.archived).length || 0}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Архивных</CardTitle>
            <Warehouse className="h-4 w-4 text-gray-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-600">
              {stores?.filter((s: any) => s.archived).length || 0}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Stores list */}
      <Card>
        <CardHeader>
          <CardTitle>Список складов</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
            </div>
          ) : !stores || stores.length === 0 ? (
            <div className="text-center py-12">
              <Warehouse className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-semibold">Склады не найдены</h3>
              <p className="mt-1 text-sm text-gray-500">
                Синхронизируйте данные с МойСклад
              </p>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {stores.map((store: any) => (
                <Card key={store.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="space-y-4">
                      {/* Header */}
                      <div className="flex items-start justify-between">
                        <div className="flex items-center">
                          <div className="p-2 rounded-lg bg-blue-50 dark:bg-blue-900 mr-3">
                            <Warehouse className="h-6 w-6 text-blue-600 dark:text-blue-300" />
                          </div>
                          <div>
                            <h3 className="font-semibold">{store.name}</h3>
                            {store.code && (
                              <p className="text-xs text-muted-foreground">
                                Код: {store.code}
                              </p>
                            )}
                          </div>
                        </div>
                        <Badge variant={store.archived ? 'secondary' : 'success'}>
                          {store.archived ? 'Архивный' : 'Активный'}
                        </Badge>
                      </div>

                      {/* Description */}
                      {store.description && (
                        <p className="text-sm text-muted-foreground">
                          {store.description}
                        </p>
                      )}

                      {/* Address */}
                      {store.address && (
                        <div className="flex items-start pt-2 border-t">
                          <MapPin className="h-4 w-4 text-muted-foreground mr-2 mt-0.5 flex-shrink-0" />
                          <p className="text-sm text-muted-foreground">
                            {store.address}
                          </p>
                        </div>
                      )}

                      {/* External ID */}
                      {store.external_id && (
                        <div className="text-xs text-muted-foreground pt-2 border-t">
                          ID: {store.external_id.substring(0, 20)}...
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}