"""Application extensions."""

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(
    engine_options={
        "pool_pre_ping": True,
        "pool_recycle": 1800,
    }
)
migrate = Migrate()
