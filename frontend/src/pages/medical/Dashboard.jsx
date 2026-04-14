import { useState } from 'react';
import { Heart, Stethoscope, ShieldAlert, Activity } from 'lucide-react';
import StatsCard from '../../components/common/StatsCard';
import Chart from '../../components/common/Chart';

export default function MedicalDashboard() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Tibbiyot paneli</h1>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatsCard title="Tibbiy kartalar" value={450} icon={Heart} color="red" />
        <StatsCard title="Bu oy ko'riklar" value={32} icon={Stethoscope} color="blue" />
        <StatsCard title="Karantinda" value={3} icon={ShieldAlert} color="yellow" />
        <StatsCard title="Sog'lom" value="96%" icon={Activity} color="green" />
      </div>
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4">Ko'riklar statistikasi</h2>
        <Chart type="bar" data={[
          { month: 'Sen', exams: 45 }, { month: 'Okt', exams: 38 },
          { month: 'Noy', exams: 52 }, { month: 'Dek', exams: 28 },
          { month: 'Yan', exams: 30 }, { month: 'Fev', exams: 35 },
        ]} xKey="month" yKey="exams" />
      </div>
    </div>
  );
}
