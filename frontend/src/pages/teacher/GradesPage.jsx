import { useState, useEffect } from 'react';
import api from '../../services/api';

export default function TeacherGradesPage() {
  const [classes, setClasses] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [selectedClass, setSelectedClass] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('');
  const [students, setStudents] = useState([]);
  const [grades, setGrades] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get('/academic/classes').then(res => setClasses((res.data || res).items || [])).catch(() => {});
    api.get('/academic/subjects').then(res => setSubjects((res.data || res).items || [])).catch(() => {});
  }, []);

  useEffect(() => {
    if (!selectedClass) return;
    api.get(`/academic/classes/${selectedClass}/students`).then(res => {
      setStudents((res.data || res).items || res.data || res || []);
    }).catch(() => {});
  }, [selectedClass]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const entries = Object.entries(grades).filter(([, v]) => v).map(([student_id, grade_value]) => ({
        student_id, subject_id: selectedSubject, grade_value: parseInt(grade_value), grade_date: new Date().toISOString().split('T')[0],
      }));
      await api.post('/grades/bulk', { grades: entries });
    } catch {} finally { setSaving(false); }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Baho qo'yish</h1>
      <div className="flex gap-4 flex-wrap">
        <select value={selectedClass} onChange={(e) => setSelectedClass(e.target.value)} className="border rounded-lg px-4 py-2">
          <option value="">Sinf tanlang</option>
          {classes.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <select value={selectedSubject} onChange={(e) => setSelectedSubject(e.target.value)} className="border rounded-lg px-4 py-2">
          <option value="">Fan tanlang</option>
          {subjects.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
      </div>
      {students.length > 0 && selectedSubject && (
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
                <div className="flex gap-1">
                  {[1, 2, 3, 4, 5].map(g => (
                    <button key={g} onClick={() => setGrades(prev => ({ ...prev, [s.id]: g }))}
                      className={`w-10 h-10 rounded-lg font-bold text-lg transition-colors ${grades[s.id] === g ? 'bg-blue-600 text-white' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'}`}>
                      {g}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
