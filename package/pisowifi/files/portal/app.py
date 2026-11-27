import sys, os
sys.path.append('/opt/pisowifi')
from flask import Flask, request, render_template, jsonify, redirect
import yaml, subprocess
from lib import db, session

app = Flask(__name__)
with open("/etc/pisowifi/config.yaml") as f: CFG = yaml.safe_load(f)
db.init()

app._session_mgr = session.SessionManager()
app._session_mgr.start()

def client_mac():
    ip = request.remote_addr
    try:
        out = subprocess.check_output(["ip", "neigh", "show", ip], text=True)
        return out.split()[4].lower()
    except: return None

@app.route("/")
def index():
    mac = client_mac()
    if not mac: return "Cannot resolve MAC", 400
    db.upsert_client(mac, ip=request.remote_addr)
    c = db.get_client(mac)
    if c["authorized"] and c["remaining_seconds"] > 0:
        return render_template("status.html", c=c, cfg=CFG)
    return render_template("login.html", c=c, cfg=CFG)

@app.route("/api/insert-coin", methods=["POST"])
def insert_coin():
    mac = client_mac()
    if mac:
        db.upsert_client(mac, ip=request.remote_addr)
        db.set_pending(mac)
        return jsonify(ok=True, wait=CFG["billing"]["pending_timeout_seconds"])
    return jsonify(ok=False), 400

@app.route("/api/status")
def status():
    mac = client_mac()
    c = db.get_client(mac) if mac else None
    if not c: return jsonify(ok=False), 404
    return jsonify(ok=True, authorized=bool(c["authorized"]), remaining=c["remaining_seconds"], paused=bool(c["paused"]), pending=bool(c["pending"]))

@app.route("/api/pause", methods=["POST"])
def pause():
    mac = client_mac()
    c = db.get_client(mac)
    if c and c["authorized"]:
        db.set_paused(mac, not c["paused"])
        return jsonify(ok=True, paused=not c["paused"])
    return jsonify(ok=False), 400

@app.route("/generate_204")
@app.route("/hotspot-detect.html")
def captive(): return redirect("http://10.0.0.1/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=CFG["network"]["portal_port"])
