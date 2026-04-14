import { useState, useEffect } from 'react';
import { Calendar as CalendarIcon } from 'lucide-react';
import Chart from '../../components/common/Chart';
import DataTable from '../../components/common/DataTable';
import Badge from '../../components/common/Badge';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import api from '../../services/api';

export default function AttendancePage() {
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [stats, setStats] = useState([]);
  const [absentStudents, setAbsentStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.get('/attendance/reports', { params: { date } })
      .then(res => { const d = res.data || res; setStats(d.class_stats || []); setAbsentStudents(d.absent_students || []); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [date]);

  if (loading) return <LoadingSpinner size="lg" />;

  const columns = [
    { key: 'student_name', label: 'O\'quvchi' },
    { key: 'class_name', label: 'Sinf' },
    { key: 'status', label: 'Holat', render: (v) => <Badge text={v === 'absent' ? 'Kelmagan' : 'Kech qolgan'} variant={v === 'absent' ? 'danger' : 'warning'} /> },
    { key: 'reason', label: 'Sabab' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Davomat</h1>
        <div className="flex items-center gap-2">
          <CalendarIcon size={18} className="text-gray-500" />
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} className="border rounded-lg px-3 py-2" />
        </div>
      </div>
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4">Sinflar bo'yicha davomat</h2>
        <Chart type="bar" data={stats.length ? stats : [
          { name: '1-A', present: 28, absent: 2 }, { name: '2-A', present: 25, absent: 5 },
          { name: '3-A', present: 30, absent: 0 }, { name: '4-A', present: 27, absent: 3 },
        ]} xKey="name" yKey="present" />
      </div>
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4">Kelmagan o'quvchilar</h2>
        <DataTable columns={columns} data={absentStudents} loading={false} emptyMessage="Barcha o'quvchilar kelgan" />
      </div>
    </div>
  );
}
