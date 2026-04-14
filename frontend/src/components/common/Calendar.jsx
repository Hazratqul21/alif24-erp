import { useState, useMemo } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import {
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  eachDayOfInterval,
  format,
  isSameMonth,
  isSameDay,
  addMonths,
  subMonths,
  isToday,
} from 'date-fns';
import { ru } from 'date-fns/locale';

const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

const Calendar = ({ events = [], onDateClick, selectedDate }) => {
  const [current, setCurrent] = useState(new Date());

  const days = useMemo(() => {
    const monthStart = startOfMonth(current);
    const monthEnd = endOfMonth(current);
    const start = startOfWeek(monthStart, { weekStartsOn: 1 });
    const end = endOfWeek(monthEnd, { weekStartsOn: 1 });
    return eachDayOfInterval({ start, end });
  }, [current]);

  const eventsByDate = useMemo(() => {
    const map = {};
    events.forEach((ev) => {
      const key = format(new Date(ev.date), 'yyyy-MM-dd');
      (map[key] ??= []).push(ev);
    });
    return map;
  }, [events]);

  return (
    <div className="rounded-2xl border border-gray-200 bg-white shadow-sm p-5">
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={() => setCurrent((d) => subMonths(d, 1))}
          className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>
        <h3 className="text-sm font-semibold text-gray-800 capitalize">
          {format(current, 'LLLL yyyy', { locale: ru })}
        </h3>
        <button
          onClick={() => setCurrent((d) => addMonths(d, 1))}
          className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>

      <div className="grid grid-cols-7 gap-px">
        {weekDays.map((d) => (
          <div key={d} className="text-center text-xs font-medium text-gray-400 py-2">
            {d}
          </div>
        ))}

        {days.map((day) => {
          const key = format(day, 'yyyy-MM-dd');
          const dayEvents = eventsByDate[key] || [];
          const inMonth = isSameMonth(day, current);
          const selected = selectedDate && isSameDay(day, new Date(selectedDate));
          const today = isToday(day);

          return (
            <button
              key={key}
              onClick={() => onDateClick?.(day)}
              className={`relative flex flex-col items-center py-2 rounded-lg text-sm transition-colors ${
                !inMonth ? 'text-gray-300' : today ? 'font-bold text-blue-600' : 'text-gray-700'
              } ${selected ? 'bg-blue-600 !text-white' : 'hover:bg-gray-100'}`}
            >
              {format(day, 'd')}
              {dayEvents.length > 0 && (
                <div className="flex gap-0.5 mt-0.5">
                  {dayEvents.slice(0, 3).map((ev, i) => (
                    <span
                      key={i}
                      className="w-1.5 h-1.5 rounded-full"
                      style={{ backgroundColor: ev.color || '#3b82f6' }}
                    />
                  ))}
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default Calendar;
