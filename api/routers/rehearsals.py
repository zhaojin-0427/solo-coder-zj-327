from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Rehearsal, RehearsalError
from schemas import RehearsalCreate, RehearsalResponse, RehearsalDetailResponse, RehearsalErrorResponse

router = APIRouter(prefix="/api/rehearsals", tags=["rehearsals"])


@router.post("", response_model=RehearsalResponse)
def create_rehearsal(data: RehearsalCreate, db: Session = Depends(get_db)):
    errors_data = data.errors
    rehearsal_data = data.model_dump(exclude={"errors"})
    rehearsal = Rehearsal(**rehearsal_data)
    db.add(rehearsal)
    db.flush()

    for err in errors_data:
        db.add(RehearsalError(rehearsal_id=rehearsal.id, **err.model_dump()))

    db.commit()
    db.refresh(rehearsal)
    return rehearsal


@router.get("", response_model=list[RehearsalResponse])
def list_rehearsals(song_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Rehearsal)
    if song_id:
        query = query.filter(Rehearsal.song_id == song_id)
    return query.order_by(Rehearsal.date.desc()).all()


@router.get("/{rehearsal_id}", response_model=RehearsalDetailResponse)
def get_rehearsal(rehearsal_id: int, db: Session = Depends(get_db)):
    rehearsal = db.query(Rehearsal).filter(Rehearsal.id == rehearsal_id).first()
    if not rehearsal:
        raise HTTPException(status_code=404, detail="Rehearsal not found")
    errors = db.query(RehearsalError).filter(RehearsalError.rehearsal_id == rehearsal_id).all()
    return RehearsalDetailResponse(
        id=rehearsal.id,
        song_id=rehearsal.song_id,
        date=rehearsal.date,
        duration_minutes=rehearsal.duration_minutes,
        teacher_notes=rehearsal.teacher_notes,
        created_at=rehearsal.created_at,
        errors=[RehearsalErrorResponse.model_validate(e) for e in errors],
    )
