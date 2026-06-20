from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, Text, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    beat_count = Column(Integer, nullable=False)
    formation_type = Column(String(20), nullable=False)
    performance_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    member_songs = relationship("MemberSong", back_populates="song", cascade="all, delete-orphan")
    formations = relationship("Formation", back_populates="song", cascade="all, delete-orphan")
    rehearsals = relationship("Rehearsal", back_populates="song", cascade="all, delete-orphan")
    attendance = relationship("Attendance", back_populates="song", cascade="all, delete-orphan")
    substitute_assignments = relationship("SubstituteAssignment", back_populates="song", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("formation_type IN ('line', 'triangle', 'square', 'circle', 'double_row', 'v_shape')", name="ck_songs_formation_type"),
    )


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    height_range = Column(String(10), nullable=False)
    phone = Column(String(20))
    age = Column(Integer)
    emergency_contact = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())

    member_songs = relationship("MemberSong", back_populates="member", cascade="all, delete-orphan")
    substitute_positions = relationship("MemberSubstitutePosition", back_populates="member", cascade="all, delete-orphan")
    formation_positions = relationship("FormationPosition", back_populates="member")
    attendance = relationship("Attendance", back_populates="member", cascade="all, delete-orphan")
    health_records = relationship("MemberHealthRecord", back_populates="member", cascade="all, delete-orphan")
    emergency_incidents = relationship("EmergencyIncident", back_populates="member", foreign_keys="EmergencyIncident.member_id")

    __table_args__ = (
        CheckConstraint("height_range IN ('short', 'medium', 'tall')", name="ck_members_height_range"),
    )


class MemberSong(Base):
    __tablename__ = "member_songs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id", ondelete="CASCADE"), nullable=False)

    member = relationship("Member", back_populates="member_songs")
    song = relationship("Song", back_populates="member_songs")

    __table_args__ = (
        UniqueConstraint("member_id", "song_id", name="uq_member_song"),
    )


class MemberSubstitutePosition(Base):
    __tablename__ = "member_substitute_positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    position_label = Column(String(20), nullable=False)

    member = relationship("Member", back_populates="substitute_positions")


class Formation(Base):
    __tablename__ = "formations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    song_id = Column(Integer, ForeignKey("songs.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    is_locked = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.now())

    song = relationship("Song", back_populates="formations")
    positions = relationship("FormationPosition", back_populates="formation", cascade="all, delete-orphan")


class FormationPosition(Base):
    __tablename__ = "formation_positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    formation_id = Column(Integer, ForeignKey("formations.id", ondelete="CASCADE"), nullable=False)
    position_id = Column(String(20), nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    row_num = Column(Integer, nullable=False)
    col_num = Column(Integer, nullable=False)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="SET NULL"), nullable=True)

    formation = relationship("Formation", back_populates="positions")
    member = relationship("Member", back_populates="formation_positions")


class Rehearsal(Base):
    __tablename__ = "rehearsals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    song_id = Column(Integer, ForeignKey("songs.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    duration_minutes = Column(Integer, nullable=False, default=60)
    teacher_notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    song = relationship("Song", back_populates="rehearsals")
    errors = relationship("RehearsalError", back_populates="rehearsal", cascade="all, delete-orphan")


class RehearsalError(Base):
    __tablename__ = "rehearsal_errors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rehearsal_id = Column(Integer, ForeignKey("rehearsals.id", ondelete="CASCADE"), nullable=False)
    position_id = Column(String(20), nullable=False)
    error_type = Column(String(20), nullable=False)
    beat_number = Column(Integer)
    description = Column(Text)

    rehearsal = relationship("Rehearsal", back_populates="errors")

    __table_args__ = (
        CheckConstraint("error_type IN ('beat_error', 'position_error')", name="ck_rehearsal_errors_error_type"),
    )


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String(10), nullable=False)

    member = relationship("Member", back_populates="attendance")
    song = relationship("Song", back_populates="attendance")

    __table_args__ = (
        CheckConstraint("status IN ('present', 'absent')", name="ck_attendance_status"),
        UniqueConstraint("member_id", "song_id", "date", name="uq_attendance"),
    )


class SubstituteAssignment(Base):
    __tablename__ = "substitute_assignments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    song_id = Column(Integer, ForeignKey("songs.id", ondelete="CASCADE"), nullable=False)
    absent_member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    substitute_member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    position_id = Column(String(20), nullable=False)
    priority = Column(Integer, nullable=False, default=1)

    song = relationship("Song", back_populates="substitute_assignments")
    absent_member = relationship("Member", foreign_keys=[absent_member_id])
    substitute_member = relationship("Member", foreign_keys=[substitute_member_id])


