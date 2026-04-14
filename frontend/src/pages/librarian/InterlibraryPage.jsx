import { useState, useEffect } from 'react';
import DataTable from '../../components/common/DataTable';
import Badge from '../../components/common/Badge';
import api from '../../services/api';

export default function InterlibraryPage() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/library/interlibrary/nearby').then(res => setRequests((res.data || res).items || []))
      .catch(() => {}).finally(() => setLoading(false));
  }, []);

  const columns = [
    { key: 'student_name', label: 'O\'quvchi' },
    { key: 'book_title', label: 'Kitob' },
    { key: 'source_school', label: 'Qayerdan' },
    { key: 'target_school', label: 'Qayerga' },
    { key: 'status', label: 'Holat', render: (v) => <Badge text={v || 'pending'} variant={v === 'approved' ? 'success' : v === 'rejected' ? 'danger' : 'warning'} /> },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Kutubxonalar arasi</h1>
      <DataTable columns={columns} data={requests} loading={loading} emptyMessage="So'rovlar yo'q" />
    </div>
  );
}
