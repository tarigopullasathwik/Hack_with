import { useEffect, useState } from 'react';
import {
  Ticket as TicketIcon, CheckCircle, XCircle, ArrowUpRight,
  Clock, FileText, User,
} from 'lucide-react';
import { getTickets, getCustomers } from '../services/api';
import type { Ticket, Customer, TicketStatus } from '../types';
import clsx from 'clsx';

function parseSteps(raw?: string): string[] {
  if (!raw) return [];
  try {
    const p = JSON.parse(raw);
    if (Array.isArray(p)) return p.map(String);
  } catch { /* ignore */ }
  return raw.split(/\n/).map(s => s.trim()).filter(Boolean);
}

const STATUS_BADGE: Record<TicketStatus, string> = {
  open: 'badge-blue',
  in_progress: 'badge-yellow',
  pending_customer: 'badge-gray',
  escalated: 'badge-red',
  resolved: 'badge-green',
  closed: 'badge-gray',
};

const PRIORITY_BADGE: Record<string, string> = {
  low: 'badge-gray', medium: 'badge-blue', high: 'badge-yellow', critical: 'badge-red',
};

function TicketDetail({ ticket, customer }: { ticket: Ticket; customer?: Customer }) {
  const failed = parseSteps(ticket.failed_steps);

  return (
    <div className="card p-5 space-y-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="font-mono text-xs text-gray-400">{ticket.id}</span>
            <span className={clsx('badge capitalize', STATUS_BADGE[ticket.status])}>
              {ticket.status.replace(/_/g, ' ')}
            </span>
            <span className={clsx('badge capitalize', PRIORITY_BADGE[ticket.priority])}>{ticket.priority}</span>
          </div>
          <h2 className="text-base font-semibold text-gray-900">{ticket.title}</h2>
        </div>
        <span className="badge-gray capitalize flex-shrink-0">{ticket.category.replace(/_/g, ' ')}</span>
      </div>

      {customer && (
        <div className="flex items-center gap-2 text-sm text-gray-600 pt-1 border-t border-gray-50">
          <User className="w-3.5 h-3.5 text-gray-400" />
          {customer.name} · {customer.company} · <span className="capitalize">{customer.plan}</span>
        </div>
      )}

      {ticket.description && (
        <div>
          <div className="text-xs font-semibold text-gray-700 mb-1">Description</div>
          <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-wrap">{ticket.description}</p>
        </div>
      )}

      {/* Troubleshooting outcome — the memory-relevant part */}
      {(failed.length > 0 || ticket.successful_step) && (
        <div className="rounded-lg bg-gray-50 border border-gray-100 p-3 space-y-1.5">
          <div className="text-xs font-semibold text-gray-700 mb-1">Troubleshooting outcome</div>
          {failed.map((s, i) => (
            <div key={i} className="flex items-start gap-1.5 text-xs text-red-600">
              <XCircle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
              <span className="line-through opacity-70">{s}</span>
              <span className="font-medium">(failed)</span>
            </div>
          ))}
          {ticket.successful_step && (
            <div className="flex items-start gap-1.5 text-xs text-green-700">
              <CheckCircle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
              <span className="font-medium">{ticket.successful_step}</span>
              <span>(worked)</span>
            </div>
          )}
        </div>
      )}

      {ticket.resolution && (
        <div>
          <div className="text-xs font-semibold text-gray-700 mb-1">Resolution</div>
          <p className="text-sm text-gray-600 leading-relaxed">{ticket.resolution}</p>
        </div>
      )}

      {/* Escalation / handoff */}
      {ticket.status === 'escalated' && (
        <div className="rounded-lg bg-orange-50 border border-orange-200 p-3 space-y-2">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-orange-700">
            <ArrowUpRight className="w-3.5 h-3.5" />
            Escalated{ticket.escalated_to ? ` to ${ticket.escalated_to}` : ''}
          </div>
          {ticket.escalation_reason && (
            <p className="text-xs text-orange-700">{ticket.escalation_reason}</p>
          )}
          {ticket.handoff_summary && (
            <div className="pt-2 border-t border-orange-200">
              <div className="flex items-center gap-1.5 text-xs font-semibold text-orange-700 mb-1">
                <FileText className="w-3.5 h-3.5" />
                Human handoff summary
              </div>
              <pre className="text-xs text-gray-700 whitespace-pre-wrap font-sans leading-relaxed">
                {ticket.handoff_summary}
              </pre>
            </div>
          )}
        </div>
      )}

      <div className="flex items-center gap-4 text-xs text-gray-400 pt-1 border-t border-gray-50">
        {ticket.created_at && (
          <span className="flex items-center gap-1"><Clock className="w-3 h-3" />Created {ticket.created_at.slice(0, 10)}</span>
        )}
        {ticket.resolved_at && (
          <span className="flex items-center gap-1"><CheckCircle className="w-3 h-3" />Resolved {ticket.resolved_at.slice(0, 10)}</span>
        )}
      </div>
    </div>
  );
}

