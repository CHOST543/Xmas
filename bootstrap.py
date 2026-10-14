"""CHOST bootstrap: zero-touch setup for PasarGuard on Railway. Idempotent: safe on every boot."""
import json, os, sys, time, urllib.error, urllib.parse, urllib.request

BASE = "http://127.0.0.1:8000"
PANEL_DIR = os.getenv("PANEL_DIR", "/code")   # where the PasarGuard panel code lives (found by entrypoint.sh)
DATA = os.getenv("CHOST_DATA", "/var/lib/pasarguard")
SEEN_DOMAIN = f"{DATA}/domain.txt"     # the address the owner really opens the panel with (sent by the panel page)
import re as _re
_DOM_RE = _re.compile(r"^(?=.{4,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$")
def dom():
    """public domain for configs and links: PUBLIC_DOMAIN > the domain the panel is opened with > Railway's domain.
    Read on every call, so a domain generated after the deploy is picked up without a redeploy."""
    d = (os.getenv("PUBLIC_DOMAIN") or "").strip().lower()
    if d: return d
    try:
        d = open(SEEN_DOMAIN).read().strip().lower()
        if _DOM_RE.match(d): return d
    except Exception: pass
    return (os.getenv("RAILWAY_PUBLIC_DOMAIN") or "").strip().lower()
import subprocess
USER, PASS = "admin", "admin"          # first-boot login; change it later in the panel or with the owner key
RESELLER_USER, RESELLER_PASS, RESELLER_GB = "reseller", "reseller", 50
CORE_NAME, NODE_NAME = "CHOST-Core", "CHOST-Core"
VIP_GROUP, GAME_GROUP = "𝗖𝗛𝗢𝗦𝗧 VIP", "𝗖𝗛𝗢𝗦𝗧 GAME"   # speed (download/stream) / low ping (gaming/calls)
TITLE = os.getenv("CONFIG_TITLE", "CHOST")   # subscription title shown in the apps
GB = 1024 ** 3
DAY = 86400

# All configs go through Railway's TLS edge on 443 with alpn=http/1.1 (the only thing Railway serves).
# 6 configs that are really different (protocol / transport / fingerprint / path), all supported by
# v2rayNG, V2Box, Hiddify, Streisand, NekoBox, Shadowrocket, Clash Meta and sing-box.
# ?ed=2560 = early data on the WebSocket configs (one round trip less per connection). The HTTPUpgrade configs
# stay plain on purpose, so if an operator or a client app ever trips over early data, half the configs never depend on it.
# The symbol in the name tells the subscription page which group a config belongs to (✦ VIP, ◆ GAME).
INBOUNDS = [
    # tag                proto     port   net            path        fp         name                  group
    ("CH-V1-VLESS-WS",  "vless",  10001, "ws",          "/ws/",     "chrome",  "𝗖𝗛𝗢𝗦𝗧 ✦ Turbo",   "vip"),
    ("CH-V2-VMESS-WS",  "vmess",  10002, "ws",          "/stream/", "firefox", "𝗖𝗛𝗢𝗦𝗧 ✦ Stream",  "vip"),
    ("CH-V3-VLESS-HU",  "vless",  10003, "httpupgrade", "/cdn/",    "safari",  "𝗖𝗛𝗢𝗦𝗧 ✦ Ultra",   "vip"),
    ("CH-G1-VLESS-WS",  "vless",  10004, "ws",          "/play/",   "chrome",  "𝗖𝗛𝗢𝗦𝗧 ◆ Gaming",  "game"),
    ("CH-G2-TROJAN-WS", "trojan", 10005, "ws",          "/live/",   "edge",    "𝗖𝗛𝗢𝗦𝗧 ◆ Call",    "game"),
    ("CH-G3-VLESS-HU",  "vless",  10006, "httpupgrade", "/edge/",   "ios",     "𝗖𝗛𝗢𝗦𝗧 ◆ Stable",  "game"),
]
EARLY_DATA = "?ed=2560"
# real paths are unique per install (genpaths.py writes them to the volume before nginx starts)
def _load_paths():
    with open(f"{DATA}/paths.json") as f: return json.load(f)
try:
    _P = _load_paths()
except Exception as _e:
    # self-heal: write the paths now and let nginx pick them up, instead of waiting for a new deploy
    print("[bootstrap] paths.json missing, writing it now:", _e, flush=True)
    try:
        import subprocess
        subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "genpaths.py")], timeout=30)
        try: subprocess.run(["nginx", "-s", "reload"], timeout=15)
        except Exception: pass
        _P = _load_paths()
    except Exception as _e2:
        print("[bootstrap] paths still missing, trying again shortly:", _e2, flush=True)
        time.sleep(30); sys.exit(1)
INBOUNDS = [(t, pr, po, n, _P.get(t, pa), fp, nm, g) for (t, pr, po, n, pa, fp, nm, g) in INBOUNDS]
TEMPLATES = [  # name, GB, days, group
    ("VIP 10GB - 30 روز", 10, 30, "vip"), ("VIP 30GB - 30 روز", 30, 30, "vip"), ("VIP 50GB - 30 روز", 50, 30, "vip"),
    ("VIP 100GB - 30 روز", 100, 30, "vip"), ("VIP 200GB - 60 روز", 200, 60, "vip"), ("VIP نامحدود - 30 روز", 0, 30, "vip"),
    ("GAME 20GB - 30 روز", 20, 30, "game"), ("GAME 50GB - 30 روز", 50, 30, "game"),
    ("GAME 100GB - 30 روز", 100, 30, "game"), ("GAME نامحدود - 30 روز", 0, 30, "game"),
]

TOKEN = None

def log(*a): print("[bootstrap]", *a, flush=True)

_GLOBAL = object()

def req(method, path, body=None, form=False, ok=(200, 201, 204), token=_GLOBAL):
    """panel API call; if a route answers 404/405 because of a trailing slash difference between
    PasarGuard versions, the other spelling is tried once, so a panel update never breaks the setup"""
    code, res = _req(method, path, body, form, token)
    if code in (404, 405, 307, 308) and "?" not in path and len(path) > 5:
        alt = path[:-1] if path.endswith("/") else path + "/"
        c2, r2 = _req(method, alt, body, form, token)
        if c2 not in (404, 405, 307, 308): return c2, r2
    return code, res

