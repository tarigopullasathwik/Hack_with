import { useEffect, useMemo, useState } from 'react';
import {
  Sparkles, Brain, Activity, MessageSquare, ArrowRight,
  Lightbulb, GitBranch, Play, RotateCcw, ChevronRight,
  ShieldCheck, TrendingUp,
} from 'lucide-react';
import {
  getDemoScenarios, getDemoStats, getCustomer, getMemoryTimeline,
} from '../services/api';
import type {
  DemoScenario, DemoStats, Customer, TimelineEntry,
  ActivityEntry, RecalledMemory, ScenarioTurn,
} from '../types';
import HindsightBadge from '../components/common/HindsightBadge';
import ScenarioCard from '../components/demo/ScenarioCard';
import CustomerProfile from '../components/demo/CustomerProfile';
import ChatWindow from '../components/chat/ChatWindow';
import ActivityFeed from '../components/chat/ActivityFeed';
import MemoryPanel from '../components/memory/MemoryPanel';
import MemoryTimeline from '../components/memory/MemoryTimeline';
import BeforeAfterPanel from '../components/memory/BeforeAfterPanel';

function parseTurns(raw?: string | ScenarioTurn[]): ScenarioTurn[] {
  if (!raw) return [];
  if (Array.isArray(raw)) return raw;
  try {
    const p = JSON.parse(raw);
    return Array.isArray(p) ? p : [];
  } catch {
    return [];
  }
}

