import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTenant } from '../contexts/TenantContext';
import { useTranslation } from 'react-i18next';
import { Eye, EyeOff, Loader2, GraduationCap } from 'lucide-react';
import toast from 'react-hot-toast';

export default function LoginPage() {
  const { t, i18n } = useTranslation();
  const { login } = useAuth();
  const { tenant } = useTenant();
  const navigate = useNavigate();

  const [emailOrPhone, setEmailOrPhone] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!emailOrPhone || !password) return;

    setLoading(true);
    try {
      const user = await login(emailOrPhone, password);
      toast.success(t('login_success'));
      const role = user.role?.toLowerCase();
      const roleRoutes = {
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
      navigate(roleRoutes[role] || '/');
    } catch {
      toast.error(t('login_error'));
    } finally {
      setLoading(false);
    }
  };

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
    localStorage.setItem('lang', lng);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-blue-50 px-4">
      <div className="w-full max-w-md animate-scale-in">
        {/* Language switcher */}
        <div className="flex justify-end mb-4 gap-1">
          {['uz', 'ru', 'en'].map((lng) => (
            <button
              key={lng}
              onClick={() => changeLanguage(lng)}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                i18n.language === lng
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
              }`}
            >
              {lng.toUpperCase()}
            </button>
          ))}
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-xl shadow-gray-200/50 p-8 border border-gray-100">
          {/* Logo */}
          <div className="text-center mb-8">
            {tenant?.logo ? (
              <img src={tenant.logo} alt={tenant.name} className="h-16 mx-auto mb-3" />
            ) : (
              <div className="w-16 h-16 bg-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-3">
                <GraduationCap className="w-8 h-8 text-white" />
              </div>
            )}
            <h1 className="text-2xl font-bold text-gray-900">
              {tenant?.name || 'Alif24 School ERP'}
            </h1>
            <p className="text-sm text-gray-500 mt-1">{t('welcome_back')}</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="login" className="block text-sm font-medium text-gray-700 mb-1.5">
                {t('email_or_phone')}
              </label>
              <input
                id="login"
                type="text"
                value={emailOrPhone}
                onChange={(e) => setEmailOrPhone(e.target.value)}
                placeholder="+998 90 123 45 67"
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 outline-none transition-all text-sm"
                autoComplete="username"
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1.5">
                {t('password')}
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 outline-none transition-all text-sm pr-12"
                  autoComplete="current-password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
                <span className="text-sm text-gray-600">{t('remember_me')}</span>
              </label>
              <a href="#" className="text-sm text-primary-600 hover:text-primary-700 font-medium">
                {t('forgot_password')}
              </a>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 focus:ring-4 focus:ring-primary-500/20 transition-all disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading && <Loader2 className="w-4 h-4 animate-spin" />}
              {t('login')}
            </button>
          </form>
        </div>

        {/* Footer */}
        <p className="text-center text-xs text-gray-400 mt-6">
          &copy; {new Date().getFullYear()} Alif24 School ERP
        </p>
      </div>
    </div>
  );
}