def _req(method, path, body=None, form=False, token=_GLOBAL):
    url = BASE + path
    headers = {"Accept": "application/json"}
    data = None
    if body is not None:
        if form:
            data = urllib.parse.urlencode(body).encode(); headers["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            data = json.dumps(body).encode(); headers["Content-Type"] = "application/json"
    tok = TOKEN if token is _GLOBAL else token
    if tok: headers["Authorization"] = f"Bearer {tok}"
    r = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            raw = resp.read().decode()
            try: return resp.status, json.loads(raw) if raw.strip() else None
            except ValueError: return resp.status, raw
    except urllib.error.HTTPError as e:
        txt = e.read().decode(errors="ignore")
        try: return e.code, json.loads(txt)
        except Exception: return e.code, txt

def must(method, path, body=None):
    code, res = req(method, path, body)
    if code not in (200, 201, 204):
        raise RuntimeError(f"{method} {path} -> {code}: {res}")
    return res

def as_list(res, key):
    if isinstance(res, list): return res
    if isinstance(res, dict): return res.get(key) or []
    return []

def wait_panel():
    for _ in range(180):
        try:
            code, _ = req("GET", "/api/system")
            if code and code < 500: return
        except Exception: pass
        time.sleep(2)
    raise RuntimeError("panel did not come up")

TEMP_KEY_PY = """
import asyncio
from app.db.base import GetDB
from app.db.crud.temp_key import create_temp_key
async def main():
    async with GetDB() as db:
        k = await create_temp_key(db)
        print("KEY=" + k.key)
asyncio.run(main())
"""

def temp_key():
    out = subprocess.run([sys.executable, "-c", TEMP_KEY_PY], cwd=PANEL_DIR, capture_output=True, text=True, timeout=60)
    for line in out.stdout.splitlines():
        if line.startswith("KEY="): return line[4:].strip()
    raise RuntimeError(f"temp key failed: {out.stderr[-500:]}")

ADMIN_PW_PY = """
import asyncio, sys
from app.db.base import GetDB
from app.db.crud.admin import get_owner, get_admin
from app.models.admin import _hash_password_sync
async def main():
    mode, user, pw = sys.argv[1], sys.argv[2], sys.argv[3]
    async with GetDB() as db:
        if mode == "owner":
            o = await get_owner(db)
        else:
            o = await get_admin(db, user, load_users=False, load_usage_logs=False)
        if o is None:
            print("MISSING"); return
        o.username = user
        o.hashed_password = _hash_password_sync(pw)
        await db.commit()
        print("OK")
asyncio.run(main())
"""

def write_password(mode, user, pw):
    out = subprocess.run([sys.executable, "-c", ADMIN_PW_PY, mode, user, pw], cwd=PANEL_DIR,
                         capture_output=True, text=True, timeout=90)
    ok = out.stdout.strip().splitlines()[-1:] == ["OK"]
    if not ok: log(f"password write ({mode} {user}) failed:", (out.stdout + out.stderr)[-400:])
    return ok

def strong_tmp():
    import secrets
    return "Ch" + secrets.token_hex(8) + "Aa9!Zz7"

TOKEN_PY = """
import asyncio
from app.db.base import GetDB
from app.db.crud.admin import get_owner
from app.utils.jwt import create_admin_token
async def main():
    async with GetDB() as db:
        o = await get_owner(db)
        if o is None:
            print("NOOWNER"); return
        print("TOKEN=" + await create_admin_token(o.id, o.username))
asyncio.run(main())
"""

def owner_token():
    out = subprocess.run([sys.executable, "-c", TOKEN_PY], cwd=PANEL_DIR, capture_output=True, text=True, timeout=60)
    for line in out.stdout.splitlines():
        if line.startswith("TOKEN="): return line[6:].strip()
        if line.strip() == "NOOWNER": return None
    raise RuntimeError(f"token failed: {(out.stdout + out.stderr)[-400:]}")

MARKER = f"{DATA}/.owner_initialized"
RESELLER_MARKER = f"{DATA}/.reseller_initialized"

def ensure_owner():
    """First boot: owner = admin/admin. After that the password is YOURS: change it in the panel
    or with the owner key (sidebar page "امنیت حساب"). Bootstrap never touches it again."""
    if owner_token() is None:
        code, res = req("POST", "/api/setup/owner", {"key": temp_key(), "username": "chostowner", "password": strong_tmp()})
        if code not in (200, 201, 409): log(f"owner create failed {code}: {res}")
        if os.path.exists(MARKER): os.remove(MARKER)
    if not os.path.exists(MARKER):
        if write_password("owner", USER, PASS):
            open(MARKER, "w").write(str(int(time.time())))
            log("owner ready:", USER, "/", PASS, "(first boot)")

# ---- CHOST owner keys: CH-XXXX-XXXX-XXXX, 5 minutes, one use, kept on the volume (hashed) ----
import hashlib, secrets as _sec, threading as _th
KEYS_FILE = f"{DATA}/.owner_keys.json"
KEY_TTL = 300
_KEY_ALPHA = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
_klock = _th.Lock()

def _khash(k): return hashlib.sha256(("chost:" + k).encode()).hexdigest()

def _kload():
    try:
        with open(KEYS_FILE) as f: d = json.load(f)
        return {h: t for h, t in d.items() if isinstance(t, (int, float)) and t > time.time()}
    except Exception: return {}

def _ksave(d):
    tmp = KEYS_FILE + ".tmp"
    with open(tmp, "w") as f: json.dump(d, f)
    os.replace(tmp, KEYS_FILE)

def issue_key():
    body = "".join(_sec.choice(_KEY_ALPHA) for _ in range(12))
    key = "CH-" + "-".join(body[i:i + 4] for i in range(0, 12, 4))
    with _klock:
        d = _kload(); d[_khash(key)] = time.time() + KEY_TTL; _ksave(d)
    return key

def norm_key(k):
    s = "".join(c for c in str(k or "").upper() if c.isalnum())
    if s.startswith("CH"): s = s[2:]
    return "CH-" + "-".join(s[i:i + 4] for i in range(0, 12, 4)) if len(s) == 12 else ""

def use_key(k):
    k = norm_key(k)
    if not k: return False
    with _klock:
        d = _kload(); h = _khash(k)
        if h not in d: return False
        d.pop(h); _ksave(d)
    return True

def print_owner_key():
    try:
        k = issue_key()
        log("=" * 60)
        log("OWNER KEY (valid 5 min, one use):", k)
        log("use it on the login page (Owner access / دسترسی مالک) to set a new username and password")
        log("need a new key? Restart the service in Railway")
        log("=" * 60)
    except Exception as e:
        log("owner key failed:", e)

def login():
    global TOKEN
    ensure_owner()
    for _ in range(30):
        tok = owner_token()
        if tok:
            TOKEN = tok; return
        time.sleep(3)
    raise RuntimeError("could not get an owner token")

def inbound(tag, proto, port, net, path):
    stream = {"network": net, "security": "none"}
    if net == "ws": stream["wsSettings"] = {"path": path}
    elif net == "httpupgrade": stream["httpupgradeSettings"] = {"path": path}
    elif net == "xhttp": stream["xhttpSettings"] = {"path": path, "mode": "auto"}
    settings = {"clients": []}
    if proto == "vless": settings["decryption"] = "none"
    return {"tag": tag, "listen": "127.0.0.1", "port": port, "protocol": proto,
            "settings": settings, "streamSettings": {**stream, "sockopt": {"tcpNoDelay": True}},
            "sniffing": {"enabled": True, "destOverride": ["http", "tls", "quic"], "routeOnly": True}}

CORE_CONFIG = {
    "log": {"loglevel": "warning"},
    # system resolver first (fastest on Railway), DoH as backup; results are cached by Xray
    "dns": {"servers": ["localhost", "https+local://1.1.1.1/dns-query", "8.8.8.8"], "queryStrategy": "UseIP"},
    "inbounds": [inbound(*i[:5]) for i in INBOUNDS],
    "outbounds": [
        # AsIs = the system dialer (IPv4 and IPv6 with automatic fallback): works in every Railway region,
        # also where the outside network is IPv6 first
        {"protocol": "freedom", "tag": "DIRECT", "settings": {"domainStrategy": "AsIs"},
         "streamSettings": {"sockopt": {"tcpNoDelay": True, "tcpKeepAliveInterval": 30, "tcpKeepAliveIdle": 60}}},
        {"protocol": "blackhole", "tag": "BLOCK"},
    ],
    # AsIs: no DNS lookup before routing = lower latency on every new connection
    "routing": {"domainStrategy": "AsIs", "rules": [
        # plain ranges instead of geoip:private: the core never depends on geo files being present
        {"type": "field", "ip": ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8", "169.254.0.0/16",
                                 "fc00::/7", "fe80::/10", "::1/128"], "outboundTag": "BLOCK"},
        {"type": "field", "protocol": ["bittorrent"], "outboundTag": "BLOCK"},
    ]},
    "policy": {"levels": {"0": {"handshake": 4, "connIdle": 300, "uplinkOnly": 1, "downlinkOnly": 1, "bufferSize": 512}}},
}

