import sys, os
sys.path.append('/opt/pisowifi')
from flask import Flask, render_template, request, redirect, session as flask_sess, jsonify
import yaml, hashlib
from lib import db, firewall

app = Flask(__name__)
with open("/etc/pisowifi/config.yaml") as f: CFG = yaml.safe_load(f)
app.secret_key = CFG["admin"]["session_secret"]
db.init()

def check_login(u, p):
    stored = db.get_setting("admin_hash") or hashlib.sha256("admin").hexdigest()
    return hashlib.sha256(p.encode()).hexdigest() == stored

@app.route("/admin", methods=["GET", "POST"])
@app.route("/admin/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if check_login(request.form["u"], request.form["p"]):
            flask_sess["admin"] = True
            return redirect("/admin/sessions")
        return render_template("index.html", error="Invalid credentials")
    return render_template("index.html", error=None)

@app.route("/admin/sessions")
def sessions():
    if not flask_sess.get("admin"): return redirect("/admin")
    return render_template("sessions.html", sessions=db.list_sessions(), coins=db.recent_coins(15))

@app.route("/admin/revoke/<mac>", methods=["POST"])
def revoke(mac):
    if flask_sess.get("admin"):
        db.set_paused(mac, True)
        firewall.remove_authorized(mac)
    return redirect("/admin/sessions")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=CFG["network"]["admin_port"])
