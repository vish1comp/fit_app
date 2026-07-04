'use client';

import React, { useEffect } from 'react';
import { Provider, useDispatch, useSelector } from 'react-redux';
import { store, RootState } from '../store';
import { api } from '../lib/api';
import { setUser, setUserStats, clearCredentials, setLoading } from '../store/authSlice';
import { usePathname, useRouter } from 'next/navigation';

function AppInitializer({ children }: { children: React.ReactNode }) {
  const dispatch = useDispatch();
  const router = useRouter();
  const pathname = usePathname();
  const token = useSelector((state: RootState) => state.auth.token);

  useEffect(() => {
    async function loadUser() {
      if (!token) {
        dispatch(setLoading(false));
        // Redirect to login if on private route
        const publicRoutes = ['/', '/login', '/register', '/forgot-password', '/reset-password', '/verify-email'];
        if (!publicRoutes.includes(pathname) && !pathname.startsWith('/auth/callback')) {
          router.push('/login');
        }
        return;
      }

      try {
        dispatch(setLoading(true));
        const userProfile = await api.users.me();
        dispatch(setUser(userProfile));

        const userStats = await api.users.stats();
        dispatch(setUserStats(userStats));
      } catch (err) {
        console.error('Failed to load user session', err);
        dispatch(clearCredentials());
        router.push('/login');
      } finally {
        dispatch(setLoading(false));
      }
    }

    loadUser();
  }, [token, pathname, dispatch, router]);

  return <>{children}</>;
}

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <Provider store={store}>
      <AppInitializer>{children}</AppInitializer>
    </Provider>
  );
}
