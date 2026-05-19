from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.city import City

router = APIRouter(prefix="/cities", tags=["Cities"])


@router.post("/")
def create_city(name: str, db: Session = Depends(get_db)):
    city = City(name=name)
    db.add(city)
    db.commit()
    db.refresh(city)
    return city


@router.get("/")
def get_cities(db: Session = Depends(get_db)):
    return db.query(City).all()