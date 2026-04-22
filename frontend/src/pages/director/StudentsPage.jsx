import { useState, useEffect } from 'react';
import { Plus, Download, Search, Link2, Star, BookOpen, Gamepad2, Trophy } from 'lucide-react';
import DataTable from '../../components/common/DataTable';
import SearchBar from '../../components/common/SearchBar';
import Pagination from '../../components/common/Pagination';
import Badge from '../../components/common/Badge';
import Modal from '../../components/common/Modal';
import api from '../../services/api';
import toast from 'react-hot-toast';

export default function StudentsPage() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [classFilter, setClassFilter] = useState('');
  const [classes, setClasses] = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [showAlif24Import, setShowAlif24Import] = useState(false);
  const [showAlif24Results, setShowAlif24Results] = useState(false);
  const [alif24Search, setAlif24Search] = useState('');
  const [alif24Results, setAlif24Results] = useState([]);
  const [alif24Searching, setAlif24Searching] = useState(false);
  const [alif24UserDetail, setAlif24UserDetail] = useState(null);
  const [selectedStudentResults, setSelectedStudentResults] = useState(null);
  const [importClassId, setImportClassId] = useState('');
  const [form, setForm] = useState({ first_name: '', last_name: '', phone: '', class_id: '', email: '' });

  useEffect(() => {
    api.get('/academic/classes').then(res => setClasses((res.data || res).items || [])).catch(() => {});
  }, []);

  const loadStudents = () => {
    setLoading(true);
    api.get('/students', { params: { page, search, class_id: classFilter || undefined } })
      .then(res => { const d = res.data || res; setStudents(d.items || []); setTotalPages(d.total_pages || Math.ceil((d.total || 0) / 20) || 1); })
      .catch(() => setStudents([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadStudents(); }, [page, search, classFilter]);

  const handleCreate = async () => {
    try {
      await api.post('/students', form);
      setShowCreate(false);
      setForm({ first_name: '', last_name: '', phone: '', class_id: '', email: '' });
      loadStudents();
      toast.success("O'quvchi qo'shildi");
    } catch {}
  };

  // ── Alif24 Integration ──

  const handleAlif24Search = async () => {
    if (!alif24Search.trim()) return;
    setAlif24Searching(true);
    try {
      const res = await api.get('/integration/search', { params: { q: alif24Search, role: 'student', limit: 20 } });
      const data = res.data || res;
      setAlif24Results(data.users || []);
      if ((data.users || []).length === 0) {
        toast.error("Alif24 da topilmadi");
      }
    } catch {
      setAlif24Results([]);
    } finally {
      setAlif24Searching(false);
    }
  };

  const handleAlif24Lookup = async (alif24Id) => {
    try {
      const res = await api.get(`/integration/lookup/${alif24Id}`);
      const data = res.data || res;
      if (data.found) {
        setAlif24UserDetail(data.user);
      } else {
        toast.error("Foydalanuvchi topilmadi");
      }
    } catch {}
  };

  const handleAlif24Import = async (alif24Id) => {
    try {
      await api.post('/alif24/import/student', {
        alif24_id: alif24Id,
        class_id: importClassId || null,
      });
      toast.success("O'quvchi Alif24 dan import qilindi!");
      setShowAlif24Import(false);
      setAlif24Results([]);
      setAlif24Search('');
      setAlif24UserDetail(null);
      loadStudents();
    } catch {}
  };

  const handleViewAlif24Results = async (erpUserId) => {
    try {
      const res = await api.get(`/alif24/results/${erpUserId}`);
      setSelectedStudentResults(res.data || res);
      setShowAlif24Results(true);
    } catch {}
  };

  const columns = [
    { key: 'student_code', label: 'ID' },
    { key: 'full_name', label: 'F.I.Sh.', render: (_, r) => `${r.last_name || ''} ${r.first_name || ''}` },
    { key: 'class_name', label: 'Sinf' },
    { key: 'phone', label: 'Telefon' },
    {
      key: 'alif24_user_id',
      label: 'Alif24',
      render: (v, r) => v
        ? (
          <button onClick={() => handleViewAlif24Results(r.id)} className="flex items-center gap-1 text-green-600 hover:text-green-800 text-sm font-medium">
            <Link2 size={14} /> {v}
          </button>
        )
        : <span className="text-gray-400 text-sm">—</span>
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center flex-wrap gap-4">
        <h1 className="text-2xl font-bold">O'quvchilar</h1>
        <div className="flex gap-2">
          <button className="flex items-center gap-2 border px-4 py-2 rounded-lg hover:bg-gray-50">
            <Download size={18} /> Export
          </button>
          <button
            onClick={() => setShowAlif24Import(true)}
            className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
          >
            <Link2 size={18} /> Alif24 dan qo'shish
          </button>
          <button
            onClick={() => setShowCreate(true)}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            <Plus size={18} /> Yangi o'quvchi
          </button>
        </div>
      </div>

      <div className="flex gap-4 flex-wrap">
        <div className="flex-1 min-w-[200px]">
          <SearchBar value={search} onChange={setSearch} placeholder="O'quvchi qidirish..." />
        </div>
        <select value={classFilter} onChange={(e) => setClassFilter(e.target.value)} className="border rounded-lg px-3 py-2">
          <option value="">Barcha sinflar</option>
          {classes.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
      </div>

      <DataTable columns={columns} data={students} loading={loading} emptyMessage="O'quvchilar topilmadi" />
      <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />

      {/* Oddiy yaratish modali */}
      <Modal isOpen={showCreate} onClose={() => setShowCreate(false)} title="Yangi o'quvchi qo'shish" size="md">
        <div className="space-y-4">
          <input placeholder="Ism" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} className="w-full border rounded-lg px-3 py-2" />
          <input placeholder="Familiya" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} className="w-full border rounded-lg px-3 py-2" />
          <input placeholder="Telefon" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} className="w-full border rounded-lg px-3 py-2" />
          <select value={form.class_id} onChange={(e) => setForm({ ...form, class_id: e.target.value })} className="w-full border rounded-lg px-3 py-2">
            <option value="">Sinf tanlang</option>
            {classes.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <button onClick={handleCreate} className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">Qo'shish</button>
        </div>
      </Modal>

      {/* Alif24 dan import qilish modali */}
      <Modal isOpen={showAlif24Import} onClose={() => { setShowAlif24Import(false); setAlif24UserDetail(null); setAlif24Results([]); }} title="Alif24 dan o'quvchi qo'shish" size="lg">
        <div className="space-y-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-sm text-green-800">
            Alif24 platformasidagi o'quvchini ID yoki ismi bilan qidirib, ERP ga import qiling.
            O'quvchining barcha ma'lumotlari avtomatik olib kelinadi.
          </div>

          {/* Qidirish */}
          <div className="flex gap-2">
            <input
              placeholder="Alif24 ID, ism, telefon yoki email..."
              value={alif24Search}
              onChange={(e) => setAlif24Search(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAlif24Search()}
              className="flex-1 border rounded-lg px-3 py-2"
            />
            <button
              onClick={handleAlif24Search}
              disabled={alif24Searching}
              className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              <Search size={18} /> {alif24Searching ? 'Qidirilmoqda...' : 'Qidirish'}
            </button>
          </div>

          {/* Sinf tanlash */}
          <select value={importClassId} onChange={(e) => setImportClassId(e.target.value)} className="w-full border rounded-lg px-3 py-2">
            <option value="">Import qilinganda sinf tanlang (ixtiyoriy)</option>
            {classes.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>

          {/* Qidiruv natijalari */}
          {alif24Results.length > 0 && !alif24UserDetail && (
            <div className="border rounded-lg divide-y max-h-64 overflow-y-auto">
              {alif24Results.map((u) => (
                <div key={u.alif24_id} className="flex items-center justify-between p-3 hover:bg-gray-50">
                  <div>
                    <p className="font-medium">{u.last_name} {u.first_name}</p>
                    <p className="text-sm text-gray-500">ID: {u.alif24_id} | {u.phone || 'telefon yo\'q'} | {u.role}</p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleAlif24Lookup(u.alif24_id)}
                      className="text-blue-600 hover:text-blue-800 text-sm border border-blue-200 px-3 py-1 rounded-lg"
                    >
                      Batafsil
                    </button>
                    <button
                      onClick={() => handleAlif24Import(u.alif24_id)}
                      className="bg-green-600 text-white text-sm px-3 py-1 rounded-lg hover:bg-green-700"
                    >
                      Import
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Batafsil ko'rish */}
          {alif24UserDetail && (
            <div className="border rounded-lg p-4 bg-gray-50 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {alif24UserDetail.avatar && (
                    <img src={alif24UserDetail.avatar} alt="" className="w-12 h-12 rounded-full object-cover" />
                  )}
                  <div>
                    <h3 className="font-bold text-lg">{alif24UserDetail.last_name} {alif24UserDetail.first_name}</h3>
                    <p className="text-sm text-gray-500">Alif24 ID: {alif24UserDetail.alif24_id} | Rol: {alif24UserDetail.role}</p>
                  </div>
                </div>
                <button onClick={() => setAlif24UserDetail(null)} className="text-gray-400 hover:text-gray-600">Orqaga</button>
              </div>

              <div className="grid grid-cols-2 gap-3 text-sm">
                <div><span className="text-gray-500">Telefon:</span> {alif24UserDetail.phone || '—'}</div>
                <div><span className="text-gray-500">Email:</span> {alif24UserDetail.email || '—'}</div>
                <div><span className="text-gray-500">Tug'ilgan kun:</span> {alif24UserDetail.date_of_birth || '—'}</div>
                <div><span className="text-gray-500">Jins:</span> {alif24UserDetail.gender || '—'}</div>
              </div>

              {alif24UserDetail.student_profile && (
                <div className="bg-white rounded-lg p-3 border">
                  <h4 className="font-semibold mb-2 text-sm text-gray-700">Alif24 dagi natijalari</h4>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
                    <div className="flex items-center gap-2">
                      <Star size={16} className="text-yellow-500" />
                      <div>
                        <p className="text-gray-500">Daraja</p>
                        <p className="font-bold">{alif24UserDetail.student_profile.level}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Trophy size={16} className="text-orange-500" />
                      <div>
                        <p className="text-gray-500">Ball</p>
                        <p className="font-bold">{alif24UserDetail.student_profile.total_points}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <BookOpen size={16} className="text-blue-500" />
                      <div>
                        <p className="text-gray-500">Darslar</p>
                        <p className="font-bold">{alif24UserDetail.student_profile.total_lessons_completed}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Gamepad2 size={16} className="text-purple-500" />
                      <div>
                        <p className="text-gray-500">O'yinlar</p>
                        <p className="font-bold">{alif24UserDetail.student_profile.total_games_played}</p>
                      </div>
                    </div>
                  </div>
                  <div className="mt-2 text-sm text-gray-500">
                    O'rtacha ball: <span className="font-bold text-gray-800">{alif24UserDetail.student_profile.average_score}%</span>
                    {' | '}Streak: <span className="font-bold text-gray-800">{alif24UserDetail.student_profile.current_streak} kun</span>
                  </div>
                </div>
              )}

              <button
                onClick={() => handleAlif24Import(alif24UserDetail.alif24_id)}
                className="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 font-medium"
              >
                ERP ga import qilish
              </button>
            </div>
          )}
        </div>
      </Modal>

      {/* Alif24 natijalarini ko'rish modali */}
      <Modal isOpen={showAlif24Results} onClose={() => { setShowAlif24Results(false); setSelectedStudentResults(null); }} title="Alif24 natijalari" size="md">
        {selectedStudentResults && (
          <div className="space-y-4">
            {selectedStudentResults.results ? (
              <>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800">
                  Alif24 ID: <span className="font-bold">{selectedStudentResults.alif24_id}</span> — bu ma'lumotlar Alif24 platformasidan real vaqtda olingan.
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-center">
                    <Star className="mx-auto text-yellow-500 mb-1" size={24} />
                    <p className="text-xs text-gray-500">Daraja</p>
                    <p className="text-2xl font-bold">{selectedStudentResults.results.level}</p>
                  </div>
                  <div className="bg-orange-50 border border-orange-200 rounded-lg p-3 text-center">
                    <Trophy className="mx-auto text-orange-500 mb-1" size={24} />
                    <p className="text-xs text-gray-500">Umumiy ball</p>
                    <p className="text-2xl font-bold">{selectedStudentResults.results.total_points}</p>
                  </div>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-center">
                    <BookOpen className="mx-auto text-blue-500 mb-1" size={24} />
                    <p className="text-xs text-gray-500">Tugatilgan darslar</p>
                    <p className="text-2xl font-bold">{selectedStudentResults.results.total_lessons_completed}</p>
                  </div>
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-3 text-center">
                    <Gamepad2 className="mx-auto text-purple-500 mb-1" size={24} />
                    <p className="text-xs text-gray-500">O'ynalgan o'yinlar</p>
                    <p className="text-2xl font-bold">{selectedStudentResults.results.total_games_played}</p>
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3 text-sm space-y-1">
                  <p>O'rtacha ball: <span className="font-bold">{selectedStudentResults.results.average_score}%</span></p>
                  <p>Joriy streak: <span className="font-bold">{selectedStudentResults.results.current_streak} kun</span></p>
                  <p>Eng uzun streak: <span className="font-bold">{selectedStudentResults.results.longest_streak} kun</span></p>
                  <p>Umumiy vaqt: <span className="font-bold">{Math.round((selectedStudentResults.results.total_time_spent_minutes || 0) / 60)} soat</span></p>
                  <p>Tangalar: <span className="font-bold">{selectedStudentResults.results.total_coins}</span></p>
                </div>
              </>
            ) : (
              <div className="text-center text-gray-500 py-8">
                <p>{selectedStudentResults.message || "Ma'lumot topilmadi"}</p>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}
