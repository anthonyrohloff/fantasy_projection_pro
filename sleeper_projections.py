import sqlite3

from sleeper_wrapper import Stats

stats = Stats()

# pulls all of the stats for week 1 of the 2023 regular season
week_stats = stats.get_week_stats("regular", 2023, 1)

# retrieves stats for the Detroit defense for the provided week
score = stats.get_player_week_score(week_stats, "DET")

all_projections = stats.get_all_projections("regular", "2024")
print(all_projections)

# Connect to the database
conn = sqlite3.connect('nfl_players.db')
cursor = conn.cursor()

# Iterate through the all_projections dictionary
for player_id, player_data in all_projections.items():
    # Extract the pts_ppr value
    pts_ppr = player_data.get('pts_ppr', None)  # Default to None if 'pts_ppr' is not present

    # Update the players table with the projection
    cursor.execute("""
        UPDATE players
        SET projection = ?
        WHERE player_id = ?
    """, (pts_ppr, player_id))

# Commit the changes and close the connection
conn.commit()
conn.close()