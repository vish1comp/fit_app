from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import date, datetime
from enum import Enum


# --- Enums ---
class ActivityLevel(str, Enum):
    sedentary = "sedentary"
    lightly_active = "lightly_active"
    moderately_active = "moderately_active"
    very_active = "very_active"
    extra_active = "extra_active"


class FitnessGoal(str, Enum):
    muscle_building = "muscle_building"
    fat_loss = "fat_loss"
    strength = "strength"
    recomposition = "recomposition"
    weight_gain = "weight_gain"
    general = "general"
    athletic = "athletic"


class MealType(str, Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snacks = "snacks"


class DietaryPreference(str, Enum):
    vegetarian = "vegetarian"
    vegan = "vegan"
    non_veg = "non_veg"
    keto = "keto"
    high_protein = "high_protein"
    indian = "indian"
    mediterranean = "mediterranean"


class PlanType(str, Enum):
    free = "free"
    premium = "premium"
    pro = "pro"


# --- Auth Schemas ---
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(min_length=1)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


# --- User Schemas ---
class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=10, le=120)
    gender: Optional[str] = None
    height_cm: Optional[float] = Field(None, ge=50, le=300)
    weight_kg: Optional[float] = Field(None, ge=20, le=500)
    activity_level: Optional[ActivityLevel] = None
    fitness_goal: Optional[FitnessGoal] = None
    dietary_preference: Optional[DietaryPreference] = None
    profile_picture_url: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    age: Optional[int]
    gender: Optional[str]
    height_cm: Optional[float]
    weight_kg: Optional[float]
    activity_level: Optional[str]
    fitness_goal: Optional[str]
    dietary_preference: Optional[str]
    profile_picture_url: Optional[str]
    is_verified: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- Progress Schemas ---
class UserProgressCreate(BaseModel):
    date: date
    weight_kg: Optional[float] = None
    body_fat_percent: Optional[float] = None
    neck_cm: Optional[float] = None
    chest_cm: Optional[float] = None
    waist_cm: Optional[float] = None
    hips_cm: Optional[float] = None
    biceps_cm: Optional[float] = None
    thighs_cm: Optional[float] = None
    notes: Optional[str] = None


class UserProgressResponse(UserProgressCreate):
    id: int
    user_id: int

    class Config:
        from_attributes = True


# --- Food / Nutrition Schemas ---
class FoodItemCreate(BaseModel):
    name: str
    brand: Optional[str] = None
    calories: float = 0
    protein: float = 0
    carbs: float = 0
    fat: float = 0
    fiber: float = 0
    sugar: float = 0
    sodium: float = 0
    vitamins: Optional[str] = None
    serving_size: str = "100g"
    serving_size_g: float = 100
    category: Optional[str] = None
    barcode: Optional[str] = None


class FoodItemResponse(FoodItemCreate):
    id: int
    is_admin_created: bool

    class Config:
        from_attributes = True


class NutritionLogCreate(BaseModel):
    food_item_id: Optional[int] = None
    date: date
    meal_type: MealType
    food_name: str
    serving_size_g: float = 100
    servings: float = 1
    calories: float = 0
    protein: float = 0
    carbs: float = 0
    fat: float = 0
    fiber: float = 0
    sugar: float = 0
    sodium: float = 0


class NutritionLogResponse(NutritionLogCreate):
    id: int
    user_id: int
    logged_at: datetime

    class Config:
        from_attributes = True


class DailySummary(BaseModel):
    date: date
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    total_fiber: float
    total_sodium: float
    logs: List[NutritionLogResponse]


# --- Exercise / Workout Schemas ---
class ExerciseResponse(BaseModel):
    id: int
    name: str
    muscle_group: str
    secondary_muscles: Optional[str]
    difficulty: str
    equipment: Optional[str]
    video_url: Optional[str]
    instructions: Optional[str]
    common_mistakes: Optional[str]
    tips: Optional[str]

    class Config:
        from_attributes = True


class WorkoutSetCreate(BaseModel):
    exercise_id: int
    set_number: int = 1
    weight_kg: float = 0
    reps: int = 0
    rpe: Optional[int] = Field(None, ge=1, le=10)
    is_warmup: bool = False


class WorkoutSetResponse(WorkoutSetCreate):
    id: int
    workout_log_id: int
    is_pr: bool
    exercise: Optional[ExerciseResponse] = None

    class Config:
        from_attributes = True


class WorkoutLogCreate(BaseModel):
    date: date
    name: str
    duration_seconds: Optional[int] = None
    notes: Optional[str] = None
    sets: List[WorkoutSetCreate] = []


class WorkoutLogResponse(BaseModel):
    id: int
    user_id: int
    date: date
    name: str
    duration_seconds: Optional[int]
    notes: Optional[str]
    created_at: datetime
    sets: List[WorkoutSetResponse] = []

    class Config:
        from_attributes = True


# --- Supplement Schemas ---
class SupplementResponse(BaseModel):
    id: int
    name: str
    category: Optional[str]
    description: Optional[str]
    benefits: Optional[str]
    side_effects: Optional[str]
    dosage: Optional[str]
    timing: Optional[str]
    warnings: Optional[str]
    scientific_evidence: Optional[str]
    evidence_rating: Optional[str]
    references_json: Optional[Any]

    class Config:
        from_attributes = True


# --- AI Schemas ---
class AIChat(BaseModel):
    message: str
    conversation_history: Optional[List[dict]] = []


class AIChatResponse(BaseModel):
    reply: str
    conversation_history: List[dict]


class MealPlanRequest(BaseModel):
    days: int = Field(7, ge=1, le=14)


class WorkoutPlanRequest(BaseModel):
    split_type: Optional[str] = None  # ppl|upper_lower|bro_split|full_body|hiit|5x5|powerlifting
    days_per_week: int = Field(4, ge=2, le=6)


# --- Subscription Schemas ---
class SubscriptionResponse(BaseModel):
    id: int
    plan_type: str
    status: str
    current_period_end: Optional[datetime]

    class Config:
        from_attributes = True


class CheckoutSessionCreate(BaseModel):
    plan_type: PlanType


# --- Admin Schemas ---
class AdminStats(BaseModel):
    total_users: int
    verified_users: int
    total_food_items: int
    total_exercises: int
    total_workout_logs: int
    premium_subscribers: int
    pro_subscribers: int
