import { useState, useEffect } from 'react';
import { Plus, Users } from 'lucide-react';
import DataTable from '../../components/common/DataTable';
import Modal from '../../components/common/Modal';
import api from '../../services/api';

export default function ClassesPage() {
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: '', grade_level: '', section: '', capacity: 30 });

  useEffect(() => {
    api.get('/academic/classes').then(res => setClasses((res.data || res).items || []))
      .catch(() => setClasses([])).finally(() => setLoading(false));
  }, []);

  const handleCreate = async () => {
    try { await api.post('/academic/classes', form); setShowCreate(false); window.location.reload(); } catch {}
  };

  const columns = [
    { key: 'name', label: 'Sinf nomi' },
    { key: 'grade_level', label: 'Daraja' },
    { key: 'section', label: 'Bo\'lim' },
    { key: 'capacity', label: 'Sig\'im' },
    { key: 'student_count', label: 'O\'quvchilar', render: (v) => <span className="flex items-center gap-1"><Users size={14} /> {v || 0}</span> },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Sinflar</h1>
        <button onClick={() => setShowCreate(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"><Plus size={18} /> Yangi sinf</button>
      </div>
      <DataTable columns={columns} data={classes} loading={loading} emptyMessage="Sinflar topilmadi" />
      <Modal isOpen={showCreate} onClose={() => setShowCreate(false)} title="Yangi sinf" size="md">
        <div className="space-y-4">
          <input placeholder="Sinf nomi (masalan: 5-A)" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full border rounded-lg px-3 py-2" />
          <input placeholder="Daraja (masalan: 5)" value={form.grade_level} onChange={(e) => setForm({ ...form, grade_level: e.target.value })} className="w-full border rounded-lg px-3 py-2" />
          <input placeholder="Bo'lim (masalan: A)" value={form.section} onChange={(e) => setForm({ ...form, section: e.target.value })} className="w-full border rounded-lg px-3 py-2" />
          <input type="number" placeholder="Sig'im" value={form.capacity} onChange={(e) => setForm({ ...form, capacity: parseInt(e.target.value) || 30 })} className="w-full border rounded-lg px-3 py-2" />
          <button onClick={handleCreate} className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">Yaratish</button>
        </div>
      </Modal>
    </div>
  );
}
