import axios from 'axios';
import toast from 'react-hot-toast';

const api = axios.create({
  baseURL: '/api/v1',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      'Xatolik yuz berdi';

    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    } else if (error.response?.status === 403) {
      toast.error('Sizda bu amal uchun ruxsat yo\'q');
    } else if (error.response?.status === 404) {
      toast.error('Ma\'lumot topilmadi');
    } else if (error.response?.status >= 500) {
      toast.error('Server xatosi. Iltimos qayta urinib ko\'ring');
    } else if (error.response?.status === 422) {
      const details = error.response?.data?.detail;
      if (Array.isArray(details)) {
        details.forEach((d) => toast.error(d.msg || d.message || String(d)));
      } else {
        toast.error(message);
      }
    } else {
      toast.error(message);
    }

    return Promise.reject(error);
  }
);

export default api;
