import { PlayCircle, User, Tag } from 'lucide-react';
import type { DemoScenario } from '../../types';
import clsx from 'clsx';

const SCENARIO_ICONS: Record<string, string> = {
  recurring_billing:   '💳',
  integration_failure: '🔗',
  escalation:          '🚨',
};

const SCENARIO_COLORS: Record<string, string> = {
  recurring_billing:   'border-blue-200 hover:border-blue-400',
  integration_failure: 'border-purple-200 hover:border-purple-400',
  escalation:          'border-orange-200 hover:border-orange-400',
};

interface Props {
  scenario: DemoScenario;
  onSelect: (s: DemoScenario) => void;
  active?: boolean;
}

export default function ScenarioCard({ scenario, onSelect, active }: Props) {
  return (
    <button
      onClick={() => onSelect(scenario)}
      className={clsx(
        'w-full text-left p-4 rounded-xl border-2 bg-white transition-all hover:shadow-md',
        active
          ? 'border-brand-500 shadow-md ring-2 ring-brand-200'
          : SCENARIO_COLORS[scenario.scenario_type] ?? 'border-gray-200 hover:border-gray-400'
      )}
    >
      <div className="flex items-start gap-3">
        <div className="text-2xl">{SCENARIO_ICONS[scenario.scenario_type] ?? '🎯'}</div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-gray-900">{scenario.name}</h3>
            {active && <span className="badge-green">Active</span>}
          </div>
          <p className="text-xs text-gray-500 mt-0.5 leading-relaxed">{scenario.description}</p>
          <div className="flex items-center gap-3 mt-2">
            <span className="flex items-center gap-1 text-xs text-gray-400">
              <User className="w-3 h-3" />{scenario.customer_name}
            </span>
            <span className="flex items-center gap-1 text-xs text-gray-400">
              <Tag className="w-3 h-3" />
              <span className="capitalize">{scenario.scenario_type.replace(/_/g, ' ')}</span>
            </span>
          </div>
        </div>
        <PlayCircle className={clsx('w-5 h-5 flex-shrink-0 mt-0.5', active ? 'text-brand-500' : 'text-gray-300')} />
      </div>
    </button>
  );
}
