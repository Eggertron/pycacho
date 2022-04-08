from flask import Flask, render_template, request, flash, redirect, url_for
from flask_cors import CORS
from pycacho import CachoDBManager, CachoManager

app = Flask(__name__)
app.config.from_object(__name__)
CORS(app, resources={r"/*": {'origins': "*"}})

# Main single page React
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/new_session", methods=["GET", "POST"])
def new_session():
    if request.method == "POST":
        cm = CachoManager()
        game_id = request.form["game_id"]
        session_id = cm.generate_session(game_id)
        return redirect(f"/session_/{session_id}")
    games = get_games()
    return render_template("new_session_form.html", data=games)

@app.route("/players")
def players():
    db = CachoDBManager()
    players = {}
    for player in db.get_players():
        players[player["id"]] = player
    return render_template("players_form.html", players=players)

@app.route("/games")
def games():
    games = get_games()
    return render_template("games_form.html", data=games)

@app.route("/api/games")
def get_games():
    db = CachoDBManager()
    games = db.get_games()
    print(games)
    data = {}
    for game in games:
        names = " , ".join([db.get_player_name(n) for n in game['players'].split(',')])
        data[str(game['id'])] = {
            "id": game['id'],
            "player_ids": game['players'],
            "player_names": names,
            "description": game['description']
        }
    return data

@app.route("/new_game")
def new_game():
    cm = CachoManager()
    

@app.route("/session_selector", methods=["GET", "POST"])
def session_selector():
    if request.method == 'POST':
        session_id = request.form['session_id']

        if not session_id:
            flash('Session id is required!')
        else:
            return redirect(f"/session/{session_id}")
    cm = CachoManager()
    return render_template('session_select_form.html', sessions=cm.db.get_sessions())

@app.route("/api/session/end/<id>")
def end_session(id=None):
    cm = CachoManager()
    cm.end_session_id(id)
    return redirect(url_for("index"))

@app.route("/api/session/<id>")
def get_session(id=None):
    db = CachoDBManager()
    session =  db.get_scores_from_session_id_dict(int(id))
    return session

@app.route("/api/session/purge/<id>")
def purge_session(id=None):
    cm = CachoManager()
    cm.delete_active_session(int(id))
    return redirect(url_for("index"))

@app.route("/session/<session_id>")
def session(session_id=None):
    cm = CachoManager()
    scores = cm.db.get_scores_from_session_id_dict(int(session_id))
    data = {}
    for _, v in scores.items():
        data[v["player_name"]] = fix_score(v)
        data[v["player_name"]]["stats"] = cm.generate_player_stats(v["player_id"], v["game_id"])
    debug = request.args.get('debug')
    if debug:
        data['debug'] = debug
    title = f"Game Session: {session_id}"
    return render_template("session.html", title=title, data=data)

@app.route("/session_/<session_id>")
def session_(session_id=None):
    db = CachoDBManager()
    scores = db.get_scores_from_session_id_dict(int(session_id))
    data = {}
    for _, v in scores.items():
        data[v["player_name"]] = fix_score(v)
    debug = request.args.get('debug')
    if debug:
        data['debug'] = debug
    title = f"Game Session: {session_id}"
    return render_template("session_.html", title=title, data=data)

@app.route("/score/edit/<score_id>/<col>", methods=["GET", "POST"])
def edit_score_form(score_id=None, col=None):
    if request.method == 'POST':
        value = request.form['value']

        if not value:
            flash('value is required!')
        else:
            return redirect(f"/api/score/edit/{score_id}/{col}/{value}")
    db = CachoDBManager()
    score = db.get_score(int(score_id))
    mult = 0
    if col == "ones":
        mult = 1
    elif col == "twos":
        mult = 2
    elif col == "threes":
        mult = 3
    elif col == "fours":
        mult = 4
    elif col == "fives":
        mult = 5
    elif col == "sixes":
        mult = 6
    selections = [ x * mult for x in range(6)]
    if col == "straight":
        selections = [ 0, 20, 25]
    elif col == "full":
        selections = [ 0, 30, 35]
    elif col == "poker":
        selections = [ 0, 40, 45]
    elif col == "grande":
        selections = [ 0, 50]
    elif col == "tutti":
        selections = [ 0, 100]
    data = {
        "score_id": score_id,
        "player_name": score["player_name"],
        "current_value": score[col],
        "col_name": col,
        "selections": selections
    }
    return render_template("edit_score_form.html", data=data)

@app.route("/api/score/edit/<score_id>/<col>/<value>")
def edit_score(score_id=None, col=None, value=None):
    db = CachoDBManager()
    score = db.get_score(score_id)
    db.update_score(int(score_id), str(col), int(value))
    return redirect(f"/session_/{score['session_id']}")

@app.route("/api/score/<score_id>")
def get_score_card(score_id=None):
    db = CachoDBManager()
    return db.get_score(int(score_id))

def fix_score(score: dict) -> dict:
    result = {}
    for k, v in score.items():
        if v == -1:
            v = "🐞"
        elif v == 0:
            v = "❌"
        result[k] = v
    return result
            

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")