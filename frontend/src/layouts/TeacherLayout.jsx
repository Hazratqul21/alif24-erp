import { Outlet } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  LayoutDashboard,
  BookOpen,
  CalendarDays,
  ClipboardCheck,
  Star,
  FileText,
  PenTool,
  MessageSquare,
} from 'lucide-react';
import BaseLayout from './BaseLayout';

export default function TeacherLayout() {
  const { t } = useTranslation();

  const navItems = [
    { icon: LayoutDashboard, label: t('nav.dashboard', 'Dashboard'), path: '/teacher' },
    { icon: BookOpen, label: t('nav.myClasses', 'Mening sinflarim'), path: '/teacher/classes' },
    { icon: CalendarDays, label: t('nav.schedule', 'Dars jadvali'), path: '/teacher/schedule' },
    { icon: ClipboardCheck, label: t('nav.attendance', 'Davomat'), path: '/teacher/attendance' },
    { icon: Star, label: t('nav.grades', 'Baholar'), path: '/teacher/grades' },
    { icon: FileText, label: t('nav.homework', 'Uy vazifasi'), path: '/teacher/homework' },
    { icon: PenTool, label: t('nav.exams', 'Imtihonlar'), path: '/teacher/exams' },
    { icon: MessageSquare, label: t('nav.messages', 'Xabarlar'), path: '/teacher/messages' },
  ];

  return (
    <BaseLayout navItems={navItems}>
      <Outlet />
    </BaseLayout>
  );
}
