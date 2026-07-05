interface EmptyStateProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
  icon?: React.ReactNode;
}

export function EmptyState({ title, description, action, icon }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-nexus-border px-6 py-14 text-center">
      {icon && <div className="text-nexus-muted">{icon}</div>}
      <p className="text-sm font-medium text-nexus-text">{title}</p>
      {description && <p className="max-w-sm text-sm text-nexus-muted">{description}</p>}
      {action}
    </div>
  );
}

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({ message = "Something went wrong loading this data.", onRetry }: ErrorStateProps) {
  return (
    <div
      role="alert"
      className="flex items-center justify-between gap-3 rounded-lg border border-nexus-red/30 bg-nexus-red/5 px-4 py-3 text-sm text-nexus-red"
    >
      <span>{message}</span>
      {onRetry && (
        <button
          onClick={onRetry}
          className="focus-ring shrink-0 rounded border border-nexus-red/40 px-2.5 py-1 text-xs font-medium hover:bg-nexus-red/10"
        >
          Retry
        </button>
      )}
    </div>
  );
}
