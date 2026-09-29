import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Users, Ticket as TicketIcon, CheckCircle, ArrowUpRight,
  MessageSquare, Brain, PlayCircle, ArrowRight,
} from 'lucide-react';
import { getDemoStats } from '../services/api';
import type { DemoStats } from '../types';
import HindsightBadge from '../components/common/HindsightBadge';

interface StatCard {
  label: string;
  value: number | string;
  icon: React.ElementType;
  tone: string;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DemoStats | null>(null);
  const [error, setError] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    getDemoStats().then(setStats).catch(() => setError(true));
  }, []);

  const cards: StatCard[] = stats
    ? [
        { label: 'Customers', value: stats.total_customers, icon: Users, tone: 'bg-brand-50 text-brand-600' },
        { label: 'Support tickets', value: stats.total_tickets, icon: TicketIcon, tone: 'bg-blue-50 text-blue-600' },
        { label: 'Resolved', value: stats.resolved_tickets, icon: CheckCircle, tone: 'bg-green-50 text-green-600' },
        { label: 'Escalated', value: stats.escalated_tickets, icon: ArrowUpRight, tone: 'bg-orange-50 text-orange-600' },
        { label: 'Messages logged', value: stats.total_messages, icon: MessageSquare, tone: 'bg-purple-50 text-purple-600' },
      ]
    : [];

  return (
    <div className="max-w-6xl mx-auto px-6 py-6">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            RecallDesk — support that remembers what happened.
          </p>
        </div>
        {stats && <HindsightBadge status={stats.hindsight_status} />}
      </div>

      {error && (
        <div className="card p-4 mb-6 text-sm text-red-600">
          Could not reach the backend. Ensure the API is running on port 8000.
        </div>
      )}

      {/* Stat grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
        {cards.map(c => {
          const Icon = c.icon;
          return (
            <div key={c.label} className="card p-4">
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center mb-3 ${c.tone}`}>
                <Icon className="w-4 h-4" />
              </div>
              <div className="text-2xl font-bold text-gray-900">{c.value}</div>
              <div className="text-xs text-gray-500 mt-0.5">{c.label}</div>
            </div>
          );
        })}
      </div>

      {/* Memory concept explainer */}
      <div className="grid md:grid-cols-2 gap-4 mb-6">
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-2">
            <Brain className="w-4 h-4 text-green-600" />
            <h2 className="text-sm font-semibold text-gray-900">Customer memory (Hindsight)</h2>
          </div>
          <p className="text-xs text-gray-500 leading-relaxed">
            Persistent, customer-specific experience: what problems occurred, which fixes
            worked, which failed, preferences, and outcomes. The agent recalls this at the
            start of every conversation and adapts its recommendations accordingly.
          </p>
        </div>
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-2">
            <MessageSquare className="w-4 h-4 text-blue-600" />
            <h2 className="text-sm font-semibold text-gray-900">Product knowledge base</h2>
          </div>
          <p className="text-xs text-gray-500 leading-relaxed">
            General, non-personal product documentation — troubleshooting articles that apply
            to every customer. Combined with memory, the agent skips fixes that already failed
            for this specific customer.
          </p>
        </div>
      </div>

      {/* CTA to demo */}
      <button
        onClick={() => navigate('/demo')}
        className="w-full card p-5 flex items-center gap-4 text-left hover:shadow-md transition-shadow group"
      >
        <div className="w-10 h-10 rounded-xl bg-brand-600 flex items-center justify-center flex-shrink-0">
          <PlayCircle className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <div className="text-sm font-semibold text-gray-900">Open Demo Mode</div>
          <div className="text-xs text-gray-500">
            Watch the agent recall a previous resolution and avoid a fix that already failed.
          </div>
        </div>
        <ArrowRight className="w-5 h-5 text-gray-300 group-hover:text-brand-500 transition-colors" />
      </button>
    </div>
  );
}
