import sqlite3

# Connect to SQLite database (creates file if not exists)
conn = sqlite3.connect("cricket.db")
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    matches INTEGER,
    runs INTEGER,
    wickets INTEGER
)
""")
conn.commit()

# Function to add player
def add_player():
    name = input("Enter player name: ")
    matches = int(input("Enter matches played: "))
    runs = int(input("Enter total runs: "))
    wickets = int(input("Enter total wickets: "))
    cursor.execute("INSERT INTO players (name, matches, runs, wickets) VALUES (?, ?, ?, ?)", 
                   (name, matches, runs, wickets))
    conn.commit()
    print("✅ Player added successfully!\n")

# Function to view all players
def view_players():
    cursor.execute("SELECT * FROM players")
    rows = cursor.fetchall()
    print("\n📌 All Players:")
    if not rows:
        print("No players found!\n")
    else:
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Matches: {row[2]}, Runs: {row[3]}, Wickets: {row[4]}")
    print()

# Function to update player
def update_player():
    view_players()
    player_id = int(input("Enter player ID to update: "))
    name = input("Enter new name: ")
    matches = int(input("Enter new matches played: "))
    runs = int(input("Enter new runs: "))
    wickets = int(input("Enter new wickets: "))
    cursor.execute("UPDATE players SET name=?, matches=?, runs=?, wickets=? WHERE id=?", 
                   (name, matches, runs, wickets, player_id))
    conn.commit()
    print("✏️ Player updated successfully!\n")

# Function to delete player
def delete_player():
    view_players()
    player_id = int(input("Enter player ID to delete: "))
    cursor.execute("DELETE FROM players WHERE id=?", (player_id,))
    conn.commit()
    print("🗑️ Player deleted successfully!\n")

# Function to analyze performance
def analyze_performance():
    print("\n=== Player Performance Analysis ===")

    # Highest run scorer
    cursor.execute("SELECT name, runs FROM players ORDER BY runs DESC LIMIT 1")
    top_batsman = cursor.fetchone()
    if top_batsman:
        print(f"🏆 Highest Run Scorer: {top_batsman[0]} ({top_batsman[1]} runs)")

    # Best bowler
    cursor.execute("SELECT name, wickets FROM players ORDER BY wickets DESC LIMIT 1")
    top_bowler = cursor.fetchone()
    if top_bowler:
        print(f"🥇 Best Bowler: {top_bowler[0]} ({top_bowler[1]} wickets)")

    # Average runs per match
    cursor.execute("SELECT AVG(runs*1.0/matches) FROM players WHERE matches > 0")
    avg_runs = cursor.fetchone()[0]
    if avg_runs:
        print(f"📊 Average Runs per Match (All Players): {avg_runs:.2f}")
    print()

# Main program
def main():
    while True:
        print("==== CRICKET PLAYER PERFORMANCE SYSTEM ====")
        print("1. Add Player")
        print("2. View Players")
        print("3. Update Player")
        print("4. Delete Player")
        print("5. Analyze Performance")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == "1":
            add_player()
        elif choice == "2":
            view_players()
        elif choice == "3":
            update_player()
        elif choice == "4":
            delete_player()
        elif choice == "5":
            analyze_performance()
        elif choice == "6":
            print("👋 Exiting... Goodbye!")
            break
        else:
            print("❌ Invalid choice! Try again.\n")

if __name__ == "__main__":
    main()

# Close DB when program ends
conn.close()
