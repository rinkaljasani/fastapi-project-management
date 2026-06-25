from sqlalchemy.orm import Session

from app.models.role import Role

DEFAULT_ROLES = [
    "admin",
    "manager",
    "user",
]


def seed_roles(db: Session):
    for role_name in DEFAULT_ROLES:

        role_exists = (
            db.query(Role)
            .filter(Role.name == role_name)
            .first()
        )

        if not role_exists:
            db.add(
                Role(
                    name=role_name
                )
            )

    db.commit()

    print("Roles seeded successfully")