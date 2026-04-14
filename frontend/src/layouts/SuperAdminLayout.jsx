import { Outlet } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  LayoutDashboard,
  School,
  CreditCard,
  Activity,
  FileSearch,
  Settings,
} from 'lucide-react';
import BaseLayout from './BaseLayout';

export default function SuperAdminLayout() {
  const { t } = useTranslation();

  const navItems = [
    { icon: LayoutDashboard, label: t('nav.dashboard', 'Dashboard'), path: '/superadmin' },
    { icon: School, label: t('nav.schools', 'Maktablar'), path: '/superadmin/schools' },
    { icon: CreditCard, label: t('nav.plans', 'Tariflar'), path: '/superadmin/plans' },
    { icon: Activity, label: t('nav.monitoring', 'Monitoring'), path: '/superadmin/monitoring' },
    { icon: FileSearch, label: t('nav.audit', 'Audit'), path: '/superadmin/audit' },
    { icon: Settings, label: t('nav.settings', 'Sozlamalar'), path: '/superadmin/settings' },
  ];

  return (
    <BaseLayout navItems={navItems}>
      <Outlet />
    </BaseLayout>
  );
}
