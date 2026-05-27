from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.location import Location

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.post("/")
def create_location(
    name: str = Form(...),
    street_id: int = Form(...),
    db: Session = Depends(get_db)
):

    location = Location(
        name=name,
        street_id=street_id
    )

    db.add(location)
    db.commit()
    db.refresh(location)

    return {
        "message": "Location created successfully",
        "location": location
    }


@router.get("/")
def get_locations(db: Session = Depends(get_db)):
    return db.query(Location).all()


@router.get("/{location_id}")
def get_location(location_id: int, db: Session = Depends(get_db)):

    location = db.query(Location).filter(
        Location.location_id == location_id
    ).first()

    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    return location


@router.delete("/{location_id}")
def delete_location(location_id: int, db: Session = Depends(get_db)):

    location = db.query(Location).filter(
        Location.location_id == location_id
    ).first()

    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    db.delete(location)
    db.commit()

    return {"message": "Location deleted"}