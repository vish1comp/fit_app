from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models.models import User, FoodItem, Exercise, Supplement, Subscription, WorkoutLog, NutritionLog
from app.schemas.schemas import AdminStats, UserResponse, FoodItemCreate, FoodItemResponse, ExerciseResponse

router = APIRouter(prefix="/admin", tags=["Admin Control Panel"])


@router.get("/stats", response_model=AdminStats)
def get_platform_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    total_users = db.query(User).count()
    verified_users = db.query(User).filter(User.is_verified == True).count()
    total_food_items = db.query(FoodItem).count()
    total_exercises = db.query(Exercise).count()
    total_workout_logs = db.query(WorkoutLog).count()
    
    premium_subscribers = db.query(Subscription).filter(Subscription.plan_type == "premium", Subscription.status == "active").count()
    pro_subscribers = db.query(Subscription).filter(Subscription.plan_type == "pro", Subscription.status == "active").count()

    return AdminStats(
        total_users=total_users,
        verified_users=verified_users,
        total_food_items=total_food_items,
        total_exercises=total_exercises,
        total_workout_logs=total_workout_logs,
        premium_subscribers=premium_subscribers,
        pro_subscribers=pro_subscribers,
    )


# --- Manage Users ---
@router.get("/users", response_model=List[UserResponse])
def list_users(
    limit: int = 50,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    return db.query(User).limit(limit).all()


@router.put("/users/{user_id}/role")
def set_admin_role(
    user_id: int,
    is_admin: bool,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.is_admin = is_admin
    db.commit()
    return {"message": f"User admin status set to {is_admin}"}


@router.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    db.delete(user)
    db.commit()


# --- Manage Foods ---
@router.post("/foods", response_model=FoodItemResponse, status_code=201)
def admin_create_food(
    food_in: FoodItemCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    food = FoodItem(**food_in.model_dump(), is_admin_created=True)
    db.add(food)
    db.commit()
    db.refresh(food)
    return food


@router.delete("/foods/{food_id}", status_code=204)
def delete_food(
    food_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    food = db.query(FoodItem).filter(FoodItem.id == food_id).first()
    if not food:
        raise HTTPException(status_code=404, detail="Food item not found.")
    db.delete(food)
    db.commit()


# --- Manage Exercises ---
@router.post("/exercises", response_model=ExerciseResponse, status_code=201)
def admin_create_exercise(
    name: str,
    muscle_group: str,
    difficulty: str,
    equipment: str = None,
    instructions: str = None,
    common_mistakes: str = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    ex = Exercise(
        name=name,
        muscle_group=muscle_group,
        difficulty=difficulty,
        equipment=equipment,
        instructions=instructions,
        common_mistakes=common_mistakes
    )
    db.add(ex)
    db.commit()
    db.refresh(ex)
    return ex


@router.delete("/exercises/{ex_id}", status_code=204)
def delete_exercise(
    ex_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    ex = db.query(Exercise).filter(Exercise.id == ex_id).first()
    if not ex:
        raise HTTPException(status_code=404, detail="Exercise not found.")
    db.delete(ex)
    db.commit()
