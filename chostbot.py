"""CHOST sales bot: a Telegram bot that sells subscriptions from this panel.
Token and admin numeric IDs come from the panel (sidebar page "ربات تلگرام").
Plans, prices, card number, texts and everything else are managed by the admins inside the bot."""
import datetime, html, json, os, sqlite3, sys, threading, time, urllib.error, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bootstrap as B   # panel API helpers: owner token, request helper, group names

DATA = B.DATA
CFG_FILE = f"{DATA}/chost-bot.json"
STATUS_FILE = f"{DATA}/chost-bot.status.json"
DB_FILE = f"{DATA}/chost-bot.db"
GB = B.GB
GROUPS = {"vip": B.VIP_GROUP, "game": B.GAME_GROUP}
GROUP_FA = {"vip": "VIP · دانلود و استریم", "game": "GAME · گیم و تماس"}
CFG = {}

def log(*a): print("[bot]", *a, flush=True)
def esc(s): return html.escape(str(s if s is not None else ""), quote=False)
def money(n):
    try: return f"{int(n):,} تومان"
    except Exception: return f"{n} تومان"
def gbtxt(gb):
    try: gb = float(gb or 0)
    except Exception: gb = 0
    return "نامحدود" if gb <= 0 else (f"{gb:.1f}".rstrip("0").rstrip(".") + " GB")
def bytes_txt(b): return "نامحدود" if not b else gbtxt(b / GB)
DIG = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
def to_num(s, allow_float=False):
    t = str(s or "").strip().translate(DIG).replace(",", "").replace("،", "").replace(" ", "")
    try: v = float(t)
    except ValueError: return None
    if v != v or v < 0: return None
    return v if allow_float else int(v)
def card_fmt(c):
    d = "".join(ch for ch in str(c or "").translate(DIG) if ch.isdigit())
    return "-".join(d[i:i + 4] for i in range(0, len(d), 4)) if d else ""

# ---------------- config / status files ----------------
def load_cfg():
    try:
        with open(CFG_FILE) as f: c = json.load(f)
        return c if isinstance(c, dict) else {}
    except Exception: return {}

def write_status(**kw):
    try:
        cur = {}
        try:
            with open(STATUS_FILE) as f: cur = json.load(f)
        except Exception: pass
        cur.update(kw); cur["ts"] = int(time.time())
        tmp = STATUS_FILE + ".tmp"
        with open(tmp, "w") as f: json.dump(cur, f, ensure_ascii=False)
        os.replace(tmp, STATUS_FILE)
    except Exception as e: log("status write failed:", e)

# ---------------- database (sqlite on the volume) ----------------
_dbl = threading.RLock()
def _conn():
    c = sqlite3.connect(DB_FILE, timeout=30, isolation_level=None)
    c.row_factory = sqlite3.Row
    return c
def q(sql, args=(), one=False):
    with _dbl:
        c = _conn()
        try: rows = c.execute(sql, args).fetchall()
        finally: c.close()
    return (rows[0] if rows else None) if one else rows
def x(sql, args=()):
    with _dbl:
        c = _conn()
        try: cur = c.execute(sql, args); return cur.lastrowid, cur.rowcount
        finally: c.close()
def kv_get(k, d=""):
    r = q("SELECT v FROM kv WHERE k=?", (k,), one=True)
    return r["v"] if r else d
def kv_set(k, v): x("INSERT INTO kv(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", (k, str(v)))

def init_db():
    with _dbl:
        c = _conn()
        try:
            c.executescript("""
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS kv(k TEXT PRIMARY KEY, v TEXT);
            CREATE TABLE IF NOT EXISTS plans(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, grp TEXT, gb REAL, days INTEGER,
                price INTEGER, active INTEGER DEFAULT 1, sort INTEGER DEFAULT 0);
            CREATE TABLE IF NOT EXISTS users(tg INTEGER PRIMARY KEY, name TEXT, uname TEXT, joined INTEGER, blocked INTEGER DEFAULT 0);
            CREATE TABLE IF NOT EXISTS subs(id INTEGER PRIMARY KEY AUTOINCREMENT, tg INTEGER, username TEXT UNIQUE, plan_id INTEGER, created INTEGER);
            CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT, tg INTEGER, plan_id INTEGER, kind TEXT, target TEXT,
                amount INTEGER, status TEXT, receipt TEXT, created INTEGER, updated INTEGER, result TEXT);
            CREATE TABLE IF NOT EXISTS state(tg INTEGER PRIMARY KEY, st TEXT, data TEXT);
            CREATE TABLE IF NOT EXISTS codes(code TEXT PRIMARY KEY, pct INTEGER, max_uses INTEGER DEFAULT 0, used INTEGER DEFAULT 0, active INTEGER DEFAULT 1, created INTEGER);
            CREATE TABLE IF NOT EXISTS code_uses(code TEXT, tg INTEGER, oid INTEGER, PRIMARY KEY(code, tg));
            """)
            cols = [r[1] for r in c.execute("PRAGMA table_info(orders)").fetchall()]
            if "code" not in cols: c.execute("ALTER TABLE orders ADD COLUMN code TEXT")
            if "price" not in cols: c.execute("ALTER TABLE orders ADD COLUMN price INTEGER")
            if "paid_by" not in cols: c.execute("ALTER TABLE orders ADD COLUMN paid_by TEXT")
            ucols = [r[1] for r in c.execute("PRAGMA table_info(users)").fetchall()]
            if "balance" not in ucols: c.execute("ALTER TABLE users ADD COLUMN balance INTEGER DEFAULT 0")
            if "banned" not in ucols: c.execute("ALTER TABLE users ADD COLUMN banned INTEGER DEFAULT 0")
            if "ref" not in ucols: c.execute("ALTER TABLE users ADD COLUMN ref INTEGER")
            c.execute("CREATE TABLE IF NOT EXISTS wallet_tx(id INTEGER PRIMARY KEY AUTOINCREMENT, tg INTEGER, delta INTEGER, reason TEXT, by INTEGER, created INTEGER)")
        finally: c.close()
    if not kv_get("seeded"):
        for i, (n, g, gb, d, p) in enumerate([("VIP 30 گیگ · یک ماهه", "vip", 30, 30, 120000), ("VIP 50 گیگ · یک ماهه", "vip", 50, 30, 180000),
                                               ("VIP 100 گیگ · یک ماهه", "vip", 100, 30, 300000), ("GAME 50 گیگ · یک ماهه", "game", 50, 30, 200000)]):
            x("INSERT INTO plans(name,grp,gb,days,price,sort) VALUES(?,?,?,?,?,?)", (n, g, gb, d, p, i))
        kv_set("seeded", "1")

def set_state(tg_id, st, data=None): x("INSERT INTO state(tg,st,data) VALUES(?,?,?) ON CONFLICT(tg) DO UPDATE SET st=excluded.st,data=excluded.data", (tg_id, st, json.dumps(data or {})))
def get_state(tg_id):
    r = q("SELECT st,data FROM state WHERE tg=?", (tg_id,), one=True)
    try: return (r["st"], json.loads(r["data"] or "{}")) if r else ("", {})
    except Exception: return (r["st"], {}) if r else ("", {})
def clear_state(tg_id): x("DELETE FROM state WHERE tg=?", (tg_id,))

# ---------------- telegram ----------------
TOKEN = ""
import http.client
_tl = threading.local()
def _tg_conn(timeout):
    c = getattr(_tl, "c", None)
    if c is None:
        c = http.client.HTTPSConnection("api.telegram.org", timeout=timeout); _tl.c = c
    c.timeout = timeout
    if c.sock: c.sock.settimeout(timeout)
    return c
def _tg_drop():
    c = getattr(_tl, "c", None); _tl.c = None
    if c:
        try: c.close()
        except Exception: pass
def tg(method, payload=None, timeout=35):
    """Telegram Bot API call over a kept-alive HTTPS connection (one per thread): no new TLS handshake per message"""
    body = json.dumps(payload or {}).encode()
    for attempt in range(3):
        try:
            c = _tg_conn(timeout)
            c.request("POST", f"/bot{TOKEN}/{method}", body, {"Content-Type": "application/json", "Connection": "keep-alive"})
            resp = c.getresponse(); raw = resp.read()
            try: j = json.loads(raw.decode())
            except Exception: j = {"ok": False, "error_code": resp.status, "description": f"HTTP {resp.status}"}
            if resp.getheader("Connection", "").lower() == "close": _tg_drop()
            if not j.get("ok") and j.get("error_code") == 429 and attempt < 2:     # flood control: wait as told, then retry
                time.sleep(min(10, int((j.get("parameters") or {}).get("retry_after", 1)) + 0.2)); continue
            return j
        except (http.client.RemoteDisconnected, BrokenPipeError, ConnectionResetError, http.client.CannotSendRequest, http.client.ResponseNotReady) as e:
            _tg_drop()
            if attempt == 0: continue          # idle keep-alive connection was closed by Telegram: reconnect once
            return {"ok": False, "description": str(e) or e.__class__.__name__}
        except Exception as e:
            _tg_drop(); return {"ok": False, "description": str(e) or e.__class__.__name__}
    return {"ok": False, "description": "Too Many Requests"}

STYLES = {"g": "success", "r": "danger", "b": "primary"}
def _btn(b):
    """(text, action[, color]) -> Telegram button. action: callback data, https:// link, or "copy:<text>".
    color: g = green, r = red, b = blue (Telegram colored buttons; older apps simply show them uncolored)."""
    t, d = str(b[0])[:64], str(b[1])
    if d.startswith("copy:"): o = {"text": t, "copy_text": {"text": d[5:][:256]}}
    elif d.startswith("http"): o = {"text": t, "url": d}
    else: o = {"text": t, "callback_data": d.encode()[:64].decode(errors="ignore")}
    if len(b) > 2 and b[2] in STYLES: o["style"] = STYLES[b[2]]
    return o
def kb(rows): return {"inline_keyboard": [[_btn(b) for b in row] for row in rows if row]}
import re as _re
def _plain(t): return html.unescape(_re.sub(r"<[^>]+>", "", t))
def _bad_html(r): return "parse entities" in str(r.get("description", "")) or "unsupported start tag" in str(r.get("description", ""))
def send(chat, text, rows=None):
    p = {"chat_id": chat, "text": text[:4096], "parse_mode": "HTML", "disable_web_page_preview": True}
    if rows is not None: p["reply_markup"] = kb(rows)
    r = tg("sendMessage", p)
    if not r.get("ok") and _bad_html(r):   # admin text with broken HTML: send it as plain text instead of failing
        p.pop("parse_mode"); p["text"] = _plain(text)[:4096]; r = tg("sendMessage", p)
    return r
def edit(chat, mid, text, rows=None):
    if not mid: return send(chat, text, rows)
    p = {"chat_id": chat, "message_id": mid, "text": text[:4096], "parse_mode": "HTML", "disable_web_page_preview": True}
    if rows is not None: p["reply_markup"] = kb(rows)
    r = tg("editMessageText", p)
    if r.get("ok") or "not modified" in str(r.get("description", "")): return r
    if _bad_html(r):
        p.pop("parse_mode"); p["text"] = _plain(text)[:4096]; r = tg("editMessageText", p)
        if r.get("ok"): return r
    return send(chat, text, rows)
def answer(cid, text="", alert=False): tg("answerCallbackQuery", {"callback_query_id": cid, "text": text[:190], "show_alert": alert}, timeout=10)

# ---------------- panel API ----------------
_tok = {"t": None}
def papi(method, path, body=None):
    if not _tok["t"]: _tok["t"] = B.owner_token()
    code, res = B.req(method, path, body, token=_tok["t"])
    if code == 401:
        _tok["t"] = B.owner_token(); code, res = B.req(method, path, body, token=_tok["t"])
    return code, res

