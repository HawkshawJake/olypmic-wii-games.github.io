from flask import Blueprint, render_template, request, redirect

games = {}

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("index.html")

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