export default function TicketsPage() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [customers, setCustomers] = useState<Record<string, Customer>>({});
  const [selected, setSelected] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('all');
  const [error, setError] = useState(false);

  useEffect(() => {
    getTickets()
      .then(r => {
        setTickets(r.tickets);
        if (r.tickets.length) setSelected(r.tickets[0].id);
      })
      .catch(() => setError(true));
    getCustomers()
      .then(r => setCustomers(Object.fromEntries(r.customers.map(c => [c.id, c]))))
      .catch(() => {});
  }, []);

  const filtered = tickets.filter(t => filter === 'all' || t.status === filter);
  const active = tickets.find(t => t.id === selected);

  const filters = ['all', 'open', 'in_progress', 'escalated', 'resolved'];

  return (
    <div className="max-w-6xl mx-auto px-6 py-6">
      <div className="mb-5">
        <h1 className="text-xl font-bold text-gray-900">Tickets</h1>
        <p className="text-sm text-gray-500 mt-0.5">
          Support tickets with resolution outcomes. Escalated tickets carry a human handoff summary
          built from the customer's memory.
        </p>
      </div>

      <div className="flex gap-1.5 mb-4 flex-wrap">
        {filters.map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={clsx(
              'text-xs px-2.5 py-1 rounded-full capitalize transition-colors',
              filter === f ? 'bg-brand-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            )}
          >
            {f.replace(/_/g, ' ')}
          </button>
        ))}
      </div>

      {error && <div className="card p-4 text-sm text-red-600">Could not load tickets.</div>}

      <div className="grid md:grid-cols-[320px_1fr] gap-4">
        {/* List */}
        <div className="space-y-1.5 max-h-[70vh] overflow-y-auto scrollbar-thin pr-1">
          {filtered.map(t => (
            <button
              key={t.id}
              onClick={() => setSelected(t.id)}
              className={clsx(
                'w-full text-left p-3 rounded-lg border transition-colors',
                t.id === selected ? 'bg-brand-50 border-brand-300' : 'bg-white border-gray-100 hover:border-gray-300'
              )}
            >
              <div className="flex items-center gap-2 mb-1">
                <TicketIcon className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                <span className="font-mono text-xs text-gray-400">{t.id}</span>
                <span className={clsx('badge capitalize ml-auto', STATUS_BADGE[t.status])}>
                  {t.status.replace(/_/g, ' ')}
                </span>
              </div>
              <div className="text-sm font-medium text-gray-800 line-clamp-1">{t.title}</div>
              <div className="text-xs text-gray-400">{customers[t.customer_id]?.name ?? t.customer_id}</div>
            </button>
          ))}
          {filtered.length === 0 && !error && (
            <div className="text-center py-8 text-gray-400 text-sm">No tickets in this view.</div>
          )}
        </div>

        {/* Detail */}
        <div>
          {active ? (
            <TicketDetail ticket={active} customer={customers[active.customer_id]} />
          ) : (
            <div className="card p-8 text-center text-gray-400 text-sm">Select a ticket to view details.</div>
          )}
        </div>
      </div>
    </div>
  );
}