class PerformanceTask(Base):
    __tablename__ = "performance_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    location = Column(String(200), nullable=False)
    meeting_time = Column(DateTime, nullable=False)
    start_time = Column(DateTime, nullable=False)
    costume_requirements = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    song_tasks = relationship("PerformanceSongTask", back_populates="performance", cascade="all, delete-orphan")
    confirmations = relationship("PerformanceConfirmation", back_populates="performance", cascade="all, delete-orphan")


class PerformanceSongTask(Base):
    __tablename__ = "performance_song_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    performance_id = Column(Integer, ForeignKey("performance_tasks.id", ondelete="CASCADE"), nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id", ondelete="CASCADE"), nullable=False)
    formation_id = Column(Integer, ForeignKey("formations.id", ondelete="SET NULL"), nullable=True)
    performance_order = Column(Integer, nullable=False, default=0)

    performance = relationship("PerformanceTask", back_populates="song_tasks")
    song = relationship("Song")
    formation = relationship("Formation")

    __table_args__ = (
        UniqueConstraint("performance_id", "song_id", name="uq_performance_song"),
    )


class PerformanceConfirmation(Base):
    __tablename__ = "performance_confirmations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    performance_id = Column(Integer, ForeignKey("performance_tasks.id", ondelete="CASCADE"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False, default="unconfirmed")
    transport_mode = Column(String(50))
    remark = Column(Text)
    phone_reminded = Column(Boolean, nullable=False, default=False)
    confirmed_at = Column(DateTime, nullable=True)

    performance = relationship("PerformanceTask", back_populates="confirmations")
    member = relationship("Member")

    __table_args__ = (
        CheckConstraint("status IN ('unconfirmed', 'confirmed', 'leave')", name="ck_perf_conf_status"),
        UniqueConstraint("performance_id", "member_id", name="uq_perf_member_conf"),
    )


class PrePerformanceChecklist(Base):
    __tablename__ = "pre_performance_checklists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    performance_id = Column(Integer, ForeignKey("performance_tasks.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    performance = relationship("PerformanceTask")
    items = relationship("PrePerformanceCheckItem", back_populates="checklist", cascade="all, delete-orphan")


class PrePerformanceCheckItem(Base):
    __tablename__ = "pre_performance_check_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    checklist_id = Column(Integer, ForeignKey("pre_performance_checklists.id", ondelete="CASCADE"), nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(30), nullable=False)
    item_name = Column(String(200), nullable=False)
    responsible_member_id = Column(Integer, ForeignKey("members.id", ondelete="SET NULL"), nullable=True)
    position_id = Column(String(20), nullable=True)
    deadline = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default="not_started")
    abnormal_description = Column(Text)
    photo_url = Column(String(500))
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    checklist = relationship("PrePerformanceChecklist", back_populates="items")
    song = relationship("Song")
    responsible_member = relationship("Member")

    __table_args__ = (
        CheckConstraint(
            "category IN ('costume', 'prop', 'audio', 'accompaniment', 'transport', 'substitute')",
            name="ck_check_item_category",
        ),
        CheckConstraint(
            "status IN ('not_started', 'in_progress', 'abnormal', 'completed')",
            name="ck_check_item_status",
        ),
    )


class MemberHealthRecord(Base):
    __tablename__ = "member_health_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    record_date = Column(Date, nullable=False)
    condition_type = Column(String(30), nullable=False)
    description = Column(Text)
    is_chronic = Column(Boolean, nullable=False, default=False)
    needs_accommodation = Column(Boolean, nullable=False, default=False)
    accommodation_notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    member = relationship("Member", back_populates="health_records")

    __table_args__ = (
        CheckConstraint(
            "condition_type IN ('heart_disease', 'hypertension', 'diabetes', 'asthma', 'joint_pain', 'dizziness', 'allergy', 'injury', 'other')",
            name="ck_health_condition_type",
        ),
    )


