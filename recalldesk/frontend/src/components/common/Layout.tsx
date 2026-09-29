import { Outlet, NavLink } from 'react-router-dom';
import {
  LayoutDashboard, MessageSquare, Brain, Ticket,
  BookOpen, PlayCircle, Zap
} from 'lucide-react';
import clsx from 'clsx';

const nav = [
  { to: '/demo',      icon: PlayCircle,      label: 'Demo Mode',   highlight: true },
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/chat',      icon: MessageSquare,   label: 'Chat' },
  { to: '/memory',    icon: Brain,           label: 'Memory' },
  { to: '/tickets',   icon: Ticket,          label: 'Tickets' },
  { to: '/knowledge', icon: BookOpen,        label: 'Knowledge' },
];

export default function Layout() {
  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-56 flex-shrink-0 bg-white border-r border-gray-200 flex flex-col">
        {/* Logo */}
        <div className="px-4 py-4 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <div>
              <div className="text-sm font-bold text-gray-900">RecallDesk</div>
              <div className="text-xs text-gray-400">Nexora Cloud</div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-2 py-3 space-y-0.5">
          {nav.map(({ to, icon: Icon, label, highlight }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? highlight
                      ? 'bg-brand-600 text-white'
                      : 'bg-brand-50 text-brand-700'
                    : highlight
                      ? 'text-brand-600 hover:bg-brand-50'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                )
              }
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              {label}
              {highlight && (
                <span className="ml-auto text-xs bg-brand-100 text-brand-700 px-1.5 py-0.5 rounded-full">
                  Live
                </span>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="px-4 py-3 border-t border-gray-100">
          <div className="text-xs text-gray-400">
            Powered by{' '}
            <span className="font-medium text-brand-600">Hindsight</span>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}
