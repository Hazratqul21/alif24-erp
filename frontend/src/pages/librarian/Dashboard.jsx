import { useState, useEffect } from 'react';
import { BookOpen, BookMarked, Clock, BarChart3 } from 'lucide-react';
import StatsCard from '../../components/common/StatsCard';
import Chart from '../../components/common/Chart';
import api from '../../services/api';

export default function LibrarianDashboard() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Kutubxona paneli</h1>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatsCard title="Jami kitoblar" value={1250} icon={BookOpen} color="blue" />
        <StatsCard title="Berilgan" value={89} icon={BookMarked} color="green" />
        <StatsCard title="Muddati o'tgan" value={12} icon={Clock} color="red" />
        <StatsCard title="Bu oy o'qilgan" value={234} icon={BarChart3} color="yellow" />
      </div>
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4">Oylik o'qish statistikasi</h2>
        <Chart type="line" data={[
          { month: 'Yan', books: 180 }, { month: 'Fev', books: 210 },
          { month: 'Mar', books: 195 }, { month: 'Apr', books: 234 },
        ]} xKey="month" yKey="books" />
      </div>
    </div>
  );
}
