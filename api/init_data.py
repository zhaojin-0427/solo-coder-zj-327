import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import date
from database import engine, SessionLocal, Base
from models import (
    Song, Member, MemberSong, MemberSubstitutePosition,
    Formation, FormationPosition, Rehearsal, RehearsalError,
    Attendance, SubstituteAssignment,
    MemberHealthRecord, TrainingSafetyChecklist, EmergencyIncident,
    RiskMember, VenueHazardRecord,
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
    {"name": "张阿姨", "height_range": "short", "phone": "13800001001", "age": 68, "emergency_contact": "13900001001"},
    {"name": "李阿姨", "height_range": "short", "phone": "13800001002", "age": 62, "emergency_contact": "13900001002"},
    {"name": "王阿姨", "height_range": "medium", "phone": "13800001003", "age": 55, "emergency_contact": "13900001003"},
    {"name": "赵阿姨", "height_range": "medium", "phone": "13800001004", "age": 70, "emergency_contact": "13900001004"},
    {"name": "刘阿姨", "height_range": "tall", "phone": "13800001005", "age": 58, "emergency_contact": "13900001005"},
    {"name": "陈阿姨", "height_range": "tall", "phone": "13800001006", "age": 65, "emergency_contact": "13900001006"},
    {"name": "杨阿姨", "height_range": "short", "phone": "13800001007", "age": 52, "emergency_contact": "13900001007"},
    {"name": "黄阿姨", "height_range": "medium", "phone": "13800001008", "age": 67, "emergency_contact": "13900001008"},
    {"name": "周阿姨", "height_range": "tall", "phone": "13800001009", "age": 60, "emergency_contact": "13900001009"},
    {"name": "吴阿姨", "height_range": "short", "phone": "13800001010", "age": 72, "emergency_contact": "13900001010"},
    {"name": "徐阿姨", "height_range": "medium", "phone": "13800001011", "age": 56, "emergency_contact": "13900001011"},
    {"name": "孙阿姨", "height_range": "tall", "phone": "13800001012", "age": 63, "emergency_contact": "13900001012"},
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

health_records_data = [
    {"member_id": members[0].id, "record_date": date(2026, 5, 15), "condition_type": "hypertension", "description": "高血压10年，长期服药", "is_chronic": True, "needs_accommodation": True, "accommodation_notes": "避免剧烈运动，定时测量血压"},
    {"member_id": members[3].id, "record_date": date(2026, 5, 20), "condition_type": "heart_disease", "description": "冠心病史", "is_chronic": True, "needs_accommodation": True, "accommodation_notes": "避免高强度动作"},
    {"member_id": members[5].id, "record_date": date(2026, 6, 1), "condition_type": "joint_pain", "description": "膝关节退行性病变", "is_chronic": True, "needs_accommodation": True, "accommodation_notes": "减少跳跃动作"},
    {"member_id": members[7].id, "record_date": date(2026, 5, 25), "condition_type": "diabetes", "description": "II型糖尿病", "is_chronic": True, "needs_accommodation": True, "accommodation_notes": "定时休息补充能量"},
    {"member_id": members[9].id, "record_date": date(2026, 6, 5), "condition_type": "dizziness", "description": "偶尔眩晕", "is_chronic": True, "needs_accommodation": True, "accommodation_notes": "避免快速转头动作"},
    {"member_id": members[1].id, "record_date": date(2026, 5, 10), "condition_type": "asthma", "description": "运动性哮喘", "is_chronic": True, "needs_accommodation": True, "accommodation_notes": "随身携带药物"},
]
for hr in health_records_data:
    db.add(MemberHealthRecord(**hr))

db.flush()

rehearsals = db.query(Rehearsal).all()

safety_checklists_data = [
    {
        "rehearsal_id": rehearsals[0].id,
        "ground_condition": "good",
        "ground_notes": "水泥地面平整",
        "audio_cables_arranged": True,
        "audio_cables_notes": "电线已用胶带固定",
        "members_illness_reported": False,
        "illness_notes": None,
        "weather_temperature": 28.0,
        "weather_condition": "sunny",
        "weather_notes": "天气晴朗",
        "drinking_water_provided": True,
        "rest_schedule_arranged": True,
        "rest_notes": "每30分钟休息5分钟",
        "high_risk_moves_reminded": True,
        "high_risk_moves_notes": "已提醒旋转动作注意事项",
        "risk_level": "low",
    },
    {
        "rehearsal_id": rehearsals[1].id,
        "ground_condition": "fair",
        "ground_notes": "有少许沙土",
        "audio_cables_arranged": False,
        "audio_cables_notes": "电线部分裸露",
        "members_illness_reported": False,
        "illness_notes": None,
        "weather_temperature": 36.5,
        "weather_condition": "hot",
        "weather_notes": "高温天气",
        "drinking_water_provided": True,
        "rest_schedule_arranged": False,
        "rest_notes": None,
        "high_risk_moves_reminded": False,
        "high_risk_moves_notes": None,
        "risk_level": "high",
    },
    {
        "rehearsal_id": rehearsals[2].id,
        "ground_condition": "good",
        "ground_notes": None,
        "audio_cables_arranged": True,
        "audio_cables_notes": None,
        "members_illness_reported": True,
        "illness_notes": "张阿姨今日感觉头晕",
        "weather_temperature": 22.0,
        "weather_condition": "cloudy",
        "weather_notes": None,
        "drinking_water_provided": True,
        "rest_schedule_arranged": True,
        "rest_notes": None,
        "high_risk_moves_reminded": True,
        "high_risk_moves_notes": None,
        "risk_level": "medium",
    },
]

checklists = []
for sc in safety_checklists_data:
    checklist = TrainingSafetyChecklist(**sc)
    db.add(checklist)
    db.flush()
    checklists.append(checklist)

from services import _calculate_risk_level, _identify_risk_members

for checklist in checklists:
    risk_level, risk_score, risk_factors, recommendations = _calculate_risk_level(db, checklist)
    checklist.risk_level = risk_level
    checklist.risk_assessment_notes = "、".join(risk_factors) if risk_factors else None

    risk_member_data = _identify_risk_members(db, checklist)
    for rm in risk_member_data:
        risk_member = RiskMember(
            checklist_id=checklist.id,
            member_id=rm["member_id"],
            risk_level=rm["risk_level"],
            risk_factors=rm["risk_factors"],
            recommendation=rm["recommendation"],
            status="pending",
        )
        db.add(risk_member)

db.flush()

emergency_incidents_data = [
    {
        "checklist_id": checklists[1].id,
        "member_id": members[0].id,
        "incident_type": "dizziness",
        "song_id": songs[1].id,
        "position_id": "P1",
        "formation_position": "第1排第1位",
        "description": "高温下排练出现头晕症状",
        "severity": "moderate",
        "treatment_given": "转移至阴凉处休息，服用藿香正气水",
        "treated_by": "李队长",
        "family_notified": True,
        "family_notification_details": "已电话通知家属，家属表示会来接",
        "community_leader_notified": True,
        "community_notification_details": "已通知社区主任",
        "follow_up_required": True,
        "follow_up_notes": "明日随访观察血压",
        "resolved": True,
    },
    {
        "checklist_id": checklists[1].id,
        "member_id": members[3].id,
        "incident_type": "cable_trip",
        "song_id": songs[1].id,
        "position_id": "P4",
        "formation_position": "第2排第2位",
        "description": "被裸露的电线绊倒",
        "severity": "minor",
        "treatment_given": "检查无大碍，休息即可",
        "treated_by": "队长",
        "family_notified": False,
        "family_notification_details": None,
        "community_leader_notified": False,
        "community_notification_details": None,
        "follow_up_required": False,
        "follow_up_notes": None,
        "resolved": True,
    },
    {
        "checklist_id": checklists[2].id,
        "member_id": members[9].id,
        "incident_type": "sprain",
        "song_id": songs[2].id,
        "position_id": "P3",
        "description": "转身时扭伤脚踝",
        "severity": "moderate",
        "treatment_given": "冰敷处理",
        "treated_by": "王阿姨",
        "family_notified": True,
        "family_notification_details": "通知了家人情况",
        "community_leader_notified": False,
        "community_notification_details": None,
        "follow_up_required": True,
        "follow_up_notes": "建议去医院检查",
        "resolved": False,
    },
]

for ei in emergency_incidents_data:
    db.add(EmergencyIncident(**ei))

venue_hazards_data = [
    {
        "rehearsal_id": rehearsals[0].id,
        "hazard_type": "loose_cable",
        "location": "音响附近",
        "description": "电线杂乱堆放",
        "severity": "medium",
        "resolved": True,
        "resolution_notes": "已用胶带固定",
    },
    {
        "rehearsal_id": rehearsals[1].id,
        "hazard_type": "slippery_floor",
        "location": "场地东南角",
        "description": "地面有积水",
        "severity": "high",
        "resolved": False,
    },
    {
        "rehearsal_id": rehearsals[2].id,
        "hazard_type": "lack_of_first_aid",
        "location": "急救箱",
        "description": "药品过期",
        "severity": "medium",
        "resolved": False,
    },
]

for vh in venue_hazards_data:
    db.add(VenueHazardRecord(**vh))

db.commit()
db.close()
print("Initialization complete!")
