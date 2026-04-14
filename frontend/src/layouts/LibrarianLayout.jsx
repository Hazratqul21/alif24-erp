import { Outlet } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  LayoutDashboard,
  BookOpen,
  BookMarked,
  Clock,
  ArrowLeftRight,
  BarChart3,
} from 'lucide-react';
import BaseLayout from './BaseLayout';

export default function LibrarianLayout() {
  const { t } = useTranslation();

  const navItems = [
    { icon: LayoutDashboard, label: t('nav.dashboard', 'Dashboard'), path: '/librarian' },
    { icon: BookOpen, label: t('nav.books', 'Kitoblar'), path: '/librarian/books' },
    { icon: BookMarked, label: t('nav.issued', 'Berilganlar'), path: '/librarian/issued' },
    { icon: Clock, label: t('nav.overdue', "Muddati o'tganlar"), path: '/librarian/overdue' },
    { icon: ArrowLeftRight, label: t('nav.interlibrary', 'Kutubxonalar arasi'), path: '/librarian/interlibrary' },
    { icon: BarChart3, label: t('nav.statistics', 'Statistika'), path: '/librarian/statistics' },
  ];

  return (
    <BaseLayout navItems={navItems}>
      <Outlet />
    </BaseLayout>
  );
}
