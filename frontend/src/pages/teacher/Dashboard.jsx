import { useState, useEffect } from 'react';
import { Clock, Users, BookOpen, Star } from 'lucide-react';
import StatsCard from '../../components/common/StatsCard';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import api from '../../services/api';

export default function TeacherDashboard() {
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/reports/teacher-dashboard').then(res => setData(res.data || res)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner size="lg" />;

  const schedule = data.today_schedule || [
    { time: '08:00 - 08:45', subject: 'Matematika', class: '5-A', room: '201' },
    { time: '09:00 - 09:45', subject: 'Matematika', class: '6-B', room: '201' },
    { time: '10:00 - 10:45', subject: 'Geometriya', class: '7-A', room: '305' },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Salom, o'qituvchi!</h1>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatsCard title="Bugungi darslar" value={schedule.length} icon={Clock} color="blue" />
        <StatsCard title="Mening sinflarim" value={data.my_classes || 4} icon={Users} color="green" />
        <StatsCard title="Jami o'quvchilar" value={data.total_students || 120} icon={BookOpen} color="yellow" />
        <StatsCard title="O'rtacha baho" value={data.avg_grade || '4.2'} icon={Star} color="purple" />
      </div>
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4">Bugungi dars jadvali</h2>
        <div className="space-y-3">
          {schedule.map((s, i) => (
            <div key={i} className="flex items-center gap-4 p-3 rounded-lg bg-gray-50 hover:bg-blue-50 transition-colors">
              <span className="text-sm font-mono text-gray-500 w-28">{s.time}</span>
              <span className="font-semibold flex-1">{s.subject}</span>
              <span className="text-blue-600 font-medium">{s.class}</span>
              <span className="text-gray-400 text-sm">{s.room}-xona</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
