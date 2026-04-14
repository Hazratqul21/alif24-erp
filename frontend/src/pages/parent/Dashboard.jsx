import { useState, useEffect } from 'react';
import { Users, Star, CheckCircle, Wallet, AlertTriangle } from 'lucide-react';
import StatsCard from '../../components/common/StatsCard';
import Badge from '../../components/common/Badge';
import api from '../../services/api';

export default function ParentDashboard() {
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/reports/parent-dashboard').then(res => setData(res.data || res)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const children = data.children || [
    { name: 'Ali Karimov', class: '5-A', avg_grade: 4.3, attendance: '95%', status: 'present' },
    { name: 'Malika Karimova', class: '3-B', avg_grade: 4.7, attendance: '98%', status: 'present' },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Ota-ona paneli</h1>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatsCard title="Farzandlar" value={children.length} icon={Users} color="blue" />
        <StatsCard title="O'rtacha baho" value="4.5" icon={Star} color="green" />
        <StatsCard title="Davomat" value="96%" icon={CheckCircle} color="yellow" />
        <StatsCard title="Qarz" value="0 so'm" icon={Wallet} color="purple" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {children.map((child, i) => (
          <div key={i} className="bg-white rounded-xl p-6 shadow-sm">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-bold">{child.name}</h3>
                <p className="text-gray-500">{child.class} sinf</p>
              </div>
              <Badge text={child.status === 'present' ? 'Maktabda' : 'Kelmagan'} variant={child.status === 'present' ? 'success' : 'danger'} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-blue-50 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-blue-600">{child.avg_grade}</div>
                <div className="text-sm text-gray-500">O'rtacha baho</div>
              </div>
              <div className="bg-green-50 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-green-600">{child.attendance}</div>
                <div className="text-sm text-gray-500">Davomat</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
