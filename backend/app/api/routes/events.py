from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.event import Event
from app.schemas.event import EventCreate, EventResponse


router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.post(
    "/",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
):
    event = Event(
        case_id=event_data.case_id,
        event_type=event_data.event_type,
        timestamp=event_data.timestamp,
        source=event_data.source,
        actor=event_data.actor,
        description=event_data.description,
        severity=event_data.severity,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


@router.get(
    "/",
    response_model=list[EventResponse],
)
def get_events(
    db: Session = Depends(get_db),
):
    return db.query(Event).all()


@router.get(
    "/{event_id}",
    response_model=EventResponse,
)
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