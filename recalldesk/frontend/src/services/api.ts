import axios from 'axios';
import type {
  Customer, Ticket, ChatRequest, ChatResponse,
  MemoryItem, KnowledgeArticle, DemoScenario,
  TimelineEntry, BeforeAfterResult, DemoStats, RecalledMemory
} from '../types';

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
});

// ─── Customers ────────────────────────────────────────────────────────────────
export const getCustomers = () =>
  api.get<{ customers: Customer[]; count: number }>('/customers').then(r => r.data);

export const getCustomer = (id: string) =>
  api.get<Customer>(`/customers/${id}`).then(r => r.data);

export const createCustomer = (data: Partial<Customer>) =>
  api.post<Customer>('/customers', data).then(r => r.data);

// ─── Chat ─────────────────────────────────────────────────────────────────────
export const sendMessage = (req: ChatRequest) =>
  api.post<ChatResponse>('/chat', req).then(r => r.data);

export const getChatHistory = (customerId: string, sessionId: string) =>
  api.get(`/chat/history/${customerId}/${sessionId}`).then(r => r.data);

export const getSessions = (customerId: string) =>
  api.get<{ sessions: string[] }>(`/chat/sessions/${customerId}`).then(r => r.data);

// ─── Tickets ──────────────────────────────────────────────────────────────────
export const getTickets = (customerId?: string) =>
  api.get<{ tickets: Ticket[]; count: number }>('/tickets', {
    params: customerId ? { customer_id: customerId } : {},
  }).then(r => r.data);

export const getTicket = (id: string) =>
  api.get<Ticket>(`/tickets/${id}`).then(r => r.data);

export const updateTicket = (id: string, data: Partial<Ticket>) =>
  api.patch<Ticket>(`/tickets/${id}`, data).then(r => r.data);

// ─── Memory ───────────────────────────────────────────────────────────────────
export const getMemoryStatus = () =>
  api.get('/memory/status').then(r => r.data);

export const getCustomerMemories = (customerId: string, limit = 50) =>
  api.get<{ memories: MemoryItem[]; count: number; hindsight_available: boolean }>(
    `/memory/${customerId}`, { params: { limit } }
  ).then(r => r.data);

export const recallMemories = (customerId: string, query: string) =>
  api.post<{ memories: RecalledMemory[]; count: number; hindsight_available: boolean }>(
    `/memory/${customerId}/recall`, { query }
  ).then(r => r.data);

export const retainMemory = (customerId: string, content: string, context?: string) =>
  api.post(`/memory/${customerId}/retain`, { content, context }).then(r => r.data);

// ─── Knowledge ────────────────────────────────────────────────────────────────
export const getArticles = (category?: string) =>
  api.get<{ articles: KnowledgeArticle[]; count: number }>(
    '/knowledge', { params: category ? { category } : {} }
  ).then(r => r.data);

export const searchArticles = (q: string) =>
  api.get<{ articles: KnowledgeArticle[]; count: number }>(
    '/knowledge/search', { params: { q } }
  ).then(r => r.data);

// ─── Demo ─────────────────────────────────────────────────────────────────────
export const getDemoScenarios = () =>
  api.get<{ scenarios: DemoScenario[] }>('/demo/scenarios').then(r => r.data);

export const getDemoCustomers = () =>
  api.get('/demo/customers').then(r => r.data);

export const getMemoryTimeline = (customerId: string) =>
  api.get<{ customer_id: string; timeline: TimelineEntry[]; hindsight_memories: MemoryItem[]; hindsight_available: boolean }>(
    `/demo/memory-timeline/${customerId}`
  ).then(r => r.data);

export const compareBeforeAfter = (customerId: string, message: string) =>
  api.post<BeforeAfterResult>(`/demo/compare/${customerId}`, { message }).then(r => r.data);

export const getDemoStats = () =>
  api.get<DemoStats>('/demo/stats').then(r => r.data);

export const getHealth = () =>
  axios.get('/health').then(r => r.data);
