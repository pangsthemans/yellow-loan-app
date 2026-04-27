from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.models import Phone
from app.schemas.schemas import PhoneResponse, PhoneWithPricing

router = APIRouter(prefix="/phones", tags=["phones"])


def compute_pricing(phone: Phone, interest_rate: float, monthly_income: Optional[float] = None):
    """Calculate all derived pricing fields for a phone + interest rate."""
    deposit_amount = phone.cash_price * phone.deposit_percent
    loan_principal = phone.cash_price * (1 - phone.deposit_percent)
    loan_amount = loan_principal * (1 + interest_rate)
    daily_payment = loan_amount / 360
    monthly_payment = daily_payment * 30

    affordable = True
    if monthly_income is not None:
        affordable = monthly_income >= (monthly_payment * 10)

    return {
        "id": phone.id,
        "name": phone.name,
        "brand": phone.brand,
        "description": phone.description,
        "image_url": phone.image_url,
        "cash_price": round(phone.cash_price, 2),
        "deposit_percent": phone.deposit_percent,
        "deposit_amount": round(deposit_amount, 2),
        "loan_principal": round(loan_principal, 2),
        "interest_rate": interest_rate,
        "loan_amount": round(loan_amount, 2),
        "daily_payment": round(daily_payment, 2),
        "monthly_payment": round(monthly_payment, 2),
        "affordable": affordable,
    }


@router.get("/", response_model=List[PhoneWithPricing])
def list_phones(
    risk_group: int = Query(default=2, ge=1, le=3, description="User risk group 1-3"),
    monthly_income: Optional[float] = Query(default=None, description="Monthly income for affordability filter"),
    db: Session = Depends(get_db),
):
    """
    List all phones with pricing calculated for the given risk group.
    Optionally filter by affordability using monthly_income.
    """
    phones = db.query(Phone).all()

    rate_field = {
        1: "interest_rate_group1",
        2: "interest_rate_group2",
        3: "interest_rate_group3",
    }[risk_group]

    result = []
    for phone in phones:
        rate = getattr(phone, rate_field)
        pricing = compute_pricing(phone, rate, monthly_income)
        result.append(PhoneWithPricing(**pricing))

    return result


@router.get("/{phone_id}", response_model=PhoneWithPricing)
def get_phone(
    phone_id: int,
    risk_group: int = Query(default=2, ge=1, le=3),
    monthly_income: Optional[float] = Query(default=None),
    db: Session = Depends(get_db),
):
    phone = db.query(Phone).filter(Phone.id == phone_id).first()
    if not phone:
        raise HTTPException(status_code=404, detail="Phone not found")

    rate_field = {
        1: "interest_rate_group1",
        2: "interest_rate_group2",
        3: "interest_rate_group3",
    }[risk_group]

    rate = getattr(phone, rate_field)
    return PhoneWithPricing(**compute_pricing(phone, rate, monthly_income))


@router.post("/seed", tags=["admin"])
def seed_phones(db: Session = Depends(get_db)):
    """Seed the database with sample phones. Idempotent."""
    if db.query(Phone).count() > 0:
        return {"message": "Phones already seeded", "count": db.query(Phone).count()}

    phones = [
        Phone(
            name="Galaxy A55",
            brand="Samsung",
            description="6.6\" AMOLED display, 50MP camera, 5000mAh battery. A solid everyday smartphone.",
            image_url="https://fdn2.gsmarena.com/vv/bigpic/samsung-galaxy-a55.jpg",
            cash_price=8999.00,
            deposit_percent=0.10,
            interest_rate_group1=0.15,
            interest_rate_group2=0.20,
            interest_rate_group3=0.28,
        ),
        Phone(
            name="iPhone 15",
            brand="Apple",
            description="6.1\" Super Retina XDR, A16 Bionic chip, 48MP main camera. Premium iOS experience.",
            image_url="https://fdn2.gsmarena.com/vv/bigpic/apple-iphone-15.jpg",
            cash_price=19999.00,
            deposit_percent=0.15,
            interest_rate_group1=0.15,
            interest_rate_group2=0.20,
            interest_rate_group3=0.28,
        ),
        Phone(
            name="Redmi Note 13",
            brand="Xiaomi",
            description="6.67\" AMOLED, 108MP camera, 5000mAh. Feature-packed at an affordable price.",
            image_url="https://fdn2.gsmarena.com/vv/bigpic/xiaomi-redmi-note-13-4g.jpg",
            cash_price=4999.00,
            deposit_percent=0.10,
            interest_rate_group1=0.15,
            interest_rate_group2=0.20,
            interest_rate_group3=0.28,
        ),
        Phone(
            name="P50 Lite",
            brand="Huawei",
            description="6.67\" LCD display, 64MP camera, 4000mAh battery. Reliable daily driver.",
            image_url="https://fdn2.gsmarena.com/vv/bigpic/huawei-nova-10-se.jpg",
            cash_price=5999.00,
            deposit_percent=0.10,
            interest_rate_group1=0.15,
            interest_rate_group2=0.20,
            interest_rate_group3=0.28,
        ),
        Phone(
            name="Pixel 8a",
            brand="Google",
            description="6.1\" OLED, Google Tensor G3, 64MP camera with AI features. Pure Android.",
            image_url="https://fdn2.gsmarena.com/vv/bigpic/google-pixel-8a.jpg",
            cash_price=13999.00,
            deposit_percent=0.12,
            interest_rate_group1=0.15,
            interest_rate_group2=0.20,
            interest_rate_group3=0.28,
        ),
        Phone(
            name="Galaxy S24",
            brand="Samsung",
            description="6.2\" Dynamic AMOLED, Snapdragon 8 Gen 3, 50MP camera. Flagship performance.",
            image_url="https://fdn2.gsmarena.com/vv/bigpic/samsung-galaxy-s24.jpg",
            cash_price=24999.00,
            deposit_percent=0.20,
            interest_rate_group1=0.15,
            interest_rate_group2=0.20,
            interest_rate_group3=0.28,
        ),
        Phone(
            name="TECNO Spark 20",
            brand="TECNO",
            description="6.56\" LCD, 48MP camera, 5000mAh battery. Entry-level value champ.",
            image_url="https://fdn2.gsmarena.com/vv/bigpic/tecno-spark-20.jpg",
            cash_price=2999.00,
            deposit_percent=0.10,
            interest_rate_group1=0.15,
            interest_rate_group2=0.20,
            interest_rate_group3=0.28,
        ),
        Phone(
            name="iPhone 15 Pro",
            brand="Apple",
            description="6.1\" ProMotion XDR, A17 Pro chip, titanium design, 48MP triple camera system.",
            image_url="https://fdn2.gsmarena.com/vv/bigpic/apple-iphone-15-pro.jpg",
            cash_price=29999.00,
            deposit_percent=0.20,
            interest_rate_group1=0.15,
            interest_rate_group2=0.20,
            interest_rate_group3=0.28,
        ),
    ]

    db.add_all(phones)
    db.commit()

    return {"message": "Phones seeded successfully", "count": len(phones)}
