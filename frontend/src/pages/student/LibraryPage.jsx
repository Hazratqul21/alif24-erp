import { useState, useEffect } from 'react';
import { BookOpen, Search } from 'lucide-react';
import SearchBar from '../../components/common/SearchBar';
import Badge from '../../components/common/Badge';
import api from '../../services/api';

export default function StudentLibraryPage() {
  const [books, setBooks] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/library/books', { params: { search } }).then(res => setBooks((res.data || res).items || []))
      .catch(() => setBooks([])).finally(() => setLoading(false));
  }, [search]);

  const sampleBooks = books.length ? books : [
    { id: 1, title: 'Algebra va analiz asoslari', author: 'A. Abdurahmonov', available: 3 },
    { id: 2, title: 'Fizika 10-sinf', author: 'B. Toshmatov', available: 0 },
    { id: 3, title: "O'zbek adabiyoti", author: 'N. Karimov', available: 5 },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Kutubxona</h1>
      <SearchBar value={search} onChange={setSearch} placeholder="Kitob qidirish..." />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sampleBooks.map(b => (
          <div key={b.id} className="bg-white rounded-xl p-6 shadow-sm">
            <BookOpen size={32} className="text-blue-600 mb-3" />
            <h3 className="font-semibold mb-1">{b.title}</h3>
            <p className="text-gray-500 text-sm mb-3">{b.author}</p>
            <div className="flex justify-between items-center">
              <Badge text={b.available > 0 ? `${b.available} ta bor` : 'Mavjud emas'} variant={b.available > 0 ? 'success' : 'danger'} />
              {b.available > 0 && <button className="text-sm text-blue-600 hover:text-blue-800">Band qilish</button>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
