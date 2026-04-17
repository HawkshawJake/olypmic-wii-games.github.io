from flask import Blueprint, render_template, request, redirect, url_for
from .models import db, Game, Team, Player, Event, TeamResult
import secrets

main = Blueprint("main", __name__)


def _generate_game_code():
    code = secrets.token_hex(3)
    while Game.query.filter_by(code=code).first() is not None:
        code = secrets.token_hex(3)
    return code


def _stage_sort_value(stage: str) -> int:
    order = {"Heat": 1, "Semi": 2, "Final": 3}
    return order.get(stage, 99)


@main.route("/")
def home():
    games = Game.query.order_by(Game.created_at.desc()).limit(10).all()
    return render_template("index.html", games=games)


@main.route("/create_game", methods=["POST"])
def create_game():
    username = request.form.get("username")
    game_name = request.form.get("game_name")
    platform = request.form.get("platform", "Wii")
    team_name = request.form.get("team_name", "Team 1").strip() or "Team 1"

    if not username or not game_name:
        return "Missing username or game name", 400

    code = _generate_game_code()
    game = Game(code=code, name=game_name, host=username, platform=platform)
    team = Team(name=team_name, game=game)
    player = Player(name=username, score=0, game=game, team=team)

    db.session.add(game)
    db.session.add(team)
    db.session.add(player)
    db.session.commit()

    return redirect(url_for("main.game", code=code))


@main.route("/join_game", methods=["POST"])
def join_game():
    username = request.form.get("username")
    game_code = request.form.get("game_code")
    team_name = request.form.get("team_name", "").strip()

    if not username or not game_code:
        return "Missing username or game code", 400

    game = Game.query.filter_by(code=game_code).first()
    if not game:
        return "Game not found", 404

    if team_name:
        team = Team.query.filter_by(name=team_name, game_id=game.id).first()
        if not team:
            team = Team(name=team_name, game=game)
            db.session.add(team)
    else:
        team = Team.query.filter_by(game_id=game.id).first()
        if not team:
            team = Team(name="Team 1", game=game)
            db.session.add(team)

    player = Player.query.filter_by(name=username, game_id=game.id).first()
    if not player:
        player = Player(name=username, score=0, game=game, team=team)
        db.session.add(player)
    elif player.team is None:
        player.team = team

    db.session.commit()
    return redirect(url_for("main.game", code=game_code))


@main.route("/add_team/<code>", methods=["POST"])
def add_team(code):
    game = Game.query.filter_by(code=code).first()
    if not game:
        return "Game not found", 404

    team_name = request.form.get("team_name", "").strip()
    if not team_name:
        count = Team.query.filter_by(game_id=game.id).count()
        team_name = f"Team {count + 1}"

    existing = Team.query.filter_by(name=team_name, game_id=game.id).first()
    if not existing:
        team = Team(name=team_name, game=game)
        db.session.add(team)
        db.session.commit()

    return redirect(url_for("main.game", code=code))


@main.route("/add_player/<code>", methods=["POST"])
def add_player(code):
    player_name = request.form.get("player_name", "").strip()
    team_id = request.form.get("team_id")

    game = Game.query.filter_by(code=code).first()
    if not game:
        return "Game not found", 404

    if not player_name:
        return "Missing player name", 400

    team = Team.query.filter_by(id=team_id, game_id=game.id).first() if team_id else None
    if not team:
        team = Team.query.filter_by(game_id=game.id).first()
        if not team:
            team = Team(name="Team 1", game=game)
            db.session.add(team)

    player = Player.query.filter_by(name=player_name, game_id=game.id).first()
    if not player:
        player = Player(name=player_name, score=0, game=game, team=team)
        db.session.add(player)
    else:
        player.team = team

    db.session.commit()
    return redirect(url_for("main.game", code=code))


@main.route("/create_event/<code>", methods=["POST"])
def create_event(code):
    event_name = request.form.get("event_name", "").strip()
    stage = request.form.get("stage", "Heat")

    game = Game.query.filter_by(code=code).first()
    if not game:
        return "Game not found", 404

    if not event_name:
        return "Missing event name", 400

    order = len(game.events) + 1
    event = Event(name=event_name, stage=stage, sort_order=order, game=game)
    db.session.add(event)
    db.session.commit()

    return redirect(url_for("main.game", code=code))


@main.route("/add_result/<code>", methods=["POST"])
def add_result(code):
    event_id = request.form.get("event_id")
    team_id = request.form.get("team_id")
    try:
        points = int(request.form.get("points", 0))
    except ValueError:
        points = 0

    game = Game.query.filter_by(code=code).first()
    if not game:
        return "Game not found", 404

    event = Event.query.filter_by(id=event_id, game_id=game.id).first()
    team = Team.query.filter_by(id=team_id, game_id=game.id).first()
    if not event or not team:
        return "Event or team not found", 404

    result = TeamResult.query.filter_by(event_id=event.id, team_id=team.id).first()
    if result:
        result.points = points
    else:
        result = TeamResult(event=event, team=team, points=points)
        db.session.add(result)

    db.session.commit()
    return redirect(url_for("main.game", code=code))


@main.route("/game/<code>")
def game(code):
    game = Game.query.filter_by(code=code).first()

    if not game:
        return "Game not found"

    teams = sorted(game.teams, key=lambda team: -team.score_total)
    events = sorted(game.events, key=lambda event: (_stage_sort_value(event.stage), event.sort_order))

    return render_template(
        "game.html",
        game=game,
        code=code,
        teams=teams,
        events=events,
    )