def ensure_core():
    cores = as_list(must("GET", "/api/cores"), "cores")
    for c in cores:
        if c.get("name") == CORE_NAME:
            if c.get("name") == CORE_NAME and c.get("config") == CORE_CONFIG:
                log("core ok (unchanged)", c["id"]); return c["id"]
            body = {"name": CORE_NAME, "config": CORE_CONFIG, "exclude_inbound_tags": [], "fallbacks_inbound_tags": []}
            code, res = req("PUT", f"/api/core/{c['id']}?restart_nodes=true", body)
            if code not in (200, 201):  # node may still be starting: save config without restart
                code, res = req("PUT", f"/api/core/{c['id']}?restart_nodes=false", body)
            log("core updated" if code in (200, 201) else f"core update failed {code}: {res}", c["id"])
            return c["id"]
    c = must("POST", "/api/core", {"name": CORE_NAME, "config": CORE_CONFIG,
                                    "exclude_inbound_tags": [], "fallbacks_inbound_tags": []})
    log("core created", c["id"]); return c["id"]

def ensure_node(core_id):
    api_key = open(f"{DATA}/node_api_key").read().strip()
    cert = open(f"{DATA}/node-certs/cert.pem").read().strip()
    body = {"name": NODE_NAME, "address": "127.0.0.1", "port": 62050, "usage_coefficient": 1,
            "connection_type": "grpc", "server_ca": cert, "keep_alive": 60,
            "core_config_id": core_id, "api_key": api_key}
    for n in as_list(must("GET", "/api/nodes"), "nodes"):
        if n.get("name") == NODE_NAME:
            must("PUT", f"/api/node/{n['id']}", body); log("node updated"); return
    must("POST", "/api/node", body); log("node created")

def ensure_groups():
    """Two groups: VIP_GROUP -> the 3 ✦ configs, GAME_GROUP -> the 3 ◆ configs. Returns {"vip": id, "game": id}."""
    want = {"vip": (VIP_GROUP, [i[0] for i in INBOUNDS if i[7] == "vip"]),
            "game": (GAME_GROUP, [i[0] for i in INBOUNDS if i[7] == "game"])}
    groups = as_list(must("GET", "/api/groups"), "groups")
    by_name = {g.get("name"): g for g in groups}
    ids = {}
    for key, (name, tags) in want.items():
        g = by_name.get(name)
        if g:
            if sorted(g.get("inbound_tags") or []) != sorted(tags):
                must("PUT", f"/api/group/{g['id']}", {"name": name, "inbound_tags": tags}); log("group fixed:", name)
            ids[key] = g["id"]
        else:
            g = must("POST", "/api/group", {"name": name, "inbound_tags": tags}); ids[key] = g["id"]
            log("group created:", name, f"({len(tags)} configs)")
    return ids

QUIET = {}

def _norm(v):
    """compare host fields the same way whether the API returns a string, a list or an enum"""
    if isinstance(v, list): return [str(x).lower() for x in v]
    if v is None: return None
    if isinstance(v, bool): return v
    return [str(v).lower()] if isinstance(v, str) and "," not in v else str(v).lower()

def ensure_hosts():
    DOMAIN = dom()
    if not DOMAIN:
        log("WARNING: no public domain yet (Settings > Networking > Generate Domain), hosts skipped"); return
    existing = as_list(must("GET", "/api/hosts"), "hosts")
    wanted = {i[0] for i in INBOUNDS}
    for h in existing:  # clean CHOST hosts whose config no longer exists
        if str(h.get("inbound_tag") or "").startswith("CH-") and h.get("inbound_tag") not in wanted:
            req("DELETE", f"/api/host/{h['id']}")
    changed = 0
    for idx, (tag, proto, port, net, path, fp, name, grp) in enumerate(INBOUNDS):
        body = {"remark": name, "allowinsecure": False, "address": [DOMAIN], "inbound_tag": tag,
                "port": 443, "sni": [DOMAIN], "host": [DOMAIN], "path": path + (EARLY_DATA if net == "ws" else ""), "security": "tls",
                "alpn": ["http/1.1"], "fingerprint": fp, "priority": idx + 1, "is_disabled": False}
        mine = [h for h in existing if h.get("inbound_tag") == tag]
        if mine:
            cur = mine[0]
            if any(_norm(cur.get(k)) != _norm(v) for k, v in body.items()):
                must("PUT", f"/api/host/{cur['id']}", {**body, "id": cur["id"]}); changed += 1
            for extra in mine[1:]:  # remove auto-created duplicates
                req("DELETE", f"/api/host/{extra['id']}")
        else:
            must("POST", "/api/host/", body); changed += 1
    if changed or not QUIET.get("hosts"): log(f"{len(INBOUNDS)} hosts ready on", DOMAIN); QUIET["hosts"] = True