def group_id(key):
    code, res = papi("GET", "/api/groups")
    for g in (B.as_list(res, "groups") if code == 200 else []):
        if g.get("name") == GROUPS.get(key): return g["id"]
    return None

def domain():
    return B.dom()

def sub_link(u):
    s = str((u or {}).get("subscription_url") or "")
    if s.startswith("/") and domain(): s = f"https://{domain()}{s}"
    return s

def iso(ts): return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def parse_exp(v):
    if not v: return 0
    if isinstance(v, (int, float)): return int(v)
    try:
        d = datetime.datetime.fromisoformat(str(v).replace("Z", "+00:00"))
        if d.tzinfo is None: d = d.replace(tzinfo=datetime.timezone.utc)
        return int(d.timestamp())
    except Exception: return 0

def _expire_variants(ts):
    """PasarGuard versions accept the expire time as ISO date or as a unix timestamp: try both"""
    return [iso(ts), ts] if ts else [None, 0]

def _err(res):
    if isinstance(res, dict):
        d = res.get("detail")
        if isinstance(d, str): return d
        if isinstance(d, list) and d and isinstance(d[0], dict): return str(d[0].get("msg", ""))
    return str(res)[:150]

def create_user(username, p):
    gid = group_id(p["grp"])
    if not gid: raise RuntimeError("گروه کانفیگ در پنل پیدا نشد")
    secs = int(p.get("secs") or 0) or (int(p["days"]) * 86400 if p["days"] else 0)
    ts = int(time.time() + secs) if secs else 0
    body = {"username": username, "group_ids": [gid], "status": "active", "data_limit_reset_strategy": "no_reset",
            "data_limit": int(float(p["gb"]) * GB) if p["gb"] else 0, "note": p.get("note") or "CHOST bot"}
    code, res = 0, None
    for e in _expire_variants(ts):
        code, res = papi("POST", "/api/user", dict(body, expire=e))
        if code in (200, 201): return res if isinstance(res, dict) else (get_user(username) or {})
        if code == 409: raise RuntimeError("نام کاربری تکراری است")
        if code != 422: break
    raise RuntimeError(f"ساخت کاربر در پنل ممکن نشد ({code}): {_err(res)}")

def get_user(username):
    code, res = papi("GET", f"/api/user/{urllib.parse.quote(username)}")
    return res if code == 200 and isinstance(res, dict) else None

def renew_user(username, p):
    u = get_user(username)
    if not u: raise RuntimeError("این اشتراک در پنل پیدا نشد")
    gid = group_id(p["grp"])
    ts = int(max(time.time(), parse_exp(u.get("expire"))) + int(p["days"]) * 86400) if p["days"] else 0
    body = {"status": "active", "data_limit": int(float(p["gb"]) * GB) if p["gb"] else 0}
    if gid: body["group_ids"] = [gid]
    code, res = 0, None
    for e in _expire_variants(ts):
        code, res = papi("PUT", f"/api/user/{urllib.parse.quote(username)}", dict(body, expire=e))
        if code in (200, 201):
            papi("POST", f"/api/user/{urllib.parse.quote(username)}/reset")   # fresh quota for the new period, only after the renewal is saved
            return get_user(username) or (res if isinstance(res, dict) else {})
        if code != 422: break
    raise RuntimeError(f"تمدید در پنل ممکن نشد ({code}): {_err(res)}")

# ---------------- helpers ----------------
def admins():
    out = []
    for a in CFG.get("admins", []):
        try: out.append(int(str(a).strip()))
        except ValueError: pass
    return out
def is_admin(t): return t in admins()
def shop_open(): return kv_get("shop", "1") == "1"
def plans(active_only=True): return q("SELECT * FROM plans " + ("WHERE active=1 " if active_only else "") + "ORDER BY grp DESC, sort, price")
def plan(pid):
    r = q("SELECT * FROM plans WHERE id=?", (pid,), one=True)
    return dict(r) if r else None
def days_txt(d): return f"{int(d)} روز" if d else "بدون محدودیت زمانی"
def plan_line(p): return f"<b>{esc(p['name'])}</b>\n{gbtxt(p['gb'])} · {days_txt(p['days'])} · {GROUP_FA.get(p['grp'], '')}\nقیمت: <b>{money(p['price'])}</b>"

def notify_admins(text, rows=None, photo=None):
    for a in admins():
        if photo:
            p = {"chat_id": a, "photo": photo, "caption": text[:1024], "parse_mode": "HTML"}
            if rows: p["reply_markup"] = kb(rows)
            r = tg("sendPhoto", p)
            if not r.get("ok"): send(a, text, rows)
        else: send(a, text, rows)

def channel_ref():
    ch = kv_get("channel", "").strip()
    if not ch: return ""
    if ch.startswith("https://t.me/"): ch = ch[len("https://t.me/"):]
    return ch if ch.startswith("@") or ch.lstrip("-").isdigit() else "@" + ch

def join_needed(t):
    ch = channel_ref()
    if not ch or kv_get("force_join", "0") != "1" or is_admin(t): return None
    r = tg("getChatMember", {"chat_id": ch, "user_id": t}, timeout=10)
    if not r.get("ok"): return None   # bot is not an admin of the channel: never lock users out
    if (r.get("result") or {}).get("status") in ("member", "administrator", "creator"): return None
    return "https://t.me/" + ch.lstrip("@") if ch.startswith("@") else None

def home_rows(t):
    rows = [[("◈ خرید اشتراک", "buy", "b")], [("◇ اشتراک‌های من", "my"), ("↻ تمدید اشتراک", "renew", "g")]]
    if wallet_on(): rows.append([(f"▣ کیف پول · {money(bal(t))}", "w")] + ([("✦ دعوت دوستان", "ref")] if ref_on() else []))
    rows.append([("◎ آموزش اتصال", "help"), ("✆ پشتیبانی", "support")])
    if trial_on() and not kv_get(f"trial:{t}"): rows.insert(1, [("◌ اکانت تست رایگان", "trial", "g")])
    if is_admin(t): rows.append([("◉ مدیریت ربات", "adm")])
    return rows

# ---------------- free test account ----------------
def trial_on(): return kv_get("trial_on", "1") == "1"
def trial_cfg():
    return {"gb": to_num(kv_get("trial_gb", "1"), True) or 1, "hours": to_num(kv_get("trial_hours", "24")) or 24,
            "grp": kv_get("trial_grp", "vip") if kv_get("trial_grp", "vip") in GROUPS else "vip"}

def take_trial(chat, mid, frm):
    if not trial_on(): return edit(chat, mid, "اکانت تست در حال حاضر فعال نیست.", home_rows(chat))
    if kv_get(f"trial:{chat}"): return edit(chat, mid, "قبلاً اکانت تست گرفته‌ای. برای ادامه، یک اشتراک بخر.", [[("◈ خرید اشتراک", "buy", "b")], [("بازگشت", "home")]])
    kv_set(f"trial:{chat}", "pending")     # reserve first: double taps never create two test accounts
    c = trial_cfg(); uname = f"ch{chat}_t"
    try:
        if get_user(uname): uname = new_username(chat)
        u = create_user(uname, {"grp": c["grp"], "gb": c["gb"], "days": 0, "secs": int(c["hours"]) * 3600, "note": "CHOST test"})
    except Exception as e:
        x("DELETE FROM kv WHERE k=?", (f"trial:{chat}",)); log("trial failed", chat, e)
        return edit(chat, mid, "ساخت اکانت تست الان ممکن نشد. چند دقیقه دیگر دوباره امتحان کن.", home_rows(chat))
    kv_set(f"trial:{chat}", uname)
    x("INSERT OR IGNORE INTO subs(tg,username,plan_id,created) VALUES(?,?,?,?)", (chat, uname, None, int(time.time())))
    u = get_user(uname) or u; link = sub_link(u)
    rows = [[("صفحه‌ی اشتراک و افزودن خودکار", link, "b")], [("⧉ کپی لینک اشتراک", "copy:" + link, "g")]] if link.startswith("http") else []
    rows.append([("◈ خرید اشتراک", "buy"), ("◎ آموزش اتصال", "help")])
    who = esc(frm.get("first_name", "")) + (f" · @{esc(frm['username'])}" if frm.get("username") else "")
    notify_admins(f"◌ اکانت تست ساخته شد\nکاربر: {who}\nآیدی: <code>{chat}</code>\nنام کاربری: <code>{esc(uname)}</code>")
    return edit(chat, mid, f"<b>اکانت تست رایگانت آماده است</b>\n{gbtxt(c['gb'])} · {int(c['hours'])} ساعت\n\n{sub_card(uname, u)}\n\n<i>از سرعت لذت ببر. برای ادامه، از «خرید اشتراک» پلن مناسبت را بگیر.</i>", rows)

def home_text(name):
    t = kv_get("welcome", "") or "به ربات رسمی <b>CHOST</b> خوش آمدی.\n\nاشتراک پرسرعت بخر، تمدید کن و وضعیت اشتراکت را هر لحظه ببین."
    t = t.replace("{name}", esc(name))
    return f"سلام <b>{esc(name)}</b>\n\n{t}" if "{name}" not in (kv_get("welcome", "") or "") else t

# ---------------- user side ----------------
def show_home(chat, name, mid=None):
    clear_state(chat)
    return edit(chat, mid, home_text(name), home_rows(chat))

def show_plans(chat, mid=None, target=None):
    if not shop_open() and not is_admin(chat):
        return edit(chat, mid, "فروش در حال حاضر بسته است. کمی بعد دوباره سر بزن.", [[("بازگشت", "home")]])
    ps = plans()
    if not ps: return edit(chat, mid, "فعلاً پلنی برای فروش وجود ندارد.", [[("بازگشت", "home")]])
    head = (f"↻ <b>تمدید</b> <code>{esc(target)}</code>\nپلن تمدید را انتخاب کن:" if target else "◈ <b>خرید اشتراک</b>\nپلن مورد نظرت را انتخاب کن:")
    body = "\n\n".join(plan_line(p) for p in ps)
    rows = [[(f"{p['name']} · {money(p['price'])}", f"pl:{p['id']}:{target or ''}", "b")] for p in ps]
    rows.append([("بازگشت", "renew" if target else "home")])
    return edit(chat, mid, head + "\n\n" + body, rows)

def checkout(chat, mid, pid, target):
    p = plan(pid)
    if not p or not p["active"]: return edit(chat, mid, "این پلن دیگر موجود نیست.", [[("بازگشت", "buy")]])
    if not shop_open() and not is_admin(chat): return edit(chat, mid, "فروش در حال حاضر بسته است.", [[("بازگشت", "home")]])
    if target and not q("SELECT 1 FROM subs WHERE tg=? AND username=?", (chat, target), one=True):
        return edit(chat, mid, "این اشتراک متعلق به تو نیست.", [[("بازگشت", "home")]])
    card = card_fmt(kv_get("card", ""))
    if not card:
        notify_admins("یک کاربر قصد خرید داشت اما <b>شماره کارت</b> تنظیم نشده است.\nمدیریت ربات ← اطلاعات پرداخت")
        return edit(chat, mid, "پرداخت موقتاً در دسترس نیست. چند دقیقه دیگر دوباره امتحان کن.", [[("بازگشت", "home")]])
    now = int(time.time())
    x("UPDATE orders SET status='cancel',updated=? WHERE tg=? AND status='wait'", (now, chat))
    oid, _ = x("INSERT INTO orders(tg,plan_id,kind,target,amount,price,status,created,updated) VALUES(?,?,?,?,?,?,?,?,?)",
               (chat, pid, "renew" if target else "new", target or None, int(p["price"]), int(p["price"]), "wait", now, now))
    set_state(chat, "receipt", {"order": oid})
    return invoice(chat, mid, oid)

