'use client';

import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';
import { api } from '../../lib/api';
import DashboardLayout from '../../components/DashboardLayout';
import { 
  Apple, Plus, Search, Calendar, ChevronRight, Sparkles, Trash2, Camera, ClipboardList, ShieldAlert
} from 'lucide-react';

export default function NutritionPage() {
  const { stats, user } = useSelector((state: RootState) => state.auth);
  
  const getTodayStr = () => new Date().toISOString().split('T')[0];
  
  const [selectedDate, setSelectedDate] = useState(getTodayStr());
  const [logs, setLogs] = useState<any[]>([]);
  const [dailySummary, setDailySummary] = useState<any>({ total_calories: 0, total_protein: 0, total_carbs: 0, total_fat: 0 });
  
  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [selectedFood, setSelectedFood] = useState<any | null>(null);
  const [servingQuantity, setServingQuantity] = useState(1);
  const [selectedMealType, setSelectedMealType] = useState<'breakfast' | 'lunch' | 'dinner' | 'snacks'>('breakfast');

  // Custom Food builder state
  const [showCustomFood, setShowCustomFood] = useState(false);
  const [customName, setCustomName] = useState('');
  const [customCalories, setCustomCalories] = useState(0);
  const [customProtein, setCustomProtein] = useState(0);
  const [customCarbs, setCustomCarbs] = useState(0);
  const [customFat, setCustomFat] = useState(0);

  // AI Planner state
  const [aiMealPlan, setAiMealPlan] = useState<any | null>(null);
  const [generatingAI, setGeneratingAI] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);

  // Barcode simulation
  const [barcodeInput, setBarcodeInput] = useState('');
  const [barcodeError, setBarcodeError] = useState<string | null>(null);

  const fetchLogs = async () => {
    try {
      const summary = await api.nutrition.getDailySummary(selectedDate);
      setDailySummary(summary);
      setLogs(summary.logs || []);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [selectedDate]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    try {
      const results = await api.nutrition.searchFoods(searchQuery);
      setSearchResults(results);
    } catch (err) {
      console.error(err);
    }
  };

  const logFoodItem = async (food: any) => {
    try {
      await api.nutrition.logFood({
        food_item_id: food.id,
        date: selectedDate,
        meal_type: selectedMealType,
        food_name: food.name,
        serving_size_g: food.serving_size_g,
        servings: parseFloat(servingQuantity.toString()),
        calories: food.calories,
        protein: food.protein,
        carbs: food.carbs,
        fat: food.fat,
        fiber: food.fiber || 0,
        sugar: food.sugar || 0,
        sodium: food.sodium || 0
      });
      setSelectedFood(null);
      setSearchQuery('');
      setSearchResults([]);
      fetchLogs();
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateCustomFood = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const newFood = await api.nutrition.createFood({
        name: customName,
        calories: customCalories,
        protein: customProtein,
        carbs: customCarbs,
        fat: customFat,
        serving_size: '100g',
        serving_size_g: 100
      });
      setShowCustomFood(false);
      logFoodItem(newFood);
      setCustomName('');
      setCustomCalories(0);
      setCustomProtein(0);
      setCustomCarbs(0);
      setCustomFat(0);
    } catch (err) {
      console.error(err);
    }
  };

  const deleteLogEntry = async (id: number) => {
    try {
      await api.nutrition.deleteLog(id);
      fetchLogs();
    } catch (err) {
      console.error(err);
    }
  };

  const simulateBarcodeScan = async () => {
    setBarcodeError(null);
    if (!barcodeInput.trim()) return;
    try {
      const food = await api.nutrition.getFoodByBarcode(barcodeInput);
      setSelectedFood(food);
      setBarcodeInput('');
    } catch (err: any) {
      setBarcodeError(err.message || 'No product found with this barcode.');
    }
  };

  const generateAIMealPlan = async () => {
    setAiError(null);
    setGeneratingAI(true);
    try {
      const plan = await api.ai.generateDiet(7);
      setAiMealPlan(plan);
    } catch (err: any) {
      setAiError(err.message || 'Failed to generate plan. Ensure you have a premium subscription.');
    } finally {
      setGeneratingAI(false);
    }
  };

  // Grouped logs helper
  const getLogsByMeal = (mealType: string) => logs.filter(l => l.meal_type === mealType);

  const mealTypes: ('breakfast' | 'lunch' | 'dinner' | 'snacks')[] = ['breakfast', 'lunch', 'dinner', 'snacks'];

  return (
    <DashboardLayout>
      <div className="space-y-8">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-extrabold text-white">Nutrition Logging</h1>
            <p className="text-slate-400 text-sm mt-1">Keep track of your macros, vitamins, and calories.</p>
          </div>
          {/* Date Picker */}
          <div className="relative">
            <input 
              type="date" 
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="bg-white/5 border border-white/10 px-4 py-2.5 rounded-2xl text-slate-300 text-sm font-semibold focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        {/* Eaten Summary Header */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="glass-card p-4 rounded-2xl border-white/5 text-center">
            <div className="text-xs text-slate-400 font-bold uppercase">Calories Eaten</div>
            <div className="text-xl font-extrabold text-white mt-1">{Math.round(dailySummary.total_calories || 0)} <span className="text-[10px] text-slate-400 font-medium">kcal</span></div>
          </div>
          <div className="glass-card p-4 rounded-2xl border-white/5 text-center">
            <div className="text-xs text-slate-400 font-bold uppercase">Protein Target</div>
            <div className="text-xl font-extrabold text-indigo-400 mt-1">{Math.round(dailySummary.total_protein || 0)}g <span className="text-[10px] text-slate-500">/ {stats?.macros?.protein_g || 140}g</span></div>
          </div>
          <div className="glass-card p-4 rounded-2xl border-white/5 text-center">
            <div className="text-xs text-slate-400 font-bold uppercase">Carbohydrates</div>
            <div className="text-xl font-extrabold text-teal-400 mt-1">{Math.round(dailySummary.total_carbs || 0)}g <span className="text-[10px] text-slate-500">/ {stats?.macros?.carbs_g || 220}g</span></div>
          </div>
          <div className="glass-card p-4 rounded-2xl border-white/5 text-center">
            <div className="text-xs text-slate-400 font-bold uppercase">Fats Tracked</div>
            <div className="text-xl font-extrabold text-pink-400 mt-1">{Math.round(dailySummary.total_fat || 0)}g <span className="text-[10px] text-slate-500">/ {stats?.macros?.fat_g || 65}g</span></div>
          </div>
          <div className="glass-card p-4 rounded-2xl border-white/5 text-center col-span-2 md:col-span-1">
            <div className="text-xs text-slate-400 font-bold uppercase">Sodium / Fiber</div>
            <div className="text-sm font-semibold text-slate-300 mt-2">
              {Math.round(dailySummary.total_sodium || 0)}mg / {Math.round(dailySummary.total_fiber || 0)}g
            </div>
          </div>
        </div>

        {/* Meal Logging Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Main Log List */}
          <div className="lg:col-span-2 space-y-6">
            {mealTypes.map((mealType) => {
              const mealLogs = getLogsByMeal(mealType);
              const mealCalories = mealLogs.reduce((acc, curr) => acc + curr.calories, 0);
              return (
                <div key={mealType} className="glass-card rounded-3xl p-6 border-white/5 space-y-4">
                  <div className="flex justify-between items-center pb-2 border-b border-white/5">
                    <h3 className="font-bold text-lg text-white capitalize">{mealType}</h3>
                    <span className="text-xs font-bold text-slate-400">{Math.round(mealCalories)} kcal</span>
                  </div>
                  
                  {mealLogs.length > 0 ? (
                    <div className="space-y-3">
                      {mealLogs.map((log) => (
                        <div key={log.id} className="flex items-center justify-between p-3.5 bg-white/2 rounded-2xl border border-white/5 hover:border-white/10 transition">
                          <div>
                            <div className="font-bold text-white text-sm">{log.food_name}</div>
                            <div className="text-xs text-slate-400 mt-0.5">
                              {log.servings} serving(s) • P: {log.protein}g C: {log.carbs}g F: {log.fat}g
                            </div>
                          </div>
                          <div className="flex items-center gap-4">
                            <span className="text-sm font-bold text-white">{Math.round(log.calories)} kcal</span>
                            <button onClick={() => deleteLogEntry(log.id)} className="text-slate-500 hover:text-rose-400 transition">
                              <Trash2 className="h-4.5 w-4.5" />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-6 text-xs font-semibold text-slate-500">
                      No logs entered for this meal.
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Sidebar Tools: Add Food, Barcode simulator, AI Planner */}
          <div className="space-y-8">
            
            {/* Search/Add Food */}
            <div className="glass-card p-6 rounded-3xl border-white/5 space-y-4">
              <h3 className="font-bold text-white text-base">Quick-Log Food</h3>
              
              <form onSubmit={handleSearch} className="relative">
                <Search className="absolute left-4 top-3 h-5 w-5 text-slate-500" />
                <input 
                  type="text"
                  placeholder="Search Chicken, Rice..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 pl-12 pr-4 py-2.5 rounded-2xl text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 text-sm"
                />
              </form>

              {/* Barcode Simulator */}
              <div className="border border-white/5 p-4 rounded-2xl space-y-3">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
                  <Camera className="h-4.5 w-4.5 text-indigo-400" />
                  Barcode Product Scan
                </div>
                <div className="flex gap-2">
                  <input 
                    type="text" 
                    placeholder="Enter EAN barcode..."
                    value={barcodeInput}
                    onChange={(e) => setBarcodeInput(e.target.value)}
                    className="flex-1 bg-white/5 border border-white/10 px-3 py-1.5 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none"
                  />
                  <button onClick={simulateBarcodeScan} className="bg-indigo-600 hover:bg-indigo-500 px-3 py-1.5 rounded-xl text-xs font-bold text-white transition">
                    Scan
                  </button>
                </div>
                {barcodeError && <div className="text-[10px] text-rose-400">{barcodeError}</div>}
              </div>

              {/* Search Results list */}
              {searchResults.length > 0 && (
                <div className="max-h-48 overflow-y-auto space-y-2 pr-1">
                  {searchResults.map((food) => (
                    <button 
                      key={food.id} 
                      onClick={() => setSelectedFood(food)}
                      className="w-full text-left p-3.5 bg-white/2 border border-white/5 rounded-xl hover:border-indigo-500/30 transition flex items-center justify-between"
                    >
                      <div>
                        <div className="text-xs font-bold text-white">{food.name}</div>
                        <div className="text-[10px] text-slate-400">P: {food.protein}g C: {food.carbs}g F: {food.fat}g</div>
                      </div>
                      <ChevronRight className="h-4 w-4 text-slate-400" />
                    </button>
                  ))}
                </div>
              )}

              {/* Food log configurations form */}
              {selectedFood && (
                <div className="p-4 bg-indigo-500/5 border border-indigo-500/20 rounded-2xl space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-bold text-indigo-300 truncate max-w-[150px]">{selectedFood.name}</span>
                    <button onClick={() => setSelectedFood(null)} className="text-[10px] text-slate-400 hover:underline">Cancel</button>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">Meal Type</label>
                      <select 
                        value={selectedMealType}
                        onChange={(e: any) => setSelectedMealType(e.target.value)}
                        className="w-full bg-slate-900 border border-white/10 px-2 py-1.5 rounded-xl text-xs text-white"
                      >
                        {mealTypes.map(m => <option key={m} value={m}>{m}</option>)}
                      </select>
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1">Servings</label>
                      <input 
                        type="number"
                        step="0.25"
                        min="0.25"
                        value={servingQuantity}
                        onChange={(e) => setServingQuantity(parseFloat(e.target.value))}
                        className="w-full bg-slate-900 border border-white/10 px-3 py-1.5 rounded-xl text-xs text-white"
                      />
                    </div>
                  </div>
                  <button onClick={() => logFoodItem(selectedFood)} className="w-full py-2 bg-gradient-to-r from-indigo-600 to-teal-500 text-white rounded-xl text-xs font-bold shadow-md shadow-indigo-600/10">
                    Add to Meal Log
                  </button>
                </div>
              )}

              {/* Custom food builder toggler */}
              <button 
                onClick={() => setShowCustomFood(!showCustomFood)} 
                className="w-full text-center text-xs font-semibold text-indigo-400 hover:underline"
              >
                {showCustomFood ? 'Cancel custom food' : 'Create Custom Food Item'}
              </button>

              {/* Custom Food builder form */}
              {showCustomFood && (
                <form onSubmit={handleCreateCustomFood} className="p-4 bg-white/2 border border-white/5 rounded-2xl space-y-3">
                  <input 
                    type="text" 
                    required 
                    placeholder="Food Name (e.g. Scrambled eggs)" 
                    value={customName}
                    onChange={(e) => setCustomName(e.target.value)}
                    className="w-full bg-slate-900 border border-white/10 px-3 py-2 rounded-xl text-xs text-white"
                  />
                  <div className="grid grid-cols-2 gap-2">
                    <input 
                      type="number" 
                      placeholder="Calories (kcal)" 
                      value={customCalories || ''}
                      onChange={(e) => setCustomCalories(parseFloat(e.target.value) || 0)}
                      className="bg-slate-900 border border-white/10 px-3 py-2 rounded-xl text-xs text-white"
                    />
                    <input 
                      type="number" 
                      placeholder="Protein (g)" 
                      value={customProtein || ''}
                      onChange={(e) => setCustomProtein(parseFloat(e.target.value) || 0)}
                      className="bg-slate-900 border border-white/10 px-3 py-2 rounded-xl text-xs text-white"
                    />
                    <input 
                      type="number" 
                      placeholder="Carbs (g)" 
                      value={customCarbs || ''}
                      onChange={(e) => setCustomCarbs(parseFloat(e.target.value) || 0)}
                      className="bg-slate-900 border border-white/10 px-3 py-2 rounded-xl text-xs text-white"
                    />
                    <input 
                      type="number" 
                      placeholder="Fat (g)" 
                      value={customFat || ''}
                      onChange={(e) => setCustomFat(parseFloat(e.target.value) || 0)}
                      className="bg-slate-900 border border-white/10 px-3 py-2 rounded-xl text-xs text-white"
                    />
                  </div>
                  <button type="submit" className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 rounded-xl text-xs font-bold text-white transition">
                    Create & Log
                  </button>
                </form>
              )}

            </div>

            {/* AI Meal Planner */}
            <div className="glass-card p-6 rounded-3xl border-white/5 space-y-4">
              <div className="flex items-center gap-2">
                <Sparkles className="h-5.5 w-5.5 text-indigo-400" />
                <h3 className="font-bold text-white text-base">AI Diet Planner</h3>
              </div>
              <p className="text-slate-400 text-xs leading-relaxed">
                Generate a personalized weekly meal structure designed around your dietary preference ({user?.dietary_preference || 'vegetarian'}).
              </p>
              
              <button 
                onClick={generateAIMealPlan}
                disabled={generatingAI}
                className="w-full py-3 bg-gradient-to-r from-indigo-600 to-teal-500 text-white rounded-xl text-xs font-bold shadow-lg transition flex items-center justify-center gap-1.5"
              >
                {generatingAI ? 'Generating plan...' : 'Build 7-Day Meal Split'}
              </button>

              {aiError && (
                <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl text-[10px] font-bold flex items-start gap-1.5 leading-normal">
                  <ShieldAlert className="h-4.5 w-4.5 text-rose-400 flex-shrink-0" />
                  {aiError}
                </div>
              )}

              {aiMealPlan && (
                <div className="mt-4 p-4 bg-slate-950 border border-white/5 rounded-2xl max-h-80 overflow-y-auto space-y-4 text-left">
                  <div className="border-b border-white/5 pb-2 text-center">
                    <span className="text-[10px] font-bold uppercase text-slate-400">Target Calories</span>
                    <div className="text-lg font-black text-white">{aiMealPlan.daily_targets?.calories} kcal</div>
                    <div className="text-[10px] text-indigo-300">P: {aiMealPlan.daily_targets?.protein}g C: {aiMealPlan.daily_targets?.carbs}g F: {aiMealPlan.daily_targets?.fat}g</div>
                  </div>
                  {aiMealPlan.days?.map((d: any) => (
                    <div key={d.day} className="space-y-2 border-b border-white/5 pb-3 last:border-0 last:pb-0">
                      <div className="text-xs font-bold text-indigo-400">Day {d.day}</div>
                      {Object.entries(d.meals).map(([type, meal]: any) => (
                        <div key={type} className="text-[10px] space-y-0.5">
                          <span className="font-bold text-slate-300 capitalize">{type}:</span>{' '}
                          <span className="text-slate-400">{meal.name}</span>
                        </div>
                      ))}
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
