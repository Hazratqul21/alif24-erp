import { ChevronUp, ChevronDown } from 'lucide-react';
import { useState } from 'react';

const SkeletonRow = ({ columns }) => (
  <tr className="animate-pulse">
    {columns.map((_, i) => (
      <td key={i} className="px-6 py-4 whitespace-nowrap">
        <div className="h-4 bg-gray-200 rounded w-3/4" />
      </td>
    ))}
  </tr>
);

const DataTable = ({
  columns = [],
  data = [],
  loading = false,
  onRowClick,
  emptyMessage = 'Нет данных',
  actions,
  sortable = false,
}) => {
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

  const handleSort = (key) => {
    if (!sortable) return;
    setSortConfig((prev) => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc',
    }));
  };

  const sortedData = sortable && sortConfig.key
    ? [...data].sort((a, b) => {
        const aVal = a[sortConfig.key];
        const bVal = b[sortConfig.key];
        if (aVal == null) return 1;
        if (bVal == null) return -1;
        const cmp = typeof aVal === 'string' ? aVal.localeCompare(bVal) : aVal - bVal;
        return sortConfig.direction === 'asc' ? cmp : -cmp;
      })
    : data;

  const allColumns = actions
    ? [...columns, { key: '__actions', label: '', render: (_, row) => actions(row) }]
    : columns;

  return (
    <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {allColumns.map((col) => (
              <th
                key={col.key}
                onClick={() => col.key !== '__actions' && handleSort(col.key)}
                className={`px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider ${
                  sortable && col.key !== '__actions' ? 'cursor-pointer select-none hover:text-gray-700' : ''
                }`}
              >
                <span className="inline-flex items-center gap-1">
                  {col.label}
                  {sortable && sortConfig.key === col.key && (
                    sortConfig.direction === 'asc' ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />
                  )}
                </span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {loading ? (
            Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} columns={allColumns} />)
          ) : sortedData.length === 0 ? (
            <tr>
              <td colSpan={allColumns.length} className="px-6 py-16 text-center text-gray-400 text-sm">
                {emptyMessage}
              </td>
            </tr>
          ) : (
            sortedData.map((row, rowIdx) => (
              <tr
                key={row.id ?? rowIdx}
                onClick={() => onRowClick?.(row)}
                className={`transition-colors ${
                  onRowClick ? 'cursor-pointer hover:bg-blue-50/60' : 'hover:bg-gray-50'
                }`}
              >
                {allColumns.map((col) => (
                  <td key={col.key} className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {col.render ? col.render(row[col.key], row) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default DataTable;