export default function DemoPage() {
  const [scenarios, setScenarios] = useState<DemoScenario[]>([]);
  const [stats, setStats] = useState<DemoStats | null>(null);
  const [active, setActive] = useState<DemoScenario | null>(null);
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [timeline, setTimeline] = useState<TimelineEntry[]>([]);
  const [sessionId, setSessionId] = useState('demo-' + Date.now());
  const [activity, setActivity] = useState<ActivityEntry[]>([]);
  const [recalled, setRecalled] = useState<RecalledMemory[]>([]);
  const [injected, setInjected] = useState<{ text: string; nonce: number }>();
  const [walkthroughStep, setWalkthroughStep] = useState(0);

  useEffect(() => {
    getDemoScenarios().then(r => {
      setScenarios(r.scenarios);
      if (r.scenarios.length) selectScenario(r.scenarios[0]);
    }).catch(() => {});
    getDemoStats().then(setStats).catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const selectScenario = (s: DemoScenario) => {
    setActive(s);
    setSessionId('demo-' + s.id + '-' + Date.now());
    setActivity([]);
    setRecalled([]);
    getCustomer(s.customer_id).then(setCustomer).catch(() => setCustomer(null));
    getMemoryTimeline(s.customer_id).then(r => setTimeline(r.timeline)).catch(() => setTimeline([]));
  };

  const suggestedPrompts = useMemo(() => {
    const turns = parseTurns(active?.turns);
    const fromTurns = turns.filter(t => t.role === 'user').map(t => t.content);
    if (fromTurns.length) return fromTurns;
    return [
      "I'm having another billing problem — my payment keeps failing.",
      "The fix you gave me last time isn't the issue this time.",
      "This is urgent, I've tried everything already.",
    ];
  }, [active]);

  const send = (text: string) => setInjected({ text, nonce: Date.now() });
  const walkthrough = [
    { label: 'Set the scene', text: suggestedPrompts[0] ?? 'I am having another billing problem — my payment keeps failing.' },
    { label: 'Reveal memory', text: suggestedPrompts[1] ?? 'The fix you gave me last time is not the issue this time.' },
    { label: 'Show adaptation', text: suggestedPrompts[2] ?? 'This is urgent, I have tried everything already.' },
  ];
  const startWalkthrough = () => {
    setWalkthroughStep(1);
    send(walkthrough[0].text);
  };
  const nextWalkthroughStep = () => {
    const next = Math.min(walkthroughStep + 1, walkthrough.length);
    setWalkthroughStep(next);
    if (next > 0 && next <= walkthrough.length) send(walkthrough[next - 1].text);
  };
  const resetWalkthrough = () => {
    setWalkthroughStep(0);
    setActivity([]);
    setRecalled([]);
    setInjected(undefined);
  };

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-5">
      {/* Header */}
      <div className="flex items-start justify-between mb-4 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-brand-600" />
            <h1 className="text-xl font-bold text-gray-900">Demo Mode</h1>
            <span className="badge-purple">For judges</span>
          </div>
          <p className="text-sm text-gray-500 mt-0.5">
            Pick a scenario, send a message, and watch the agent recall past outcomes — and skip
            fixes that already failed for this customer.
          </p>
        </div>
        {stats && <HindsightBadge status={stats.hindsight_status} />}
      </div>

      {/* Presentation control deck */}
      <section className="mb-5 rounded-2xl bg-gray-950 text-white p-5 shadow-lg shadow-gray-200/50" aria-label="Presentation controls">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-5">
          <div className="max-w-xl">
            <div className="flex items-center gap-2 text-brand-300 text-xs font-semibold uppercase tracking-[0.16em]">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              Live product walkthrough
            </div>
            <h2 className="text-xl font-bold mt-2">Show how memory changes the next reply.</h2>
            <p className="text-sm text-gray-300 mt-1.5 leading-relaxed">
              Start the scripted customer journey, then advance through the moments where RecallDesk remembers what worked, what failed, and why.
            </p>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <button onClick={startWalkthrough} className="inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-semibold text-white hover:bg-brand-400 transition-colors">
              <Play className="w-4 h-4" /> Start walkthrough
            </button>
            <button onClick={nextWalkthroughStep} disabled={walkthroughStep === 0 || walkthroughStep >= walkthrough.length} className="inline-flex items-center gap-2 rounded-lg border border-gray-700 px-3 py-2.5 text-sm font-medium text-gray-200 hover:bg-gray-800 disabled:opacity-40 transition-colors">
              Next moment <ChevronRight className="w-4 h-4" />
            </button>
            <button onClick={resetWalkthrough} className="inline-flex items-center gap-2 rounded-lg px-3 py-2.5 text-sm font-medium text-gray-400 hover:text-white transition-colors" aria-label="Reset walkthrough">
              <RotateCcw className="w-4 h-4" /> Reset
            </button>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 mt-5">
          {walkthrough.map((step, index) => (
            <div key={step.label} className={`rounded-lg border px-3 py-2.5 ${walkthroughStep > index ? 'border-brand-400/60 bg-brand-500/15' : 'border-gray-800 bg-gray-900/60'}`}>
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-semibold text-gray-200">{step.label}</span>
                <span className="text-[10px] text-gray-500">0{index + 1}</span>
              </div>
              <p className="text-[11px] text-gray-400 mt-1 line-clamp-1">{step.text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Presenter proof points */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-5">
        <div className="card p-3.5 flex items-center gap-3"><ShieldCheck className="w-5 h-5 text-emerald-500" /><div><div className="text-xs text-gray-400">Memory safety</div><div className="text-sm font-semibold text-gray-900">Customer-scoped recall</div></div></div>
        <div className="card p-3.5 flex items-center gap-3"><Brain className="w-5 h-5 text-brand-500" /><div><div className="text-xs text-gray-400">What to highlight</div><div className="text-sm font-semibold text-gray-900">Past outcomes, not just facts</div></div></div>
        <div className="card p-3.5 flex items-center gap-3"><TrendingUp className="w-5 h-5 text-amber-500" /><div><div className="text-xs text-gray-400">Business impact</div><div className="text-sm font-semibold text-gray-900">Fewer repeated fixes</div></div></div>
      </div>

      {/* Scenario cards */}
      <div className="grid md:grid-cols-3 gap-3 mb-5">
        {scenarios.map(s => (
          <ScenarioCard key={s.id} scenario={s} onSelect={selectScenario} active={active?.id === s.id} />
        ))}
      </div>

      {active && (
        <>
          {/* Main working area */}
          <div className="grid grid-cols-1 xl:grid-cols-[280px_1fr_340px] gap-4 mb-5">
            {/* Left: profile + timeline */}
            <div className="space-y-4">
              {customer && <CustomerProfile customer={customer} />}
              <div className="card p-4">
                <div className="flex items-center gap-2 mb-3">
                  <GitBranch className="w-4 h-4 text-brand-500" />
                  <span className="text-sm font-semibold text-gray-900">Memory timeline</span>
                </div>
                <div className="max-h-[360px] overflow-y-auto scrollbar-thin pr-1">
                  <MemoryTimeline timeline={timeline} />
                </div>
              </div>
            </div>

            {/* Center: chat */}
            <div className="card flex flex-col h-[560px] overflow-hidden">
              <div className="flex items-center gap-2 px-4 py-2.5 border-b border-gray-100 flex-shrink-0">
                <MessageSquare className="w-4 h-4 text-brand-500" />
                <span className="text-sm font-semibold text-gray-900">Live conversation</span>
                <span className="memory-badge ml-auto"><Brain className="w-3 h-3" /> Memory active</span>
              </div>

              {/* Suggested prompts */}
              <div className="px-4 py-2 border-b border-gray-50 flex-shrink-0 bg-gray-50/50">
                <div className="flex items-center gap-1.5 mb-1.5">
                  <Lightbulb className="w-3 h-3 text-amber-400" />
                  <span className="text-xs font-medium text-gray-500">Try sending:</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {suggestedPrompts.slice(0, 3).map((p, i) => (
                    <button
                      key={i}
                      onClick={() => send(p)}
                      className="text-xs text-left px-2.5 py-1 rounded-lg bg-white border border-gray-200 text-gray-600 hover:border-brand-400 hover:text-brand-700 transition-colors"
                    >
                      {p.length > 60 ? p.slice(0, 60) + '…' : p}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex-1 min-h-0">
                <ChatWindow
                  customerId={active.customer_id}
                  sessionId={sessionId}
                  memoryMode="with_memory"
                  injected={injected}
                  onActivity={setActivity}
                  onMemoriesRecalled={setRecalled}
                />
              </div>
            </div>

            {/* Right: activity + memory */}
            <div className="space-y-4">
              <div className="card p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Activity className="w-4 h-4 text-brand-500" />
                  <span className="text-sm font-semibold text-gray-900">Agent activity</span>
                </div>
                <ActivityFeed activity={activity} />
              </div>
              <div className="card h-[300px]">
                <MemoryPanel
                  customerId={active.customer_id}
                  highlightedMemories={recalled.length > 0 ? recalled : undefined}
                />
              </div>
            </div>
          </div>

          {/* Before / After — the key moment */}
          <div className="card p-5">
            <BeforeAfterPanel customerId={active.customer_id} />
          </div>

          {/* How it works strip */}
          <div className="mt-5 flex items-center justify-center gap-2 text-xs text-gray-400 flex-wrap">
            {['Interaction', 'Retain', 'Recall', 'Learn', 'Adapt'].map((step, i, arr) => (
              <span key={step} className="flex items-center gap-2">
                <span className="px-2 py-1 rounded-md bg-gray-100 text-gray-600 font-medium">{step}</span>
                {i < arr.length - 1 && <ArrowRight className="w-3 h-3" />}
              </span>
            ))}
          </div>
        </>
      )}

      {!active && scenarios.length === 0 && (
        <div className="card p-12 text-center text-sm text-gray-400">
          Loading demo scenarios… ensure the backend is running on port 8000.
        </div>
      )}
    </div>
  );
}
