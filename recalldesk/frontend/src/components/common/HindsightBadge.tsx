import { Brain, AlertCircle, Wifi } from 'lucide-react';
import clsx from 'clsx';
import type { HindsightStatus } from '../../types';

interface Props {
  status: HindsightStatus;
  compact?: boolean;
}

export default function HindsightBadge({ status, compact }: Props) {
  if (compact) {
    return (
      <span className={clsx(
        'inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-xs font-medium',
        status.available
          ? 'bg-green-100 text-green-700'
          : 'bg-amber-100 text-amber-700'
      )}>
        <Brain className="w-3 h-3" />
        {status.available ? 'Hindsight' : 'Fallback'}
      </span>
    );
  }

  return (
    <div className={clsx(
      'flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium',
      status.available
        ? 'bg-green-50 text-green-700 border border-green-200'
        : 'bg-amber-50 text-amber-700 border border-amber-200'
    )}>
      {status.available ? (
        <><Brain className="w-3.5 h-3.5" />Hindsight Connected</>
      ) : (
        <><Wifi className="w-3.5 h-3.5" />Fallback Memory Mode</>
      )}
    </div>
  );
}
