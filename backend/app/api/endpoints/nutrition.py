from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, timedelta
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, FoodItem, NutritionLog
from app.schemas.schemas import (
    FoodItemCreate, FoodItemResponse,
    NutritionLogCreate, NutritionLogResponse, DailySummary
)

router = APIRouter(prefix="/nutrition", tags=["Nutrition"])


# --- Food Database ---
@router.get("/foods", response_model=List[FoodItemResponse])
def search_foods(
    q: Optional[str] = Query(None, description="Search term"),
    category: Optional[str] = None,
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(FoodItem)
    if q:
        query = query.filter(FoodItem.name.ilike(f"%{q}%"))
    if category:
        query = query.filter(FoodItem.category == category)
    return query.limit(limit).all()


@router.get("/foods/{food_id}", response_model=FoodItemResponse)
def get_food(food_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    food = db.query(FoodItem).filter(FoodItem.id == food_id).first()
    if not food:
        raise HTTPException(status_code=404, detail="Food item not found.")
    return food


@router.get("/foods/barcode/{barcode}", response_model=FoodItemResponse)
def get_food_by_barcode(barcode: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    food = db.query(FoodItem).filter(FoodItem.barcode == barcode).first()
    if not food:
        raise HTTPException(status_code=404, detail="No food found with this barcode.")
    return food


@router.post("/foods", response_model=FoodItemResponse, status_code=201)
def create_custom_food(
    food_in: FoodItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    food = FoodItem(**food_in.model_dump(), is_admin_created=False)
    db.add(food)
    db.commit()
    db.refresh(food)
    return food


# --- Nutrition Logging ---
@router.post("/logs", response_model=NutritionLogResponse, status_code=201)
def log_food(
    log_in: NutritionLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # If food_item_id given, auto-calculate macros based on servings
    if log_in.food_item_id:
        food = db.query(FoodItem).filter(FoodItem.id == log_in.food_item_id).first()
        if food:
            ratio = (log_in.serving_size_g / food.serving_size_g) * log_in.servings
            log_in = log_in.model_copy(update={
                "food_name": food.name,
                "calories": round(food.calories * ratio, 1),
                "protein": round(food.protein * ratio, 1),
                "carbs": round(food.carbs * ratio, 1),
                "fat": round(food.fat * ratio, 1),
                "fiber": round(food.fiber * ratio, 1),
                "sugar": round(food.sugar * ratio, 1),
                "sodium": round(food.sodium * ratio, 1),
            })

    log = NutritionLog(user_id=current_user.id, **log_in.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/logs", response_model=List[NutritionLogResponse])
def get_logs(
    log_date: Optional[date] = Query(None),
    meal_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(NutritionLog).filter(NutritionLog.user_id == current_user.id)
    if log_date:
        query = query.filter(NutritionLog.date == log_date)
    if meal_type:
        query = query.filter(NutritionLog.meal_type == meal_type)
    return query.order_by(NutritionLog.logged_at.desc()).all()


@router.get("/logs/summary/{log_date}", response_model=DailySummary)
def get_daily_summary(
    log_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logs = (
        db.query(NutritionLog)
        .filter(NutritionLog.user_id == current_user.id, NutritionLog.date == log_date)
        .all()
    )
    return DailySummary(
        date=log_date,
        total_calories=round(sum(l.calories for l in logs), 1),
        total_protein=round(sum(l.protein for l in logs), 1),
        total_carbs=round(sum(l.carbs for l in logs), 1),
        total_fat=round(sum(l.fat for l in logs), 1),
        total_fiber=round(sum(l.fiber for l in logs), 1),
        total_sodium=round(sum(l.sodium for l in logs), 1),
        logs=logs,
    )


@router.get("/logs/weekly")
def get_weekly_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    seven_days_ago = today - timedelta(days=6)
    logs = (
        db.query(NutritionLog)
        .filter(
            NutritionLog.user_id == current_user.id,
            NutritionLog.date >= seven_days_ago,
            NutritionLog.date <= today
        )
        .all()
    )
    # Group by date
    by_date = {}
    for log in logs:
        d = str(log.date)
        if d not in by_date:
            by_date[d] = {"date": d, "calories": 0, "protein": 0, "carbs": 0, "fat": 0}
        by_date[d]["calories"] += log.calories
        by_date[d]["protein"] += log.protein
        by_date[d]["carbs"] += log.carbs
        by_date[d]["fat"] += log.fat

    # Fill missing days with zeros
    result = []
    for i in range(7):
        d = str(seven_days_ago + timedelta(days=i))
        result.append(by_date.get(d, {"date": d, "calories": 0, "protein": 0, "carbs": 0, "fat": 0}))
    return result


@router.delete("/logs/{log_id}", status_code=204)
def delete_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = db.query(NutritionLog).filter(
        NutritionLog.id == log_id, NutritionLog.user_id == current_user.id
    ).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log entry not found.")
    db.delete(log)
    db.commit()
