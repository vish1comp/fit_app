from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, UserProgress
from app.schemas.schemas import UserUpdate, UserResponse, UserProgressCreate, UserProgressResponse

router = APIRouter(prefix="/users", tags=["Users"])


def _calc_bmi(weight_kg: float, height_cm: float) -> float:
    if not height_cm or height_cm == 0:
        return 0.0
    h_m = height_cm / 100
    return round(weight_kg / (h_m ** 2), 1)


def _calc_bmr(user: User) -> float:
    if not all([user.weight_kg, user.height_cm, user.age]):
        return 0.0
    if user.gender == "male":
        return round(10 * user.weight_kg + 6.25 * user.height_cm - 5 * user.age + 5, 1)
    return round(10 * user.weight_kg + 6.25 * user.height_cm - 5 * user.age - 161, 1)


def _calc_body_fat(user: User) -> Optional[float]:
    """Navy method estimate (rough). Requires measurements."""
    if not all([user.weight_kg, user.height_cm, user.age]):
        return None
    bmi = _calc_bmi(user.weight_kg, user.height_cm)
    if user.gender == "male":
        bf = (1.20 * bmi) + (0.23 * (user.age or 25)) - 16.2
    else:
        bf = (1.20 * bmi) + (0.23 * (user.age or 25)) - 5.4
    return round(max(bf, 3.0), 1)


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_my_profile(
    update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    for field, value in update.model_dump(exclude_none=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me/stats")
def get_my_stats(current_user: User = Depends(get_current_user)):
    bmi = _calc_bmi(current_user.weight_kg or 0, current_user.height_cm or 0)
    bmr = _calc_bmr(current_user)
    bf = _calc_body_fat(current_user)

    multipliers = {
        "sedentary": 1.2, "lightly_active": 1.375, "moderately_active": 1.55,
        "very_active": 1.725, "extra_active": 1.9
    }
    tdee = round(bmr * multipliers.get(current_user.activity_level or "moderately_active", 1.55), 1)

    if current_user.fitness_goal == "fat_loss":
        target_calories = tdee - 500
    elif current_user.fitness_goal in ["muscle_building", "weight_gain"]:
        target_calories = tdee + 300
    else:
        target_calories = tdee

    weight = current_user.weight_kg or 70
    protein_g = round(weight * (2.0 if current_user.fitness_goal in ["muscle_building", "strength"] else 1.6))
    fat_g = round(target_calories * 0.25 / 9)
    carbs_g = round((target_calories - protein_g * 4 - fat_g * 9) / 4)

    return {
        "bmi": bmi,
        "bmi_category": (
            "Underweight" if bmi < 18.5 else
            "Normal weight" if bmi < 25 else
            "Overweight" if bmi < 30 else
            "Obese"
        ),
        "bmr": bmr,
        "tdee": tdee,
        "body_fat_estimate": bf,
        "target_calories": int(target_calories),
        "macros": {
            "protein_g": protein_g,
            "carbs_g": carbs_g,
            "fat_g": fat_g,
        },
        "water_ml": int(weight * 35),  # 35ml per kg
    }


# --- Progress Tracking ---
@router.post("/me/progress", response_model=UserProgressResponse, status_code=201)
def log_progress(
    entry: UserProgressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    progress = UserProgress(user_id=current_user.id, **entry.model_dump())
    db.add(progress)
    db.commit()
    db.refresh(progress)
    return progress


@router.get("/me/progress", response_model=List[UserProgressResponse])
def get_progress(
    limit: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(UserProgress)
        .filter(UserProgress.user_id == current_user.id)
        .order_by(UserProgress.date.desc())
        .limit(limit)
        .all()
    )
