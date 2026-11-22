"""Room server for Exit Interview.

One record per room. The game rules live in the apps; the server keeps the room's flags and items,
hands them out, and applies a change only if nothing that change depended on was altered by the
partner in the meantime (each key remembers the room version that last changed it).
Runs on AWS Lambda (Function URL + DynamoDB) and, through local_server.py, on any computer.
"""
import base64
import json
import os
import random
import time

KEY = os.environ.get("EI_KEY", "")
TABLE = os.environ.get("EI_TABLE", "ExitInterviewRooms")
ROOM_DAYS = 30
MAX_STATE = 60000


def _build():
    """What a deploy wrote beside this file: which commit's server folder is running, and since when."""
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build.json"), encoding="utf-8") as fh:
            found = json.load(fh)
        return found if isinstance(found, dict) else {}
    except (OSError, ValueError):
        return {}


BUILD = _build()


def info(path):
    """The answer to a GET: build.json (read by KsanHub to tell whether the deploy is current) or a sign of life."""
    if (path or "").split("?")[0].rstrip("/").endswith("/build.json"):
        return BUILD
    return {"ok": True, "name": "exit-interview"}


class MemStore:
    """Rooms kept in memory (local server and tests)."""

    def __init__(self):
        self.rooms = {}

    def get(self, code, consistent=False):
        room = self.rooms.get(code)
        return dict(room) if room else None

    def create(self, room, now):
        old = self.rooms.get(room["code"])
        if old and old["exp"] > now:
            return False
        self.rooms[room["code"]] = dict(room)
        return True

    def update(self, code, sets, expect_ver=None):
        room = self.rooms.get(code)
        if room is None or (expect_ver is not None and room["ver"] != expect_ver):
            return None
        room.update(sets)
        return dict(room)


class DynamoStore:
    """Rooms kept in a DynamoDB table whose key is `code`."""

    def __init__(self, table):
        import boto3
        self.table = boto3.resource("dynamodb").Table(table)

    @staticmethod
    def _plain(item):
        if item is None:
            return None
        return {k: (int(v) if not isinstance(v, (str, bool)) else v) for k, v in item.items()}

    @staticmethod
    def _failed(err):
        return getattr(err, "response", {}).get("Error", {}).get("Code") == "ConditionalCheckFailedException"

    def get(self, code, consistent=False):
        return self._plain(self.table.get_item(Key={"code": code}, ConsistentRead=consistent).get("Item"))

    def create(self, room, now):
        try:
            self.table.put_item(Item=room, ConditionExpression="attribute_not_exists(#c) OR #e < :now",
                                ExpressionAttributeNames={"#c": "code", "#e": "exp"}, ExpressionAttributeValues={":now": now})
            return True
        except Exception as err:  # noqa: BLE001
            if self._failed(err):
                return False
            raise

    def update(self, code, sets, expect_ver=None):
        names, values, parts = {"#c": "code"}, {}, []
        for i, (k, v) in enumerate(sets.items()):
            names["#a%d" % i] = k
            values[":v%d" % i] = v
            parts.append("#a%d = :v%d" % (i, i))
        cond = "attribute_exists(#c)"
        if expect_ver is not None:
            names["#ver"] = "ver"
            values[":ev"] = expect_ver
            cond += " AND #ver = :ev"
        try:
            r = self.table.update_item(Key={"code": code}, UpdateExpression="SET " + ", ".join(parts), ConditionExpression=cond,
                                       ExpressionAttributeNames=names, ExpressionAttributeValues=values, ReturnValues="ALL_NEW")
            return self._plain(r["Attributes"])
        except Exception as err:  # noqa: BLE001
            if self._failed(err):
                return None
            raise


def _reply(room, ok, err, slot, now):
    return {"ok": ok, "err": err, "code": room["code"], "slot": slot, "ver": room["ver"], "st": room["st"],
            "v": [room["v0"], room["v1"]], "s": [room["s0"], room["s1"]], "p1": bool(room["p1"]), "mode": room["mode"], "now": now}


def _fail(err, now):
    return {"ok": False, "err": err, "now": now}


