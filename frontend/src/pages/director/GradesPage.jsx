import { useState, useEffect } from 'react';
import Chart from '../../components/common/Chart';
import DataTable from '../../components/common/DataTable';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import api from '../../services/api';

export default function GradesPage() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({});

  useEffect(() => {
    api.get('/reports/director-dashboard').then(res => setData(res.data || res)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner size="lg" />;

  const subjectData = [
    { subject: 'Matematika', avg: 4.1 }, { subject: 'Ona tili', avg: 3.8 },
    { subject: 'Ingliz tili', avg: 3.5 }, { subject: 'Fizika', avg: 3.9 },
    { subject: 'Kimyo', avg: 4.0 }, { subject: 'Tarix', avg: 4.2 },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Baholar tahlili</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h2 className="text-lg font-semibold mb-4">Fanlar bo'yicha o'rtacha baho</h2>
          <Chart type="bar" data={subjectData} xKey="subject" yKey="avg" />
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h2 className="text-lg font-semibold mb-4">Sinflar reytingi</h2>
          <DataTable columns={[
            { key: 'rank', label: '#' },
            { key: 'class_name', label: 'Sinf' },
            { key: 'avg_grade', label: 'O\'rtacha baho' },
            { key: 'student_count', label: 'O\'quvchilar' },
          ]} data={[
            { rank: 1, class_name: '10-A', avg_grade: 4.5, student_count: 28 },
            { rank: 2, class_name: '9-B', avg_grade: 4.3, student_count: 30 },
            { rank: 3, class_name: '11-A', avg_grade: 4.2, student_count: 25 },
          ]} loading={false} />
        </div>
      </div>
    </div>
  );
}
