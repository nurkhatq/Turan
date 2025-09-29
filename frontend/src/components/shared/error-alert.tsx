import { AlertCircle } from 'lucide-react';
// Removed import of Alert, AlertDescription, and AlertTitle as they are defined below

export function Alert({
  title,
  description,
  variant = 'default',
}: {
  title?: string;
  description: string;
  variant?: 'default' | 'destructive';
}) {
  return (
    <div
      className={`p-4 rounded-lg border ${
        variant === 'destructive'
          ? 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800'
          : 'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800'
      }`}
    >
      <div className="flex">
        <div className="flex-shrink-0">
          <AlertCircle
            className={`h-5 w-5 ${
              variant === 'destructive' ? 'text-red-600' : 'text-blue-600'
            }`}
          />
        </div>
        <div className="ml-3">
          {title && (
            <h3
              className={`text-sm font-medium ${
                variant === 'destructive' ? 'text-red-800 dark:text-red-200' : 'text-blue-800 dark:text-blue-200'
              }`}
            >
              {title}
            </h3>
          )}
          <div
            className={`text-sm ${
              variant === 'destructive' ? 'text-red-700 dark:text-red-300' : 'text-blue-700 dark:text-blue-300'
            } ${title ? 'mt-2' : ''}`}
          >
            {description}
          </div>
        </div>
      </div>
    </div>
  );
}

export function AlertTitle({ children }: { children: React.ReactNode }) {
  return <h3 className="font-medium">{children}</h3>;
}

export function AlertDescription({ children }: { children: React.ReactNode }) {
  return <div className="text-sm">{children}</div>;
}
