import { useState, useEffect } from 'react';
import { Plus } from 'lucide-react';
import DataTable from '../../components/common/DataTable';
import Modal from '../../components/common/Modal';
import Badge from '../../components/common/Badge';
import api from '../../services/api';

export default function TeacherHomeworkPage() {
  const [homework, setHomework] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ title: '', description: '', due_date: '', class_id: '', subject_id: '' });

  useEffect(() => {
    api.get('/homework').then(res => setHomework((res.data || res).items || [])).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const columns = [
    { key: 'title', label: 'Sarlavha' },
    { key: 'class_name', label: 'Sinf' },
    { key: 'subject_name', label: 'Fan' },
    { key: 'due_date', label: 'Muddat' },
    { key: 'submission_count', label: 'Topshirildi', render: (v) => <Badge text={`${v || 0} ta`} variant="info" /> },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Uy vazifalari</h1>
        <button onClick={() => setShowCreate(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"><Plus size={18} /> Yangi vazifa</button>
      </div>
      <DataTable columns={columns} data={homework} loading={loading} emptyMessage="Uy vazifalari topilmadi" />
      <Modal isOpen={showCreate} onClose={() => setShowCreate(false)} title="Yangi uy vazifasi" size="lg">
        <div className="space-y-4">
          <input placeholder="Sarlavha" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="w-full border rounded-lg px-3 py-2" />
          <textarea placeholder="Tavsif" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={4} className="w-full border rounded-lg px-3 py-2" />
          <input type="date" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} className="w-full border rounded-lg px-3 py-2" />
          <button className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">Yaratish</button>
        </div>
      </Modal>
    </div>
  );
}
