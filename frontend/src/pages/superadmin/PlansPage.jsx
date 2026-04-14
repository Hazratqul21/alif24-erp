import { useState, useEffect } from 'react';
import { Plus, Edit2 } from 'lucide-react';
import DataTable from '../../components/common/DataTable';
import Modal from '../../components/common/Modal';
import Badge from '../../components/common/Badge';
import api from '../../services/api';

export default function PlansPage() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editPlan, setEditPlan] = useState(null);
  const [form, setForm] = useState({ name: '', price_monthly: '', price_yearly: '', max_users: 100, max_students: 500 });

  useEffect(() => {
    api.get('/superadmin/plans').then(res => { setPlans((res.data || res).items || res.data || res || []); }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const columns = [
    { key: 'name', label: 'Tarif nomi' },
    { key: 'price_monthly', label: 'Oylik narx', render: (v) => `${Number(v || 0).toLocaleString()} so'm` },
    { key: 'price_yearly', label: 'Yillik narx', render: (v) => `${Number(v || 0).toLocaleString()} so'm` },
    { key: 'max_students', label: 'Max o\'quvchilar' },
    { key: 'is_active', label: 'Holat', render: (v) => <Badge text={v ? 'Faol' : 'Nofaol'} variant={v ? 'success' : 'warning'} /> },
    { key: 'actions', label: '', render: (_, row) => (
      <button onClick={() => { setEditPlan(row); setShowModal(true); }} className="text-blue-600 hover:text-blue-800"><Edit2 size={16} /></button>
    )},
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Tariflar</h1>
        <button onClick={() => { setEditPlan(null); setShowModal(true); }} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"><Plus size={18} /> Yangi tarif</button>
      </div>
      <DataTable columns={columns} data={plans} loading={loading} emptyMessage="Tariflar topilmadi" />
      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title={editPlan ? 'Tarifni tahrirlash' : 'Yangi tarif'} size="md">
        <div className="space-y-4">
          <input placeholder="Tarif nomi" className="w-full border rounded-lg px-3 py-2" defaultValue={editPlan?.name} />
          <input placeholder="Oylik narx" type="number" className="w-full border rounded-lg px-3 py-2" defaultValue={editPlan?.price_monthly} />
          <input placeholder="Yillik narx" type="number" className="w-full border rounded-lg px-3 py-2" defaultValue={editPlan?.price_yearly} />
          <button className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">Saqlash</button>
        </div>
      </Modal>
    </div>
  );
}