def ensure_settings():
    DOMAIN = dom()
    if not DOMAIN: return
    code, s = req("GET", "/api/settings")
    if code != 200 or not isinstance(s, dict) or "subscription" not in s:
        log("settings endpoint not as expected, skipped"); return
    sub = s["subscription"]
    want = {"url_prefix": f"https://{DOMAIN}", "profile_title": TITLE, "update_interval": 12}
    if all(sub.get(k) == v for k, v in want.items()):
        log("subscription settings ok"); return
    sub.update(want)
    code, res = req("PUT", "/api/settings", {"subscription": sub})
    log("subscription settings", "ok" if code in (200, 201) else f"skipped ({code})")

RESELLER_ROLE = "نماینده"

def ensure_reseller_role(gids):
    """Reseller role: manages only its own users, must use the ready-made templates."""
    own = {"scope": 1}
    role = {
        "name": RESELLER_ROLE,
        "permissions": {
            "users": {"create": own, "read": own, "read_simple": own, "update": own, "delete": own,
                      "reset_usage": own, "revoke_sub": own, "activate_next_plan": own},
            "templates": {"read": True, "read_simple": True},
            "groups": {"read_simple": True},
            "system": {"read": True},
            "settings": {"read_general": True},
        },
        "access": {"require_template": True, "allowed_group_ids": sorted(gids.values())},
        "disabled_when_limited": True,
    }
    for base in ("/api/admin-role",):
        code, res = req("GET", base + "s")
        if code != 200: continue
        roles = as_list(res, "roles")
        mine = [r for r in roles if r.get("name") == RESELLER_ROLE]
        if mine:
            acc = mine[0].get("access") or {}
            if (sorted(acc.get("allowed_group_ids") or []) != role["access"]["allowed_group_ids"]
                    or acc.get("require_template") is not True):
                req("PUT", f"{base}/{mine[0]['id']}", {"access": role["access"]})
            log("reseller role ready"); return
        code, res = req("POST", base, role)
        if code in (200, 201): log("reseller role created"); return
        log(f"reseller role failed {code}: {res}"); return
    log("reseller role endpoint not found, skipped")

def role_id_by_name(name):
    code, res = req("GET", "/api/admin-roles")
    for r in as_list(res, "roles") if code == 200 else []:
        if r.get("name") == name: return r["id"]
    return None

def ensure_demo_reseller():
    """A ready reseller account (like the reseller panels): 50 GB quota, own users only."""
    if os.getenv("DEMO_RESELLER", "on").lower() in ("off", "false", "0", "no"):
        return
    if os.path.exists(RESELLER_MARKER): return      # created once; deleting it in the panel is respected
    rid = role_id_by_name(RESELLER_ROLE)
    if not rid: log("demo reseller skipped (no role)"); return
    code, _ = req("POST", "/api/admin/token", {"username": RESELLER_USER, "password": RESELLER_PASS}, form=True)
    if code == 200: open(RESELLER_MARKER, "w").write("1"); return
    code, res = req("POST", "/api/admin", {"username": RESELLER_USER, "password": strong_tmp(),
                                           "role_id": rid, "data_limit": RESELLER_GB * GB,
                                           "profile_title": TITLE})
    if code in (200, 201):
        if write_password("user", RESELLER_USER, RESELLER_PASS):
            open(RESELLER_MARKER, "w").write("1"); log("demo reseller ready:", RESELLER_USER)
    elif code == 409:
        open(RESELLER_MARKER, "w").write("1")   # already exists with its own password
    else:
        log(f"demo reseller failed {code}: {res}")

def ensure_templates(gids):
    have = {t.get("name"): t for t in as_list(must("GET", "/api/user_templates"), "templates")}
    for name, gb, days, grp in TEMPLATES:
        body = {"name": name, "data_limit": gb * GB, "expire_duration": days * DAY, "group_ids": [gids[grp]],
                "status": "active", "data_limit_reset_strategy": "no_reset"}
        if name in have:
            if have[name].get("group_ids") != [gids[grp]]: req("PUT", f"/api/user_template/{have[name]['id']}", body)
        else:
            must("POST", "/api/user_template", body)
    log("user templates ready")

AUTO_GROUP = os.getenv("AUTO_GROUP", "on").lower() in ("on", "true", "1", "yes")

def users_page(offset, limit):
    for q in (f"/api/users?offset={offset}&limit={limit}&sort=-created_at", f"/api/users?offset={offset}&limit={limit}"):
        code, res = req("GET", q)
        if code == 401:
            login(); code, res = req("GET", q)
        if code == 200: return as_list(res, "users")
    return None

_attach_failed = {}

def attach_orphans(gids, full=False):
    """AUTO_GROUP (on by default): a user saved without any group would get an empty subscription,
    so CHOST gives them both groups (all 6 configs). Users that already have a group are never touched.
    Every 10 s the newest 200 users are checked; every few minutes all of them."""
    if not AUTO_GROUP: return
    both = sorted({gids.get("vip"), gids.get("game")} - {None})
    if not both: return
    offset = 0
    while offset < 20000:
        users = users_page(offset, 200)
        if users is None: return
        for u in users:
            if not isinstance(u, dict) or not u.get("username"): continue
            if "group_ids" not in u or u.get("group_ids"): continue      # unknown shape or has a group: never touch
            if time.time() - _attach_failed.get(u["username"], 0) < 600: continue   # failed a moment ago: try again later, no log spam
            c, r = req("PUT", f"/api/user/{urllib.parse.quote(str(u['username']))}", {"group_ids": both})
            if c == 200: log(f"{u['username']} had no group -> all CHOST configs")
            else: _attach_failed[u["username"]] = time.time(); log(f"attach {u['username']} failed {c}: {str(r)[:200]}")
        if not full or len(users) < 200: return
        offset += 200

