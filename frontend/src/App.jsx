import { Routes, Route, Navigate, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import { useTranslation } from 'react-i18next';
import { Loader2 } from 'lucide-react';
import LoginPage from './pages/LoginPage';

// Placeholder layout/page components — replace with real ones as you build them
function PlaceholderPage({ title }) {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="text-center animate-fade-in">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">{title}</h1>
        <p className="text-gray-500">Bu sahifa tez orada tayyor bo'ladi</p>
      </div>
    </div>
  );
}

function DashboardPlaceholder({ role }) {
  const { t } = useTranslation();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-primary-700">Alif24 ERP</h1>
          <p className="text-sm text-gray-500">{t(role)} {t('dashboard')}</p>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">
            {user?.full_name || user?.email || role}
          </span>
          <button
            onClick={handleLogout}
            className="px-4 py-2 text-sm bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors"
          >
            {t('logout')}
          </button>
        </div>
      </header>
      <main className="p-6">
        <Outlet />
      </main>
    </div>
  );
}

// --- Protected Route Wrapper ---
function ProtectedRoute({ allowedRoles }) {
  const { user, loading, isAuthenticated } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && allowedRoles.length > 0) {
    const userRole = user?.role?.toLowerCase();
    if (!allowedRoles.includes(userRole)) {
      return <Navigate to={`/${userRole}`} replace />;
    }
  }

  return <Outlet />;
}

// --- Role-based redirect after login ---
function RoleRedirect() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (!user) return <Navigate to="/login" replace />;

  const role = user.role?.toLowerCase();
  const roleRoutes = {
    superadmin: '/superadmin',
    director: '/director',
    deputy_director: '/deputy-director',
    teacher: '/teacher',
    student: '/student',
    parent: '/parent',
    accountant: '/accountant',
    librarian: '/librarian',
    medical: '/medical',
    hr: '/hr',
    receptionist: '/receptionist',
    security: '/security',
    it_admin: '/it-admin',
    psychologist: '/psychologist',
  };

  return <Navigate to={roleRoutes[role] || '/login'} replace />;
}

