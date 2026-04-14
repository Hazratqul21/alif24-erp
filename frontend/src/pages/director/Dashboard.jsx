import { useState, useEffect } from 'react';
import { Users, GraduationCap, BookOpen, Wallet, CheckCircle, TrendingUp } from 'lucide-react';
import StatsCard from '../../components/common/StatsCard';
import Chart from '../../components/common/Chart';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import api from '../../services/api';

export default function DirectorDashboard() {
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/reports/director-dashboard').then(res => setStats(res.data || res)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner size="lg" text="Yuklanmoqda..." />;

  const attendanceData = [
    { name: 'Dush', present: 92, absent: 8 }, { name: 'Sesh', present: 95, absent: 5 },
    { name: 'Chor', present: 88, absent: 12 }, { name: 'Pay', present: 91, absent: 9 },
    { name: 'Jum', present: 94, absent: 6 },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Maktab boshqaruv paneli</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard title="Jami o'quvchilar" value={stats.total_students || 0} icon={GraduationCap} color="blue" trend="up" trendValue="5%" />
        <StatsCard title="O'qituvchilar" value={stats.total_teachers || 0} icon={Users} color="green" />
        <StatsCard title="Bugungi davomat" value={`${stats.attendance_rate || 92}%`} icon={CheckCircle} color="yellow" />
        <StatsCard title="Oylik daromad" value={`${(stats.monthly_revenue || 0).toLocaleString()} so'm`} icon={Wallet} color="purple" />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h2 className="text-lg font-semibold mb-4">Haftalik davomat</h2>
          <Chart type="bar" data={attendanceData} xKey="name" yKey="present" />
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h2 className="text-lg font-semibold mb-4">O'rtacha baho</h2>
          <Chart type="line" data={[
            { month: 'Sen', avg: 3.8 }, { month: 'Okt', avg: 3.9 }, { month: 'Noy', avg: 4.1 },
            { month: 'Dek', avg: 3.7 }, { month: 'Yan', avg: 4.0 }, { month: 'Fev', avg: 4.2 },
          ]} xKey="month" yKey="avg" />
        </div>
      </div>
    </div>
  );
}
