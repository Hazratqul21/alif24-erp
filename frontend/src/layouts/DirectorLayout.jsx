import { Outlet } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  LayoutDashboard,
  Users,
  GraduationCap,
  UserCheck,
  BookOpen,
  ClipboardCheck,
  Star,
  Wallet,
  Library,
  BarChart3,
  Settings,
} from 'lucide-react';
import BaseLayout from './BaseLayout';

export default function DirectorLayout() {
  const { t } = useTranslation();

  const navItems = [
    { icon: LayoutDashboard, label: t('nav.dashboard', 'Dashboard'), path: '/director' },
    { icon: Users, label: t('nav.staff', 'Xodimlar'), path: '/director/hr/staff' },
    { icon: GraduationCap, label: t('nav.classes', 'Sinflar'), path: '/director/classes' },
    { icon: UserCheck, label: t('nav.students', "O'quvchilar"), path: '/director/students' },
    { icon: BookOpen, label: t('nav.teachers', "O'qituvchilar"), path: '/director/teachers' },
    { icon: ClipboardCheck, label: t('nav.attendance', 'Davomat'), path: '/director/attendance' },
    { icon: Star, label: t('nav.grades', 'Baholar'), path: '/director/grades' },
    { icon: Wallet, label: t('nav.payments', "To'lovlar"), path: '/director/payments' },
    { icon: Library, label: t('nav.library', 'Kutubxona'), path: '/director/library' },
    { icon: BarChart3, label: t('nav.reports', 'Hisobotlar'), path: '/director/reports' },
    { icon: Settings, label: t('nav.settings', 'Sozlamalar'), path: '/director/settings' },
  ];

  return (
    <BaseLayout navItems={navItems}>
      <Outlet />
    </BaseLayout>
  );
}
