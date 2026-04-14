import { useState, useRef, useEffect } from 'react';
import { Bell, Check } from 'lucide-react';

const NotificationBell = ({ notifications = [], onMarkRead, onMarkAllRead }) => {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  const unreadCount = notifications.filter((n) => !n.read).length;

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleClick = (notification) => {
    if (!notification.read) onMarkRead?.(notification.id);
  };

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="relative p-2 rounded-xl text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 flex items-center justify-center min-w-[18px] h-[18px] px-1 rounded-full bg-red-500 text-white text-[10px] font-bold ring-2 ring-white">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden z-50">
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
            <h4 className="text-sm font-semibold text-gray-800">Уведомления</h4>
            {unreadCount > 0 && (
              <button
                onClick={() => onMarkAllRead?.()}
                className="text-xs text-blue-600 hover:text-blue-700 font-medium"
              >
                Прочитать все
              </button>
            )}
          </div>

          <div className="max-h-80 overflow-y-auto divide-y divide-gray-50">
            {notifications.length === 0 ? (
              <div className="px-4 py-8 text-center text-sm text-gray-400">
                Нет уведомлений
              </div>
            ) : (
              notifications.map((n) => (
                <button
                  key={n.id}
                  onClick={() => handleClick(n)}
                  className={`w-full text-left px-4 py-3 flex items-start gap-3 transition-colors hover:bg-gray-50 ${
                    !n.read ? 'bg-blue-50/40' : ''
                  }`}
                >
                  <div className="flex-1 min-w-0">
                    <p className={`text-sm ${!n.read ? 'font-medium text-gray-800' : 'text-gray-600'}`}>
                      {n.title}
                    </p>
                    {n.message && (
                      <p className="text-xs text-gray-400 mt-0.5 truncate">{n.message}</p>
                    )}
                    {n.time && <p className="text-xs text-gray-400 mt-1">{n.time}</p>}
                  </div>
                  {!n.read && <span className="mt-1.5 w-2 h-2 rounded-full bg-blue-500 shrink-0" />}
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationBell;
