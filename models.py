from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="citizen")

    complaints = relationship(
        "Complaint",
        back_populates="user"
    )


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    description = Column(String, nullable=False)

    image_path = Column(String, nullable=True)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    category = Column(String, default="Other")

    department = Column(
        String,
        default="General Municipal Department"
    )

    urgency = Column(
        String,
        default="Low"
    )

    status = Column(
        String,
        default="Submitted"
    )

    # ============================================================
    # SAVED AI / RAG RESULTS
    # ============================================================

    ai_analysis = Column(
        String,
        nullable=True
    )

    duplicate_decision = Column(
        String,
        nullable=True
    )

    # ============================================================
    # SAVED MUNICIPAL SLA
    # ============================================================

    municipal_sla_days = Column(
        Integer,
        nullable=True
    )

    municipal_sla_service = Column(
        String,
        nullable=True
    )

    municipal_sla_department = Column(
        String,
        nullable=True
    )

    municipal_sla_source = Column(
        String,
        nullable=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    user = relationship(
        "User",
        back_populates="complaints"
    )