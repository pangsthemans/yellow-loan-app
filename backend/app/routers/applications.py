from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.sa_id import parse_sa_id, get_risk_group
from app.models.models import Application, Phone, ApplicationStatus
from app.schemas.schemas import (
    ApplicationCreate,
    ApplicationResponse,
    ValidateIDRequest,
    ValidateIDResponse,
)
from app.routers.phones import compute_pricing

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("/validate-id", response_model=ValidateIDResponse)
def validate_id(request: ValidateIDRequest, db: Session = Depends(get_db)):
    """Validate a SA ID number and return parsed info."""
    result = parse_sa_id(request.id_number)

    if not result["valid"]:
        return ValidateIDResponse(valid=False, error=result["error"])

    age = result["age"]
    if age < 18 or age > 65:
        return ValidateIDResponse(
            valid=False,
            error=f"Applicant must be between 18 and 65 years old (you are {age})",
        )

    # Check uniqueness
    existing = (
        db.query(Application)
        .filter(Application.id_number == request.id_number)
        .first()
    )
    if existing:
        return ValidateIDResponse(
            valid=False,
            error="An application already exists for this ID number",
        )

    risk_group = get_risk_group(age)

    return ValidateIDResponse(
        valid=True,
        dob=result["dob"].isoformat(),
        age=age,
        gender=result["gender"],
        risk_group=risk_group,
    )


@router.post("/", response_model=ApplicationResponse, status_code=201)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    """Submit a complete loan application."""

    # ── 1. Validate SA ID ─────────────────────────────────────────────────────
    id_result = parse_sa_id(payload.id_number)
    if not id_result["valid"]:
        raise HTTPException(status_code=422, detail=id_result["error"])

    age = id_result["age"]
    if age < 18 or age > 65:
        raise HTTPException(
            status_code=422,
            detail=f"Applicant must be between 18 and 65 years old",
        )

    # ── 2. Check ID uniqueness ────────────────────────────────────────────────
    existing = (
        db.query(Application)
        .filter(Application.id_number == payload.id_number)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail="An application already exists for this ID number",
        )

    # ── 3. Get phone and compute pricing ──────────────────────────────────────
    phone = db.query(Phone).filter(Phone.id == payload.phone_id).first()
    if not phone:
        raise HTTPException(status_code=404, detail="Selected phone not found")

    risk_group = get_risk_group(age)
    rate_field = {1: "interest_rate_group1", 2: "interest_rate_group2", 3: "interest_rate_group3"}[risk_group]
    interest_rate = getattr(phone, rate_field)
    pricing = compute_pricing(phone, interest_rate, payload.monthly_income)

    # ── 4. Affordability check ────────────────────────────────────────────────
    if not pricing["affordable"]:
        raise HTTPException(
            status_code=422,
            detail=f"Monthly income must be at least 10x the monthly payment of R{pricing['monthly_payment']:.2f}",
        )

    # ── 5. Validate DOB matches ID ────────────────────────────────────────────
    dob_from_id = id_result["dob"].isoformat()
    if payload.date_of_birth != dob_from_id:
        raise HTTPException(
            status_code=422,
            detail="Date of birth does not match the ID number provided",
        )

    # ── 6. Create application ─────────────────────────────────────────────────
    application = Application(
        first_name=payload.first_name.strip(),
        last_name=payload.last_name.strip(),
        id_number=payload.id_number,
        date_of_birth=payload.date_of_birth,
        age=age,
        gender=id_result.get("gender"),
        risk_group=risk_group,
        monthly_income=payload.monthly_income,
        income_document_filename=payload.income_document_filename,
        income_document_data=payload.income_document_data,
        phone_id=phone.id,
        loan_principal=pricing["loan_principal"],
        loan_amount=pricing["loan_amount"],
        daily_payment=pricing["daily_payment"],
        interest_rate_applied=interest_rate,
        status=ApplicationStatus.COMPLETED,
        completed_at=datetime.now(timezone.utc),
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return ApplicationResponse(
        id=application.id,
        first_name=application.first_name,
        last_name=application.last_name,
        id_number=application.id_number,
        date_of_birth=application.date_of_birth,
        age=application.age,
        gender=application.gender,
        risk_group=application.risk_group,
        monthly_income=application.monthly_income,
        phone_id=application.phone_id,
        loan_principal=application.loan_principal,
        loan_amount=application.loan_amount,
        daily_payment=application.daily_payment,
        interest_rate_applied=application.interest_rate_applied,
        status=application.status.value,
        created_at=application.created_at.isoformat(),
    )


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(application_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    return ApplicationResponse(
        id=app.id,
        first_name=app.first_name,
        last_name=app.last_name,
        id_number=app.id_number,
        date_of_birth=app.date_of_birth,
        age=app.age,
        gender=app.gender,
        risk_group=app.risk_group,
        monthly_income=app.monthly_income,
        phone_id=app.phone_id,
        loan_principal=app.loan_principal,
        loan_amount=app.loan_amount,
        daily_payment=app.daily_payment,
        interest_rate_applied=app.interest_rate_applied,
        status=app.status.value,
        created_at=app.created_at.isoformat(),
    )
