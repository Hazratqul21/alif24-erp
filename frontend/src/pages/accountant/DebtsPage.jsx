import { useState, useEffect } from 'react';
import { Bell } from 'lucide-react';
import DataTable from '../../components/common/DataTable';
import Badge from '../../components/common/Badge';
import api from '../../services/api';

export default function DebtsPage() {
  const [debts, setDebts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/payments/debts').then(res => setDebts((res.data || res).items || []))
      .catch(() => {}).finally(() => setLoading(false));
  }, []);

  const columns = [
    { key: 'student_name', label: 'O\'quvchi' },
    { key: 'class_name', label: 'Sinf' },
    { key: 'debt_amount', label: 'Qarz', render: (v) => <span className="text-red-600 font-semibold">{Number(v || 0).toLocaleString()} so'm</span> },
    { key: 'months_overdue', label: 'Muddat' },
    { key: 'actions', label: '', render: () => (
      <button className="flex items-center gap-1 text-sm text-orange-600 hover:text-orange-800"><Bell size={14} /> Eslatma</button>
    )},
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Qarzlar</h1>
        <button className="flex items-center gap-2 bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700"><Bell size={18} /> Barchaga eslatma</button>
      </div>
      <DataTable columns={columns} data={debts} loading={loading} emptyMessage="Qarzlar yo'q" />
    </div>
  );
}
