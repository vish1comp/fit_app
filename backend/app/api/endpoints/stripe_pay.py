from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
import stripe
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, Subscription
from app.schemas.schemas import CheckoutSessionCreate, SubscriptionResponse
from app.core.config import settings
from datetime import datetime

router = APIRouter(prefix="/payments", tags=["Payments"])

stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/checkout-session")
def create_checkout_session(
    checkout_in: CheckoutSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Retrieve Price ID based on choice
    price_id = (
        settings.STRIPE_PREMIUM_PRICE_ID
        if checkout_in.plan_type == "premium"
        else settings.STRIPE_PRO_PRICE_ID
    )

    # Get subscription
    sub = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    customer_id = sub.stripe_customer_id if sub else None

    # Create customer if doesn't exist
    if not customer_id:
        customer = stripe.Customer.create(
            email=current_user.email,
            name=current_user.name,
            metadata={"user_id": current_user.id}
        )
        customer_id = customer.id
        if sub:
            sub.stripe_customer_id = customer_id
            db.commit()

    try:
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=f"{settings.FRONTEND_URL}/dashboard?session_id={{CHECKOUT_SESSION_ID}}&status=success",
            cancel_url=f"{settings.FRONTEND_URL}/profile?status=cancel",
            metadata={
                "user_id": current_user.id,
                "plan_type": checkout_in.plan_type.value
            }
        )
        return {"session_url": session.url}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: Session = Depends(get_db)
):
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        raise HTTPException(status_code=400, detail="Invalid Stripe signature.")

    event_type = event["type"]
    
    # Process subscription success / updates
    if event_type in ["checkout.session.completed", "customer.subscription.created", "customer.subscription.updated"]:
        session = event["data"]["object"]
        
        # Depending on session vs subscription event, parse customer & plan
        customer_id = session.get("customer")
        subscription_id = session.get("subscription") or session.get("id")
        
        # Fetch actual subscription to check period end
        try:
            stripe_sub = stripe.Subscription.retrieve(subscription_id)
            current_period_end = datetime.fromtimestamp(stripe_sub.current_period_end)
            
            # Find matching price id to map plan_type
            plan_type = "free"
            price_id = stripe_sub["items"]["data"][0]["price"]["id"]
            if price_id == settings.STRIPE_PREMIUM_PRICE_ID:
                plan_type = "premium"
            elif price_id == settings.STRIPE_PRO_PRICE_ID:
                plan_type = "pro"
            
            # Update Database
            db_sub = db.query(Subscription).filter(
                (Subscription.stripe_customer_id == customer_id) | 
                (Subscription.stripe_subscription_id == subscription_id)
            ).first()
            
            if db_sub:
                db_sub.stripe_subscription_id = subscription_id
                db_sub.stripe_customer_id = customer_id
                db_sub.plan_type = plan_type
                db_sub.status = stripe_sub.status
                db_sub.current_period_end = current_period_end
                db.commit()
        except stripe.error.StripeError:
            pass

    elif event_type == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        sub_id = subscription.get("id")
        
        db_sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == sub_id).first()
        if db_sub:
            db_sub.plan_type = "free"
            db_sub.status = "canceled"
            db_sub.current_period_end = None
            db.commit()

    return {"status": "success"}


@router.get("/me", response_model=SubscriptionResponse)
def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sub = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    if not sub:
        # Create default
        sub = Subscription(user_id=current_user.id, plan_type="free", status="active")
        db.add(sub)
        db.commit()
        db.refresh(sub)
    return sub
