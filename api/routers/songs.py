from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Song
from schemas import SongCreate, SongUpdate, SongResponse

router = APIRouter(prefix="/api/songs", tags=["songs"])


@router.post("", response_model=SongResponse)
def create_song(data: SongCreate, db: Session = Depends(get_db)):
    song = Song(**data.model_dump())
    db.add(song)
    db.commit()
    db.refresh(song)
    return song


@router.get("", response_model=list[SongResponse])
def list_songs(db: Session = Depends(get_db)):
    return db.query(Song).order_by(Song.performance_order).all()


@router.get("/{song_id}", response_model=SongResponse)
def get_song(song_id: int, db: Session = Depends(get_db)):
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song


@router.put("/{song_id}", response_model=SongResponse)
def update_song(song_id: int, data: SongUpdate, db: Session = Depends(get_db)):
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(song, key, value)
    db.commit()
    db.refresh(song)
    return song


@router.delete("/{song_id}")
def delete_song(song_id: int, db: Session = Depends(get_db)):
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    db.delete(song)
    db.commit()
    return {"detail": "Deleted"}
