'use client';

import { useState } from 'react';
import { useContracts, useOrganizations } from '@/lib/hooks/use-api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/input-badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input-badge';
import { formatCurrency, formatDate } from '@/lib/utils';
import { FileText, Search, Loader2, Calendar, DollarSign, Building2 } from 'lucide-react';

export default function ContractsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [selectedOrg, setSelectedOrg] = useState<number | undefined>();
  const [contractType, setContractType] = useState<string | undefined>();

  const { data: contractsData, isLoading } = useContracts({
    page,
    limit: 20,
    search: search || undefined,
    organization_id: selectedOrg,
    contract_type: contractType,
  });

  const { data: organizations } = useOrganizations({ limit: 100 });

  const contracts = contractsData?.items || [];
  const totalPages = contractsData?.pages || 1;

  // Calculate stats
  const totalAmount = contracts.reduce((sum: number, c: any) => sum + (c.sum_amount || 0), 0);
  const activeContracts = contracts.filter((c: any) => !c.archived).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Договоры</h1>
        <p className="text-muted-foreground">Управление договорами и контрактами</p>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Всего договоров</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{contractsData?.total || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Активных</CardTitle>
            <FileText className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{activeContracts}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Общая сумма</CardTitle>
            <DollarSign className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {formatCurrency(totalAmount)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Средняя сумма</CardTitle>
            <DollarSign className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">
              {contracts.length > 0 ? formatCurrency(totalAmount / contracts.length) : '₽0'}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Фильтры</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Поиск по названию или номеру..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="pl-10"
            />
          </div>

          {/* Type filter */}
          <div>
            <p className="text-sm font-medium mb-2">Тип договора</p>
            <div className="flex flex-wrap gap-2">
              <Button
                variant={contractType === undefined ? 'default' : 'outline'}
                size="sm"
                onClick={() => {
                  setContractType(undefined);
                  setPage(1);
                }}
              >
                Все типы
              </Button>
              <Button
                variant={contractType === 'sales' ? 'default' : 'outline'}
                size="sm"
                onClick={() => {
                  setContractType('sales');
                  setPage(1);
                }}
              >
                Продажи
              </Button>
              <Button
                variant={contractType === 'purchase' ? 'default' : 'outline'}
                size="sm"
                onClick={() => {
                  setContractType('purchase');
                  setPage(1);
                }}
              >
                Закупки
              </Button>
            </div>
          </div>

          {/* Organization filter */}
          <div>
            <p className="text-sm font-medium mb-2">Организация</p>
            <div className="flex flex-wrap gap-2">
              <Button
                variant={selectedOrg === undefined ? 'default' : 'outline'}
                size="sm"
                onClick={() => {
                  setSelectedOrg(undefined);
                  setPage(1);
                }}
              >
                Все организации
              </Button>
              {organizations?.items?.slice(0, 5).map((org: any) => (
                <Button
                  key={org.id}
                  variant={selectedOrg === org.id ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => {
                    setSelectedOrg(org.id);
                    setPage(1);
                  }}
                >
                  {org.name}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Contracts list */}
      <Card>
        <CardHeader>
          <CardTitle>Список договоров</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
            </div>
          ) : contracts.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-semibold">Договоры не найдены</h3>
              <p className="mt-1 text-sm text-gray-500">
                Попробуйте изменить параметры поиска
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Desktop table */}
              <div className="hidden md:block overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-4 font-medium">Договор</th>
                      <th className="text-left p-4 font-medium">Номер</th>
                      <th className="text-left p-4 font-medium">Тип</th>
                      <th className="text-right p-4 font-medium">Сумма</th>
                      <th className="text-left p-4 font-medium">Дата</th>
                      <th className="text-left p-4 font-medium">Статус</th>
                    </tr>
                  </thead>
                  <tbody>
                    {contracts.map((contract: any) => (
                      <tr key={contract.id} className="border-b hover:bg-muted/50">
                        <td className="p-4">
                          <div>
                            <p className="font-medium">{contract.name}</p>
                            {contract.code && (
                              <p className="text-xs text-muted-foreground">
                                Код: {contract.code}
                              </p>
                            )}
                          </div>
                        </td>
                        <td className="p-4">
                          {contract.number ? (
                            <Badge variant="outline">{contract.number}</Badge>
                          ) : (
                            <span className="text-sm text-muted-foreground">—</span>
                          )}
                        </td>
                        <td className="p-4">
                          <Badge 
                            variant={contract.contract_type === 'sales' ? 'default' : 'secondary'}
                          >
                            {contract.contract_type === 'sales' ? 'Продажи' : 
                             contract.contract_type === 'purchase' ? 'Закупки' : 
                             contract.contract_type}
                          </Badge>
                        </td>
                        <td className="p-4 text-right">
                          <span className="font-semibold text-green-600">
                            {formatCurrency(contract.sum_amount)}
                          </span>
                        </td>
                        <td className="p-4">
                          <div className="flex items-center text-sm text-muted-foreground">
                            <Calendar className="h-3 w-3 mr-2" />
                            {formatDate(contract.moment)}
                          </div>
                        </td>
                        <td className="p-4">
                          <Badge variant={contract.archived ? 'secondary' : 'success'}>
                            {contract.archived ? 'Архивный' : 'Активный'}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Mobile cards */}
              <div className="md:hidden space-y-4">
                {contracts.map((contract: any) => (
                  <Card key={contract.id}>
                    <CardContent className="p-4">
                      <div className="space-y-3">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className="font-semibold">{contract.name}</h4>
                            {contract.number && (
                              <p className="text-sm text-muted-foreground mt-1">
                                № {contract.number}
                              </p>
                            )}
                          </div>
                          <Badge variant={contract.archived ? 'secondary' : 'success'}>
                            {contract.archived ? 'Архивный' : 'Активный'}
                          </Badge>
                        </div>

                        <div className="flex items-center justify-between">
                          <Badge 
                            variant={contract.contract_type === 'sales' ? 'default' : 'secondary'}
                          >
                            {contract.contract_type === 'sales' ? 'Продажи' : 
                             contract.contract_type === 'purchase' ? 'Закупки' : 
                             contract.contract_type}
                          </Badge>
                          <span className="text-lg font-bold text-green-600">
                            {formatCurrency(contract.sum_amount)}
                          </span>
                        </div>

                        <div className="flex items-center text-sm text-muted-foreground">
                          <Calendar className="h-3 w-3 mr-2" />
                          {formatDate(contract.moment)}
                        </div>

                        {contract.description && (
                          <p className="text-sm text-muted-foreground pt-2 border-t">
                            {contract.description}
                          </p>
                        )}

                        {contract.reward_percent && (
                          <div className="text-sm">
                            <span className="text-muted-foreground">Вознаграждение:</span>
                            <span className="ml-2 font-medium">
                              {contract.reward_percent}%
                            </span>
                          </div>
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