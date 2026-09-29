import { Clock, Brain, Wrench, MessageSquare, CheckCircle, ArrowUpRight, Database, User } from 'lucide-react';
import type { ActivityEntry } from '../../types';

const ICON_MAP: Record<string, React.ElementType> = {
  'Received': MessageSquare,
  'Identified': User,
  'Recalled': Brain,
  'Querying': Brain,
  'memory': Brain,
  'Memory': Brain,
  'Calling tool': Wrench,
  'Created ticket': Database,
  'Generated': ArrowUpRight,
  'Generating': MessageSquare,
  'Retained': CheckCircle,
  'Outcome': CheckCircle,
  'Response': CheckCircle,
};

function getIcon(action: string): React.ElementType {
  for (const [key, Icon] of Object.entries(ICON_MAP)) {
    if (action.toLowerCase().includes(key.toLowerCase())) return Icon;
  }
  return Clock;
}

interface Props {
  activity: ActivityEntry[];
}

export default function ActivityFeed({ activity }: Props) {
  if (activity.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400 text-sm">
        Activity will appear here during agent processing.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {activity.map((entry, i) => {
        const Icon = getIcon(entry.action);
        const isMemory = entry.action.toLowerCase().includes('memory') || entry.action.toLowerCase().includes('hindsight');
        const isResolved = entry.action.toLowerCase().includes('resolved') || entry.action.toLowerCase().includes('retained');

        return (
          <div key={i} className="flex items-start gap-2.5 animate-fade-in">
            <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 ${
              isMemory ? 'bg-green-100 text-green-600' :
              isResolved ? 'bg-brand-100 text-brand-600' :
              'bg-gray-100 text-gray-500'
            }`}>
              <Icon className="w-3 h-3" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs text-gray-700">{entry.action}</div>
              <div className="text-xs text-gray-400 font-mono">{entry.time}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
