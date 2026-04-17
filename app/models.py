from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Game(db.Model):
    __tablename__ = "games"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    host = db.Column(db.String(120), nullable=False)
    platform = db.Column(db.String(50), nullable=False, default="Wii")
    started = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    teams = db.relationship(
        "Team",
        back_populates="game",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    players = db.relationship(
        "Player",
        back_populates="game",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    events = db.relationship(
        "Event",
        back_populates="game",
        cascade="all, delete-orphan",
        lazy="joined",
    )


class Team(db.Model):
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    game = db.relationship("Game", back_populates="teams")
    players = db.relationship(
        "Player",
        back_populates="team",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    results = db.relationship(
        "TeamResult",
        back_populates="team",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    @property
    def score_total(self):
        return sum(result.points for result in self.results)


class Player(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    score = db.Column(db.Integer, default=0, nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=True)

    game = db.relationship("Game", back_populates="players")
    team = db.relationship("Team", back_populates="players")


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    stage = db.Column(db.String(50), nullable=False, default="Heat")
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    game = db.relationship("Game", back_populates="events")
    results = db.relationship(
        "TeamResult",
        back_populates="event",
        cascade="all, delete-orphan",
        lazy="joined",
    )


class TeamResult(db.Model):
    __tablename__ = "team_results"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    points = db.Column(db.Integer, nullable=False, default=0)

    event = db.relationship("Event", back_populates="results")
    team = db.relationship("Team", back_populates="results")