def invoice(chat, mid, oid):
    o = q("SELECT * FROM orders WHERE id=?", (oid,), one=True); p = plan(o["plan_id"]) if o and o["plan_id"] else None
    if not o or o["status"] != "wait" or (o["kind"] != "topup" and not p): return edit(chat, mid, "این سفارش دیگر فعال نیست.", home_rows(chat))
    card = card_fmt(kv_get("card", "")); holder, bank = kv_get("holder", ""), kv_get("bank", "")
    price = int(o["price"] or p["price"]); amount = int(o["amount"])
    off = (f"\nقیمت: <s>{money(price)}</s>\nکد تخفیف <code>{esc(o['code'])}</code>: {money(price - amount)} تخفیف\n" if o["code"] else "")
    what = plan_line(p) if p else f"<b>شارژ کیف پول</b>\nمبلغ شارژ: {money(o['amount'])}"
    text = (f"<b>فاکتور سفارش #{oid}</b>\n\n{what}\n" + (f"\nتمدید برای: <code>{esc(o['target'])}</code>\n" if o["target"] else "") + off +
            f"\n<b>مبلغ قابل پرداخت:</b> {money(amount)}\n\n<b>شماره کارت:</b>\n<code>{card}</code>\n" +
            (f"به نام: <b>{esc(holder)}</b>\n" if holder else "") + (f"بانک: {esc(bank)}\n" if bank else "") +
            "\nمبلغ را دقیق واریز کن و <b>عکس رسید</b> را همین‌جا بفرست. بعد از تأیید، اشتراک خودکار برایت ارسال می‌شود.")
    rows = []
    if o["kind"] != "topup" and wallet_on():
        b = bal(chat)
        if b >= amount: rows.append([(f"▣ پرداخت فوری از کیف پول · موجودی {money(b)}", f"wp:{oid}", "g")])
    rows.append([("⧉ کپی شماره کارت", "copy:" + card.replace("-", ""), "b"), ("⧉ کپی مبلغ", "copy:" + str(amount))])
    if o["kind"] != "topup" and not o["code"] and q("SELECT 1 FROM codes WHERE active=1 LIMIT 1", one=True): rows.append([("◍ کد تخفیف دارم", f"cd:{oid}", "g")])
    rows.append([("انصراف از سفارش", f"cx:{oid}", "r")])
    return edit(chat, mid, text, rows)

def apply_code(chat, oid, text):
    o = q("SELECT * FROM orders WHERE id=? AND tg=?", (oid, chat), one=True)
    if not o or o["status"] != "wait": clear_state(chat); return send(chat, "این سفارش دیگر فعال نیست.", home_rows(chat))
    code = "".join(ch for ch in str(text).upper().translate(DIG) if ch.isalnum() or ch in "_-")[:24]
    c = q("SELECT * FROM codes WHERE code=? AND active=1", (code,), one=True)
    back = [[("بازگشت به فاکتور", f"iv:{oid}")]]
    set_state(chat, "receipt", {"order": oid})
    if not c: return send(chat, "این کد تخفیف معتبر نیست.", back)
    if c["max_uses"] and c["used"] >= c["max_uses"]: return send(chat, "ظرفیت این کد تخفیف تمام شده است.", back)
    if q("SELECT 1 FROM code_uses WHERE code=? AND tg=?", (code, chat), one=True): return send(chat, "قبلاً از این کد استفاده کرده‌ای.", back)
    price = int(o["price"] or o["amount"]); amount = max(1000, int(round(price * (100 - int(c["pct"])) / 100.0)))
    x("UPDATE orders SET code=?,amount=?,updated=? WHERE id=? AND status='wait'", (code, amount, int(time.time()), oid))
    send(chat, f"کد تخفیف <b>{c['pct']}%</b> اعمال شد.")
    return invoice(chat, None, oid)

def on_receipt(chat, msg, oid):
    o = q("SELECT * FROM orders WHERE id=? AND tg=?", (oid, chat), one=True)
    if not o or o["status"] != "wait":
        clear_state(chat); return send(chat, "این سفارش دیگر فعال نیست.", home_rows(chat))
    fid = None
    if msg.get("photo"): fid = msg["photo"][-1]["file_id"]
    elif msg.get("document") and str(msg["document"].get("mime_type", "")).startswith("image/"): fid = msg["document"]["file_id"]
    if not fid: return send(chat, "لطفاً <b>عکس رسید</b> واریز را بفرست.", [[("انصراف از سفارش", f"cx:{oid}", "r")]])
    _, n = x("UPDATE orders SET status='review',receipt=?,updated=? WHERE id=? AND status='wait'", (fid, int(time.time()), oid))
    if not n: return
    clear_state(chat)
    p = plan(o["plan_id"]); u = msg.get("from") or {}
    who = esc(u.get("first_name", "")) + (f" · @{esc(u['username'])}" if u.get("username") else "")
    cap = (f"<b>رسید جدید · سفارش #{oid}</b>\n\nکاربر: {who}\nآیدی: <code>{chat}</code>\n" +
           (f"پلن: {esc(p['name'])}\n" if p else "") + f"مبلغ: <b>{money(o['amount'])}</b>\n" +
           ("نوع: شارژ کیف پول" if o["kind"] == "topup" else f"نوع: تمدید <code>{esc(o['target'])}</code>" if o["kind"] == "renew" else "نوع: خرید جدید"))
    notify_admins(cap, [[("✓ تأیید و فعال‌سازی", f"ok:{oid}", "g"), ("✕ رد", f"no:{oid}", "r")]], photo=fid)
    send(chat, f"رسیدت برای سفارش <b>#{oid}</b> ثبت شد.\nبعد از بررسی، " + ("کیف پولت شارژ می‌شود." if o["kind"] == "topup" else "اشتراک خودکار برایت ارسال می‌شود.") + " معمولاً چند دقیقه بیشتر طول نمی‌کشد.", [[("صفحه‌ی اصلی", "home")]])

def sub_card(username, u):
    if not u: return f"<code>{esc(username)}</code>\nاطلاعات این اشتراک در پنل پیدا نشد."
    used, lim = int(u.get("used_traffic") or 0), int(u.get("data_limit") or 0)
    exp = parse_exp(u.get("expire")); st = str(u.get("status") or "")
    st_fa = {"active": "فعال", "limited": "حجم تمام شده", "expired": "منقضی شده", "disabled": "غیرفعال", "on_hold": "در انتظار شروع"}.get(st, st)
    left = f"{max(0, int((exp - time.time()) // 86400))} روز" if exp else "بدون محدودیت"
    link = sub_link(u)
    return (f"<b>{esc(username)}</b> · {st_fa}\nمصرف: {bytes_txt(used) if used else '0 GB'} از {bytes_txt(lim)}\nزمان باقی‌مانده: {left}\n" +
            (f"\nلینک اشتراک:\n<code>{esc(link)}</code>" if link else ""))

def show_my(chat, mid=None, renew=False):
    subs = q("SELECT * FROM subs WHERE tg=? ORDER BY id DESC LIMIT 10", (chat,))
    if not subs:
        return edit(chat, mid, "هنوز اشتراکی نداری.\nاز «خرید اشتراک» اولین اشتراکت را بگیر.", [[("◈ خرید اشتراک", "buy", "b")], [("◷ سفارش‌ها", "ord"), ("بازگشت", "home")]])
    if renew:
        rows = [[(s["username"], f"rn:{s['username']}")] for s in subs] + [[("بازگشت", "home")]]
        return edit(chat, mid, "↻ <b>تمدید اشتراک</b>\nکدام اشتراک را تمدید می‌کنی؟", rows)
    parts, rows = [], []
    for s in subs:
        u = get_user(s["username"]); parts.append(sub_card(s["username"], u))
        link = sub_link(u)
        if link.startswith("http"): rows.append([(f"صفحه‌ی {s['username']}", link, "b"), ("⧉ کپی لینک", "copy:" + link, "g")])
    rows.append([("↻ تمدید", "renew", "g"), ("◷ سفارش‌ها", "ord")]); rows.append([("بازگشت", "home")])
    return edit(chat, mid, "◇ <b>اشتراک‌های من</b>\n\n" + "\n\n".join(parts), rows)

ST_FA = {"wait": "در انتظار پرداخت", "review": "در حال بررسی رسید", "work": "در حال فعال‌سازی", "done": "انجام شد", "reject": "رد شد", "cancel": "لغو شد"}
def show_orders(chat, mid=None):
    os_ = q("SELECT * FROM orders WHERE tg=? AND status!='cancel' ORDER BY id DESC LIMIT 8", (chat,))
    if not os_: return edit(chat, mid, "◷ هنوز سفارشی ثبت نکرده‌ای.", [[("◈ خرید اشتراک", "buy", "b")], [("بازگشت", "home")]])
    lines = []
    for o in os_:
        p = plan(o["plan_id"]) if o["plan_id"] else None
        what = "شارژ کیف پول" if o["kind"] == "topup" else (("تمدید " if o["kind"] == "renew" else "") + (p["name"] if p else "اشتراک"))
        when = time.strftime("%m/%d %H:%M", time.gmtime((o["created"] or 0) + 12600))
        lines.append(f"<b>#{o['id']}</b> · {esc(what)}\n{money(o['amount'])} · {ST_FA.get(o['status'], o['status'])} · {when}" +
                     (f"\nدلیل: {esc(o['result'])}" if o["status"] == "reject" and o["result"] else ""))
    rows = []
    w = [o for o in os_ if o["status"] == "wait"]
    if w: rows.append([(f"ادامه‌ی پرداخت سفارش #{w[0]['id']}", f"iv:{w[0]['id']}", "g")])
    rows.append([("بازگشت", "home")])
    return edit(chat, mid, "◷ <b>سفارش‌های من</b>\n\n" + "\n\n".join(lines), rows)

def help_text():
    t = kv_get("help", "")
    return t or ("◎ <b>آموزش اتصال</b>\n\n1. برنامه‌ی مناسب را نصب کن:\nاندروید: Hiddify یا v2rayNG\nآیفون: Streisand یا V2Box\nویندوز: Hiddify یا v2rayN\n\n"
                 "2. لینک اشتراک را کپی کن و در برنامه گزینه‌ی افزودن از کلیپ‌بورد را بزن.\n\n3. کانفیگ با کمترین پینگ را انتخاب کن و وصل شو.\n\n"
                 "اگر لینک اشتراک را در مرورگر باز کنی، صفحه‌ی اختصاصی CHOST با دکمه‌ی افزودن خودکار برایت باز می‌شود.")

def support_text():
    s = kv_get("support", "").strip()
    return ("✆ <b>پشتیبانی</b>\n\n" + (f"برای هر سؤال یا مشکل به {esc(s if s.startswith('@') else '@' + s)} پیام بده." if s else "پشتیبانی هنوز تنظیم نشده است.") +
            (f"\n\nکانال: {esc(channel_ref())}" if channel_ref() else ""))

# ---------------- wallet ----------------
TOPUP_MIN, TOPUP_MAX = 10000, 50000000
def bal(t):
    r = q("SELECT balance FROM users WHERE tg=?", (t,), one=True)
    return int(r["balance"] or 0) if r else 0
def add_bal(t, delta, reason, by=None):
    """atomic: never lets a balance go below zero. returns the new balance, or None when there is not enough money"""
    delta = int(delta)
    if not q("SELECT 1 FROM users WHERE tg=?", (t,), one=True):
        x("INSERT OR IGNORE INTO users(tg,name,uname,joined) VALUES(?,?,?,?)", (t, "", "", int(time.time())))
    _, n = x("UPDATE users SET balance=COALESCE(balance,0)+? WHERE tg=? AND COALESCE(balance,0)+?>=0", (delta, t, delta))
    if not n: return None
    x("INSERT INTO wallet_tx(tg,delta,reason,by,created) VALUES(?,?,?,?,?)", (t, delta, str(reason)[:120], by, int(time.time())))
    return bal(t)
