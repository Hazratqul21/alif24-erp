import { Outlet } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  LayoutDashboard,
  FileHeart,
  Stethoscope,
  ShieldAlert,
} from 'lucide-react';
import BaseLayout from './BaseLayout';

export default function MedicalLayout() {
  const { t } = useTranslation();

  const navItems = [
    { icon: LayoutDashboard, label: t('nav.dashboard', 'Dashboard'), path: '/medical' },
    { icon: FileHeart, label: t('nav.medicalRecords', 'Tibbiy kartalar'), path: '/medical/records' },
    { icon: Stethoscope, label: t('nav.examinations', "Ko'riklar"), path: '/medical/examinations' },
    { icon: ShieldAlert, label: t('nav.quarantine', 'Karantin'), path: '/medical/quarantine' },
  ];

  return (
    <BaseLayout navItems={navItems}>
      <Outlet />
    </BaseLayout>
  );
}
