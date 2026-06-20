from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SongCreate(BaseModel):
    name: str
    beat_count: int
    formation_type: str
    performance_order: int = 0


class SongUpdate(BaseModel):
    name: Optional[str] = None
    beat_count: Optional[int] = None
    formation_type: Optional[str] = None
    performance_order: Optional[int] = None


class SongResponse(BaseModel):
    id: int
    name: str
    beat_count: int
    formation_type: str
    performance_order: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MemberCreate(BaseModel):
    name: str
    height_range: str
    phone: Optional[str] = None
    song_ids: list[int] = []
    substitute_positions: list[str] = []


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    height_range: Optional[str] = None
    phone: Optional[str] = None
    song_ids: Optional[list[int]] = None
    substitute_positions: Optional[list[str]] = None


class MemberResponse(BaseModel):
    id: int
    name: str
    height_range: str
    phone: Optional[str] = None
    song_ids: list[int] = []
    substitute_positions: list[str] = []
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MemberDetailResponse(MemberResponse):
    pass


class FormationPositionResponse(BaseModel):
    id: int
    position_id: str
    x: float
    y: float
    row_num: int
    col_num: int
    member_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class FormationResponse(BaseModel):
    id: int
    song_id: int
    version: int
    is_locked: bool
    created_at: Optional[datetime] = None
    positions: list[FormationPositionResponse] = []

    model_config = ConfigDict(from_attributes=True)


class FormationUpdateRequest(BaseModel):
    positions: list[FormationPositionUpdate]


class FormationPositionUpdate(BaseModel):
    id: int
    x: Optional[float] = None
    y: Optional[float] = None
    member_id: Optional[int] = None


class FormationVersionResponse(BaseModel):
    id: int
    version: int
    is_locked: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RehearsalCreate(BaseModel):
    song_id: int
    date: date
    duration_minutes: int = 60
    teacher_notes: Optional[str] = None
    errors: list["RehearsalErrorCreate"] = []


class RehearsalErrorCreate(BaseModel):
    position_id: str
    error_type: str
    beat_number: Optional[int] = None
    description: Optional[str] = None


class RehearsalErrorResponse(BaseModel):
    id: int
    position_id: str
    error_type: str
    beat_number: Optional[int] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RehearsalResponse(BaseModel):
    id: int
    song_id: int
    date: date
    duration_minutes: int
    teacher_notes: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RehearsalDetailResponse(RehearsalResponse):
    errors: list[RehearsalErrorResponse] = []


class AttendanceCreate(BaseModel):
    member_id: int
    song_id: int
    date: date
    status: str


class AttendanceResponse(BaseModel):
    id: int
    member_id: int
    song_id: int
    date: date
    status: str

    model_config = ConfigDict(from_attributes=True)


class SubstituteAssignCreate(BaseModel):
    song_id: int
    absent_member_id: int
    substitute_member_id: int
    position_id: str
    priority: int = 1


class SubstituteAssignResponse(BaseModel):
    id: int
    song_id: int
    absent_member_id: int
    substitute_member_id: int
    position_id: str
    priority: int

    model_config = ConfigDict(from_attributes=True)


class SubstitutePriorityUpdate(BaseModel):
    priority: int


class SubstituteRecommendResponse(BaseModel):
    member_id: int
    name: str
    matched_positions: list[str]
    priority: int


class OverviewResponse(BaseModel):
    total_songs: int
    total_members: int
    total_rehearsals: int
    total_formations: int


class RehearsalCountItem(BaseModel):
    song_id: int
    song_name: str
    count: int


class SubstituteRateItem(BaseModel):
    song_id: int
    song_name: str
    total_assignments: int
    total_rehearsals: int
    rate: float


class ErrorPositionItem(BaseModel):
    position_id: str
    count: int


class AttendanceItem(BaseModel):
    member_id: int
    member_name: str
    present_count: int
    absent_count: int
    attendance_rate: float


class PerformanceSongTaskCreate(BaseModel):
    song_id: int
    formation_id: Optional[int] = None
    performance_order: int = 0


class PerformanceSongTaskResponse(BaseModel):
    id: int
    song_id: int
    song_name: str
    formation_id: Optional[int] = None
    formation_version: Optional[int] = None
    performance_order: int

    model_config = ConfigDict(from_attributes=True)


