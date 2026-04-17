from flask import Blueprint, render_template, request, redirect, url_for
from .models import db, Game, Player
import secrets

main = Blueprint("main", __name__)


def _generate_game_code():
    code = secrets.token_hex(3)
    while Game.query.filter_by(code=code).first() is not None:
        code = secrets.token_hex(3)
    return code


@main.route("/")
def home():
    games = Game.query.order_by(Game.created_at.desc()).limit(10).all()
    return render_template("index.html", games=games)


@main.route("/create_game", methods=["POST"])
def create_game():
    username = request.form.get("username")
    game_name = request.form.get("game_name")
    platform = request.form.get("platform", "Wii")

    if not username or not game_name:
        return "Missing username or game name", 400

    code = _generate_game_code()
    game = Game(code=code, name=game_name, host=username, platform=platform)
    player = Player(name=username, score=0, game=game)

    db.session.add(game)
    db.session.add(player)
    db.session.commit()

    return redirect(url_for("main.game", code=code))


@main.route("/join_game", methods=["POST"])
def join_game():
    username = request.form.get("username")
    game_code = request.form.get("game_code")

    if not username or not game_code:
        return "Missing username or game code", 400

    game = Game.query.filter_by(code=game_code).first()
    if not game:
        return "Game not found", 404

    existing_player = Player.query.filter_by(name=username, game_id=game.id).first()
    if not existing_player:
        player = Player(name=username, score=0, game=game)
        db.session.add(player)
        db.session.commit()

    return redirect(url_for("main.game", code=game_code))


@main.route("/game/<code>")
def game(code):
    game = Game.query.filter_by(code=code).first()

    if not game:
        return "Game not found"

    sorted_scores = sorted(
        [(player.name, player.score) for player in game.players],
        key=lambda x: x[1],
        reverse=True,
    )

    return render_template(
        "game.html",
        game=game,
        code=code,
        scores=sorted_scores,
    )


@main.route("/add_score/<code>", methods=["POST"])
def add_score(code):
    player_name = request.form.get("player")
    try:
        points = int(request.form.get("points", 0))
    except ValueError:
        points = 0

    game = Game.query.filter_by(code=code).first()
    if not game:
        return "Game not found", 404

    player = Player.query.filter_by(name=player_name, game_id=game.id).first()
    if not player:
        return "Player not found", 404

    player.score += points
    db.session.commit()

    return redirect(url_for("main.game", code=code))
