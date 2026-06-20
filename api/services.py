import math
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import (
    Song, Member, MemberSong, MemberSubstitutePosition,
    Formation, FormationPosition, Rehearsal, RehearsalError,
    Attendance, SubstituteAssignment,
    PerformanceTask, PerformanceSongTask, PrePerformanceChecklist, PrePerformanceCheckItem,
    MemberHealthRecord, TrainingSafetyChecklist, EmergencyIncident,
    RiskMember, VenueHazardRecord,
)
from schemas import (
    FormationPositionUpdate,
)

HEIGHT_ORDER = {"short": 0, "medium": 1, "tall": 2}


def generate_formation_positions(formation_type: str, members: list[Member]) -> list[dict]:
    sorted_members = sorted(members, key=lambda m: HEIGHT_ORDER.get(m.height_range, 1))
    n = len(sorted_members)
    if n == 0:
        return []

    if formation_type == "line":
        return _generate_line(sorted_members)
    elif formation_type == "triangle":
        return _generate_triangle(sorted_members)
    elif formation_type == "square":
        return _generate_square(sorted_members)
    elif formation_type == "circle":
        return _generate_circle(sorted_members)
    elif formation_type == "double_row":
        return _generate_double_row(sorted_members)
    elif formation_type == "v_shape":
        return _generate_v_shape(sorted_members)
    return []


def _generate_line(members: list[Member]) -> list[dict]:
    n = len(members)
    positions = []
    for i, m in enumerate(members):
        x = (i / (n - 1)) * 800 if n > 1 else 400
        y = 300
        positions.append({
            "position_id": f"P{i+1}",
            "x": round(x, 1),
            "y": round(y, 1),
            "row_num": 1,
            "col_num": i + 1,
            "member_id": m.id,
        })
    return positions


def _generate_triangle(members: list[Member]) -> list[dict]:
    n = len(members)
    rows = []
    remaining = n
    row_size = 1
    while remaining > 0:
        take = min(row_size, remaining)
        rows.append(take)
        remaining -= take
        row_size += 1

    positions = []
    idx = 0
    total_rows = len(rows)
    for r_idx, row_count in enumerate(rows):
        for c_idx in range(row_count):
            if idx >= n:
                break
            x = 400 + (c_idx - (row_count - 1) / 2) * 120
            y = 100 + r_idx * 100
            positions.append({
                "position_id": f"P{idx+1}",
                "x": round(x, 1),
                "y": round(y, 1),
                "row_num": r_idx + 1,
                "col_num": c_idx + 1,
                "member_id": members[idx].id,
            })
            idx += 1
    return positions


def _generate_square(members: list[Member]) -> list[dict]:
    n = len(members)
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)

    positions = []
    idx = 0
    for r_idx in range(rows):
        row_count = min(cols, n - idx)
        for c_idx in range(row_count):
            if idx >= n:
                break
            x = 400 + (c_idx - (row_count - 1) / 2) * 120
            y = 100 + r_idx * 100
            positions.append({
                "position_id": f"P{idx+1}",
                "x": round(x, 1),
                "y": round(y, 1),
                "row_num": r_idx + 1,
                "col_num": c_idx + 1,
                "member_id": members[idx].id,
            })
            idx += 1
    return positions


def _generate_circle(members: list[Member]) -> list[dict]:
    n = len(members)
    positions = []
    cx, cy, radius = 400, 300, 200
    for i, m in enumerate(members):
        angle = (2 * math.pi * i) / n - math.pi / 2
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        positions.append({
            "position_id": f"P{i+1}",
            "x": round(x, 1),
            "y": round(y, 1),
            "row_num": 1,
            "col_num": i + 1,
            "member_id": m.id,
        })
    return positions


def _generate_double_row(members: list[Member]) -> list[dict]:
    n = len(members)
    front_count = math.ceil(n / 2)
    positions = []
    for i, m in enumerate(members):
        if i < front_count:
            row_num = 1
            x = 400 + (i - (front_count - 1) / 2) * 120
            y = 200
        else:
            row_num = 2
            back_idx = i - front_count
            back_count = n - front_count
            x = 400 + (back_idx - (back_count - 1) / 2) * 120
            y = 350
        positions.append({
            "position_id": f"P{i+1}",
            "x": round(x, 1),
            "y": round(y, 1),
            "row_num": row_num,
            "col_num": (i if i < front_count else i - front_count) + 1,
            "member_id": m.id,
        })
    return positions


def _generate_v_shape(members: list[Member]) -> list[dict]:
    tall_order = {"short": 0, "medium": 1, "tall": 2}
    sorted_members = sorted(members, key=lambda m: -tall_order.get(m.height_range, 1))
    n = len(sorted_members)
    positions = []
    cx, cy = 400, 300
    for i, m in enumerate(sorted_members):
        if i == 0:
            positions.append({
                "position_id": f"P{i+1}",
                "x": round(cx, 1),
                "y": round(cy, 1),
                "row_num": 1,
                "col_num": 1,
                "member_id": m.id,
            })
        else:
            side = 1 if i % 2 == 1 else -1
            depth = (i + 1) // 2
            x = cx + side * depth * 100
            y = cy - depth * 80
            positions.append({
                "position_id": f"P{i+1}",
                "x": round(x, 1),
                "y": round(y, 1),
                "row_num": depth + 1,
                "col_num": 1 if side == -1 else 2,
                "member_id": m.id,
            })
    return positions


def create_formation_draft(db: Session, song_id: int) -> Formation:
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        return None

    member_ids = [ms.member_id for ms in db.query(MemberSong).filter(MemberSong.song_id == song_id).all()]
    members = db.query(Member).filter(Member.id.in_(member_ids)).all() if member_ids else []

    last_formation = db.query(Formation).filter(Formation.song_id == song_id).order_by(Formation.version.desc()).first()
    next_version = (last_formation.version + 1) if last_formation else 1

    formation = Formation(song_id=song_id, version=next_version, is_locked=False)
    db.add(formation)
    db.flush()

    position_data = generate_formation_positions(song.formation_type, members)
    for pd in position_data:
        pos = FormationPosition(
            formation_id=formation.id,
            **pd,
        )
        db.add(pos)

    db.commit()
    db.refresh(formation)
    return formation


def update_formation_positions(db: Session, formation_id: int, updates: list[FormationPositionUpdate]) -> Formation:
    formation = db.query(Formation).filter(Formation.id == formation_id).first()
    if not formation or formation.is_locked:
        return None

    for upd in updates:
        pos = db.query(FormationPosition).filter(FormationPosition.id == upd.id).first()
        if pos and pos.formation_id == formation_id:
            if upd.x is not None:
                pos.x = upd.x
            if upd.y is not None:
                pos.y = upd.y
            if upd.member_id is not None:
                pos.member_id = upd.member_id

    db.commit()
    db.refresh(formation)
    return formation


def lock_formation(db: Session, formation_id: int) -> Formation:
    formation = db.query(Formation).filter(Formation.id == formation_id).first()
    if not formation:
        return None
    formation.is_locked = True
    db.commit()
    db.refresh(formation)
    return formation