def handle(q, store, now=None, key=None):
    """Answers one request (a dict) with a dict."""
    now = int(time.time() if now is None else now)
    key = KEY if key is None else key
    if not isinstance(q, dict):
        return _fail("bad", now)
    if key and q.get("k") != key:
        return _fail("key", now)
    op = q.get("op")
    st = q.get("st")
    if st is not None and (not isinstance(st, str) or len(st) > MAX_STATE):
        return _fail("big", now)
    view = q.get("view")
    if view is not None and (not isinstance(view, str) or len(view) > 32):
        return _fail("bad", now)

    if op == "create":
        pid = str(q.get("pid") or "")[:64]
        for _ in range(60):
            room = {"code": "%04d" % random.randrange(10000), "ver": 1, "st": st or "", "mod": "{}", "mode": str(q.get("mode") or "main")[:8],
                    "p0": pid, "p1": "", "v0": "", "v1": "", "s0": now, "s1": 0, "exp": now + ROOM_DAYS * 86400}
            if store.create(room, now):
                return _reply(room, True, None, 0, now)
        return _fail("busy", now)

    code = q.get("code")
    if not isinstance(code, str) or not (1 <= len(code) <= 8):
        return _fail("nf", now)
    slot = 1 if q.get("slot") == 1 else 0

    if op == "join":
        pid = str(q.get("pid") or "")[:64]
        room = store.get(code, True)
        if room is None or room["exp"] <= now:
            return _fail("nf", now)
        if pid == room["p0"]:
            slot = 0
        elif not room["p1"] or room["p1"] == pid:
            slot = 1
        else:
            return _fail("full", now)
        sets = {"s%d" % slot: now}
        if slot == 1:
            sets["p1"] = pid
        room = store.update(code, sets) or room
        return _reply(room, True, None, slot, now)

    if op == "get":
        if view is not None:
            room = store.update(code, {"v%d" % slot: view, "s%d" % slot: now})
        else:
            room = store.get(code)
        if room is None:
            return _fail("nf", now)
        return _reply(room, True, None, slot, now)

    if op == "put":
        base, reads, writes = q.get("ver"), q.get("r") or [], q.get("w") or {}
        if (not isinstance(base, int) or not isinstance(reads, list) or not isinstance(writes, dict)
                or len(reads) > 600 or len(writes) > 300
                or not all(isinstance(k, str) and len(k) <= 48 for k in list(reads) + list(writes))
                or not all(isinstance(v, int) and not isinstance(v, bool) for v in writes.values())
                or not all(k[:2] in ("f:", "i:") for k in writes)):
            return _fail("bad", now)
        for _ in range(8):
            room = store.get(code, True)
            if room is None or room["exp"] <= now:
                return _fail("nf", now)
            mod = json.loads(room.get("mod") or "{}")
            if any(mod.get(k, 0) > base for k in list(reads) + list(writes)):
                return _reply(room, False, "ver", slot, now)
            sets = {}
            if view is not None:
                sets["v%d" % slot] = view
                sets["s%d" % slot] = now
            if writes:
                state = json.loads(room["st"] or "{}")
                state.setdefault("f", {})
                state.setdefault("i", {})
                ver = room["ver"] + 1
                for k, v in writes.items():
                    part = state["i"] if k[0] == "i" else state["f"]
                    if v == 0:
                        part.pop(k[2:], None)
                    else:
                        part[k[2:]] = v
                    mod[k] = ver
                st = json.dumps(state, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
                if len(st) > MAX_STATE:
                    return _fail("big", now)
                sets.update(st=st, mod=json.dumps(mod, separators=(",", ":")), ver=ver)
            if not sets:
                return _reply(room, True, None, slot, now)
            done = store.update(code, sets, expect_ver=room["ver"])
            if done is not None:
                return _reply(done, True, None, slot, now)
        return _fail("busy", now)

    return _fail("op", now)


_store = None


def lambda_handler(event, context):
    global _store
    method = (event.get("requestContext", {}).get("http", {}) or {}).get("method", "POST")
    if method != "POST":
        body = info(event.get("rawPath"))
    else:
        raw = event.get("body") or "{}"
        if event.get("isBase64Encoded"):
            raw = base64.b64decode(raw).decode("utf-8")
        try:
            q = json.loads(raw)
        except ValueError:
            q = None
        if _store is None:
            _store = DynamoStore(TABLE)
        body = handle(q, _store)
    return {"statusCode": 200, "headers": {"content-type": "application/json", "cache-control": "no-store"},
            "body": json.dumps(body, ensure_ascii=False)}
