from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import (
    MemberHealthRecordCreate,
    MemberHealthRecordUpdate,
    MemberHealthRecordResponse,
    MemberWithHealthResponse,
    TrainingSafetyChecklistCreate,
    TrainingSafetyChecklistUpdate,
    TrainingSafetyChecklistResponse,
    EmergencyIncidentCreate,
    EmergencyIncidentUpdate,
    EmergencyIncidentResponse,
    RiskMemberCreate,
    RiskMemberUpdate,
    RiskMemberResponse,
    RiskAssessmentResponse,
    VenueHazardCreate,
    VenueHazardUpdate,
    VenueHazardResponse,
    SafetyStatOverview,
    IncidentTypeStat,
    SafetyStatItem,
    HighRiskMemberItem,
    HazardTypeStat,
    EmergencyResponseStat,
)
import services

router = APIRouter(prefix="/api/safety", tags=["safety"])


@router.get("/health-records", response_model=list[MemberHealthRecordResponse])
def get_health_records(member_id: int | None = None, db: Session = Depends(get_db)):
    return services.get_health_records(db, member_id)


@router.get("/health-records/{record_id}", response_model=MemberHealthRecordResponse)
def get_health_record(record_id: int, db: Session = Depends(get_db)):
    result = services.get_health_record(db, record_id)
    if not result:
        raise HTTPException(status_code=404, detail="Health record not found")
    return result


@router.post("/health-records", response_model=MemberHealthRecordResponse)
def create_health_record(data: MemberHealthRecordCreate, db: Session = Depends(get_db)):
    return services.create_health_record(db, data.model_dump())


