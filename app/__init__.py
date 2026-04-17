from flask import Flask
import os
import secrets
from sqlalchemy import inspect, text

from .models import db


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))

    database_url = os.getenv("DATABASE_URL", "sqlite:///games.db")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()
        _ensure_schema_migrations()

    return app


def _ensure_schema_migrations():
    inspector = inspect(db.engine)
    if not inspector.has_table("games"):
        return

    columns = [column["name"] for column in inspector.get_columns("games")]

    with db.engine.begin() as conn:
        if "platform" not in columns:
            conn.execute(text("ALTER TABLE games ADD COLUMN platform VARCHAR(50) DEFAULT 'Wii' NOT NULL"))

        if "started" not in columns:
            if db.engine.dialect.name == "postgresql":
                conn.execute(text("ALTER TABLE games ADD COLUMN started BOOLEAN DEFAULT FALSE NOT NULL"))
            else:
                conn.execute(text("ALTER TABLE games ADD COLUMN started BOOLEAN DEFAULT 0 NOT NULL"))

        if "created_at" not in columns:
            if db.engine.dialect.name == "sqlite":
                conn.execute(text("ALTER TABLE games ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL"))
            else:
                conn.execute(text("ALTER TABLE games ADD COLUMN created_at TIMESTAMP DEFAULT NOW() NOT NULL"))

    if inspector.has_table("players"):
        player_columns = [column["name"] for column in inspector.get_columns("players")]
        if "team_id" not in player_columns:
            with db.engine.begin() as conn:
                conn.execute(text("ALTER TABLE players ADD COLUMN team_id INTEGER"))