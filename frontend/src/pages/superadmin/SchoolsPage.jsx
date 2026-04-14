import { useState, useEffect } from 'react';
import { Plus, Search, Ban, CheckCircle } from 'lucide-react';
import DataTable from '../../components/common/DataTable';
import Modal from '../../components/common/Modal';
import SearchBar from '../../components/common/SearchBar';
import Badge from '../../components/common/Badge';
import Pagination from '../../components/common/Pagination';
import api from '../../services/api';

export default function SchoolsPage() {
  const [schools, setSchools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ subdomain: '', name: '', phone: '', email: '' });

  const fetchSchools = async () => {
    setLoading(true);
    try {
      const res = await api.get('/superadmin/tenants', { params: { page, search } });
      const data = res.data || res;
      setSchools(data.items || []);
      setTotalPages(data.total_pages || 1);
    } catch { setSchools([]); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchSchools(); }, [page, search]);

  const handleCreate = async () => {
    try {
      await api.post('/superadmin/tenants', form);
      setShowCreate(false);
      setForm({ subdomain: '', name: '', phone: '', email: '' });
      fetchSchools();
    } catch {}
  };

  const toggleBlock = async (id, isActive) => {
    try {
      await api.put(`/superadmin/tenants/${id}/${isActive ? 'block' : 'unblock'}`);
      fetchSchools();
    } catch {}
  };

  const columns = [
    { key: 'name', label: 'Nomi' },
    { key: 'subdomain', label: 'Subdomen', render: (v) => <code className="text-blue-600">{v}.alif24.uz</code> },
    { key: 'is_active', label: 'Holat', render: (v) => <Badge text={v ? 'Faol' : 'Bloklangan'} variant={v ? 'success' : 'danger'} /> },
    { key: 'phone', label: 'Telefon' },
    { key: 'actions', label: '', render: (_, row) => (
      <button onClick={() => toggleBlock(row.id, row.is_active)} className="text-sm text-gray-500 hover:text-red-600">
        {row.is_active ? <Ban size={16} /> : <CheckCircle size={16} />}
      </button>
    )},
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Maktablar</h1>
        <button onClick={() => setShowCreate(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
          <Plus size={18} /> Yangi maktab
        </button>
      </div>
      <SearchBar value={search} onChange={setSearch} placeholder="Maktab qidirish..." />
      <DataTable columns={columns} data={schools} loading={loading} emptyMessage="Maktablar topilmadi" />
      <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />

      <Modal isOpen={showCreate} onClose={() => setShowCreate(false)} title="Yangi maktab qo'shish" size="md">
        <div className="space-y-4">
          <input placeholder="Subdomen (masalan: 31-maktab)" value={form.subdomain} onChange={(e) => setForm({ ...form, subdomain: e.target.value })} className="w-full border rounded-lg px-3 py-2" />
          <input placeholder="Maktab nomi" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full border rounded-lg px-3 py-2" />
          <input placeholder="Telefon" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} className="w-full border rounded-lg px-3 py-2" />
          <input placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="w-full border rounded-lg px-3 py-2" />
          <button onClick={handleCreate} className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">Yaratish</button>
        </div>
      </Modal>
    </div>
  );
}
