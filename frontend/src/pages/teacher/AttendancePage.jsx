import { useState, useEffect } from 'react';
import { Check, X, Clock } from 'lucide-react';
import api from '../../services/api';

export default function TeacherAttendancePage() {
  const [classes, setClasses] = useState([]);
  const [selectedClass, setSelectedClass] = useState('');
  const [students, setStudents] = useState([]);
  const [attendance, setAttendance] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get('/academic/classes').then(res => setClasses((res.data || res).items || [])).catch(() => {});
  }, []);

  useEffect(() => {
    if (!selectedClass) return;
    api.get(`/academic/classes/${selectedClass}/students`).then(res => {
      const s = (res.data || res).items || res.data || res || [];
      setStudents(s);
      const init = {};
      s.forEach(st => { init[st.id] = 'present'; });
      setAttendance(init);
    }).catch(() => {});
  }, [selectedClass]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const records = Object.entries(attendance).map(([student_id, status]) => ({ student_id, status }));
      await api.post('/attendance/bulk', { class_id: selectedClass, date: new Date().toISOString().split('T')[0], records });
    } catch {} finally { setSaving(false); }
  };

  const statusBtn = (studentId, status, icon, color) => (
    <button onClick={() => setAttendance(prev => ({ ...prev, [studentId]: status }))}
      className={`p-2 rounded-lg transition-colors ${attendance[studentId] === status ? color : 'bg-gray-100 text-gray-400 hover:bg-gray-200'}`}>
      {icon}
    </button>
  );

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Davomat belgilash</h1>
      <select value={selectedClass} onChange={(e) => setSelectedClass(e.target.value)} className="border rounded-lg px-4 py-2 text-lg">
        <option value="">Sinf tanlang</option>
        {classes.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
      </select>
      {students.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm">
          <div className="p-4 border-b flex justify-between items-center">
            <span className="font-semibold">{students.length} o'quvchi</span>
            <button onClick={handleSave} disabled={saving} className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50">
              {saving ? 'Saqlanmoqda...' : 'Saqlash'}
            </button>
          </div>
          <div className="divide-y">
            {students.map((s, i) => (
              <div key={s.id} className="flex items-center justify-between px-4 py-3 hover:bg-gray-50">
                <div className="flex items-center gap-3">
                  <span className="text-gray-400 w-8">{i + 1}</span>
                  <span className="font-medium">{s.last_name} {s.first_name}</span>
                </div>
                <div className="flex gap-2">
                  {statusBtn(s.id, 'present', <Check size={18} />, 'bg-green-100 text-green-700')}
                  {statusBtn(s.id, 'late', <Clock size={18} />, 'bg-yellow-100 text-yellow-700')}
                  {statusBtn(s.id, 'absent', <X size={18} />, 'bg-red-100 text-red-700')}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
