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
