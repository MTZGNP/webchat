import hashlib

from flask import Flask,session,render_template,request,redirect,url_for,jsonify
import os
from datetime import datetime
app = Flask(__name__)
app.secret_key = os.urandom(64)
def encrypt(hash_string):
    return hashlib.sha256(hash_string.encode()).hexdigest()
messages = [["","",""]]*8
users = {
    "mtz.gnp":"0d945621a8ae7755c3c1c8b0ff9c60e9de3ab199e9376cb127430151c2b50065"
}

@app.route("/admin" ,methods = ["GET","POST"])
def admin():
    if session.get("nickname") == "mtz.gnp":
        if request.method == "POST":
            users[request.form["un"]]=encrypt(request.form["pw"])
            print(users)
        return render_template("adminpage.html",uns = users.keys())
    else:
        return redirect(url_for('home'))
@app.route("/send" , methods=["POST"])
def send():
    if session.get('logged_in'):
        dateTimeObj = datetime.now()
        timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S)")
        messages.pop(0)
        messages.append((session["nickname"], timestampStr, request.form["message"]))
    return redirect(url_for('home'))
@app.route("/")
def home():
    if not session.get('logged_in'):
        return render_template("login.html")
    else:
        return render_template("chat.html",messages = messages)

@app.route("/chat", methods=["GET"])
def renderchat():
    if not session.get('logged_in'):
        return redirect(url_for('home'))
    else:
        return render_template("chatrenderer.html",messages = messages)
@app.route("/login",methods=["POST"])
def login():
    if request.form["un"] in users.keys():
        if encrypt(request.form["pw"]) == users[request.form["un"]]:
            session['logged_in'] =True
            session['nickname'] = request.form["un"]
            print (request.form["un"],"logged in")
    return redirect(url_for('home'))
    return home()
@app.route("/logout",methods=["GET"])
def logout():
    session['logged_in'] = False
    session['nickname'] =None
    return redirect(url_for('home'))
if __name__ == "__main__":

    app.run()
