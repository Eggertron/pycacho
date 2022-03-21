from distutils.command.config import config
from flask import Flask, jsonify, render_template, session
from flask_cors import CORS
from pycacho import CachoDBManager
from textwrap import dedent

app = Flask(__name__)
app.config.from_object(__name__)
CORS(app, resources={r"/*": {'origins': "*"}})

# Main single page React
@app.route("/", methods=["GET"])
@app.route("/hello/<id>")
def greetings(id=None):
    return render_template('board.html', session_id=id)

@app.route("/session/<id>")
def get_session(id=None):
    db = CachoDBManager()
    session =  db.get_scores_from_session_id_dict(int(id))
    return session

@app.route("/main/<id>")
def main(id=None):
    db = CachoDBManager()
    session = db.get_scores_from_session_id_dict(int(id))
    data = {}
    for k, v in session.items():
        data[db.get_player_name(int(k))] = v
    title = "testing"
    return render_template("template.html", title=title, data=data)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")