class PerformanceTaskCreate(BaseModel):
    name: str
    location: str
    meeting_time: datetime
    start_time: datetime
    costume_requirements: Optional[str] = None
    notes: Optional[str] = None
    song_tasks: list[PerformanceSongTaskCreate] = []
    member_ids: list[int] = []


class PerformanceTaskUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    meeting_time: Optional[datetime] = None
    start_time: Optional[datetime] = None
    costume_requirements: Optional[str] = None
    notes: Optional[str] = None
    song_tasks: Optional[list[PerformanceSongTaskCreate]] = None
    member_ids: Optional[list[int]] = None


class PerformanceTaskResponse(BaseModel):
    id: int
    name: str
    location: str
    meeting_time: datetime
    start_time: datetime
    costume_requirements: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    song_tasks: list[PerformanceSongTaskResponse] = []
    total_members: int = 0
    confirmed_count: int = 0
    unconfirmed_count: int = 0
    leave_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class PerformanceTaskDetailResponse(PerformanceTaskResponse):
    confirmations: list["PerformanceConfirmationResponse"] = []


class PerformanceConfirmationCreate(BaseModel):
    performance_id: int
    member_id: int
    status: str
    transport_mode: Optional[str] = None
    remark: Optional[str] = None


class PerformanceConfirmationUpdate(BaseModel):
    status: Optional[str] = None
    transport_mode: Optional[str] = None
    remark: Optional[str] = None
    phone_reminded: Optional[bool] = None


class PerformanceConfirmationResponse(BaseModel):
    id: int
    performance_id: int
    member_id: int
    member_name: str
    member_phone: Optional[str] = None
    status: str
    transport_mode: Optional[str] = None
    remark: Optional[str] = None
    phone_reminded: bool
    confirmed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SongPerformanceDetail(BaseModel):
    song_id: int
    song_name: str
    formation_id: Optional[int] = None
    formation_version: Optional[int] = None
    total_positions: int = 0
    leave_members: list[dict] = []
    confirmed_substitutes: list[dict] = []
    gap_positions: list[str] = []


class PerformanceTaskWithSongDetailsResponse(PerformanceTaskDetailResponse):
    song_details: list[SongPerformanceDetail] = []


class PerformanceConfirmationStatItem(BaseModel):
    performance_id: int
    performance_name: str
    performance_date: str
    total_members: int
    confirmed_count: int
    unconfirmed_count: int
    leave_count: int
    confirmation_rate: float
    phone_reminded_count: int
    phone_reminder_rate: float


class CheckItemCreate(BaseModel):
    song_id: int
    category: str
    item_name: str
    responsible_member_id: Optional[int] = None
    position_id: Optional[str] = None
    deadline: Optional[datetime] = None


class CheckItemUpdate(BaseModel):
    status: Optional[str] = None
    abnormal_description: Optional[str] = None
    photo_url: Optional[str] = None


class ChecklistGenerateRequest(BaseModel):
    items: list[CheckItemCreate] = []


