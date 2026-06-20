from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import (
    PerformanceTaskCreate,
    PerformanceTaskUpdate,
    PerformanceTaskResponse,
    PerformanceTaskDetailResponse,
    PerformanceTaskWithSongDetailsResponse,
    PerformanceConfirmationUpdate,
    PerformanceConfirmationResponse,
)
import services

router = APIRouter(prefix="/api/performances", tags=["performances"])


@router.get("", response_model=list[PerformanceTaskResponse])
def list_performances(db: Session = Depends(get_db)):
    return services.get_performance_task_list(db)


@router.post("", response_model=PerformanceTaskResponse)
def create_performance(data: PerformanceTaskCreate, db: Session = Depends(get_db)):
    return services.create_performance_task(db, data.model_dump())


@router.get("/{task_id}", response_model=PerformanceTaskDetailResponse)
def get_performance(task_id: int, db: Session = Depends(get_db)):
    result = services.get_performance_task_detail(db, task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Performance task not found")
    return result


@router.get("/{task_id}/details", response_model=PerformanceTaskWithSongDetailsResponse)
def get_performance_with_song_details(task_id: int, db: Session = Depends(get_db)):
    result = services.get_performance_task_with_song_details(db, task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Performance task not found")
    return result


@router.put("/{task_id}", response_model=PerformanceTaskResponse)
def update_performance(task_id: int, data: PerformanceTaskUpdate, db: Session = Depends(get_db)):
    result = services.update_performance_task(db, task_id, data.model_dump(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="Performance task not found")
    return result


@router.delete("/{task_id}")
def delete_performance(task_id: int, db: Session = Depends(get_db)):
    success = services.delete_performance_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Performance task not found")
    return {"success": True}


@router.put("/{task_id}/confirmations/{member_id}", response_model=PerformanceConfirmationResponse)
def update_confirmation(
    task_id: int,
    member_id: int,
    data: PerformanceConfirmationUpdate,
    db: Session = Depends(get_db),
):
    result = services.update_performance_confirmation(db, task_id, member_id, data.model_dump())
    if not result:
        raise HTTPException(status_code=404, detail="Confirmation not found")
    return result


@router.post("/{task_id}/confirmations/{member_id}/phone-reminded", response_model=PerformanceConfirmationResponse)
def mark_phone_reminded(task_id: int, member_id: int, db: Session = Depends(get_db)):
    result = services.mark_phone_reminded(db, task_id, member_id)
    if not result:
        raise HTTPException(status_code=404, detail="Confirmation not found")
    return result
