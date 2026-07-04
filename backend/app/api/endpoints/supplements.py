from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, Supplement
from app.schemas.schemas import SupplementResponse

router = APIRouter(prefix="/supplements", tags=["Supplements"])


@router.get("", response_model=List[SupplementResponse])
def list_supplements(
    q: Optional[str] = Query(None),
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Supplement)
    if q:
        query = query.filter(Supplement.name.ilike(f"%{q}%"))
    if category:
        query = query.filter(Supplement.category == category)
    return query.all()


@router.get("/{supplement_id}", response_model=SupplementResponse)
def get_supplement(
    supplement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    supp = db.query(Supplement).filter(Supplement.id == supplement_id).first()
    if not supp:
        raise HTTPException(status_code=404, detail="Supplement not found.")
    return supp
