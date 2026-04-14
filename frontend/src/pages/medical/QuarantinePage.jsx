import { useState, useEffect } from 'react';
import DataTable from '../../components/common/DataTable';
import Badge from '../../components/common/Badge';
import api from '../../services/api';

export default function QuarantinePage() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/medical/quarantine').then(res => setRecords((res.data || res).items || []))
      .catch(() => {}).finally(() => setLoading(false));
  }, []);

  const columns = [
    { key: 'student_name', label: 'O\'quvchi' },
    { key: 'disease', label: 'Kasallik' },
    { key: 'start_date', label: 'Boshlanish' },
    { key: 'end_date', label: 'Tugash' },
    { key: 'status', label: 'Holat', render: (v) => <Badge text={v === 'active' ? 'Faol' : 'Tugagan'} variant={v === 'active' ? 'danger' : 'success'} /> },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Karantin</h1>
      <DataTable columns={columns} data={records} loading={loading} emptyMessage="Karantin yozuvlari yo'q" />
    </div>
  );
}
