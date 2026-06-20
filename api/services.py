import math
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import (
    Song, Member, MemberSong, MemberSubstitutePosition,
    Formation, FormationPosition, Rehearsal, RehearsalError,
    Attendance, SubstituteAssignment,
    PerformanceTask, PerformanceSongTask, PerformanceConfirmation,
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
    latest_formation = (
        db.query(Formation)
        .filter(Formation.song_id == song_id)
        .order_by(Formation.version.desc())
        .first()
    )

    absent_position_ids = []
    if latest_formation:
        absent_positions = (
            db.query(FormationPosition)
            .filter(
                FormationPosition.formation_id == latest_formation.id,
                FormationPosition.member_id == absent_member_id,
            )
            .all()
        )
        absent_position_ids = [p.position_id for p in absent_positions]

    absent_member = db.query(Member).filter(Member.id == absent_member_id).first()
    absent_height = absent_member.height_range if absent_member else "medium"

    absent_member_songs = db.query(MemberSong).filter(MemberSong.member_id == absent_member_id).all()
    absent_song_ids = {ms.song_id for ms in absent_member_songs}

    all_member_songs = db.query(MemberSong).filter(MemberSong.song_id == song_id).all()
    eligible_member_ids = {ms.member_id for ms in all_member_songs} - {absent_member_id}

    attendance_records = (
        db.query(Attendance)
        .filter(Attendance.song_id == song_id)
        .order_by(Attendance.date.desc())
        .all()
    )
    latest_attendance = {}
    for rec in attendance_records:
        if rec.member_id not in latest_attendance:
            latest_attendance[rec.member_id] = rec.status

    present_member_ids = {
        mid for mid in eligible_member_ids
        if latest_attendance.get(mid, "present") == "present"
    }

    results = []
    for mid in present_member_ids:
        member = db.query(Member).filter(Member.id == mid).first()
        if not member:
            continue

        sub_positions = (
            db.query(MemberSubstitutePosition)
            .filter(MemberSubstitutePosition.member_id == mid)
            .all()
        )
        sub_labels = {sp.position_label for sp in sub_positions}
        matched = [pid for pid in absent_position_ids if pid in sub_labels]

        member_song_ids = {
            ms.song_id
            for ms in db.query(MemberSong).filter(MemberSong.member_id == mid).all()
        }
        common_songs = len(absent_song_ids & member_song_ids)

        height_match = 1 if member.height_range == absent_height else 0

        priority = len(matched) * 3 + common_songs * 2 + height_match

        results.append({
            "member_id": mid,
            "name": member.name,
            "matched_positions": matched if matched else [],
            "priority": priority,
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

    song_tasks_data = data.get("song_tasks", [])
    for st in song_tasks_data:
        song_task = PerformanceSongTask(
            performance_id=task.id,
            song_id=st["song_id"],
            formation_id=st.get("formation_id"),
            performance_order=st.get("performance_order", 0),
        )
        db.add(song_task)

    member_ids = data.get("member_ids", [])
    for mid in member_ids:
        conf = PerformanceConfirmation(
            performance_id=task.id,
            member_id=mid,
            status="unconfirmed",
            phone_reminded=False,
        )
        db.add(conf)

    db.commit()
    db.refresh(task)
    return _performance_task_to_dict(db, task)


def update_performance_task(db: Session, task_id: int, data: dict) -> dict:
    task = db.query(PerformanceTask).filter(PerformanceTask.id == task_id).first()
    if not task:
        return None

    if "name" in data and data["name"] is not None:
        task.name = data["name"]
    if "location" in data and data["location"] is not None:
        task.location = data["location"]
    if "meeting_time" in data and data["meeting_time"] is not None:
        task.meeting_time = data["meeting_time"]
    if "start_time" in data and data["start_time"] is not None:
        task.start_time = data["start_time"]
    if "costume_requirements" in data and data["costume_requirements"] is not None:
        task.costume_requirements = data["costume_requirements"]
    if "notes" in data and data["notes"] is not None:
        task.notes = data["notes"]

    if "song_tasks" in data and data["song_tasks"] is not None:
        db.query(PerformanceSongTask).filter(PerformanceSongTask.performance_id == task_id).delete()
        for st in data["song_tasks"]:
            song_task = PerformanceSongTask(
                performance_id=task.id,
                song_id=st["song_id"],
                formation_id=st.get("formation_id"),
                performance_order=st.get("performance_order", 0),
            )
            db.add(song_task)

    if "member_ids" in data and data["member_ids"] is not None:
        existing_confs = db.query(PerformanceConfirmation).filter(
            PerformanceConfirmation.performance_id == task_id
        ).all()
        existing_member_ids = {c.member_id for c in existing_confs}
        new_member_ids = set(data["member_ids"])

        for mid in existing_member_ids - new_member_ids:
            db.query(PerformanceConfirmation).filter(
                PerformanceConfirmation.performance_id == task_id,
                PerformanceConfirmation.member_id == mid,
            ).delete()

        for mid in new_member_ids - existing_member_ids:
            conf = PerformanceConfirmation(
                performance_id=task.id,
                member_id=mid,
                status="unconfirmed",
                phone_reminded=False,
            )
            db.add(conf)

    db.commit()
    db.refresh(task)
    return _performance_task_to_dict(db, task)


def delete_performance_task(db: Session, task_id: int) -> bool:
    task = db.query(PerformanceTask).filter(PerformanceTask.id == task_id).first()
    if not task:
        return False
    db.delete(task)
    db.commit()
    return True


def get_performance_task_list(db: Session) -> list[dict]:
    tasks = db.query(PerformanceTask).order_by(PerformanceTask.start_time.desc()).all()
    return [_performance_task_to_dict(db, t) for t in tasks]


def get_performance_task_detail(db: Session, task_id: int) -> dict:
    task = db.query(PerformanceTask).filter(PerformanceTask.id == task_id).first()
    if not task:
        return None
    result = _performance_task_to_dict(db, task)
    result["confirmations"] = _get_confirmations_for_performance(db, task_id)
    return result


def get_performance_task_with_song_details(db: Session, task_id: int) -> dict:
    task = db.query(PerformanceTask).filter(PerformanceTask.id == task_id).first()
    if not task:
        return None
    result = _performance_task_to_dict(db, task)
    result["song_details"] = _get_song_performance_details(db, task_id)
    result["confirmations"] = _get_confirmations_for_performance(db, task_id)
    return result


def update_performance_confirmation(db: Session, task_id: int, member_id: int, data: dict) -> dict:
    conf = db.query(PerformanceConfirmation).filter(
        PerformanceConfirmation.performance_id == task_id,
        PerformanceConfirmation.member_id == member_id,
    ).first()
    if not conf:
        return None

    if "status" in data and data["status"] is not None:
        conf.status = data["status"]
        if data["status"] in ("confirmed", "leave"):
            from datetime import datetime
            conf.confirmed_at = datetime.now()
    if "transport_mode" in data and data["transport_mode"] is not None:
        conf.transport_mode = data["transport_mode"]
    if "remark" in data and data["remark"] is not None:
        conf.remark = data["remark"]
    if "phone_reminded" in data and data["phone_reminded"] is not None:
        conf.phone_reminded = data["phone_reminded"]

    db.commit()
    db.refresh(conf)
    return _confirmation_to_dict(db, conf)


def mark_phone_reminded(db: Session, task_id: int, member_id: int) -> dict:
    return update_performance_confirmation(db, task_id, member_id, {"phone_reminded": True})


def get_performance_confirmation_stats(db: Session) -> list[dict]:
    tasks = db.query(PerformanceTask).order_by(PerformanceTask.start_time.desc()).all()
    results = []
    for task in tasks:
        confs = db.query(PerformanceConfirmation).filter(
            PerformanceConfirmation.performance_id == task.id
        ).all()
        total = len(confs)
        confirmed = sum(1 for c in confs if c.status == "confirmed")
        unconfirmed = sum(1 for c in confs if c.status == "unconfirmed")
        leave = sum(1 for c in confs if c.status == "leave")
        phone_reminded = sum(1 for c in confs if c.phone_reminded)

        results.append({
            "performance_id": task.id,
            "performance_name": task.name,
            "performance_date": task.start_time.strftime("%Y-%m-%d"),
            "total_members": total,
            "confirmed_count": confirmed,
            "unconfirmed_count": unconfirmed,
            "leave_count": leave,
            "confirmation_rate": round(confirmed / total, 2) if total > 0 else 0,
            "phone_reminded_count": phone_reminded,
            "phone_reminder_rate": round(phone_reminded / total, 2) if total > 0 else 0,
        })
    return results


def _performance_task_to_dict(db: Session, task: PerformanceTask) -> dict:
    song_tasks = sorted(task.song_tasks, key=lambda st: st.performance_order)
    song_task_dicts = []
    for st in song_tasks:
        song = db.query(Song).filter(Song.id == st.song_id).first()
        formation = db.query(Formation).filter(Formation.id == st.formation_id).first() if st.formation_id else None
        song_task_dicts.append({
            "id": st.id,
            "song_id": st.song_id,
            "song_name": song.name if song else "",
            "formation_id": st.formation_id,
            "formation_version": formation.version if formation else None,
            "performance_order": st.performance_order,
        })

    confs = db.query(PerformanceConfirmation).filter(
        PerformanceConfirmation.performance_id == task.id
    ).all()
    total = len(confs)
    confirmed = sum(1 for c in confs if c.status == "confirmed")
    unconfirmed = sum(1 for c in confs if c.status == "unconfirmed")
    leave = sum(1 for c in confs if c.status == "leave")

    return {
        "id": task.id,
        "name": task.name,
        "location": task.location,
        "meeting_time": task.meeting_time,
        "start_time": task.start_time,
        "costume_requirements": task.costume_requirements,
        "notes": task.notes,
        "created_at": task.created_at,
        "song_tasks": song_task_dicts,
        "total_members": total,
        "confirmed_count": confirmed,
        "unconfirmed_count": unconfirmed,
        "leave_count": leave,
    }


def _get_confirmations_for_performance(db: Session, task_id: int) -> list[dict]:
    confs = db.query(PerformanceConfirmation).filter(
        PerformanceConfirmation.performance_id == task_id
    ).all()
    return [_confirmation_to_dict(db, c) for c in confs]


def _confirmation_to_dict(db: Session, conf: PerformanceConfirmation) -> dict:
    member = db.query(Member).filter(Member.id == conf.member_id).first()
    return {
        "id": conf.id,
        "performance_id": conf.performance_id,
        "member_id": conf.member_id,
        "member_name": member.name if member else "",
        "member_phone": member.phone if member else None,
        "status": conf.status,
        "transport_mode": conf.transport_mode,
        "remark": conf.remark,
        "phone_reminded": conf.phone_reminded,
        "confirmed_at": conf.confirmed_at,
    }


def _get_song_performance_details(db: Session, task_id: int) -> list[dict]:
    song_tasks = db.query(PerformanceSongTask).filter(
        PerformanceSongTask.performance_id == task_id
    ).order_by(PerformanceSongTask.performance_order).all()

    leave_member_ids = set()
    confirmed_member_ids = set()
    confs = db.query(PerformanceConfirmation).filter(
        PerformanceConfirmation.performance_id == task_id
    ).all()
    for c in confs:
        if c.status == "leave":
            leave_member_ids.add(c.member_id)
        elif c.status == "confirmed":
            confirmed_member_ids.add(c.member_id)

    details = []
    for st in song_tasks:
        song = db.query(Song).filter(Song.id == st.song_id).first()
        formation = None
        positions = []
        if st.formation_id:
            formation = db.query(Formation).filter(Formation.id == st.formation_id).first()
            positions = db.query(FormationPosition).filter(
                FormationPosition.formation_id == st.formation_id
            ).all()
        elif song:
            latest_formation = (
                db.query(Formation)
                .filter(Formation.song_id == song.id)
                .order_by(Formation.version.desc())
                .first()
            )
            if latest_formation:
                formation = latest_formation
                positions = db.query(FormationPosition).filter(
                    FormationPosition.formation_id == latest_formation.id
                ).all()

        leave_members = []
        confirmed_substitutes = []
        gap_positions = []

        for pos in positions:
            if pos.member_id:
                if pos.member_id in leave_member_ids:
                    member = db.query(Member).filter(Member.id == pos.member_id).first()
                    leave_members.append({
                        "position_id": pos.position_id,
                        "member_id": pos.member_id,
                        "member_name": member.name if member else "",
                    })

                    sub_assign = (
                        db.query(SubstituteAssignment)
                        .filter(
                            SubstituteAssignment.song_id == st.song_id,
                            SubstituteAssignment.absent_member_id == pos.member_id,
                            SubstituteAssignment.position_id == pos.position_id,
                        )
                        .order_by(SubstituteAssignment.priority)
                        .first()
                    )
                    if sub_assign and sub_assign.substitute_member_id in confirmed_member_ids:
                        sub_member = db.query(Member).filter(Member.id == sub_assign.substitute_member_id).first()
                        confirmed_substitutes.append({
                            "position_id": pos.position_id,
                            "substitute_member_id": sub_assign.substitute_member_id,
                            "substitute_member_name": sub_member.name if sub_member else "",
                        })
                    else:
                        gap_positions.append(pos.position_id)

        details.append({
            "song_id": st.song_id,
            "song_name": song.name if song else "",
            "formation_id": formation.id if formation else None,
            "formation_version": formation.version if formation else None,
            "total_positions": len(positions),
            "leave_members": leave_members,
            "confirmed_substitutes": confirmed_substitutes,
            "gap_positions": gap_positions,
        })

    return details
