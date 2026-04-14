import { TrendingUp, TrendingDown } from 'lucide-react';

const colorMap = {
  blue:   { bg: 'bg-blue-50',   icon: 'text-blue-600',   ring: 'ring-blue-100' },
  green:  { bg: 'bg-green-50',  icon: 'text-green-600',  ring: 'ring-green-100' },
  red:    { bg: 'bg-red-50',    icon: 'text-red-600',    ring: 'ring-red-100' },
  yellow: { bg: 'bg-yellow-50', icon: 'text-yellow-600', ring: 'ring-yellow-100' },
  purple: { bg: 'bg-purple-50', icon: 'text-purple-600', ring: 'ring-purple-100' },
  indigo: { bg: 'bg-indigo-50', icon: 'text-indigo-600', ring: 'ring-indigo-100' },
};

const StatsCard = ({ title, value, icon: Icon, trend, trendValue, color = 'blue' }) => {
  const c = colorMap[color] ?? colorMap.blue;

  return (
    <div className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="text-2xl font-bold text-gray-900 tracking-tight">{value}</p>
        </div>
        {Icon && (
          <div className={`p-2.5 rounded-xl ${c.bg} ring-1 ${c.ring}`}>
            <Icon className={`w-5 h-5 ${c.icon}`} />
          </div>
        )}
      </div>

      {trend && trendValue != null && (
        <div className="mt-3 flex items-center gap-1.5 text-sm">
          {trend === 'up' ? (
            <TrendingUp className="w-4 h-4 text-green-500" />
          ) : (
            <TrendingDown className="w-4 h-4 text-red-500" />
          )}
          <span className={trend === 'up' ? 'text-green-600 font-medium' : 'text-red-600 font-medium'}>
            {trendValue}%
          </span>
          <span className="text-gray-400">за период</span>
        </div>
      )}
    </div>
  );
};

export default StatsCard;
