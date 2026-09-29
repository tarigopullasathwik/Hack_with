import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Activity, Brain, RefreshCw, Zap, EyeOff } from 'lucide-react';
import { getCustomer } from '../services/api';
import type { Customer, MemoryMode, ActivityEntry, RecalledMemory } from '../types';
import CustomerSelector from '../components/common/CustomerSelector';
import CustomerProfile from '../components/demo/CustomerProfile';
import ChatWindow from '../components/chat/ChatWindow';
import ActivityFeed from '../components/chat/ActivityFeed';
import MemoryPanel from '../components/memory/MemoryPanel';
import clsx from 'clsx';

function newSession() {
  return (crypto.randomUUID?.() ?? `sess-${Date.now()}`);
}

export default function ChatPage() {
  const { customerId: routeId } = useParams();
  const [customerId, setCustomerId] = useState<string>(routeId ?? '');
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [sessionId, setSessionId] = useState(newSession());
  const [memoryMode, setMemoryMode] = useState<MemoryMode>('with_memory');
  const [activity, setActivity] = useState<ActivityEntry[]>([]);
  const [recalled, setRecalled] = useState<RecalledMemory[]>([]);

  useEffect(() => {
    if (!customerId) { setCustomer(null); return; }
    getCustomer(customerId).then(setCustomer).catch(() => setCustomer(null));
    setActivity([]);
    setRecalled([]);
  }, [customerId]);

  const resetSession = () => {
    setSessionId(newSession());
    setActivity([]);
    setRecalled([]);
  };

  return (
    <div className="h-full flex flex-col">
      {/* Top bar */}
      <div className="flex items-center gap-3 px-6 py-3 border-b border-gray-200 bg-white flex-shrink-0">
        <CustomerSelector value={customerId} onChange={c => { setCustomerId(c.id); resetSession(); }} className="w-64" />

        {/* Memory mode toggle */}
        <div className="flex items-center rounded-lg border border-gray-200 overflow-hidden text-xs font-medium">
          <button
            onClick={() => setMemoryMode('with_memory')}
            className={clsx('flex items-center gap-1.5 px-3 py-2 transition-colors',
              memoryMode === 'with_memory' ? 'bg-green-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50')}
          >
            <Brain className="w-3.5 h-3.5" /> With Memory
          </button>
          <button
            onClick={() => setMemoryMode('without_memory')}
            className={clsx('flex items-center gap-1.5 px-3 py-2 transition-colors',
              memoryMode === 'without_memory' ? 'bg-gray-700 text-white' : 'bg-white text-gray-600 hover:bg-gray-50')}
          >
            <EyeOff className="w-3.5 h-3.5" /> Without Memory
          </button>
        </div>

        <button onClick={resetSession} className="btn-ghost ml-auto" title="New session">
          <RefreshCw className="w-3.5 h-3.5" /> New session
        </button>
      </div>

      {/* Body */}
      <div className="flex-1 grid grid-cols-[260px_1fr_320px] min-h-0">
        {/* Left: profile */}
        <div className="border-r border-gray-200 bg-gray-50 overflow-y-auto scrollbar-thin p-3">
          {customer ? (
            <CustomerProfile customer={customer} />
          ) : (
            <div className="text-center text-xs text-gray-400 py-8">Select a customer.</div>
          )}
          <div className="mt-3 flex items-center gap-2 px-1">
            {memoryMode === 'with_memory'
              ? <span className="memory-badge"><Zap className="w-3 h-3" /> Memory active</span>
              : <span className="badge-yellow">Memory disabled</span>}
          </div>
        </div>

        {/* Center: chat */}
        <div className="min-w-0 bg-gray-50">
          <ChatWindow
            customerId={customerId}
            sessionId={sessionId}
            memoryMode={memoryMode}
            onActivity={setActivity}
            onMemoriesRecalled={setRecalled}
          />
        </div>

        {/* Right: activity + recalled memory */}
        <div className="border-l border-gray-200 bg-white overflow-y-auto scrollbar-thin flex flex-col">
          <div className="px-4 py-3 border-b border-gray-100 flex items-center gap-2">
            <Activity className="w-4 h-4 text-brand-500" />
            <span className="text-sm font-semibold text-gray-900">Agent Activity</span>
          </div>
          <div className="p-4">
            <ActivityFeed activity={activity} />
          </div>
          {customerId && (
            <div className="border-t border-gray-100 flex-1 min-h-[240px]">
              <MemoryPanel
                customerId={customerId}
                highlightedMemories={recalled.length > 0 ? recalled : undefined}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
