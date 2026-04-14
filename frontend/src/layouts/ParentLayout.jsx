import { Outlet } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  LayoutDashboard,
  Users,
  Star,
  ClipboardCheck,
  Wallet,
  MessageSquare,
} from 'lucide-react';
import BaseLayout from './BaseLayout';

export default function ParentLayout() {
  const { t } = useTranslation();

  const navItems = [
    { icon: LayoutDashboard, label: t('nav.dashboard', 'Dashboard'), path: '/parent' },
    { icon: Users, label: t('nav.children', 'Farzandlarim'), path: '/parent/children' },
    { icon: Star, label: t('nav.grades', 'Baholar'), path: '/parent/grades' },
    { icon: ClipboardCheck, label: t('nav.attendance', 'Davomat'), path: '/parent/attendance' },
    { icon: Wallet, label: t('nav.payments', "To'lovlar"), path: '/parent/payments' },
    { icon: MessageSquare, label: t('nav.messages', 'Xabarlar'), path: '/parent/messages' },
  ];

  return (
    <BaseLayout navItems={navItems}>
      <Outlet />
    </BaseLayout>
  );
}
