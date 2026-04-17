from flask import Blueprint, render_template, request, redirect, url_for
import secrets

games = {}

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("index.html")

@main.route("/create_game", methods=["POST"])
def create_game():
    username = request.form.get("username")
    game_name = request.form.get("game_name")

    if not username or not game_name:
        return "Missing username or game name", 400

    code = secrets.token_hex(3)
    games[code] = {
        "name": game_name,
        "host": username,
        "scores": {}
    }

    return redirect(url_for("main.game", code=code))

@main.route("/join_game", methods=["POST"])
def join_game():
    username = request.form.get("username")
    game_code = request.form.get("game_code")

    if not username or not game_code:
        return "Missing username or game code", 400

    game = games.get(game_code)
    if not game:
        return "Game not found", 404

    if "scores" not in game:
        game["scores"] = {}

    if username not in game["scores"]:
        game["scores"][username] = 0

    return redirect(url_for("main.game", code=game_code))

@main.route("/game/<code>")
def game(code):
    game = games.get(code)

    if not game:
        return "Game not found"

    # build leaderboard
    scores = game.get("scores", {})

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return render_template(
        "game.html",
        game=game,
        code=code,
        scores=sorted_scores
    )

@main.route("/add_score/<code>", methods=["POST"])
def add_score(code):
    player = request.form.get("player")
    points = int(request.form.get("points"))

    game = games.get(code)

    if "scores" not in game:
        game["scores"] = {}

    if player not in game["scores"]:
        game["scores"][player] = 0

    game["scores"][player] += points

    return redirect(f"/game/{code}")