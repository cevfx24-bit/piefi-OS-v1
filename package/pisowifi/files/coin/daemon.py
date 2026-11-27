import time, logging, yaml, serial, os, sys
sys.path.append('/opt/pisowifi')
from lib import db, firewall

logging.basicConfig(level=logging.INFO, format="%(asctime)s [coin] %(message)s")

def main():
    try:
        with open("/etc/pisowifi/config.yaml") as f: cfg = yaml.safe_load(f)
    except Exception as e:
        logging.error(f"Config error: {e}"); return
    db.init()
    cmap = {int(k): int(v) for k, v in cfg["coin"]["coin_map"].items()}
    rate = cfg["billing"]["rate_per_peso_minutes"]
    
    while True:
        try:
            ser = serial.Serial(cfg["coin"]["serial_port"], cfg["coin"]["baudrate"], timeout=1)
            break
        except Exception:
            time.sleep(3)

    logging.info("Coin daemon ready")
    while True:
        line = ser.readline().decode(errors="ignore").strip()
        if not line.startswith("COIN:"): continue
        try: pulses = int(line.split(":")[1])
        except: continue
        peso = cmap.get(pulses)
        if not peso: continue
        
        seconds = peso * rate * 60
        target = db.oldest_pending(within_seconds=90)
        if target:
            db.credit_client(target["mac"], seconds, peso)
            firewall.add_authorized(target["mac"])
            logging.info(f"Credited {target['mac']} +P{peso} (+{seconds}s)")
        else:
            logging.warning(f"Coin P{peso} dropped. No pending session.")

if __name__ == "__main__": main()
