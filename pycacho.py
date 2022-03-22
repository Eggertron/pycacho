import argparse
from datetime import datetime, tzinfo
import logging
import os
import sqlite3
import sys


class CachoDBManager():
    TABLES_INSERT ={
                "players": "INSERT INTO players(id, description) VALUES(NULL, ?)",
                "sessions": "INSERT INTO sessions(id, date) VALUES(NULL, ?)",
                "games": "INSERT INTO games(id, players, description) VALUES(NULL, ?, ?)",
                "scores": "INSERT INTO scores(id, player_id, session_id, game_id, ones, twos, threes, fours, fives, sixes, straight, full, poker, grande, tutti) VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            }
    SCORE_COLS = ["id", "player_id", "session_id", "game_id", "ones", "twos", "threes", "fours", "fives", "sixes", "straight", "full", "poker", "grande", "tutti"]
    SESSION_COLS = ["id", "date", "high_score_id", "low_score_id"]
    GAMES_COLS = ["id", "players", "description"]
    PLAYER_COLS = ["id", "description"]
    def __init__(self, db="cacho_data.db"):
        """ docstring """
        self.init_all_tables = False
        if not os.path.exists(db):
            self.init_all_tables = True
        self.con = sqlite3.connect(db)
        self.cur = self.con.cursor()
        if self.init_all_tables:
            self.init_tables()

    def init_tables(self):
        """ docstring """
        self.cur.execute('''CREATE TABLE games
                            (id integer PRIMARY KEY, players text, description text)''')
        self.cur.execute('''CREATE TABLE players
                            (id integer PRIMARY KEY, description text)''')
        self.cur.execute('''CREATE TABLE sessions
                            (id integer PRIMARY KEY, date text, high_score_id integer, low_score_id integer)''')
        self.cur.execute('''CREATE TABLE scores
                            (id integer PRIMARY KEY, player_id integer, session_id integer, game_id integer, ones integer, twos integer, threes integer, fours integer, fives integer, sixes integer, straight integer, full integer, poker integer, grande integer, tutti integer)''')
        self.con.commit()
    def get_last_row_id(self):
        """ docstring """
        self.cur.execute('SELECT last_insert_rowid()')
        return self.cur.fetchone()[0]
    def print_table(self, table):
        """ docstring """
        print(f"TABLE: {table}")
        table = self.get_table(table)
        for row in table:
            print(row)
    def get_sessions(self) -> list:
        """ returns a list of sessions dictionary with keys:
            "id", "date", "high_score_id", "low_score_id"
        """
        return [ self.zip_to_dict(self.SESSION_COLS, s) for s in self.get_table("sessions")]
    def zip_to_dict(self, Key_list: list, value_list: list) -> dict:
        result = {}
        for k, v in zip(Key_list, value_list):
            result[k] = v
        return result
    def get_games(self) -> list:
        """ returns a list of games as dictionary  with keys:
            "id", "players", "description"
        """
        return [ self.zip_to_dict(self.GAMES_COLS, g) for g in self.get_table("games")]
    def get_table(self, table: str):
        self.cur.execute(f'SELECT * FROM {table}')
        return self.cur.fetchall()
    def get_players(self) -> list:
        """ returns list of player dictionaries: id, description """
        return [ self.zip_to_dict(self.PLAYER_COLS, p) for p in self.get_table("players") ]
    def create_player(self, player_name):
        """ docstring """
        return self.insert("players", (player_name,))
    def get_player_names(self):
        self.cur.execute("SELECT description FROM players")
        return [x[0] for x in self.cur.fetchall()]
    def create_session(self):
        """ docstring """
        now = int(datetime.now().timestamp())
        return self.insert("sessions", (now,))
    def get_sessions_by_player_id(self, player_id: int):
        self.cur.execute(f"SELECT * FROM sessions WHERE player_id = {player_id}")
        return self.cur.fetchall()
    def get_session_date(self, session_id: int) -> datetime:
        self.cur.execute(f"SELECT date FROM sessions WHERE id = {session_id}")
        epoch = self.cur.fetchone()[0]
        return datetime.fromtimestamp(int(epoch))
    def set_session_winner(self, session_id: int, score_id: int):
        self.update_sessions_table(session_id, "high_score_id", str(score_id))
    def get_sessions_verb_by_player_id(self, verb, player_id: int) -> list:
        self.cur.execute(f"SELECT sessions.id FROM sessions INNER JOIN scores ON sessions.{verb} = scores.id INNER JOIN players ON players.id = scores.player_id WHERE players.id = {player_id}")
        return [ x[0] for x in self.cur.fetchall() ]
    def get_sessions_lowest_by_player_id(self, player_id: int) -> list:
        return self.get_sessions_verb_by_player_id("low_score_id", player_id)
    def get_sessions_won_by_player_id(self, player_id: int) -> list:
        return self.get_sessions_verb_by_player_id("high_score_id", player_id)
    def set_session_looser(self, session_id: int, score_id: int):
        self.update_sessions_table(session_id, "low_score_id", str(score_id))
    def update_sessions_table(self, session_id: int, col: str, value: str):
        self.cur.execute(f"UPDATE sessions SET {col} = {value} WHERE id = {session_id}")
        self.con.commit()
    def create_game(self, players, description="generic game"):
        """ docstring """
        logging.debug(f"Creating game, number of players: {len(players)}")
        players_str = ",".join([str(x) for x in sorted(players)])
        logging.debug(f"Players string: {players_str}")
        return self.insert("games", (players_str, description,))
    def create_score(self, player_id, session_id, game_id):
        """ docstring """
        return self.insert("scores", (player_id, session_id, game_id, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0,))
    def get_player_name(self, player_id: int) -> str:
        """ docstring """
        self.cur.execute(f"SELECT description from players WHERE id = {player_id};")
        return self.cur.fetchone()[0]
    def update_score(self, score_id: int, col: str, value: int):
        """ docstring """
        self.cur.execute(f"UPDATE scores SET {col} = {value} WHERE id = {score_id}")
        self.con.commit()
    def delete_record_id(self, table: str, rid: int):
        self.cur.execute(f"DELETE FROM {table} WHERE id = {rid}")
        self.con.commit()
    def get_score(self, score_id: int):
        """ docstring """
        self.cur.execute(f"SELECT * FROM scores WHERE id = {score_id}")
        return self.score_to_dict(self.cur.fetchone())
    def get_scores_from_session_id(self, session_id: int) -> list:
        """ returns a list of score dictionaries """
        self.cur.execute(f"SELECT * FROM scores WHERE session_id = {session_id}")
        return [self.score_to_dict(score) for score in self.cur.fetchall()]
    def get_scores_from_session_id_dict(self, session_id: int) -> dict:
        """ returns { "{player_id}": {score}, ... } """
        result = {}
        logging.debug(self.get_scores_from_session_id(session_id))
        for score in self.get_scores_from_session_id(session_id):
            result[str(score["player_id"])] = score
        return result
    def get_scores_by_player_id_as_dict_list(self, player_id: int) -> list:
        return [self.score_to_dict(x) for x in self.get_scores_by_player_id(player_id)]
    def get_scores_by_player_id(self, player_id: int):
        self.cur.execute(f"SELECT * FROM scores WHERE player_id = {player_id}")
        return self.cur.fetchall()
    def score_to_dict(self, score_list) -> dict:
        result = self.zip_to_dict(self.SCORE_COLS, score_list)
        result["total"] = sum([int(v) for k,v in result.items() if "id" not in k and v != -1])
        result["player_name"] = self.get_player_name(result["player_id"])
        return result
    def get_game_description(self, game_id:int) -> str:
        self.cur.execute(f"SELECT description FROM games WHERE id = {game_id}")
        return self.cur.fetchone()[0]
    def get_game(self, game_id):
        self.cur.execute(f"SELECT * FROM games WHERE id = {game_id}")
        return self.zip_to_dict(self.GAMES_COLS, self.cur.fetchone())
    def insert(self, table, entities):
        """ docstring """
        insert_str = self.TABLES_INSERT[table]
        self.cur.execute(insert_str, entities)
        self.con.commit()
        return self.get_last_row_id()


class CachoManager():
    """ docstring """
    def __init__(self):
        self.db = CachoDBManager()
        self.queue_index = 0
        self.curr_game_id = None
        self.curr_session_id = None
    def set_score_ones(self, value, sid):
        self.db.update_score(sid, "ones", value)
    def set_current_score_ones(self, value):
        self.set_score_ones(value, self.get_current_player_score_id())
    def set_score_twos(self, value, sid):
        self.db.update_score(sid, "twos", value)
    def set_current_score_twos(self, value):
        self.set_score_twos(value, self.get_current_player_score_id())
    def set_score_threes(self, value, sid):
        self.db.update_score(sid, "threes", value)
    def set_current_score_threes(self, value):
        self.set_score_threes(value, self.get_current_player_score_id())
    def set_score_fours(self, value, sid):
        self.db.update_score(sid, "fours", value)
    def set_current_score_fours(self, value):
        self.set_score_fours(value, self.get_current_player_score_id())
    def set_score_fives(self, value, sid):
        self.db.update_score(sid, "fives", value)
    def set_current_score_fives(self, value):
        self.set_score_fives(value, self.get_current_player_score_id())
    def set_score_sixes(self, value, sid):
        self.db.update_score(sid, "sixes", value)
    def set_current_score_sixes(self, value):
        self.set_score_sixes(value, self.get_current_player_score_id())
    def set_score_straight(self, value, sid):
        self.db.update_score(sid, "straight", value)
    def set_current_score_straight(self, value):
        self.set_score_straight(value, self.get_current_player_score_id())
    def set_score_full(self, value, sid):
        self.db.update_score(sid, "full", value)
    def set_current_score_full(self, value):
        self.set_score_full(value, self.get_current_player_score_id())
    def set_score_poker(self, value, sid):
        self.db.update_score(sid, "poker", value)
    def set_current_score_poker(self, value):
        self.set_score_poker(value, self.get_current_player_score_id())
    def set_score_grande(self, value, sid):
        self.db.update_score(sid, "grande", value)
    def set_current_score_grande(self, value):
        self.set_score_grande(value, self.get_current_player_score_id())
    def set_score_tutti(self, value, sid):
        self.db.update_score(sid, "tutti", value)
    def set_current_score_tutti(self, value):
        self.set_score_tutti(value, self.get_current_player_score_id())
    def get_current_player(self) -> int:
        return self.player_queue[self.queue_index]
    def get_next_player(self):
        self.queue_index = (self.queue_index + 1) % len(self.player_queue)
        return self.get_current_player()
    def get_current_player_score_id(self):
        return self.player_scores[str(self.get_current_player())]
    def get_current_player_score_card(self):
        return self.get_score_card(self.get_current_player_score_id())
    def get_score_card(self, score_id: int) -> dict:
        return self.db.get_score(score_id)
    def get_list_of_games(self):
        return self.db.get_table("games")
    def get_players_in_current_game(self):
        return self.get_players_in_game(self.curr_game_id)
    def get_players_in_game(self, game_id):
        return [ (x, self.db.get_player_name(x)) for x in self.get_player_ids(game_id) ]
    def get_player_ids(self, game_id):
        game = self.db.get_game(game_id)
        return [ int(x) for x in game["players"].split(",") ]
    def get_all_players(self):
        return self.db.get_table("players")
    def player_ids_to_names(self, player_ids):
        return [ self.db.get_player_name(x) for x in player_ids ]
    def set_player_order(self, player_queue):
        self.player_queue = player_queue
    def get_player_order(self):
        return self.player_queue
    def delete_current_session(self):
        for _, v in self.player_scores.items():
            logging.debug(f"Deleting score id: {v}")
            self.db.delete_record_id("scores", v)
        logging.debug(f"Deleting session id: {self.curr_session_id}")
        self.db.delete_record_id("sessions", self.curr_session_id)
    def delete_active_session(self, session_id: int):
        """ deletes active session including scores """
        for score in self.db.get_scores_from_session_id(session_id):
            self.db.delete_record_id("scores", score["id"])
        self.db.delete_record_id("sessions", session_id)
    def end_current_session(self):
        high_score_id = None
        low_score_id = None
        low_score_value = 10000
        high_score_value = 0
        for _, score_id in self.player_scores.items():
            score = self.db.get_score(score_id)
            for k, v in score:
                logging.debug(f"score: {score}")
                if v == -1:
                    self.db.update_score(score_id, k, 0)  # update the scores in database
                logging.debug(f"Updated score: {self.db.get_score(score_id)}")
            logging.debug(f"Total for this score: {score['total']}")
            if score["total"] > high_score_value:
                logging.debug(f"New high score replaces {high_score_value}")
                high_score_value = score["total"]
                high_score_id = score_id
                self.db.set_session_winner(self.curr_session_id, high_score_id)
            if score["total"] < low_score_value:
                logging.debug(f"New low score replaces {low_score_value}")
                low_score_value = score["total"]
                low_score_id = score_id
                self.db.set_session_looser(self.curr_session_id, low_score_id)

    def get_current_total(self):
        return self.get_current_player_score_card()["total"]
    def generate_game_session(self):
        self.curr_session_id = self.generate_session(game_id)
        self.player_scores = {}
        for score in self.db.get_scores_from_session_id(self.curr_session_id):
            player_id = str(score["player_id"])
            self.player_scores[player_id] = score["id"]
        return self.curr_session_id
    def generate_session(self, game_id: int) -> int:
        player_ids = self.get_player_ids(game_id)
        session_id = self.db.create_session()
        for player_id in player_ids:
            self.db.create_score(player_id, session_id, game_id)
        return session_id
    def generate_player_stats(self, player_id: int, game_id=None) -> dict:
        scores = self.db.get_scores_by_player_id_as_dict_list(player_id)
        logging.debug(f"list of scores: {scores}")
        if game_id:
            scores = [x for x in scores if int(x["game_id"]) == int(game_id)]
            logging.debug(f"list of scores with game_id of {game_id}: {scores}")
        games_played = len(scores)
        total_grandes = 0
        total_tuttis = 0
        sessions_won = [ int(x) for x in self.db.get_sessions_won_by_player_id(player_id) ]
        logging.debug(f"sessions won: {sessions_won}")
        total_wins = [ x for x in scores if int(x["game_id"]) == int(game_id) and int(x["session_id"]) in sessions_won ]
        sessions_lowest = [ int(x) for x in self.db.get_sessions_lowest_by_player_id(player_id) ]
        total_last = [ x for x in scores if int(x["game_id"]) == int(game_id) and int(x["session_id"]) in sessions_lowest ]
        logging.debug(f"sessions lowest score: {sessions_lowest}")
        total_score = 0
        high_score = 0
        for score in scores:
            if score['grande'] > 0:
                total_grandes += 1
            if score["tutti"] > 0:
                total_tuttis += 1
            if score["total"] > high_score:
                high_score = score["total"]
            total_score += score["total"]
        return {
            "player name": self.db.get_player_name(player_id),
            "games played": games_played,
            "high score": high_score,
            "average score": total_score / games_played if games_played != 0 else 0,
            "total Grandes": total_grandes,
            "total Tuttis": total_tuttis,
            "total wins": len(sessions_won),
            "total last place": len(sessions_lowest),
            "subtotal wins": len(total_wins),
            "subtotal last places": len(total_last)
        }
    

def print_line():
    print("================================")
def print_games(cm):
    table = cm.get_list_of_games()
    print_line()
    print("Game ID\t\tPlayers\t\tDescription")
    for row in table:
        game_id = row[0]
        player_ids = cm.get_player_ids(game_id)
        player_names = cm.player_ids_to_names(player_ids)
        game_description = row[2]
        print(f"{game_id}\t\t{player_names}\t\t{game_description}")
def game_selection_menu(cm):
    print_line()
    print("Select your game...")
    opt = None
    while not opt:
        print_games(cm)
        opt = input("Select game ID: ")
        logging.debug(f"selected game ID: {opt}")
        if opt and cm.db.get_game(opt) is None:
            opt = None
    cm.curr_game_id = opt
    return opt
def print_players(players):
    print_line()
    print("Player ID\t\tPlayer Name")
    for player in players:
        print(f"{player[0]}\t\t{player[1]}")
def game_create_menu(cm, descr):
    print_line()
    print(f"Create a game: {descr}")
    players = cm.get_all_players()
    print_players(players)
    max_players = len(players)
    selected_players = []
    num_players = 0
    while num_players < 1:
        num_players = int(input(f"How many players [max: {max_players}]?"))
        if num_players > max_players:
            num_players = 0
    while len(selected_players) < num_players:
        print_players(players)
        print(f"Current ids: {selected_players}")
        curr = len(selected_players) + 1
        select = int(input(f"Add player ID [{curr}/{num_players}]: "))
        if select not in selected_players:
            selected_players.append(select)
    print(f"{num_players} player game created as {descr}")
    return cm.db.create_game(selected_players, descr)
def menu_player_order(players):
    print_line()
    print("Define order of players")
    player_order = []
    while len(player_order) < len(players):
        print_players(players)
        print(f"Current Players Order: {player_order}")
        select = int(input("Select ID of next player: "))
        if select not in player_order:
            player_order.append(select)
    return player_order
def print_current_player_card(cm: CachoManager):
    print_player_card(cm, cm.get_current_player())
def print_player_card(cm: CachoManager, player_id: int):
    print_line()
    score_card = cm.get_score_card(cm.player_scores[str(player_id)])
    print(f"Player: {score_card['player_name']}\t|\tTotal: {score_card['total']}")
    print(f"{score_card['ones']}\t|\t{score_card['straight']}\t|\t{score_card['fours']}")
    print("----------------------------")
    print(f"{score_card['twos']}\t|\t{score_card['full']}\t|\t{score_card['fives']}")
    print("----------------------------")
    print(f"{score_card['threes']}\t|\t{score_card['poker']}\t|\t{score_card['sixes']}")
    print("----------------------------")
    print(f"Grande: {score_card['grande']}\t|\tTutti: {score_card['tutti']}")

def session_menu(cm: CachoManager):
    print_line()
    print("Session Menu:")
    select = None
    while True:
        print("Enter slot 1 - 6 or s=straight, f=full, p=poker, g=grande, t=tutti")
        print("c=card, v=view all cards, a=stats, q=quit(delete), e=end game")
        select = input("Selection: ")
        logging.debug(f"Selection: {select}")
        if not select:
            pass
        elif select[0] in "123456sfpgt":
            break
        elif select == "c":
            print_current_player_card(cm)
        elif select == 'v':
            for x in cm.get_players_in_current_game():
                print_player_card(cm, x[0])
        elif select == 'q':
            cm.delete_current_session()
            sys.exit()
        elif select == 'e':
            cm.end_current_session()
            for x in cm.get_players_in_current_game():
                print_player_card(cm, x[0])
            sys.exit()
        elif select == 'a':
            print(f"These are your stats for game called {cm.db.get_game_description(cm.curr_game_id)}")
            for k,v in cm.generate_player_stats(cm.get_current_player(), cm.curr_game_id).items():
                print(f"{k}: {v}")
    while True:
        value = input("Value: ")
        try:
            value = int(value)
            break
        except:
            print("Enter a valid number")
    if select == '1':
        cm.set_current_score_ones(value)
    elif select == '2':
        cm.set_current_score_twos(value)
    elif select == '3':
        cm.set_current_score_threes(value)
    elif select == '4':
        cm.set_current_score_fours(value)
    elif select == '5':
        cm.set_current_score_fives(value)
    elif select == '6':
        cm.set_current_score_sixes(value)
    elif select == 's':
        cm.set_current_score_straight(value)
    elif select == 'f':
        cm.set_current_score_full(value)
    elif select == 'p':
        cm.set_current_score_poker(value)
    elif select == 'g':
        cm.set_current_score_grande(value)
    elif select == 't':
        cm.set_current_score_tutti(value)
        
def start_game(cm: CachoManager):
    players = cm.get_players_in_current_game()
    cm.set_player_order(menu_player_order(players))
    cm.generate_game_session()
    in_progress = True
    while in_progress:
        print_current_player_card(cm)
        session_menu(cm)
        cm.get_next_player()

def menu_player_stats(cm: CachoManager):
    ids = []
    for x in cm.db.get_table("players"):
        ids.append(x[0])
        print(x)
    logging.debug(f"available id: {ids}")
    select = input("Select Player number for stats: ")
    if int(select) in ids:
        for k, v in cm.generate_player_stats(int(select)).items():
            print(f"{k}: {v}")

def parse_args():
    """ docstring """
    parser = argparse.ArgumentParser(description="PyCacho")
    parser.add_argument("-a", "--add-player", type=str, help="Creates a new player")
    parser.add_argument("-g", "--create-game", type=str, help="Creates a new game")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-l", "--list-players", action="store_true")
    parser.add_argument("-s", "--list-scores", action="store_true")
    parser.add_argument("-S", "--list-sessions", action="store_true")
    parser.add_argument("-p", "--player-stats", action="store_true", help="Get player stats")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    if args.verbose:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        logging.info("verbose mode set")
        logging.debug("verbose mode set")
    else:
        logging.basicConfig(stream=sys.stdout)
    cm = CachoManager()
    if args.add_player:
        for x in cm.db.get_player_names():
            if x == args.add_player:
                logging.error(f"User {args.add_user} already exists!")
                sys.exit(1)
        cm.db.create_player(args.add_player)
        sys.exit()
    elif args.player_stats:
        menu_player_stats(cm)
        sys.exit()
    elif args.list_players:
        print("Available Players")
        for x in cm.db.get_player_names():
            print(x)
        sys.exit()
    elif args.list_scores:
        cm.db.print_table("scores")
        sys.exit()
    elif args.list_sessions:
        table = cm.db.get_table("sessions")
        for row in table:
            print(f"id: {row[0]} date: {cm.db.get_session_date(int(row[0]))} high score id: {row[2]} low score id: {row[3]}")
        sys.exit()
    elif args.create_game:
        game_create_menu(cm, args.create_game)
        sys.exit()
    game_id = game_selection_menu(cm)
    try:
        start_game(cm)
    except Exception as e:
        logging.exception(e)
        logging.debug("Destroy current sessions...")
        cm.delete_current_session()