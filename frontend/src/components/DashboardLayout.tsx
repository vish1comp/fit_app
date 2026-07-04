'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../store';
import { clearCredentials } from '../store/authSlice';
import { 
  Activity, 
  LayoutDashboard, 
  Apple, 
  Dumbbell, 
  MessageSquare, 
  BookOpen, 
  User, 
  ShieldAlert, 
  LogOut,
  Sparkles
} from 'lucide-react';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const dispatch = useDispatch();
  const { user, stats, isLoading } = useSelector((state: RootState) => state.auth);

  const handleLogout = () => {
    dispatch(clearCredentials());
    router.push('/login');
  };

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Nutrition Logs', path: '/nutrition', icon: Apple },
    { name: 'Workouts', path: '/workouts', icon: Dumbbell },
    { name: 'AI Coach', path: '/coach', icon: MessageSquare },
    { name: 'Supplements', path: '/supplements', icon: BookOpen },
    { name: 'My Profile', path: '/profile', icon: User },
  ];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#030712] flex flex-col items-center justify-center gap-4">
        <div className="h-12 w-12 rounded-xl bg-indigo-500/20 border border-indigo-500 flex items-center justify-center animate-pulse">
          <Activity className="h-6 w-6 text-indigo-400 animate-spin" />
        </div>
        <span className="text-sm font-semibold text-slate-400">Restoring session...</span>
      </div>
    );
  }

  if (!user) {
    return null; // Initializer in Providers will handle routing to /login
  }

  const userPlan = user.is_admin ? 'admin' : (user as any).plan_type || 'free';

  return (
    <div className="min-h-screen bg-[#030712] flex">
      {/* Sidebar */}
      <aside className="w-64 border-r border-white/5 bg-slate-950/80 backdrop-blur-xl hidden md:flex flex-col justify-between p-6 sticky top-0 h-screen z-20">
        <div className="space-y-8">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-indigo-500 to-teal-500 flex items-center justify-center shadow-lg">
              <Activity className="h-5 w-5 text-white" />
            </div>
            <span className="font-extrabold text-xl tracking-wider text-white">
              FITSPHERE<span className="text-indigo-400 font-medium text-xs">.AI</span>
            </span>
          </Link>

          {/* User Preview */}
          <div className="p-4 rounded-2xl bg-white/5 border border-white/5 flex flex-col gap-1 relative overflow-hidden">
            <div className="text-sm font-bold text-white truncate">{user.name}</div>
            <div className="text-xs text-slate-400 truncate">{user.email}</div>
            <div className="mt-2 flex items-center gap-1.5">
              <span className="inline-block h-2 w-2 rounded-full bg-teal-400" />
              <span className="text-[10px] font-bold uppercase tracking-wider text-teal-400">
                {userPlan} Account
              </span>
            </div>
            {userPlan === 'free' && (
              <Link href="/profile" className="mt-3 text-[10px] text-indigo-400 font-bold hover:underline flex items-center gap-0.5">
                <Sparkles className="h-3 w-3 text-indigo-400" /> Upgrade to Premium
              </Link>
            )}
          </div>

          {/* Navigation Links */}
          <nav className="space-y-1.5">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.path;
              return (
                <Link
                  key={item.path}
                  href={item.path}
                  className={`flex items-center gap-3.5 px-4 py-3 rounded-xl text-sm font-semibold transition ${
                    isActive 
                      ? 'bg-gradient-to-r from-indigo-600 to-indigo-500/70 text-white shadow-lg shadow-indigo-600/10' 
                      : 'text-slate-400 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  {item.name}
                </Link>
              );
            })}

            {/* Admin Panel */}
            {user.is_admin && (
              <Link
                href="/admin"
                className={`flex items-center gap-3.5 px-4 py-3 rounded-xl text-sm font-bold transition ${
                  pathname === '/admin'
                    ? 'bg-rose-600 text-white shadow-lg shadow-rose-600/15'
                    : 'text-rose-400/80 hover:text-rose-300 hover:bg-rose-500/5'
                }`}
              >
                <ShieldAlert className="h-5 w-5" />
                Admin Panel
              </Link>
            )}
          </nav>
        </div>

        {/* Logout */}
        <button
          onClick={handleLogout}
          className="flex items-center gap-3.5 px-4 py-3 rounded-xl text-sm font-semibold text-slate-500 hover:text-rose-400 hover:bg-rose-500/5 transition w-full text-left"
        >
          <LogOut className="h-5 w-5" />
          Log Out
        </button>
      </aside>

      {/* Main Page Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile Navigation Header */}
        <header className="md:hidden w-full border-b border-white/5 bg-slate-950/80 backdrop-blur-xl py-4 px-6 flex justify-between items-center z-20">
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-teal-500 flex items-center justify-center">
              <Activity className="h-4.5 w-4.5 text-white" />
            </div>
            <span className="font-extrabold text-lg tracking-wider text-white">FITSPHERE</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/profile" className="text-slate-400 hover:text-white">
              <User className="h-5.5 w-5.5" />
            </Link>
            <button onClick={handleLogout} className="text-slate-400 hover:text-rose-400">
              <LogOut className="h-5.5 w-5.5" />
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-6 md:p-10 max-w-7xl mx-auto w-full relative">
          {children}
        </main>
      </div>
    </div>
  );
}
