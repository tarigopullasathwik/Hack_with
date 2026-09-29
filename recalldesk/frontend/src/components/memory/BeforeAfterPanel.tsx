import { useState } from 'react';
import { Brain, EyeOff, Loader2, Zap, ArrowRight } from 'lucide-react';
import { compareBeforeAfter } from '../../services/api';
import type { BeforeAfterResult } from '../../types';

const DEMO_MESSAGES = [
  "I'm having trouble with my payment getting declined again.",
  "I'm experiencing issues with my SSO login.",
  "My files aren't syncing to the desktop client.",
  "I'm being charged twice this month.",
  "I can't access my workspace — getting locked out.",
];

interface Props {
  customerId: string;
}

export default function BeforeAfterPanel({ customerId }: Props) {
  const [message, setMessage] = useState('');
  const [result, setResult] = useState<BeforeAfterResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const run = async (msg?: string) => {
    const text = (msg ?? message).trim();
    if (!text || !customerId) return;
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const r = await compareBeforeAfter(customerId, text);
      setResult(r);
    } catch (e: unknown) {
      setError('Failed to run comparison. Ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Zap className="w-4 h-4 text-brand-500" />
        <h3 className="text-sm font-semibold text-gray-900">Before / After Comparison</h3>
        <span className="badge-purple ml-auto">Key Demo</span>
      </div>
      <p className="text-xs text-gray-500">
        Send the same message through both modes. See exactly how Hindsight memory changes the agent's response.
      </p>

      {/* Quick picks */}
      <div className="flex flex-wrap gap-1.5">
        {DEMO_MESSAGES.map((m, i) => (
          <button key={i} onClick={() => { setMessage(m); run(m); }}
            className="text-xs px-2.5 py-1 rounded-full bg-gray-100 text-gray-600 hover:bg-brand-50 hover:text-brand-700 transition-colors">
            {m.slice(0, 40)}…
          </button>
        ))}
      </div>

      {/* Custom input */}
      <div className="flex gap-2">
        <input
          value={message}
          onChange={e => setMessage(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && run()}
          placeholder="Type a customer message to compare…"
          className="flex-1 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-400"
        />
        <button onClick={() => run()} disabled={loading || !message.trim() || !customerId}
          className="btn-primary">
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Compare'}
        </button>
      </div>

      {error && <p className="text-xs text-red-600">{error}</p>}

      {/* Results */}
      {result && (
        <div className="grid grid-cols-2 gap-3 animate-fade-in">
          {/* Without Memory */}
          <div className="rounded-xl border border-gray-200 overflow-hidden">
            <div className="flex items-center gap-2 px-3 py-2 bg-gray-50 border-b border-gray-200">
              <EyeOff className="w-3.5 h-3.5 text-gray-500" />
              <span className="text-xs font-semibold text-gray-600">WITHOUT MEMORY</span>
              <span className="ml-auto badge-gray">Generic</span>
            </div>
            <div className="p-3">
              <div className="text-xs text-gray-500 mb-1">Memories recalled: 0</div>
              <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                {result.without_memory.response}
              </p>
            </div>
          </div>

          {/* With Memory */}
          <div className="rounded-xl border border-green-200 overflow-hidden bg-green-50/30">
            <div className="flex items-center gap-2 px-3 py-2 bg-green-50 border-b border-green-200">
              <Brain className="w-3.5 h-3.5 text-green-600" />
              <span className="text-xs font-semibold text-green-700">WITH HINDSIGHT</span>
              <span className="ml-auto memory-badge">{result.with_memory.memory_count} memories</span>
            </div>
            <div className="p-3">
              <div className="text-xs text-green-600 mb-1">
                {result.with_memory.memory_count} memories recalled from Hindsight
              </div>
              <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                {result.with_memory.response}
              </p>
              {result.with_memory.memories_recalled.length > 0 && (
                <div className="mt-3 space-y-1.5 pt-3 border-t border-green-200">
                  <div className="text-xs font-medium text-green-700 mb-1">Memories used:</div>
                  {result.with_memory.memories_recalled.slice(0, 3).map((m, i) => (
                    <div key={i} className="text-xs bg-white border border-green-100 rounded-md p-2 text-gray-600">
                      <span className="font-medium text-green-700 capitalize">[{m.type}]</span>{' '}
                      {m.text.slice(0, 100)}{m.text.length > 100 ? '…' : ''}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Arrow between */}
          <div className="col-span-2 flex items-center justify-center gap-3 text-xs text-gray-400">
            <span>Generic answer</span>
            <ArrowRight className="w-4 h-4 text-brand-400" />
            <span className="text-green-700 font-medium">Personalized with memory context</span>
          </div>
        </div>
      )}
    </div>
  );
}
