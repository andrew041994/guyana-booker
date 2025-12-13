import os

from app.database import SessionLocal
from app import crud, schemas


def main():
    import os

    email = os.environ.get("ADMIN_EMAIL")
    password = os.environ.get("ADMIN_PASSWORD")
    full_name = os.environ.get("ADMIN_FULL_NAME", "Admin")
    phone = os.environ.get("ADMIN_PHONE")
    location = os.environ.get("ADMIN_LOCATION")

    print("[create_admin] ADMIN_PHONE =", repr(phone))
    print("[create_admin] ADMIN_LOCATION =", repr(location))

    if not phone or not location:
        raise RuntimeError("Missing ADMIN_PHONE or ADMIN_LOCATION environment variables")


    print("[create_admin] ADMIN_EMAIL =", repr(email))
    print("[create_admin] ADMIN_PASSWORD is set =", bool(password))

    if not email or not password:
        raise RuntimeError("Missing ADMIN_EMAIL or ADMIN_PASSWORD environment variables")

    db = SessionLocal()

    try:
        existing = crud.get_user_by_email(db, email)
        if existing:
            print(f"Admin already exists: {email}")
            return

        user = crud.create_user(
            db,
            schemas.UserCreate(
                email=email,
                password=password,
                full_name=full_name,
                phone=phone,
                location=location,
            ),
        )

        # If your project has an admin flag/role, set it here (uncomment/adapt):
        # user.is_admin = True
        # db.commit()
        # db.refresh(user)

        print(f"Created admin: {user.email} (id={user.id})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
