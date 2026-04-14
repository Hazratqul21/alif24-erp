import { useState, useEffect } from 'react';
import { AlertTriangle } from 'lucide-react';
import DataTable from '../../components/common/DataTable';
import api from '../../services/api';

export default function OverduePage() {
  const [overdue, setOverdue] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/library/loans/overdue').then(res => setOverdue((res.data || res).items || []))
      .catch(() => {}).finally(() => setLoading(false));
  }, []);

  const columns = [
    { key: 'student_name', label: 'O\'quvchi' },
    { key: 'book_title', label: 'Kitob' },
    { key: 'due_date', label: 'Muddat' },
    { key: 'days_overdue', label: 'Kechikish', render: (v) => <span className="text-red-600 font-semibold">{v || 0} kun</span> },
    { key: 'fine_amount', label: 'Jarima', render: (v) => `${Number(v || 0).toLocaleString()} so'm` },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <AlertTriangle className="text-red-500" />
        <h1 className="text-2xl font-bold">Muddati o'tgan kitoblar</h1>
      </div>
      <DataTable columns={columns} data={overdue} loading={loading} emptyMessage="Muddati o'tgan kitoblar yo'q" />
    </div>
  );
}
