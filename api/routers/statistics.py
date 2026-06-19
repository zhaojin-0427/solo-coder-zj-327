from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import (
    OverviewResponse, RehearsalCountItem,
    SubstituteRateItem, ErrorPositionItem, AttendanceItem,
)
import services

router = APIRouter(prefix="/api/statistics", tags=["statistics"])


@router.get("/overview", response_model=OverviewResponse)
def get_overview(db: Session = Depends(get_db)):
    return services.get_overview(db)


@router.get("/rehearsal-counts", response_model=list[RehearsalCountItem])
def get_rehearsal_counts(db: Session = Depends(get_db)):
    return services.get_rehearsal_counts(db)


@router.get("/substitute-rates", response_model=list[SubstituteRateItem])
def get_substitute_rates(db: Session = Depends(get_db)):
    return services.get_substitute_rates(db)


@router.get("/error-positions", response_model=list[ErrorPositionItem])
def get_error_positions(db: Session = Depends(get_db)):
    return services.get_error_positions(db)


@router.get("/attendance", response_model=list[AttendanceItem])
def get_attendance_stats(db: Session = Depends(get_db)):
    return services.get_attendance_stats(db)
