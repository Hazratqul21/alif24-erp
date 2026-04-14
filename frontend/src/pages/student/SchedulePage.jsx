import { useState, useEffect } from 'react';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import api from '../../services/api';

const DAYS = ['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba'];
const TIMES = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00'];

export default function SchedulePage() {
  const [schedule, setSchedule] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/schedules/today').then(res => setSchedule((res.data || res).items || []))
      .catch(() => setSchedule([])).finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner size="lg" />;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dars jadvali</h1>
      <div className="bg-white rounded-xl shadow-sm overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-blue-600 text-white">
              <th className="p-3 text-left">Vaqt</th>
              {DAYS.map(d => <th key={d} className="p-3 text-center">{d}</th>)}
            </tr>
          </thead>
          <tbody>
            {TIMES.map(time => (
              <tr key={time} className="border-b hover:bg-gray-50">
                <td className="p-3 font-mono text-gray-500">{time}</td>
                {DAYS.map(day => {
                  const lesson = schedule.find(s => s.day_of_week === day && s.start_time?.startsWith(time));
                  return (
                    <td key={day} className="p-2 text-center">
                      {lesson ? (
                        <div className="bg-blue-50 rounded-lg p-2">
                          <div className="font-semibold text-sm text-blue-700">{lesson.subject_name || 'Fan'}</div>
                          <div className="text-xs text-gray-500">{lesson.room_number}</div>
                        </div>
                      ) : <span className="text-gray-300">—</span>}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
