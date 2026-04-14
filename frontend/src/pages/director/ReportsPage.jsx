import { useState } from 'react';
import { FileText, Download, BarChart3 } from 'lucide-react';

const reportTypes = [
  { id: 'attendance', name: 'Davomat hisoboti', icon: BarChart3, desc: 'Sinflar bo\'yicha davomat statistikasi' },
  { id: 'grades', name: 'Baholar hisoboti', icon: FileText, desc: 'O\'rtacha baholar va reyting' },
  { id: 'financial', name: 'Moliyaviy hisobot', icon: Download, desc: 'Daromad va xarajatlar' },
];

export default function ReportsPage() {
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Hisobotlar</h1>
      <div className="flex gap-4">
        <input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} className="border rounded-lg px-3 py-2" />
        <input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} className="border rounded-lg px-3 py-2" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {reportTypes.map(r => (
          <div key={r.id} className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
            <r.icon size={32} className="text-blue-600 mb-4" />
            <h3 className="text-lg font-semibold mb-2">{r.name}</h3>
            <p className="text-gray-500 text-sm mb-4">{r.desc}</p>
            <button className="flex items-center gap-2 text-blue-600 hover:text-blue-800"><Download size={16} /> Yuklab olish</button>
          </div>
        ))}
      </div>
    </div>
  );
}