def recommend_substitutes(db: Session, song_id: int, absent_member_id: int) -> list[dict]:
    absent_positions = db.query(FormationPosition).filter(
        FormationPosition.member_id == absent_member_id
    ).all()
    absent_position_ids = [p.position_id for p in absent_positions]

    absent_member_songs = db.query(MemberSong).filter(MemberSong.member_id == absent_member_id).all()
    absent_song_ids = {ms.song_id for ms in absent_member_songs}

    all_member_songs = db.query(MemberSong).filter(MemberSong.song_id == song_id).all()
    eligible_member_ids = {ms.member_id for ms in all_member_songs} - {absent_member_id}

    results = []
    for mid in eligible_member_ids:
        member = db.query(Member).filter(Member.id == mid).first()
        if not member:
            continue
        sub_positions = db.query(MemberSubstitutePosition).filter(
            MemberSubstitutePosition.member_id == mid
        ).all()
        sub_labels = {sp.position_label for sp in sub_positions}
        matched = [pid for pid in absent_position_ids if pid in sub_labels]

        member_song_ids = {ms.song_id for ms in db.query(MemberSong).filter(MemberSong.member_id == mid).all()}
        common_songs = len(absent_song_ids & member_song_ids)

        if matched or common_songs > 0:
            results.append({
                "member_id": mid,
                "name": member.name,
                "matched_positions": matched if matched else [],
                "priority": len(matched) + common_songs,
            })

    results.sort(key=lambda r: -r["priority"])
    return results


def get_overview(db: Session) -> dict:
    return {
        "total_songs": db.query(func.count(Song.id)).scalar(),
        "total_members": db.query(func.count(Member.id)).scalar(),
        "total_rehearsals": db.query(func.count(Rehearsal.id)).scalar(),
        "total_formations": db.query(func.count(Formation.id)).scalar(),
    }


def get_rehearsal_counts(db: Session) -> list[dict]:
    results = (
        db.query(Rehearsal.song_id, Song.name, func.count(Rehearsal.id))
        .join(Song, Rehearsal.song_id == Song.id)
        .group_by(Rehearsal.song_id)
        .all()
    )
    return [{"song_id": r[0], "song_name": r[1], "count": r[2]} for r in results]


def get_substitute_rates(db: Session) -> list[dict]:
    rehearsal_counts = (
        db.query(Rehearsal.song_id, func.count(Rehearsal.id))
        .group_by(Rehearsal.song_id)
        .all()
    )
    sub_counts = (
        db.query(SubstituteAssignment.song_id, func.count(SubstituteAssignment.id))
        .group_by(SubstituteAssignment.song_id)
        .all()
    )
    rehearsal_map = {r[0]: r[1] for r in rehearsal_counts}
    sub_map = {s[0]: s[1] for s in sub_counts}
    all_song_ids = set(rehearsal_map.keys()) | set(sub_map.keys())

    results = []
    for sid in all_song_ids:
        song = db.query(Song).filter(Song.id == sid).first()
        if not song:
            continue
        r_count = rehearsal_map.get(sid, 0)
        s_count = sub_map.get(sid, 0)
        rate = s_count / r_count if r_count > 0 else 0
        results.append({
            "song_id": sid,
            "song_name": song.name,
            "total_assignments": s_count,
            "total_rehearsals": r_count,
            "rate": round(rate, 2),
        })
    return results


def get_error_positions(db: Session) -> list[dict]:
    results = (
        db.query(RehearsalError.position_id, func.count(RehearsalError.id))
        .group_by(RehearsalError.position_id)
        .order_by(func.count(RehearsalError.id).desc())
        .all()
    )
    return [{"position_id": r[0], "count": r[1]} for r in results]


def get_attendance_stats(db: Session) -> list[dict]:
    results = (
        db.query(
            Attendance.member_id,
            Member.name,
            func.sum(func.iif(Attendance.status == "present", 1, 0)),
            func.sum(func.iif(Attendance.status == "absent", 1, 0)),
        )
        .join(Member, Attendance.member_id == Member.id)
        .group_by(Attendance.member_id)
        .all()
    )
    items = []
    for r in results:
        present = r[2] or 0
        absent = r[3] or 0
        total = present + absent
        rate = round(present / total, 2) if total > 0 else 0
        items.append({
            "member_id": r[0],
            "member_name": r[1],
            "present_count": present,
            "absent_count": absent,
            "attendance_rate": rate,
        })
    return items


CATEGORY_DISPLAY = {
    "costume": "服装",
    "prop": "道具",
    "audio": "音响",
    "accompaniment": "伴奏文件",
    "transport": "交通集合",
    "substitute": "替补到位",
}

DEFAULT_CATEGORY_ITEMS = {
    "costume": "服装检查",
    "prop": "道具检查",
    "audio": "音响设备检查",
    "accompaniment": "伴奏文件确认",
    "transport": "交通集合确认",
    "substitute": "替补人员到位确认",
}


def _category_display_name(category: str) -> str:
    return CATEGORY_DISPLAY.get(category, category)


def _check_item_to_dict(item: PrePerformanceCheckItem) -> dict:
    return {
        "id": item.id,
        "checklist_id": item.checklist_id,
        "song_id": item.song_id,
        "song_name": item.song.name if item.song else "",
        "category": item.category,
        "item_name": item.item_name,
        "responsible_member_id": item.responsible_member_id,
        "responsible_member_name": item.responsible_member.name if item.responsible_member else None,
        "position_id": item.position_id,
        "deadline": item.deadline,
        "status": item.status,
        "abnormal_description": item.abnormal_description,
        "photo_url": item.photo_url,
        "completed_at": item.completed_at,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }


def _check_item_abnormal_to_dict(item: PrePerformanceCheckItem) -> dict:
    return {
        "item_id": item.id,
        "item_name": item.item_name,
        "category": item.category,
        "song_id": item.song_id,
        "song_name": item.song.name if item.song else "",
        "responsible_member_id": item.responsible_member_id,
        "responsible_member_name": item.responsible_member.name if item.responsible_member else None,
        "position_id": item.position_id,
        "abnormal_description": item.abnormal_description,
    }


def _checklist_to_dict(checklist: PrePerformanceChecklist) -> dict:
    return {
        "id": checklist.id,
        "performance_id": checklist.performance_id,
        "created_at": checklist.created_at,
        "items": [_check_item_to_dict(item) for item in checklist.items],
    }


def generate_checklist(db: Session, performance_id: int, data: dict) -> dict | None:
    performance = db.query(PerformanceTask).filter(PerformanceTask.id == performance_id).first()
    if not performance:
        return None

    existing = db.query(PrePerformanceChecklist).filter(
        PrePerformanceChecklist.performance_id == performance_id
    ).first()
    if existing:
        return None

    checklist = PrePerformanceChecklist(performance_id=performance_id)
    db.add(checklist)
    db.flush()

    custom_items = data.get("items") or []
    if custom_items:
        for ci in custom_items:
            item = PrePerformanceCheckItem(
                checklist_id=checklist.id,
                song_id=ci["song_id"],
                category=ci["category"],
                item_name=ci["item_name"],
                responsible_member_id=ci.get("responsible_member_id"),
                position_id=ci.get("position_id"),
                deadline=ci.get("deadline"),
            )
            db.add(item)
    else:
        song_tasks = (
            db.query(PerformanceSongTask)
            .filter(PerformanceSongTask.performance_id == performance_id)
            .order_by(PerformanceSongTask.performance_order)
            .all()
        )
        for st in song_tasks:
            for cat, name in DEFAULT_CATEGORY_ITEMS.items():
                item = PrePerformanceCheckItem(
                    checklist_id=checklist.id,
                    song_id=st.song_id,
                    category=cat,
                    item_name=name,
                )
                db.add(item)

    db.commit()
    db.refresh(checklist)
    return _checklist_to_dict(checklist)


