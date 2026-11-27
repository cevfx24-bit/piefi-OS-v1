import subprocess, logging
SET_NAME = "authorized_macs"
TABLE = "inet pisowifi"

def _run(args):
    try:
        subprocess.run(["nft"] + args, check=True, capture_output=True)
    except Exception as e:
        logging.error(f"nft error: {e}")

def add_authorized(mac):
    _run(["add", "element", TABLE, SET_NAME, "{", mac.lower(), "}"])

def remove_authorized(mac):
    _run(["delete", "element", TABLE, SET_NAME, "{", mac.lower(), "}"])
