const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  
  const headers = new Headers(options.headers);
  headers.set('Content-Type', 'application/json');
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      // Redirect to login if on protected route
      if (!window.location.pathname.startsWith('/login') && !window.location.pathname.startsWith('/register') && window.location.pathname !== '/') {
        window.location.href = '/login';
      }
    }
    throw new Error('Unauthorized');
  }

  if (response.status === 204) {
    return {} as T;
  }

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Something went wrong');
  }

  return data as T;
}

export const api = {
  // Auth
  auth: {
    register: (body: any) => request<any>('/auth/register', { method: 'POST', body: JSON.stringify(body) }),
    login: (body: any) => request<any>('/auth/login', { method: 'POST', body: JSON.stringify(body) }),
    forgotPassword: (body: any) => request<any>('/auth/forgot-password', { method: 'POST', body: JSON.stringify(body) }),
    resetPassword: (body: any) => request<any>('/auth/reset-password', { method: 'POST', body: JSON.stringify(body) }),
    verifyEmail: (token: string) => request<any>(`/auth/verify-email?token=${token}`),
  },

  // Users
  users: {
    me: () => request<any>('/users/me'),
    updateMe: (body: any) => request<any>('/users/me', { method: 'PUT', body: JSON.stringify(body) }),
    stats: () => request<any>('/users/me/stats'),
    getProgress: () => request<any[]>('/users/me/progress'),
    logProgress: (body: any) => request<any>('/users/me/progress', { method: 'POST', body: JSON.stringify(body) }),
  },

  // Nutrition
  nutrition: {
    searchFoods: (q?: string, category?: string) => {
      let query = '';
      if (q || category) {
        const params = new URLSearchParams();
        if (q) params.set('q', q);
        if (category) params.set('category', category);
        query = `?${params.toString()}`;
      }
      return request<any[]>(`/nutrition/foods${query}`);
    },
    getFoodByBarcode: (barcode: string) => request<any>(`/nutrition/foods/barcode/${barcode}`),
    createFood: (body: any) => request<any>('/nutrition/foods', { method: 'POST', body: JSON.stringify(body) }),
    logFood: (body: any) => request<any>('/nutrition/logs', { method: 'POST', body: JSON.stringify(body) }),
    getLogs: (date?: string, mealType?: string) => {
      const params = new URLSearchParams();
      if (date) params.set('log_date', date);
      if (mealType) params.set('meal_type', mealType);
      return request<any[]>(`/nutrition/logs?${params.toString()}`);
    },
    getDailySummary: (date: string) => request<any>(`/nutrition/logs/summary/${date}`),
    getWeeklySummary: () => request<any[]>('/nutrition/logs/weekly'),
    deleteLog: (id: number) => request<any>(`/nutrition/logs/${id}`, { method: 'DELETE' }),
  },

  // Workouts
  workouts: {
    searchExercises: (q?: string, muscle?: string) => {
      const params = new URLSearchParams();
      if (q) params.set('q', q);
      if (muscle) params.set('muscle_group', muscle);
      return request<any[]>(`/workouts/exercises?${params.toString()}`);
    },
    logWorkout: (body: any) => request<any>('/workouts/logs', { method: 'POST', body: JSON.stringify(body) }),
    getLogs: () => request<any[]>('/workouts/logs'),
    getVolumeAnalytics: (exerciseId?: number) => {
      const q = exerciseId ? `?exercise_id=${exerciseId}` : '';
      return request<any[]>(`/workouts/analytics/volume${q}`);
    },
    getPRs: () => request<any[]>('/workouts/analytics/prs'),
    deleteLog: (id: number) => request<any>(`/workouts/logs/${id}`, { method: 'DELETE' }),
  },

  // Supplements
  supplements: {
    list: (q?: string, category?: string) => {
      const params = new URLSearchParams();
      if (q) params.set('q', q);
      if (category) params.set('category', category);
      return request<any[]>(`/supplements?${params.toString()}`);
    },
    get: (id: number) => request<any>(`/supplements/${id}`),
  },

  // AI
  ai: {
    coachChat: (message: string, history: any[]) => request<any>('/ai/coach', {
      method: 'POST',
      body: JSON.stringify({ message, conversation_history: history }),
    }),
    generateDiet: (days: number = 7) => request<any>('/ai/diet-plan', {
      method: 'POST',
      body: JSON.stringify({ days }),
    }),
    generateWorkout: (splitType?: string, daysPerWeek: number = 4) => request<any>('/ai/workout-plan', {
      method: 'POST',
      body: JSON.stringify({ split_type: splitType, days_per_week: daysPerWeek }),
    }),
  },

  // Subscriptions
  payments: {
    createCheckout: (planType: 'premium' | 'pro') => request<any>('/payments/checkout-session', {
      method: 'POST',
      body: JSON.stringify({ plan_type: planType }),
    }),
    getSubscription: () => request<any>('/payments/me'),
  },

  // Admin
  admin: {
    stats: () => request<any>('/admin/stats'),
    users: () => request<any[]>('/admin/users'),
    setAdminRole: (userId: number, isAdmin: boolean) => request<any>(`/admin/users/${userId}/role?is_admin=${isAdmin}`, {
      method: 'PUT',
    }),
    deleteUser: (userId: number) => request<any>(`/admin/users/${userId}`, { method: 'DELETE' }),
    createGlobalFood: (body: any) => request<any>('/admin/foods', { method: 'POST', body: JSON.stringify(body) }),
    deleteGlobalFood: (id: number) => request<any>(`/admin/foods/${id}`, { method: 'DELETE' }),
    createGlobalExercise: (body: any) => request<any>('/admin/exercises', { method: 'POST', body: JSON.stringify(body) }),
    deleteGlobalExercise: (id: number) => request<any>(`/admin/exercises/${id}`, { method: 'DELETE' }),
  },
};
