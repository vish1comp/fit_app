from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from datetime import date, timedelta
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, Exercise, WorkoutLog, WorkoutSet
from app.schemas.schemas import (
    ExerciseResponse, WorkoutLogCreate, WorkoutLogResponse, WorkoutSetCreate, WorkoutSetResponse
)

router = APIRouter(prefix="/workouts", tags=["Workouts"])


# --- Exercise Database ---
@router.get("/exercises", response_model=List[ExerciseResponse])
def list_exercises(
    muscle_group: Optional[str] = None,
    difficulty: Optional[str] = None,
    equipment: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Exercise)
    if muscle_group:
        query = query.filter(Exercise.muscle_group == muscle_group)
    if difficulty:
        query = query.filter(Exercise.difficulty == difficulty)
    if equipment:
        query = query.filter(Exercise.equipment.ilike(f"%{equipment}%"))
    if q:
        query = query.filter(Exercise.name.ilike(f"%{q}%"))
    return query.limit(limit).all()


@router.get("/exercises/{exercise_id}", response_model=ExerciseResponse)
def get_exercise(exercise_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ex = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not ex:
        raise HTTPException(status_code=404, detail="Exercise not found.")
    return ex


# --- Workout Logging ---
@router.post("/logs", response_model=WorkoutLogResponse, status_code=201)
def create_workout_log(
    log_in: WorkoutLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = WorkoutLog(
        user_id=current_user.id,
        date=log_in.date,
        name=log_in.name,
        duration_seconds=log_in.duration_seconds,
        notes=log_in.notes,
    )
    db.add(log)
    db.flush()  # Get log.id

    for set_data in log_in.sets:
        # Check PR
        best = (
            db.query(func.max(WorkoutSet.weight_kg))
            .join(WorkoutLog)
            .filter(
                WorkoutLog.user_id == current_user.id,
                WorkoutSet.exercise_id == set_data.exercise_id,
            )
            .scalar()
        )
        is_pr = set_data.weight_kg > (best or 0) and set_data.weight_kg > 0

        ws = WorkoutSet(
            workout_log_id=log.id,
            exercise_id=set_data.exercise_id,
            set_number=set_data.set_number,
            weight_kg=set_data.weight_kg,
            reps=set_data.reps,
            rpe=set_data.rpe,
            is_warmup=set_data.is_warmup,
            is_pr=is_pr,
        )
        db.add(ws)

    db.commit()
    db.refresh(log)
    return log


@router.get("/logs", response_model=List[WorkoutLogResponse])
def get_workout_logs(
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(WorkoutLog)
        .options(joinedload(WorkoutLog.sets).joinedload(WorkoutSet.exercise))
        .filter(WorkoutLog.user_id == current_user.id)
        .order_by(WorkoutLog.date.desc())
        .limit(limit)
        .all()
    )


@router.get("/logs/{log_id}", response_model=WorkoutLogResponse)
def get_workout_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = (
        db.query(WorkoutLog)
        .options(joinedload(WorkoutLog.sets).joinedload(WorkoutSet.exercise))
        .filter(WorkoutLog.id == log_id, WorkoutLog.user_id == current_user.id)
        .first()
    )
    if not log:
        raise HTTPException(status_code=404, detail="Workout log not found.")
    return log


@router.delete("/logs/{log_id}", status_code=204)
def delete_workout_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = db.query(WorkoutLog).filter(
        WorkoutLog.id == log_id, WorkoutLog.user_id == current_user.id
    ).first()
    if not log:
        raise HTTPException(status_code=404, detail="Workout log not found.")
    db.delete(log)
    db.commit()


# --- Analytics ---
@router.get("/analytics/volume")
def get_volume_analytics(
    exercise_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Weekly volume (sets × reps × weight) for the last 8 weeks."""
    today = date.today()
    eight_weeks_ago = today - timedelta(weeks=8)

    query = (
        db.query(
            WorkoutLog.date,
            func.sum(WorkoutSet.weight_kg * WorkoutSet.reps).label("volume"),
            func.count(WorkoutSet.id).label("total_sets"),
        )
        .join(WorkoutSet, WorkoutSet.workout_log_id == WorkoutLog.id)
        .filter(
            WorkoutLog.user_id == current_user.id,
            WorkoutLog.date >= eight_weeks_ago,
        )
    )
    if exercise_id:
        query = query.filter(WorkoutSet.exercise_id == exercise_id)

    results = query.group_by(WorkoutLog.date).order_by(WorkoutLog.date).all()
    return [{"date": str(r.date), "volume": round(r.volume or 0, 1), "total_sets": r.total_sets} for r in results]


@router.get("/analytics/prs")
def get_personal_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Best weight lifted per exercise."""
    results = (
        db.query(
            Exercise.name,
            Exercise.muscle_group,
            func.max(WorkoutSet.weight_kg).label("max_weight"),
            func.max(WorkoutSet.reps).label("max_reps"),
        )
        .join(WorkoutSet, WorkoutSet.exercise_id == Exercise.id)
        .join(WorkoutLog, WorkoutLog.id == WorkoutSet.workout_log_id)
        .filter(WorkoutLog.user_id == current_user.id)
        .group_by(Exercise.id, Exercise.name, Exercise.muscle_group)
        .all()
    )
    return [
        {"exercise": r.name, "muscle_group": r.muscle_group, "max_weight_kg": r.max_weight, "max_reps": r.max_reps}
        for r in results
    ]
