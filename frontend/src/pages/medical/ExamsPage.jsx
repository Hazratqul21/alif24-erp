import { useState, useEffect } from 'react';
import { Plus } from 'lucide-react';
import DataTable from '../../components/common/DataTable';
import api from '../../services/api';

export default function MedicalExamsPage() {
  const [exams, setExams] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/medical/exams').then(res => setExams((res.data || res).items || []))
      .catch(() => {}).finally(() => setLoading(false));
  }, []);

  const columns = [
    { key: 'student_name', label: 'O\'quvchi' },
    { key: 'exam_date', label: 'Sana' },
    { key: 'height', label: 'Bo\'y (sm)' },
    { key: 'weight', label: 'Vazn (kg)' },
    { key: 'diagnosis', label: 'Tashxis' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Tibbiy ko'riklar</h1>
        <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"><Plus size={18} /> Yangi ko'rik</button>
      </div>
      <DataTable columns={columns} data={exams} loading={loading} emptyMessage="Ko'riklar topilmadi" />
    </div>
  );
}