def heal_node(state):
    """Self-healing: if the built-in core is not connected twice in a row, restart it."""
    code, res = req("GET", "/api/nodes")
    if code == 401: login(); code, res = req("GET", "/api/nodes")
    if code != 200: return
    for n in as_list(res, "nodes"):
        if n.get("name") != NODE_NAME: continue
        st = str(n.get("status") or "")
        if st in ("connected", "disabled"):
            state["bad"] = 0; return
        state["bad"] = state.get("bad", 0) + 1
        if state["bad"] >= 2:
            log(f"core status '{st}' -> auto-restart"); alert("core", "هسته‌ی کانفیگ‌ها قطع شده بود و خودکار دوباره راه‌اندازی شد.")
            c, _ = req("POST", f"/api/core/{n.get('core_config_id')}/restart")
            if c not in (200, 204):
                try: ensure_node(n.get("core_config_id"))
                except Exception as e: log("node reconnect failed:", e)
            state["bad"] = 0
        return

# ---------------- CHOST doctor: finds problems on its own, fixes them, tells the admins ----------------
SUB_TPL = "/code/custom_templates/subscription/index.html"
SAFE_SUB = """<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CHOST</title><style>body{margin:0;background:#070605;color:#efe3c2;font:15px/1.8 Tahoma,sans-serif;padding:24px}h1{color:#e9cf8a;font-size:22px;margin:0 0 12px}
textarea{width:100%;min-height:220px;box-sizing:border-box;background:#0d0b07;color:#efe3c2;border:1px solid #6b5420;border-radius:12px;padding:12px;direction:ltr;font:12px monospace}
.u{color:#a99d84;margin-bottom:16px}</style></head><body><h1>CHOST</h1>
<div class="u">{{ user.username }}</div>
{% set L = ((links.split() if links is string else (links|list)) if (links is defined and links) else []) %}
<textarea readonly onclick="this.select()">{{ L|join("\n") }}</textarea></body></html>
"""
_alerts = {}

def alert(key, text, every=3600):
    """short Persian message to the bot admins (only if the sales bot is set up), at most once an hour per problem"""
    now = time.time()
    if now - _alerts.get(key, 0) < every: return
    _alerts[key] = now
    try:
        c = _jload(BOT_CFG); tok = str(c.get("token") or "")
        if not tok: return
        for a in (c.get("admins") or [])[:10]:
            _tgcall(tok, "sendMessage", {"chat_id": a, "text": "◉ پزشک CHOST\n" + text})
    except Exception as e:
        log("doctor alert failed:", e)

def _raw_get(path, headers):
    r = urllib.request.Request(BASE + path, headers=headers)
    try:
        with urllib.request.urlopen(r, timeout=20) as resp: return resp.status, resp.read(400000).decode(errors="ignore")
    except urllib.error.HTTPError as e: return e.code, ""
    except Exception: return 0, ""

def doctor(gids, state):
    fixed = []
    d = dom()
    # 1) every CHOST config must exist, be on, and point to the current domain
    if d:
        code, res = req("GET", "/api/hosts")
        if code == 200:
            hs = as_list(res, "hosts"); mine = {}
            for h in hs:
                t = str(h.get("inbound_tag") or "")
                if t.startswith("CH-"): mine.setdefault(t, h)
            bad = 0
            for t, *_ in INBOUNDS:
                h = mine.get(t)
                raw = h.get("address") if h else None
                addr = [str(x).strip().lower() for x in (raw if isinstance(raw, list) else str(raw or "").split(","))]
                if not h or d not in addr or h.get("is_disabled"): bad += 1
            if bad:
                ensure_hosts(); fixed.append(f"{bad} کانفیگ خراب یا خاموش بود و درست شد")
    # 2) the subscription must answer: the page for people, the config list for the apps
    for u in (users_page(0, 5) or []):
        su = str((u or {}).get("subscription_url") or "")
        path = urllib.parse.urlparse(su).path if su else ""
        if not path.startswith("/"): continue
        c1, _ = _raw_get(path, {"Accept": "text/html", "User-Agent": "Mozilla/5.0"})
        c2, body = _raw_get(path, {"User-Agent": "v2rayNG/1.9.0", "Accept": "*/*"})
        # the apps get their configs but the page breaks -> the page template is the problem
        if c1 >= 500 and c2 == 200 and os.path.exists(SUB_TPL) and not state.get("safe_sub"):
            try:
                if not os.path.exists(SUB_TPL + ".chost"): os.replace(SUB_TPL, SUB_TPL + ".chost")
                with open(SUB_TPL, "w") as f: f.write(SAFE_SUB)
                state["safe_sub"] = True; fixed.append("صفحه‌ی ساب خطا می‌داد؛ نسخه‌ی ساده و مطمئن جایگزین شد تا لینک‌ها همیشه باز شوند")
            except Exception as e: log("doctor: sub page fallback failed:", e)
        if c2 == 200 and str(u.get("status") or "").lower().endswith("active") and len(body.strip()) < 16:
            if not u.get("group_ids") and "group_ids" in u: attach_orphans(gids)
            ensure_hosts(); fixed.append(f"ساب‌لینک {u.get('username')} خالی بود و کانفیگ‌ها دوباره ساخته شدند")
        break
    if fixed:
        log("doctor:", " | ".join(fixed))
        alert("fix:" + "|".join(sorted(fixed)), "\n".join("· " + x for x in fixed))

def watch(gids):
    log("watcher on: doctor, self-heal core, keep groups, hosts and the domain correct")
    state, i, down = {"domain": dom()}, 0, 0
    while True:
        def regroup():
            new = ensure_groups()
            if new: gids.update(new)
        def domain_check():
            d = dom()
            if d and d != state.get("domain"):
                log("domain is now", d, "-> updating configs and subscription links")
                ensure_hosts(); ensure_settings(); state["domain"] = d
        ok = True
        for job, every in ((domain_check, 1), (lambda: attach_orphans(gids), 1), (lambda: attach_orphans(gids, True), 30), (lambda: heal_node(state), 4),
                           (lambda: doctor(gids, state), 6), (ensure_hosts, 40), (regroup, 40), (ensure_settings, 40)):
            if i % every == 0:
                try: job()
                except Exception as e: ok = False; log("self-heal:", e)
        down = 0 if ok else down + 1
        if down == 30: alert("down", "پنل چند دقیقه است جواب نمی‌دهد؛ پزشک CHOST در حال راه‌اندازی دوباره‌ی آن است.")
        i += 1
        time.sleep(10)

# ---------------- owner key service (POST /chost/key, used by the "امنیت حساب" page) ----------------
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
_attempts = {}

