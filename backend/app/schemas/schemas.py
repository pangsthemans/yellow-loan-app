from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
from datetime import date


# ─── Phone Schemas ────────────────────────────────────────────────────────────

class PhoneBase(BaseModel):
    name: str
    brand: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    cash_price: float
    deposit_percent: float
    interest_rate_group1: float
    interest_rate_group2: float
    interest_rate_group3: float


class PhoneCreate(PhoneBase):
    pass


class PhonePricing(BaseModel):
    """Computed pricing for a specific risk group."""
    cash_price: float
    deposit_percent: float
    deposit_amount: float
    loan_principal: float
    interest_rate: float
    loan_amount: float
    daily_payment: float
    monthly_payment: float


class PhoneResponse(PhoneBase):
    id: int
    pricing_group1: Optional[PhonePricing] = None
    pricing_group2: Optional[PhonePricing] = None
    pricing_group3: Optional[PhonePricing] = None

    class Config:
        from_attributes = True


class PhoneWithPricing(BaseModel):
    """Phone with pricing for a specific user's risk group."""
    id: int
    name: str
    brand: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    cash_price: float
    deposit_percent: float
    deposit_amount: float
    loan_principal: float
    interest_rate: float
    loan_amount: float
    daily_payment: float
    monthly_payment: float
    affordable: bool  # True if income >= 10x monthly_payment

    class Config:
        from_attributes = True


# ─── Application Schemas ──────────────────────────────────────────────────────

class ValidateIDRequest(BaseModel):
    id_number: str

    @field_validator("id_number")
    @classmethod
    def validate_format(cls, v):
        v = v.strip()
        if not v.isdigit() or len(v) != 13:
            raise ValueError("ID number must be exactly 13 digits")
        return v


class ValidateIDResponse(BaseModel):
    valid: bool
    dob: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    risk_group: Optional[int] = None
    error: Optional[str] = None


class ApplicationCreate(BaseModel):
    # Step 1: Bio
    first_name: str
    last_name: str
    id_number: str
    date_of_birth: str  # YYYY-MM-DD

    # Step 2: Income
    monthly_income: float
    income_document_filename: Optional[str] = None
    income_document_data: Optional[str] = None  # base64

    # Step 3: Phone
    phone_id: int

    @field_validator("first_name", "last_name")
    @classmethod
    def name_not_empty(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters")
        return v

    @field_validator("id_number")
    @classmethod
    def validate_id_format(cls, v):
        v = v.strip()
        if not v.isdigit() or len(v) != 13:
            raise ValueError("ID number must be exactly 13 digits")
        return v

    @field_validator("monthly_income")
    @classmethod
    def income_positive(cls, v):
        if v <= 0:
            raise ValueError("Monthly income must be greater than 0")
        return v


class ApplicationResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    id_number: str
    date_of_birth: str
    age: int
    gender: Optional[str]
    risk_group: int
    monthly_income: float
    phone_id: Optional[int]
    loan_principal: Optional[float]
    loan_amount: Optional[float]
    daily_payment: Optional[float]
    interest_rate_applied: Optional[float]
    status: str
    created_at: str

    class Config:
        from_attributes = True