def is_banned(t): r = q("SELECT banned FROM users WHERE tg=?", (t,), one=True); return bool(r and r["banned"])
def wallet_on(): return kv_get("wallet_on", "1") == "1"

def show_wallet(chat, mid=None):
    clear_state(chat); b = bal(chat)
    txs = q("SELECT * FROM wallet_tx WHERE tg=? ORDER BY id DESC LIMIT 6", (chat,))
    hist = "\n".join(("+" if t["delta"] > 0 else "−") + f" {money(abs(t['delta']))} · {esc(t['reason'])}" for t in txs)
    text = (f"▣ <b>کیف پول</b>\n\nموجودی: <b>{money(b)}</b>\n\nبا موجودی کیف پول، خرید و تمدید اشتراک فوری و بدون ارسال رسید انجام می‌شود." +
            (f"\n\n<b>تراکنش‌های اخیر</b>\n{hist}" if hist else ""))
    rows = [[("+ افزایش موجودی", "w:add", "g")]]
    if ref_on(): rows.append([("✦ دعوت دوستان و درآمد", "ref", "b")])
    rows.append([("بازگشت", "home")])
    return edit(chat, mid, text, rows)

def wallet_add_menu(chat, mid=None):
    if not card_fmt(kv_get("card", "")):
        notify_admins("یک کاربر قصد شارژ کیف پول داشت اما <b>شماره کارت</b> تنظیم نشده است.\nمدیریت ربات ← اطلاعات پرداخت")
        return edit(chat, mid, "پرداخت موقتاً در دسترس نیست. چند دقیقه دیگر دوباره امتحان کن.", [[("بازگشت", "w")]])
    set_state(chat, "topup")
    amts = [50000, 100000, 200000, 500000]
    rows = [[(money(a), f"w:amt:{a}", "b") for a in amts[:2]], [(money(a), f"w:amt:{a}", "b") for a in amts[2:]], [("انصراف", "w", "r")]]
    return edit(chat, mid, f"+ <b>افزایش موجودی</b>\n\nیکی از مبلغ‌ها را انتخاب کن یا مبلغ دلخواهت را به تومان بفرست.\n(حداقل {money(TOPUP_MIN)})", rows)

def topup_order(chat, mid, amount):
    if not TOPUP_MIN <= amount <= TOPUP_MAX:
        return send(chat, f"مبلغ باید بین {money(TOPUP_MIN)} و {money(TOPUP_MAX)} باشد. دوباره بفرست:", [[("انصراف", "w", "r")]])
    now = int(time.time())
    x("UPDATE orders SET status='cancel',updated=? WHERE tg=? AND status='wait'", (now, chat))
    oid, _ = x("INSERT INTO orders(tg,plan_id,kind,target,amount,price,status,created,updated) VALUES(?,?,?,?,?,?,?,?,?)",
               (chat, None, "topup", None, int(amount), int(amount), "wait", now, now))
    set_state(chat, "receipt", {"order": oid})
    return invoice(chat, mid, oid)

# ---------------- referral ----------------
def ref_on(): return (to_num(kv_get("ref_pct", "10")) or 0) > 0 and wallet_on()
def ref_pct(): return int(to_num(kv_get("ref_pct", "10")) or 0)
BOT_USER = {"u": ""}
def show_ref(chat, mid=None):
    if not ref_on(): return edit(chat, mid, "سیستم دعوت در حال حاضر فعال نیست.", [[("بازگشت", "home")]])
    link = f"https://t.me/{BOT_USER['u']}?start=ref_{chat}" if BOT_USER["u"] else ""
    n = q("SELECT COUNT(*) n FROM users WHERE ref=?", (chat,), one=True)["n"]
    earned = q("SELECT COALESCE(SUM(delta),0) s FROM wallet_tx WHERE tg=? AND reason LIKE 'پورسانت%'", (chat,), one=True)["s"]
    text = (f"✦ <b>دعوت دوستان</b>\n\nبا لینک اختصاصی خودت دوستانت را دعوت کن. از هر خرید آن‌ها <b>{ref_pct()}%</b> به کیف پولت اضافه می‌شود؛ برای همیشه.\n\n"
            f"دعوت‌شده‌ها: <b>{n}</b>\nدرآمد تا امروز: <b>{money(earned)}</b>" + (f"\n\nلینک دعوت تو:\n<code>{esc(link)}</code>" if link else ""))
    rows = ([[("⧉ کپی لینک دعوت", "copy:" + link, "g")]] if link else []) + [[("▣ کیف پول", "w"), ("بازگشت", "home")]]
    return edit(chat, mid, text, rows)
def pay_commission(o):
    if o["kind"] not in ("new", "renew") or not ref_on(): return
    r = q("SELECT ref FROM users WHERE tg=?", (o["tg"],), one=True)
    if not r or not r["ref"] or r["ref"] == o["tg"]: return
    amt = int(int(o["amount"] or 0) * ref_pct() / 100)
    if amt <= 0: return
    nb = add_bal(r["ref"], amt, f"پورسانت دعوت · سفارش #{o['id']}")
    if nb is not None:
        send(r["ref"], f"✦ <b>{money(amt)}</b> پورسانت دعوت به کیف پولت اضافه شد.\nموجودی فعلی: <b>{money(nb)}</b>", [[("▣ کیف پول", "w", "b")]])

def pay_from_wallet(chat, mid, oid):
    o = q("SELECT * FROM orders WHERE id=? AND tg=?", (oid, chat), one=True)
    if not o or o["status"] != "wait" or o["kind"] == "topup": return edit(chat, mid, "این سفارش دیگر فعال نیست.", home_rows(chat))
    amount = int(o["amount"])
    _, n = x("UPDATE orders SET status='work',paid_by='wallet',updated=? WHERE id=? AND status='wait'", (int(time.time()), oid))
    if not n: return edit(chat, mid, "این سفارش دیگر فعال نیست.", home_rows(chat))
    nb = add_bal(chat, -amount, f"پرداخت سفارش #{oid}")
    if nb is None:
        x("UPDATE orders SET status='wait',paid_by=NULL WHERE id=?", (oid,))
        return edit(chat, mid, f"موجودی کیف پولت کافی نیست.\nموجودی: {money(bal(chat))} · مبلغ سفارش: {money(amount)}", [[("+ افزایش موجودی", "w:add", "g")], [("بازگشت به فاکتور", f"iv:{oid}")]])
    clear_state(chat)
    edit(chat, mid, f"✓ مبلغ {money(amount)} از کیف پولت کسر شد. در حال فعال‌سازی…")
    r = fulfill(oid)
    if r.startswith("خطا"):
        add_bal(chat, amount, f"بازگشت وجه سفارش #{oid}")
        x("UPDATE orders SET status='cancel',updated=? WHERE id=?", (int(time.time()), oid))
        notify_admins(f"فعال‌سازی سفارش #{oid} (پرداخت از کیف پول) انجام نشد و مبلغ به کیف پول کاربر برگشت.\n{esc(r)}")
        return send(chat, "فعال‌سازی الان ممکن نشد و مبلغ به کیف پولت برگشت. چند دقیقه دیگر دوباره امتحان کن.", [[("▣ کیف پول", "w"), ("صفحه‌ی اصلی", "home")]])
    p = plan(o["plan_id"]); u = q("SELECT * FROM users WHERE tg=?", (chat,), one=True) or {}
    who = esc(u["name"] if u else "") + (f" · @{esc(u['uname'])}" if u and u["uname"] else "")
    notify_admins(f"▣ <b>خرید از کیف پول · سفارش #{oid}</b>\nکاربر: {who}\nآیدی: <code>{chat}</code>\n" + (f"پلن: {esc(p['name'])}\n" if p else "") + f"مبلغ: <b>{money(amount)}</b>")

# ---------------- approve / reject ----------------
def new_username(t):
    for n in range(1, 500):
        u = f"ch{t}_{n}"
        if not q("SELECT 1 FROM subs WHERE username=?", (u,), one=True) and not get_user(u): return u
    return f"ch{t}_{int(time.time())}"

def approve(oid, admin_chat):
    _, n = x("UPDATE orders SET status='work',paid_by=COALESCE(paid_by,'card'),updated=? WHERE id=? AND status='review'", (int(time.time()), oid))
    if not n:
        o = q("SELECT status FROM orders WHERE id=?", (oid,), one=True)
        return "این سفارش قبلاً بررسی شده" if o else "سفارش پیدا نشد"
    r = fulfill(oid)
    if r.startswith("خطا"): x("UPDATE orders SET status='review',updated=? WHERE id=? AND status='work'", (int(time.time()), oid))
    return r

def fulfill(oid):
    """order is in status 'work' (paid): create / renew the subscription or charge the wallet, then tell the user"""
    o = q("SELECT * FROM orders WHERE id=?", (oid,), one=True)
    if not o: return "خطا: سفارش پیدا نشد"
    if o["kind"] == "topup":
        nb = add_bal(o["tg"], int(o["amount"]), f"شارژ کیف پول · سفارش #{oid}")
        if nb is None: return "خطا: شارژ کیف پول انجام نشد"
        x("UPDATE orders SET status='done',result=?,updated=? WHERE id=?", ("wallet", int(time.time()), oid))
        send(o["tg"], f"<b>پرداختت تأیید شد</b>\n\n{money(o['amount'])} به کیف پولت اضافه شد.\nموجودی فعلی: <b>{money(nb)}</b>\n\n<i>حالا می‌توانی فوری و بدون ارسال رسید خرید کنی.</i>",
             [[("◈ خرید اشتراک", "buy", "b")], [("▣ کیف پول", "w"), ("صفحه‌ی اصلی", "home")]])
        return f"✓ سفارش #{oid} تأیید شد · شارژ {money(o['amount'])}"
    p = plan(o["plan_id"])
    try:
        if not p: raise RuntimeError("پلن این سفارش حذف شده")
        if o["kind"] == "renew" and o["target"]:
            u = renew_user(o["target"], p); uname = o["target"]
        else:
            uname = new_username(o["tg"]); u = create_user(uname, p)
            x("INSERT OR IGNORE INTO subs(tg,username,plan_id,created) VALUES(?,?,?,?)", (o["tg"], uname, p["id"], int(time.time())))
        x("UPDATE orders SET status='done',result=?,updated=? WHERE id=?", (uname, int(time.time()), oid))
        if o["code"]:
            _, n2 = x("INSERT OR IGNORE INTO code_uses(code,tg,oid) VALUES(?,?,?)", (o["code"], o["tg"], oid))
            if n2: x("UPDATE codes SET used=used+1 WHERE code=?", (o["code"],))
    except Exception as e:
        log("fulfill failed", oid, e)
        return f"خطا: {e}"
    u = get_user(uname) or u
    link = sub_link(u)
    rows = [[("صفحه‌ی اشتراک و افزودن خودکار", link, "b")], [("⧉ کپی لینک اشتراک", "copy:" + link, "g")]] if link.startswith("http") else []
    rows.append([("◇ اشتراک‌های من", "my"), ("◎ آموزش اتصال", "help")])
    send(o["tg"], (f"<b>{'پرداختت تأیید شد' if o['paid_by'] != 'wallet' else 'خرید با موفقیت انجام شد'}</b>\n\n" + ("اشتراکت تمدید شد." if o["kind"] == "renew" else "اشتراکت آماده است.") +
                   f"\n\n{sub_card(uname, u)}\n\n<i>با زدن روی لینک، کپی می‌شود. آن را در برنامه‌ی اتصال وارد کن.</i>"), rows)
    try: pay_commission(o)
    except Exception as e: log("commission error", oid, e)
    return f"✓ سفارش #{oid} تأیید شد · {uname}"

