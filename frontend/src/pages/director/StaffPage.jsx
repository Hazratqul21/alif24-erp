import { useState, useEffect } from 'react';
import DataTable from '../../components/common/DataTable';
import SearchBar from '../../components/common/SearchBar';
import Badge from '../../components/common/Badge';
import api from '../../services/api';

export default function StaffPage() {
  const [staff, setStaff] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    api.get('/users', { params: { search } }).then(res => setStaff((res.data || res).items || [])).catch(() => {}).finally(() => setLoading(false));
  }, [search]);

  const columns = [
    { key: 'full_name', label: 'F.I.Sh.', render: (_, r) => `${r.last_name || ''} ${r.first_name || ''}` },
    { key: 'roles', label: 'Rol', render: (v) => (v || []).map(r => <Badge key={r} text={r} variant="info" />).slice(0, 2) },
    { key: 'phone', label: 'Telefon' },
    { key: 'email', label: 'Email' },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Xodimlar</h1>
      <SearchBar value={search} onChange={setSearch} placeholder="Xodim qidirish..." />
      <DataTable columns={columns} data={staff} loading={loading} emptyMessage="Xodimlar topilmadi" />
    </div>
  );
}
