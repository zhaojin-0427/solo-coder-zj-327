import math
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import (
    Song, Member, MemberSong, MemberSubstitutePosition,
    Formation, FormationPosition, Rehearsal, RehearsalError,
    Attendance, SubstituteAssignment,
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
