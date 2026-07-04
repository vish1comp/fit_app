from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Date,
    Text, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Nullable for OAuth users
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)  # male | female | other
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    activity_level = Column(String, nullable=True)  # sedentary|lightly_active|moderately_active|very_active|extra_active
    fitness_goal = Column(String, nullable=True)  # muscle_building|fat_loss|strength|recomposition|weight_gain|general|athletic
    dietary_preference = Column(String, nullable=True)  # vegetarian|vegan|non_veg|keto|high_protein|indian|mediterranean
    profile_picture_url = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    google_id = Column(String, nullable=True, unique=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    nutrition_logs = relationship("NutritionLog", back_populates="user", cascade="all, delete")
    workout_logs = relationship("WorkoutLog", back_populates="user", cascade="all, delete")
    progress_entries = relationship("UserProgress", back_populates="user", cascade="all, delete")
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete")


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    weight_kg = Column(Float, nullable=True)
    body_fat_percent = Column(Float, nullable=True)
    neck_cm = Column(Float, nullable=True)
    chest_cm = Column(Float, nullable=True)
    waist_cm = Column(Float, nullable=True)
    hips_cm = Column(Float, nullable=True)
    biceps_cm = Column(Float, nullable=True)
    thighs_cm = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

    user = relationship("User", back_populates="progress_entries")


class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    brand = Column(String, nullable=True)
    calories = Column(Float, default=0)
    protein = Column(Float, default=0)
    carbs = Column(Float, default=0)
    fat = Column(Float, default=0)
    fiber = Column(Float, default=0)
    sugar = Column(Float, default=0)
    sodium = Column(Float, default=0)
    vitamins = Column(String, nullable=True)
    serving_size = Column(String, default="100g")
    serving_size_g = Column(Float, default=100)
    barcode = Column(String, nullable=True, unique=True)
    is_admin_created = Column(Boolean, default=True)
    category = Column(String, nullable=True)  # protein|carb|fat|vegetable|fruit|dairy|supplement

    nutrition_logs = relationship("NutritionLog", back_populates="food_item")


class NutritionLog(Base):
    __tablename__ = "nutrition_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    food_item_id = Column(Integer, ForeignKey("food_items.id"), nullable=True)
    date = Column(Date, nullable=False)
    meal_type = Column(String, nullable=False)  # breakfast|lunch|dinner|snacks
    food_name = Column(String, nullable=False)
    serving_size_g = Column(Float, default=100)
    servings = Column(Float, default=1)
    calories = Column(Float, default=0)
    protein = Column(Float, default=0)
    carbs = Column(Float, default=0)
    fat = Column(Float, default=0)
    fiber = Column(Float, default=0)
    sugar = Column(Float, default=0)
    sodium = Column(Float, default=0)
    logged_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="nutrition_logs")
    food_item = relationship("FoodItem", back_populates="nutrition_logs")


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    muscle_group = Column(String, nullable=False)  # chest|back|shoulders|legs|arms|core|cardio
    secondary_muscles = Column(String, nullable=True)
    difficulty = Column(String, nullable=False)  # beginner|intermediate|advanced
    equipment = Column(String, nullable=True)  # barbell|dumbbell|machine|bodyweight|cable|kettlebell
    video_url = Column(String, nullable=True)
    instructions = Column(Text, nullable=True)
    common_mistakes = Column(Text, nullable=True)
    tips = Column(Text, nullable=True)

    workout_sets = relationship("WorkoutSet", back_populates="exercise")


class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    name = Column(String, nullable=False)
    duration_seconds = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="workout_logs")
    sets = relationship("WorkoutSet", back_populates="workout_log", cascade="all, delete")


class WorkoutSet(Base):
    __tablename__ = "workout_sets"

    id = Column(Integer, primary_key=True, index=True)
    workout_log_id = Column(Integer, ForeignKey("workout_logs.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    set_number = Column(Integer, default=1)
    weight_kg = Column(Float, default=0)
    reps = Column(Integer, default=0)
    rpe = Column(Integer, nullable=True)  # Rate of Perceived Exertion 1-10
    is_warmup = Column(Boolean, default=False)
    is_pr = Column(Boolean, default=False)

    workout_log = relationship("WorkoutLog", back_populates="sets")
    exercise = relationship("Exercise", back_populates="workout_sets")


class Supplement(Base):
    __tablename__ = "supplements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, nullable=True)  # protein|creatine|pre-workout|recovery|vitamins|minerals|fat-burner
    description = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)
    side_effects = Column(Text, nullable=True)
    dosage = Column(Text, nullable=True)
    timing = Column(Text, nullable=True)
    warnings = Column(Text, nullable=True)
    scientific_evidence = Column(Text, nullable=True)
    evidence_rating = Column(String, nullable=True)  # strong|moderate|limited|insufficient
    references_json = Column(JSON, nullable=True)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    stripe_customer_id = Column(String, unique=True, nullable=True)
    stripe_subscription_id = Column(String, unique=True, nullable=True)
    plan_type = Column(String, default="free")  # free|premium|pro
    status = Column(String, default="active")   # active|canceled|past_due|trialing
    current_period_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="subscription")
