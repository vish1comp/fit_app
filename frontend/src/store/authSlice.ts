import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UserProfile {
  id: number;
  email: string;
  name: string;
  age: number | null;
  gender: string | null;
  height_cm: number | null;
  weight_kg: number | null;
  activity_level: string | null;
  fitness_goal: string | null;
  dietary_preference: string | null;
  profile_picture_url: string | null;
  is_verified: boolean;
  is_admin: boolean;
}

interface UserStats {
  bmi: number;
  bmi_category: string;
  bmr: number;
  tdee: number;
  body_fat_estimate: number | null;
  target_calories: number;
  macros: {
    protein_g: number;
    carbs_g: number;
    fat_g: number;
  };
  water_ml: number;
}

interface AuthState {
  token: string | null;
  refreshToken: string | null;
  user: UserProfile | null;
  stats: UserStats | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  token: typeof window !== 'undefined' ? localStorage.getItem('token') : null,
  refreshToken: typeof window !== 'undefined' ? localStorage.getItem('refreshToken') : null,
  user: null,
  stats: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials(
      state,
      action: PayloadAction<{ token: string; refresh_token: string }>
    ) {
      state.token = action.payload.token;
      state.refreshToken = action.payload.refresh_token;
      state.isAuthenticated = true;
      if (typeof window !== 'undefined') {
        localStorage.setItem('token', action.payload.token);
        localStorage.setItem('refreshToken', action.payload.refresh_token);
      }
    },
    setUser(state, action: PayloadAction<UserProfile>) {
      state.user = action.payload;
      state.isAuthenticated = true;
    },
    setUserStats(state, action: PayloadAction<UserStats>) {
      state.stats = action.payload;
    },
    clearCredentials(state) {
      state.token = null;
      state.refreshToken = null;
      state.user = null;
      state.stats = null;
      state.isAuthenticated = false;
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
      }
    },
    setLoading(state, action: PayloadAction<boolean>) {
      state.isLoading = action.payload;
    },
    setError(state, action: PayloadAction<string | null>) {
      state.error = action.payload;
    },
  },
});

export const {
  setCredentials,
  setUser,
  setUserStats,
  clearCredentials,
  setLoading,
  setError,
} = authSlice.actions;

export default authSlice.reducer;
export type { UserProfile, UserStats };
