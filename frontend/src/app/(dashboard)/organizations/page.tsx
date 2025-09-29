'use client';

import { useState } from 'react';
import {
  useOrganizations,
  useEmployees,
  useProjects,
  useContracts,
  useCurrencies,
} from '@/lib/hooks/use-api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/input-badge';
import { Button } from '@/components/ui/button';
import { formatDate, formatCurrency } from '@/lib/utils';
import {
  Building2,
  Users,
  FileText,
  Briefcase,
  Loader2,
  Mail,
  Phone,
} from 'lucide-react';

type TabType = 'organizations' | 'employees' | 'projects' | 'contracts';

export default function OrganizationsPage() {
  const [activeTab, setActiveTab] = useState<TabType>('organizations');
  const [page, setPage] = useState(1);

  const { data: organizationsData, isLoading: orgsLoading } = useOrganizations({
    page,
    limit: 20,
  });

  const { data: employeesData, isLoading: empsLoading } = useEmployees({
    page,
    limit: 20,
  });

  const { data: projectsData, isLoading: projsLoading } = useProjects({
    page,
    limit: 20,
  });

  const { data: contractsData, isLoading: contractsLoading } = useContracts({
    page,
    limit: 20,
  });

  const { data: currencies } = useCurrencies();

  const tabs = [
    { id: 'organizations' as TabType, name: 'Организации', icon: Building2 },
    { id: 'employees' as TabType, name: 'Сотрудники', icon: Users },
    { id: 'projects' as TabType, name: 'Проекты', icon: Briefcase },
    { id: 'contracts' as TabType, name: 'Договоры', icon: FileText },
  ];

  const getActiveData = () => {
    switch (activeTab) {
      case 'organizations':
        return { data: organizationsData, isLoading: orgsLoading };
      case 'employees':
        return { data: employeesData, isLoading: empsLoading };
      case 'projects':
        return { data: projectsData, isLoading: projsLoading };
      case 'contracts':
        return { data: contractsData, isLoading: contractsLoading };
      default:
        return { data: null, isLoading: false };
    }
  };

  const { data, isLoading } = getActiveData();
  const items = data?.items || [];
  const totalPages = data?.pages || 1;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Организации и сотрудники</h1>
        <p className="text-muted-foreground">Управление организационной структурой</p>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Организации</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{organizationsData?.total || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Сотрудники</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{employeesData?.total || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Проекты</CardTitle>
            <Briefcase className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{projectsData?.total || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Договоры</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{contractsData?.total || 0}</div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Card>
        <CardHeader>
          <div className="flex flex-wrap gap-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <Button
                  key={tab.id}
                  variant={activeTab === tab.id ? 'default' : 'outline'}
                  onClick={() => {
                    setActiveTab(tab.id);
                    setPage(1);
                  }}
                >
                  <Icon className="mr-2 h-4 w-4" />
                  {tab.name}
                </Button>
              );
            })}
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
            </div>
          ) : items.length === 0 ? (
            <div className="text-center py-12">
              <Building2 className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-semibold">Нет данных</h3>
              <p className="mt-1 text-sm text-gray-500">
                Данные не найдены для выбранной категории
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Organizations */}
              {activeTab === 'organizations' && (
                <div className="space-y-4">
                  {items.map((org: any) => (
                    <Card key={org.id}>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="space-y-2 flex-1">
                            <div className="flex items-center">
                              <h3 className="font-semibold text-lg">{org.name}</h3>
                              {org.archived && (
                                <Badge variant="secondary" className="ml-2">
                                  Архивная
                                </Badge>
                              )}
                            </div>

                            {org.legal_title && (
                              <p className="text-sm text-muted-foreground">{org.legal_title}</p>
                            )}

                            <div className="grid gap-2 md:grid-cols-2 text-sm">
                              {org.inn && (
                                <div>
                                  <span className="text-muted-foreground">ИНН:</span>
                                  <span className="ml-2 font-medium">{org.inn}</span>
                                </div>
                              )}
                              {org.kpp && (
                                <div>
                                  <span className="text-muted-foreground">КПП:</span>
                                  <span className="ml-2 font-medium">{org.kpp}</span>
                                </div>
                              )}
                              {org.email && (
                                <div className="flex items-center">
                                  <Mail className="h-3 w-3 mr-1 text-muted-foreground" />
                                  <span className="text-muted-foreground">{org.email}</span>
                                </div>
                              )}
                              {org.phone && (
                                <div className="flex items-center">
                                  <Phone className="h-3 w-3 mr-1 text-muted-foreground" />
                                  <span className="text-muted-foreground">{org.phone}</span>
                                </div>
                              )}
                            </div>

                            {org.legal_address && (
                              <p className="text-sm text-muted-foreground">
                                Адрес: {org.legal_address}
                              </p>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}

              {/* Employees */}
              {activeTab === 'employees' && (
                <div className="space-y-4">
                  {items.map((emp: any) => (
                    <Card key={emp.id}>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="space-y-2 flex-1">
                            <div className="flex items-center">
                              <h3 className="font-semibold">{emp.full_name}</h3>
                              {emp.archived && (
                                <Badge variant="secondary" className="ml-2">
                                  Архивный
                                </Badge>
                              )}
                            </div>

                            {emp.position && (
                              <p className="text-sm text-muted-foreground">{emp.position}</p>
                            )}

                            <div className="grid gap-2 md:grid-cols-2 text-sm">
                              {emp.email && (
                                <div className="flex items-center">
                                  <Mail className="h-3 w-3 mr-1 text-muted-foreground" />
                                  <span className="text-muted-foreground">{emp.email}</span>
                                </div>
                              )}
                              {emp.phone && (
                                <div className="flex items-center">
                                  <Phone className="h-3 w-3 mr-1 text-muted-foreground" />
                                  <span className="text-muted-foreground">{emp.phone}</span>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}

              {/* Projects */}
              {activeTab === 'projects' && (
                <div className="space-y-4">
                  {items.map((project: any) => (
                    <Card key={project.id}>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="space-y-2 flex-1">
                            <div className="flex items-center">
                              <h3 className="font-semibold">{project.name}</h3>
                              {project.archived && (
                                <Badge variant="secondary" className="ml-2">
                                  Архивный
                                </Badge>
                              )}
                            </div>

                            {project.code && (
                              <p className="text-sm text-muted-foreground">Код: {project.code}</p>
                            )}

                            {project.description && (
                              <p className="text-sm text-muted-foreground">{project.description}</p>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}

              {/* Contracts */}
              {activeTab === 'contracts' && (
                <div className="space-y-4">
                  {items.map((contract: any) => (
                    <Card key={contract.id}>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="space-y-2 flex-1">
                            <div className="flex items-center">
                              <h3 className="font-semibold">{contract.name}</h3>
                              {contract.archived && (
                                <Badge variant="secondary" className="ml-2">
                                  Архивный
                                </Badge>
                              )}
                            </div>

                            <div className="grid gap-2 md:grid-cols-2 text-sm">
                              {contract.number && (
                                <div>
                                  <span className="text-muted-foreground">Номер:</span>
                                  <span className="ml-2 font-medium">{contract.number}</span>
                                </div>
                              )}
                              <div>
                                <span className="text-muted-foreground">Тип:</span>
                                <span className="ml-2 font-medium capitalize">
                                  {contract.contract_type === 'sales' ? 'Продажи' : contract.contract_type}
                                </span>
                              </div>
                              <div>
                                <span className="text-muted-foreground">Сумма:</span>
                                <span className="ml-2 font-semibold">
                                  {formatCurrency(contract.sum_amount)}
                                </span>
                              </div>
                              <div>
                                <span className="text-muted-foreground">Дата:</span>
                                <span className="ml-2">
                                  {formatDate(contract.moment)}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}

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