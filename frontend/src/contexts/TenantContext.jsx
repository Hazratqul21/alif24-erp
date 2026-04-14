import { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const TenantContext = createContext(null);

function extractSubdomain() {
  const hostname = window.location.hostname;
  const parts = hostname.split('.');

  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return null;
  }

  // e.g. school1.alif24.uz -> school1
  if (parts.length >= 3) {
    const sub = parts[0];
    if (sub === 'www' || sub === 'app' || sub === 'admin') {
      return null;
    }
    return sub;
  }

  return null;
}

export function TenantProvider({ children }) {
  const [tenant, setTenant] = useState(null);
  const [loading, setLoading] = useState(true);

  const subdomain = extractSubdomain();
  const isSuperAdmin = !subdomain;

  useEffect(() => {
    async function loadTenant() {
      if (!subdomain) {
        setLoading(false);
        return;
      }

      try {
        const { data } = await api.get(`/tenants/by-subdomain/${subdomain}`);
        setTenant(data);
      } catch {
        setTenant(null);
      } finally {
        setLoading(false);
      }
    }

    loadTenant();
  }, [subdomain]);

  const value = {
    tenant,
    subdomain,
    isSuperAdmin,
    loading,
    setTenant,
  };

  return <TenantContext.Provider value={value}>{children}</TenantContext.Provider>;
}

export function useTenant() {
  const context = useContext(TenantContext);
  if (!context) {
    throw new Error('useTenant must be used within a TenantProvider');
  }
  return context;
}

export default TenantContext;
