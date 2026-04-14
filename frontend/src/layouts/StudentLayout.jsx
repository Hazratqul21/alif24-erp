import { Outlet } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  LayoutDashboard,
  CalendarDays,
  Star,
  FileText,
  Library,
  FolderOpen,
  MessageSquare,
} from 'lucide-react';
import BaseLayout from './BaseLayout';

export default function StudentLayout() {
  const { t } = useTranslation();

  const navItems = [
    { icon: LayoutDashboard, label: t('nav.dashboard', 'Dashboard'), path: '/student' },
    { icon: CalendarDays, label: t('nav.schedule', 'Dars jadvali'), path: '/student/schedule' },
    { icon: Star, label: t('nav.myGrades', 'Baholarim'), path: '/student/grades' },
    { icon: FileText, label: t('nav.homework', 'Uy vazifasi'), path: '/student/homework' },
    { icon: Library, label: t('nav.library', 'Kutubxona'), path: '/student/library' },
    { icon: FolderOpen, label: t('nav.portfolio', 'Portfolio'), path: '/student/portfolio' },
    { icon: MessageSquare, label: t('nav.messages', 'Xabarlar'), path: '/student/messages' },
  ];

  return (
    <BaseLayout navItems={navItems}>
      <Outlet />
    </BaseLayout>
  );
}