def get_checklist_by_performance(db: Session, performance_id: int) -> dict | None:
    checklist = (
        db.query(PrePerformanceChecklist)
        .filter(PrePerformanceChecklist.performance_id == performance_id)
        .first()
    )
    if not checklist:
        return None
    return _checklist_to_dict(checklist)


def get_checklist_summary(db: Session, performance_id: int) -> dict | None:
    checklist = (
        db.query(PrePerformanceChecklist)
        .filter(PrePerformanceChecklist.performance_id == performance_id)
        .first()
    )
    if not checklist:
        return None

    performance = db.query(PerformanceTask).filter(PerformanceTask.id == performance_id).first()
    name = performance.name if performance else ""

    items = checklist.items
    total = len(items)
    not_started = sum(1 for i in items if i.status == "not_started")
    in_progress = sum(1 for i in items if i.status == "in_progress")
    abnormal = sum(1 for i in items if i.status == "abnormal")
    completed = sum(1 for i in items if i.status == "completed")
    rate = round(completed / total, 2) if total > 0 else 0

    return {
        "performance_id": performance_id,
        "performance_name": name,
        "total_items": total,
        "not_started_count": not_started,
        "in_progress_count": in_progress,
        "abnormal_count": abnormal,
        "completed_count": completed,
        "completion_rate": rate,
    }


def get_all_checklist_summaries(db: Session) -> list[dict]:
    checklists = db.query(PrePerformanceChecklist).all()
    result = []
    for cl in checklists:
        s = get_checklist_summary(db, cl.performance_id)
        if s:
            result.append(s)
    return result


def get_abnormal_items(db: Session, performance_id: int) -> list[dict]:
    items = (
        db.query(PrePerformanceCheckItem)
        .join(PrePerformanceChecklist, PrePerformanceCheckItem.checklist_id == PrePerformanceChecklist.id)
        .filter(
            PrePerformanceChecklist.performance_id == performance_id,
            PrePerformanceCheckItem.status == "abnormal",
        )
        .all()
    )
    return [_check_item_abnormal_to_dict(i) for i in items]


def get_member_check_items(db: Session, performance_id: int, member_id: int) -> list[dict]:
    items = (
        db.query(PrePerformanceCheckItem)
        .join(PrePerformanceChecklist, PrePerformanceCheckItem.checklist_id == PrePerformanceChecklist.id)
        .filter(
            PrePerformanceChecklist.performance_id == performance_id,
            PrePerformanceCheckItem.responsible_member_id == member_id,
        )
        .all()
    )
    return [_check_item_to_dict(i) for i in items]


def update_check_item(db: Session, item_id: int, data: dict) -> dict | None:
    item = db.query(PrePerformanceCheckItem).filter(PrePerformanceCheckItem.id == item_id).first()
    if not item:
        return None

    if "status" in data:
        item.status = data["status"]
        if data["status"] == "completed":
            item.completed_at = datetime.now()
        elif data["status"] != "completed":
            item.completed_at = None

    if "abnormal_description" in data:
        item.abnormal_description = data["abnormal_description"]
    if "photo_url" in data:
        item.photo_url = data["photo_url"]

    db.commit()
    db.refresh(item)
    return _check_item_to_dict(item)