class KeyHandler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, code, body):
        data = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store"); self.send_header("Content-Length", str(len(data)))
        self.end_headers(); self.wfile.write(data)
    def do_GET(self): self._send(405, {"detail": "use POST"})
    def do_POST(self):
        route = self.path.split("?")[0].rstrip("/")
        if route not in ("/chost/key", "/chost/password", "/chost/recover", "/chost/hello") and not route.startswith(("/chost/resellers", "/chost/bot")):
            return self._send(404, {"detail": "not found"})
        try: body = json.loads(self.rfile.read(min(int(self.headers.get("Content-Length") or 0), 4096)) or b"{}") or {}
        except Exception: body = {}
        if not isinstance(body, dict): body = {}
        if route == "/chost/hello": return hello(self)
        if route == "/chost/password": return change_password(self, body)
        if route == "/chost/recover": return recover_owner(self, body)
        if route.startswith("/chost/resellers"): return resellers_api(self, route, body)
        if route.startswith("/chost/bot"): return bot_api(self, route, body)
        token = None
        auth = self.headers.get("Authorization", "")
        if auth.lower().startswith("bearer ") and not body.get("username"):
            token = auth[7:].strip()                     # already logged in to the panel
        else:
            ip = (self.headers.get("X-Real-IP") or self.client_address[0]).strip()
            now = time.time(); hist = [t for t in _attempts.get(ip, []) if now - t < 600]
            if len(hist) >= 5: return self._send(429, {"detail": "تعداد تلاش‌ها زیاد بود. 10 دقیقه‌ی دیگر دوباره امتحان کنید"})
            u, p = str(body.get("username", ""))[:64], str(body.get("password", ""))[:128]
            if not u or not p: return self._send(401, {"detail": "نام کاربری و رمز مالک را وارد کنید"})
            code, res = req_anon("POST", "/api/admin/token", {"username": u, "password": p}, form=True)
            if code != 200:
                hist.append(now); _attempts[ip] = hist
                return self._send(401, {"detail": "نام کاربری یا رمز عبور اشتباه است"})
            token = res["access_token"]
        code, me = req_anon("GET", "/api/admin", token=token)
        if code != 200: return self._send(401, {"detail": "نشست شما منقضی شده است. دوباره وارد پنل شوید"})
        if not ((me or {}).get("role") or {}).get("is_owner"):
            return self._send(403, {"detail": "فقط مالک پنل می‌تواند کلید دریافت کند"})
        try: key = issue_key()
        except Exception as e:
            log("owner key failed:", e); return self._send(500, {"detail": "ساخت کلید انجام نشد"})
        log("owner key issued from the security page for", me.get("username"))
        self._send(200, {"key": key, "ttl": 300})

def recover_owner(handler, body):
    """login page "Owner access": CHOST owner key + new username/password for the panel owner (no login needed)"""
    ip = (handler.headers.get("X-Real-IP") or handler.client_address[0]).strip()
    now = time.time(); hist = [t for t in _attempts.get("rk:" + ip, []) if now - t < 600]
    if len(hist) >= 5: return handler._send(429, {"detail": "تعداد تلاش‌ها زیاد بود. 10 دقیقه‌ی دیگر دوباره امتحان کنید"})
    u = str(body.get("username", "")).strip()[:32]; pw = str(body.get("password", ""))[:128]
    if not _USER_RE.match(u): return handler._send(400, {"detail": "نام کاربری باید فقط شامل حروف انگلیسی، عدد و _ باشد (3 تا 32 کاراکتر)"})
    if len(pw) < 4: return handler._send(400, {"detail": "رمز جدید باید حداقل 4 کاراکتر باشد"})
    if not use_key(body.get("key")):
        hist.append(now); _attempts["rk:" + ip] = hist
        left = 5 - len(hist)
        return handler._send(401, {"detail": "کلید اشتباه است یا منقضی شده" + (f" ({left} تلاش باقی‌مانده)" if left > 0 else "")})
    if not write_password("owner", u, pw):
        return handler._send(500, {"detail": "ذخیره انجام نشد. یک کلید تازه دریافت کنید و دوباره امتحان کنید"})
    try: open(MARKER, "w").write(str(int(time.time())))
    except Exception: pass
    log("owner login reset with owner key:", u)
    handler._send(200, {"ok": True, "username": u})

def change_password(handler, body):
    """POST /chost/password {current, new} with the panel login token: change YOUR OWN password."""
    auth = handler.headers.get("Authorization", "")
    if not auth.lower().startswith("bearer "): return handler._send(401, {"detail": "نشست شما منقضی شده است. دوباره وارد پنل شوید"})
    code, me = req_anon("GET", "/api/admin", token=auth[7:].strip())
    if code != 200 or not isinstance(me, dict): return handler._send(401, {"detail": "نشست شما منقضی شده است. دوباره وارد پنل شوید"})
    user = me.get("username") or ""
    ip = (handler.headers.get("X-Real-IP") or handler.client_address[0]).strip()
    now = time.time(); hist = [t for t in _attempts.get(ip, []) if now - t < 600]
    if len(hist) >= 5: return handler._send(429, {"detail": "تعداد تلاش‌ها زیاد بود. 10 دقیقه‌ی دیگر دوباره امتحان کنید"})
    cur, new = str(body.get("current", ""))[:128], str(body.get("new", ""))[:128]
    if len(new) < 4: return handler._send(400, {"detail": "رمز جدید باید حداقل 4 کاراکتر باشد"})
    c, _ = req_anon("POST", "/api/admin/token", {"username": user, "password": cur}, form=True)
    if c != 200:
        hist.append(now); _attempts[ip] = hist
        return handler._send(401, {"detail": "رمز فعلی اشتباه است"})
    mode = "owner" if ((me.get("role") or {}).get("is_owner")) else "user"
    if not write_password(mode, user, new): return handler._send(500, {"detail": "ذخیره‌ی رمز انجام نشد. دوباره امتحان کنید"})
    log("password changed from Settings for", user)
    handler._send(200, {"ok": True})

# ---------------- reseller panels (sidebar "پنل نمایندگی", owner only) ----------------
import re as _re
_USER_RE = _re.compile(r"^[A-Za-z0-9_]{3,32}$")

def hello(handler):
    """the panel page tells us (as the logged-in owner) which address it is opened with:
    that address goes into every config and subscription link, even if the domain was added after the deploy"""
    tok = _owner_token(handler)
    if not tok: return
    host = (handler.headers.get("X-Forwarded-Host") or handler.headers.get("Host") or "").split(",")[0].strip().lower()
    host = host.rsplit(":", 1)[0] if host.count(":") == 1 else host
    if not _DOM_RE.match(host) or host.endswith(".internal") or host in ("localhost",):
        return handler._send(200, {"ok": True, "domain": dom()})
    try:
        old = open(SEEN_DOMAIN).read().strip().lower()
    except Exception: old = ""
    if host != old:
        tmp = SEEN_DOMAIN + ".tmp"
        with open(tmp, "w") as f: f.write(host)
        os.replace(tmp, SEEN_DOMAIN)
        log("panel opened on", host, "(saved for configs and links)")
    handler._send(200, {"ok": True, "domain": dom()})