def reject(oid, reason=""):
    _, n = x("UPDATE orders SET status='reject',result=?,updated=? WHERE id=? AND status='review'", (reason, int(time.time()), oid))
    if not n: return "این سفارش قبلاً بررسی شده"
    o = q("SELECT * FROM orders WHERE id=?", (oid,), one=True)
    s = kv_get("support", "").strip()
    send(o["tg"], f"رسید سفارش <b>#{oid}</b> تأیید نشد." + (f"\nدلیل: {esc(reason)}" if reason else "") +
         (f"\n\nاگر فکر می‌کنی اشتباه شده، به {esc(s if s.startswith('@') else '@' + s)} پیام بده." if s else ""), [[("صفحه‌ی اصلی", "home")]])
    return f"✕ سفارش #{oid} رد شد"

# ---------------- admin side (inside the bot) ----------------
def stats():
    day = int(time.time() - 86400)
    r = q("SELECT COUNT(*) n, COALESCE(SUM(amount),0) s FROM orders WHERE status='done'", one=True)
    d = q("SELECT COUNT(*) n, COALESCE(SUM(amount),0) s FROM orders WHERE status='done' AND updated>=?", (day,), one=True)
    return {"users": q("SELECT COUNT(*) n FROM users", one=True)["n"], "sales": r["n"], "revenue": r["s"],
            "sales_today": d["n"], "revenue_today": d["s"], "pending": q("SELECT COUNT(*) n FROM orders WHERE status='review'", one=True)["n"],
            "wallets": q("SELECT COALESCE(SUM(balance),0) s FROM users", one=True)["s"],
            "new_users": q("SELECT COUNT(*) n FROM users WHERE joined>=?", (day,), one=True)["n"]}

def adm_home(chat, mid=None):
    clear_state(chat); s = stats()
    text = (f"◉ <b>مدیریت ربات فروش</b>\n\nفروش: <b>{'باز' if shop_open() else 'بسته'}</b>\nکاربران ربات: {s['users']} · امروز +{s['new_users']}\nموجودی کیف پول‌ها: {money(s['wallets'])}\n"
            f"فروش امروز: {s['sales_today']} سفارش · {money(s['revenue_today'])}\nکل فروش: {s['sales']} سفارش · {money(s['revenue'])}\n"
            f"در انتظار بررسی: <b>{s['pending']}</b>")
    rows = [[("▤ پلن‌ها و قیمت‌ها", "a:pl", "b"), ("▣ اطلاعات پرداخت", "a:pay", "b")],
            [(f"◷ رسیدهای در انتظار ({s['pending']})", "a:pend", "g" if s["pending"] else None)],
            [("◎ مدیریت کاربران", "a:us", "b")],
            [("◍ کدهای تخفیف", "a:cd"), ("◌ اکانت تست", "a:tr")],
            [("▣ کیف پول و دعوت", "a:rf")],
            [("✎ متن‌ها و کانال", "a:txt"), ("➤ پیام همگانی", "a:bc")],
            [("↓ بکاپ کامل", "a:bk", "b")],
            [("■ بستن فروش", "a:shop", "r") if shop_open() else ("► باز کردن فروش", "a:shop", "g")], [("بازگشت", "home")]]
    return edit(chat, mid, text, rows)

def adm_plans(chat, mid=None):
    clear_state(chat); ps = plans(False)
    text = "▤ <b>پلن‌ها</b>\nروی هر پلن بزن تا قیمت، حجم، زمان یا گروهش را تغییر بدهی." + ("" if ps else "\n\nهنوز پلنی نساختی.")
    rows = [[(("● " if p["active"] else "○ ") + f"{p['name']} · {money(p['price'])}", f"a:pv:{p['id']}")] for p in ps]
    rows += [[("+ افزودن پلن", "a:padd", "g")], [("بازگشت", "adm")]]
    return edit(chat, mid, text, rows)

def adm_plan(chat, mid, pid):
    clear_state(chat); p = plan(pid)
    if not p: return adm_plans(chat, mid)
    text = f"{plan_line(p)}\nوضعیت: {'فعال' if p['active'] else 'غیرفعال'}"
    rows = [[("قیمت", f"a:pe:{pid}:price"), ("حجم", f"a:pe:{pid}:gb"), ("مدت", f"a:pe:{pid}:days")],
            [("نام", f"a:pe:{pid}:name"), ("گروه: " + p["grp"].upper(), f"a:pg:{pid}")],
            [("غیرفعال کردن", f"a:pt:{pid}") if p["active"] else ("فعال کردن", f"a:pt:{pid}", "g"), ("حذف", f"a:pd:{pid}", "r")], [("بازگشت", "a:pl")]]
    return edit(chat, mid, text, rows)

FIELD_ASK = {"name": "نام پلن را بفرست (مثلاً: VIP 50 گیگ · یک ماهه)", "price": "قیمت را به تومان بفرست (فقط عدد، مثلاً 150000)",
             "gb": "حجم را به گیگابایت بفرست (0 یعنی نامحدود)", "days": "مدت را به روز بفرست (0 یعنی بدون محدودیت زمانی)"}

def check_field(f, text):
    if f == "name":
        t = text.strip()
        return (t[:60], None) if 2 <= len(t) <= 60 else (None, "نام باید بین 2 تا 60 کاراکتر باشد")
    v = to_num(text, allow_float=(f == "gb"))
    if v is None: return None, "فقط عدد بفرست"
    if f == "price" and not (1000 <= v <= 1000000000): return None, "قیمت باید بین 1,000 تا 1,000,000,000 تومان باشد"
    if f == "gb" and v > 100000: return None, "حجم خیلی زیاد است"
    if f == "days" and v > 3650: return None, "حداکثر 3650 روز"
    return v, None

def adm_pay(chat, mid=None):
    clear_state(chat)
    text = (f"▣ <b>اطلاعات پرداخت</b>\n\nشماره کارت: <code>{card_fmt(kv_get('card')) or 'تنظیم نشده'}</code>\n"
            f"صاحب حساب: {esc(kv_get('holder') or 'تنظیم نشده')}\nبانک: {esc(kv_get('bank') or 'تنظیم نشده')}")
    rows = [[("شماره کارت", "a:set:card")], [("صاحب حساب", "a:set:holder"), ("بانک", "a:set:bank")], [("بازگشت", "adm")]]
    return edit(chat, mid, text, rows)

def adm_txt(chat, mid=None):
    clear_state(chat); fj = kv_get("force_join", "0") == "1"
    text = (f"✎ <b>متن‌ها و کانال</b>\n\nپشتیبانی: {esc(kv_get('support') or 'تنظیم نشده')}\nکانال: {esc(channel_ref() or 'تنظیم نشده')}\n"
            f"عضویت اجباری: {'روشن' if fj else 'خاموش'}\n\n<i>برای عضویت اجباری، ربات باید ادمین کانال باشد.</i>")
    rows = [[("متن خوش‌آمد", "a:set:welcome"), ("متن آموزش", "a:set:help")], [("آیدی پشتیبانی", "a:set:support"), ("کانال", "a:set:channel")],
            [("عضویت اجباری: " + ("خاموش کن" if fj else "روشن کن"), "a:fj")], [("بازگشت", "adm")]]
    return edit(chat, mid, text, rows)

SET_ASK = {"trial_gb": "حجم اکانت تست را به گیگابایت بفرست (مثلاً 1 یا 0.5)", "trial_hours": "مدت اکانت تست را به ساعت بفرست (مثلاً 24)",
           "card": "شماره کارت 16 رقمی را بفرست", "holder": "نام صاحب حساب را بفرست", "bank": "نام بانک را بفرست",
           "welcome": "متن خوش‌آمد را بفرست. می‌توانی از {name} برای اسم کاربر استفاده کنی. برای حالت پیش‌فرض بفرست: -",
           "help": "متن آموزش اتصال را بفرست. برای حالت پیش‌فرض بفرست: -", "support": "آیدی پشتیبانی را بفرست (مثلاً @CHOST_support)",
           "channel": "آیدی کانال را بفرست (مثلاً @CHOST543). برای حذف بفرست: -",
           "ref_pct": "درصد پورسانت دعوت را بفرست (0 تا 50). 0 یعنی خاموش"}

def save_setting(k, text):
    t = text.strip()
    if k == "trial_gb":
        v = to_num(t, True)
        if v is None or not 0.1 <= v <= 100: return "عددی بین 0.1 تا 100 بفرست"
        kv_set(k, v); return None
    if k == "ref_pct":
        v = to_num(t)
        if v is None or not 0 <= v <= 50: return "عددی بین 0 تا 50 بفرست"
        kv_set(k, v); return None
    if k == "trial_hours":
        v = to_num(t)
        if v is None or not 1 <= v <= 720: return "عددی بین 1 تا 720 بفرست"
        kv_set(k, v); return None
    if t == "-" and k in ("welcome", "help", "channel"): kv_set(k, ""); return None
    if k == "card":
        d = "".join(ch for ch in t.translate(DIG) if ch.isdigit())
        if len(d) != 16: return "شماره کارت باید 16 رقم باشد"
        kv_set(k, d); return None
    if k == "support":
        u = t.lstrip("@")
        if not u.replace("_", "").isalnum() or not 3 <= len(u) <= 40: return "آیدی را درست بفرست (مثلاً @CHOST_support)"
        kv_set(k, "@" + u); return None
    if k == "channel":
        c = t.replace("https://t.me/", "").lstrip("@")
        if not c.replace("_", "").lstrip("-").isalnum(): return "آیدی کانال را درست بفرست"
        kv_set(k, c if c.lstrip("-").isdigit() else "@" + c); return None
    if len(t) > 3000: return "متن خیلی طولانی است"
    kv_set(k, t); return None

def adm_pending(chat, mid=None):
    rows_db = q("SELECT * FROM orders WHERE status='review' ORDER BY id LIMIT 10")
    if not rows_db: return edit(chat, mid, "◷ رسیدی در انتظار بررسی نیست.", [[("بازگشت", "adm")]])
    edit(chat, mid, f"◷ <b>{len(rows_db)} رسید در انتظار</b> · برایت ارسال شدند.", [[("بازگشت", "adm")]])
    for o in rows_db:
        p = plan(o["plan_id"])
        cap = (f"<b>سفارش #{o['id']}</b>\nآیدی: <code>{o['tg']}</code>\n" + (f"پلن: {esc(p['name'])}\n" if p else "") +
               f"مبلغ: <b>{money(o['amount'])}</b>\n" + ("شارژ کیف پول" if o["kind"] == "topup" else f"تمدید <code>{esc(o['target'])}</code>" if o["kind"] == "renew" else "خرید جدید"))
        notify_one(chat, cap, o["receipt"], [[("✓ تأیید و فعال‌سازی", f"ok:{o['id']}", "g"), ("✕ رد", f"no:{o['id']}", "r")]])

def notify_one(chat, cap, photo, rows):
    r = tg("sendPhoto", {"chat_id": chat, "photo": photo, "caption": cap[:1024], "parse_mode": "HTML", "reply_markup": kb(rows)}) if photo else {"ok": False}
    if not r.get("ok"): send(chat, cap, rows)

def adm_codes(chat, mid=None):
    clear_state(chat); cs = q("SELECT * FROM codes ORDER BY created DESC LIMIT 30")
    text = "◍ <b>کدهای تخفیف</b>\nکاربر موقع پرداخت با «کد تخفیف دارم» از آن استفاده می‌کند. هر کاربر از هر کد فقط یک بار." + ("" if cs else "\n\nهنوز کدی نساختی.")
    rows = [[(("● " if c["active"] else "○ ") + f"{c['code']} · {c['pct']}% · {c['used']}/{c['max_uses'] or '∞'}", f"a:cv:{c['code']}")] for c in cs]
    return edit(chat, mid, text, rows + [[("+ ساخت کد تخفیف", "a:cadd", "g")], [("بازگشت", "adm")]])

