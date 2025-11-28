import os
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# -------------------------------
# DATABASE PATH (works on Render)
# -------------------------------
basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(basedir, "cricket.db")


# -------------------------------
# DATABASE CONNECTION
# -------------------------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------------
# CREATE TABLE IF NOT EXISTS
# -------------------------------
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


# -------------------------------
# FETCH ALL PLAYERS
# -------------------------------
def get_all_players():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM players")
    players = cur.fetchall()
    conn.close()
    return players


# -------------------------------
# PERFORMANCE ANALYSIS
# -------------------------------
def analyze_performance():
    conn = get_db_connection()
    cur = conn.cursor()

    # Highest run scorer
    cur.execute("SELECT name, runs FROM players ORDER BY runs DESC LIMIT 1")
    highest_runs = cur.fetchone()

    # Best bowler
    cur.execute("SELECT name, wickets FROM players ORDER BY wickets DESC LIMIT 1")
    best_bowler = cur.fetchone()

    # Avg runs/match
    cur.execute("SELECT SUM(runs) AS total_runs, SUM(matches) AS total_matches FROM players")
    total = cur.fetchone()

    conn.close()

    highest_run_scorer = None
    best_bowler_player = None
    avg_runs = 0.0

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
        avg_runs = round(total["total_runs"] / total["total_matches"], 2)

    return highest_run_scorer, best_bowler_player, avg_runs


# -------------------------------
# HOME PAGE
# -------------------------------
@app.route("/", methods=["GET"])
def index():
    players = get_all_players()
    highest, best, avg = analyze_performance()

    return render_template(
        "index.html",
        players=players,
        highest_run_scorer=highest,
        best_bowler_player=best,
        avg_runs_per_match=avg
    )


# -------------------------------
# FORM ACTIONS (ADD/UPDATE/DELETE)
# -------------------------------
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

    def safe_int(value):
        try:
            return int(value)
        except:
            return None

    # Add player
    if action == "add":
        if name and matches and runs and wickets:
            cur.execute(
                "INSERT INTO players (name, matches, runs, wickets) VALUES (?, ?, ?, ?)",
                (name, safe_int(matches), safe_int(runs), safe_int(wickets))
            )

    # Update player
    elif action == "update":
        if player_id:
            cur.execute("""
                UPDATE players
                SET 
                    name = COALESCE(?, name),
                    matches = COALESCE(?, matches),
                    runs = COALESCE(?, runs),
                    wickets = COALESCE(?, wickets)
                WHERE id = ?
            """, (
                name if name else None,
                safe_int(matches),
                safe_int(runs),
                safe_int(wickets),
                safe_int(player_id)
            ))

    # Delete player
    elif action == "delete":
        if player_id:
            cur.execute("DELETE FROM players WHERE id = ?", (safe_int(player_id),))

    conn.commit()
    conn.close()

    return redirect(url_for("index"))


# -------------------------------
# RUN LOCALLY (Render ignores this)
# -------------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)



