import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#f97316'];

const ChartInner = ({ type, data, xKey, yKey }) => {
  if (type === 'pie') {
    return (
      <PieChart>
        <Pie
          data={data}
          dataKey={yKey}
          nameKey={xKey}
          cx="50%"
          cy="50%"
          outerRadius="75%"
          strokeWidth={2}
          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
        >
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    );
  }

  const ChartType = type === 'line' ? LineChart : BarChart;
  const DataElement = type === 'line' ? Line : Bar;

  return (
    <ChartType data={data}>
      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
      <XAxis dataKey={xKey} tick={{ fontSize: 12 }} stroke="#9ca3af" />
      <YAxis tick={{ fontSize: 12 }} stroke="#9ca3af" />
      <Tooltip
        contentStyle={{ borderRadius: '12px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.05)' }}
      />
      <Legend />
      <DataElement
        dataKey={yKey}
        fill="#3b82f6"
        stroke="#3b82f6"
        strokeWidth={2}
        radius={type === 'bar' ? [6, 6, 0, 0] : undefined}
        dot={type === 'line' ? { r: 3 } : undefined}
      />
    </ChartType>
  );
};

const Chart = ({ type = 'bar', data = [], xKey = 'name', yKey = 'value', title }) => (
  <div className="rounded-2xl border border-gray-200 bg-white shadow-sm p-5">
    {title && <h3 className="text-sm font-semibold text-gray-800 mb-4">{title}</h3>}
    <div className="w-full h-72">
      <ResponsiveContainer width="100%" height="100%">
        <ChartInner type={type} data={data} xKey={xKey} yKey={yKey} />
      </ResponsiveContainer>
    </div>
  </div>
);

export default Chart;
