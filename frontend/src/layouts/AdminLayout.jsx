import { Outlet } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  LayoutDashboard,
  Users,
  Shield,
  GraduationCap,
  BookOpen,
  CalendarRange,
  DoorOpen,
  PartyPopper,
  FileSearch,
} from 'lucide-react';
import BaseLayout from './BaseLayout';

export default function AdminLayout() {
  const { t } = useTranslation();

  const navItems = [
    { icon: LayoutDashboard, label: t('nav.dashboard', 'Dashboard'), path: '/admin' },
    { icon: Users, label: t('nav.users', 'Foydalanuvchilar'), path: '/admin/users' },
    { icon: Shield, label: t('nav.roles', 'Rollar'), path: '/admin/roles' },
    { icon: GraduationCap, label: t('nav.classes', 'Sinflar'), path: '/admin/classes' },
    { icon: BookOpen, label: t('nav.subjects', 'Fanlar'), path: '/admin/subjects' },
    { icon: CalendarRange, label: t('nav.academicYears', "O'quv yillari"), path: '/admin/academic-years' },
    { icon: DoorOpen, label: t('nav.rooms', 'Xonalar'), path: '/admin/rooms' },
    { icon: PartyPopper, label: t('nav.holidays', 'Bayramlar'), path: '/admin/holidays' },
    { icon: FileSearch, label: t('nav.audit', 'Audit'), path: '/admin/audit' },
  ];

  return (
    <BaseLayout navItems={navItems}>
      <Outlet />
    </BaseLayout>
  );
}
