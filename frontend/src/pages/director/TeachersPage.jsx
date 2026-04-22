import { useState, useEffect } from 'react';
import { Plus } from 'lucide-react';
import DataTable from '../../components/common/DataTable';
import SearchBar from '../../components/common/SearchBar';
import Pagination from '../../components/common/Pagination';
import Badge from '../../components/common/Badge';
import api from '../../services/api';

export default function TeachersPage() {
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    setLoading(true);
    api.get('/teachers', { params: { page, search } })
      .then(res => { const d = res.data || res; setTeachers(d.items || []); setTotalPages(d.total_pages || Math.ceil((d.total || 0) / 20) || 1); })
      .catch(() => setTeachers([]))
      .finally(() => setLoading(false));
  }, [page, search]);

  const columns = [
    { key: 'employee_id', label: 'ID' },
    { key: 'full_name', label: 'F.I.Sh.', render: (_, r) => `${r.last_name || ''} ${r.first_name || ''}` },
    { key: 'specialization', label: 'Mutaxassislik' },
    { key: 'qualification', label: 'Malaka' },
    { key: 'phone', label: 'Telefon' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">O'qituvchilar</h1>
        <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"><Plus size={18} /> Yangi o'qituvchi</button>
      </div>
      <SearchBar value={search} onChange={setSearch} placeholder="O'qituvchi qidirish..." />
      <DataTable columns={columns} data={teachers} loading={loading} emptyMessage="O'qituvchilar topilmadi" />
      <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
    </div>
  );
}
