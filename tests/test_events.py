import uuid
from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes.events import router as events_router
from app.db.database import Base, get_db
from app.models import Case, Evidence, Event, User


# Use an isolated in-memory SQLite database for testing.
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


# Create a dedicated test application.
api = FastAPI()
api.include_router(events_router)


@pytest.fixture
def client():
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    api.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(api) as test_client:
            yield test_client
    finally:
        api.dependency_overrides.clear()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def existing_case_id(client):
    """Create a case required by the Event foreign key."""
    case_id = uuid.uuid4()

    with TestingSessionLocal() as db:
        case = Case(
            id=case_id,
            case_number=f"TEST-{uuid.uuid4().hex[:12]}",
            title="Automated Test Case",
        )
        db.add(case)
        db.commit()

    return str(case_id)


def valid_event_payload(case_id):
    return {
        "case_id": case_id,
        "event_type": "login_attempt",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "test-auth-service",
        "actor": "test-user",
        "description": "Automated test event",
        "severity": "high",
    }


def test_create_event(client, existing_case_id):
    response = client.post(
        "/events/",
        json=valid_event_payload(existing_case_id),
    )

    assert response.status_code == 201

    data = response.json()
    assert data["case_id"] == existing_case_id
    assert data["event_type"] == "login_attempt"
    assert data["severity"] == "high"
    assert "id" in data
    assert "created_at" in data


def test_list_events(client, existing_case_id):
    client.post(
        "/events/",
        json=valid_event_payload(existing_case_id),
    )

    response = client.get("/events/")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["event_type"] == "login_attempt"


def test_get_event(client, existing_case_id):
    create_response = client.post(
        "/events/",
        json=valid_event_payload(existing_case_id),
    )
    event_id = create_response.json()["id"]

    response = client.get(f"/events/{event_id}")

    assert response.status_code == 200
    assert response.json()["id"] == event_id


def test_get_nonexistent_event_returns_404(client):
    response = client.get(f"/events/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_delete_event(client, existing_case_id):
    create_response = client.post(
        "/events/",
        json=valid_event_payload(existing_case_id),
    )
    event_id = create_response.json()["id"]

    delete_response = client.delete(f"/events/{event_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["event_id"] == event_id

    get_response = client.get(f"/events/{event_id}")
    assert get_response.status_code == 404


def test_invalid_event_payload_returns_422(client):
    response = client.post(
        "/events/",
        json={
            "case_id": "not-a-valid-uuid",
            "event_type": "",
            "timestamp": "not-a-date",
            "description": "",
            "severity": "high",
        },
    )

    assert response.status_code == 422