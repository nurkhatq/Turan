'use client';

import { useState } from 'react';
import { useEmployees, useOrganizations } from '@/lib/hooks/use-api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/input-badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input-badge';
import { formatDate } from '@/lib/utils';
import { Users, Search, Loader2, Mail, Phone, Briefcase, Building2 } from 'lucide-react';

export default function EmployeesPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [selectedOrg, setSelectedOrg] = useState<number | undefined>();

  const { data: employeesData, isLoading } = useEmployees({
    page,
    limit: 20,
    search: search || undefined,
    organization_id: selectedOrg,
  });

  const { data: organizations } = useOrganizations({ limit: 100 });

  const employees = employeesData?.items || [];
  const totalPages = employeesData?.pages || 1;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Сотрудники</h1>
        <p className="text-muted-foreground">Управление сотрудниками организаций</p>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Всего сотрудников</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{employeesData?.total || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Активных</CardTitle>
            <Users className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {employees.filter((e: any) => !e.archived).length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Организаций</CardTitle>
            <Building2 className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {new Set(employees.map((e: any) => e.organization_id).filter(Boolean)).size}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">С email</CardTitle>
            <Mail className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">
              {employees.filter((e: any) => e.email).length}
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
              placeholder="Поиск по имени..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="pl-10"
            />
          </div>

          {/* Organization filter */}
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
            {organizations?.items?.slice(0, 10).map((org: any) => (
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
        </CardContent>
      </Card>

      {/* Employees list */}
      <Card>
        <CardHeader>
          <CardTitle>Список сотрудников</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
            </div>
          ) : employees.length === 0 ? (
            <div className="text-center py-12">
              <Users className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-semibold">Сотрудники не найдены</h3>
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
                      <th className="text-left p-4 font-medium">Сотрудник</th>
                      <th className="text-left p-4 font-medium">Должность</th>
                      <th className="text-left p-4 font-medium">Контакты</th>
                      <th className="text-left p-4 font-medium">Организация</th>
                      <th className="text-left p-4 font-medium">Статус</th>
                      <th className="text-left p-4 font-medium">Обновлено</th>
                    </tr>
                  </thead>
                  <tbody>
                    {employees.map((employee: any) => (
                      <tr key={employee.id} className="border-b hover:bg-muted/50">
                        <td className="p-4">
                          <div className="flex items-center">
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-semibold mr-3">
                              {employee.first_name?.charAt(0) || employee.last_name?.charAt(0)}
                            </div>
                            <div>
                              <p className="font-medium">{employee.full_name}</p>
                              {employee.code && (
                                <p className="text-xs text-muted-foreground">
                                  Код: {employee.code}
                                </p>
                              )}
                            </div>
                          </div>
                        </td>
                        <td className="p-4">
                          {employee.position ? (
                            <div className="flex items-center text-sm">
                              <Briefcase className="h-4 w-4 mr-2 text-muted-foreground" />
                              {employee.position}
                            </div>
                          ) : (
                            <span className="text-sm text-muted-foreground">—</span>
                          )}
                        </td>
                        <td className="p-4">
                          <div className="space-y-1 text-sm">
                            {employee.email && (
                              <div className="flex items-center text-muted-foreground">
                                <Mail className="h-3 w-3 mr-2" />
                                {employee.email}
                              </div>
                            )}
                            {employee.phone && (
                              <div className="flex items-center text-muted-foreground">
                                <Phone className="h-3 w-3 mr-2" />
                                {employee.phone}
                              </div>
                            )}
                            {!employee.email && !employee.phone && (
                              <span className="text-muted-foreground">—</span>
                            )}
                          </div>
                        </td>
                        <td className="p-4">
                          {employee.organization_id ? (
                            <Badge variant="outline">
                              Орг. #{employee.organization_id}
                            </Badge>
                          ) : (
                            <span className="text-sm text-muted-foreground">—</span>
                          )}
                        </td>
                        <td className="p-4">
                          <Badge variant={employee.archived ? 'secondary' : 'success'}>
                            {employee.archived ? 'Архивный' : 'Активный'}
                          </Badge>
                        </td>
                        <td className="p-4 text-sm text-muted-foreground">
                          {employee.last_sync_at ? formatDate(employee.last_sync_at) : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Mobile cards */}
              <div className="md:hidden space-y-4">
                {employees.map((employee: any) => (
                  <Card key={employee.id}>
                    <CardContent className="p-4">
                      <div className="space-y-3">
                        <div className="flex items-start justify-between">
                          <div className="flex items-center">
                            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-semibold mr-3">
                              {employee.first_name?.charAt(0) || employee.last_name?.charAt(0)}
                            </div>
                            <div>
                              <p className="font-medium">{employee.full_name}</p>
                              {employee.position && (
                                <p className="text-sm text-muted-foreground">
                                  {employee.position}
                                </p>
                              )}
                            </div>
                          </div>
                          <Badge variant={employee.archived ? 'secondary' : 'success'}>
                            {employee.archived ? 'Архивный' : 'Активный'}
                          </Badge>
                        </div>

                        {(employee.email || employee.phone) && (
                          <div className="space-y-1 text-sm">
                            {employee.email && (
                              <div className="flex items-center text-muted-foreground">
                                <Mail className="h-3 w-3 mr-2" />
                                {employee.email}
                              </div>
                            )}
                            {employee.phone && (
                              <div className="flex items-center text-muted-foreground">
                                <Phone className="h-3 w-3 mr-2" />
                                {employee.phone}
                              </div>
                            )}
                          </div>
                        )}

                        {employee.organization_id && (
                          <Badge variant="outline">
                            Организация #{employee.organization_id}
                          </Badge>
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