def _owner_token(handler):
    """the caller must be logged in as the panel owner; returns their token or None (response already sent)"""
    auth = handler.headers.get("Authorization", "")
    if not auth.lower().startswith("bearer "):
        handler._send(401, {"detail": "نشست شما منقضی شده است. دوباره وارد پنل شوید"}); return None
    tok = auth[7:].strip()
    code, me = req_anon("GET", "/api/admin", token=tok)
    if code != 200 or not isinstance(me, dict):
        handler._send(401, {"detail": "نشست شما منقضی شده است. دوباره وارد پنل شوید"}); return None
    if not ((me.get("role") or {}).get("is_owner")):
        handler._send(403, {"detail": "فقط مالک پنل به این بخش دسترسی دارد"}); return None
    return tok

def _num(*vals):
    for v in vals:
        if isinstance(v, (int, float)) and not isinstance(v, bool): return int(v)
    return 0

def _reseller_view(a):
    return {"username": a.get("username"),
            "disabled": bool(a.get("is_disabled") or a.get("disabled")),
            "limit": _num(a.get("data_limit")),
            "used": _num(a.get("used_traffic"), a.get("users_usage"), a.get("lifetime_used_traffic")),
            "users": _num(a.get("total_users"), a.get("users_count")),
            "role": ((a.get("role") or {}).get("name") if isinstance(a.get("role"), dict) else a.get("role_name"))}

def _list_resellers(tok):
    code, res = req_anon("GET", "/api/admins?limit=500", token=tok)
    if code != 200: return None
    out = []
    for a in as_list(res, "admins"):
        if not isinstance(a, dict) or ((a.get("role") or {}).get("is_owner") if isinstance(a.get("role"), dict) else False):
            continue
        if a.get("username") in (USER, "chostowner"): continue
        out.append(_reseller_view(a))
    out.sort(key=lambda x: str(x["username"]).lower())
    return out

def _api_err(res, fallback):
    if isinstance(res, dict):
        d = res.get("detail")
        if isinstance(d, str): return d
        if isinstance(d, list) and d and isinstance(d[0], dict): return str(d[0].get("msg") or fallback)
    return fallback

def resellers_api(handler, route, body):
    tok = _owner_token(handler)
    if not tok: return
    if route == "/chost/resellers":
        lst = _list_resellers(tok)
        if lst is None: return handler._send(502, {"detail": "لیست نماینده‌ها از پنل دریافت نشد"})
        return handler._send(200, {"resellers": lst})
    if route == "/chost/resellers/create":
        u = str(body.get("username", "")).strip()[:32]; pw = str(body.get("password", ""))[:128]
        try: gb = float(body.get("gb") or 0)
        except (TypeError, ValueError): gb = -1
        if not _USER_RE.match(u): return handler._send(400, {"detail": "نام کاربری باید فقط شامل حروف انگلیسی، عدد و _ باشد (3 تا 32 کاراکتر)"})
        if len(pw) < 4: return handler._send(400, {"detail": "رمز عبور باید حداقل 4 کاراکتر باشد"})
        if gb < 0 or gb > 1000000: return handler._send(400, {"detail": "سهمیه را درست وارد کنید (0 یعنی نامحدود)"})
        rid = role_id_by_name(RESELLER_ROLE)
        if not rid:
            step("reseller role", ensure_reseller_role, ensure_groups()); rid = role_id_by_name(RESELLER_ROLE)
        if not rid: return handler._send(500, {"detail": "نقش نماینده پیدا نشد. سرویس را یک بار ری‌استارت کنید"})
        payload = {"username": u, "password": strong_tmp(), "role_id": rid, "profile_title": TITLE}
        if gb > 0: payload["data_limit"] = int(gb * GB)
        code, res = req_anon("POST", "/api/admin", payload, token=tok)
        if code == 409: return handler._send(409, {"detail": "این نام کاربری قبلاً ثبت شده است"})
        if code not in (200, 201): return handler._send(400, {"detail": _api_err(res, f"ساخت نماینده ممکن نشد ({code})")})
        if not write_password("user", u, pw):
            req_anon("DELETE", f"/api/admin/{urllib.parse.quote(u)}", token=tok)
            return handler._send(500, {"detail": "ذخیره‌ی رمز انجام نشد. دوباره امتحان کنید"})
        log("reseller panel created:", u, f"{gb:g} GB" if gb else "unlimited")
        return handler._send(200, {"ok": True})
    if route == "/chost/resellers/update":
        u = str(body.get("username", "")).strip()[:32]; act = str(body.get("action", ""))
        if not _USER_RE.match(u) or u in (USER, "chostowner"): return handler._send(400, {"detail": "نماینده پیدا نشد"})
        cur = next((r for r in (_list_resellers(tok) or []) if r["username"] == u), None)
        if not cur: return handler._send(404, {"detail": "نماینده پیدا نشد"})
        path = f"/api/admin/{urllib.parse.quote(u)}"
        if act == "password":
            pw = str(body.get("password", ""))[:128]
            if len(pw) < 4: return handler._send(400, {"detail": "رمز عبور باید حداقل 4 کاراکتر باشد"})
            if not write_password("user", u, pw): return handler._send(500, {"detail": "ذخیره‌ی رمز انجام نشد"})
            log("reseller password changed:", u); return handler._send(200, {"ok": True})
        if act == "delete":
            code, res = req_anon("DELETE", path, token=tok)
            if code not in (200, 204): return handler._send(400, {"detail": _api_err(res, f"حذف ممکن نشد ({code})")})
            log("reseller panel deleted:", u); return handler._send(200, {"ok": True})
        if act in ("add_gb", "set_gb"):
            try: gb = float(body.get("gb") or 0)
            except (TypeError, ValueError): gb = -1
            if gb < 0 or gb > 1000000: return handler._send(400, {"detail": "مقدار حجم را درست وارد کنید"})
            new = int(gb * GB) + (cur["limit"] if act == "add_gb" else 0)
            if act == "add_gb" and not cur["limit"]: return handler._send(400, {"detail": "سهمیه‌ی این نماینده نامحدود است"})
            patch = {"data_limit": new if new > 0 else None}
        elif act in ("disable", "enable"):
            patch = {"is_disabled": act == "disable"}
        else:
            return handler._send(400, {"detail": "دستور نامعتبر"})
        code, res = req_anon("PUT", path, patch, token=tok)
        if code == 422:   # this PasarGuard version wants the full admin object: merge the change into it
            c2, allr = req_anon("GET", "/api/admins?limit=500", token=tok)
            raw = next((x for x in as_list(allr, "admins") if isinstance(x, dict) and x.get("username") == u), None) if c2 == 200 else None
            if raw:
                keep = ("role_id", "data_limit", "is_disabled", "telegram_id", "discord_webhook", "sub_domain",
                        "profile_title", "support_url", "notification_enable", "discord_id", "note")
                full = {k: raw[k] for k in keep if k in raw}
                if "role_id" not in full and isinstance(raw.get("role"), dict) and raw["role"].get("id"): full["role_id"] = raw["role"]["id"]
                full.update(patch)
                code, res = req_anon("PUT", path, full, token=tok)
        if code not in (200, 201): return handler._send(400, {"detail": _api_err(res, f"ذخیره ممکن نشد ({code})")})
        log("reseller panel updated:", u, act); return handler._send(200, {"ok": True})
    handler._send(404, {"detail": "not found"})

