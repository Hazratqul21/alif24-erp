import { useState, useEffect } from 'react';
import { Star } from 'lucide-react';
import Chart from '../../components/common/Chart';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import api from '../../services/api';

export default function StudentGradesPage() {
  const [grades, setGrades] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/grades/mine').then(res => setGrades((res.data || res).grades || []))
      .catch(() => setGrades([])).finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner size="lg" />;

  const subjectAverages = [
    { subject: 'Matematika', avg: 4.5 }, { subject: 'Ona tili', avg: 3.8 },
    { subject: 'Ingliz tili', avg: 4.2 }, { subject: 'Fizika', avg: 3.9 },
    { subject: 'Tarix', avg: 4.7 }, { subject: 'Kimyo', avg: 4.0 },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Baholarim</h1>
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <div className="flex items-center gap-2 mb-4">
          <Star className="text-yellow-500" size={24} />
          <h2 className="text-xl font-bold">GPA: 4.2</h2>
        </div>
        <Chart type="bar" data={subjectAverages} xKey="subject" yKey="avg" />
      </div>
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4">So'nggi baholar</h2>
        <div className="space-y-2">
          {(grades.length ? grades : [
            { subject: 'Matematika', grade: 5, date: '2026-04-10', type: 'Nazorat ishi' },
            { subject: 'Fizika', grade: 4, date: '2026-04-09', type: 'Darsda' },
            { subject: 'Ingliz tili', grade: 5, date: '2026-04-08', type: 'Test' },
          ]).map((g, i) => (
            <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
              <div>
                <span className="font-semibold">{g.subject || g.subject_name}</span>
                <span className="text-gray-400 text-sm ml-2">{g.type || g.grade_type}</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-gray-400 text-sm">{g.date || g.grade_date}</span>
                <span className={`w-10 h-10 rounded-lg flex items-center justify-center font-bold text-lg ${(g.grade || g.grade_value) >= 4 ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                  {g.grade || g.grade_value}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