def adm_code(chat, mid, code):
    c = q("SELECT * FROM codes WHERE code=?", (code,), one=True)
    if not c: return adm_codes(chat, mid)
    text = f"◍ کد <code>{esc(c['code'])}</code>\nتخفیف: {c['pct']}%\nاستفاده: {c['used']} از {c['max_uses'] or 'نامحدود'}\nوضعیت: {'فعال' if c['active'] else 'غیرفعال'}"
    return edit(chat, mid, text, [[("غیرفعال کردن", f"a:ct:{code}") if c["active"] else ("فعال کردن", f"a:ct:{code}", "g"), ("حذف", f"a:cx:{code}", "r")], [("بازگشت", "a:cd")]])

def adm_trial(chat, mid=None):
    clear_state(chat); c = trial_cfg(); n = q("SELECT COUNT(*) n FROM kv WHERE k LIKE 'trial:%'", one=True)["n"]
    text = (f"◌ <b>اکانت تست رایگان</b>\n\nوضعیت: <b>{'روشن' if trial_on() else 'خاموش'}</b>\nحجم: {gbtxt(c['gb'])}\nمدت: {int(c['hours'])} ساعت\n"
            f"گروه: {GROUP_FA[c['grp']]}\nتست‌های گرفته‌شده: {n}\n\n<i>هر کاربر فقط یک بار می‌تواند اکانت تست بگیرد.</i>")
    rows = [[("خاموش کردن", "a:trt", "r") if trial_on() else ("روشن کردن", "a:trt", "g")],
            [("حجم", "a:set:trial_gb"), ("مدت", "a:set:trial_hours"), ("گروه: " + c["grp"].upper(), "a:trg")], [("بازگشت", "adm")]]
    return edit(chat, mid, text, rows)

def adm_backup_menu(chat, mid=None):
    on = kv_get("backup_on", "1") == "1"; last = to_num(kv_get("last_backup", "0")) or 0
    when = time.strftime("%Y-%m-%d %H:%M", time.gmtime(last + 12600)) if last else "هنوز گرفته نشده"
    text = (f"↓ <b>بکاپ کامل</b>\n\nشامل: دیتابیس پنل (کاربران، نماینده‌ها، تنظیمات)، دیتابیس ربات فروش و کلیدهای نصب.\n"
            f"بکاپ خودکار روزانه: <b>{'روشن' if on else 'خاموش'}</b>\nآخرین بکاپ: {when}\n\n<i>فایل بکاپ اطلاعات حساس دارد. آن را با کسی به اشتراک نگذار.</i>")
    return edit(chat, mid, text, [[("↓ گرفتن بکاپ الان", "a:bkn", "b")], [("خاموش کردن بکاپ روزانه", "a:bko", "r") if on else ("روشن کردن بکاپ روزانه", "a:bko", "g")], [("بازگشت", "adm")]])

# ---------------- admin: users and wallets ----------------
def adm_users(chat, mid=None):
    set_state(chat, "a:find")
    s = q("SELECT COUNT(*) n, COALESCE(SUM(balance),0) b, COALESCE(SUM(banned),0) x FROM users", one=True)
    recent = q("SELECT tg,name,uname,balance FROM users ORDER BY joined DESC LIMIT 8")
    text = (f"◎ <b>مدیریت کاربران</b>\n\nکل کاربران: <b>{s['n']}</b>\nمجموع موجودی کیف پول‌ها: <b>{money(s['b'])}</b>\nمسدود: {s['x']}\n\n"
            "برای پیدا کردن کاربر، <b>آیدی عددی</b> یا <b>یوزرنیم</b> او را بفرست؛ یا از آخرین کاربران انتخاب کن:")
    rows = [[((r["name"] or str(r["tg"]))[:24] + (f" · @{r['uname']}" if r["uname"] else "") + f" · {money(r['balance'] or 0)}", f"a:u:{r['tg']}")] for r in recent]
    rows.append([("بازگشت", "adm")])
    return edit(chat, mid, text, rows)

def find_user(text):
    t = text.strip().translate(DIG).lstrip("@")
    if t.lstrip("-").isdigit(): return q("SELECT * FROM users WHERE tg=?", (int(t),), one=True)
    return q("SELECT * FROM users WHERE lower(uname)=lower(?)", (t,), one=True)

def adm_user(chat, mid, tgid):
    clear_state(chat); u = q("SELECT * FROM users WHERE tg=?", (tgid,), one=True)
    if not u: return edit(chat, mid, "کاربر پیدا نشد.", [[("بازگشت", "a:us")]])
    o = q("SELECT COUNT(*) n, COALESCE(SUM(amount),0) s FROM orders WHERE tg=? AND status='done' AND kind!='topup'", (tgid,), one=True)
    subs = q("SELECT username FROM subs WHERE tg=? ORDER BY id DESC", (tgid,))
    invited = q("SELECT COUNT(*) n FROM users WHERE ref=?", (tgid,), one=True)["n"]
    joined = time.strftime("%Y-%m-%d", time.gmtime((u["joined"] or 0) + 12600))
    text = (f"◎ <b>{esc(u['name'] or 'بدون نام')}</b>" + (f" · @{esc(u['uname'])}" if u["uname"] else "") +
            f"\nآیدی: <code>{tgid}</code>\nعضویت: {joined}\nوضعیت: {'<b>مسدود</b>' if u['banned'] else 'فعال'}\n\n"
            f"موجودی کیف پول: <b>{money(u['balance'] or 0)}</b>\nخریدها: {o['n']} · {money(o['s'])}\nدعوت‌شده‌ها: {invited}\n"
            f"اشتراک‌ها: {', '.join('<code>' + esc(r['username']) + '</code>' for r in subs[:6]) or 'ندارد'}")
    rows = [[("+ افزایش موجودی", f"a:ub:p:{tgid}", "g"), ("− کاهش موجودی", f"a:ub:m:{tgid}", "r")],
            [("➤ پیام به کاربر", f"a:um:{tgid}", "b")],
            [("رفع مسدودی", f"a:ux:{tgid}", "g") if u["banned"] else ("مسدود کردن", f"a:ux:{tgid}", "r")],
            [("بازگشت", "a:us")]]
    return edit(chat, mid, text, rows)

def adm_wallet(chat, mid=None):
    clear_state(chat); won = wallet_on(); pct = ref_pct()
    n_ref = q("SELECT COUNT(*) n FROM users WHERE ref IS NOT NULL", one=True)["n"]
    paid = q("SELECT COALESCE(SUM(delta),0) s FROM wallet_tx WHERE reason LIKE 'پورسانت%'", one=True)["s"]
    text = (f"▣ <b>کیف پول و دعوت</b>\n\nکیف پول: <b>{'روشن' if won else 'خاموش'}</b>\nپورسانت دعوت: <b>{pct}%</b>" + (" (خاموش)" if not pct else "") +
            f"\nکاربران دعوت‌شده: {n_ref}\nپورسانت پرداخت‌شده: {money(paid)}\n\n"
            "<i>کاربر با موجودی کیف پول فوری و بدون رسید خرید می‌کند. از هر خرید دعوت‌شده‌ها، پورسانت به کیف پول دعوت‌کننده اضافه می‌شود. برای خاموش کردن دعوت، پورسانت را 0 بگذار.</i>")
    rows = [[("خاموش کردن کیف پول", "a:wo", "r") if won else ("روشن کردن کیف پول", "a:wo", "g")],
            [("درصد پورسانت دعوت", "a:set:ref_pct")], [("بازگشت", "adm")]]
    return edit(chat, mid, text, rows)

def broadcast(admin_chat, text):
    users = [r["tg"] for r in q("SELECT tg FROM users WHERE blocked=0")]
    def run():
        ok = bad = 0
        for u in users:
            r = send(u, text)
            if r.get("ok"): ok += 1
            else:
                bad += 1
                if r.get("error_code") == 403: x("UPDATE users SET blocked=1 WHERE tg=?", (u,))
            time.sleep(0.05)   # stay under Telegram's limit (~30 msg/s)
        send(admin_chat, f"➤ پیام همگانی تمام شد.\nارسال موفق: {ok} · ناموفق: {bad}")
    threading.Thread(target=run, daemon=True).start()
    return len(users)

