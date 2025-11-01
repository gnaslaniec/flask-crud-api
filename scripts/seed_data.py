"""Seed a number of users and projects into the application database."""

from __future__ import annotations

import argparse
import random
import string

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app
from app.config import DevelopmentConfig
from app.extensions import db
from app.models import Project, User

FIRST_NAMES = [
    "Alex",
    "Blake",
    "Casey",
    "Dana",
    "Elliott",
    "Frankie",
    "Harper",
    "Jordan",
    "Morgan",
    "Riley",
]
LAST_NAMES = [
    "Anderson",
    "Brooks",
    "Campbell",
    "Davis",
    "Edwards",
    "Foster",
    "Gray",
    "Hayes",
    "Logan",
    "Parker",
]
PROJECT_WORDS = [
    "Aurora",
    "Beacon",
    "Catalyst",
    "Delta",
    "Elevate",
    "Fusion",
    "Harbor",
    "Infinity",
    "Momentum",
    "Nova",
    "Orbit",
    "Phoenix",
    "Quantum",
    "Summit",
    "Vanguard",
]


def random_password(length: int = 16) -> str:
    """Generate a random password satisfying complexity requirements."""

    alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits + "!@#$%^&*()"
    # Ensure complexity by picking at least one from each category
    components = [
        random.choice(string.ascii_lowercase),
        random.choice(string.ascii_uppercase),
        random.choice(string.digits),
        random.choice("!@#$%^&*()"),
    ]
    components.extend(random.choice(alphabet) for _ in range(length - len(components)))
    random.shuffle(components)
    return "".join(components)


def unique_email_generator() -> itertools.count:
    """Yield unique email addresses."""

    used = set()
    while True:
        first = random.choice(FIRST_NAMES).lower()
        last = random.choice(LAST_NAMES).lower()
        for suffix in range(1, 10000):
            candidate = f"{first}.{last}.{suffix}@example.com"
            if candidate not in used:
                used.add(candidate)
                yield candidate


def seed_users(num_users: int) -> list[User]:
    """Create and persist random users."""

    users: list[User] = []
    email_iter = unique_email_generator()
    for _ in range(num_users):
        role = random.choice(["manager", "employee"])
        user = User(
            name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            email=next(email_iter),
            role=role,
        )
        user.set_password(random_password())
        db.session.add(user)
        users.append(user)
    return users


def seed_projects(users: list[User], num_projects: int) -> None:
    """Create random projects attributed to existing users."""

    managers = [u for u in users if u.role == "manager"] or users
    for _ in range(num_projects):
        owner = random.choice(managers)
        name = f"Project {random.choice(PROJECT_WORDS)} {random.randint(100, 999)}"
        description = f"A strategic initiative focused on {random.choice(PROJECT_WORDS).lower()} development."
        project = Project(
            name=name,
            description=description,
            created_by=owner.id,
        )
        db.session.add(project)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed users and projects into the database.")
    parser.add_argument("--users", type=int, default=5, help="Number of users to create.")
    parser.add_argument("--projects", type=int, default=5, help="Number of projects to create.")
    args = parser.parse_args()

    app = create_app(DevelopmentConfig)
    with app.app_context():
        db.create_all()
        users = seed_users(args.users)
        db.session.flush()
        seed_projects(users, args.projects)
        db.session.commit()
        print(f"Seeded {args.users} users and {args.projects} projects.")


if __name__ == "__main__":
    main()
