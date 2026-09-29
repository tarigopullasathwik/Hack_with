import { useEffect, useMemo, useState } from 'react';
import { BookOpen, Search, ChevronDown, ChevronUp, Tag } from 'lucide-react';
import { getArticles } from '../services/api';
import type { KnowledgeArticle } from '../types';
import clsx from 'clsx';

function parseList(raw?: string): string[] {
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed)) return parsed.map(String);
  } catch {
    // fall back to newline / comma split
  }
  return raw.split(/\n|,/).map(s => s.trim()).filter(Boolean);
}

const CATEGORY_COLORS: Record<string, string> = {
  billing: 'badge-purple', login: 'badge-blue', subscription: 'badge-purple',
  integration: 'badge-blue', notifications: 'badge-yellow', file_sync: 'badge-green',
  permissions: 'badge-gray', api: 'badge-blue', account: 'badge-gray',
};

function ArticleCard({ article }: { article: KnowledgeArticle }) {
  const [open, setOpen] = useState(false);
  const steps = parseList(article.troubleshooting_steps);
  const causes = parseList(article.common_causes);

  return (
    <div className="card overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-gray-50 transition-colors"
      >
        <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center flex-shrink-0">
          <BookOpen className="w-4 h-4 text-blue-600" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium text-gray-900">{article.title}</div>
          <div className="text-xs text-gray-400 truncate">{article.content.slice(0, 90)}…</div>
        </div>
        <span className={clsx('badge capitalize flex-shrink-0', CATEGORY_COLORS[article.category] ?? 'badge-gray')}>
          {article.category.replace(/_/g, ' ')}
        </span>
        {open ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
      </button>

      {open && (
        <div className="px-4 pb-4 pt-1 border-t border-gray-50 animate-fade-in space-y-3">
          <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-wrap">{article.content}</p>

          {causes.length > 0 && (
            <div>
              <div className="text-xs font-semibold text-gray-700 mb-1">Common causes</div>
              <ul className="space-y-0.5">
                {causes.map((c, i) => (
                  <li key={i} className="text-xs text-gray-500 flex gap-1.5">
                    <span className="text-gray-300">•</span>{c}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {steps.length > 0 && (
            <div>
              <div className="text-xs font-semibold text-gray-700 mb-1">Troubleshooting steps</div>
              <ol className="space-y-1">
                {steps.map((s, i) => (
                  <li key={i} className="text-xs text-gray-600 flex gap-2">
                    <span className="flex-shrink-0 w-4 h-4 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
                      {i + 1}
                    </span>
                    {s}
                  </li>
                ))}
              </ol>
            </div>
          )}

          {article.tags && (
            <div className="flex items-center gap-1.5 flex-wrap pt-1">
              <Tag className="w-3 h-3 text-gray-300" />
              {parseList(article.tags).map((t, i) => (
                <span key={i} className="badge-gray">{t}</span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function KnowledgePage() {
  const [articles, setArticles] = useState<KnowledgeArticle[]>([]);
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState<string>('all');
  const [error, setError] = useState(false);

  useEffect(() => {
    getArticles().then(r => setArticles(r.articles)).catch(() => setError(true));
  }, []);

  const categories = useMemo(
    () => ['all', ...Array.from(new Set(articles.map(a => a.category)))],
    [articles]
  );

  const filtered = articles.filter(a => {
    const matchesCat = category === 'all' || a.category === category;
    const matchesQuery =
      !query ||
      a.title.toLowerCase().includes(query.toLowerCase()) ||
      a.content.toLowerCase().includes(query.toLowerCase());
    return matchesCat && matchesQuery;
  });

  return (
    <div className="max-w-4xl mx-auto px-6 py-6">
      <div className="mb-5">
        <h1 className="text-xl font-bold text-gray-900">Knowledge Base</h1>
        <p className="text-sm text-gray-500 mt-0.5">
          General product documentation for Nexora Workspace — shared across all customers.
          The agent combines these articles with customer-specific memory.
        </p>
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-3 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Search articles…"
            className="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-400"
          />
        </div>
        <div className="flex gap-1.5 flex-wrap">
          {categories.map(c => (
            <button
              key={c}
              onClick={() => setCategory(c)}
              className={clsx(
                'text-xs px-2.5 py-1 rounded-full capitalize transition-colors',
                category === c ? 'bg-brand-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              )}
            >
              {c.replace(/_/g, ' ')}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="card p-4 text-sm text-red-600">Could not load articles.</div>}

      <div className="space-y-2">
        {filtered.map(a => <ArticleCard key={a.id} article={a} />)}
        {filtered.length === 0 && !error && (
          <div className="text-center py-12 text-gray-400 text-sm">No articles match your search.</div>
        )}
      </div>
    </div>
  );
}
