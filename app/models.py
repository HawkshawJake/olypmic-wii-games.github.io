from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Game(db.Model):
    __tablename__ = "games"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    host = db.Column(db.String(120), nullable=False)
    platform = db.Column(db.String(50), nullable=False, default="Wii")
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    players = db.relationship(
        "Player",
        back_populates="game",
        cascade="all, delete-orphan",
        lazy="joined",
    )


class Player(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    score = db.Column(db.Integer, default=0, nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)

    game = db.relationship("Game", back_populates="players")
