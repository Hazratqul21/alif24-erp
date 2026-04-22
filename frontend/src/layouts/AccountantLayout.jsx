import { Outlet } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  LayoutDashboard,
  Wallet,
  FileText,
  AlertTriangle,
  BarChart3,
} from 'lucide-react';
import BaseLayout from './BaseLayout';

export default function AccountantLayout() {
  const { t } = useTranslation();

  const navItems = [
    { icon: LayoutDashboard, label: t('nav.dashboard', 'Dashboard'), path: '/accountant' },
    { icon: Wallet, label: t('nav.payments', "To'lovlar"), path: '/accountant/payments' },
    { icon: FileText, label: t('nav.invoices', 'Hisob-fakturalar'), path: '/accountant/invoices' },
    { icon: AlertTriangle, label: t('nav.debts', 'Qarzlar'), path: '/accountant/students-debt' },
    { icon: BarChart3, label: t('nav.reports', 'Hisobotlar'), path: '/accountant/reports' },
  ];

  return (
    <BaseLayout navItems={navItems}>
      <Outlet />
    </BaseLayout>
  );
}
