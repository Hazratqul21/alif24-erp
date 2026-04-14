import { useState, useEffect } from 'react';
import { School, Users, DollarSign, Activity } from 'lucide-react';
import StatsCard from '../../components/common/StatsCard';
import Chart from '../../components/common/Chart';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import api from '../../services/api';

export default function SuperAdminDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.get('/superadmin/monitoring/stats');
        setStats(res.data || res);
      } catch {
        setStats({ total_tenants: 0, active_users: 0, total_revenue: 0, active_tenants: 0 });
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) return <LoadingSpinner size="lg" text="Yuklanmoqda..." />;

  const chartData = [
    { name: 'Yan', users: 120 }, { name: 'Fev', users: 250 },
    { name: 'Mar', users: 380 }, { name: 'Apr', users: 520 },
    { name: 'May', users: 690 }, { name: 'Iyun', users: 810 },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Super Admin Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard title="Jami maktablar" value={stats?.total_tenants || 0} icon={School} color="blue" />
        <StatsCard title="Faol foydalanuvchilar" value={stats?.active_users || 0} icon={Users} color="green" />
        <StatsCard title="Oylik daromad" value={`${(stats?.total_revenue || 0).toLocaleString()} so'm`} icon={DollarSign} color="yellow" />
        <StatsCard title="Faol maktablar" value={stats?.active_tenants || 0} icon={Activity} color="purple" />
      </div>
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4">Foydalanuvchilar o'sishi</h2>
        <Chart type="line" data={chartData} xKey="name" yKey="users" />
      </div>
    </div>
  );
}
