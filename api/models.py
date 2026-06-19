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
    created_at = Column(DateTime, server_default=func.now())

    member_songs = relationship("MemberSong", back_populates="member", cascade="all, delete-orphan")
    substitute_positions = relationship("MemberSubstitutePosition", back_populates="member", cascade="all, delete-orphan")
    formation_positions = relationship("FormationPosition", back_populates="member")
    attendance = relationship("Attendance", back_populates="member", cascade="all, delete-orphan")

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
