from app.core.database import SessionLocal
from app.seeders.role_seeders import seed_roles
from app.seeders.user_seeders import seed_users


def run_seeders():
    db = SessionLocal()

    try:
        seed_roles(db)
        seed_users(db)
    finally:
        db.close()


if __name__ == "__main__":
    run_seeders()