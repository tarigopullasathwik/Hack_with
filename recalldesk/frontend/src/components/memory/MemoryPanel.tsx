import { useEffect, useState } from 'react';
import { Brain, RefreshCw, AlertCircle, Clock, Tag } from 'lucide-react';
import { getCustomerMemories } from '../../services/api';
import type { MemoryItem } from '../../types';
import clsx from 'clsx';
import { formatDistanceToNow } from 'date-fns';

const TYPE_COLORS: Record<string, string> = {
  world:       'bg-blue-100 text-blue-700',
  experience:  'bg-green-100 text-green-700',
  observation: 'bg-purple-100 text-purple-700',
  unknown:     'bg-gray-100 text-gray-600',
};

interface Props {
  customerId: string;
  highlightedMemories?: MemoryItem[];
}

export default function MemoryPanel({ customerId, highlightedMemories }: Props) {
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [available, setAvailable] = useState(true);

  const load = () => {
    if (!customerId) return;
    setLoading(true);
    getCustomerMemories(customerId)
      .then(r => {
        setMemories(r.memories);
        setAvailable(r.hindsight_available);
      })
      .catch(() => setAvailable(false))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [customerId]);

  const displayMemories = highlightedMemories && highlightedMemories.length > 0
    ? highlightedMemories
    : memories;

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-brand-500" />
          <span className="text-sm font-semibold text-gray-900">Memory Bank</span>
          {displayMemories.length > 0 && (
            <span className="badge-green">{displayMemories.length}</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <span className={clsx(
            'badge text-xs',
            available ? 'badge-green' : 'badge-yellow'
          )}>
            {available ? 'Hindsight' : 'Fallback'}
          </span>
          <button onClick={load} className="btn-ghost p-1" title="Refresh">
            <RefreshCw className={clsx('w-3.5 h-3.5', loading && 'animate-spin')} />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-2 space-y-2 scrollbar-thin">
        {!available && (
          <div className="flex gap-2 items-start p-3 bg-amber-50 rounded-lg border border-amber-200 text-xs text-amber-700">
            <AlertCircle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
            <div>
              <strong>Memory unavailable for this request.</strong><br />
              Using in-process fallback store. Start a Hindsight server for full persistent memory.
            </div>
          </div>
        )}

        {displayMemories.length === 0 && !loading && (
          <div className="text-center py-8 text-gray-400 text-xs">
            No memories yet. Start a conversation to build memory.
          </div>
        )}

        {displayMemories.map((m, i) => (
          <div
            key={m.id ?? i}
            className={clsx(
              'p-3 rounded-lg border text-xs',
              highlightedMemories && highlightedMemories.length > 0
                ? 'bg-green-50 border-green-200 animate-slide-up'
                : 'bg-white border-gray-100'
            )}
          >
            {/* Type badge */}
            <div className="flex items-center gap-1.5 mb-1.5">
              <span className={clsx('badge text-xs', TYPE_COLORS[m.type] ?? TYPE_COLORS.unknown)}>
                {m.type}
              </span>
              {m.score !== undefined && m.score > 0 && (
                <span className="text-gray-400 text-xs">
                  relevance {(m.score * 100).toFixed(0)}%
                </span>
              )}
              {highlightedMemories && highlightedMemories.length > 0 && (
                <span className="ml-auto badge-green">recalled</span>
              )}
            </div>

            {/* Memory text */}
            <p className="text-gray-700 leading-relaxed">{m.text}</p>

            {/* Metadata */}
            <div className="mt-2 flex items-center gap-2 text-gray-400">
              {m.created_at && (
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {(() => {
                    try {
                      return formatDistanceToNow(new Date(m.created_at), { addSuffix: true });
                    } catch { return m.created_at; }
                  })()}
                </span>
              )}
              {m.context && (
                <span className="flex items-center gap-1 truncate">
                  <Tag className="w-3 h-3 flex-shrink-0" />
                  <span className="truncate">{m.context}</span>
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
