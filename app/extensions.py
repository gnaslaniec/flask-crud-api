"""Application extensions."""

from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy(
    engine_options={
        "pool_pre_ping": True,
        "pool_recycle": 1800,
    }
)
migrate = Migrate()
cors = CORS()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
)
