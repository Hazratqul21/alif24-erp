import { useState, useEffect } from 'react';
import { Upload } from 'lucide-react';
import Badge from '../../components/common/Badge';
import Modal from '../../components/common/Modal';
import api from '../../services/api';

export default function StudentHomeworkPage() {
  const [homework, setHomework] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showSubmit, setShowSubmit] = useState(null);

  useEffect(() => {
    api.get('/homework').then(res => setHomework((res.data || res).items || []))
      .catch(() => setHomework([])).finally(() => setLoading(false));
  }, []);

  const tasks = homework.length ? homework : [
    { id: 1, title: 'Algebra 5-mashq', subject: 'Matematika', due_date: '2026-04-15', status: 'pending' },
    { id: 2, title: 'Essay yozish', subject: 'Ona tili', due_date: '2026-04-16', status: 'submitted' },
    { id: 3, title: 'Lab ishi #3', subject: 'Fizika', due_date: '2026-04-14', status: 'graded', grade: 4 },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Uy vazifalari</h1>
      <div className="space-y-4">
        {tasks.map(hw => (
          <div key={hw.id} className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-semibold text-lg">{hw.title}</h3>
                <p className="text-gray-500">{hw.subject || hw.subject_name} • Muddat: {hw.due_date}</p>
              </div>
              <div className="flex items-center gap-2">
                {hw.status === 'pending' && <Badge text="Kutilmoqda" variant="warning" />}
                {hw.status === 'submitted' && <Badge text="Topshirildi" variant="info" />}
                {hw.status === 'graded' && <Badge text={`Baho: ${hw.grade}`} variant="success" />}
                {hw.status === 'pending' && (
                  <button onClick={() => setShowSubmit(hw)} className="flex items-center gap-1 bg-blue-600 text-white px-3 py-1 rounded-lg text-sm hover:bg-blue-700">
                    <Upload size={14} /> Topshirish
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
      <Modal isOpen={!!showSubmit} onClose={() => setShowSubmit(null)} title="Vazifani topshirish" size="md">
        <div className="space-y-4">
          <textarea placeholder="Javobingiz..." rows={4} className="w-full border rounded-lg px-3 py-2" />
          <input type="file" className="w-full" />
          <button className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">Topshirish</button>
        </div>
      </Modal>
    </div>
  );
}
