import { useState, useEffect } from 'react';
import { Wallet, TrendingUp, AlertTriangle, FileText } from 'lucide-react';
import StatsCard from '../../components/common/StatsCard';
import Chart from '../../components/common/Chart';
import api from '../../services/api';

export default function AccountantDashboard() {
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/reports/financial').then(res => setData(res.data || res)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Moliya paneli</h1>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatsCard title="Oylik daromad" value="45,000,000 so'm" icon={Wallet} color="green" />
        <StatsCard title="O'sish" value="+12%" icon={TrendingUp} color="blue" />
        <StatsCard title="Jami qarzlar" value="8,500,000 so'm" icon={AlertTriangle} color="red" />
        <StatsCard title="Hisob-fakturalar" value="156" icon={FileText} color="yellow" />
      </div>
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4">Oylik daromad dinamikasi</h2>
        <Chart type="bar" data={[
          { month: 'Yan', income: 38000000 }, { month: 'Fev', income: 40000000 },
          { month: 'Mar', income: 42000000 }, { month: 'Apr', income: 45000000 },
        ]} xKey="month" yKey="income" />
      </div>
    </div>
  );
}
