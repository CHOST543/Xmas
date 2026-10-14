"""CHOST: per-install secret paths.
Every fork / every deploy gets its own random config paths on first boot (saved on the volume),
so no two panels share the same paths. Paths never change after that, so existing configs never break."""
import json, os, secrets, uuid

DATA = os.getenv("CHOST_DATA", "/var/lib/pasarguard")
OUT_JSON = f"{DATA}/paths.json"
OUT_INC = f"{DATA}/inbounds.inc"
# tag -> (local port, path prefix)   CHOST VIP: CH-V1..V3   CHOST GAME: CH-G1..G3
SLOTS = {"CH-V1-VLESS-WS": (10001, "/ws/"), "CH-V2-VMESS-WS": (10002, "/stream/"), "CH-V3-VLESS-HU": (10003, "/cdn/"),
         "CH-G1-VLESS-WS": (10004, "/play/"), "CH-G2-TROJAN-WS": (10005, "/live/"), "CH-G3-VLESS-HU": (10006, "/edge/")}

def load():
    try:
        with open(OUT_JSON) as f: p = json.load(f)
        if all(isinstance(p.get(t), str) and p[t].startswith("/") for t in SLOTS): return p
    except Exception: pass
    return None

def main():
    os.makedirs(DATA, exist_ok=True)
    p = load()
    if p is None:
        p = {t: pre + str(uuid.UUID(bytes=secrets.token_bytes(16), version=4)) for t, (_, pre) in SLOTS.items()}
        print("[paths] new install: unique config paths generated")
        tmp = OUT_JSON + ".tmp"
        with open(tmp, "w") as f: json.dump(p, f, indent=1)
        os.replace(tmp, OUT_JSON)
    lines = [f"location = {p[t]} {{ proxy_pass http://127.0.0.1:{port}; include /etc/nginx/ws.inc; }}"
             for t, (port, _) in SLOTS.items()]
    with open(OUT_INC, "w") as f: f.write(chr(10).join(lines) + chr(10))

if __name__ == "__main__":
    main()
