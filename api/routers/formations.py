from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Formation
from schemas import FormationResponse, FormationUpdateRequest, FormationVersionResponse
import services

router = APIRouter(prefix="/api/formations", tags=["formations"])


@router.post("/generate/{song_id}", response_model=FormationResponse)
def generate_formation(song_id: int, db: Session = Depends(get_db)):
    formation = services.create_formation_draft(db, song_id)
    if not formation:
        raise HTTPException(status_code=404, detail="Song not found")
    return formation


@router.get("/{song_id}", response_model=FormationResponse)
def get_current_formation(song_id: int, db: Session = Depends(get_db)):
    formation = (
        db.query(Formation)
        .filter(Formation.song_id == song_id)
        .order_by(Formation.version.desc())
        .first()
    )
    if not formation:
        raise HTTPException(status_code=404, detail="Formation not found")
    return formation


@router.get("/by-id/{formation_id}", response_model=FormationResponse)
def get_formation_by_id(formation_id: int, db: Session = Depends(get_db)):
    formation = db.query(Formation).filter(Formation.id == formation_id).first()
    if not formation:
        raise HTTPException(status_code=404, detail="Formation not found")
    return formation


@router.get("/{song_id}/versions", response_model=list[FormationVersionResponse])
def get_formation_versions(song_id: int, db: Session = Depends(get_db)):
    return db.query(Formation).filter(Formation.song_id == song_id).order_by(Formation.version).all()


@router.put("/{formation_id}", response_model=FormationResponse)
def update_formation(formation_id: int, data: FormationUpdateRequest, db: Session = Depends(get_db)):
    formation = services.update_formation_positions(db, formation_id, data.positions)
    if not formation:
        raise HTTPException(status_code=400, detail="Formation not found or locked")
    return formation


@router.post("/{formation_id}/lock", response_model=FormationResponse)
def lock_formation(formation_id: int, db: Session = Depends(get_db)):
    formation = services.lock_formation(db, formation_id)
    if not formation:
        raise HTTPException(status_code=404, detail="Formation not found")
    return formation
