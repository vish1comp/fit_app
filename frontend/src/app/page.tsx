'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { 
  Dumbbell, 
  Sparkles, 
  Apple, 
  TrendingUp, 
  ShieldCheck, 
  MessageSquare, 
  ArrowRight,
  BrainCircuit,
  Zap,
  Activity
} from 'lucide-react';

export default function LandingPage() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.15 }
    }
  };

  const itemVariants = {
    hidden: { y: 30, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { duration: 0.6, ease: "easeOut" }
    }
  };

  return (
    <div className="min-h-screen relative flex flex-col justify-between">
      
      {/* Background Glows */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-indigo-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-teal-500/10 rounded-full blur-[120px] pointer-events-none" />

      {/* Navigation */}
      <header className="w-full border-b border-white/5 py-4 px-6 md:px-12 flex justify-between items-center glass-card sticky top-0 z-50">
        <Link href="/" className="flex items-center gap-2">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-teal-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Activity className="h-6 w-6 text-white" />
          </div>
          <span className="font-extrabold text-2xl tracking-wider bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent">
            FITSPHERE<span className="text-indigo-400 font-medium">.AI</span>
          </span>
        </Link>
        <nav className="hidden md:flex items-center gap-8 text-sm font-semibold text-slate-300">
          <a href="#features" className="hover:text-white transition">Features</a>
          <a href="#pricing" className="hover:text-white transition">Pricing</a>
          <a href="#supplements" className="hover:text-white transition">Scientific Supplements</a>
        </nav>
        <div className="flex items-center gap-4">
          <Link href="/login" className="text-sm font-semibold text-slate-300 hover:text-white transition">
            Log In
          </Link>
          <Link href="/register" className="btn-premium px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-teal-500 text-white rounded-xl text-sm font-bold shadow-lg shadow-indigo-600/30 hover:scale-105 transition transform duration-200">
            Get Started
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-grow max-w-7xl mx-auto px-6 md:px-12 pt-20 pb-24 text-center">
        <motion.div 
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="flex flex-col items-center"
        >
          {/* Tag */}
          <motion.div 
            variants={itemVariants}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/5 border border-white/10 text-xs font-semibold tracking-wide text-indigo-300 mb-8"
          >
            <Sparkles className="h-4.5 w-4.5 text-teal-400" />
            Empowered by Gemini 2.0 Flash AI
          </motion.div>

          {/* Heading */}
          <motion.h1 
            variants={itemVariants}
            className="text-4xl md:text-7xl font-extrabold tracking-tight max-w-4xl leading-tight md:leading-none text-white mb-6"
          >
            Re-engineer Your Body with <span className="text-gradient font-black">AI Precision</span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p 
            variants={itemVariants}
            className="text-lg md:text-xl text-slate-400 max-w-2xl mb-12 font-medium leading-relaxed"
          >
            Your ultimate companion for automated workout programs, personalized diet plan analytics, scientific supplement guides, and direct 24/7 access to your personal AI Coach.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div 
            variants={itemVariants}
            className="flex flex-col sm:flex-row items-center gap-5 w-full sm:w-auto"
          >
            <Link href="/register" className="w-full sm:w-auto btn-premium flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-indigo-600 to-teal-500 text-white rounded-2xl text-base font-bold shadow-xl shadow-indigo-600/20 hover:scale-[1.03] transition duration-200">
              Start Free Trial <ArrowRight className="h-5 w-5" />
            </Link>
            <a href="#features" className="w-full sm:w-auto flex items-center justify-center gap-2 px-8 py-4 bg-white/5 border border-white/10 hover:bg-white/10 text-white rounded-2xl text-base font-bold transition">
              Explore Features
            </a>
          </motion.div>
        </motion.div>

        {/* Mockup Showcase */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.8 }}
          className="mt-20 relative glass-card p-4 rounded-3xl border border-white/10 max-w-5xl mx-auto shadow-2xl overflow-hidden"
        >
          <div className="absolute top-0 left-0 w-full h-8 bg-white/5 border-b border-white/5 flex items-center gap-2 px-4">
            <div className="h-3.5 w-3.5 rounded-full bg-rose-500/80" />
            <div className="h-3.5 w-3.5 rounded-full bg-amber-500/80" />
            <div className="h-3.5 w-3.5 rounded-full bg-emerald-500/80" />
          </div>
          <div className="pt-8 aspect-[16/9] w-full bg-slate-950 flex items-center justify-center rounded-2xl border border-white/5 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-b from-indigo-950/20 to-slate-950" />
            <div className="z-10 grid grid-cols-3 gap-6 max-w-3xl p-6 text-left w-full">
              <div className="glass-card p-6 rounded-2xl">
                <Dumbbell className="h-8 w-8 text-indigo-400 mb-4" />
                <h3 className="font-bold text-lg mb-1 text-white">Push Pull Legs</h3>
                <p className="text-slate-400 text-xs">Generated for Muscle Building</p>
                <div className="mt-4 h-2 bg-indigo-500/20 rounded-full overflow-hidden">
                  <div className="h-full w-[80%] bg-indigo-500 rounded-full" />
                </div>
              </div>
              <div className="glass-card p-6 rounded-2xl">
                <Apple className="h-8 w-8 text-teal-400 mb-4" />
                <h3 className="font-bold text-lg mb-1 text-white">Daily Target</h3>
                <p className="text-slate-400 text-xs">2,450 Calories • 160g Protein</p>
                <div className="mt-4 h-2 bg-teal-500/20 rounded-full overflow-hidden">
                  <div className="h-full w-[65%] bg-teal-500 rounded-full" />
                </div>
              </div>
              <div className="glass-card p-6 rounded-2xl">
                <MessageSquare className="h-8 w-8 text-pink-400 mb-4" />
                <h3 className="font-bold text-lg mb-1 text-white">AI Coach</h3>
                <p className="text-slate-400 text-xs">"Take 5g Creatine post-workout..."</p>
                <div className="mt-4 h-2 bg-pink-500/20 rounded-full overflow-hidden">
                  <div className="h-full w-[95%] bg-pink-500 rounded-full" />
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Features Grid */}
        <section id="features" className="pt-32">
          <h2 className="text-3xl md:text-5xl font-extrabold text-white mb-4">Core Ecosystem</h2>
          <p className="text-slate-400 max-w-xl mx-auto mb-16 font-medium">Professional grade modules packed into a beautiful cloud-synced software engine.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
            <div className="glass-card p-8 rounded-3xl">
              <div className="h-12 w-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-6">
                <BrainCircuit className="h-6 w-6" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">AI Coach Chatbot</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                Connect instantly to your personal trainer powered by deep knowledge of your statistics, history, goals, and training records.
              </p>
            </div>
            <div className="glass-card p-8 rounded-3xl">
              <div className="h-12 w-12 rounded-2xl bg-teal-500/10 border border-teal-500/20 flex items-center justify-center text-teal-400 mb-6">
                <Apple className="h-6 w-6" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Barcode Food Logger</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                Seamless food logging with detailed summaries of proteins, carbohydrates, fats, sodium, sugars, and vitamins categorized into meals.
              </p>
            </div>
            <div className="glass-card p-8 rounded-3xl">
              <div className="h-12 w-12 rounded-2xl bg-pink-500/10 border border-pink-500/20 flex items-center justify-center text-pink-400 mb-6">
                <Dumbbell className="h-6 w-6" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Workout Set Tracker</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                Log exercises set-by-set (reps, weight, RPE). Automatically detects Personal Records (PRs) and calculates training volume statistics.
              </p>
            </div>
          </div>
        </section>

        {/* Pricing Matrix */}
        <section id="pricing" className="pt-32">
          <h2 className="text-3xl md:text-5xl font-extrabold text-white mb-4">Subscription Tiers</h2>
          <p className="text-slate-400 max-w-xl mx-auto mb-16 font-medium">Upgrade anytime. Standard transparent billing with Stripe checkout.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Free */}
            <div className="glass-card p-8 rounded-3xl text-left border-white/5 relative flex flex-col justify-between">
              <div>
                <h3 className="text-xl font-bold text-slate-300 mb-2">Free Plan</h3>
                <div className="flex items-baseline gap-1 mb-6">
                  <span className="text-4xl font-extrabold text-white">$0</span>
                  <span className="text-slate-400 text-sm">/month</span>
                </div>
                <ul className="space-y-4 text-sm text-slate-300 mb-8">
                  <li className="flex items-center gap-2"><ShieldCheck className="h-4.5 w-4.5 text-teal-400" /> Basic Calorie Tracking</li>
                  <li className="flex items-center gap-2"><ShieldCheck className="h-4.5 w-4.5 text-teal-400" /> Basic Workout Logs</li>
                  <li className="flex items-center gap-2"><ShieldCheck className="h-4.5 w-4.5 text-teal-400" /> Max 5 AI Coach Queries</li>
                </ul>
              </div>
              <Link href="/register" className="w-full text-center py-3 bg-white/5 border border-white/10 hover:bg-white/10 text-white rounded-xl font-bold text-sm transition">
                Get Started
              </Link>
            </div>

            {/* Premium */}
            <div className="glass-card p-8 rounded-3xl text-left border-indigo-500/30 relative flex flex-col justify-between shadow-xl shadow-indigo-500/5">
              <div className="absolute top-0 right-8 transform -translate-y-1/2 bg-gradient-to-r from-indigo-500 to-teal-500 text-white text-xs font-bold uppercase tracking-wider px-3.5 py-1 rounded-full">
                Most Popular
              </div>
              <div>
                <h3 className="text-xl font-bold text-white mb-2">Premium Plan</h3>
                <div className="flex items-baseline gap-1 mb-6">
                  <span className="text-4xl font-extrabold text-white">$9.99</span>
                  <span className="text-slate-400 text-sm">/month</span>
                </div>
                <ul className="space-y-4 text-sm text-slate-300 mb-8">
                  <li className="flex items-center gap-2"><Zap className="h-4.5 w-4.5 text-indigo-400" /> Unlimited AI Coach Chat</li>
                  <li className="flex items-center gap-2"><Zap className="h-4.5 w-4.5 text-indigo-400" /> Custom AI Workout Builder</li>
                  <li className="flex items-center gap-2"><Zap className="h-4.5 w-4.5 text-indigo-400" /> Custom AI Meal Planner</li>
                  <li className="flex items-center gap-2"><Zap className="h-4.5 w-4.5 text-indigo-400" /> Scientific Supplement Center</li>
                  <li className="flex items-center gap-2"><Zap className="h-4.5 w-4.5 text-indigo-400" /> Advanced Volume Analytics</li>
                </ul>
              </div>
              <Link href="/register?plan=premium" className="w-full text-center py-3 bg-gradient-to-r from-indigo-600 to-teal-500 text-white rounded-xl font-bold text-sm shadow-lg shadow-indigo-600/20 hover:scale-[1.02] transition">
                Subscribe Now
              </Link>
            </div>

            {/* Pro */}
            <div className="glass-card p-8 rounded-3xl text-left border-white/5 relative flex flex-col justify-between">
              <div>
                <h3 className="text-xl font-bold text-slate-300 mb-2">Pro Plan</h3>
                <div className="flex items-baseline gap-1 mb-6">
                  <span className="text-4xl font-extrabold text-white">$19.99</span>
                  <span className="text-slate-400 text-sm">/month</span>
                </div>
                <ul className="space-y-4 text-sm text-slate-300 mb-8">
                  <li className="flex items-center gap-2"><Sparkles className="h-4.5 w-4.5 text-pink-400" /> Everything in Premium</li>
                  <li className="flex items-center gap-2"><Sparkles className="h-4.5 w-4.5 text-pink-400" /> Advanced AI Trainer</li>
                  <li className="flex items-center gap-2"><Sparkles className="h-4.5 w-4.5 text-pink-400" /> Personalized Nutrition Coaching</li>
                  <li className="flex items-center gap-2"><Sparkles className="h-4.5 w-4.5 text-pink-400" /> Priority Admin Support</li>
                </ul>
              </div>
              <Link href="/register?plan=pro" className="w-full text-center py-3 bg-white/5 border border-white/10 hover:bg-white/10 text-white rounded-xl font-bold text-sm transition">
                Get Started
              </Link>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-white/5 py-8 text-center text-sm text-slate-500">
        © {new Date().getFullYear()} FitSphere AI Inc. Built for peak performance.
      </footer>
    </div>
  );
}
