import requests
import json
import sqlite3

def get_player_id(first_name, last_name):
    connection = sqlite3.connect('nfl_players.db')
    cursor = connection.cursor()
    cursor.execute('''SELECT * FROM PLAYERS WHERE first_name = ? AND last_name = ?''', (first_name, last_name,))
    rows = cursor.fetchall()
    connection.close()

    for row in rows:
        print(row)

def get_projections(player_id, year):
    '''Sends projection data for a player in the specified year
    
    Arguments:
    player_id [string] -- player id number in database
    year [string] -- year to get projections from
    '''
    response = requests.get(f"https://api.sleeper.com/projections/nfl/player/{player_id}?season={year}&season_type=regular&grouping=week")
    projection = response.json()

    # Sort the dictionary by the integer value of the week
    pts_ppr_by_week = {}
    for week, data in sorted(projection.items(), key=lambda x: int(x[0])):
        if data and 'stats' in data:
            pts_ppr_by_week[week] = data['stats'].get('pts_ppr', None)

    with open('projection.json', 'w') as json_file:
        json.dump(pts_ppr_by_week, json_file, indent=4)

def get_stats(player_id, year):
    '''Sends stats data for a player in the specified year
    
    Arguments:
    player_id [string] -- player id number in database
    year [string] -- year to get projections from
    '''
    response = requests.get(f"https://api.sleeper.com/stats/nfl/player/{player_id}?season={year}&season_type=regular&grouping=week")
    stats = response.json()

    # Sort the dictionary by the integer value of the week
    stats_ppr_by_week = {}
    for week, data in sorted(stats.items(), key=lambda x: int(x[0])):
        if data and 'stats' in data:
            stats_ppr_by_week[week] = data['stats'].get('pts_ppr', None)

    with open('stats.json', 'w') as json_file:
        json.dump(stats_ppr_by_week, json_file, indent=4)

get_player_id("Brock", "Purdy")