@router.put("/health-records/{record_id}", response_model=MemberHealthRecordResponse)
def update_health_record(record_id: int, data: MemberHealthRecordUpdate, db: Session = Depends(get_db)):
    result = services.update_health_record(db, record_id, data.model_dump(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="Health record not found")
    return result


@router.delete("/health-records/{record_id}")
def delete_health_record(record_id: int, db: Session = Depends(get_db)):
    success = services.delete_health_record(db, record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Health record not found")
    return {"success": True}


@router.get("/members/{member_id}/health", response_model=MemberWithHealthResponse)
def get_member_with_health(member_id: int, db: Session = Depends(get_db)):
    result = services.get_member_with_health(db, member_id)
    if not result:
        raise HTTPException(status_code=404, detail="Member not found")
    return result


@router.get("/checklists", response_model=list[TrainingSafetyChecklistResponse])
def get_safety_checklists(rehearsal_id: int | None = None, db: Session = Depends(get_db)):
    return services.get_safety_checklists(db, rehearsal_id)


@router.get("/checklists/{checklist_id}", response_model=TrainingSafetyChecklistResponse)
def get_safety_checklist(checklist_id: int, db: Session = Depends(get_db)):
    result = services.get_safety_checklist(db, checklist_id)
    if not result:
        raise HTTPException(status_code=404, detail="Safety checklist not found")
    return result


@router.post("/checklists", response_model=TrainingSafetyChecklistResponse)
def create_safety_checklist(data: TrainingSafetyChecklistCreate, db: Session = Depends(get_db)):
    return services.create_safety_checklist(db, data.model_dump())


@router.put("/checklists/{checklist_id}", response_model=TrainingSafetyChecklistResponse)
def update_safety_checklist(checklist_id: int, data: TrainingSafetyChecklistUpdate, db: Session = Depends(get_db)):
    result = services.update_safety_checklist(db, checklist_id, data.model_dump(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="Safety checklist not found")
    return result


@router.delete("/checklists/{checklist_id}")
def delete_safety_checklist(checklist_id: int, db: Session = Depends(get_db)):
    success = services.delete_safety_checklist(db, checklist_id)
    if not success:
        raise HTTPException(status_code=404, detail="Safety checklist not found")
    return {"success": True}


@router.get("/checklists/{checklist_id}/risk-assessment", response_model=RiskAssessmentResponse)
def get_risk_assessment(checklist_id: int, db: Session = Depends(get_db)):
    result = services.assess_risks(db, checklist_id)
    if not result:
        raise HTTPException(status_code=404, detail="Safety checklist not found")
    return result


@router.get("/incidents", response_model=list[EmergencyIncidentResponse])
def get_emergency_incidents(checklist_id: int | None = None, member_id: int | None = None, db: Session = Depends(get_db)):
    return services.get_emergency_incidents(db, checklist_id, member_id)


@router.get("/incidents/{incident_id}", response_model=EmergencyIncidentResponse)
def get_emergency_incident(incident_id: int, db: Session = Depends(get_db)):
    result = services.get_emergency_incident(db, incident_id)
    if not result:
        raise HTTPException(status_code=404, detail="Emergency incident not found")
    return result


@router.post("/incidents", response_model=EmergencyIncidentResponse)
def create_emergency_incident(data: EmergencyIncidentCreate, db: Session = Depends(get_db)):
    return services.create_emergency_incident(db, data.model_dump())


@router.put("/incidents/{incident_id}", response_model=EmergencyIncidentResponse)
def update_emergency_incident(incident_id: int, data: EmergencyIncidentUpdate, db: Session = Depends(get_db)):
    result = services.update_emergency_incident(db, incident_id, data.model_dump(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="Emergency incident not found")
    return result


@router.post("/incidents/{incident_id}/resolve", response_model=EmergencyIncidentResponse)
def resolve_emergency_incident(incident_id: int, db: Session = Depends(get_db)):
    result = services.resolve_emergency_incident(db, incident_id)
    if not result:
        raise HTTPException(status_code=404, detail="Emergency incident not found")
    return result


@router.get("/risk-members", response_model=list[RiskMemberResponse])
def get_risk_members(checklist_id: int | None = None, member_id: int | None = None, db: Session = Depends(get_db)):
    return services.get_risk_members(db, checklist_id, member_id)


@router.get("/risk-members/{risk_member_id}", response_model=RiskMemberResponse)
def get_risk_member(risk_member_id: int, db: Session = Depends(get_db)):
    result = services.get_risk_member(db, risk_member_id)
    if not result:
        raise HTTPException(status_code=404, detail="Risk member not found")
    return result


@router.post("/risk-members", response_model=RiskMemberResponse)
def create_risk_member(data: RiskMemberCreate, db: Session = Depends(get_db)):
    return services.create_risk_member(db, data.model_dump())


@router.put("/risk-members/{risk_member_id}", response_model=RiskMemberResponse)
def update_risk_member(risk_member_id: int, data: RiskMemberUpdate, db: Session = Depends(get_db)):
    result = services.update_risk_member(db, risk_member_id, data.model_dump(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="Risk member not found")
    return result


@router.get("/hazards", response_model=list[VenueHazardResponse])
def get_venue_hazards(rehearsal_id: int | None = None, unresolved_only: bool = False, db: Session = Depends(get_db)):
    return services.get_venue_hazards(db, rehearsal_id, unresolved_only)


@router.get("/hazards/{hazard_id}", response_model=VenueHazardResponse)
def get_venue_hazard(hazard_id: int, db: Session = Depends(get_db)):
    result = services.get_venue_hazard(db, hazard_id)
    if not result:
        raise HTTPException(status_code=404, detail="Venue hazard not found")
    return result


@router.post("/hazards", response_model=VenueHazardResponse)
def create_venue_hazard(data: VenueHazardCreate, db: Session = Depends(get_db)):
    return services.create_venue_hazard(db, data.model_dump())


@router.put("/hazards/{hazard_id}", response_model=VenueHazardResponse)
def update_venue_hazard(hazard_id: int, data: VenueHazardUpdate, db: Session = Depends(get_db)):
    result = services.update_venue_hazard(db, hazard_id, data.model_dump(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="Venue hazard not found")
    return result


@router.post("/hazards/{hazard_id}/resolve", response_model=VenueHazardResponse)
def resolve_venue_hazard(hazard_id: int, db: Session = Depends(get_db)):
    result = services.resolve_venue_hazard(db, hazard_id)
    if not result:
        raise HTTPException(status_code=404, detail="Venue hazard not found")
    return result


@router.get("/stats/overview", response_model=SafetyStatOverview)
def get_safety_overview_stats(db: Session = Depends(get_db)):
    return services.get_safety_overview_stats(db)


@router.get("/stats/incident-types", response_model=list[IncidentTypeStat])
def get_incident_type_stats(db: Session = Depends(get_db)):
    return services.get_incident_type_stats(db)


@router.get("/stats/rehearsals", response_model=list[SafetyStatItem])
def get_rehearsal_safety_stats(db: Session = Depends(get_db)):
    return services.get_rehearsal_safety_stats(db)


@router.get("/stats/high-risk-members", response_model=list[HighRiskMemberItem])
def get_high_risk_members_stats(db: Session = Depends(get_db)):
    return services.get_high_risk_members_stats(db)


@router.get("/stats/hazard-types", response_model=list[HazardTypeStat])
def get_hazard_type_stats(db: Session = Depends(get_db)):
    return services.get_hazard_type_stats(db)


@router.get("/stats/emergency-response", response_model=EmergencyResponseStat)
def get_emergency_response_stats(db: Session = Depends(get_db)):
    return services.get_emergency_response_stats(db)
