'use client';

import { useState } from 'react';
import { useUsers } from '@/lib/hooks/use-api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/input-badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input-badge';
import { formatDate } from '@/lib/utils';
import { Users, Shield, Search, Loader2, Mail, Clock, CheckCircle, XCircle } from 'lucide-react';

export default function AdminUsersPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');

  const { data: usersData, isLoading } = useUsers({
    page,
    limit: 20,
    search: search || undefined,
  });

  const users = usersData?.items || [];
  const totalPages = usersData?.pages || 1;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Пользователи</h1>
        <p className="text-muted-foreground">Управление пользователями системы</p>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Всего пользователей</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{usersData?.total || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Активных</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {users.filter((u: any) => u.is_active).length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Администраторов</CardTitle>
            <Shield className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {users.filter((u: any) => u.is_superuser).length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Неактивных</CardTitle>
            <XCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {users.filter((u: any) => !u.is_active).length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search */}
      <Card>
        <CardHeader>
          <CardTitle>Поиск</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Поиск по имени или email..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* Users list */}
      <Card>
        <CardHeader>
          <CardTitle>Список пользователей</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
            </div>
          ) : users.length === 0 ? (
            <div className="text-center py-12">
              <Users className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-semibold">Пользователи не найдены</h3>
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
                      <th className="text-left p-4 font-medium">Пользователь</th>
                      <th className="text-left p-4 font-medium">Email</th>
                      <th className="text-left p-4 font-medium">Роли</th>
                      <th className="text-left p-4 font-medium">Статус</th>
                      <th className="text-left p-4 font-medium">Последний вход</th>
                      <th className="text-left p-4 font-medium">Создан</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((user: any) => (
                      <tr key={user.id} className="border-b hover:bg-muted/50">
                        <td className="p-4">
                          <div className="flex items-center">
                            <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-semibold mr-3">
                              {user.full_name?.charAt(0) || user.email?.charAt(0)}
                            </div>
                            <div>
                              <p className="font-medium">{user.full_name || 'Без имени'}</p>
                              {user.is_superuser && (
                                <Badge variant="default" className="text-xs mt-1">
                                  <Shield className="h-3 w-3 mr-1" />
                                  Администратор
                                </Badge>
                              )}
                            </div>
                          </div>
                        </td>
                        <td className="p-4">
                          <div className="flex items-center text-sm text-muted-foreground">
                            <Mail className="h-4 w-4 mr-2" />
                            {user.email}
                          </div>
                        </td>
                        <td className="p-4">
                          <div className="flex flex-wrap gap-1">
                            {user.roles && user.roles.length > 0 ? (
                              user.roles.map((role: any) => (
                                <Badge key={role.id} variant="outline" className="text-xs">
                                  {role.name}
                                </Badge>
                              ))
                            ) : (
                              <span className="text-sm text-muted-foreground">—</span>
                            )}
                          </div>
                        </td>
                        <td className="p-4">
                          <Badge variant={user.is_active ? 'success' : 'destructive'}>
                            {user.is_active ? 'Активен' : 'Неактивен'}
                          </Badge>
                        </td>
                        <td className="p-4 text-sm text-muted-foreground">
                          {user.last_login_at ? (
                            <div className="flex items-center">
                              <Clock className="h-3 w-3 mr-1" />
                              {formatDate(user.last_login_at)}
                            </div>
                          ) : (
                            '—'
                          )}
                        </td>
                        <td className="p-4 text-sm text-muted-foreground">
                          {formatDate(user.created_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Mobile cards */}
              <div className="md:hidden space-y-4">
                {users.map((user: any) => (
                  <Card key={user.id}>
                    <CardContent className="p-4">
                      <div className="space-y-3">
                        <div className="flex items-start justify-between">
                          <div className="flex items-center">
                            <div className="w-12 h-12 rounded-full bg-blue-500 flex items-center justify-center text-white font-semibold mr-3">
                              {user.full_name?.charAt(0) || user.email?.charAt(0)}
                            </div>
                            <div>
                              <p className="font-medium">{user.full_name || 'Без имени'}</p>
                              <p className="text-sm text-muted-foreground">{user.email}</p>
                            </div>
                          </div>
                          <Badge variant={user.is_active ? 'success' : 'destructive'}>
                            {user.is_active ? 'Активен' : 'Неактивен'}
                          </Badge>
                        </div>

                        {user.is_superuser && (
                          <Badge variant="default">
                            <Shield className="h-3 w-3 mr-1" />
                            Администратор
                          </Badge>
                        )}

                        {user.roles && user.roles.length > 0 && (
                          <div>
                            <p className="text-xs text-muted-foreground mb-1">Роли:</p>
                            <div className="flex flex-wrap gap-1">
                              {user.roles.map((role: any) => (
                                <Badge key={role.id} variant="outline" className="text-xs">
                                  {role.name}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}

                        <div className="text-xs text-muted-foreground space-y-1">
                          {user.last_login_at && (
                            <div className="flex items-center">
                              <Clock className="h-3 w-3 mr-1" />
                              Последний вход: {formatDate(user.last_login_at)}
                            </div>
                          )}
                          <div>Создан: {formatDate(user.created_at)}</div>
                        </div>
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