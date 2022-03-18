import argparse
from datetime import datetime, tzinfo
import logging
import os
import sqlite3
import sys

logging.basicConfig(level=logging.DEBUG)

class CachoDBManager():
    TABLES_INSERT ={
                "players": "INSERT INTO players(id, description) VALUES(NULL, ?)",
                "sessions": "INSERT INTO sessions(id, date) VALUES(NULL, ?)",
                "games": "INSERT INTO games(id, players, description) VALUES(NULL, ?, ?)",
                "scores": "INSERT INTO scores(id, player_id, session_id, game_id, ones, twos, threes, fours, fives, sixes, straight, full, poker, grande, tutti) VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            }
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
                            (id integer PRIMARY KEY, date text, winner integer, looser integer)''')
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
    def get_table(self, table: str):
        self.cur.execute(f'SELECT * FROM {table}')
        return self.cur.fetchall()
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
    def get_session_date(self, session_id: int) -> datetime:
        self.cur.execute(f"SELECT date FROM sessions WHERE id = {session_id}")
        epoch = self.cur.fetchone()[0]
        return datetime.fromtimestamp(int(epoch))
    def set_session_winner(self, session_id: int, player_id: int):
        self.update_sessions_table(session_id, "winner", str(player_id))
    def set_session_looser(self, session_id: int, player_id: int):
        self.update_sessions_table(session_id, "looser", str(player_id))
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
        return self.cur.fetchone()
    def get_game(self, game_id):
        self.cur.execute(f"SELECT * FROM games WHERE id = {game_id}")
        return self.cur.fetchone()
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
        self.set_score_three(value, self.get_current_player_score_id())
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
    def get_current_player(self):
        return self.player_queue[self.queue_index]
    def get_next_player(self):
        self.queue_index = (self.queue_index + 1) % len(self.player_queue)
        return self.get_current_player()
    def get_current_player_score_id(self):
        return self.player_scores[str(self.get_current_player())]
    def get_current_player_score_card(self):
        return self.get_score_card(self.get_current_player_score_id())
    def get_score_card(self, score_id):
        return self.db.get_score(score_id)
    def get_list_of_games(self):
        return self.db.get_table("games")
    def get_players_in_current_game(self):
        return self.get_players_in_game(self.curr_game_id)
    def get_players_in_game(self, game_id):
        return [ (x, self.db.get_player_name(x)) for x in self.get_player_ids(game_id) ]
    def get_player_ids(self, game_id):
        game = self.db.get_game(game_id)
        return [ int(x) for x in game[1].split(",") ]
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
    def end_current_session(self):
        for k, v in self.player_scores.items():

            for score in self.db.get_score(v):
                logging.debug(f"score: {score}")

    def get_current_total(self):
        return self.get_total(self.get_current_player_score_card())
    def get_total(self, scores):
        scores = scores[4:]
        total = 0
        for score in scores:
            if score != -1:
                total += score
        return total
    def generate_game_session(self):
        self.curr_session_id = self.db.create_session()
        self.player_scores = {}
        for player_id in self.player_queue:
            score_id = self.db.create_score(player_id, self.curr_session_id, self.curr_game_id)
            self.player_scores[str(player_id)] = score_id
        return self.curr_session_id
    

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
def print_current_player_card(cm):
    print_player_card(cm, cm.get_current_player())
def print_player_card(cm, player_id):
    print_line()
    player_name = cm.db.get_player_name(player_id)
    score_card = cm.get_score_card(cm.player_scores[str(player_id)])
    one = score_card[4]
    two = score_card[5]
    three = score_card[6]
    four = score_card[7]
    five = score_card[8]
    six = score_card[9]
    straight = score_card[10]
    full = score_card[11]
    poker = score_card[12]
    grande = score_card[13]
    tutti = score_card[14]
    print(f"Player: {player_name}\t|\tTotal: {cm.get_total(score_card)}")
    print(f"{one}\t|\t{straight}\t|\t{four}")
    print("----------------------------")
    print(f"{two}\t|\t{full}\t|\t{five}")
    print("----------------------------")
    print(f"{three}\t|\t{poker}\t|\t{six}")
    print("----------------------------")
    print(f"Grande: {grande}\t|\tTutti: {tutti}")

def session_menu(cm):
    print_line()
    print("Session Menu:")
    select = None
    while True:
        print("Enter slot 1 - 6 or s=straight, f=full, p=poker, g=grande, t=tutti")
        print("c=card, v=view all, q=quit(delete), e=end game")
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
            sys.exit()
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
        
def start_game(cm):
    players = cm.get_players_in_current_game()
    cm.set_player_order(menu_player_order(players))
    cm.generate_game_session()
    in_progress = True
    while in_progress:
        print_current_player_card(cm)
        session_menu(cm)
        cm.get_next_player()


def parse_args():
    """ docstring """
    parser = argparse.ArgumentParser(description="PyCacho")
    parser.add_argument("-a", "--add-player", type=str, help="Creates a new player")
    parser.add_argument("-g", "--create-game", type=str, help="Creates a new game")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-l", "--list-players", action="store_true")
    parser.add_argument("-s", "--list-scores", action="store_true")
    parser.add_argument("-S", "--list-sessions", action="store_true")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(stream=sys.stdout)
    if args.add_player:
        db = CachoDBManager()
        for x in db.get_player_names():
            if x == args.add_player:
                logging.error(f"User {args.add_user} already exists!")
                sys.exit(1)
        db.create_player(args.add_player)
        sys.exit()
    if args.list_players:
        db = CachoDBManager()
        print("Available Players")
        for x in db.get_player_names():
            print(x)
        sys.exit()
    if args.list_scores:
        db = CachoDBManager()
        db.print_table("scores")
        sys.exit()
    if args.list_sessions:
        db = CachoDBManager()
        table = db.get_table("sessions")
        for row in table:
            print(f"id: {row[0]} date: {db.get_session_date(int(row[0]))}")
        sys.exit()
    if args.create_game:
        game_create_menu(CachoManager(), args.create_game)
        sys.exit()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    cm = CachoManager()
    game_id = game_selection_menu(cm)
    start_game(cm)
