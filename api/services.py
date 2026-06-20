import math
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import (
    Song, Member, MemberSong, MemberSubstitutePosition,
    Formation, FormationPosition, Rehearsal, RehearsalError,
    Attendance, SubstituteAssignment,
    PerformanceTask, PerformanceSongTask, PrePerformanceChecklist, PrePerformanceCheckItem,
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
