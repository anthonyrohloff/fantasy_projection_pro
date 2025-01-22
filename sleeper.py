# Python 3.13.0
# Standard Libraries
import sqlite3

# Third-party Libraries
import pandas as pd
import requests


class SleeperProjectionGetter():
    def __init__(self, username, league_name, year, week):
        '''Constructor
        
        Arguments:
        username [string] -- sleeper username
        league_name [string] -- sleeper league name
        year [string] -- year to search in
        week [string] -- week to search for
        '''
        self.username = username
        self.league_name = league_name
        self.year = year
        self.week = week
    

    def update_db(self):
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


    def get_player_id(self, first_name, last_name):
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


    def get_user(self):
        '''Returns username, display_name, and user_id in key_user_info dict'''

        response = requests.get(f"https://api.sleeper.app/v1/user/{self.username}")
        user_info = response.json()

        key_user_info ={
            'username': user_info['username'],
            'display_name': user_info['display_name'],
            'user_id': user_info['user_id']
        }

        return key_user_info


    def get_league(self, user_id):
        '''Returns list league information dicts
        
        Arguments:
        user_id [string] -- user_id from get_user function
        '''
        
        response = requests.get(f"https://api.sleeper.app/v1/user/{user_id}/leagues/nfl/{self.year}")
        leagues = response.json()

        # Loop over each league and put relevant information in list of dictionaries
        league_info = {}
        for league in leagues:
            if league['name'] == self.league_name:
                league_info = {
                    'name': league.get('name'),
                    'season': league.get('season'),
                    'scoring_settings': league.get('scoring_settings'),
                    'roster_positions': league.get('roster_positions'),
                    'league_id': league.get('league_id')
                }

        return league_info


    def get_roster(self, league_id, user_id):
        '''Returns roster in a league for a user
        
        Arguments:
        league_id [string] -- league_id from get_leagues
        user_id [string] -- user_id from get_user
        '''

        response = requests.get(f"https://api.sleeper.app/v1/league/{league_id}/rosters")
        rosters = response.json()

        roster_info = {}
        for roster in rosters:
            if roster['owner_id'] == user_id:
                roster_info = {
                    'roster_id': roster['roster_id']
                }
                break 

        # Need to get matchup info to find starters/bench
        response = requests.get(f"https://api.sleeper.app/v1/league/{league_id}/matchups/{self.week}")
        matchup = response.json()

        for roster in matchup:
            if roster['roster_id'] == roster_info['roster_id']:
                roster_info = {
                    'players': roster['players'],
                    'starters': roster['starters']             
                }
                break 
        return roster_info


    def get_projection(self, player_id):
        '''Returns projection data for a player in the specified year
        
        Arguments:
        player_id [string] -- player id number in database
        '''

        # Connect to db to get player name from player_id
        connection = sqlite3.connect('nfl_players.db')
        cursor = connection.cursor()
        cursor.execute('''SELECT * FROM PLAYERS WHERE player_id = ?''', (player_id,))
        player = cursor.fetchall()
        connection.close()

        player_name = player[0][1] + ' ' + player[0][2]


        # Query api to get projections for the specified year
        response = requests.get(f"https://api.sleeper.com/projections/nfl/player/{player_id}?season={self.year}&season_type=regular&grouping=week")
        projection = response.json()   

        # Sort the dictionary by the integer value of the week
        pts_ppr_by_week = {}
        for week, data in sorted(projection.items(), key=lambda x: int(x[0])):
            if data and 'stats' in data and week == self.week:
                pts_ppr_by_week[week] = data['stats'].get('pts_ppr', None)
        
        # Create dict with all information to return
        projection = {
            'player_id': player_id,
            'name': player_name,
            'projection': pts_ppr_by_week
        }

        return projection


    def view_projections(self):
        '''View projections for current week on a team in any league'''

        user_info = self.get_user()
        league_info = self.get_league(user_info['user_id'])
        roster = self.get_roster(league_info['league_id'], user_info['user_id'])

        projections = []
        for player in roster['players']:
            projections.append(self.get_projection(player))

            if player in roster['starters']:
                projections[-1]['status'] = "starter"
            else:
                projections[-1]['status'] = "bench"

        df = pd.DataFrame(projections)
        print(df)

query = SleeperProjectionGetter(username="anthonyrohloff", league_name="Dyna$ty", 
                                year="2023", week="6")

query.view_projections()