class TrainingSafetyChecklist(Base):
    __tablename__ = "training_safety_checklists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rehearsal_id = Column(Integer, ForeignKey("rehearsals.id", ondelete="CASCADE"), nullable=False)
    ground_condition = Column(String(20), nullable=False)
    ground_notes = Column(Text)
    audio_cables_arranged = Column(Boolean, nullable=False, default=False)
    audio_cables_notes = Column(Text)
    members_illness_reported = Column(Boolean, nullable=False, default=False)
    illness_notes = Column(Text)
    weather_temperature = Column(Float)
    weather_condition = Column(String(20))
    weather_notes = Column(Text)
    drinking_water_provided = Column(Boolean, nullable=False, default=False)
    rest_schedule_arranged = Column(Boolean, nullable=False, default=False)
    rest_notes = Column(Text)
    high_risk_moves_reminded = Column(Boolean, nullable=False, default=False)
    high_risk_moves_notes = Column(Text)
    risk_level = Column(String(10), nullable=False, default="low")
    risk_assessment_notes = Column(Text)
    created_by = Column(Integer, ForeignKey("members.id", ondelete="SET NULL"))
    created_at = Column(DateTime, server_default=func.now())

    rehearsal = relationship("Rehearsal")
    incidents = relationship("EmergencyIncident", back_populates="checklist")
    risk_members = relationship("RiskMember", back_populates="checklist")

    __table_args__ = (
        CheckConstraint(
            "ground_condition IN ('good', 'fair', 'poor')",
            name="ck_ground_condition",
        ),
        CheckConstraint(
            "weather_condition IN ('sunny', 'cloudy', 'rainy', 'windy', 'hot', 'cold')",
            name="ck_weather_condition",
        ),
        CheckConstraint(
            "risk_level IN ('low', 'medium', 'high', 'critical')",
            name="ck_risk_level",
        ),
    )


class EmergencyIncident(Base):
    __tablename__ = "emergency_incidents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    checklist_id = Column(Integer, ForeignKey("training_safety_checklists.id", ondelete="CASCADE"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    incident_type = Column(String(20), nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id", ondelete="SET NULL"))
    position_id = Column(String(20))
    formation_position = Column(String(50))
    description = Column(Text)
    severity = Column(String(10), nullable=False, default="minor")
    treatment_given = Column(Text)
    treated_by = Column(String(50))
    family_notified = Column(Boolean, nullable=False, default=False)
    family_notification_details = Column(Text)
    community_leader_notified = Column(Boolean, nullable=False, default=False)
    community_notification_details = Column(Text)
    follow_up_required = Column(Boolean, nullable=False, default=False)
    follow_up_notes = Column(Text)
    incident_time = Column(DateTime, server_default=func.now())
    resolved = Column(Boolean, nullable=False, default=False)
    resolved_time = Column(DateTime)

    checklist = relationship("TrainingSafetyChecklist", back_populates="incidents")
    member = relationship("Member", back_populates="emergency_incidents", foreign_keys=[member_id])
    song = relationship("Song")

    __table_args__ = (
        CheckConstraint(
            "incident_type IN ('sprain', 'dizziness', 'fall', 'cable_trip', 'heat_stroke', 'dehydration', 'heart_issue', 'breathing_difficulty', 'injury', 'other')",
            name="ck_incident_type",
        ),
        CheckConstraint(
            "severity IN ('minor', 'moderate', 'severe', 'critical')",
            name="ck_incident_severity",
        ),
    )


class RiskMember(Base):
    __tablename__ = "risk_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    checklist_id = Column(Integer, ForeignKey("training_safety_checklists.id", ondelete="CASCADE"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    risk_level = Column(String(10), nullable=False)
    risk_factors = Column(Text)
    recommendation = Column(Text)
    action_taken = Column(Text)
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(DateTime, server_default=func.now())

    checklist = relationship("TrainingSafetyChecklist", back_populates="risk_members")
    member = relationship("Member")

    __table_args__ = (
        CheckConstraint(
            "risk_level IN ('low', 'medium', 'high', 'critical')",
            name="ck_risk_member_level",
        ),
        CheckConstraint(
            "status IN ('pending', 'adjusted', 'resting', 'monitoring')",
            name="ck_risk_member_status",
        ),
    )


class VenueHazardRecord(Base):
    __tablename__ = "venue_hazard_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rehearsal_id = Column(Integer, ForeignKey("rehearsals.id", ondelete="CASCADE"), nullable=False)
    hazard_type = Column(String(30), nullable=False)
    location = Column(String(100))
    description = Column(Text)
    severity = Column(String(10), nullable=False, default="low")
    reported_by = Column(Integer, ForeignKey("members.id", ondelete="SET NULL"))
    resolved = Column(Boolean, nullable=False, default=False)
    resolution_notes = Column(Text)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    rehearsal = relationship("Rehearsal")

    __table_args__ = (
        CheckConstraint(
            "hazard_type IN ('slippery_floor', 'obstacle', 'loose_cable', 'uneven_ground', 'poor_lighting', 'sharp_edge', 'lack_of_first_aid', 'other')",
            name="ck_hazard_type",
        ),
        CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name="ck_hazard_severity",
        ),
    )