// --- Main App ---
export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/login" element={<LoginPage />} />

      {/* Root redirect */}
      <Route path="/" element={<RoleRedirect />} />

      {/* ========== SUPERADMIN ========== */}
      <Route element={<ProtectedRoute allowedRoles={['superadmin']} />}>
        <Route path="/superadmin" element={<DashboardPlaceholder role="superadmin" />}>
          <Route index element={<PlaceholderPage title="Super Admin Dashboard" />} />
          <Route path="schools" element={<PlaceholderPage title="Maktablar" />} />
          <Route path="schools/:id" element={<PlaceholderPage title="Maktab tafsilotlari" />} />
          <Route path="users" element={<PlaceholderPage title="Foydalanuvchilar" />} />
          <Route path="plans" element={<PlaceholderPage title="Tariflar" />} />
          <Route path="billing" element={<PlaceholderPage title="Hisob-kitob" />} />
          <Route path="analytics" element={<PlaceholderPage title="Analitika" />} />
          <Route path="settings" element={<PlaceholderPage title="Sozlamalar" />} />
          <Route path="logs" element={<PlaceholderPage title="Tizim loglari" />} />
        </Route>
      </Route>

      {/* ========== DIRECTOR ========== */}
      <Route element={<ProtectedRoute allowedRoles={['director']} />}>
        <Route path="/director" element={<DashboardPlaceholder role="director" />}>
          <Route index element={<PlaceholderPage title="Direktor Dashboard" />} />
          <Route path="students" element={<PlaceholderPage title="O'quvchilar" />} />
          <Route path="students/:id" element={<PlaceholderPage title="O'quvchi profili" />} />
          <Route path="teachers" element={<PlaceholderPage title="O'qituvchilar" />} />
          <Route path="teachers/:id" element={<PlaceholderPage title="O'qituvchi profili" />} />
          <Route path="classes" element={<PlaceholderPage title="Sinflar" />} />
          <Route path="classes/:id" element={<PlaceholderPage title="Sinf tafsilotlari" />} />
          <Route path="subjects" element={<PlaceholderPage title="Fanlar" />} />
          <Route path="schedule" element={<PlaceholderPage title="Dars jadvali" />} />
          <Route path="attendance" element={<PlaceholderPage title="Davomat" />} />
          <Route path="grades" element={<PlaceholderPage title="Baholar" />} />
          <Route path="exams" element={<PlaceholderPage title="Imtihonlar" />} />
          <Route path="finance" element={<PlaceholderPage title="Moliya" />} />
          <Route path="finance/payments" element={<PlaceholderPage title="To'lovlar" />} />
          <Route path="finance/salaries" element={<PlaceholderPage title="Oyliklar" />} />
          <Route path="finance/expenses" element={<PlaceholderPage title="Xarajatlar" />} />
          <Route path="hr" element={<PlaceholderPage title="Kadrlar" />} />
          <Route path="hr/staff" element={<PlaceholderPage title="Xodimlar" />} />
          <Route path="library" element={<PlaceholderPage title="Kutubxona" />} />
          <Route path="medical" element={<PlaceholderPage title="Tibbiyot" />} />
          <Route path="reports" element={<PlaceholderPage title="Hisobotlar" />} />
          <Route path="announcements" element={<PlaceholderPage title="E'lonlar" />} />
          <Route path="messages" element={<PlaceholderPage title="Xabarlar" />} />
          <Route path="settings" element={<PlaceholderPage title="Sozlamalar" />} />
          <Route path="profile" element={<PlaceholderPage title="Profil" />} />
        </Route>
      </Route>

      {/* ========== DEPUTY DIRECTOR ========== */}
      <Route element={<ProtectedRoute allowedRoles={['deputy_director']} />}>
        <Route path="/deputy-director" element={<DashboardPlaceholder role="director" />}>
          <Route index element={<PlaceholderPage title="O'rinbosar Dashboard" />} />
          <Route path="students" element={<PlaceholderPage title="O'quvchilar" />} />
          <Route path="teachers" element={<PlaceholderPage title="O'qituvchilar" />} />
          <Route path="classes" element={<PlaceholderPage title="Sinflar" />} />
          <Route path="schedule" element={<PlaceholderPage title="Dars jadvali" />} />
          <Route path="attendance" element={<PlaceholderPage title="Davomat" />} />
          <Route path="grades" element={<PlaceholderPage title="Baholar" />} />
          <Route path="exams" element={<PlaceholderPage title="Imtihonlar" />} />
          <Route path="reports" element={<PlaceholderPage title="Hisobotlar" />} />
          <Route path="profile" element={<PlaceholderPage title="Profil" />} />
        </Route>
      </Route>

      {/* ========== TEACHER ========== */}
      <Route element={<ProtectedRoute allowedRoles={['teacher']} />}>
        <Route path="/teacher" element={<DashboardPlaceholder role="teacher" />}>
          <Route index element={<PlaceholderPage title="O'qituvchi Dashboard" />} />
          <Route path="my-classes" element={<PlaceholderPage title="Mening sinflarim" />} />
          <Route path="my-classes/:id" element={<PlaceholderPage title="Sinf" />} />
          <Route path="schedule" element={<PlaceholderPage title="Dars jadvali" />} />
          <Route path="attendance" element={<PlaceholderPage title="Davomat" />} />
          <Route path="attendance/:classId" element={<PlaceholderPage title="Sinf davomati" />} />
          <Route path="grades" element={<PlaceholderPage title="Baholar" />} />
          <Route path="grades/:classId" element={<PlaceholderPage title="Sinf baholari" />} />
          <Route path="exams" element={<PlaceholderPage title="Imtihonlar" />} />
          <Route path="homework" element={<PlaceholderPage title="Uy vazifalari" />} />
          <Route path="students" element={<PlaceholderPage title="O'quvchilar" />} />
          <Route path="students/:id" element={<PlaceholderPage title="O'quvchi profili" />} />
          <Route path="messages" element={<PlaceholderPage title="Xabarlar" />} />
          <Route path="profile" element={<PlaceholderPage title="Profil" />} />
        </Route>
      </Route>

      {/* ========== STUDENT ========== */}
      <Route element={<ProtectedRoute allowedRoles={['student']} />}>
        <Route path="/student" element={<DashboardPlaceholder role="student" />}>
          <Route index element={<PlaceholderPage title="O'quvchi Dashboard" />} />
          <Route path="schedule" element={<PlaceholderPage title="Dars jadvali" />} />
          <Route path="grades" element={<PlaceholderPage title="Baholarim" />} />
          <Route path="attendance" element={<PlaceholderPage title="Davomatim" />} />
          <Route path="homework" element={<PlaceholderPage title="Uy vazifalari" />} />
          <Route path="exams" element={<PlaceholderPage title="Imtihonlar" />} />
          <Route path="library" element={<PlaceholderPage title="Kutubxona" />} />
          <Route path="payments" element={<PlaceholderPage title="To'lovlar" />} />
          <Route path="messages" element={<PlaceholderPage title="Xabarlar" />} />
          <Route path="profile" element={<PlaceholderPage title="Profil" />} />
        </Route>
      </Route>

      {/* ========== PARENT ========== */}
      <Route element={<ProtectedRoute allowedRoles={['parent']} />}>
        <Route path="/parent" element={<DashboardPlaceholder role="parent" />}>
          <Route index element={<PlaceholderPage title="Ota-ona Dashboard" />} />
          <Route path="children" element={<PlaceholderPage title="Farzandlarim" />} />
          <Route path="children/:id" element={<PlaceholderPage title="Farzand profili" />} />
          <Route path="children/:id/grades" element={<PlaceholderPage title="Baholar" />} />
          <Route path="children/:id/attendance" element={<PlaceholderPage title="Davomat" />} />
          <Route path="children/:id/homework" element={<PlaceholderPage title="Uy vazifalari" />} />
          <Route path="payments" element={<PlaceholderPage title="To'lovlar" />} />
          <Route path="messages" element={<PlaceholderPage title="Xabarlar" />} />
          <Route path="profile" element={<PlaceholderPage title="Profil" />} />
        </Route>
      </Route>

      {/* ========== ACCOUNTANT ========== */}
      <Route element={<ProtectedRoute allowedRoles={['accountant']} />}>
        <Route path="/accountant" element={<DashboardPlaceholder role="accountant" />}>
          <Route index element={<PlaceholderPage title="Hisobchi Dashboard" />} />
          <Route path="payments" element={<PlaceholderPage title="To'lovlar" />} />
          <Route path="payments/:id" element={<PlaceholderPage title="To'lov tafsilotlari" />} />
          <Route path="salaries" element={<PlaceholderPage title="Oyliklar" />} />
          <Route path="expenses" element={<PlaceholderPage title="Xarajatlar" />} />
          <Route path="invoices" element={<PlaceholderPage title="Hisob-fakturalar" />} />
          <Route path="reports" element={<PlaceholderPage title="Moliyaviy hisobotlar" />} />
          <Route path="students-debt" element={<PlaceholderPage title="Qarzdorlar" />} />
          <Route path="profile" element={<PlaceholderPage title="Profil" />} />
        </Route>
      </Route>

      {/* ========== LIBRARIAN ========== */}
      <Route element={<ProtectedRoute allowedRoles={['librarian']} />}>
        <Route path="/librarian" element={<DashboardPlaceholder role="librarian" />}>
          <Route index element={<PlaceholderPage title="Kutubxonachi Dashboard" />} />
          <Route path="books" element={<PlaceholderPage title="Kitoblar" />} />
          <Route path="books/:id" element={<PlaceholderPage title="Kitob tafsilotlari" />} />
          <Route path="issued" element={<PlaceholderPage title="Berilgan kitoblar" />} />
          <Route path="returns" element={<PlaceholderPage title="Qaytarilgan kitoblar" />} />
          <Route path="overdue" element={<PlaceholderPage title="Muddati o'tgan" />} />
          <Route path="categories" element={<PlaceholderPage title="Kategoriyalar" />} />
          <Route path="reports" element={<PlaceholderPage title="Hisobotlar" />} />
          <Route path="profile" element={<PlaceholderPage title="Profil" />} />
        </Route>
      </Route>

      {/* ========== MEDICAL ========== */}
      <Route element={<ProtectedRoute allowedRoles={['medical']} />}>
        <Route path="/medical" element={<DashboardPlaceholder role="medical_staff" />}>
          <Route index element={<PlaceholderPage title="Tibbiyot Dashboard" />} />
          <Route path="records" element={<PlaceholderPage title="Tibbiy yozuvlar" />} />
          <Route path="records/:id" element={<PlaceholderPage title="Tibbiy yozuv" />} />
          <Route path="checkups" element={<PlaceholderPage title="Tibbiy ko'riklar" />} />
          <Route path="incidents" element={<PlaceholderPage title="Hodisalar" />} />
          <Route path="vaccinations" element={<PlaceholderPage title="Emlashlar" />} />
          <Route path="reports" element={<PlaceholderPage title="Hisobotlar" />} />
          <Route path="profile" element={<PlaceholderPage title="Profil" />} />
        </Route>
      </Route>

      {/* ========== HR ========== */}
      <Route element={<ProtectedRoute allowedRoles={['hr']} />}>
        <Route path="/hr" element={<DashboardPlaceholder role="hr" />}>
          <Route index element={<PlaceholderPage title="Kadrlar Dashboard" />} />
          <Route path="staff" element={<PlaceholderPage title="Xodimlar" />} />
          <Route path="staff/:id" element={<PlaceholderPage title="Xodim profili" />} />
          <Route path="positions" element={<PlaceholderPage title="Lavozimlar" />} />
          <Route path="departments" element={<PlaceholderPage title="Bo'limlar" />} />
          <Route path="leaves" element={<PlaceholderPage title="Ta'tillar" />} />
          <Route path="contracts" element={<PlaceholderPage title="Shartnomalar" />} />
          <Route path="attendance" element={<PlaceholderPage title="Davomat" />} />
          <Route path="reports" element={<PlaceholderPage title="Hisobotlar" />} />
          <Route path="profile" element={<PlaceholderPage title="Profil" />} />
        </Route>
      </Route>

      {/* ========== RECEPTIONIST ========== */}
      <Route element={<ProtectedRoute allowedRoles={['receptionist']} />}>
        <Route path="/receptionist" element={<DashboardPlaceholder role="receptionist" />}>
          <Route index element={<PlaceholderPage title="Qabulxona Dashboard" />} />
          <Route path="visitors" element={<PlaceholderPage title="Tashrif buyuruvchilar" />} />
          <Route path="admissions" element={<PlaceholderPage title="Qabul" />} />
          <Route path="inquiries" element={<PlaceholderPage title="So'rovlar" />} />
          <Route path="announcements" element={<PlaceholderPage title="E'lonlar" />} />
          <Route path="profile" element={<PlaceholderPage title="Profil" />} />
        </Route>
      </Route>

      {/* ========== SECURITY ========== */}
      <Route element={<ProtectedRoute allowedRoles={['security']} />}>
        <Route path="/security" element={<DashboardPlaceholder role="security" />}>
          <Route index element={<PlaceholderPage title="Qo'riqchi Dashboard" />} />
          <Route path="gate-log" element={<PlaceholderPage title="Kirish-chiqish" />} />
          <Route path="visitors" element={<PlaceholderPage title="Tashrif buyuruvchilar" />} />
          <Route path="incidents" element={<PlaceholderPage title="Hodisalar" />} />
          <Route path="profile" element={<PlaceholderPage title="Profil" />} />
        </Route>
      </Route>

      {/* ========== IT ADMIN ========== */}
      <Route element={<ProtectedRoute allowedRoles={['it_admin']} />}>
        <Route path="/it-admin" element={<DashboardPlaceholder role="it_admin" />}>
          <Route index element={<PlaceholderPage title="IT Admin Dashboard" />} />
          <Route path="users" element={<PlaceholderPage title="Foydalanuvchilar" />} />
          <Route path="roles" element={<PlaceholderPage title="Rollar va ruxsatlar" />} />
          <Route path="system" element={<PlaceholderPage title="Tizim holati" />} />
          <Route path="logs" element={<PlaceholderPage title="Loglar" />} />
          <Route path="backup" element={<PlaceholderPage title="Zaxira nusxa" />} />
          <Route path="settings" element={<PlaceholderPage title="Sozlamalar" />} />
          <Route path="profile" element={<PlaceholderPage title="Profil" />} />
        </Route>
      </Route>

      {/* ========== PSYCHOLOGIST ========== */}
      <Route element={<ProtectedRoute allowedRoles={['psychologist']} />}>
        <Route path="/psychologist" element={<DashboardPlaceholder role="psychologist" />}>
          <Route index element={<PlaceholderPage title="Psixolog Dashboard" />} />
          <Route path="students" element={<PlaceholderPage title="O'quvchilar" />} />
          <Route path="students/:id" element={<PlaceholderPage title="O'quvchi profili" />} />
          <Route path="sessions" element={<PlaceholderPage title="Seanslar" />} />
          <Route path="sessions/:id" element={<PlaceholderPage title="Seans tafsilotlari" />} />
          <Route path="assessments" element={<PlaceholderPage title="Baholashlar" />} />
          <Route path="reports" element={<PlaceholderPage title="Hisobotlar" />} />
          <Route path="profile" element={<PlaceholderPage title="Profil" />} />
        </Route>
      </Route>

      {/* Catch all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
