import requests
import json
import sqlite3
import pandas as pd


def get_nfl_state():
    '''Returns NFL state'''

    response = requests.get(f"https://api.sleeper.app/v1/state/nfl")
    state = response.json()  

    return state     


def get_player_id(first_name, last_name):
    '''Gets player informaton from database
    
    Arguments:
    first_name [string] -- player first name
    last_name [strong] -- player last name
    '''

    connection = sqlite3.connect('nfl_players.db')
    cursor = connection.cursor()
    cursor.execute('''SELECT * FROM PLAYERS WHERE first_name = ? AND last_name = ?''', (first_name, last_name,))
    rows = cursor.fetchall()
    connection.close()

    for row in rows:
        print(row)


def get_projection(player_id, year, proj_week):
    '''Returns projection data for a player in the specified year
    
    Arguments:
    player_id [string] -- player id number in database
    year [string] -- year to get projections from
    '''

    # Connect to db to get player name from player_id
    connection = sqlite3.connect('nfl_players.db')
    cursor = connection.cursor()
    cursor.execute('''SELECT * FROM PLAYERS WHERE player_id = ?''', (player_id,))
    player = cursor.fetchall()
    connection.close()

    player_name = player[0][1] + ' ' + player[0][2]

    # state = get_nfl_state()

    # Query api to get projections for the specified year
    response = requests.get(f"https://api.sleeper.com/projections/nfl/player/{player_id}?season={year}&season_type=regular&grouping=week")
    projection = response.json()   

    # Sort the dictionary by the integer value of the week
    pts_ppr_by_week = {}
    for week, data in sorted(projection.items(), key=lambda x: int(x[0])):
        if data and 'stats' in data and week == proj_week:
            pts_ppr_by_week[week] = data['stats'].get('pts_ppr', None)
    
    # Create dict with all information to return
    projection = {
        'player_id': player_id,
        'name': player_name,
        'projection': pts_ppr_by_week
    }

    return projection


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


# TODO 1
def update_db():
    '''Fetch player data from the Sleeper API'''

    response = requests.get("https://api.sleeper.app/v1/players/nfl")
    players = response.json()

    conn = sqlite3.connect('nfl_players.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            player_id TEXT PRIMARY KEY,
            search_full_name TEXT,
            first_name TEXT,
            last_name TEXT,
            team TEXT,
            position TEXT,
            status TEXT,
            age INTEGER,
            height TEXT,
            weight TEXT,
            college TEXT,
            years_exp INTEGER
        )
    ''')

    for player_id, player_data in players.items():
        cursor.execute('''
            INSERT OR REPLACE INTO players (
                player_id, first_name, last_name, team, position, status, age, height, weight, college, years_exp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            player_data.get("player_id"),
            player_data.get("first_name"),
            player_data.get("last_name"),
            player_data.get("team"),
            player_data.get("position"),
            player_data.get("status"),
            player_data.get("age"),
            player_data.get("height"),
            player_data.get("weight"),
            player_data.get("college"),
            player_data.get("years_exp")
        ))

    conn.commit()
    conn.close()


def get_user(username):
    '''Returns username, display_name, and user_id
    
    Argument:
    username [string] -- username (NOT display_name)
    '''

    response = requests.get(f"https://api.sleeper.app/v1/user/{username}")
    user_info = response.json()

    key_user_info ={
        'username': user_info['username'],
        'display_name': user_info['display_name'],
        'user_id': user_info['user_id']
    }

    return key_user_info


def get_league(league_name, user_id, season):
    '''Returns list league information dicts
    
    Arguments:
    league_name [string] -- name of league
    user_id [string] -- user_id from get_user function
    season [string] -- year to search for
    '''
    
    response = requests.get(f"https://api.sleeper.app/v1/user/{user_id}/leagues/nfl/{season}")
    leagues = response.json()

    # Loop over each league and put relevant information in list of dictionaries
    league_info = {}
    for league in leagues:
        if league['name'] == league_name:
            league_info = {
                'name': league.get('name'),
                'season': league.get('season'),
                'scoring_settings': league.get('scoring_settings'),
                'roster_positions': league.get('roster_positions'),
                'league_id': league.get('league_id')
            }

    return league_info


def get_roster(league_id, user_id):
    '''Returns roster in a league for a user
    
    Arguments:
    league_id [string] -- league_id from get_leagues
    '''

    response = requests.get(f"https://api.sleeper.app/v1/league/{league_id}/rosters")
    rosters = response.json()

    for roster in rosters:
        if roster['owner_id'] == user_id:
            roster_info = {
                'players': roster['players'],
                'starters': roster['starters'],
                'reserve': roster['reserve'],
                'taxi': roster['taxi']
            }
            return roster_info


def view_projections(username, year, week, league_name):
    '''View projections for current week on a team in any league
    
    Arguments:
    username [string] -- sleeper username
    year [string] -- year of season to get projections for
    league_name [string] -- name of sleeper league
    '''

    user_info = get_user(username)
    league_info = get_league(league_name, user_info['user_id'], year)
    roster = get_roster(league_info['league_id'], user_info['user_id'])

    projections = []
    for player in roster['players']:
        projections.append(get_projection(player, year, week))

        if player in roster['starters']:
            projections[-1]['status'] = "starter"
        elif player in roster['reserve']:
            projections[-1]['status'] = "reserve"
        elif player in roster['taxi']:
            projections[-1]['status'] = "taxi"
        else:
            projections[-1]['status'] = "bench"

    df = pd.DataFrame(projections)
    print(df)


view_projections("anthonyrohloff", '2023', '3', "Dyna$ty")