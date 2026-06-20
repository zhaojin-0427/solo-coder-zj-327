from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import (
    ChecklistGenerateRequest,
    ChecklistResponse,
    ChecklistSummaryResponse,
    CheckItemCreate,
    CheckItemUpdate,
    CheckItemResponse,
    CheckItemAbnormalDetail,
    PreCheckStatItem,
    MemberCompletionRankItem,
    FrequentAbnormalTypeItem,
)
import services

router = APIRouter(prefix="/api/checklists", tags=["checklists"])


@router.post("/performances/{performance_id}", response_model=ChecklistResponse)
def generate_checklist(performance_id: int, data: ChecklistGenerateRequest, db: Session = Depends(get_db)):
    result = services.generate_checklist(db, performance_id, data.model_dump())
    if not result:
        raise HTTPException(status_code=404, detail="Performance task not found or checklist already exists")
    return result


@router.get("/performances/{performance_id}", response_model=ChecklistResponse)
def get_checklist(performance_id: int, db: Session = Depends(get_db)):
    result = services.get_checklist_by_performance(db, performance_id)
    if not result:
        raise HTTPException(status_code=404, detail="Checklist not found")
    return result


@router.get("/performances/{performance_id}/summary", response_model=ChecklistSummaryResponse)
def get_summary(performance_id: int, db: Session = Depends(get_db)):
    result = services.get_checklist_summary(db, performance_id)
    if not result:
        raise HTTPException(status_code=404, detail="Checklist not found")
    return result


@router.get("/performances/{performance_id}/abnormal", response_model=list[CheckItemAbnormalDetail])
def get_abnormal(performance_id: int, db: Session = Depends(get_db)):
    return services.get_abnormal_items(db, performance_id)


@router.get("/performances/{performance_id}/member/{member_id}", response_model=list[CheckItemResponse])
def get_member_items(performance_id: int, member_id: int, db: Session = Depends(get_db)):
    return services.get_member_check_items(db, performance_id, member_id)


@router.put("/items/{item_id}", response_model=CheckItemResponse)
def update_item(item_id: int, data: CheckItemUpdate, db: Session = Depends(get_db)):
    result = services.update_check_item(db, item_id, data.model_dump(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="Check item not found")
    return result


@router.post("/performances/{performance_id}/items", response_model=CheckItemResponse)
def add_item(performance_id: int, data: CheckItemCreate, db: Session = Depends(get_db)):
    result = services.add_check_item(db, performance_id, data.model_dump())
    if not result:
        raise HTTPException(status_code=404, detail="Checklist not found")
    return result


@router.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    success = services.delete_check_item(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Check item not found")
    return {"success": True}


@router.get("/summaries", response_model=list[ChecklistSummaryResponse])
def get_all_summaries(db: Session = Depends(get_db)):
    return services.get_all_checklist_summaries(db)


@router.get("/stats/pre-check", response_model=list[PreCheckStatItem])
def get_pre_check_stats(db: Session = Depends(get_db)):
    return services.get_pre_check_stats(db)


@router.get("/stats/member-rank", response_model=list[MemberCompletionRankItem])
def get_member_rank(db: Session = Depends(get_db)):
    return services.get_member_completion_rank(db)


@router.get("/stats/abnormal-types", response_model=list[FrequentAbnormalTypeItem])
def get_abnormal_types(db: Session = Depends(get_db)):
    return services.get_frequent_abnormal_types(db)
