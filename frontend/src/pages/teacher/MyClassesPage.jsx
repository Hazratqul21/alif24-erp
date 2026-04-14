import { useState, useEffect } from 'react';
import { Users, BookOpen } from 'lucide-react';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import api from '../../services/api';

export default function MyClassesPage() {
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/academic/classes').then(res => setClasses((res.data || res).items || []))
      .catch(() => setClasses([])).finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner size="lg" />;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Mening sinflarim</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {classes.map(c => (
          <div key={c.id} className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
            <h3 className="text-xl font-bold text-blue-600 mb-2">{c.name}</h3>
            <div className="flex items-center gap-4 text-gray-500">
              <span className="flex items-center gap-1"><Users size={16} /> {c.student_count || 0} o'quvchi</span>
              <span className="flex items-center gap-1"><BookOpen size={16} /> {c.grade_level}-sinf</span>
            </div>
          </div>
        ))}
        {classes.length === 0 && <p className="text-gray-500 col-span-3">Sinflar topilmadi</p>}
      </div>
    </div>
  );
}
