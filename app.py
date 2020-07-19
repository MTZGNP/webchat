import hashlib

from flask import Flask, session, render_template, request, redirect, url_for, jsonify
import secrets
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(64)


def encrypt(hash_string):
    return hashlib.sha256(hash_string.encode()).hexdigest()

invitekeys = []
messages = [["", "", ""]] * 8
users = {
    "mtz.gnp": "0d945621a8ae7755c3c1c8b0ff9c60e9de3ab199e9376cb127430151c2b50065"
}

@app.route("/dump")
def dump():
    if session.get("nickname") == "mtz.gnp" and session.get("logged_in") :
        return jsonify({"users":users,"inviteTokens":invitekeys})
    return "401 unauthorized"
@app.route("/admin", methods=["GET"])
def adminpage():
    if session.get("nickname") == "mtz.gnp":
        return render_template("adminpage.html", uns=users.keys()  )
    else:
        return redirect(url_for('home'))
    
@app.route("/geninvite", methods=["GET"])
def geninvite():
    if session.get("nickname") == "mtz.gnp":
        token = secrets.token_urlsafe(4)
        invitekeys.append(token)
        return "gnp1auth.pythonanywhere.com/invite?token=%s" % token
    else:
        return redirect(url_for('home'))
@app.route("/invite", methods=["GET"])
def invite():
    if request.args["token"] in invitekeys:
        session.clear()
        return render_template("register.html" , token = request.args["token"])
    else:
        return "401 unauthorized"
@app.route("/register", methods=["POST"])
def signup():
    if request.args["token"] in invitekeys:
        session.clear()
        users[request.form["un"]] = encrypt(request.form["pw"])
        invitekeys.remove(request.args["token"])
        return redirect(url_for("home"))
    else:
        return "401 unauthorized"
@app.route("/adminaction", methods=["POST"])
def adminaction():
    global users
    global messages
    if session.get("nickname") == "mtz.gnp":
        if request.args["action"] == "add":
            users[request.form["un"]] = encrypt(request.form["pw"])
        elif request.args["action"] == "remove":
            users.pop(request.form["un"])
        elif request.args["action"] == "reset":
            if request.form["reset"] == "users":
                users = {
                    "mtz.gnp": "0d945621a8ae7755c3c1c8b0ff9c60e9de3ab199e9376cb127430151c2b50065"
                }
            elif request.form["reset"] == "messages":
                messages = [["", "", ""]] * 8
        
        return redirect(url_for('adminpage'))
    else:
        return redirect(url_for('home'))


@app.route("/send", methods=["POST"])
def send():
    if session.get('logged_in'):
        dateTimeObj = datetime.now()
        timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S)")
        messages.pop(0)
        messages.append((session["nickname"], timestampStr, request.form["message"]))
        return "202 success"
    return "401 unauthorized"


@app.route("/")
def home():
    if not session.get('logged_in'):
        return render_template("login.html")
    else:
        return render_template("chat.html", messages=messages)


@app.route("/chat", methods=["GET"])
def renderchat():
    if not session.get('logged_in'):
        return redirect(url_for('home'))
    else:
        return render_template("chatrenderer.html", messages=messages,current = session["nickname"])


@app.route("/login", methods=["POST"])
def login():
    if request.form["un"] in users.keys():
        if encrypt(request.form["pw"]) == users[request.form["un"]]:
            session['logged_in'] = True
            session['nickname'] = request.form["un"]
            print(request.form["un"], "logged in")
    return redirect(url_for('home'))
    return home()


@app.route("/logout", methods=["GET"])
def logout():
    session['logged_in'] = False
    session['nickname'] = None
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run()
