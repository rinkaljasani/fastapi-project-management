from sqlalchemy.orm import Session

from app.models.user import User
from app.models.role import Role

from app.services.auth_services import get_password_hash


USERS = [
    {
        "email": "admin@admin.com",
        "first_name": "Admin",
        "last_name": "User",
        "password": "Admin@123",
        "role": "admin",
    },
    {
        "email": "manager@manager.com",
        "first_name": "Manager",
        "last_name": "User",
        "password": "Manager@123",
        "role": "manager",
    },
    {
        "email": "user@user.com",
        "first_name": "Normal",
        "last_name": "User",
        "password": "User@123",
        "role": "user",
    },
]


def seed_users(db: Session):

    for user_data in USERS:

        existing_user = (
            db.query(User)
            .filter(User.email == user_data["email"])
            .first()
        )

        if existing_user:
            continue

        role = (
            db.query(Role)
            .filter(Role.name == user_data["role"])
            .first()
        )

        if not role:
            print(f"Role {user_data['role']} not found")
            continue

        user = User(
            email=user_data["email"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            password_hash=get_password_hash(user_data["password"]),
        )

        # many-to-many relationship
        user.roles.append(role)

        db.add(user)

    db.commit()

    print("Users seeded successfully")