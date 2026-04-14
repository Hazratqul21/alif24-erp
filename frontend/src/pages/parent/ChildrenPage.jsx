import { useState } from 'react';
import Chart from '../../components/common/Chart';
import Badge from '../../components/common/Badge';

export default function ChildrenPage() {
  const [selectedChild, setSelectedChild] = useState(0);

  const children = [
    { name: 'Ali Karimov', class: '5-A', grades: [
      { subject: 'Matematika', avg: 4.5 }, { subject: 'Ona tili', avg: 3.8 }, { subject: 'Ingliz tili', avg: 4.2 },
    ]},
    { name: 'Malika Karimova', class: '3-B', grades: [
      { subject: 'Matematika', avg: 4.8 }, { subject: 'Ona tili', avg: 4.5 }, { subject: 'Tabiatshunoslik', avg: 4.9 },
    ]},
  ];

  const child = children[selectedChild];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Farzandlarim</h1>
      <div className="flex gap-2">
        {children.map((c, i) => (
          <button key={i} onClick={() => setSelectedChild(i)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${selectedChild === i ? 'bg-blue-600 text-white' : 'bg-gray-100 hover:bg-gray-200'}`}>
            {c.name}
          </button>
        ))}
      </div>
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-xl font-bold">{child.name}</h2>
            <p className="text-gray-500">{child.class} sinf</p>
          </div>
          <Badge text="Faol" variant="success" />
        </div>
        <Chart type="bar" data={child.grades} xKey="subject" yKey="avg" />
      </div>
    </div>
  );
}
