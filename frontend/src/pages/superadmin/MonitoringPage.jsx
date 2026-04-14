import { useState, useEffect } from 'react';
import { Activity, Server, Database, AlertTriangle } from 'lucide-react';
import StatsCard from '../../components/common/StatsCard';
import Chart from '../../components/common/Chart';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import api from '../../services/api';

export default function MonitoringPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/superadmin/monitoring/stats').then(res => setStats(res.data || res)).catch(() => setStats({})).finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner size="lg" text="Monitoring yuklanmoqda..." />;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Monitoring</h1>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatsCard title="Server holati" value="Faol" icon={Server} color="green" />
        <StatsCard title="DB hajmi" value={stats?.db_size || 'N/A'} icon={Database} color="blue" />
        <StatsCard title="So'rovlar/soat" value={stats?.queries_per_hour || 0} icon={Activity} color="yellow" />
        <StatsCard title="Xatoliklar" value={stats?.error_count || 0} icon={AlertTriangle} color="red" />
      </div>
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4">Tizim yuklama</h2>
        <Chart type="line" data={[
          { time: '00:00', load: 20 }, { time: '04:00', load: 15 }, { time: '08:00', load: 45 },
          { time: '12:00', load: 78 }, { time: '16:00', load: 62 }, { time: '20:00', load: 35 },
        ]} xKey="time" yKey="load" />
      </div>
    </div>
  );
}
