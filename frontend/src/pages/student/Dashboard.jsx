import { useState, useEffect } from 'react';
import { CalendarDays, Star, BookOpen, Clock } from 'lucide-react';
import StatsCard from '../../components/common/StatsCard';
import Badge from '../../components/common/Badge';
import api from '../../services/api';

export default function StudentDashboard() {
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/reports/teacher-dashboard').then(res => setData(res.data || res)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const todaySchedule = [
    { time: '08:00', subject: 'Matematika', teacher: 'A. Karimov', room: '201' },
    { time: '09:00', subject: 'Ona tili', teacher: 'S. Rahimova', room: '105' },
    { time: '10:00', subject: 'Ingliz tili', teacher: 'D. Wilson', room: '303' },
    { time: '11:00', subject: 'Fizika', teacher: 'B. Toshmatov', room: 'Lab 1' },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Salom, o'quvchi!</h1>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatsCard title="Bugungi darslar" value={todaySchedule.length} icon={CalendarDays} color="blue" />
        <StatsCard title="O'rtacha baho" value="4.3" icon={Star} color="green" />
        <StatsCard title="Uy vazifalari" value="3" icon={BookOpen} color="yellow" />
        <StatsCard title="Kutubxona" value="2 kitob" icon={Clock} color="purple" />
      </div>
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4">Bugungi dars jadvali</h2>
        <div className="space-y-3">
          {todaySchedule.map((s, i) => (
            <div key={i} className="flex items-center gap-4 p-3 rounded-lg bg-gray-50">
              <span className="text-sm font-mono text-gray-500 w-16">{s.time}</span>
              <span className="font-semibold flex-1">{s.subject}</span>
              <span className="text-gray-500">{s.teacher}</span>
              <Badge text={s.room} variant="info" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
