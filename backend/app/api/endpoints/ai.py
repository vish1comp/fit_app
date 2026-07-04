from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, Subscription
from app.schemas.schemas import AIChat, AIChatResponse, MealPlanRequest, WorkoutPlanRequest
from app.services import ai_service

router = APIRouter(prefix="/ai", tags=["AI Engine"])


def _check_premium_or_pro(user: User):
    """Enforces Premium/Pro subscription checks."""
    sub = user.subscription
    if not sub or sub.plan_type not in ["premium", "pro"]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="This is a Premium feature. Please upgrade your subscription to access.",
        )


@router.post("/coach", response_model=AIChatResponse)
async def ai_coach_chat(
    chat_in: AIChat,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Free Tier Limit: Cap history length or question count
    sub = current_user.subscription
    is_premium = sub and sub.plan_type in ["premium", "pro"]
    
    # Simple check: if not premium, check total chat history size
    user_questions = [h for h in chat_in.conversation_history if h.get("role") == "user"]
    if not is_premium and len(user_questions) >= 5:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Free plan is limited to 5 AI Coach questions. Upgrade to Premium for unlimited coaching!",
        )

    # Assemble user context for personalization
    user_context = {
        "name": current_user.name,
        "age": current_user.age,
        "gender": current_user.gender,
        "height_cm": current_user.height_cm,
        "weight_kg": current_user.weight_kg,
        "fitness_goal": current_user.fitness_goal,
        "activity_level": current_user.activity_level,
        "dietary_preference": current_user.dietary_preference,
    }

    reply, updated_history = await ai_service.get_ai_chat_response(
        message=chat_in.message,
        conversation_history=chat_in.conversation_history,
        user_context=user_context
    )

    return AIChatResponse(reply=reply, conversation_history=updated_history)


@router.post("/diet-plan")
async def generate_diet_plan(
    request: MealPlanRequest,
    current_user: User = Depends(get_current_user),
):
    _check_premium_or_pro(current_user)

    user_context = {
        "name": current_user.name,
        "age": current_user.age,
        "gender": current_user.gender,
        "height_cm": current_user.height_cm,
        "weight_kg": current_user.weight_kg,
        "fitness_goal": current_user.fitness_goal,
        "activity_level": current_user.activity_level,
        "dietary_preference": current_user.dietary_preference,
    }

    plan = await ai_service.generate_meal_plan(user_context=user_context, days=request.days)
    return plan


@router.post("/workout-plan")
async def generate_workout_program(
    request: WorkoutPlanRequest,
    current_user: User = Depends(get_current_user),
):
    _check_premium_or_pro(current_user)

    user_context = {
        "name": current_user.name,
        "age": current_user.age,
        "gender": current_user.gender,
        "height_cm": current_user.height_cm,
        "weight_kg": current_user.weight_kg,
        "fitness_goal": current_user.fitness_goal,
        "activity_level": current_user.activity_level,
    }

    plan = await ai_service.generate_workout_plan(
        user_context=user_context,
        split_type=request.split_type,
        days_per_week=request.days_per_week
    )
    return plan
