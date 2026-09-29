import { CheckCircle, XCircle, AlertTriangle, ArrowUpRight, Clock } from 'lucide-react';
import type { TimelineEntry } from '../../types';
import clsx from 'clsx';

const STATUS_CONFIG = {
  resolved:  { icon: CheckCircle, color: 'text-green-600',  dot: 'bg-green-500',  label: 'Resolved' },
  escalated: { icon: ArrowUpRight, color: 'text-orange-600', dot: 'bg-orange-500', label: 'Escalated' },
  open:      { icon: Clock,        color: 'text-blue-600',   dot: 'bg-blue-500',   label: 'Open' },
  closed:    { icon: CheckCircle,  color: 'text-gray-500',   dot: 'bg-gray-400',   label: 'Closed' },
  in_progress: { icon: Clock,      color: 'text-yellow-600', dot: 'bg-yellow-500', label: 'In Progress' },
  pending_customer: { icon: Clock, color: 'text-gray-500',   dot: 'bg-gray-400',   label: 'Pending' },
};

const CATEGORY_LABELS: Record<string, string> = {
  billing: 'Billing', login: 'Login', subscription: 'Subscription',
  integration: 'Integration', notifications: 'Notifications',
  file_sync: 'File Sync', permissions: 'Permissions', api: 'API',
  account: 'Account', other: 'Other',
};

interface Props {
  timeline: TimelineEntry[];
}

export default function MemoryTimeline({ timeline }: Props) {
  if (timeline.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400 text-sm">
        No interaction history yet.
      </div>
    );
  }

  return (
    <div className="relative">
      {/* Vertical line */}
      <div className="absolute left-3.5 top-2 bottom-2 w-0.5 bg-gray-200" />

      <div className="space-y-4">
        {timeline.map((entry, i) => {
          const cfg = STATUS_CONFIG[entry.status as keyof typeof STATUS_CONFIG] ?? STATUS_CONFIG.open;
          const Icon = cfg.icon;
          const failedSteps = entry.failed_steps ?? [];

          return (
            <div key={entry.ticket_id ?? i} className="flex gap-3 relative animate-fade-in">
              {/* Dot */}
              <div className={clsx('w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 z-10 bg-white border-2', {
                'border-green-400': entry.status === 'resolved',
                'border-orange-400': entry.status === 'escalated',
                'border-blue-400': entry.status === 'open' || entry.status === 'in_progress',
                'border-gray-300': !['resolved','escalated','open','in_progress'].includes(entry.status),
              })}>
                <Icon className={clsx('w-3.5 h-3.5', cfg.color)} />
              </div>

              {/* Content */}
              <div className="flex-1 pb-4">
                <div className="bg-white border border-gray-100 rounded-xl p-3 shadow-sm">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <span className="text-xs font-medium text-gray-400">{entry.date}</span>
                      <h4 className="text-sm font-medium text-gray-900 mt-0.5">{entry.title}</h4>
                    </div>
                    <div className="flex gap-1 flex-shrink-0">
                      <span className="badge-gray capitalize">{CATEGORY_LABELS[entry.category] ?? entry.category}</span>
                      <span className={clsx('badge capitalize', {
                        'badge-green': entry.status === 'resolved',
                        'badge-red':   entry.status === 'escalated',
                        'badge-blue':  entry.status === 'open',
                        'badge-yellow': entry.status === 'in_progress',
                        'badge-gray':  !['resolved','escalated','open','in_progress'].includes(entry.status),
                      })}>{cfg.label}</span>
                    </div>
                  </div>

                  {/* Steps */}
                  <div className="mt-2 space-y-1">
                    {failedSteps.map((step, j) => (
                      <div key={j} className="flex items-start gap-1.5 text-xs text-red-600">
                        <XCircle className="w-3 h-3 flex-shrink-0 mt-0.5" />
                        <span className="line-through opacity-70">{step}</span>
                        <span className="font-medium">(failed)</span>
                      </div>
                    ))}
                    {entry.successful_step && (
                      <div className="flex items-start gap-1.5 text-xs text-green-700">
                        <CheckCircle className="w-3 h-3 flex-shrink-0 mt-0.5" />
                        <span className="font-medium">{entry.successful_step}</span>
                      </div>
                    )}
                    {entry.escalated && (
                      <div className="flex items-start gap-1.5 text-xs text-orange-600">
                        <ArrowUpRight className="w-3 h-3 flex-shrink-0 mt-0.5" />
                        <span>Escalated to human support</span>
                      </div>
                    )}
                  </div>

                  {/* Memory indicator */}
                  {(entry.successful_step || failedSteps.length > 0) && (
                    <div className="mt-2 pt-2 border-t border-gray-50">
                      <span className="memory-badge">Memory retained in Hindsight</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
