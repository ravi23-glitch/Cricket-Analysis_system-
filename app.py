from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DATABASE = "cricket.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row   # so we can use row["column_name"]
    return conn


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            matches INTEGER NOT NULL,
            runs INTEGER NOT NULL,
            wickets INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def get_all_players():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM players")
    players = cur.fetchall()
    conn.close()
    return players


def analyze_performance():
    conn = get_db_connection()
    cur = conn.cursor()

    # Highest run scorer
    cur.execute("SELECT name, runs FROM players ORDER BY runs DESC LIMIT 1")
    highest_runs = cur.fetchone()

    # Best bowler (max wickets)
    cur.execute("SELECT name, wickets FROM players ORDER BY wickets DESC LIMIT 1")
    best_bowler = cur.fetchone()

    # Average runs per match for all players
    cur.execute("SELECT SUM(runs) as total_runs, SUM(matches) as total_matches FROM players")
    total = cur.fetchone()

    conn.close()

    highest_run_scorer = None
    best_bowler_player = None
    avg_runs_per_match = 0.0

    if highest_runs:
        highest_run_scorer = {
            "name": highest_runs["name"],
            "runs": highest_runs["runs"]
        }

    if best_bowler:
        best_bowler_player = {
            "name": best_bowler["name"],
            "wickets": best_bowler["wickets"]
        }

    if total["total_matches"]:
        avg_runs_per_match = total["total_runs"] / total["total_matches"]

    return highest_run_scorer, best_bowler_player, round(avg_runs_per_match, 2)


@app.route("/", methods=["GET"])
def index():
    players = get_all_players()
    highest_run_scorer, best_bowler_player, avg_runs_per_match = analyze_performance()

    return render_template(
        "index.html",
        players=players,
        highest_run_scorer=highest_run_scorer,
        best_bowler_player=best_bowler_player,
        avg_runs_per_match=avg_runs_per_match
    )


@app.route("/player", methods=["POST"])
def handle_player():
    action = request.form.get("action")

    name = request.form.get("playerName")
    matches = request.form.get("matches")
    runs = request.form.get("runs")
    wickets = request.form.get("wickets")
    player_id = request.form.get("playerId")

    conn = get_db_connection()
    cur = conn.cursor()

    # Convert numeric fields safely
    def to_int(value, default=0):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    if action == "add":
        if name and matches and runs and wickets:
            cur.execute(
                "INSERT INTO players (name, matches, runs, wickets) VALUES (?, ?, ?, ?)",
                (name, to_int(matches), to_int(runs), to_int(wickets))
            )

    elif action == "update":
        if player_id:
            cur.execute("""
                UPDATE players
                SET name = COALESCE(?, name),
                    matches = COALESCE(?, matches),
                    runs = COALESCE(?, runs),
                    wickets = COALESCE(?, wickets)
                WHERE id = ?
            """, (
                name if name else None,
                to_int(matches) if matches else None,
                to_int(runs) if runs else None,
                to_int(wickets) if wickets else None,
                to_int(player_id)
            ))

    elif action == "delete":
        if player_id:
            cur.execute("DELETE FROM players WHERE id = ?", (to_int(player_id),))

    conn.commit()
    conn.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

