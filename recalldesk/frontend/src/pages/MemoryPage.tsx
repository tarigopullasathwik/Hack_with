import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Brain, GitBranch } from 'lucide-react';
import { getMemoryTimeline, getCustomer } from '../services/api';
import type { Customer, TimelineEntry } from '../types';
import CustomerSelector from '../components/common/CustomerSelector';
import CustomerProfile from '../components/demo/CustomerProfile';
import MemoryPanel from '../components/memory/MemoryPanel';
import MemoryTimeline from '../components/memory/MemoryTimeline';
import BeforeAfterPanel from '../components/memory/BeforeAfterPanel';

export default function MemoryPage() {
  const { customerId: routeId } = useParams();
  const [customerId, setCustomerId] = useState<string>(routeId ?? '');
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [timeline, setTimeline] = useState<TimelineEntry[]>([]);

  useEffect(() => {
    if (!customerId) return;
    getCustomer(customerId).then(setCustomer).catch(() => setCustomer(null));
    getMemoryTimeline(customerId).then(r => setTimeline(r.timeline)).catch(() => setTimeline([]));
  }, [customerId]);

  return (
    <div className="max-w-6xl mx-auto px-6 py-6">
      <div className="flex items-start justify-between mb-5 gap-4">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Memory</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Everything Hindsight remembers about this customer — and how it changes the agent's answers.
          </p>
        </div>
        <CustomerSelector
          value={customerId}
          onChange={c => setCustomerId(c.id)}
          className="w-64"
        />
      </div>

      {!customerId ? (
        <div className="card p-12 text-center">
          <Brain className="w-10 h-10 text-gray-300 mx-auto mb-3" />
          <p className="text-sm text-gray-500">Select a customer to inspect their memory bank.</p>
        </div>
      ) : (
        <div className="grid lg:grid-cols-[1fr_360px] gap-4">
          {/* Left: timeline + before/after */}
          <div className="space-y-4">
            <div className="card p-5">
              <div className="flex items-center gap-2 mb-4">
                <GitBranch className="w-4 h-4 text-brand-500" />
                <h2 className="text-sm font-semibold text-gray-900">Support timeline</h2>
                <span className="text-xs text-gray-400 ml-auto">Interaction → fix → outcome</span>
              </div>
              <MemoryTimeline timeline={timeline} />
            </div>

            <div className="card p-5">
              <BeforeAfterPanel customerId={customerId} />
            </div>
          </div>

          {/* Right: profile + memory bank */}
          <div className="space-y-4">
            {customer && <CustomerProfile customer={customer} />}
            <div className="card h-[520px]">
              <MemoryPanel customerId={customerId} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
