import { useState, useEffect } from 'react';
import { Download } from 'lucide-react';
import DataTable from '../../components/common/DataTable';
import SearchBar from '../../components/common/SearchBar';
import Pagination from '../../components/common/Pagination';
import Badge from '../../components/common/Badge';
import api from '../../services/api';

export default function AccountantPaymentsPage() {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);

  useEffect(() => {
    api.get('/payments/debts', { params: { page, search } }).then(res => setPayments((res.data || res).items || []))
      .catch(() => {}).finally(() => setLoading(false));
  }, [page, search]);

  const columns = [
    { key: 'student_name', label: 'O\'quvchi' },
    { key: 'amount', label: 'Summa', render: (v) => `${Number(v || 0).toLocaleString()} so'm` },
    { key: 'payment_type', label: 'Turi' },
    { key: 'payment_method', label: 'Usul' },
    { key: 'status', label: 'Holat', render: (v) => <Badge text={v === 'paid' ? "To'langan" : v === 'pending' ? 'Kutilmoqda' : 'Muddati o\'tgan'} variant={v === 'paid' ? 'success' : v === 'pending' ? 'warning' : 'danger'} /> },
    { key: 'payment_date', label: 'Sana' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">To'lovlar</h1>
        <button className="flex items-center gap-2 border px-4 py-2 rounded-lg hover:bg-gray-50"><Download size={18} /> Export</button>
      </div>
      <SearchBar value={search} onChange={setSearch} placeholder="To'lov qidirish..." />
      <DataTable columns={columns} data={payments} loading={loading} emptyMessage="To'lovlar topilmadi" />
      <Pagination page={page} totalPages={5} onPageChange={setPage} />
    </div>
  );
}
