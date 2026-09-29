import { useState, useEffect } from 'react';
import { User, ChevronDown } from 'lucide-react';
import { getCustomers } from '../../services/api';
import type { Customer } from '../../types';
import clsx from 'clsx';

interface Props {
  value?: string;
  onChange: (customer: Customer) => void;
  className?: string;
}

const PLAN_COLORS: Record<string, string> = {
  free: 'badge-gray',
  starter: 'badge-blue',
  business: 'badge-purple',
  enterprise: 'badge-green',
};

export default function CustomerSelector({ value, onChange, className }: Props) {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [open, setOpen] = useState(false);
  const selected = customers.find(c => c.id === value);

  useEffect(() => {
    getCustomers().then(r => setCustomers(r.customers)).catch(() => {});
  }, []);

  return (
    <div className={clsx('relative', className)}>
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center gap-2 px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm hover:border-brand-400 transition-colors text-left"
      >
        <div className="w-6 h-6 rounded-full bg-brand-100 flex items-center justify-center flex-shrink-0">
          <User className="w-3 h-3 text-brand-600" />
        </div>
        {selected ? (
          <div className="flex-1 min-w-0">
            <div className="font-medium text-gray-900 truncate">{selected.name}</div>
            <div className="text-xs text-gray-400 truncate">{selected.company}</div>
          </div>
        ) : (
          <span className="text-gray-400 flex-1">Select customer…</span>
        )}
        <ChevronDown className="w-4 h-4 text-gray-400 flex-shrink-0" />
      </button>

      {open && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-lg max-h-72 overflow-y-auto scrollbar-thin animate-fade-in">
          {customers.map(c => (
            <button
              key={c.id}
              onClick={() => { onChange(c); setOpen(false); }}
              className={clsx(
                'w-full flex items-center gap-2 px-3 py-2.5 text-left hover:bg-gray-50 transition-colors',
                c.id === value && 'bg-brand-50'
              )}
            >
              <div className="w-7 h-7 rounded-full bg-brand-100 flex items-center justify-center flex-shrink-0 text-xs font-bold text-brand-600">
                {c.name.charAt(0)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-gray-900 truncate">{c.name}</div>
                <div className="text-xs text-gray-400 truncate">{c.company}</div>
              </div>
              <span className={PLAN_COLORS[c.plan]}>{c.plan}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
