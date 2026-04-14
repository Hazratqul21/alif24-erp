import { useState, useEffect } from 'react';
import { Plus, Download } from 'lucide-react';
import DataTable from '../../components/common/DataTable';
import Badge from '../../components/common/Badge';
import api from '../../services/api';

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/payments/student/me').then(res => setInvoices((res.data || res).items || []))
      .catch(() => {}).finally(() => setLoading(false));
  }, []);

  const columns = [
    { key: 'invoice_number', label: 'Raqam' },
    { key: 'student_name', label: 'O\'quvchi' },
    { key: 'total_amount', label: 'Summa', render: (v) => `${Number(v || 0).toLocaleString()} so'm` },
    { key: 'status', label: 'Holat', render: (v) => <Badge text={v || 'pending'} variant={v === 'paid' ? 'success' : 'warning'} /> },
    { key: 'actions', label: '', render: () => <button className="text-blue-600 hover:text-blue-800 text-sm"><Download size={16} /></button> },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Hisob-fakturalar</h1>
        <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"><Plus size={18} /> Yangi faktura</button>
      </div>
      <DataTable columns={columns} data={invoices} loading={loading} emptyMessage="Fakturalar topilmadi" />
    </div>
  );
}
