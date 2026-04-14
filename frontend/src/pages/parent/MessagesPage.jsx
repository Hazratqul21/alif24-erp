import { useState } from 'react';
import { Send } from 'lucide-react';

export default function MessagesPage() {
  const [selectedThread, setSelectedThread] = useState(0);
  const [newMessage, setNewMessage] = useState('');

  const threads = [
    { id: 1, teacher: 'A. Karimov', subject: 'Matematika', lastMessage: 'Ali yaxshi o\'qiyapti', time: '10:30' },
    { id: 2, teacher: 'S. Rahimova', subject: 'Ona tili', lastMessage: 'Uy vazifasini bajarmadi', time: '09:15' },
  ];

  const messages = [
    { sender: 'teacher', text: 'Assalomu alaykum! Ali bugun darsda faol qatnashdi.', time: '09:00' },
    { sender: 'parent', text: 'Rahmat, ustoz! Uyda ham ko\'p mashq qilayapti.', time: '09:15' },
    { sender: 'teacher', text: 'Ali yaxshi o\'qiyapti, davom etsin.', time: '10:30' },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Xabarlar</h1>
      <div className="bg-white rounded-xl shadow-sm flex h-[500px]">
        <div className="w-1/3 border-r overflow-y-auto">
          {threads.map((t, i) => (
            <div key={t.id} onClick={() => setSelectedThread(i)}
              className={`p-4 cursor-pointer hover:bg-gray-50 border-b ${selectedThread === i ? 'bg-blue-50' : ''}`}>
              <div className="font-semibold">{t.teacher}</div>
              <div className="text-sm text-gray-500">{t.subject}</div>
              <div className="text-sm text-gray-400 truncate">{t.lastMessage}</div>
            </div>
          ))}
        </div>
        <div className="flex-1 flex flex-col">
          <div className="p-4 border-b">
            <h3 className="font-semibold">{threads[selectedThread]?.teacher}</h3>
            <p className="text-sm text-gray-500">{threads[selectedThread]?.subject}</p>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.sender === 'parent' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-xs px-4 py-2 rounded-2xl ${m.sender === 'parent' ? 'bg-blue-600 text-white' : 'bg-gray-100'}`}>
                  <p className="text-sm">{m.text}</p>
                  <p className={`text-xs mt-1 ${m.sender === 'parent' ? 'text-blue-200' : 'text-gray-400'}`}>{m.time}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="p-4 border-t flex gap-2">
            <input value={newMessage} onChange={(e) => setNewMessage(e.target.value)} placeholder="Xabar yozing..." className="flex-1 border rounded-lg px-3 py-2" />
            <button className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700"><Send size={18} /></button>
          </div>
        </div>
      </div>
    </div>
  );
}
