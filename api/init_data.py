import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import date
from database import engine, SessionLocal, Base
from models import (
    Song, Member, MemberSong, MemberSubstitutePosition,
    Formation, FormationPosition, Rehearsal, RehearsalError,
    Attendance, SubstituteAssignment,
)

Base.metadata.create_all(bind=engine)

db = SessionLocal()

if db.query(Song).first():
    print("Data already exists, skipping initialization.")
    db.close()
    exit(0)

songs_data = [
    {"name": "最炫民族风", "beat_count": 32, "formation_type": "line", "performance_order": 1},
    {"name": "小苹果", "beat_count": 48, "formation_type": "triangle", "performance_order": 2},
    {"name": "荷塘月色", "beat_count": 40, "formation_type": "square", "performance_order": 3},
    {"name": "最亲的人", "beat_count": 36, "formation_type": "circle", "performance_order": 4},
    {"name": "站在草原望北京", "beat_count": 44, "formation_type": "double_row", "performance_order": 5},
]
songs = []
for s in songs_data:
    song = Song(**s)
    db.add(song)
    db.flush()
    songs.append(song)

members_data = [
    {"name": "张阿姨", "height_range": "short", "phone": "13800001001"},
    {"name": "李阿姨", "height_range": "short", "phone": "13800001002"},
    {"name": "王阿姨", "height_range": "medium", "phone": "13800001003"},
    {"name": "赵阿姨", "height_range": "medium", "phone": "13800001004"},
    {"name": "刘阿姨", "height_range": "tall", "phone": "13800001005"},
    {"name": "陈阿姨", "height_range": "tall", "phone": "13800001006"},
    {"name": "杨阿姨", "height_range": "short", "phone": "13800001007"},
    {"name": "黄阿姨", "height_range": "medium", "phone": "13800001008"},
    {"name": "周阿姨", "height_range": "tall", "phone": "13800001009"},
    {"name": "吴阿姨", "height_range": "short", "phone": "13800001010"},
    {"name": "徐阿姨", "height_range": "medium", "phone": "13800001011"},
    {"name": "孙阿姨", "height_range": "tall", "phone": "13800001012"},
]
members = []
for m in members_data:
    member = Member(**m)
    db.add(member)
    db.flush()
    members.append(member)

song_member_map = {
    0: [0, 1, 2, 3, 4, 5],
    1: [0, 2, 3, 4, 6, 7, 8, 9],
    2: [1, 2, 4, 5, 6, 7, 8, 10, 11],
    3: [0, 1, 3, 5, 6, 8, 9, 10, 11],
    4: [2, 3, 4, 7, 8, 9, 10, 11],
}
for song_idx, member_indices in song_member_map.items():
    for mi in member_indices:
        db.add(MemberSong(member_id=members[mi].id, song_id=songs[song_idx].id))

sub_pos_data = [
    (0, ["P1", "P2"]),
    (1, ["P3", "P4"]),
    (2, ["P1", "P5"]),
    (3, ["P2", "P6"]),
    (4, ["P5", "P6"]),
    (5, ["P3", "P7"]),
    (6, ["P1", "P2", "P3"]),
    (7, ["P4", "P5", "P8"]),
    (8, ["P6", "P7", "P9"]),
    (9, ["P1", "P4"]),
    (10, ["P2", "P5"]),
    (11, ["P3", "P6"]),
]
for member_idx, positions in sub_pos_data:
    for pos in positions:
        db.add(MemberSubstitutePosition(member_id=members[member_idx].id, position_label=pos))

db.commit()

import services as svc

for song in songs:
    svc.create_formation_draft(db, song.id)

rehearsals_data = [
    {"song_id": songs[0].id, "date": date(2026, 6, 1), "duration_minutes": 90, "teacher_notes": "节奏感不错，注意队形整齐"},
    {"song_id": songs[1].id, "date": date(2026, 6, 3), "duration_minutes": 60, "teacher_notes": "三角形站位需要加强"},
    {"song_id": songs[2].id, "date": date(2026, 6, 5), "duration_minutes": 75, "teacher_notes": "方块队形基本到位"},
    {"song_id": songs[0].id, "date": date(2026, 6, 8), "duration_minutes": 60, "teacher_notes": "第二次排练进步明显"},
    {"song_id": songs[3].id, "date": date(2026, 6, 10), "duration_minutes": 90, "teacher_notes": "圆形队形需要更圆"},
    {"song_id": songs[4].id, "date": date(2026, 6, 12), "duration_minutes": 60, "teacher_notes": "双排队形整齐度良好"},
]
for rd in rehearsals_data:
    rehearsal = Rehearsal(**rd)
    db.add(rehearsal)
    db.flush()

    errors = [
        {"rehearsal_id": rehearsal.id, "position_id": "P1", "error_type": "beat_error", "beat_number": 8, "description": "节奏快了半拍"},
        {"rehearsal_id": rehearsal.id, "position_id": "P3", "error_type": "position_error", "beat_number": None, "description": "位置偏移"},
    ]
    for err in errors:
        db.add(RehearsalError(**err))

attendance_data = [
    {"member_id": members[0].id, "song_id": songs[0].id, "date": date(2026, 6, 1), "status": "present"},
    {"member_id": members[1].id, "song_id": songs[0].id, "date": date(2026, 6, 1), "status": "present"},
    {"member_id": members[2].id, "song_id": songs[0].id, "date": date(2026, 6, 1), "status": "absent"},
    {"member_id": members[0].id, "song_id": songs[0].id, "date": date(2026, 6, 8), "status": "present"},
    {"member_id": members[1].id, "song_id": songs[0].id, "date": date(2026, 6, 8), "status": "absent"},
    {"member_id": members[2].id, "song_id": songs[1].id, "date": date(2026, 6, 3), "status": "present"},
    {"member_id": members[3].id, "song_id": songs[1].id, "date": date(2026, 6, 3), "status": "present"},
    {"member_id": members[4].id, "song_id": songs[2].id, "date": date(2026, 6, 5), "status": "absent"},
    {"member_id": members[5].id, "song_id": songs[2].id, "date": date(2026, 6, 5), "status": "present"},
    {"member_id": members[6].id, "song_id": songs[3].id, "date": date(2026, 6, 10), "status": "present"},
    {"member_id": members[7].id, "song_id": songs[3].id, "date": date(2026, 6, 10), "status": "absent"},
    {"member_id": members[8].id, "song_id": songs[4].id, "date": date(2026, 6, 12), "status": "present"},
]
for ad in attendance_data:
    db.add(Attendance(**ad))

sub_assignments_data = [
    {"song_id": songs[0].id, "absent_member_id": members[2].id, "substitute_member_id": members[6].id, "position_id": "P1", "priority": 1},
    {"song_id": songs[3].id, "absent_member_id": members[7].id, "substitute_member_id": members[9].id, "position_id": "P4", "priority": 1},
]
for sa in sub_assignments_data:
    db.add(SubstituteAssignment(**sa))

db.commit()
db.close()
print("Initialization complete!")