class CheckItemResponse(BaseModel):
    id: int
    checklist_id: int
    song_id: int
    song_name: str
    category: str
    item_name: str
    responsible_member_id: Optional[int] = None
    responsible_member_name: Optional[str] = None
    position_id: Optional[str] = None
    deadline: Optional[datetime] = None
    status: str
    abnormal_description: Optional[str] = None
    photo_url: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ChecklistResponse(BaseModel):
    id: int
    performance_id: int
    created_at: Optional[datetime] = None
    items: list[CheckItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ChecklistSummaryResponse(BaseModel):
    performance_id: int
    performance_name: str
    total_items: int
    not_started_count: int
    in_progress_count: int
    abnormal_count: int
    completed_count: int
    completion_rate: float


class CheckItemAbnormalDetail(BaseModel):
    item_id: int
    item_name: str
    category: str
    song_id: int
    song_name: str
    responsible_member_id: Optional[int] = None
    responsible_member_name: Optional[str] = None
    position_id: Optional[str] = None
    abnormal_description: Optional[str] = None


class PreCheckStatItem(BaseModel):
    performance_id: int
    performance_name: str
    performance_date: str
    total_items: int
    completed_count: int
    abnormal_count: int
    completion_rate: float


class MemberCompletionRankItem(BaseModel):
    member_id: int
    member_name: str
    total_assigned: int
    completed_count: int
    abnormal_count: int
    completion_rate: float


class FrequentAbnormalTypeItem(BaseModel):
    category: str
    count: int


class MemberHealthRecordCreate(BaseModel):
    member_id: int
    record_date: date
    condition_type: str
    description: Optional[str] = None
    is_chronic: bool = False
    needs_accommodation: bool = False
    accommodation_notes: Optional[str] = None


class MemberHealthRecordUpdate(BaseModel):
    condition_type: Optional[str] = None
    description: Optional[str] = None
    is_chronic: Optional[bool] = None
    needs_accommodation: Optional[bool] = None
    accommodation_notes: Optional[str] = None


class MemberHealthRecordResponse(BaseModel):
    id: int
    member_id: int
    member_name: Optional[str] = None
    record_date: date
    condition_type: str
    description: Optional[str] = None
    is_chronic: bool
    needs_accommodation: bool
    accommodation_notes: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MemberWithHealthResponse(MemberResponse):
    age: Optional[int] = None
    emergency_contact: Optional[str] = None
    health_records: list[MemberHealthRecordResponse] = []


class TrainingSafetyChecklistCreate(BaseModel):
    rehearsal_id: int
    ground_condition: str
    ground_notes: Optional[str] = None
    audio_cables_arranged: bool = False
    audio_cables_notes: Optional[str] = None
    members_illness_reported: bool = False
    illness_notes: Optional[str] = None
    weather_temperature: Optional[float] = None
    weather_condition: Optional[str] = None
    weather_notes: Optional[str] = None
    drinking_water_provided: bool = False
    rest_schedule_arranged: bool = False
    rest_notes: Optional[str] = None
    high_risk_moves_reminded: bool = False
    high_risk_moves_notes: Optional[str] = None
    created_by: Optional[int] = None


class TrainingSafetyChecklistUpdate(BaseModel):
    ground_condition: Optional[str] = None
    ground_notes: Optional[str] = None
    audio_cables_arranged: Optional[bool] = None
    audio_cables_notes: Optional[str] = None
    members_illness_reported: Optional[bool] = None
    illness_notes: Optional[str] = None
    weather_temperature: Optional[float] = None
    weather_condition: Optional[str] = None
    weather_notes: Optional[str] = None
    drinking_water_provided: Optional[bool] = None
    rest_schedule_arranged: Optional[bool] = None
    rest_notes: Optional[str] = None
    high_risk_moves_reminded: Optional[bool] = None
    high_risk_moves_notes: Optional[str] = None


class TrainingSafetyChecklistResponse(BaseModel):
    id: int
    rehearsal_id: int
    song_id: Optional[int] = None
    song_name: Optional[str] = None
    rehearsal_date: Optional[date] = None
    ground_condition: str
    ground_notes: Optional[str] = None
    audio_cables_arranged: bool
    audio_cables_notes: Optional[str] = None
    members_illness_reported: bool
    illness_notes: Optional[str] = None
    weather_temperature: Optional[float] = None
    weather_condition: Optional[str] = None
    weather_notes: Optional[str] = None
    drinking_water_provided: bool
    rest_schedule_arranged: bool
    rest_notes: Optional[str] = None
    high_risk_moves_reminded: bool
    high_risk_moves_notes: Optional[str] = None
    risk_level: str
    risk_assessment_notes: Optional[str] = None
    created_by: Optional[int] = None
    created_by_name: Optional[str] = None
    created_at: Optional[datetime] = None
    incident_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class EmergencyIncidentCreate(BaseModel):
    checklist_id: int
    member_id: int
    incident_type: str
    song_id: Optional[int] = None
    position_id: Optional[str] = None
    formation_position: Optional[str] = None
    description: Optional[str] = None
    severity: str = "minor"
    treatment_given: Optional[str] = None
    treated_by: Optional[str] = None
    family_notified: bool = False
    family_notification_details: Optional[str] = None
    community_leader_notified: bool = False
    community_notification_details: Optional[str] = None
    follow_up_required: bool = False
    follow_up_notes: Optional[str] = None


class EmergencyIncidentUpdate(BaseModel):
    description: Optional[str] = None
    severity: Optional[str] = None
    treatment_given: Optional[str] = None
    treated_by: Optional[str] = None
    family_notified: Optional[bool] = None
    family_notification_details: Optional[str] = None
    community_leader_notified: Optional[bool] = None
    community_notification_details: Optional[str] = None
    follow_up_required: Optional[bool] = None
    follow_up_notes: Optional[str] = None
    resolved: Optional[bool] = None


class EmergencyIncidentResponse(BaseModel):
    id: int
    checklist_id: int
    rehearsal_id: Optional[int] = None
    member_id: int
    member_name: Optional[str] = None
    member_phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    incident_type: str
    song_id: Optional[int] = None
    song_name: Optional[str] = None
    position_id: Optional[str] = None
    formation_position: Optional[str] = None
    description: Optional[str] = None
    severity: str
    treatment_given: Optional[str] = None
    treated_by: Optional[str] = None
    family_notified: bool
    family_notification_details: Optional[str] = None
    community_leader_notified: bool
    community_notification_details: Optional[str] = None
    follow_up_required: bool
    follow_up_notes: Optional[str] = None
    incident_time: Optional[datetime] = None
    resolved: bool
    resolved_time: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RiskMemberCreate(BaseModel):
    checklist_id: int
    member_id: int
    risk_level: str
    risk_factors: Optional[str] = None
    recommendation: Optional[str] = None


class RiskMemberUpdate(BaseModel):
    risk_level: Optional[str] = None
    risk_factors: Optional[str] = None
    recommendation: Optional[str] = None
    action_taken: Optional[str] = None
    status: Optional[str] = None


class RiskMemberResponse(BaseModel):
    id: int
    checklist_id: int
    rehearsal_id: Optional[int] = None
    member_id: int
    member_name: Optional[str] = None
    member_age: Optional[int] = None
    risk_level: str
    risk_factors: Optional[str] = None
    recommendation: Optional[str] = None
    action_taken: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RiskAssessmentResponse(BaseModel):
    checklist_id: int
    overall_risk_level: str
    risk_score: int
    risk_factors: list[str]
    recommendations: list[str]
    high_risk_members: list[RiskMemberResponse]
    weather_warning: Optional[str] = None


class VenueHazardCreate(BaseModel):
    rehearsal_id: int
    hazard_type: str
    location: Optional[str] = None
    description: Optional[str] = None
    severity: str = "low"
    reported_by: Optional[int] = None


class VenueHazardUpdate(BaseModel):
    hazard_type: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    resolved: Optional[bool] = None
    resolution_notes: Optional[str] = None


class VenueHazardResponse(BaseModel):
    id: int
    rehearsal_id: int
    song_id: Optional[int] = None
    song_name: Optional[str] = None
    hazard_type: str
    location: Optional[str] = None
    description: Optional[str] = None
    severity: str
    reported_by: Optional[int] = None
    reported_by_name: Optional[str] = None
    resolved: bool
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SafetyStatOverview(BaseModel):
    total_checklists: int
    total_incidents: int
    total_hazards: int
    high_risk_member_count: int
    incident_rate: float
    hazard_resolution_rate: float
    avg_risk_level: str


class IncidentTypeStat(BaseModel):
    incident_type: str
    count: int
    rate: float


class SafetyStatItem(BaseModel):
    rehearsal_id: int
    rehearsal_date: str
    song_name: str
    risk_level: str
    incident_count: int
    hazard_count: int
    high_risk_member_count: int
    family_notified_count: int


class HighRiskMemberItem(BaseModel):
    member_id: int
    member_name: str
    member_age: Optional[int] = None
    incident_count: int
    risk_level: str
    health_conditions: list[str]
    last_incident_date: Optional[str] = None


class HazardTypeStat(BaseModel):
    hazard_type: str
    count: int
    unresolved_count: int


class EmergencyResponseStat(BaseModel):
    total_incidents: int
    resolved_count: int
    resolution_rate: float
    family_notified_count: int
    family_notification_rate: float
    community_notified_count: int
    community_notification_rate: float
    avg_response_time_minutes: Optional[float] = None