# ---------------- backups (daily + on demand, sent to the admins in Telegram) ----------------
import io, tempfile, uuid, zipfile
def send_document(chat, filename, data, caption=""):
    bd = "----chost" + uuid.uuid4().hex; out = io.BytesIO()
    for k, v in (("chat_id", str(chat)), ("caption", caption[:1024]), ("parse_mode", "HTML")):
        out.write(f'--{bd}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    out.write(f'--{bd}\r\nContent-Disposition: form-data; name="document"; filename="{filename}"\r\nContent-Type: application/zip\r\n\r\n'.encode())
    out.write(data); out.write(f"\r\n--{bd}--\r\n".encode())
    r = urllib.request.Request(f"https://api.telegram.org/bot{TOKEN}/sendDocument", data=out.getvalue(), headers={"Content-Type": f"multipart/form-data; boundary={bd}"})
    try:
        with urllib.request.urlopen(r, timeout=180) as resp: return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try: return json.loads(e.read().decode())
        except Exception: return {"ok": False, "description": f"HTTP {e.code}"}
    except Exception as e: return {"ok": False, "description": str(e)}

def _sqlite_copy(src, zf, arc):
    """consistent copy of a live sqlite database (safe while the panel is running)"""
    if not os.path.exists(src): return False
    fd, tmp = tempfile.mkstemp(suffix=".sqlite3"); os.close(fd)
    try:
        a = sqlite3.connect(src, timeout=30); b = sqlite3.connect(tmp)
        with b: a.backup(b)
        a.close(); b.close(); zf.write(tmp, arc); return True
    finally:
        try: os.remove(tmp)
        except OSError: pass

def make_backup():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        _sqlite_copy(f"{DATA}/db.sqlite3", zf, "db.sqlite3")
        with _dbl: _sqlite_copy(DB_FILE, zf, "chost-bot.db")
        for f in ("paths.json", "node_api_key", "chost-bot.json", ".owner_initialized", ".reseller_initialized"):
            if os.path.exists(f"{DATA}/{f}"): zf.write(f"{DATA}/{f}", f)
        for f in ("cert.pem", "key.pem"):
            if os.path.exists(f"{DATA}/node-certs/{f}"): zf.write(f"{DATA}/node-certs/{f}", f"node-certs/{f}")
        zf.writestr("RESTORE.txt", "CHOST backup\nRestore: stop the service, copy these files into the volume (/var/lib/pasarguard), start the service.\n")
    return buf.getvalue()

def do_backup(chats=None, why="بکاپ خودکار روزانه"):
    try:
        data = make_backup()
    except Exception as e:
        log("backup failed:", e)
        for c in chats or admins(): send(c, f"↓ ساخت بکاپ انجام نشد: {esc(e)}")
        return False
    name = time.strftime("CHOST-backup-%Y%m%d-%H%M.zip", time.gmtime(time.time() + 12600))
    if len(data) > 49 * 1024 * 1024:
        for c in chats or admins(): send(c, "↓ حجم بکاپ از حد مجاز تلگرام (50 مگابایت) بیشتر است.")
        return False
    ok = 0
    for c in chats or admins():
        r = send_document(c, name, data, f"↓ <b>{esc(why)}</b>\n{time.strftime('%Y-%m-%d %H:%M', time.gmtime(time.time() + 12600))} · {round(len(data) / 1024)} KB")
        ok += 1 if r.get("ok") else 0
    if ok: kv_set("last_backup", int(time.time()))
    return ok > 0

# ---------------- reminders: data almost used up / plan almost over ----------------
def remind_once(key, chat, text, rows):
    if kv_get(key): return
    kv_set(key, int(time.time())); send(chat, text, rows)

def check_reminders():
    for srow in q("SELECT tg, username FROM subs"):
        u = get_user(srow["username"])
        if not u or str(u.get("status") or "") != "active": continue
        uname, rows = srow["username"], [[("↻ تمدید همین اشتراک", f"rn:{srow['username']}", "g")], [("◇ اشتراک‌های من", "my")]]
        exp = parse_exp(u.get("expire"))
        if exp:
            left = exp - time.time()
            if 0 < left <= 3 * 86400:
                remind_once(f"rem:e:{uname}:{exp}", srow["tg"], f"◷ <b>اشتراک {esc(uname)}</b> کمتر از {max(1, int(left // 86400) + 1)} روز دیگر تمام می‌شود.\nبرای قطع نشدن اتصال، همین حالا تمدید کن.", rows)
        lim, used = int(u.get("data_limit") or 0), int(u.get("used_traffic") or 0)
        if lim and used and lim - used <= max(lim * 0.1, GB):
            remind_once(f"rem:v:{uname}:{lim}", srow["tg"], f"◔ <b>حجم اشتراک {esc(uname)}</b> رو به اتمام است.\nباقی‌مانده: {bytes_txt(max(0, lim - used)) if lim - used > 0 else '0 GB'}\nبرای ادامه، تمدید کن.", rows)
        time.sleep(0.2)

def maintenance():
    """runs forever next to the bot: daily backup + reminders (only while the bot is on)"""
    last_rem = 0
    while True:
        time.sleep(60)
        if not CFG.get("enabled") or not TOKEN: continue
        try:
            if kv_get("backup_on", "1") == "1" and time.time() - (to_num(kv_get("last_backup", "0")) or 0) > 86400 and admins():
                do_backup()
        except Exception as e: log("daily backup error:", e)
        try: x("UPDATE orders SET status='cancel',updated=? WHERE status='wait' AND created<?", (int(time.time()), int(time.time()) - 86400))   # unpaid invoices expire after a day
        except Exception as e: log("cleanup error:", e)
        if time.time() - last_rem > 1800:
            last_rem = time.time()
            try: check_reminders()
            except Exception as e: log("reminders error:", e)

# ---------------- dispatcher ----------------
def remember(u):
    if not u: return
    x("INSERT INTO users(tg,name,uname,joined) VALUES(?,?,?,?) ON CONFLICT(tg) DO UPDATE SET name=excluded.name,uname=excluded.uname,blocked=0",
      (u["id"], (u.get("first_name") or "")[:64], (u.get("username") or "")[:64], int(time.time())))

def gate(chat):
    link = join_needed(chat)
    if not link: return False
    send(chat, "برای استفاده از ربات، اول عضو کانال ما شو و بعد «عضو شدم» را بزن.", [[("عضویت در کانال", link, "b")], [("✓ عضو شدم", "home", "g")]])
    return True

def on_message(m):
    chat = (m.get("chat") or {}).get("id"); frm = m.get("from") or {}
    if not chat or (m.get("chat") or {}).get("type") != "private": return
    existed = bool(q("SELECT 1 FROM users WHERE tg=?", (chat,), one=True))
    remember(frm); text = (m.get("text") or "").strip()
    if not is_admin(chat) and is_banned(chat): return send(chat, "دسترسی‌ات به ربات مسدود شده است.")
    if text.startswith("/start ref_") and not existed:
        r = to_num(text[11:].strip())
        if r and r != chat and q("SELECT 1 FROM users WHERE tg=?", (r,), one=True): x("UPDATE users SET ref=? WHERE tg=? AND ref IS NULL", (r, chat))
    if text.startswith("/start") or text in ("/menu", "منو"):
        if gate(chat): return
        return show_home(chat, frm.get("first_name", ""))
    if text == "/admin" and is_admin(chat): return adm_home(chat)
    if text == "/wallet" and wallet_on():
        if gate(chat): return
        return show_wallet(chat)
    if text == "/cancel": clear_state(chat); return send(chat, "لغو شد.", home_rows(chat))
    st, data = get_state(chat)
    if st == "code": return apply_code(chat, data.get("order"), text)
    if st == "receipt": return on_receipt(chat, m, data.get("order"))
    if st == "topup":
        v = to_num(text)
        if v is None: return send(chat, "مبلغ را فقط با عدد و به تومان بفرست (مثلاً 150000):", [[("انصراف", "w", "r")]])
        return topup_order(chat, None, v)
    if is_admin(chat) and st.startswith("a:"):
        if not text: return send(chat, "متن بفرست یا /cancel")
        if st == "a:set":
            err = save_setting(data["k"], text)
            if err: return send(chat, err + "\n(لغو: /cancel)")
            send(chat, "✓ ذخیره شد")
            return (adm_pay if data["k"] in ("card", "holder", "bank") else adm_trial if data["k"].startswith("trial_") else adm_wallet if data["k"] == "ref_pct" else adm_txt)(chat)
        if st == "a:pe":
            if data.get("f") not in FIELD_ASK: clear_state(chat); return adm_plans(chat)
            v, err = check_field(data["f"], text)
            if err: return send(chat, err + "\n(لغو: /cancel)")
            x(f"UPDATE plans SET {data['f']}=? WHERE id=?", (v, data["pid"]))   # f is from a fixed whitelist
            send(chat, "✓ ذخیره شد"); return adm_plan(chat, None, data["pid"])
        if st == "a:padd":
            step = data.get("step", "name"); v, err = check_field(step, text)
            if err: return send(chat, err + "\n(لغو: /cancel)")
            data[step] = v; order = ["name", "gb", "days", "price"]
            if step != "price":
                nxt = order[order.index(step) + 1]; data["step"] = nxt; set_state(chat, "a:padd", data)
                return send(chat, FIELD_ASK[nxt])
            pid, _ = x("INSERT INTO plans(name,grp,gb,days,price,sort) VALUES(?,?,?,?,?,?)", (data["name"], data.get("grp", "vip"), data["gb"], data["days"], data["price"], int(time.time())))
            send(chat, "✓ پلن ساخته شد"); return adm_plan(chat, None, pid)
        if st == "a:cadd":
            step = data.get("step", "code")
            if step == "code":
                code = "".join(ch for ch in text.upper().translate(DIG) if ch.isalnum() or ch in "_-")[:24]
                if len(code) < 3: return send(chat, "کد باید حداقل 3 کاراکتر (حروف انگلیسی یا عدد) باشد\n(لغو: /cancel)")
                if q("SELECT 1 FROM codes WHERE code=?", (code,), one=True): return send(chat, "این کد قبلاً ساخته شده. یک کد دیگر بفرست\n(لغو: /cancel)")
                data.update(code=code, step="pct"); set_state(chat, "a:cadd", data); return send(chat, "درصد تخفیف را بفرست (1 تا 90)")
            if step == "pct":
                v = to_num(text)
                if v is None or not 1 <= v <= 90: return send(chat, "عددی بین 1 تا 90 بفرست\n(لغو: /cancel)")
                data.update(pct=v, step="max"); set_state(chat, "a:cadd", data); return send(chat, "حداکثر تعداد استفاده را بفرست (0 یعنی نامحدود)")
            v = to_num(text)
            if v is None or v > 100000: return send(chat, "عدد درست بفرست (0 یعنی نامحدود)\n(لغو: /cancel)")
            x("INSERT OR IGNORE INTO codes(code,pct,max_uses,used,active,created) VALUES(?,?,?,0,1,?)", (data["code"], data["pct"], v, int(time.time())))
            send(chat, f"✓ کد <code>{esc(data['code'])}</code> با {data['pct']}% تخفیف ساخته شد"); return adm_codes(chat)
        if st == "a:find":
            u = find_user(text)
            if not u: return send(chat, "کاربری با این آیدی یا یوزرنیم پیدا نشد. دوباره بفرست یا /cancel", [[("بازگشت", "a:us")]])
            return adm_user(chat, None, u["tg"])
        if st == "a:ub":
            v = to_num(text)
            if not v or v > 1000000000: return send(chat, "مبلغ را فقط با عدد و به تومان بفرست\n(لغو: /cancel)")
            t2, plus = data["tg"], data.get("sign") == "p"
            nb = add_bal(t2, v if plus else -v, "افزایش توسط پشتیبانی" if plus else "کاهش توسط پشتیبانی", chat)
            if nb is None: return send(chat, f"موجودی کاربر کافی نیست. موجودی فعلی: {money(bal(t2))}\nمبلغ کمتری بفرست یا /cancel")
            clear_state(chat)
            send(t2, ("+ " if plus else "− ") + f"<b>{money(v)}</b> " + ("به کیف پولت اضافه شد." if plus else "از کیف پولت کسر شد.") + f"\nموجودی فعلی: <b>{money(nb)}</b>", [[("▣ کیف پول", "w")]])
            send(chat, f"✓ انجام شد. موجودی جدید: <b>{money(nb)}</b>"); return adm_user(chat, None, t2)
        if st == "a:um":
            clear_state(chat)
            r = send(data["tg"], "➤ <b>پیام از پشتیبانی CHOST</b>\n\n" + esc(text[:3500]), [[("صفحه‌ی اصلی", "home")]])
            send(chat, "✓ پیام ارسال شد." if r.get("ok") else "پیام ارسال نشد؛ احتمالاً کاربر ربات را مسدود کرده است."); return adm_user(chat, None, data["tg"])
        if st == "a:bc":
            n = broadcast(chat, text); clear_state(chat); return send(chat, f"➤ ارسال به {n} کاربر شروع شد. در پایان خبرت می‌کنم.", [[("بازگشت", "adm")]])
        if st == "a:rej":
            clear_state(chat); return send(chat, reject(data["oid"], "" if text == "-" else text[:300]), [[("بازگشت", "adm")]])
    if gate(chat): return
    return show_home(chat, frm.get("first_name", ""))

def on_callback(c):
    cid, d = c["id"], c.get("data") or ""; msg = c.get("message") or {}
    chat = (msg.get("chat") or {}).get("id") or (c.get("from") or {}).get("id"); mid = msg.get("message_id")
    frm = c.get("from") or {}; remember(frm); name = frm.get("first_name", "")
    is_photo = bool(msg.get("photo"))
    try:
        if d.startswith(("ok:", "no:")):
            if not is_admin(frm.get("id")): return answer(cid, "دسترسی نداری", True)
            oid = int(d.split(":")[1])
            if d.startswith("ok:"):
                answer(cid, "در حال فعال‌سازی…"); r = approve(oid, chat)
            else:
                o = q("SELECT status FROM orders WHERE id=?", (oid,), one=True)
                if not o or o["status"] != "review": answer(cid, "این سفارش قبلاً بررسی شده", True); r = None
                else:
                    set_state(chat, "a:rej", {"oid": oid}); answer(cid)
                    return send(chat, f"دلیل رد سفارش #{oid} را بفرست (یا «-» برای بدون دلیل).")
            if r and r.startswith("خطا"):     # keep the buttons so the admin can try again
                send(chat, esc(r) + "\nسفارش هنوز در انتظار است، دوباره «تأیید» را بزن.")
            elif r:
                tg("editMessageReplyMarkup", {"chat_id": chat, "message_id": mid, "reply_markup": {"inline_keyboard": [[{"text": r[:60], "callback_data": "noop"}]]}})
            return
        if d == "adm": d = "a:home"        # the admin menu button and every "back to admin menu" button
        if d.startswith("a:") and not is_admin(frm.get("id")): return answer(cid, "دسترسی نداری", True)
        if not is_admin(frm.get("id")) and is_banned(chat): return answer(cid, "دسترسی‌ات به ربات مسدود شده است.", True)
        answer(cid)
        if is_photo: mid = None    # photo messages (receipts) cannot be edited as text: answer with a new message
        if d == "noop": return
        if not d.startswith("a:") and gate(chat): return
        if d == "home": return show_home(chat, name, mid)
        if d == "buy": return show_plans(chat, mid)
        if d == "renew": return show_my(chat, mid, renew=True)
        if d.startswith("rn:"): return show_plans(chat, mid, target=d[3:])
        if d.startswith("pl:"):
            _, pid, target = d.split(":", 2); return checkout(chat, mid, int(pid), target or None)
        if d.startswith("cd:"):
            oid = int(d[3:]); o = q("SELECT status FROM orders WHERE id=? AND tg=?", (oid, chat), one=True)
            if not o or o["status"] != "wait": return edit(chat, mid, "این سفارش دیگر فعال نیست.", home_rows(chat))
            set_state(chat, "code", {"order": oid}); return send(chat, "کد تخفیف را بفرست:", [[("انصراف", f"iv:{oid}", "r")]])
        if d.startswith("iv:"):
            oid = int(d[3:])
            if not q("SELECT 1 FROM orders WHERE id=? AND tg=?", (oid, chat), one=True): return show_home(chat, name, mid)
            set_state(chat, "receipt", {"order": oid}); return invoice(chat, mid, oid)
        if d == "trial": return take_trial(chat, mid, frm)
        if d == "w": return show_wallet(chat, mid) if wallet_on() else show_home(chat, name, mid)
        if d == "w:add": return wallet_add_menu(chat, mid) if wallet_on() else show_home(chat, name, mid)
        if d.startswith("w:amt:"): return topup_order(chat, mid, int(to_num(d[6:]) or 0)) if wallet_on() else show_home(chat, name, mid)
        if d == "ref": return show_ref(chat, mid)
        if d == "ord": return show_orders(chat, mid)
        if d.startswith("wp:"): return pay_from_wallet(chat, mid, int(d[3:]))
        if d.startswith("cx:"):
            x("UPDATE orders SET status='cancel',updated=? WHERE id=? AND tg=? AND status='wait'", (int(time.time()), int(d[3:]), chat))
            clear_state(chat); return edit(chat, mid, "سفارش لغو شد.", home_rows(chat))
        if d == "my": return show_my(chat, mid)
        if d == "help": return edit(chat, mid, help_text(), [[("بازگشت", "home")]])
        if d == "support": return edit(chat, mid, support_text(), [[("بازگشت", "home")]])
        if not d.startswith("a:"): return
        if d == "a:home": return adm_home(chat, mid)
        if d == "a:us": return adm_users(chat, mid)
        if d.startswith("a:u:"): return adm_user(chat, mid, int(d[4:]))
        if d.startswith("a:ub:"):
            _, _, sign, tgid = d.split(":"); set_state(chat, "a:ub", {"tg": int(tgid), "sign": sign})
            return edit(chat, mid, ("+ مبلغ افزایش" if sign == "p" else "− مبلغ کاهش") + " موجودی را به تومان بفرست:\n(لغو: /cancel)", [[("انصراف", f"a:u:{tgid}", "r")]])
        if d.startswith("a:um:"):
            set_state(chat, "a:um", {"tg": int(d[5:])}); return edit(chat, mid, "➤ متن پیام برای این کاربر را بفرست:\n(لغو: /cancel)", [[("انصراف", f"a:u:{d[5:]}", "r")]])
        if d.startswith("a:ux:"):
            t2 = int(d[5:])
            if is_admin(t2): return adm_user(chat, mid, t2)
            x("UPDATE users SET banned=1-COALESCE(banned,0) WHERE tg=?", (t2,)); return adm_user(chat, mid, t2)
        if d == "a:rf": return adm_wallet(chat, mid)
        if d == "a:wo": kv_set("wallet_on", "0" if wallet_on() else "1"); return adm_wallet(chat, mid)
        if d == "a:pl": return adm_plans(chat, mid)
        if d == "a:pay": return adm_pay(chat, mid)
        if d == "a:txt": return adm_txt(chat, mid)
        if d == "a:pend": return adm_pending(chat, mid)
        if d == "a:shop": kv_set("shop", "0" if shop_open() else "1"); return adm_home(chat, mid)
        if d == "a:fj": kv_set("force_join", "0" if kv_get("force_join", "0") == "1" else "1"); return adm_txt(chat, mid)
        if d == "a:bc": set_state(chat, "a:bc"); return edit(chat, mid, "➤ متن پیام همگانی را بفرست.\n(لغو: /cancel)", [[("انصراف", "adm")]])
        if d.startswith("a:set:"):
            k = d[6:]
            if k not in SET_ASK: return
            set_state(chat, "a:set", {"k": k}); return edit(chat, mid, SET_ASK[k] + "\n(لغو: /cancel)", [[("انصراف", "adm")]])
        if d == "a:cd": return adm_codes(chat, mid)
        if d == "a:cadd": set_state(chat, "a:cadd", {"step": "code"}); return edit(chat, mid, "کد تخفیف را بفرست (مثلاً CHOST20)\n(لغو: /cancel)", [[("انصراف", "a:cd", "r")]])
        if d.startswith("a:cv:"): return adm_code(chat, mid, d[5:])
        if d.startswith("a:ct:"): x("UPDATE codes SET active=1-active WHERE code=?", (d[5:],)); return adm_code(chat, mid, d[5:])
        if d.startswith("a:cx:"): x("DELETE FROM codes WHERE code=?", (d[5:],)); return adm_codes(chat, mid)
        if d == "a:tr": return adm_trial(chat, mid)
        if d == "a:trt": kv_set("trial_on", "0" if trial_on() else "1"); return adm_trial(chat, mid)
        if d == "a:trg": kv_set("trial_grp", "game" if trial_cfg()["grp"] == "vip" else "vip"); return adm_trial(chat, mid)
        if d == "a:bko": kv_set("backup_on", "0" if kv_get("backup_on", "1") == "1" else "1"); return adm_backup_menu(chat, mid)
        if d == "a:bk": return adm_backup_menu(chat, mid)
        if d == "a:bkn":
            edit(chat, mid, "↓ در حال آماده‌سازی بکاپ…"); threading.Thread(target=lambda: do_backup([chat], "بکاپ دستی"), daemon=True).start(); return
        if d.startswith("a:pv:"): return adm_plan(chat, mid, int(d[5:]))
        if d.startswith("a:pe:"):
            _, _, pid, f = d.split(":")
            if f not in FIELD_ASK: return
            set_state(chat, "a:pe", {"pid": int(pid), "f": f}); return edit(chat, mid, FIELD_ASK[f] + "\n(لغو: /cancel)", [[("انصراف", f"a:pv:{pid}")]])
        if d.startswith("a:pg:"):
            pid = int(d[5:]); p = plan(pid)
            if p: x("UPDATE plans SET grp=? WHERE id=?", ("game" if p["grp"] == "vip" else "vip", pid))
            return adm_plan(chat, mid, pid)
        if d.startswith("a:pt:"):
            pid = int(d[5:]); x("UPDATE plans SET active=1-active WHERE id=?", (pid,)); return adm_plan(chat, mid, pid)
        if d.startswith("a:pd:"):
            pid = int(d[5:]); return edit(chat, mid, "این پلن حذف شود؟ سفارش‌های قبلی این پلن دست نمی‌خورند.", [[("بله، حذف کن", f"a:pdd:{pid}", "r"), ("نه", f"a:pv:{pid}")]])
        if d.startswith("a:pdd:"):
            x("DELETE FROM plans WHERE id=?", (int(d[6:]),)); return adm_plans(chat, mid)
        if d == "a:padd":
            return edit(chat, mid, "گروه کانفیگ‌های این پلن را انتخاب کن:", [[("VIP · دانلود و استریم", "a:pn:vip", "b")], [("GAME · گیم و تماس", "a:pn:game", "g")], [("انصراف", "a:pl", "r")]])
        if d.startswith("a:pn:"):
            set_state(chat, "a:padd", {"grp": d[5:] if d[5:] in GROUPS else "vip", "step": "name"}); return edit(chat, mid, FIELD_ASK["name"] + "\n(لغو: /cancel)")
    except (ValueError, IndexError):
        return       # malformed or forged button data: ignore quietly
    except Exception as e:
        log("callback error:", d, e)
        try: send(chat, "یک خطای موقت پیش آمد، دوباره امتحان کن.")
        except Exception: pass

# ---------------- main loop ----------------
_locks, _locks_g = {}, threading.Lock()
def _chat_lock(upd):
    m = upd.get("message") or (upd.get("callback_query") or {}).get("message") or {}
    k = (m.get("chat") or {}).get("id") or ((upd.get("callback_query") or {}).get("from") or {}).get("id") or 0
    with _locks_g:
        if len(_locks) > 5000: _locks.clear()
        return _locks.setdefault(k, threading.Lock())
def handle(upd):
    lk = _chat_lock(upd)
    if not lk.acquire(timeout=40): return     # one update at a time per chat: double taps can never race each other
    try:
        if "message" in upd: on_message(upd["message"])
        elif "callback_query" in upd: on_callback(upd["callback_query"])
    except Exception as e:
        log("update error:", e)
    finally:
        lk.release()

def run():
    global TOKEN, CFG
    init_db()
    if not kv_get("last_backup"): kv_set("last_backup", int(time.time()) - 86400 + 3600)   # first automatic backup one hour after the bot starts
    threading.Thread(target=maintenance, daemon=True).start()
    offset, last_check, me_for, healthy = 0, 0, None, True
    while True:
        CFG = load_cfg()
        tok = str(CFG.get("token") or "").strip()
        if not CFG.get("enabled") or not tok:
            if me_for is not None: write_status(running=False, error="", username=""); me_for = None
            write_status(running=False); time.sleep(1); continue
        if tok != TOKEN or me_for != tok:
            TOKEN = tok; me = tg("getMe", timeout=15)
            if not me.get("ok"):
                write_status(running=False, error="توکن نامعتبر است یا اتصال به تلگرام برقرار نشد: " + str(me.get("description", ""))[:120], username="")
                me_for = None; time.sleep(4); continue
            tg("deleteWebhook", {"drop_pending_updates": False}, timeout=15)
            tg("setMyCommands", {"commands": [{"command": "start", "description": "منوی اصلی"}, {"command": "wallet", "description": "کیف پول"}, {"command": "cancel", "description": "لغو کار فعلی"}]}, timeout=15)
            me_for = tok; offset = 0; BOT_USER["u"] = me["result"].get("username", "")
            write_status(running=True, error="", username=me["result"].get("username", ""))
            log("bot online as @" + me["result"].get("username", ""))
        r = tg("getUpdates", {"offset": offset, "timeout": 6, "allowed_updates": ["message", "callback_query"]}, timeout=15)   # short poll: new settings apply within seconds
        if not r.get("ok"):
            if r.get("error_code") == 409: tg("deleteWebhook", {}, timeout=15)
            if r.get("error_code") == 401: me_for = None
            write_status(running=False, error="اتصال به تلگرام قطع شد، دوباره تلاش می‌کنم: " + str(r.get("description", ""))[:120])
            healthy = False; time.sleep(5); continue
        if not healthy: healthy = True; write_status(running=True, error="")
        for upd in r.get("result", []):
            offset = max(offset, upd["update_id"] + 1)
            threading.Thread(target=handle, args=(upd,), daemon=True).start()
        if time.time() - last_check > 60:
            last_check = time.time()
            try: write_status(running=True, error="", stats=stats())
            except Exception: pass

if __name__ == "__main__":
    try: run()
    except KeyboardInterrupt: pass
