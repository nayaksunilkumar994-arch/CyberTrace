import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text, UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    evidence_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        index=True,
        nullable=False,
    )

    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    acquisition_source: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    storage_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    integrity_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING",
    )

    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )