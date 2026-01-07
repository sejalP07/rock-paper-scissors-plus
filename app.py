from flask import Flask, request, render_template_string, redirect, url_for
import random

app = Flask(__name__)

# -------------------------
# GAME STATE (in-memory)
# -------------------------
state = {
    "round": 1,
    "max_rounds": 3,
    "user_score": 0,
    "bot_score": 0,
    "user_bomb_used": False,
    "bot_bomb_used": False,
    "message": "Welcome! Choose your move."
}

VALID_MOVES = ["rock", "paper", "scissors", "bomb"]

# -------------------------
# GAME LOGIC TOOLS
# -------------------------
def validate_move(move):
    if move not in VALID_MOVES:
        return False, "❌ Invalid move. Round wasted."

    if move == "bomb" and state["user_bomb_used"]:
        return False, "💣 Bomb already used!"

    return True, ""


def bot_move():
    if not state["bot_bomb_used"] and random.random() < 0.2:
        return "bomb"
    return random.choice(["rock", "paper", "scissors"])


def resolve_round(user, bot):
    if user == bot:
        return "draw"
    if user == "bomb":
        return "user"
    if bot == "bomb":
        return "bot"

    rules = {
        "rock": "scissors",
        "paper": "rock",
        "scissors": "paper"
    }
    return "user" if rules[user] == bot else "bot"


def update_state(user, bot, winner):
    if user == "bomb":
        state["user_bomb_used"] = True
    if bot == "bomb":
        state["bot_bomb_used"] = True

    if winner == "user":
        state["user_score"] += 1
    elif winner == "bot":
        state["bot_score"] += 1

    state["round"] += 1


# -------------------------
# ROUTES
# -------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST" and state["round"] <= state["max_rounds"]:
        user_move = request.form.get("move")
        valid, msg = validate_move(user_move)

        if not valid:
            state["message"] = msg
            state["round"] += 1
        else:
            bot_choice = bot_move()
            winner = resolve_round(user_move, bot_choice)
            update_state(user_move, bot_choice, winner)

            state["message"] = (
                f"You played {user_move} | "
                f"Bot played {bot_choice} → "
                f"{'Draw' if winner == 'draw' else winner.capitalize() + ' wins'}"
            )

        # ✅ POST → REDIRECT → GET (FIX)
        return redirect(url_for("index"))

    return render_template_string(TEMPLATE, state=state)


@app.route("/reset")
def reset():
    state.update({
        "round": 1,
        "user_score": 0,
        "bot_score": 0,
        "user_bomb_used": False,
        "bot_bomb_used": False,
        "message": "Game reset. Choose your move."
    })
    return redirect(url_for("index"))


# -------------------------
# HTML TEMPLATE
# -------------------------
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Rock Paper Scissors Plus</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #0f172a;
            color: white;
            text-align: center;
            padding: 40px;
        }
        .card {
            background: #1e293b;
            padding: 30px;
            border-radius: 12px;
            max-width: 420px;
            margin: auto;
        }
        button {
            padding: 12px 22px;
            margin: 8px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            font-size: 16px;
            color: white;
        }
        .rock { background: #64748b; }
        .paper { background: #38bdf8; }
        .scissors { background: #22c55e; }
        .bomb { background: #ef4444; }
        .reset { background: #facc15; color: black; }
    </style>
</head>
<body>

<div class="card">
    <h1>🎮 Rock Paper Scissors Plus</h1>
    <p>Round {{state.round}} / {{state.max_rounds}}</p>
    <p>Score → You: {{state.user_score}} | Bot: {{state.bot_score}}</p>
    <hr>
    <p>{{state.message}}</p>

    {% if state.round <= state.max_rounds %}
        <form method="post">
            <button class="rock" name="move" value="rock">Rock</button>
            <button class="paper" name="move" value="paper">Paper</button>
            <button class="scissors" name="move" value="scissors">Scissors</button>
            <button class="bomb" name="move" value="bomb">Bomb</button>
        </form>
    {% else %}
        <h2>🏁 Game Over</h2>
        {% if state.user_score > state.bot_score %}
            <h3>🎉 You Win!</h3>
        {% elif state.bot_score > state.user_score %}
            <h3>🤖 Bot Wins</h3>
        {% else %}
            <h3>🤝 Draw</h3>
        {% endif %}
        <a href="/reset"><button class="reset">Play Again</button></a>
    {% endif %}
</div>

</body>
</html>
"""

# -------------------------
# RUN SERVER
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
