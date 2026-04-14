import { useState, useEffect } from 'react';
import DataTable from '../../components/common/DataTable';
import SearchBar from '../../components/common/SearchBar';
import api from '../../services/api';

export default function RecordsPage() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    api.get('/medical/records', { params: { search } }).then(res => setRecords((res.data || res).items || []))
      .catch(() => {}).finally(() => setLoading(false));
  }, [search]);

  const columns = [
    { key: 'student_name', label: 'O\'quvchi' },
    { key: 'blood_type', label: 'Qon guruhi' },
    { key: 'allergies', label: 'Allergiya' },
    { key: 'chronic_diseases', label: 'Surunkali kasalliklar' },
    { key: 'emergency_contact', label: 'Favqulodda aloqa' },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Tibbiy kartalar</h1>
      <SearchBar value={search} onChange={setSearch} placeholder="O'quvchi qidirish..." />
      <DataTable columns={columns} data={records} loading={loading} emptyMessage="Kartalar topilmadi" />
    </div>
  );
}
