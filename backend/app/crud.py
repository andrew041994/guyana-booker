from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta, date
from decimal import Decimal
from passlib.context import CryptContext
from twilio.rest import Client
import os
from . import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
twilio_client = None
if os.getenv("TWILIO_ACCOUNT_SID"):
    twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
FROM_NUMBER = os.getenv("TWILIO_WHATSAPP_FROM")

def send_whatsapp(to: str, body: str):
    if not twilio_client or not to or not FROM_NUMBER:
        print(f"[WhatsApp Preview] To {to}: {body}")
        return
    try:
        twilio_client.messages.create(from_=FROM_NUMBER, body=body, to=to)
    except Exception as e:
        print(f"WhatsApp error: {e}")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

# USER CRUD
def create_user(db: Session, user: schemas.UserCreate):
    hashed = hash_password(user.password)
    db_user = models.User(**user.dict(exclude={"password"}), hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# PROMOTION CRUD (fully editable)
def get_promotion(db: Session, provider_id: int):
    return db.query(models.Promotion).filter(models.Promotion.provider_id == provider_id).first()

def upsert_promotion(db: Session, provider_id: int, free_total: int):
    promo = get_promotion(db, provider_id)
    if promo:
        promo.free_bookings_total = free_total
        if free_total < promo.free_bookings_used:  # can't reduce below used
            promo.free_bookings_used = free_total
    else:
        promo = models.Promotion(provider_id=provider_id, free_bookings_total=free_total, free_bookings_used=0)
        db.add(promo)
    db.commit()
    db.refresh(promo)
    return promo

# BOOKING WITH PROMOTION + LOCK CHECK
def create_booking(db: Session, booking: schemas.BookingCreate, customer_id: int):
    service = db.query(models.Service).filter(models.Service.id == booking.service_id).first()
    provider = db.query(models.Provider).filter(models.Provider.id == service.provider_id).first()
    provider_user = db.query(models.User).filter(models.User.id == provider.user_id).first()

    # Check if provider is locked (unpaid bill past due)
    overdue = db.query(models.Bill).filter(
        models.Bill.provider_id == provider.id,
        models.Bill.is_paid == False,
        models.Bill.due_date < datetime.utcnow()
    ).first()
    if overdue:
        raise ValueError("Provider account is locked due to unpaid bill")

    # Apply promotion
    promo = get_promotion(db, provider.id)
    fee_applied = Decimal('0.1') * Decimal(str(service.price_gyd))
    if promo and promo.free_bookings_used < promo.free_bookings_total:
        fee_applied = Decimal('0')
        promo.free_bookings_used += 1

    # Create booking
    end_time = booking.start_time + timedelta(minutes=service.duration_minutes)
    db_booking = models.Booking(
        customer_id=customer_id,
        service_id=booking.service_id,
        start_time=booking.start_time,
        end_time=end_time,
        status="confirmed"
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)

    # WhatsApp notifications
    customer = db.query(models.User).filter(models.User.id == customer_id).first()
    send_whatsapp(customer.whatsapp, f"Booking confirmed!\n{service.name} with {provider_user.full_name}\n{booking.start_time.strftime('%d %b %Y at %I:%M %p')}\nGYD {service.price_gyd}")
    send_whatsapp(provider_user.whatsapp, f"New booking!\n{customer.full_name} booked {service.name}\n{booking.start_time.strftime('%d %b %Y at %I:%M %p')}")

    return db_booking

# BILLING
def generate_monthly_bills(db: Session, month: date):
    providers = db.query(models.Provider).all()
    for prov in providers:
        start = month.replace(day=1)
        end = (month.replace(day=1) + timedelta(days=32)).replace(day=1)
        total = db.query(func.sum(models.Service.price_gyd))\
            .join(models.Booking)\
            .filter(models.Booking.service_id == models.Service.id,
                    models.Booking.start_time >= start,
                    models.Booking.start_time < end,
                    models.Booking.status == "confirmed",
                    models.Service.provider_id == prov.id).scalar() or 0
        fee = Decimal('0.1') * Decimal(str(total))
        due = datetime(end.year, end.month, 15, 23, 59)
        bill = models.Bill(provider_id=prov.id, month=start, total_gyd=total, fee_gyd=fee, due_date=due)
        db.add(bill)
        provider_user = db.query(models.User).filter(models.User.id == prov.user_id).first()
        send_whatsapp(provider_user.whatsapp, f"New bill for {start.strftime('%B %Y')}\nTotal bookings: GYD {total}\nYour fee (10%): GYD {fee}\nDue: 15 {end.strftime('%B %Y')}")
    db.commit()