# ---------------- sales bot settings (sidebar page "ربات تلگرام", owner only) ----------------
BOT_CFG = f"{DATA}/chost-bot.json"
BOT_STATUS = f"{DATA}/chost-bot.status.json"

def _jload(p):
    try:
        with open(p) as f: d = json.load(f)
        return d if isinstance(d, dict) else {}
    except Exception: return {}

def _tgcall(token, method, payload=None):
    r = urllib.request.Request(f"https://api.telegram.org/bot{token}/{method}", data=json.dumps(payload or {}).encode(),
                               headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=15) as resp: return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try: return json.loads(e.read().decode())
        except Exception: return {"ok": False, "description": f"HTTP {e.code}"}
    except Exception as e: return {"ok": False, "description": str(e)}

def _mask(t): return (t[:6] + "…" + t[-4:]) if len(t) > 12 else ""

def _bot_view():
    c, st = _jload(BOT_CFG), _jload(BOT_STATUS)
    fresh = st.get("ts", 0) > time.time() - 120
    return {"enabled": bool(c.get("enabled")), "has_token": bool(c.get("token")), "token_mask": _mask(str(c.get("token") or "")),
            "admins": c.get("admins") or [], "running": bool(st.get("running")) and fresh and bool(c.get("enabled")),
            "username": st.get("username") or "", "error": st.get("error") or "", "stats": st.get("stats") or {}}

def bot_api(handler, route, body):
    tok = _owner_token(handler)
    if not tok: return
    if route == "/chost/bot":
        return handler._send(200, _bot_view())
    cur = _jload(BOT_CFG)
    if route == "/chost/bot/save":
        new_tok = str(body.get("token") or "").strip()
        if not new_tok or "…" in new_tok: new_tok = str(cur.get("token") or "")
        raw = str(body.get("admins") if not isinstance(body.get("admins"), list) else ",".join(map(str, body.get("admins"))))
        raw = raw.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))
        ids = [p for p in _re.split(r"[\s,،]+", raw) if p]
        if any(not _re.match(r"^-?\d{4,20}$", p) for p in ids):
            return handler._send(400, {"detail": "آیدی عددی مدیر باید فقط عدد باشد (چند آیدی را با کاما جدا کنید)"})
        enabled = bool(body.get("enabled"))
        if enabled and not new_tok: return handler._send(400, {"detail": "توکن ربات را وارد کنید"})
        if enabled and not ids: return handler._send(400, {"detail": "حداقل یک آیدی عددی مدیر وارد کنید"})
        if new_tok and not _re.match(r"^\d{5,15}:[A-Za-z0-9_-]{30,60}$", new_tok):
            return handler._send(400, {"detail": "توکن معتبر نیست. توکن را از @BotFather کپی کنید"})
        if new_tok and new_tok != cur.get("token"):
            me = _tgcall(new_tok, "getMe")
            if not me.get("ok"): return handler._send(400, {"detail": "تلگرام این توکن را تأیید نکرد: " + str(me.get("description", ""))[:120]})
        data = {"enabled": enabled, "token": new_tok, "admins": ids, "updated": int(time.time())}
        tmp = BOT_CFG + ".tmp"
        with open(tmp, "w") as f: json.dump(data, f)
        os.replace(tmp, BOT_CFG)
        log("sales bot settings saved:", "on" if enabled else "off", f"{len(ids)} admin(s)")
        return handler._send(200, _bot_view())
    if route == "/chost/bot/test":
        t = str(cur.get("token") or "")
        if not t: return handler._send(400, {"detail": "ابتدا توکن ربات را ذخیره کنید"})
        ok = 0; last = ""
        for a in cur.get("admins") or []:
            r = _tgcall(t, "sendMessage", {"chat_id": int(a), "text": "✓ ربات فروش CHOST به پنل وصل است.\nبرای مدیریت ربات، دستور /admin را بفرستید.",})
            if r.get("ok"): ok += 1
            else: last = str(r.get("description", ""))
        if not ok:
            return handler._send(400, {"detail": "پیام ارسال نشد. ابتدا ربات را در تلگرام Start کنید و دوباره امتحان کنید." + (f" ({last[:80]})" if last else "")})
        return handler._send(200, {"ok": True, "sent": ok})
    handler._send(404, {"detail": "not found"})

def req_anon(method, path, body=None, form=False, token=None):
    return req(method, path, body, form=form, token=token)  # thread-safe: never touches the global token

def start_key_service():
    srv = ThreadingHTTPServer(("127.0.0.1", 8100), KeyHandler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    log("owner key + password change ready (sidebar page: امنیت حساب)")

def step(name, fn, *a):
    try: return fn(*a)
    except Exception as e: log(f"{name} failed: {e}")

def main():
    wait_panel(); login(); print_owner_key()
    step("key service", start_key_service)
    core_id = ensure_core()
    time.sleep(2)
    step("node", ensure_node, core_id)
    gid = None
    for _ in range(10):  # inbounds appear after the core is saved
        gid = step("groups", ensure_groups)
        if gid: break
        time.sleep(3)
    if not gid: raise RuntimeError("groups could not be created")
    step("hosts", ensure_hosts)
    step("settings", ensure_settings)
    step("templates", ensure_templates, gid)
    step("reseller role", ensure_reseller_role, gid)
    step("demo reseller", ensure_demo_reseller)
    log("DONE ->", f"https://{dom()}/dashboard/" if dom() else "generate a Railway domain, then open the panel once")
    watch(gid)

if __name__ == "__main__":
    try: main()
    except Exception as e: log("FATAL", e); sys.exit(1)
