# app/workers/cron.py

from datetime import timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models
from app.crud import send_whatsapp, now_local_naive, send_push


def send_upcoming_reminders():
    db = SessionLocal()
    now = now_local_naive()
    start = now + timedelta(hours=1) - timedelta(minutes=1)
    end = now + timedelta(hours=1) + timedelta(minutes=1)

    rows = (
        db.query(models.Booking, models.Service, models.User)
        .join(models.Service, models.Booking.service_id == models.Service.id)
        .join(models.User, models.Booking.customer_id == models.User.id)
        .filter(
            models.Booking.status == "confirmed",
            models.Booking.start_time >= start,
            models.Booking.start_time <= end,
        )
        .all()
    )

    for booking, service, customer in rows:
        send_push(
            customer.expo_push_token,
            "Upcoming appointment",
            f"Your {service.name} at {booking.start_time.strftime('%I:%M %p')} "
            "starts in 1 hour.",
        )

    db.close()



def registerCronJobs(scheduler):
    """
    Register all recurring scheduled tasks.
    """
    # Run reminder job every minute
    scheduler.add_job(send_upcoming_reminders, "interval", minutes=1)
