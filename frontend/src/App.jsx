import { Routes, Route, Navigate, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import { useTranslation } from 'react-i18next';
import { Loader2 } from 'lucide-react';
import LoginPage from './pages/LoginPage';

// Layouts
import SuperAdminLayout from './layouts/SuperAdminLayout';
import DirectorLayout from './layouts/DirectorLayout';
import TeacherLayout from './layouts/TeacherLayout';
import StudentLayout from './layouts/StudentLayout';
import ParentLayout from './layouts/ParentLayout';
import AccountantLayout from './layouts/AccountantLayout';
import LibrarianLayout from './layouts/LibrarianLayout';
import MedicalLayout from './layouts/MedicalLayout';

// SuperAdmin pages
import SuperAdminDashboard from './pages/superadmin/Dashboard';
import SchoolsPage from './pages/superadmin/SchoolsPage';
import PlansPage from './pages/superadmin/PlansPage';
import MonitoringPage from './pages/superadmin/MonitoringPage';

// Director pages
import DirectorDashboard from './pages/director/Dashboard';
import DirectorStudentsPage from './pages/director/StudentsPage';
import DirectorTeachersPage from './pages/director/TeachersPage';
import DirectorClassesPage from './pages/director/ClassesPage';
import DirectorGradesPage from './pages/director/GradesPage';
import DirectorAttendancePage from './pages/director/AttendancePage';
import DirectorPaymentsPage from './pages/director/PaymentsPage';
import DirectorReportsPage from './pages/director/ReportsPage';
import DirectorStaffPage from './pages/director/StaffPage';

// Teacher pages
import TeacherDashboard from './pages/teacher/Dashboard';
import TeacherAttendancePage from './pages/teacher/AttendancePage';
import TeacherGradesPage from './pages/teacher/GradesPage';
import TeacherHomeworkPage from './pages/teacher/HomeworkPage';
import TeacherMyClassesPage from './pages/teacher/MyClassesPage';

// Student pages
import StudentDashboard from './pages/student/Dashboard';
import StudentGradesPage from './pages/student/GradesPage';
import StudentSchedulePage from './pages/student/SchedulePage';
import StudentHomeworkPage from './pages/student/HomeworkPage';
import StudentLibraryPage from './pages/student/LibraryPage';

// Parent pages
import ParentDashboard from './pages/parent/Dashboard';
import ChildrenPage from './pages/parent/ChildrenPage';
import ParentMessagesPage from './pages/parent/MessagesPage';
import ParentPaymentsPage from './pages/parent/PaymentsPage';

// Accountant pages
import AccountantDashboard from './pages/accountant/Dashboard';
import AccountantPaymentsPage from './pages/accountant/PaymentsPage';
import DebtsPage from './pages/accountant/DebtsPage';
import InvoicesPage from './pages/accountant/InvoicesPage';

// Librarian pages
import LibrarianDashboard from './pages/librarian/Dashboard';
import BooksPage from './pages/librarian/BooksPage';
import LoansPage from './pages/librarian/LoansPage';
import OverduePage from './pages/librarian/OverduePage';
import InterlibraryPage from './pages/librarian/InterlibraryPage';

// Medical pages
import MedicalDashboard from './pages/medical/Dashboard';
import MedicalRecordsPage from './pages/medical/RecordsPage';
import MedicalExamsPage from './pages/medical/ExamsPage';
import QuarantinePage from './pages/medical/QuarantinePage';

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
  const hasToken = typeof window !== 'undefined' && !!localStorage.getItem('access_token');

  if (loading || (hasToken && !user)) {
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
    const userRoles = (user?.roles || [user?.role]).filter(Boolean).map(r => r.toLowerCase());
    const hasRole = allowedRoles.some(r => userRoles.includes(r));
    if (!hasRole) {
      const primaryRole = userRoles[0];
      if (!primaryRole) {
        return <Navigate to="/login" replace />;
      }
      const fallbackRoutes = {
        super_admin: '/superadmin',
        superadmin: '/superadmin',
        deputy_director: '/deputy-director',
        it_admin: '/it-admin',
      };
      return <Navigate to={fallbackRoutes[primaryRole] || `/${primaryRole}`} replace />;
    }
  }

  return <Outlet />;
}

