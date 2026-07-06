'use client';

import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';
import { api } from '../../lib/api';
import DashboardLayout from '../../components/DashboardLayout';
import { 
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from 'recharts';
import {
  Sparkles,
  Flame,
  Droplet,
  Scale,
  Activity,
  Plus
} from 'lucide-react';

export default function Dashboard() {
  const { user, stats } = useSelector((state: RootState) => state.auth);
  
  // Date string helper
  const getTodayStr = () => new Date().toISOString().split('T')[0];
  
 interface DailySummary {
  total_calories: number;
  total_protein: number;
  total_carbs: number;
  total_fat: number;
  logs: unknown[];
}

const [dailySummary, setDailySummary] = useState({
    total_calories: 0, total_protein: 0, total_carbs: 0, total_fat: 0, logs: []
  });
  
const [weeklySummary, setWeeklySummary] = useState([]);
const [progressLogs, setProgressLogs] = useState([]);
  const [waterIntake, setWaterIntake] = useState(0);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        const summary = await api.nutrition.getDailySummary(getTodayStr());
        setDailySummary(summary);

        const weekly = await api.nutrition.getWeeklySummary();
        setWeeklySummary(weekly);

        const progress = await api.users.getProgress();
        setProgressLogs(progress.slice().reverse()); // Oldest first for line chart

        // Load water from localstorage
        const savedWater = localStorage.getItem(`water_${getTodayStr()}`);
        if (savedWater) setWaterIntake(parseInt(savedWater));
      } catch (err) {
        console.error('Failed to load dashboard data', err);
      }
    }
    loadDashboardData();
  }, []);

  const addWater = (amount: number) => {
    const nextWater = waterIntake + amount;
    setWaterIntake(nextWater);
    localStorage.setItem(`water_${getTodayStr()}`, nextWater.toString());
  };

  // Safe targets with fallbacks
  const targetCalories = stats?.target_calories || 2000;
  const targetProtein = stats?.macros?.protein_g || 140;
  const targetCarbs = stats?.macros?.carbs_g || 220;
  const targetFat = stats?.macros?.fat_g || 65;
  const targetWater = stats?.water_ml || 2500;

  // Calorie math
  const eatenCalories = dailySummary.total_calories || 0;
  const calPercent = Math.min(Math.round((eatenCalories / targetCalories) * 100), 100);
  const remainingCalories = Math.max(targetCalories - eatenCalories, 0);

  // Formatting for Recharts
  const calorieChartData = weeklySummary.map((item: any) => ({
    name: new Date(item.date).toLocaleDateString('en-US', { weekday: 'short' }),
    Calories: Math.round(item.calories),
  }));

  const weightChartData = progressLogs.map((item: any) => ({
    name: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    Weight: item.weight_kg,
  }));

  return (
    <DashboardLayout>
      <div className="space-y-8">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-extrabold text-white">Welcome, {user?.name}!</h1>
            <p className="text-slate-400 text-sm mt-1">Here is your physical tracking report for today.</p>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl text-xs font-bold text-indigo-300">
            <Sparkles className="h-4.5 w-4.5 text-teal-400" />
            Fitness Goal: {user?.fitness_goal?.replace('_', ' ').toUpperCase() || 'GENERAL'}
          </div>
        </div>

        {/* Top Summary Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          
          {/* Calorie Donut Ring Mock */}
          <div className="glass-card p-6 rounded-3xl flex flex-col justify-between border-white/5 md:col-span-2">
            <div className="flex items-center justify-between mb-4">
              <span className="font-bold text-slate-300 text-sm">Caloric Budget</span>
              <Flame className="h-5.5 w-5.5 text-rose-500" />
            </div>
            <div className="flex flex-col sm:flex-row items-center gap-6">
              {/* Radial Circle */}
              <div className="relative h-28 w-28 flex items-center justify-center">
                <svg className="w-full h-full transform -rotate-90">
                  <circle cx="56" cy="56" r="48" stroke="rgba(255,255,255,0.03)" strokeWidth="10" fill="transparent" />
                  <circle cx="56" cy="56" r="48" stroke="url(#indigoGrad)" strokeWidth="10" fill="transparent"
                    strokeDasharray={2 * Math.PI * 48}
                    strokeDashoffset={2 * Math.PI * 48 * (1 - calPercent / 100)}
                    strokeLinecap="round" />
                  <defs>
                    <linearGradient id="indigoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="#6366f1" />
                      <stop offset="100%" stopColor="#14b8a6" />
                    </linearGradient>
                  </defs>
                </svg>
                <div className="absolute text-center">
                  <div className="text-2xl font-black text-white">{calPercent}%</div>
                  <div className="text-[10px] text-slate-400 font-bold uppercase">Budget</div>
                </div>
              </div>
              {/* Text Indicators */}
              <div className="flex-1 space-y-3 w-full">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400 font-medium">Eaten:</span>
                  <span className="text-white font-bold">{Math.round(eatenCalories)} kcal</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400 font-medium">Target:</span>
                  <span className="text-white font-bold">{targetCalories} kcal</span>
                </div>
                <hr className="border-white/5" />
                <div className="flex justify-between text-sm">
                  <span className="text-slate-300 font-bold">Remaining:</span>
                  <span className="text-gradient font-black">{Math.round(remainingCalories)} kcal</span>
                </div>
              </div>
            </div>
          </div>

          {/* Water Tracker */}
          <div className="glass-card p-6 rounded-3xl flex flex-col justify-between border-white/5">
            <div className="flex items-center justify-between mb-2">
              <span className="font-bold text-slate-300 text-sm">Hydration</span>
              <Droplet className="h-5.5 w-5.5 text-indigo-400 animate-pulse" />
            </div>
            <div className="text-center my-2">
              <span className="text-3xl font-extrabold text-white">{waterIntake}</span>
              <span className="text-slate-400 text-xs font-semibold"> / {targetWater}ml</span>
            </div>
            <div className="space-y-2 mt-2">
              <button onClick={() => addWater(250)} className="w-full py-2 bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/20 text-indigo-300 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5">
                <Plus className="h-4 w-4" /> Add 250ml
              </button>
              <button onClick={() => addWater(500)} className="w-full py-2 bg-teal-500/10 hover:bg-teal-500/20 border border-teal-500/20 text-teal-300 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5">
                <Plus className="h-4 w-4" /> Add 500ml
              </button>
            </div>
          </div>

          {/* BMI/BMR Quick view */}
          <div className="glass-card p-6 rounded-3xl flex flex-col justify-between border-white/5">
            <div className="flex items-center justify-between mb-4">
              <span className="font-bold text-slate-300 text-sm">Metabolic Info</span>
              <Activity className="h-5.5 w-5.5 text-teal-400" />
            </div>
            <div className="space-y-3.5">
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-400 font-medium">BMR:</span>
                <span className="text-white font-extrabold">{stats?.bmr || 0} kcal</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-400 font-medium">TDEE:</span>
                <span className="text-white font-extrabold">{stats?.tdee || 0} kcal</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-400 font-medium">BMI:</span>
                <span className="text-white font-extrabold">{stats?.bmi || 0} ({stats?.bmi_category?.split(' ')[0]})</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-400 font-medium">Body Fat:</span>
                <span className="text-white font-extrabold">{stats?.body_fat_estimate ? `${stats.body_fat_estimate}%` : 'N/A'}</span>
              </div>
            </div>
          </div>

        </div>

        {/* Daily Macros Progress */}
        <div className="glass-card p-6 rounded-3xl border-white/5 space-y-4">
          <h3 className="font-bold text-white text-base">Macronutrient Target Levels</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {/* Protein */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-indigo-400 font-bold">Protein</span>
                <span className="text-slate-300 text-xs font-semibold">
                  {Math.round(dailySummary.total_protein || 0)}g / {targetProtein}g
                </span>
              </div>
              <div className="h-2 bg-indigo-500/10 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-indigo-500 rounded-full" 
                  style={{ width: `${Math.min(Math.round(((dailySummary.total_protein || 0) / targetProtein) * 100), 100)}%` }}
                />
              </div>
            </div>

            {/* Carbs */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-teal-400 font-bold">Carbohydrates</span>
                <span className="text-slate-300 text-xs font-semibold">
                  {Math.round(dailySummary.total_carbs || 0)}g / {targetCarbs}g
                </span>
              </div>
              <div className="h-2 bg-teal-500/10 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-teal-400 rounded-full" 
                  style={{ width: `${Math.min(Math.round(((dailySummary.total_carbs || 0) / targetCarbs) * 100), 100)}%` }}
                />
              </div>
            </div>

            {/* Fats */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-pink-400 font-bold">Fats</span>
                <span className="text-slate-300 text-xs font-semibold">
                  {Math.round(dailySummary.total_fat || 0)}g / {targetFat}g
                </span>
              </div>
              <div className="h-2 bg-pink-500/10 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-pink-400 rounded-full" 
                  style={{ width: `${Math.min(Math.round(((dailySummary.total_fat || 0) / targetFat) * 100), 100)}%` }}
                />
              </div>
            </div>

          </div>
        </div>

        {/* Analytics Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* Caloric Intake Chart */}
          <div className="glass-card p-6 rounded-3xl border border-white/5 space-y-4">
            <h3 className="font-bold text-white text-base">Caloric Intake History</h3>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={calorieChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} tickLine={false} />
                  <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                  <Tooltip 
                    contentStyle={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }}
                    labelStyle={{ color: '#fff', fontWeight: 'bold' }}
                  />
                  <Bar dataKey="Calories" fill="#6366f1" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Weight Log Chart */}
          <div className="glass-card p-6 rounded-3xl border border-white/5 space-y-4">
            <h3 className="font-bold text-white text-base">Weight Progression (kg)</h3>
            {weightChartData.length > 0 ? (
              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={weightChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} tickLine={false} />
                    <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} domain={['dataMin - 2', 'dataMax + 2']} />
                    <Tooltip 
                      contentStyle={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }}
                      labelStyle={{ color: '#fff', fontWeight: 'bold' }}
                    />
                    <Line type="monotone" dataKey="Weight" stroke="#14b8a6" strokeWidth={3} activeDot={{ r: 6 }} dot={{ r: 3 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-72 flex flex-col items-center justify-center text-center p-6 border border-dashed border-white/5 rounded-2xl bg-white/1">
                <Scale className="h-8 w-8 text-slate-600 mb-2" />
                <div className="font-semibold text-slate-400 text-sm">No Weight Logs Yet</div>
                <p className="text-slate-500 text-xs max-w-xs mt-1">Log your weight in the Profile tab to build progress graph details.</p>
              </div>
            )}
          </div>

        </div>

      </div>
    </DashboardLayout>
  );
}
