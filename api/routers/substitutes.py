from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Attendance, SubstituteAssignment
from schemas import (
    AttendanceCreate, AttendanceResponse,
    SubstituteAssignCreate, SubstituteAssignResponse,
    SubstitutePriorityUpdate, SubstituteRecommendResponse,
)
import services

router = APIRouter(prefix="/api/substitutes", tags=["substitutes"])


@router.get("/attendance", response_model=list[AttendanceResponse])
def list_attendance(song_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Attendance)
    if song_id:
        query = query.filter(Attendance.song_id == song_id)
    return query.all()


@router.post("/attendance", response_model=AttendanceResponse)
def mark_attendance(data: AttendanceCreate, db: Session = Depends(get_db)):
    existing = db.query(Attendance).filter(
        Attendance.member_id == data.member_id,
        Attendance.song_id == data.song_id,
        Attendance.date == data.date,
    ).first()
    if existing:
        existing.status = data.status
        db.commit()
        db.refresh(existing)
        return existing
    attendance = Attendance(**data.model_dump())
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


@router.get("/recommend", response_model=list[SubstituteRecommendResponse])
def recommend_substitute(song_id: int, absent_member_id: int, db: Session = Depends(get_db)):
    results = services.recommend_substitutes(db, song_id, absent_member_id)
    return results


@router.post("/assign", response_model=SubstituteAssignResponse)
def assign_substitute(data: SubstituteAssignCreate, db: Session = Depends(get_db)):
    assignment = SubstituteAssignment(**data.model_dump())
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.get("/{song_id}", response_model=list[SubstituteAssignResponse])
def get_substitute_assignments(song_id: int, db: Session = Depends(get_db)):
    return db.query(SubstituteAssignment).filter(SubstituteAssignment.song_id == song_id).all()


@router.put("/{assignment_id}/priority", response_model=SubstituteAssignResponse)
def update_priority(assignment_id: int, data: SubstitutePriorityUpdate, db: Session = Depends(get_db)):
    assignment = db.query(SubstituteAssignment).filter(SubstituteAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    assignment.priority = data.priority
    db.commit()
    db.refresh(assignment)
    return assignment
