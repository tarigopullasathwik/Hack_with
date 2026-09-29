import { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Loader2, Brain, ChevronDown, ChevronUp, AlertCircle, CheckCircle, ArrowUpRight } from 'lucide-react';
import { sendMessage } from '../../services/api';
import type { ChatMessage, RecalledMemory, MemoryMode, ActivityEntry, ToolCall, ChatResponse } from '../../types';
import clsx from 'clsx';
import { formatDistanceToNow } from 'date-fns';

interface Props {
  customerId: string;
  sessionId: string;
  memoryMode: MemoryMode;
  onActivity?: (activity: ActivityEntry[]) => void;
  onMemoriesRecalled?: (memories: RecalledMemory[]) => void;
  onMemoryRetained?: (retained: boolean) => void;
  onOutcome?: (outcome: string, ticketId?: string | null) => void;
  /** When nonce changes, the given text is sent automatically (used by Demo Mode). */
  injected?: { text: string; nonce: number };
}

function MemoryPill({ memories, count }: { memories: RecalledMemory[]; count: number }) {
  const [expanded, setExpanded] = useState(false);
  if (count === 0) return null;

  return (
    <div className="mb-2">
      <button
        onClick={() => setExpanded(e => !e)}
        className="memory-badge cursor-pointer hover:bg-green-200 transition-colors"
      >
        <Brain className="w-3 h-3" />
        Recalled {count} memory{count !== 1 ? 'ies' : ''}
        {expanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
      </button>

      {expanded && (
        <div className="mt-1.5 ml-1 space-y-1 animate-fade-in">
          {memories.slice(0, 5).map((m, i) => (
            <div key={i} className="flex gap-2 text-xs">
              <span className="flex-shrink-0 w-4 h-4 rounded-full bg-green-100 text-green-700 flex items-center justify-center font-bold">
                {i + 1}
              </span>
              <div className="bg-green-50 border border-green-100 rounded-md px-2 py-1 text-gray-700 flex-1">
                <span className="font-medium text-green-700 capitalize">[{m.type}]</span>{' '}
                {m.text.length > 120 ? m.text.slice(0, 120) + '…' : m.text}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function MessageBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === 'user';
  const memoriesRecalled = msg.memories_recalled ?? [];
  const memCount = parseInt(msg.memory_count ?? '0', 10);

  return (
    <div className={clsx('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div className={clsx('max-w-[78%]', isUser ? 'items-end' : 'items-start')}>
        {!isUser && (
          <MemoryPill memories={memoriesRecalled} count={memCount} />
        )}
        <div className={clsx(
          'px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap',
          isUser
            ? 'bg-brand-600 text-white rounded-br-md'
            : 'bg-white border border-gray-200 text-gray-800 rounded-bl-md shadow-sm'
        )}>
          {msg.content}
        </div>
        {msg.created_at && (
          <div className="mt-1 text-xs text-gray-400 px-1">
            {formatDistanceToNow(new Date(msg.created_at), { addSuffix: true })}
          </div>
        )}
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
        <div className="flex gap-1 items-center h-4">
          {[0, 1, 2].map(i => (
            <div key={i} className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"
              style={{ animationDelay: `${i * 150}ms` }} />
          ))}
        </div>
      </div>
    </div>
  );
}

export default function ChatWindow({
  customerId, sessionId, memoryMode,
  onActivity, onMemoriesRecalled, onMemoryRetained, onOutcome, injected
}: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [lastResponse, setLastResponse] = useState<ChatResponse | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Reset messages when customer or session changes
  useEffect(() => {
    setMessages([]);
    setLastResponse(null);
  }, [customerId, sessionId]);

  const handleSend = useCallback(async (override?: string) => {
    const text = (override ?? input).trim();
    if (!text || loading || !customerId) return;

    const userMsg: ChatMessage = {
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
      memory_mode: memoryMode,
    };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await sendMessage({
        customer_id: customerId,
        message: userMsg.content,
        session_id: sessionId,
        memory_mode: memoryMode,
      });

      const agentMsg: ChatMessage = {
        role: 'agent',
        content: res.response,
        created_at: new Date().toISOString(),
        memories_recalled: res.memories_recalled,
        memory_count: String(res.memory_count),
        tool_calls: res.tool_calls as ToolCall[],
        memory_mode: memoryMode,
      };

      setMessages(prev => [...prev, agentMsg]);
      setLastResponse(res);

      onActivity?.(res.activity);
      onMemoriesRecalled?.(res.memories_recalled);
      onMemoryRetained?.(res.memory_retained);
      onOutcome?.(res.outcome, res.ticket_id);

    } catch (err: unknown) {
      const errMsg: ChatMessage = {
        role: 'agent',
        content: 'Something went wrong connecting to the support agent. Please ensure the backend is running.',
        created_at: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errMsg]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }, [input, loading, customerId, sessionId, memoryMode, onActivity, onMemoriesRecalled, onMemoryRetained, onOutcome]);

  // Auto-send injected messages from Demo Mode
  useEffect(() => {
    if (injected && injected.text) {
      handleSend(injected.text);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [injected?.nonce]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Outcome banner */}
      {lastResponse?.outcome === 'resolved' && (
        <div className="flex items-center gap-2 px-4 py-2 bg-green-50 border-b border-green-200 text-green-700 text-xs font-medium">
          <CheckCircle className="w-3.5 h-3.5" />
          Issue resolved — memory retained in Hindsight
          {lastResponse.memory_retained && <span className="memory-badge ml-1">Memory stored</span>}
        </div>
      )}
      {lastResponse?.escalated && (
        <div className="flex items-center gap-2 px-4 py-2 bg-orange-50 border-b border-orange-200 text-orange-700 text-xs font-medium">
          <ArrowUpRight className="w-3.5 h-3.5" />
          Escalated to human support — handoff summary generated
        </div>
      )}
      {!customerId && (
        <div className="flex items-center gap-2 px-4 py-2 bg-amber-50 border-b border-amber-200 text-amber-700 text-xs">
          <AlertCircle className="w-3.5 h-3.5" />
          Select a customer to start the conversation
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 scrollbar-thin">
        {messages.length === 0 && customerId && (
          <div className="flex flex-col items-center justify-center h-full text-center gap-2 py-16">
            <div className="w-12 h-12 rounded-full bg-brand-100 flex items-center justify-center">
              <Brain className="w-6 h-6 text-brand-500" />
            </div>
            <p className="text-gray-500 text-sm">Start a conversation. The agent will recall<br />relevant memories from Hindsight.</p>
            {memoryMode === 'without_memory' && (
              <span className="badge-yellow mt-1">Without Memory mode — no history recalled</span>
            )}
          </div>
        )}
        {messages.map((msg, i) => (
          <MessageBubble key={i} msg={msg} />
        ))}
        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="px-4 py-3 border-t border-gray-100 bg-white">
        <div className="flex gap-2 items-end">
          <textarea
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={customerId ? "Describe your issue…" : "Select a customer first"}
            disabled={!customerId || loading}
            rows={2}
            className="flex-1 resize-none px-3 py-2 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400 focus:border-transparent disabled:opacity-50 disabled:bg-gray-50 scrollbar-thin"
          />
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || loading || !customerId}
            className="btn-primary rounded-xl h-[72px] px-4"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          </button>
        </div>
        <div className="mt-1 flex items-center gap-2">
          <span className="text-xs text-gray-400">Enter to send · Shift+Enter for newline</span>
          {memoryMode === 'with_memory' ? (
            <span className="memory-badge text-xs">Memory active</span>
          ) : (
            <span className="badge-yellow text-xs">Memory off</span>
          )}
        </div>
      </div>
    </div>
  );
}
