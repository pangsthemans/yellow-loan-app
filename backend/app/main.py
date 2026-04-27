import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, Base
from app.routers import phones, applications

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Yellow Loan Application API",
    description="API for Yellow phone loan applications",
    version="1.0.0",
)

_default_origins = "http://localhost:9000,http://localhost:8080,http://localhost:3000"
_origins = os.getenv("ALLOWED_ORIGINS", _default_origins).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(phones.router)
app.include_router(applications.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "yellow-loan-api"}


@app.on_event("startup")
async def startup_event():
    """Auto-seed phones on first startup."""
    from app.core.database import SessionLocal
    from app.models.models import Phone
    from app.routers.phones import seed_phones

    db = SessionLocal()
    try:
        if db.query(Phone).count() == 0:
            seed_phones(db)
            print("✅ Phones seeded on startup")
    finally:
        db.close()