// --- Role-based redirect after login ---
function RoleRedirect() {
  const { user, loading } = useAuth();
  const hasToken = typeof window !== 'undefined' && !!localStorage.getItem('access_token');

  if (loading || (hasToken && !user)) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (!user) return <Navigate to="/login" replace />;

  const roles = (user.roles || [user.role]).filter(Boolean).map(r => r.toLowerCase());
  const role = roles[0];
  const roleRoutes = {
    super_admin: '/superadmin',
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
      <Route element={<ProtectedRoute allowedRoles={['super_admin', 'superadmin']} />}>
        <Route path="/superadmin" element={<SuperAdminLayout />}>
          <Route index element={<SuperAdminDashboard />} />
          <Route path="schools" element={<SchoolsPage />} />
          <Route path="schools/:id" element={<SchoolsPage />} />
          <Route path="plans" element={<PlansPage />} />
          <Route path="monitoring" element={<MonitoringPage />} />
          <Route path="users" element={<PlaceholderPage title="Foydalanuvchilar" />} />
          <Route path="billing" element={<PlaceholderPage title="Hisob-kitob" />} />
          <Route path="settings" element={<PlaceholderPage title="Sozlamalar" />} />
          <Route path="audit" element={<PlaceholderPage title="Audit loglari" />} />
        </Route>
      </Route>

      {/* ========== DIRECTOR ========== */}
      <Route element={<ProtectedRoute allowedRoles={['director']} />}>
        <Route path="/director" element={<DirectorLayout />}>
          <Route index element={<DirectorDashboard />} />
          <Route path="students" element={<DirectorStudentsPage />} />
          <Route path="students/:id" element={<DirectorStudentsPage />} />
          <Route path="teachers" element={<DirectorTeachersPage />} />
          <Route path="teachers/:id" element={<DirectorTeachersPage />} />
          <Route path="classes" element={<DirectorClassesPage />} />
          <Route path="classes/:id" element={<DirectorClassesPage />} />
          <Route path="attendance" element={<DirectorAttendancePage />} />
          <Route path="grades" element={<DirectorGradesPage />} />
          <Route path="hr/staff" element={<DirectorStaffPage />} />
          <Route path="payments" element={<DirectorPaymentsPage />} />
          <Route path="reports" element={<DirectorReportsPage />} />
          <Route path="subjects" element={<PlaceholderPage title="Fanlar" />} />
          <Route path="schedule" element={<PlaceholderPage title="Dars jadvali" />} />
          <Route path="exams" element={<PlaceholderPage title="Imtihonlar" />} />
          <Route path="library" element={<PlaceholderPage title="Kutubxona" />} />
          <Route path="medical" element={<PlaceholderPage title="Tibbiyot" />} />
          <Route path="announcements" element={<PlaceholderPage title="E'lonlar" />} />
          <Route path="messages" element={<PlaceholderPage title="Xabarlar" />} />
          <Route path="settings" element={<PlaceholderPage title="Sozlamalar" />} />
          <Route path="profile" element={<PlaceholderPage title="Profil" />} />
        </Route>
      </Route>

      {/* ========== DEPUTY DIRECTOR ========== */}
      <Route element={<ProtectedRoute allowedRoles={['deputy_director']} />}>
        <Route path="/deputy-director" element={<DirectorLayout />}>
          <Route index element={<DirectorDashboard />} />
          <Route path="students" element={<DirectorStudentsPage />} />
          <Route path="teachers" element={<DirectorTeachersPage />} />
          <Route path="classes" element={<DirectorClassesPage />} />
          <Route path="attendance" element={<DirectorAttendancePage />} />
          <Route path="grades" element={<DirectorGradesPage />} />
          <Route path="reports" element={<DirectorReportsPage />} />
          <Route path="schedule" element={<PlaceholderPage title="Dars jadvali" />} />
          <Route path="exams" element={<PlaceholderPage title="Imtihonlar" />} />
          <Route path="profile" element={<PlaceholderPage title="Profil" />} />
        </Route>
      </Route>

      {/* ========== TEACHER ========== */}
      <Route element={<ProtectedRoute allowedRoles={['teacher']} />}>
        <Route path="/teacher" element={<TeacherLayout />}>
          <Route index element={<TeacherDashboard />} />
          <Route path="my-classes" element={<TeacherMyClassesPage />} />
          <Route path="my-classes/:id" element={<TeacherMyClassesPage />} />
          <Route path="attendance" element={<TeacherAttendancePage />} />
          <Route path="attendance/:classId" element={<TeacherAttendancePage />} />
          <Route path="grades" element={<TeacherGradesPage />} />
          <Route path="grades/:classId" element={<TeacherGradesPage />} />
          <Route path="homework" element={<TeacherHomeworkPage />} />
          <Route path="schedule" element={<PlaceholderPage title="Dars jadvali" />} />
          <Route path="exams" element={<PlaceholderPage title="Imtihonlar" />} />
          <Route path="students" element={<PlaceholderPage title="O'quvchilar" />} />
          <Route path="students/:id" element={<PlaceholderPage title="O'quvchi profili" />} />
          <Route path="messages" element={<PlaceholderPage title="Xabarlar" />} />
          <Route path="profile" element={<PlaceholderPage title="Profil" />} />
        </Route>
      </Route>

      {/* ========== STUDENT ========== */}
      <Route element={<ProtectedRoute allowedRoles={['student']} />}>
        <Route path="/student" element={<StudentLayout />}>
          <Route index element={<StudentDashboard />} />
          <Route path="schedule" element={<StudentSchedulePage />} />
          <Route path="grades" element={<StudentGradesPage />} />
          <Route path="homework" element={<StudentHomeworkPage />} />
          <Route path="library" element={<StudentLibraryPage />} />
          <Route path="attendance" element={<PlaceholderPage title="Davomatim" />} />
          <Route path="exams" element={<PlaceholderPage title="Imtihonlar" />} />
          <Route path="payments" element={<PlaceholderPage title="To'lovlar" />} />
          <Route path="messages" element={<PlaceholderPage title="Xabarlar" />} />
          <Route path="profile" element={<PlaceholderPage title="Profil" />} />
        </Route>
      </Route>

      {/* ========== PARENT ========== */}
      <Route element={<ProtectedRoute allowedRoles={['parent']} />}>
        <Route path="/parent" element={<ParentLayout />}>
          <Route index element={<ParentDashboard />} />
          <Route path="children" element={<ChildrenPage />} />
          <Route path="children/:id" element={<ChildrenPage />} />
          <Route path="payments" element={<ParentPaymentsPage />} />
          <Route path="messages" element={<ParentMessagesPage />} />
          <Route path="profile" element={<PlaceholderPage title="Profil" />} />
        </Route>
      </Route>

      {/* ========== ACCOUNTANT ========== */}
      <Route element={<ProtectedRoute allowedRoles={['accountant']} />}>
        <Route path="/accountant" element={<AccountantLayout />}>
          <Route index element={<AccountantDashboard />} />
          <Route path="payments" element={<AccountantPaymentsPage />} />
          <Route path="students-debt" element={<DebtsPage />} />
          <Route path="invoices" element={<InvoicesPage />} />
          <Route path="salaries" element={<PlaceholderPage title="Oyliklar" />} />
          <Route path="expenses" element={<PlaceholderPage title="Xarajatlar" />} />
          <Route path="reports" element={<PlaceholderPage title="Moliyaviy hisobotlar" />} />
          <Route path="profile" element={<PlaceholderPage title="Profil" />} />
        </Route>
      </Route>

      {/* ========== LIBRARIAN ========== */}
      <Route element={<ProtectedRoute allowedRoles={['librarian']} />}>
        <Route path="/librarian" element={<LibrarianLayout />}>
          <Route index element={<LibrarianDashboard />} />
          <Route path="books" element={<BooksPage />} />
          <Route path="books/:id" element={<BooksPage />} />
          <Route path="loans" element={<LoansPage />} />
          <Route path="overdue" element={<OverduePage />} />
          <Route path="interlibrary" element={<InterlibraryPage />} />
          <Route path="categories" element={<PlaceholderPage title="Kategoriyalar" />} />
          <Route path="reports" element={<PlaceholderPage title="Hisobotlar" />} />
          <Route path="profile" element={<PlaceholderPage title="Profil" />} />
        </Route>
      </Route>

      {/* ========== MEDICAL ========== */}
      <Route element={<ProtectedRoute allowedRoles={['medical']} />}>
        <Route path="/medical" element={<MedicalLayout />}>
          <Route index element={<MedicalDashboard />} />
          <Route path="records" element={<MedicalRecordsPage />} />
          <Route path="checkups" element={<MedicalExamsPage />} />
          <Route path="quarantine" element={<QuarantinePage />} />
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
