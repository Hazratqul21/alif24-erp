import { useState, useEffect } from 'react';
import { Plus } from 'lucide-react';
import DataTable from '../../components/common/DataTable';
import SearchBar from '../../components/common/SearchBar';
import Pagination from '../../components/common/Pagination';
import Modal from '../../components/common/Modal';
import api from '../../services/api';

export default function BooksPage() {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [showAdd, setShowAdd] = useState(false);

  useEffect(() => {
    api.get('/library/books', { params: { page, search } }).then(res => { const d = res.data || res; setBooks(d.items || []); })
      .catch(() => {}).finally(() => setLoading(false));
  }, [page, search]);

  const columns = [
    { key: 'title', label: 'Nomi' },
    { key: 'author', label: 'Muallif' },
    { key: 'isbn', label: 'ISBN' },
    { key: 'total_copies', label: 'Jami' },
    { key: 'available_copies', label: 'Mavjud' },
    { key: 'location', label: 'Joylashuv' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Kitoblar</h1>
        <button onClick={() => setShowAdd(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"><Plus size={18} /> Kitob qo'shish</button>
      </div>
      <SearchBar value={search} onChange={setSearch} placeholder="Kitob qidirish..." />
      <DataTable columns={columns} data={books} loading={loading} emptyMessage="Kitoblar topilmadi" />
      <Pagination page={page} totalPages={5} onPageChange={setPage} />
      <Modal isOpen={showAdd} onClose={() => setShowAdd(false)} title="Yangi kitob" size="md">
        <div className="space-y-4">
          <input placeholder="ISBN" className="w-full border rounded-lg px-3 py-2" />
          <input placeholder="Nomi" className="w-full border rounded-lg px-3 py-2" />
          <input placeholder="Muallif" className="w-full border rounded-lg px-3 py-2" />
          <input type="number" placeholder="Nusxa soni" className="w-full border rounded-lg px-3 py-2" />
          <button className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">Qo'shish</button>
        </div>
      </Modal>
    </div>
  );
}
