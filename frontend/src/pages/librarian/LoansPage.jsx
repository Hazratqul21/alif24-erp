import { useState, useEffect } from 'react';
import DataTable from '../../components/common/DataTable';
import Badge from '../../components/common/Badge';
import api from '../../services/api';

export default function LoansPage() {
  const [loans, setLoans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/library/loans/overdue').then(res => setLoans((res.data || res).items || []))
      .catch(() => {}).finally(() => setLoading(false));
  }, []);

  const columns = [
    { key: 'student_name', label: 'O\'quvchi' },
    { key: 'book_title', label: 'Kitob' },
    { key: 'loan_date', label: 'Berilgan' },
    { key: 'due_date', label: 'Muddat' },
    { key: 'status', label: 'Holat', render: (v) => <Badge text={v === 'borrowed' ? 'Berilgan' : v === 'overdue' ? "Muddati o'tgan" : 'Qaytarilgan'} variant={v === 'overdue' ? 'danger' : v === 'borrowed' ? 'warning' : 'success'} /> },
    { key: 'actions', label: '', render: (_, row) => row.status !== 'returned' && <button className="text-sm text-blue-600 hover:text-blue-800">Qaytarish</button> },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Berilgan kitoblar</h1>
      <DataTable columns={columns} data={loans} loading={loading} emptyMessage="Berilgan kitoblar yo'q" />
    </div>
  );
}
