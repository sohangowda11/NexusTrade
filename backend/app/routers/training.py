from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.services.training_service import train_model, get_training_status

router = APIRouter(prefix="/api/training", tags=["training"])


@router.post("/train")
def trigger_training(db: Session = Depends(get_db)):
    return train_model(db)


@router.get("/status")
def training_status():
    return get_training_status()
