import { Monitor, Globe, Package, Users, Star } from 'lucide-react';
import type { Customer } from '../../types';
import clsx from 'clsx';

const PLAN_BADGES: Record<string, string> = {
  free:       'badge-gray',
  starter:    'badge-blue',
  business:   'badge-purple',
  enterprise: 'badge-green',
};

interface Props {
  customer: Customer;
  ticketCount?: number;
}

export default function CustomerProfile({ customer, ticketCount }: Props) {
  return (
    <div className="card p-4 space-y-3">
      {/* Header */}
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-full bg-brand-100 flex items-center justify-center text-brand-700 font-bold text-sm flex-shrink-0">
          {customer.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-gray-900">{customer.name}</h3>
            <span className={clsx('badge capitalize', PLAN_BADGES[customer.plan])}>{customer.plan}</span>
          </div>
          <div className="text-xs text-gray-500">{customer.email}</div>
          {customer.company && (
            <div className="text-xs text-gray-400">{customer.company}</div>
          )}
        </div>
      </div>

      {/* Environment */}
      <div className="space-y-1.5 pt-2 border-t border-gray-50">
        {customer.browser && (
          <div className="flex items-center gap-2 text-xs text-gray-600">
            <Globe className="w-3.5 h-3.5 text-gray-400" />
            {customer.browser}
          </div>
        )}
        {customer.operating_system && (
          <div className="flex items-center gap-2 text-xs text-gray-600">
            <Monitor className="w-3.5 h-3.5 text-gray-400" />
            {customer.operating_system}
          </div>
        )}
        {customer.product_version && (
          <div className="flex items-center gap-2 text-xs text-gray-600">
            <Package className="w-3.5 h-3.5 text-gray-400" />
            Nexora v{customer.product_version}
          </div>
        )}
        {customer.workspace_size && (
          <div className="flex items-center gap-2 text-xs text-gray-600">
            <Users className="w-3.5 h-3.5 text-gray-400" />
            {customer.workspace_size}
          </div>
        )}
      </div>

      {/* Notes */}
      {customer.profile_notes && (
        <div className="pt-2 border-t border-gray-50">
          <div className="flex items-start gap-1.5">
            <Star className="w-3 h-3 text-amber-400 flex-shrink-0 mt-0.5" />
            <p className="text-xs text-gray-500 leading-relaxed">{customer.profile_notes}</p>
          </div>
        </div>
      )}

      {ticketCount !== undefined && (
        <div className="pt-2 border-t border-gray-50 flex items-center justify-between text-xs">
          <span className="text-gray-400">Support tickets</span>
          <span className="font-medium text-gray-700">{ticketCount}</span>
        </div>
      )}
    </div>
  );
}
