from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Member, MemberSong, MemberSubstitutePosition
from schemas import MemberCreate, MemberUpdate, MemberResponse, MemberDetailResponse

router = APIRouter(prefix="/api/members", tags=["members"])


@router.post("", response_model=MemberResponse)
def create_member(data: MemberCreate, db: Session = Depends(get_db)):
    song_ids = data.song_ids
    sub_positions = data.substitute_positions
    member_data = data.model_dump(exclude={"song_ids", "substitute_positions"})
    member = Member(**member_data)
    db.add(member)
    db.flush()

    for sid in song_ids:
        db.add(MemberSong(member_id=member.id, song_id=sid))
    for sp in sub_positions:
        db.add(MemberSubstitutePosition(member_id=member.id, position_label=sp))

    db.commit()
    db.refresh(member)
    return member


@router.get("", response_model=list[MemberDetailResponse])
def list_members(db: Session = Depends(get_db)):
    members = db.query(Member).all()
    result = []
    for m in members:
        song_ids = [ms.song_id for ms in db.query(MemberSong).filter(MemberSong.member_id == m.id).all()]
        sub_positions = [sp.position_label for sp in db.query(MemberSubstitutePosition).filter(MemberSubstitutePosition.member_id == m.id).all()]
        result.append(MemberDetailResponse(
            id=m.id,
            name=m.name,
            height_range=m.height_range,
            phone=m.phone,
            created_at=m.created_at,
            song_ids=song_ids,
            substitute_positions=sub_positions,
        ))
    return result


@router.get("/{member_id}", response_model=MemberDetailResponse)
def get_member(member_id: int, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    song_ids = [ms.song_id for ms in db.query(MemberSong).filter(MemberSong.member_id == member_id).all()]
    sub_positions = [sp.position_label for sp in db.query(MemberSubstitutePosition).filter(MemberSubstitutePosition.member_id == member_id).all()]

    return MemberDetailResponse(
        id=member.id,
        name=member.name,
        height_range=member.height_range,
        phone=member.phone,
        created_at=member.created_at,
        song_ids=song_ids,
        substitute_positions=sub_positions,
    )


@router.put("/{member_id}", response_model=MemberResponse)
def update_member(member_id: int, data: MemberUpdate, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    update_data = data.model_dump(exclude_unset=True, exclude={"song_ids", "substitute_positions"})
    for key, value in update_data.items():
        setattr(member, key, value)

    if data.song_ids is not None:
        db.query(MemberSong).filter(MemberSong.member_id == member_id).delete()
        for sid in data.song_ids:
            db.add(MemberSong(member_id=member_id, song_id=sid))

    if data.substitute_positions is not None:
        db.query(MemberSubstitutePosition).filter(MemberSubstitutePosition.member_id == member_id).delete()
        for sp in data.substitute_positions:
            db.add(MemberSubstitutePosition(member_id=member_id, position_label=sp))

    db.commit()
    db.refresh(member)
    return member


@router.delete("/{member_id}")
def delete_member(member_id: int, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(member)
    db.commit()
    return {"detail": "Deleted"}
