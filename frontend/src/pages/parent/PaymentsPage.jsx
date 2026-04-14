import { useState, useEffect } from 'react';
import { CreditCard } from 'lucide-react';
import DataTable from '../../components/common/DataTable';
import Badge from '../../components/common/Badge';
import api from '../../services/api';

export default function ParentPaymentsPage() {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/payments/student/me').then(res => setPayments((res.data || res).items || []))
      .catch(() => setPayments([])).finally(() => setLoading(false));
  }, []);

  const samplePayments = payments.length ? payments : [
    { id: 1, description: 'Oylik to\'lov — Aprel', amount: 500000, status: 'paid', date: '2026-04-01' },
    { id: 2, description: 'Oylik to\'lov — May', amount: 500000, status: 'pending', date: '2026-05-01' },
  ];

  const columns = [
    { key: 'description', label: 'Tavsif' },
    { key: 'amount', label: 'Summa', render: (v) => `${Number(v).toLocaleString()} so'm` },
    { key: 'status', label: 'Holat', render: (v) => <Badge text={v === 'paid' ? "To'langan" : 'Kutilmoqda'} variant={v === 'paid' ? 'success' : 'warning'} /> },
    { key: 'date', label: 'Sana' },
    { key: 'actions', label: '', render: (_, row) => row.status !== 'paid' && (
      <button className="flex items-center gap-1 bg-blue-600 text-white px-3 py-1 rounded-lg text-sm hover:bg-blue-700">
        <CreditCard size={14} /> To'lash
      </button>
    )},
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">To'lovlar</h1>
      <DataTable columns={columns} data={samplePayments} loading={loading} emptyMessage="To'lovlar topilmadi" />
    </div>
  );
}
