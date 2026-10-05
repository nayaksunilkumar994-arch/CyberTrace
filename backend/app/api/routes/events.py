from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.event import Event


router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_event(
    case_id: UUID,
    event_type: str,
    timestamp: datetime,
    description: str,
    severity: str,
    source: str | None = None,
    actor: str | None = None,
    db: Session = Depends(get_db),
):
    event = Event(
        case_id=case_id,
        event_type=event_type,
        timestamp=timestamp,
        source=source,
        actor=actor,
        description=description,
        severity=severity,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


@router.get("/")
def get_events(
    db: Session = Depends(get_db),
):
    return db.query(Event).all()


@router.get("/{event_id}")
def get_event(
    event_id: UUID,
    db: Session = Depends(get_db),
):
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return event


@router.delete("/{event_id}")
def delete_event(
    event_id: UUID,
    db: Session = Depends(get_db),
):
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    db.delete(event)
    db.commit()

    return {
        "message": "Event deleted successfully",
        "event_id": str(event_id),
    }