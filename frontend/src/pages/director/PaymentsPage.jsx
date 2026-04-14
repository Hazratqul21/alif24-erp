import { useState, useEffect } from 'react';
import { Wallet, AlertTriangle, TrendingUp } from 'lucide-react';
import StatsCard from '../../components/common/StatsCard';
import DataTable from '../../components/common/DataTable';
import Badge from '../../components/common/Badge';
import Chart from '../../components/common/Chart';
import api from '../../services/api';

export default function PaymentsPage() {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/reports/financial').then(res => setPayments((res.data || res).recent_payments || [])).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const columns = [
    { key: 'student_name', label: 'O\'quvchi' },
    { key: 'amount', label: 'Summa', render: (v) => `${Number(v || 0).toLocaleString()} so'm` },
    { key: 'payment_method', label: 'Usul' },
    { key: 'status', label: 'Holat', render: (v) => <Badge text={v === 'paid' ? 'To\'langan' : 'Kutilmoqda'} variant={v === 'paid' ? 'success' : 'warning'} /> },
    { key: 'payment_date', label: 'Sana' },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">To'lovlar</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatsCard title="Oylik daromad" value="45,000,000 so'm" icon={Wallet} color="green" />
        <StatsCard title="Qarzlar" value="12,500,000 so'm" icon={AlertTriangle} color="red" />
        <StatsCard title="O'sish" value="+12%" icon={TrendingUp} color="blue" />
      </div>
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4">So'nggi to'lovlar</h2>
        <DataTable columns={columns} data={payments} loading={loading} emptyMessage="To'lovlar topilmadi" />
      </div>
    </div>
  );
}
