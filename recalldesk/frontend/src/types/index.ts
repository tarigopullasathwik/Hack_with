// ─── Customer ─────────────────────────────────────────────────────────────────
export interface Customer {
  id: string;
  name: string;
  email: string;
  company?: string;
  plan: 'free' | 'starter' | 'business' | 'enterprise';
  status: 'active' | 'suspended' | 'churned';
  browser?: string;
  operating_system?: string;
  product_version?: string;
  workspace_size?: string;
  profile_notes?: string;
  preferences?: string;
  created_at?: string;
}

// ─── Ticket ───────────────────────────────────────────────────────────────────
export type TicketStatus = 'open' | 'in_progress' | 'pending_customer' | 'escalated' | 'resolved' | 'closed';
export type TicketPriority = 'low' | 'medium' | 'high' | 'critical';
export type TicketCategory = 'login' | 'billing' | 'subscription' | 'integration' | 'notifications' | 'file_sync' | 'permissions' | 'api' | 'account' | 'other';

export interface Ticket {
  id: string;
  customer_id: string;
  title: string;
  description?: string;
  category: TicketCategory;
  status: TicketStatus;
  priority: TicketPriority;
  resolution?: string;
  resolution_steps?: string;
  failed_steps?: string;
  successful_step?: string;
  escalated_to?: string;
  escalation_reason?: string;
  handoff_summary?: string;
  created_at?: string;
  updated_at?: string;
  resolved_at?: string;
}

// ─── Messages ─────────────────────────────────────────────────────────────────
export type MessageRole = 'user' | 'agent' | 'system';
export type MemoryMode = 'with_memory' | 'without_memory';

export interface RecalledMemory {
  text: string;
  type: string;
  score?: number;
  chunk_id?: string | null;
  context?: string;
  created_at?: string;
  metadata?: Record<string, string>;
}

export interface ToolCall {
  tool: string;
  args: Record<string, unknown>;
  result?: Record<string, unknown>;
}

export interface ActivityEntry {
  time: string;
  action: string;
}

export interface ChatMessage {
  id?: string;
  role: MessageRole;
  content: string;
  created_at?: string;
  memories_recalled?: RecalledMemory[];
  memory_count?: string;
  tool_calls?: ToolCall[];
  memory_mode?: MemoryMode;
}

// ─── Chat API ─────────────────────────────────────────────────────────────────
export interface ChatRequest {
  customer_id: string;
  message: string;
  session_id?: string;
  memory_mode: MemoryMode;
  active_ticket_id?: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  memories_recalled: RecalledMemory[];
  memory_count: number;
  memory_retained: boolean;
  tool_calls: ToolCall[];
  activity: ActivityEntry[];
  outcome: 'resolved' | 'failed' | 'escalated' | 'ongoing' | 'error';
  ticket_id: string | null;
  escalated: boolean;
  handoff_summary: string | null;
  hindsight_status: HindsightStatus;
}

// ─── Hindsight ────────────────────────────────────────────────────────────────
export interface HindsightStatus {
  available: boolean;
  error?: string | null;
  server_url?: string | null;
  mode: 'hindsight' | 'fallback';
}

export interface MemoryItem {
  id?: string;
  text: string;
  type: string;
  score?: number;
  created_at?: string;
  context?: string;
  metadata?: Record<string, string>;
}

// ─── Knowledge ────────────────────────────────────────────────────────────────
export interface KnowledgeArticle {
  id: string;
  title: string;
  category: string;
  content: string;
  tags?: string;
  troubleshooting_steps?: string;
  common_causes?: string;
}

// ─── Demo ─────────────────────────────────────────────────────────────────────
export interface DemoScenario {
  id: string;
  name: string;
  description: string;
  customer_id: string;
  customer_name?: string;
  customer_plan?: string;
  scenario_type: string;
  sort_order: number;
  turns?: ScenarioTurn[];
}

export interface ScenarioTurn {
  role: 'user' | 'agent';
  content: string;
  delay_ms?: number;
}

export interface TimelineEntry {
  date: string;
  timestamp?: string;
  ticket_id: string;
  title: string;
  category: string;
  status: TicketStatus;
  outcome: string;
  successful_step?: string;
  failed_steps?: string[];
  resolution?: string;
  escalated: boolean;
}

export interface BeforeAfterResult {
  message: string;
  without_memory: {
    response: string;
    memories_recalled: RecalledMemory[];
    memory_count: number;
  };
  with_memory: {
    response: string;
    memories_recalled: RecalledMemory[];
    memory_count: number;
  };
}

export interface DemoStats {
  total_customers: number;
  total_tickets: number;
  resolved_tickets: number;
  escalated_tickets: number;
  total_messages: number;
  hindsight_available: boolean;
  hindsight_status: HindsightStatus;
}
