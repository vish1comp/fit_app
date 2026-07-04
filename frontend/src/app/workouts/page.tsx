'use client';

import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';
import { api } from '../../lib/api';
import DashboardLayout from '../../components/DashboardLayout';
import { 
  Dumbbell, Plus, Trash2, Search, Sparkles, Trophy, Calendar, Clock, ClipboardList, ShieldAlert, Award
} from 'lucide-react';

export default function WorkoutsPage() {
  const { user } = useSelector((state: RootState) => state.auth);
  
  const getTodayStr = () => new Date().toISOString().split('T')[0];

  const [exercises, setExercises] = useState<any[]>([]);
  const [exerciseSearch, setExerciseSearch] = useState('');
  const [muscleFilter, setMuscleFilter] = useState('');

  // Active workout logger state
  const [showLogForm, setShowLogForm] = useState(false);
  const [workoutName, setWorkoutName] = useState('My Workout');
  const [workoutDate, setWorkoutDate] = useState(getTodayStr());
  const [workoutDuration, setWorkoutDuration] = useState('60'); // minutes
  const [loggedSets, setLoggedSets] = useState<any[]>([
    { exercise_id: '', set_number: 1, weight_kg: '', reps: '', rpe: 8 }
  ]);

  // Workout History state
  const [workoutHistory, setWorkoutHistory] = useState<any[]>([]);
  const [personalRecords, setPersonalRecords] = useState<any[]>([]);

  // AI Generator state
  const [aiWorkoutPlan, setAiWorkoutPlan] = useState<any | null>(null);
  const [splitType, setSplitType] = useState('ppl');
  const [daysPerWeek, setDaysPerWeek] = useState(4);
  const [generatingAI, setGeneratingAI] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);

  const fetchWorkoutData = async () => {
    try {
      const history = await api.workouts.getLogs();
      setWorkoutHistory(history);

      const prs = await api.workouts.getPRs();
      setPersonalRecords(prs);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    // Initial exercise list
    async function loadExercises() {
      try {
        const list = await api.workouts.searchExercises();
        setExercises(list);
      } catch (err) {
        console.error(err);
      }
    }
    loadExercises();
    fetchWorkoutData();
  }, []);

  const handleSearchExercises = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    try {
      const list = await api.workouts.searchExercises(exerciseSearch, muscleFilter);
      setExercises(list);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    handleSearchExercises();
  }, [muscleFilter]);

  const addLoggedSet = () => {
    const nextSetNumber = loggedSets.length + 1;
    setLoggedSets([
      ...loggedSets,
      { exercise_id: '', set_number: nextSetNumber, weight_kg: '', reps: '', rpe: 8 }
    ]);
  };

  const removeLoggedSet = (index: number) => {
    if (loggedSets.length === 1) return;
    setLoggedSets(loggedSets.filter((_, i) => i !== index));
  };

  const updateLoggedSet = (index: number, key: string, value: any) => {
    const updated = [...loggedSets];
    updated[index] = { ...updated[index], [key]: value };
    setLoggedSets(updated);
  };

  const submitWorkoutLog = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Filter invalid sets
    const cleanSets = loggedSets
      .filter(s => s.exercise_id && s.reps && s.weight_kg)
      .map((s, idx) => ({
        exercise_id: parseInt(s.exercise_id),
        set_number: idx + 1,
        weight_kg: parseFloat(s.weight_kg),
        reps: parseInt(s.reps),
        rpe: parseInt(s.rpe)
      }));

    if (cleanSets.length === 0) return;

    try {
      await api.workouts.logWorkout({
        name: workoutName,
        date: workoutDate,
        duration_seconds: parseInt(workoutDuration) * 60,
        sets: cleanSets
      });
      
      setShowLogForm(false);
      setWorkoutName('My Workout');
      setLoggedSets([{ exercise_id: '', set_number: 1, weight_kg: '', reps: '', rpe: 8 }]);
      fetchWorkoutData();
    } catch (err) {
      console.error(err);
    }
  };

  const deleteWorkoutEntry = async (id: number) => {
    try {
      await api.workouts.deleteLog(id);
      fetchWorkoutData();
    } catch (err) {
      console.error(err);
    }
  };

  const generateAIWorkoutPlan = async () => {
    setAiError(null);
    setGeneratingAI(true);
    try {
      const plan = await api.ai.generateWorkout(splitType, daysPerWeek);
      setAiWorkoutPlan(plan);
    } catch (err: any) {
      setAiError(err.message || 'Failed to generate plan. Ensure you have a premium subscription.');
    } finally {
      setGeneratingAI(false);
    }
  };

  const muscles = ['chest', 'back', 'shoulders', 'legs', 'arms', 'core'];

  return (
    <DashboardLayout>
      <div className="space-y-8">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-extrabold text-white">Workouts Log Center</h1>
            <p className="text-slate-400 text-sm mt-1">Plan splits, log weight progression, and audit records.</p>
          </div>
          <button 
            onClick={() => setShowLogForm(!showLogForm)}
            className="btn-premium px-6 py-3 bg-gradient-to-r from-indigo-600 to-teal-500 text-white font-bold rounded-2xl text-sm shadow-lg flex items-center gap-1.5 align-self-start"
          >
            <Plus className="h-4.5 w-4.5" /> {showLogForm ? 'Cancel Logging' : 'Log New Workout'}
          </button>
        </div>

        {/* Dynamic Log Session Form */}
        {showLogForm && (
          <form onSubmit={submitWorkoutLog} className="glass-card p-6 rounded-3xl border-white/5 space-y-6">
            <div className="flex justify-between items-center pb-3 border-b border-white/5">
              <h3 className="font-bold text-lg text-white">Log Workout Session</h3>
              <span className="text-xs text-slate-400">Fill in exercise sets completed</span>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-2">Workout Name</label>
                <input 
                  type="text"
                  required
                  value={workoutName}
                  onChange={(e) => setWorkoutName(e.target.value)}
                  className="w-full bg-slate-900 border border-white/10 px-4 py-2.5 rounded-xl text-sm text-white"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-2">Date</label>
                <input 
                  type="date"
                  required
                  value={workoutDate}
                  onChange={(e) => setWorkoutDate(e.target.value)}
                  className="w-full bg-slate-900 border border-white/10 px-4 py-2.5 rounded-xl text-sm text-white"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-2">Duration (mins)</label>
                <input 
                  type="number"
                  required
                  value={workoutDuration}
                  onChange={(e) => setWorkoutDuration(e.target.value)}
                  className="w-full bg-slate-900 border border-white/10 px-4 py-2.5 rounded-xl text-sm text-white"
                />
              </div>
            </div>

            {/* Set Fields List */}
            <div className="space-y-4">
              <label className="block text-xs font-bold text-slate-300 uppercase">Sets Completed</label>
              {loggedSets.map((set, index) => (
                <div key={index} className="grid grid-cols-1 sm:grid-cols-6 gap-3 p-4 bg-white/2 border border-white/5 rounded-2xl items-center">
                  <div className="sm:col-span-2">
                    <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">Exercise</label>
                    <select
                      required
                      value={set.exercise_id}
                      onChange={(e) => updateLoggedSet(index, 'exercise_id', e.target.value)}
                      className="w-full bg-slate-900 border border-white/10 px-3 py-2 rounded-xl text-xs text-white"
                    >
                      <option value="">Select Exercise...</option>
                      {exercises.map(ex => <option key={ex.id} value={ex.id}>{ex.name} ({ex.muscle_group})</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">Set #</label>
                    <input 
                      type="number"
                      required
                      value={set.set_number}
                      className="w-full bg-slate-900 border border-white/10 px-3 py-2 rounded-xl text-xs text-slate-400"
                      readOnly
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">Weight (kg)</label>
                    <input 
                      type="number"
                      required
                      step="0.5"
                      placeholder="e.g. 60"
                      value={set.weight_kg}
                      onChange={(e) => updateLoggedSet(index, 'weight_kg', e.target.value)}
                      className="w-full bg-slate-900 border border-white/10 px-3 py-2 rounded-xl text-xs text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">Reps</label>
                    <input 
                      type="number"
                      required
                      placeholder="e.g. 10"
                      value={set.reps}
                      onChange={(e) => updateLoggedSet(index, 'reps', e.target.value)}
                      className="w-full bg-slate-900 border border-white/10 px-3 py-2 rounded-xl text-xs text-white"
                    />
                  </div>
                  <div className="flex gap-2 items-center pt-5">
                    <div className="flex-grow">
                      <select 
                        value={set.rpe}
                        onChange={(e) => updateLoggedSet(index, 'rpe', e.target.value)}
                        className="w-full bg-slate-900 border border-white/10 px-2 py-1.5 rounded-xl text-xs text-white"
                      >
                        {[6,7,8,9,10].map(v => <option key={v} value={v}>RPE {v}</option>)}
                      </select>
                    </div>
                    <button 
                      type="button" 
                      onClick={() => removeLoggedSet(index)}
                      className="text-slate-500 hover:text-rose-400 p-1"
                    >
                      <Trash2 className="h-4.5 w-4.5" />
                    </button>
                  </div>
                </div>
              ))}
              <button 
                type="button" 
                onClick={addLoggedSet}
                className="py-2.5 px-4 bg-white/5 border border-white/10 hover:bg-white/10 text-white rounded-xl text-xs font-bold transition flex items-center gap-1.5"
              >
                <Plus className="h-4 w-4" /> Add Set Row
              </button>
            </div>

            <button type="submit" className="w-full py-3.5 bg-gradient-to-r from-indigo-600 to-teal-500 text-white rounded-2xl font-bold text-sm shadow-lg shadow-indigo-600/10">
              Save Completed Session
            </button>
          </form>
        )}

        {/* Main Workouts Modules Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Workout History logs */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* History Logs List */}
            <div className="glass-card rounded-3xl p-6 border-white/5 space-y-4">
              <h3 className="font-bold text-white text-base">Workout History</h3>
              {workoutHistory.length > 0 ? (
                <div className="space-y-4">
                  {workoutHistory.map((log) => (
                    <div key={log.id} className="p-4 bg-white/2 border border-white/5 rounded-2xl space-y-3">
                      <div className="flex justify-between items-center pb-2 border-b border-white/5">
                        <div>
                          <div className="font-bold text-white text-sm">{log.name}</div>
                          <div className="flex items-center gap-2 mt-1 text-[10px] font-semibold text-slate-400">
                            <span className="flex items-center gap-0.5"><Calendar className="h-3 w-3" /> {new Date(log.date).toLocaleDateString()}</span>
                            <span className="flex items-center gap-0.5"><Clock className="h-3 w-3" /> {Math.round(log.duration_seconds / 60)} min</span>
                          </div>
                        </div>
                        <button onClick={() => deleteWorkoutEntry(log.id)} className="text-slate-500 hover:text-rose-400 transition">
                          <Trash2 className="h-4.5 w-4.5" />
                        </button>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {log.sets?.map((set: any) => (
                          <div key={set.id} className="text-xs text-slate-300 flex items-center justify-between p-2 bg-slate-900/50 rounded-xl">
                            <span>{set.exercise?.name}: Set {set.set_number}</span>
                            <span className="font-bold text-white">
                              {set.weight_kg}kg × {set.reps}{' '}
                              {set.is_pr && <Award className="h-4 w-4 inline text-teal-400 ml-1" />}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-10 border border-dashed border-white/5 rounded-2xl text-slate-500 text-xs font-semibold">
                  No workout logs found. Start by entering a completed session above!
                </div>
              )}
            </div>

            {/* Exercise Guide Database */}
            <div className="glass-card rounded-3xl p-6 border-white/5 space-y-4">
              <h3 className="font-bold text-white text-base">Exercise Database Guide</h3>
              
              <div className="flex flex-col sm:flex-row gap-3">
                <div className="relative flex-grow">
                  <Search className="absolute left-4 top-3 h-5 w-5 text-slate-500" />
                  <input 
                    type="text"
                    placeholder="Search Bench, Squats..."
                    value={exerciseSearch}
                    onChange={(e) => setExerciseSearch(e.target.value)}
                    className="w-full bg-slate-900 border border-white/10 pl-12 pr-4 py-2.5 rounded-xl text-xs text-white focus:outline-none"
                  />
                </div>
                <div className="flex gap-2">
                  <select
                    value={muscleFilter}
                    onChange={(e) => setMuscleFilter(e.target.value)}
                    className="bg-slate-900 border border-white/10 px-3 py-2.5 rounded-xl text-xs text-slate-300 focus:outline-none"
                  >
                    <option value="">All Muscles</option>
                    {muscles.map(m => <option key={m} value={m}>{m.toUpperCase()}</option>)}
                  </select>
                  <button onClick={() => handleSearchExercises()} className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold px-4 py-2.5 rounded-xl transition">
                    Search
                  </button>
                </div>
              </div>

              <div className="space-y-4 max-h-96 overflow-y-auto pr-1">
                {exercises.map((ex) => (
                  <div key={ex.id} className="p-4 bg-white/2 border border-white/5 rounded-2xl space-y-2">
                    <div className="flex justify-between items-start">
                      <div className="font-bold text-white text-sm">{ex.name}</div>
                      <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-md">
                        {ex.muscle_group}
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-400 font-semibold uppercase">Difficulty: {ex.difficulty} • Equip: {ex.equipment || 'bodyweight'}</div>
                    <p className="text-xs text-slate-300 leading-relaxed font-medium">{ex.instructions}</p>
                    {ex.common_mistakes && (
                      <div className="text-[11px] text-rose-400/80 leading-normal"><span className="font-bold">Avoid:</span> {ex.common_mistakes}</div>
                    )}
                  </div>
                ))}
              </div>
            </div>

          </div>

          {/* Sidebar Tools: Personal Records and Goal Workout Builder */}
          <div className="space-y-8">
            
            {/* PRs Showcase */}
            <div className="glass-card p-6 rounded-3xl border-white/5 space-y-4">
              <div className="flex items-center gap-2">
                <Trophy className="h-5.5 w-5.5 text-amber-500 animate-bounce" />
                <h3 className="font-bold text-white text-base">Personal Records</h3>
              </div>
              
              {personalRecords.length > 0 ? (
                <div className="space-y-3">
                  {personalRecords.map((pr, idx) => (
                    <div key={idx} className="flex justify-between items-center p-3 bg-white/2 border border-white/5 rounded-xl">
                      <div className="text-xs font-bold text-slate-200">{pr.exercise}</div>
                      <span className="text-xs font-black text-gradient">{pr.max_weight_kg} kg</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-6 text-xs font-semibold text-slate-500">
                  No PR records saved. Keep lifting!
                </div>
              )}
            </div>

            {/* AI Workout Planner */}
            <div className="glass-card p-6 rounded-3xl border-white/5 space-y-4">
              <div className="flex items-center gap-2">
                <Sparkles className="h-5.5 w-5.5 text-indigo-400" />
                <h3 className="font-bold text-white text-base">AI Workout Generator</h3>
              </div>
              <p className="text-slate-400 text-xs leading-relaxed">
                Build professional workout splits with target sets, rep ranges and volume pacing templates.
              </p>

              <div className="space-y-3 text-xs">
                <div>
                  <label className="block font-bold text-slate-400 uppercase mb-1">Split Type</label>
                  <select 
                    value={splitType}
                    onChange={(e) => setSplitType(e.target.value)}
                    className="w-full bg-slate-900 border border-white/10 px-3 py-2 rounded-xl text-white"
                  >
                    <option value="ppl">Push Pull Legs (PPL)</option>
                    <option value="upper_lower">Upper Lower</option>
                    <option value="bro_split">Bro Split</option>
                    <option value="full_body">Full Body</option>
                    <option value="hiit">HIIT Cardio Programs</option>
                    <option value="5x5">StrongLifts 5x5 Strength</option>
                  </select>
                </div>
                <div>
                  <label className="block font-bold text-slate-400 uppercase mb-1">Days Per Week</label>
                  <select 
                    value={daysPerWeek}
                    onChange={(e) => setDaysPerWeek(parseInt(e.target.value))}
                    className="w-full bg-slate-900 border border-white/10 px-3 py-2 rounded-xl text-white"
                  >
                    {[3, 4, 5, 6].map(v => <option key={v} value={v}>{v} Days Split</option>)}
                  </select>
                </div>
              </div>

              <button 
                onClick={generateAIWorkoutPlan}
                disabled={generatingAI}
                className="w-full py-3 bg-gradient-to-r from-indigo-600 to-teal-500 text-white rounded-xl text-xs font-bold shadow-lg transition flex items-center justify-center gap-1.5"
              >
                {generatingAI ? 'Building split...' : 'Build Custom Plan'}
              </button>

              {aiError && (
                <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl text-[10px] font-bold flex items-start gap-1.5 leading-normal">
                  <ShieldAlert className="h-4.5 w-4.5 text-rose-400 flex-shrink-0" />
                  {aiError}
                </div>
              )}

              {aiWorkoutPlan && (
                <div className="mt-4 p-4 bg-slate-950 border border-white/5 rounded-2xl max-h-80 overflow-y-auto space-y-4 text-left">
                  <div className="border-b border-white/5 pb-2 text-center">
                    <span className="text-[10px] font-bold uppercase text-slate-400">Workout Program</span>
                    <div className="text-base font-black text-white">{aiWorkoutPlan.program_name}</div>
                  </div>
                  <div className="text-[11px] text-teal-400 font-semibold leading-normal"><span className="font-bold uppercase text-slate-300">Overload:</span> {aiWorkoutPlan.progressive_overload}</div>
                  {aiWorkoutPlan.schedule?.map((s: any, idx: number) => (
                    <div key={idx} className="space-y-2 border-b border-white/5 pb-3 last:border-0 last:pb-0">
                      <div className="text-xs font-bold text-indigo-400">{s.name} ({s.focus})</div>
                      <div className="space-y-2">
                        {s.exercises?.map((e: any, eidx: number) => (
                          <div key={eidx} className="text-[10px] bg-white/2 p-2 rounded-lg border border-white/5">
                            <div className="font-bold text-slate-200">{e.name}</div>
                            <div className="text-slate-400 mt-0.5">{e.sets} sets × {e.reps} reps (Rest: {e.rest_seconds}s)</div>
                            {e.notes && <div className="text-slate-500 mt-1 italic font-medium">{e.notes}</div>}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

          </div>

        </div>

      </div>
    </DashboardLayout>
  );
}
