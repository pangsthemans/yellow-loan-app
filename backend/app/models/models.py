from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class ApplicationStatus(str, enum.Enum):
    STARTED = "started"
    COMPLETED = "completed"


class Phone(Base):
    __tablename__ = "phones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    brand = Column(String(50), nullable=False)
    image_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    cash_price = Column(Float, nullable=False)
    deposit_percent = Column(Float, nullable=False)  # e.g. 0.10 for 10%

    # Risk-group-specific interest rates (annual)
    interest_rate_group1 = Column(Float, nullable=False)  # age 18-30
    interest_rate_group2 = Column(Float, nullable=False)  # age 31-50
    interest_rate_group3 = Column(Float, nullable=False)  # age 51-65

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    applications = relationship("Application", back_populates="phone")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)

    # Biographical
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    id_number = Column(String(13), unique=True, nullable=False, index=True)
    date_of_birth = Column(String(10), nullable=False)  # ISO date string
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=True)
    risk_group = Column(Integer, nullable=False)

    # Income
    monthly_income = Column(Float, nullable=False)
    income_document_filename = Column(String(500), nullable=True)
    income_document_data = Column(Text, nullable=True)  # base64 encoded

    # Phone choice
    phone_id = Column(Integer, ForeignKey("phones.id"), nullable=True)
    phone = relationship("Phone", back_populates="applications")

    # Snapshot of pricing at time of application
    loan_principal = Column(Float, nullable=True)
    loan_amount = Column(Float, nullable=True)
    daily_payment = Column(Float, nullable=True)
    interest_rate_applied = Column(Float, nullable=True)

    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.STARTED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
