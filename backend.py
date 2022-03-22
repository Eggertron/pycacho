from distutils.command.config import config
from flask import Flask, jsonify, render_template, request, flash, redirect, url_for
from flask_cors import CORS
from pycacho import CachoDBManager, CachoManager
from textwrap import dedent

app = Flask(__name__)
app.config.from_object(__name__)
CORS(app, resources={r"/*": {'origins': "*"}})

# Main single page React
@app.route("/", methods=["GET", "POST"])
def greetings():
    if request.method == 'POST':
        session_id = request.form['session_id']

        if not session_id:
            flash('Session id is required!')
        else:
            return redirect(f"/session/{session_id}")
    cm = CachoManager()
    return render_template('session_select_form.html', sessions=cm.db.get_sessions())

@app.route("/api/session/<id>")
def get_session(id=None):
    db = CachoDBManager()
    session =  db.get_scores_from_session_id_dict(int(id))
    return session

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
    data = {
        "score_id": score_id,
        "player_name": score["player_name"],
        "current_value": score[col],
        "col_name": col
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