def add_check_item(db: Session, performance_id: int, data: dict) -> dict | None:
    checklist = (
        db.query(PrePerformanceChecklist)
        .filter(PrePerformanceChecklist.performance_id == performance_id)
        .first()
    )
    if not checklist:
        return None

    item = PrePerformanceCheckItem(
        checklist_id=checklist.id,
        song_id=data["song_id"],
        category=data["category"],
        item_name=data["item_name"],
        responsible_member_id=data.get("responsible_member_id"),
        position_id=data.get("position_id"),
        deadline=data.get("deadline"),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _check_item_to_dict(item)


def delete_check_item(db: Session, item_id: int) -> bool:
    item = db.query(PrePerformanceCheckItem).filter(PrePerformanceCheckItem.id == item_id).first()
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True


def get_pre_check_stats(db: Session) -> list[dict]:
    checklists = db.query(PrePerformanceChecklist).all()
    result = []
    for cl in checklists:
        perf = db.query(PerformanceTask).filter(PerformanceTask.id == cl.performance_id).first()
        if not perf:
            continue
        items = cl.items
        total = len(items)
        completed = sum(1 for i in items if i.status == "completed")
        abnormal = sum(1 for i in items if i.status == "abnormal")
        rate = round(completed / total, 2) if total > 0 else 0
        result.append({
            "performance_id": perf.id,
            "performance_name": perf.name,
            "performance_date": perf.start_time.strftime("%Y-%m-%d %H:%M") if perf.start_time else "",
            "total_items": total,
            "completed_count": completed,
            "abnormal_count": abnormal,
            "completion_rate": rate,
        })
    return result


def get_member_completion_rank(db: Session) -> list[dict]:
    items = (
        db.query(PrePerformanceCheckItem)
        .filter(PrePerformanceCheckItem.responsible_member_id.isnot(None))
        .all()
    )
    from collections import defaultdict

    member_stats = defaultdict(lambda: {"total": 0, "completed": 0, "abnormal": 0})
    for it in items:
        mid = it.responsible_member_id
        member_stats[mid]["total"] += 1
        if it.status == "completed":
            member_stats[mid]["completed"] += 1
        if it.status == "abnormal":
            member_stats[mid]["abnormal"] += 1

    result = []
    for mid, stats in member_stats.items():
        member = db.query(Member).filter(Member.id == mid).first()
        name = member.name if member else ""
        rate = round(stats["completed"] / stats["total"], 2) if stats["total"] > 0 else 0
        result.append({
            "member_id": mid,
            "member_name": name,
            "total_assigned": stats["total"],
            "completed_count": stats["completed"],
            "abnormal_count": stats["abnormal"],
            "completion_rate": rate,
        })

    result.sort(key=lambda x: (-x["completion_rate"], -x["completed_count"]))
    return result


def get_frequent_abnormal_types(db: Session) -> list[dict]:
    results = (
        db.query(
            PrePerformanceCheckItem.category,
            func.count(PrePerformanceCheckItem.id),
        )
        .filter(PrePerformanceCheckItem.status == "abnormal")
        .group_by(PrePerformanceCheckItem.category)
        .all()
    )
    return [{"category": r[0], "count": r[1]} for r in results]


def _perf_task_to_dict(task: PerformanceTask, include_confirmations: bool = False) -> dict:
    song_tasks_data = []
    for st in task.song_tasks:
        song_tasks_data.append({
            "id": st.id,
            "song_id": st.song_id,
            "song_name": st.song.name if st.song else "",
            "formation_id": st.formation_id,
            "formation_version": st.formation.version if st.formation else None,
            "performance_order": st.performance_order,
        })

    total = len(task.confirmations)
    confirmed = sum(1 for c in task.confirmations if c.status == "confirmed")
    unconfirmed = sum(1 for c in task.confirmations if c.status == "unconfirmed")
    leave = sum(1 for c in task.confirmations if c.status == "leave")

    result = {
        "id": task.id,
        "name": task.name,
        "location": task.location,
        "meeting_time": task.meeting_time,
        "start_time": task.start_time,
        "costume_requirements": task.costume_requirements,
        "notes": task.notes,
        "created_at": task.created_at,
        "song_tasks": song_tasks_data,
        "total_members": total,
        "confirmed_count": confirmed,
        "unconfirmed_count": unconfirmed,
        "leave_count": leave,
    }

    if include_confirmations:
        confs = []
        for c in task.confirmations:
            confs.append({
                "id": c.id,
                "performance_id": c.performance_id,
                "member_id": c.member_id,
                "member_name": c.member.name if c.member else "",
                "member_phone": c.member.phone if c.member else None,
                "status": c.status,
                "transport_mode": c.transport_mode,
                "remark": c.remark,
                "phone_reminded": c.phone_reminded or False,
                "confirmed_at": c.confirmed_at,
            })
        result["confirmations"] = confs

    return result


def get_performance_task_list(db: Session) -> list[dict]:
    tasks = db.query(PerformanceTask).order_by(PerformanceTask.start_time.desc()).all()
    return [_perf_task_to_dict(t) for t in tasks]


def create_performance_task(db: Session, data: dict) -> dict:
    task = PerformanceTask(
        name=data["name"],
        location=data["location"],
        meeting_time=data["meeting_time"],
        start_time=data["start_time"],
        costume_requirements=data.get("costume_requirements"),
        notes=data.get("notes"),
    )
    db.add(task)
    db.flush()

    song_tasks = data.get("song_tasks") or []
    for idx, st in enumerate(song_tasks):
        perf_song = PerformanceSongTask(
            performance_id=task.id,
            song_id=st["song_id"],
            formation_id=st.get("formation_id"),
            performance_order=st.get("performance_order", idx),
        )
        db.add(perf_song)

    member_ids = data.get("member_ids") or []
    for mid in member_ids:
        from models import PerformanceConfirmation
        conf = PerformanceConfirmation(
            performance_id=task.id,
            member_id=mid,
            status="unconfirmed",
        )
        db.add(conf)

    db.commit()
    db.refresh(task)
    return _perf_task_to_dict(task)


def get_performance_task_detail(db: Session, task_id: int) -> dict | None:
    task = db.query(PerformanceTask).filter(PerformanceTask.id == task_id).first()
    if not task:
        return None
    return _perf_task_to_dict(task, include_confirmations=True)


def get_performance_task_with_song_details(db: Session, task_id: int) -> dict | None:
    from models import FormationPosition, PerformanceConfirmation

    task = db.query(PerformanceTask).filter(PerformanceTask.id == task_id).first()
    if not task:
        return None

    result = _perf_task_to_dict(task, include_confirmations=True)

    song_details = []
    for st in task.song_tasks:
        total_positions = 0
        leave_members_list = []
        confirmed_subs = []
        gap_positions_list = []

        if st.formation_id:
            positions = (
                db.query(FormationPosition)
                .filter(FormationPosition.formation_id == st.formation_id)
                .all()
            )
            total_positions = len(positions)

            filled_positions = {}
            for p in positions:
                if p.member_id:
                    filled_positions[p.member_id] = p.id

            leave_conf = (
                db.query(PerformanceConfirmation)
                .filter(
                    PerformanceConfirmation.performance_id == task_id,
                    PerformanceConfirmation.status == "leave",
                )
                .all()
            )
            for c in leave_conf:
                if c.member_id in filled_positions:
                    pos_id = filled_positions[c.member_id]
                    leave_members_list.append({
                        "member_id": c.member_id,
                        "member_name": c.member.name if c.member else "",
                        "position_id": pos_id,
                    })
                    gap_positions_list.append(pos_id)

        song_details.append({
            "song_id": st.song_id,
            "song_name": st.song.name if st.song else "",
            "formation_id": st.formation_id,
            "formation_version": st.formation.version if st.formation else None,
            "total_positions": total_positions,
            "leave_members": leave_members_list,
            "confirmed_substitutes": confirmed_subs,
            "gap_positions": gap_positions_list,
        })

    result["song_details"] = song_details
    return result


def update_performance_task(db: Session, task_id: int, data: dict) -> dict | None:
    from models import PerformanceConfirmation

    task = db.query(PerformanceTask).filter(PerformanceTask.id == task_id).first()
    if not task:
        return None

    if "name" in data:
        task.name = data["name"]
    if "location" in data:
        task.location = data["location"]
    if "meeting_time" in data:
        task.meeting_time = data["meeting_time"]
    if "start_time" in data:
        task.start_time = data["start_time"]
    if "costume_requirements" in data:
        task.costume_requirements = data["costume_requirements"]
    if "notes" in data:
        task.notes = data["notes"]

    if "song_tasks" in data and data["song_tasks"] is not None:
        for st in task.song_tasks:
            db.delete(st)
        db.flush()
        for idx, st in enumerate(data["song_tasks"]):
            perf_song = PerformanceSongTask(
                performance_id=task.id,
                song_id=st["song_id"],
                formation_id=st.get("formation_id"),
                performance_order=st.get("performance_order", idx),
            )
            db.add(perf_song)

    if "member_ids" in data and data["member_ids"] is not None:
        existing = {c.member_id: c for c in task.confirmations}
        new_ids = set(data["member_ids"])
        old_ids = set(existing.keys())

        for old_id in old_ids - new_ids:
            db.delete(existing[old_id])

        for new_id in new_ids - old_ids:
            conf = PerformanceConfirmation(
                performance_id=task.id,
                member_id=new_id,
                status="unconfirmed",
            )
            db.add(conf)

    db.commit()
    db.refresh(task)
    return _perf_task_to_dict(task)


def delete_performance_task(db: Session, task_id: int) -> bool:
    task = db.query(PerformanceTask).filter(PerformanceTask.id == task_id).first()
    if not task:
        return False
    db.delete(task)
    db.commit()
    return True


def update_performance_confirmation(db: Session, task_id: int, member_id: int, data: dict) -> dict | None:
    from models import PerformanceConfirmation

    conf = (
        db.query(PerformanceConfirmation)
        .filter(
            PerformanceConfirmation.performance_id == task_id,
            PerformanceConfirmation.member_id == member_id,
        )
        .first()
    )
    if not conf:
        return None

    if "status" in data:
        conf.status = data["status"]
        if data["status"] == "confirmed":
            conf.confirmed_at = datetime.now()
    if "transport_mode" in data:
        conf.transport_mode = data["transport_mode"]
    if "remark" in data:
        conf.remark = data["remark"]
    if "phone_reminded" in data:
        conf.phone_reminded = data["phone_reminded"]

    db.commit()
    db.refresh(conf)
    return {
        "id": conf.id,
        "performance_id": conf.performance_id,
        "member_id": conf.member_id,
        "member_name": conf.member.name if conf.member else "",
        "member_phone": conf.member.phone if conf.member else None,
        "status": conf.status,
        "transport_mode": conf.transport_mode,
        "remark": conf.remark,
        "phone_reminded": conf.phone_reminded or False,
        "confirmed_at": conf.confirmed_at,
    }


def mark_phone_reminded(db: Session, task_id: int, member_id: int) -> dict | None:
    return update_performance_confirmation(db, task_id, member_id, {"phone_reminded": True})


def get_performance_confirmation_stats(db: Session) -> list[dict]:
    from models import PerformanceConfirmation

    tasks = db.query(PerformanceTask).order_by(PerformanceTask.start_time.desc()).all()
    result = []
    for task in tasks:
        total = len(task.confirmations)
        confirmed = sum(1 for c in task.confirmations if c.status == "confirmed")
        unconfirmed = sum(1 for c in task.confirmations if c.status == "unconfirmed")
        leave = sum(1 for c in task.confirmations if c.status == "leave")
        reminded = sum(1 for c in task.confirmations if c.phone_reminded)

        conf_rate = round(confirmed / total, 2) if total > 0 else 0
        remind_rate = round(reminded / total, 2) if total > 0 else 0

        result.append({
            "performance_id": task.id,
            "performance_name": task.name,
            "performance_date": task.start_time.strftime("%Y-%m-%d %H:%M") if task.start_time else "",
            "total_members": total,
            "confirmed_count": confirmed,
            "unconfirmed_count": unconfirmed,
            "leave_count": leave,
            "confirmation_rate": conf_rate,
            "phone_reminded_count": reminded,
            "phone_reminder_rate": remind_rate,
        })
    return result


HEALTH_CONDITION_DISPLAY = {
    "heart_disease": "心脏病",
    "hypertension": "高血压",
    "diabetes": "糖尿病",
    "asthma": "哮喘",
    "joint_pain": "关节疼痛",
    "dizziness": "眩晕症",
    "allergy": "过敏",
    "injury": "旧伤",
    "other": "其他",
}

GROUND_CONDITION_DISPLAY = {
    "good": "良好",
    "fair": "一般",
    "poor": "较差",
}

WEATHER_CONDITION_DISPLAY = {
    "sunny": "晴天",
    "cloudy": "多云",
    "rainy": "雨天",
    "windy": "大风",
    "hot": "高温",
    "cold": "寒冷",
}

RISK_LEVEL_DISPLAY = {
    "low": "低风险",
    "medium": "中风险",
    "high": "高风险",
    "critical": "极高风险",
}

INCIDENT_TYPE_DISPLAY = {
    "sprain": "扭伤",
    "dizziness": "头晕",
    "fall": "摔倒",
    "cable_trip": "设备绊线",
    "heat_stroke": "中暑",
    "dehydration": "脱水",
    "heart_issue": "心脏不适",
    "breathing_difficulty": "呼吸困难",
    "injury": "受伤",
    "other": "其他",
}

INCIDENT_SEVERITY_DISPLAY = {
    "minor": "轻微",
    "moderate": "中等",
    "severe": "严重",
    "critical": "危急",
}

HAZARD_TYPE_DISPLAY = {
    "slippery_floor": "地面湿滑",
    "obstacle": "障碍物",
    "loose_cable": "电线松动",
    "uneven_ground": "地面不平",
    "poor_lighting": "照明不良",
    "sharp_edge": "尖锐边缘",
    "lack_of_first_aid": "缺乏急救设备",
    "other": "其他",
}

RISK_MEMBER_STATUS_DISPLAY = {
    "pending": "待处理",
    "adjusted": "已调整站位",
    "resting": "安排休息",
    "monitoring": "持续观察",
}


def _health_record_to_dict(record: MemberHealthRecord) -> dict:
    return {
        "id": record.id,
        "member_id": record.member_id,
        "member_name": record.member.name if record.member else "",
        "record_date": record.record_date,
        "condition_type": record.condition_type,
        "description": record.description,
        "is_chronic": record.is_chronic,
        "needs_accommodation": record.needs_accommodation,
        "accommodation_notes": record.accommodation_notes,
        "created_at": record.created_at,
    }


def get_health_records(db: Session, member_id: int | None = None) -> list[dict]:
    query = db.query(MemberHealthRecord)
    if member_id:
        query = query.filter(MemberHealthRecord.member_id == member_id)
    records = query.order_by(MemberHealthRecord.record_date.desc()).all()
    return [_health_record_to_dict(r) for r in records]


def get_health_record(db: Session, record_id: int) -> dict | None:
    record = db.query(MemberHealthRecord).filter(MemberHealthRecord.id == record_id).first()
    if not record:
        return None
    return _health_record_to_dict(record)


def create_health_record(db: Session, data: dict) -> dict:
    record = MemberHealthRecord(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return _health_record_to_dict(record)


def update_health_record(db: Session, record_id: int, data: dict) -> dict | None:
    record = db.query(MemberHealthRecord).filter(MemberHealthRecord.id == record_id).first()
    if not record:
        return None
    for key, value in data.items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return _health_record_to_dict(record)


def delete_health_record(db: Session, record_id: int) -> bool:
    record = db.query(MemberHealthRecord).filter(MemberHealthRecord.id == record_id).first()
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True


def get_member_with_health(db: Session, member_id: int) -> dict | None:
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        return None
    song_ids = [ms.song_id for ms in member.member_songs]
    sub_positions = [sp.position_label for sp in member.substitute_positions]
    health_records = [_health_record_to_dict(hr) for hr in member.health_records]
    return {
        "id": member.id,
        "name": member.name,
        "height_range": member.height_range,
        "phone": member.phone,
        "age": member.age,
        "emergency_contact": member.emergency_contact,
        "song_ids": song_ids,
        "substitute_positions": sub_positions,
        "created_at": member.created_at,
        "health_records": health_records,
    }


def _safety_checklist_to_dict(checklist: TrainingSafetyChecklist) -> dict:
    return {
        "id": checklist.id,
        "rehearsal_id": checklist.rehearsal_id,
        "song_id": checklist.rehearsal.song_id if checklist.rehearsal else None,
        "song_name": checklist.rehearsal.song.name if checklist.rehearsal and checklist.rehearsal.song else "",
        "rehearsal_date": checklist.rehearsal.date if checklist.rehearsal else None,
        "ground_condition": checklist.ground_condition,
        "ground_notes": checklist.ground_notes,
        "audio_cables_arranged": checklist.audio_cables_arranged,
        "audio_cables_notes": checklist.audio_cables_notes,
        "members_illness_reported": checklist.members_illness_reported,
        "illness_notes": checklist.illness_notes,
        "weather_temperature": checklist.weather_temperature,
        "weather_condition": checklist.weather_condition,
        "weather_notes": checklist.weather_notes,
        "drinking_water_provided": checklist.drinking_water_provided,
        "rest_schedule_arranged": checklist.rest_schedule_arranged,
        "rest_notes": checklist.rest_notes,
        "high_risk_moves_reminded": checklist.high_risk_moves_reminded,
        "high_risk_moves_notes": checklist.high_risk_moves_notes,
        "risk_level": checklist.risk_level,
        "risk_assessment_notes": checklist.risk_assessment_notes,
        "created_by": checklist.created_by,
        "created_by_name": "",
        "created_at": checklist.created_at,
        "incident_count": len(checklist.incidents),
    }


def get_safety_checklists(db: Session, rehearsal_id: int | None = None) -> list[dict]:
    query = db.query(TrainingSafetyChecklist)
    if rehearsal_id:
        query = query.filter(TrainingSafetyChecklist.rehearsal_id == rehearsal_id)
    checklists = query.order_by(TrainingSafetyChecklist.created_at.desc()).all()
    return [_safety_checklist_to_dict(c) for c in checklists]


def get_safety_checklist(db: Session, checklist_id: int) -> dict | None:
    checklist = db.query(TrainingSafetyChecklist).filter(TrainingSafetyChecklist.id == checklist_id).first()
    if not checklist:
        return None
    return _safety_checklist_to_dict(checklist)


def _calculate_risk_level(db: Session, checklist: TrainingSafetyChecklist) -> tuple[str, int, list[str], list[str]]:
    risk_score = 0
    risk_factors = []
    recommendations = []

    if checklist.ground_condition == "poor":
        risk_score += 3
        risk_factors.append("场地地面情况较差")
        recommendations.append("建议更换训练场地或暂停高强度动作")
    elif checklist.ground_condition == "fair":
        risk_score += 1
        risk_factors.append("场地地面情况一般")
        recommendations.append("提醒队员注意地面状况")

    if not checklist.audio_cables_arranged:
        risk_score += 2
        risk_factors.append("音响电线未整理")
        recommendations.append("请立即整理音响电线，避免绊倒风险")

    if checklist.members_illness_reported:
        risk_score += 2
        risk_factors.append("有队员报告身体不适")
        recommendations.append("重点关注身体不适队员，必要时安排休息")

    if checklist.weather_temperature is not None:
        if checklist.weather_temperature >= 35:
            risk_score += 3
            risk_factors.append(f"高温天气({checklist.weather_temperature}°C)")
            recommendations.append("减少训练强度，增加饮水和休息频率，注意防暑")
        elif checklist.weather_temperature <= 5:
            risk_score += 2
            risk_factors.append(f"低温天气({checklist.weather_temperature}°C)")
            recommendations.append("做好热身准备，注意保暖")

    if checklist.weather_condition in ["rainy", "windy"]:
        risk_score += 2
        risk_factors.append(f"{WEATHER_CONDITION_DISPLAY.get(checklist.weather_condition, '')}天气")
        recommendations.append("考虑改为室内训练或调整训练内容")

    if not checklist.drinking_water_provided:
        risk_score += 1
        risk_factors.append("未准备饮用水")
        recommendations.append("请准备充足的饮用水")

    if not checklist.rest_schedule_arranged:
        risk_score += 1
        risk_factors.append("未安排休息计划")
        recommendations.append("请合理安排训练和休息时间")

    if not checklist.high_risk_moves_reminded:
        risk_score += 1
        risk_factors.append("未进行高风险动作提示")
        recommendations.append("训练前提醒高风险动作注意事项")

    rehearsal = checklist.rehearsal
    if rehearsal:
        song_member_ids = [ms.member_id for ms in db.query(MemberSong).filter(MemberSong.song_id == rehearsal.song_id).all()]
        members = db.query(Member).filter(Member.id.in_(song_member_ids)).all()
        for member in members:
            if member.age is not None:
                if member.age >= 65:
                    risk_score += 1
                    risk_factors.append(f"队员{member.name}年龄较大({member.age}岁)")
                elif member.age <= 12:
                    risk_score += 1
                    risk_factors.append(f"队员{member.name}年龄较小({member.age}岁)")
            health_records = member.health_records
            for hr in health_records:
                if hr.is_chronic and hr.condition_type in ["heart_disease", "hypertension", "diabetes", "asthma"]:
                    risk_score += 2
                    risk_factors.append(f"队员{member.name}有慢性{HEALTH_CONDITION_DISPLAY.get(hr.condition_type, hr.condition_type)}病史")

    if risk_score >= 10:
        risk_level = "critical"
    elif risk_score >= 6:
        risk_level = "high"
    elif risk_score >= 3:
        risk_level = "medium"
    else:
        risk_level = "low"

    return risk_level, risk_score, risk_factors, recommendations


def _identify_risk_members(db: Session, checklist: TrainingSafetyChecklist) -> list[dict]:
    risk_members = []
    rehearsal = checklist.rehearsal
    if not rehearsal:
        return risk_members

    song_member_ids = [ms.member_id for ms in db.query(MemberSong).filter(MemberSong.song_id == rehearsal.song_id).all()]
    members = db.query(Member).filter(Member.id.in_(song_member_ids)).all()

    for member in members:
        risk_factors = []
        risk_score = 0
        recommendation = ""

        if member.age is not None:
            if member.age >= 65:
                risk_score += 2
                risk_factors.append(f"年龄较大({member.age}岁)")
            elif member.age <= 12:
                risk_score += 1
                risk_factors.append(f"年龄较小({member.age}岁)")

        health_records = member.health_records
        for hr in health_records:
            if hr.is_chronic:
                condition_name = HEALTH_CONDITION_DISPLAY.get(hr.condition_type, hr.condition_type)
                risk_score += 3 if hr.condition_type in ["heart_disease", "hypertension"] else 2
                risk_factors.append(f"慢性{condition_name}")
            if hr.condition_type == "joint_pain":
                risk_score += 1
                risk_factors.append("关节疼痛史")
            if hr.condition_type == "dizziness":
                risk_score += 2
                risk_factors.append("眩晕史")

        if risk_score >= 5:
            risk_level = "high"
        elif risk_score >= 3:
            risk_level = "medium"
        elif risk_score >= 1:
            risk_level = "low"
        else:
            continue

        if risk_level in ["high", "medium"]:
            if risk_level == "high":
                recommendation = "建议安排旁观休息或减少高强度动作参与"
            else:
                recommendation = "建议调整至低强度站位，避免剧烈动作"

            risk_members.append({
                "checklist_id": checklist.id,
                "member_id": member.id,
                "member_name": member.name,
                "member_age": member.age,
                "risk_level": risk_level,
                "risk_factors": "、".join(risk_factors),
                "recommendation": recommendation,
            })

    return risk_members


def create_safety_checklist(db: Session, data: dict) -> dict:
    checklist = TrainingSafetyChecklist(**data)
    db.add(checklist)
    db.flush()

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

    db.commit()
    db.refresh(checklist)
    return _safety_checklist_to_dict(checklist)


def update_safety_checklist(db: Session, checklist_id: int, data: dict) -> dict | None:
    checklist = db.query(TrainingSafetyChecklist).filter(TrainingSafetyChecklist.id == checklist_id).first()
    if not checklist:
        return None
    for key, value in data.items():
        setattr(checklist, key, value)

    risk_level, risk_score, risk_factors, recommendations = _calculate_risk_level(db, checklist)
    checklist.risk_level = risk_level
    checklist.risk_assessment_notes = "、".join(risk_factors) if risk_factors else None

    existing_risk_members = db.query(RiskMember).filter(RiskMember.checklist_id == checklist_id).all()
    for rm in existing_risk_members:
        db.delete(rm)
    db.flush()

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

    db.commit()
    db.refresh(checklist)
    return _safety_checklist_to_dict(checklist)


def delete_safety_checklist(db: Session, checklist_id: int) -> bool:
    checklist = db.query(TrainingSafetyChecklist).filter(TrainingSafetyChecklist.id == checklist_id).first()
    if not checklist:
        return False
    db.delete(checklist)
    db.commit()
    return True


def assess_risks(db: Session, checklist_id: int) -> dict | None:
    checklist = db.query(TrainingSafetyChecklist).filter(TrainingSafetyChecklist.id == checklist_id).first()
    if not checklist:
        return None

    risk_level, risk_score, risk_factors, recommendations = _calculate_risk_level(db, checklist)

    checklist.risk_level = risk_level
    checklist.risk_assessment_notes = "、".join(risk_factors) if risk_factors else None

    existing_risk_members = db.query(RiskMember).filter(RiskMember.checklist_id == checklist_id).all()
    for rm in existing_risk_members:
        db.delete(rm)
    db.flush()

    risk_member_data = _identify_risk_members(db, checklist)
    high_risk_members = []
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
        high_risk_members.append(_risk_member_to_dict(risk_member))

    db.commit()

    weather_warning = None
    if checklist.weather_temperature is not None and checklist.weather_temperature >= 35:
        weather_warning = f"高温预警：当前温度{checklist.weather_temperature}°C，请减少高强度训练，注意防暑降温"
    elif checklist.weather_condition == "rainy":
        weather_warning = "雨天预警：场地可能湿滑，建议改为室内训练"

    return {
        "checklist_id": checklist_id,
        "overall_risk_level": risk_level,
        "risk_score": risk_score,
        "risk_factors": risk_factors,
        "recommendations": recommendations,
        "high_risk_members": high_risk_members,
        "weather_warning": weather_warning,
    }


def _emergency_incident_to_dict(incident: EmergencyIncident) -> dict:
    return {
        "id": incident.id,
        "checklist_id": incident.checklist_id,
        "rehearsal_id": incident.checklist.rehearsal_id if incident.checklist else None,
        "member_id": incident.member_id,
        "member_name": incident.member.name if incident.member else "",
        "member_phone": incident.member.phone if incident.member else None,
        "emergency_contact": incident.member.emergency_contact if incident.member else None,
        "incident_type": incident.incident_type,
        "song_id": incident.song_id,
        "song_name": incident.song.name if incident.song else "",
        "position_id": incident.position_id,
        "formation_position": incident.formation_position,
        "description": incident.description,
        "severity": incident.severity,
        "treatment_given": incident.treatment_given,
        "treated_by": incident.treated_by,
        "family_notified": incident.family_notified,
        "family_notification_details": incident.family_notification_details,
        "community_leader_notified": incident.community_leader_notified,
        "community_notification_details": incident.community_notification_details,
        "follow_up_required": incident.follow_up_required,
        "follow_up_notes": incident.follow_up_notes,
        "incident_time": incident.incident_time,
        "resolved": incident.resolved,
        "resolved_time": incident.resolved_time,
    }


def get_emergency_incidents(db: Session, checklist_id: int | None = None, member_id: int | None = None) -> list[dict]:
    query = db.query(EmergencyIncident)
    if checklist_id:
        query = query.filter(EmergencyIncident.checklist_id == checklist_id)
    if member_id:
        query = query.filter(EmergencyIncident.member_id == member_id)
    incidents = query.order_by(EmergencyIncident.incident_time.desc()).all()
    return [_emergency_incident_to_dict(i) for i in incidents]


def get_emergency_incident(db: Session, incident_id: int) -> dict | None:
    incident = db.query(EmergencyIncident).filter(EmergencyIncident.id == incident_id).first()
    if not incident:
        return None
    return _emergency_incident_to_dict(incident)


def create_emergency_incident(db: Session, data: dict) -> dict:
    incident = EmergencyIncident(**data)
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return _emergency_incident_to_dict(incident)


def update_emergency_incident(db: Session, incident_id: int, data: dict) -> dict | None:
    incident = db.query(EmergencyIncident).filter(EmergencyIncident.id == incident_id).first()
    if not incident:
        return None
    for key, value in data.items():
        setattr(incident, key, value)
        if key == "resolved" and value and incident.resolved_time is None:
            incident.resolved_time = datetime.now()
    db.commit()
    db.refresh(incident)
    return _emergency_incident_to_dict(incident)


def resolve_emergency_incident(db: Session, incident_id: int) -> dict | None:
    incident = db.query(EmergencyIncident).filter(EmergencyIncident.id == incident_id).first()
    if not incident:
        return None
    incident.resolved = True
    incident.resolved_time = datetime.now()
    db.commit()
    db.refresh(incident)
    return _emergency_incident_to_dict(incident)


def _risk_member_to_dict(rm: RiskMember) -> dict:
    return {
        "id": rm.id,
        "checklist_id": rm.checklist_id,
        "rehearsal_id": rm.checklist.rehearsal_id if rm.checklist else None,
        "member_id": rm.member_id,
        "member_name": rm.member.name if rm.member else "",
        "member_age": rm.member.age if rm.member else None,
        "risk_level": rm.risk_level,
        "risk_factors": rm.risk_factors,
        "recommendation": rm.recommendation,
        "action_taken": rm.action_taken,
        "status": rm.status,
        "created_at": rm.created_at,
    }


def get_risk_members(db: Session, checklist_id: int | None = None, member_id: int | None = None) -> list[dict]:
    query = db.query(RiskMember)
    if checklist_id:
        query = query.filter(RiskMember.checklist_id == checklist_id)
    if member_id:
        query = query.filter(RiskMember.member_id == member_id)
    risk_members = query.order_by(RiskMember.created_at.desc()).all()
    return [_risk_member_to_dict(rm) for rm in risk_members]


def get_risk_member(db: Session, risk_member_id: int) -> dict | None:
    rm = db.query(RiskMember).filter(RiskMember.id == risk_member_id).first()
    if not rm:
        return None
    return _risk_member_to_dict(rm)


def create_risk_member(db: Session, data: dict) -> dict:
    rm = RiskMember(**data)
    db.add(rm)
    db.commit()
    db.refresh(rm)
    return _risk_member_to_dict(rm)


def update_risk_member(db: Session, risk_member_id: int, data: dict) -> dict | None:
    rm = db.query(RiskMember).filter(RiskMember.id == risk_member_id).first()
    if not rm:
        return None
    for key, value in data.items():
        setattr(rm, key, value)
    db.commit()
    db.refresh(rm)
    return _risk_member_to_dict(rm)


def _venue_hazard_to_dict(hazard: VenueHazardRecord) -> dict:
    return {
        "id": hazard.id,
        "rehearsal_id": hazard.rehearsal_id,
        "song_id": hazard.rehearsal.song_id if hazard.rehearsal else None,
        "song_name": hazard.rehearsal.song.name if hazard.rehearsal and hazard.rehearsal.song else "",
        "hazard_type": hazard.hazard_type,
        "location": hazard.location,
        "description": hazard.description,
        "severity": hazard.severity,
        "reported_by": hazard.reported_by,
        "reported_by_name": "",
        "resolved": hazard.resolved,
        "resolution_notes": hazard.resolution_notes,
        "resolved_at": hazard.resolved_at,
        "created_at": hazard.created_at,
    }


def get_venue_hazards(db: Session, rehearsal_id: int | None = None, unresolved_only: bool = False) -> list[dict]:
    query = db.query(VenueHazardRecord)
    if rehearsal_id:
        query = query.filter(VenueHazardRecord.rehearsal_id == rehearsal_id)
    if unresolved_only:
        query = query.filter(VenueHazardRecord.resolved == False)
    hazards = query.order_by(VenueHazardRecord.created_at.desc()).all()
    return [_venue_hazard_to_dict(h) for h in hazards]


def get_venue_hazard(db: Session, hazard_id: int) -> dict | None:
    hazard = db.query(VenueHazardRecord).filter(VenueHazardRecord.id == hazard_id).first()
    if not hazard:
        return None
    return _venue_hazard_to_dict(hazard)


def create_venue_hazard(db: Session, data: dict) -> dict:
    hazard = VenueHazardRecord(**data)
    db.add(hazard)
    db.commit()
    db.refresh(hazard)
    return _venue_hazard_to_dict(hazard)


def update_venue_hazard(db: Session, hazard_id: int, data: dict) -> dict | None:
    hazard = db.query(VenueHazardRecord).filter(VenueHazardRecord.id == hazard_id).first()
    if not hazard:
        return None
    for key, value in data.items():
        setattr(hazard, key, value)
        if key == "resolved" and value and hazard.resolved_at is None:
            hazard.resolved_at = datetime.now()
    db.commit()
    db.refresh(hazard)
    return _venue_hazard_to_dict(hazard)


def resolve_venue_hazard(db: Session, hazard_id: int) -> dict | None:
    hazard = db.query(VenueHazardRecord).filter(VenueHazardRecord.id == hazard_id).first()
    if not hazard:
        return None
    hazard.resolved = True
    hazard.resolved_at = datetime.now()
    db.commit()
    db.refresh(hazard)
    return _venue_hazard_to_dict(hazard)


def get_safety_overview_stats(db: Session) -> dict:
    total_checklists = db.query(func.count(TrainingSafetyChecklist.id)).scalar()
    total_incidents = db.query(func.count(EmergencyIncident.id)).scalar()
    total_hazards = db.query(func.count(VenueHazardRecord.id)).scalar()

    high_risk_members_count = db.query(func.count(func.distinct(RiskMember.member_id))).filter(
        RiskMember.risk_level.in_(["high", "critical"])
    ).scalar()

    incident_rate = round(total_incidents / total_checklists, 2) if total_checklists > 0 else 0

    resolved_hazards = db.query(func.count(VenueHazardRecord.id)).filter(
        VenueHazardRecord.resolved == True
    ).scalar()
    hazard_resolution_rate = round(resolved_hazards / total_hazards, 2) if total_hazards > 0 else 0

    risk_level_counts = db.query(
        TrainingSafetyChecklist.risk_level,
        func.count(TrainingSafetyChecklist.id)
    ).group_by(TrainingSafetyChecklist.risk_level).all()
    risk_level_map = {r[0]: r[1] for r in risk_level_counts}
    if risk_level_map.get("critical", 0) > 0:
        avg_risk_level = "critical"
    elif risk_level_map.get("high", 0) > risk_level_map.get("medium", 0) and risk_level_map.get("high", 0) > risk_level_map.get("low", 0):
        avg_risk_level = "high"
    elif risk_level_map.get("medium", 0) > risk_level_map.get("low", 0):
        avg_risk_level = "medium"
    else:
        avg_risk_level = "low"

    return {
        "total_checklists": total_checklists,
        "total_incidents": total_incidents,
        "total_hazards": total_hazards,
        "high_risk_member_count": high_risk_members_count,
        "incident_rate": incident_rate,
        "hazard_resolution_rate": hazard_resolution_rate,
        "avg_risk_level": avg_risk_level,
    }


def get_incident_type_stats(db: Session) -> list[dict]:
    total_incidents = db.query(func.count(EmergencyIncident.id)).scalar()
    results = db.query(
        EmergencyIncident.incident_type,
        func.count(EmergencyIncident.id)
    ).group_by(EmergencyIncident.incident_type).all()
    return [
        {
            "incident_type": r[0],
            "count": r[1],
            "rate": round(r[1] / total_incidents, 2) if total_incidents > 0 else 0,
        }
        for r in results
    ]


def get_rehearsal_safety_stats(db: Session) -> list[dict]:
    checklists = db.query(TrainingSafetyChecklist).order_by(TrainingSafetyChecklist.created_at.desc()).all()
    results = []
    for cl in checklists:
        incident_count = len(cl.incidents)
        hazard_count = db.query(func.count(VenueHazardRecord.id)).filter(
            VenueHazardRecord.rehearsal_id == cl.rehearsal_id
        ).scalar()
        high_risk_count = len([rm for rm in cl.risk_members if rm.risk_level in ["high", "critical"]])
        family_notified_count = sum(1 for inc in cl.incidents if inc.family_notified)

        song_name = cl.rehearsal.song.name if cl.rehearsal and cl.rehearsal.song else ""
        rehearsal_date = cl.rehearsal.date.strftime("%Y-%m-%d") if cl.rehearsal and cl.rehearsal.date else ""

        results.append({
            "rehearsal_id": cl.rehearsal_id,
            "rehearsal_date": rehearsal_date,
            "song_name": song_name,
            "risk_level": cl.risk_level,
            "incident_count": incident_count,
            "hazard_count": hazard_count,
            "high_risk_member_count": high_risk_count,
            "family_notified_count": family_notified_count,
        })
    return results


def get_high_risk_members_stats(db: Session) -> list[dict]:
    from collections import defaultdict

    member_incidents = defaultdict(int)
    member_last_incident = {}
    incidents = db.query(EmergencyIncident).all()
    for inc in incidents:
        member_incidents[inc.member_id] += 1
        if inc.member_id not in member_last_incident or (inc.incident_time and inc.incident_time > member_last_incident[inc.member_id]):
            member_last_incident[inc.member_id] = inc.incident_time

    high_risk_members = db.query(RiskMember).filter(
        RiskMember.risk_level.in_(["high", "medium"])
    ).all()

    member_map = {}
    for rm in high_risk_members:
        mid = rm.member_id
        if mid not in member_map:
            member = db.query(Member).filter(Member.id == mid).first()
            health_conditions = []
            for hr in member.health_records if member else []:
                cond_name = HEALTH_CONDITION_DISPLAY.get(hr.condition_type, hr.condition_type)
                if hr.is_chronic:
                    cond_name = "慢性" + cond_name
                health_conditions.append(cond_name)

            member_map[mid] = {
                "member_id": mid,
                "member_name": member.name if member else "",
                "member_age": member.age if member else None,
                "incident_count": member_incidents.get(mid, 0),
                "risk_level": rm.risk_level,
                "health_conditions": health_conditions,
                "last_incident_date": member_last_incident.get(mid),
            }
        elif rm.risk_level == "high" and member_map[mid]["risk_level"] != "high":
            member_map[mid]["risk_level"] = "high"

    result = list(member_map.values())
    result.sort(key=lambda x: (0 if x["risk_level"] == "high" else 1, -x["incident_count"]))
    for item in result:
        if item["last_incident_date"]:
            item["last_incident_date"] = item["last_incident_date"].strftime("%Y-%m-%d")
    return result


def get_hazard_type_stats(db: Session) -> list[dict]:
    results = db.query(
        VenueHazardRecord.hazard_type,
        func.count(VenueHazardRecord.id),
        func.sum(func.iif(VenueHazardRecord.resolved == False, 1, 0)),
    ).group_by(VenueHazardRecord.hazard_type).all()
    return [
        {
            "hazard_type": r[0],
            "count": r[1],
            "unresolved_count": r[2] or 0,
        }
        for r in results
    ]


def get_emergency_response_stats(db: Session) -> dict:
    total_incidents = db.query(func.count(EmergencyIncident.id)).scalar()
    resolved_count = db.query(func.count(EmergencyIncident.id)).filter(
        EmergencyIncident.resolved == True
    ).scalar()
    family_notified_count = db.query(func.count(EmergencyIncident.id)).filter(
        EmergencyIncident.family_notified == True
    ).scalar()
    community_notified_count = db.query(func.count(EmergencyIncident.id)).filter(
        EmergencyIncident.community_leader_notified == True
    ).scalar()

    resolution_rate = round(resolved_count / total_incidents, 2) if total_incidents > 0 else 0
    family_notification_rate = round(family_notified_count / total_incidents, 2) if total_incidents > 0 else 0
    community_notification_rate = round(community_notified_count / total_incidents, 2) if total_incidents > 0 else 0

    avg_response_time = None
    resolved_incidents = db.query(EmergencyIncident).filter(
        EmergencyIncident.resolved == True,
        EmergencyIncident.incident_time.isnot(None),
        EmergencyIncident.resolved_time.isnot(None),
    ).all()
    if resolved_incidents:
        total_minutes = 0
        for inc in resolved_incidents:
            delta = inc.resolved_time - inc.incident_time
            total_minutes += delta.total_seconds() / 60
        avg_response_time = round(total_minutes / len(resolved_incidents), 1)

    return {
        "total_incidents": total_incidents,
        "resolved_count": resolved_count,
        "resolution_rate": resolution_rate,
        "family_notified_count": family_notified_count,
        "family_notification_rate": family_notification_rate,
        "community_notified_count": community_notified_count,
        "community_notification_rate": community_notification_rate,
        "avg_response_time_minutes": avg_response_time,
    }
