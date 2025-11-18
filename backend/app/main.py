from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
from . import crud, models, schemas, database

from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from datetime import datetime, timedelta

app = FastAPI(title="Guyana Booker")


SECRET_KEY = "your-super-secret-key-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@app.post("/auth/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = crud.create_user(db, user)
    return {"message": "User created", "user_id": new_user.id}

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode(
        {"sub": user.email, "user_id": user.id}, SECRET_KEY, algorithm=ALGORITHM
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_dep = database.get_db

# Scheduler for bills & reminders
scheduler = AsyncIOScheduler(timezone="UTC")

async def monthly_bills():
    with next(db_dep) as db:
        today = date.today()
        first = today.replace(day=1)
        crud.generate_monthly_bills(db, first)

scheduler.add_job(monthly_bills, "cron", day=1, hour=1)

@app.on_event("startup")
async def start_scheduler():
    models.Base.metadata.create_all(bind=database.engine)
    scheduler.start()

# Simple routes (you'll expand these)
@app.post("/auth/register")
def register(user: schemas.UserCreate, db: Session = Depends(db_dep)):
    return crud.create_user(db, user)

@app.post("/bookings/")
def book(booking: schemas.BookingCreate, customer_id: int = 1, db: Session = Depends(db_dep)):
    return crud.create_booking(db, booking, customer_id)

@app.put("/admin/promotions/{provider_id}")
def set_promo(provider_id: int, data: schemas.PromotionUpdate, db: Session = Depends(db_dep)):
    return crud.upsert_promotion(db, provider_id, data.free_bookings_total)

@app.get("/")
def home():
    return {"message": "Guyana Booker API running – editable promotions ready!"}