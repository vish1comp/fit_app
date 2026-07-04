'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { useDispatch } from 'react-redux';
import { api } from '../../lib/api';
import { setCredentials, setUser, setUserStats } from '../../store/authSlice';
import { Activity, Lock, Mail, User, Sparkles } from 'lucide-react';

export default function RegisterPage() {
  const router = useRouter();
  const dispatch = useDispatch();
  const searchParams = useSearchParams();
  const plan = searchParams.get('plan'); // 'premium' | 'pro' | null

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      // 1. Register User
      await api.auth.register({ name, email, password });

      // 2. Auto Login User
      const loginResp = await api.auth.login({ email, password });
      dispatch(setCredentials(loginResp));

      const profile = await api.users.me();
      dispatch(setUser(profile));

      const stats = await api.users.stats();
      dispatch(setUserStats(stats));

      // 3. Handle Subscription Plan Redirect
      if (plan === 'premium' || plan === 'pro') {
        const checkoutResp = await api.payments.createCheckout(plan);
        if (checkoutResp?.session_url) {
          router.push(checkoutResp.session_url);
          return;
        }
      }

      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Registration failed. Try using a different email.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center p-6 bg-[#030712]">
      {/* Glows */}
      <div className="absolute top-[20%] left-[25%] w-[40%] h-[40%] bg-indigo-500/10 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-[20%] right-[25%] w-[40%] h-[40%] bg-teal-500/10 rounded-full blur-[100px] pointer-events-none" />

      <div className="w-full max-w-md glass-card p-8 rounded-3xl z-10 border border-white/5 relative">
        {/* Title */}
        <div className="flex flex-col items-center mb-8">
          <Link href="/" className="flex items-center gap-2 mb-4">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-teal-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Activity className="h-6 w-6 text-white" />
            </div>
            <span className="font-extrabold text-2xl tracking-wider text-white">
              FITSPHERE<span className="text-indigo-400 font-medium">.AI</span>
            </span>
          </Link>
          <h2 className="text-2xl font-bold text-white mb-1">Create an account</h2>
          <p className="text-slate-400 text-sm">
            {plan ? `Sign up to unlock FitSphere ${plan.charAt(0).toUpperCase() + plan.slice(1)}` : 'Join FitSphere AI fitness ecosystem'}
          </p>
        </div>

        {error && (
          <div className="p-4 mb-6 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm font-medium">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Name */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Your Name</label>
            <div className="relative">
              <User className="absolute left-4 top-3.5 h-5 w-5 text-slate-500" />
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Alex Smith"
                className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition text-sm"
              />
            </div>
          </div>

          {/* Email */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-4 top-3.5 h-5 w-5 text-slate-500" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@domain.com"
                className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition text-sm"
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Password</label>
            <div className="relative">
              <Lock className="absolute left-4 top-3.5 h-5 w-5 text-slate-500" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Min. 8 characters"
                className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition text-sm"
              />
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 bg-gradient-to-r from-indigo-600 to-teal-500 hover:scale-[1.01] active:scale-[0.99] text-white rounded-xl font-bold text-sm shadow-lg shadow-indigo-600/20 transition flex items-center justify-center gap-2"
          >
            {loading ? 'Creating Account...' : plan ? `Subscribe to ${plan.charAt(0).toUpperCase() + plan.slice(1)}` : 'Register Now'}
          </button>
        </form>

        <div className="mt-8 text-center text-sm text-slate-400">
          Already have an account?{' '}
          <Link href="/login" className="text-indigo-400 font-semibold hover:underline">
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}
