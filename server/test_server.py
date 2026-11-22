#!/usr/bin/env python3
"""Checks the room server against both stores (memory, and DynamoDB through the moto mock).

    pip install boto3 "moto[dynamodb]"      then      python3 server/test_server.py
"""
import json
import os
import sys

os.environ.setdefault("AWS_DEFAULT_REGION", "ap-southeast-2")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lambda_function as room  # noqa: E402

FAILS = []


def check(ok, what):
    print(("ok    " if ok else "FAIL  ") + what)
    if not ok:
        FAILS.append(what)


def scenario(store, label):
    h = lambda q, now=1000: room.handle(q, store, now=now, key="K")  # noqa: E731
    check(h({"op": "create", "k": "X", "pid": "a"})["err"] == "key", label + ": a request with a wrong key is refused")
    check(h({"op": "create", "pid": "a"})["ok"], label + ": a request without a key is accepted (the app meets by passphrase)")
    c = h({"op": "create", "k": "K", "pid": "a", "mode": "test", "st": "S0"})
    code = c["code"]
    check(c["ok"] and c["slot"] == 0 and c["ver"] == 1 and c["st"] == "S0" and c["mode"] == "test" and not c["p1"] and len(code) == 4,
          label + ": create")
    j = h({"op": "join", "k": "K", "code": code, "pid": "b"})
    check(j["ok"] and j["slot"] == 1 and j["p1"], label + ": join takes seat 2")
    check(h({"op": "join", "k": "K", "code": code, "pid": "a"})["slot"] == 0, label + ": the creator rejoins seat 1")
    check(h({"op": "join", "k": "K", "code": code, "pid": "b"})["slot"] == 1, label + ": the partner rejoins seat 2")
    check(h({"op": "join", "k": "K", "code": code, "pid": "c"})["err"] == "full", label + ": a third player is refused")
    check(h({"op": "join", "k": "K", "code": "nope", "pid": "c"})["err"] == "nf", label + ": unknown room")
    c2 = h({"op": "create", "k": "K", "pid": "a", "st": '{"f":{"x":1,"y":4},"i":{"coin":1}}'})
    code2 = c2["code"]
    p = h({"op": "put", "k": "K", "code": code2, "slot": 0, "ver": 1, "r": ["f:x"], "w": {"f:x": 2}})
    check(p["ok"] and p["ver"] == 2 and json.loads(p["st"]) == {"f": {"x": 2, "y": 4}, "i": {"coin": 1}}, label + ": put applies a change")
    other = h({"op": "put", "k": "K", "code": code2, "slot": 1, "ver": 1, "r": ["f:y", "i:coin"], "w": {"f:y": 0, "i:coin": 0, "i:key": 1}})
    check(other["ok"] and other["ver"] == 3 and json.loads(other["st"]) == {"f": {"x": 2}, "i": {"key": 1}},
          label + ": a change that touches other keys goes through although the room moved on")
    stale = h({"op": "put", "k": "K", "code": code2, "slot": 1, "ver": 1, "r": ["f:x"], "w": {"f:z": 9}})
    check(not stale["ok"] and stale["err"] == "ver" and stale["ver"] == 3 and "z" not in stale["st"],
          label + ": a change that read an altered key is refused and gets the newer state")
    stale2 = h({"op": "put", "k": "K", "code": code2, "slot": 1, "ver": 2, "r": [], "w": {"i:key": 2}})
    check(not stale2["ok"] and stale2["err"] == "ver", label + ": a change that overwrites an altered key is refused")
    fresh = h({"op": "put", "k": "K", "code": code2, "slot": 1, "ver": 3, "r": ["f:x"], "w": {"f:z": 9}, "view": "s1v1"})
    check(fresh["ok"] and fresh["ver"] == 4 and fresh["v"][1] == "s1v1", label + ": the same change is accepted from the current version")
    g = h({"op": "get", "k": "K", "code": code, "slot": 1, "view": "s1v2"}, now=1005)
    check(g["ok"] and g["v"] == ["", "s1v2"] and g["s"][1] == 1005 and g["ver"] == 1, label + ": get with a view records where the player is")
    g2 = h({"op": "get", "k": "K", "code": code, "slot": 0})
    check(g2["v"] == ["", "s1v2"] and g2["st"] == "S0", label + ": plain get")
    check(h({"op": "put", "k": "K", "code": code2, "slot": 0, "ver": 4, "r": ["x" * 60], "w": {}})["err"] == "bad"
          and h({"op": "put", "k": "K", "code": code2, "slot": 0, "ver": 4, "w": {"zz": 1}})["err"] == "bad", label + ": malformed changes are refused")
    check(h({"op": "get", "k": "K", "code": "0000x"})["err"] == "nf" and h({"op": "zzz", "k": "K", "code": code})["err"] == "op", label + ": bad requests")
    late = room.ROOM_DAYS * 86400 + 2000
    check(h({"op": "join", "k": "K", "code": code, "pid": "a"}, now=late)["err"] == "nf", label + ": an expired room cannot be joined")
    codes = {h({"op": "create", "k": "K", "pid": "z", "st": ""})["code"] for _ in range(30)}
    check(len(codes) == 30, label + ": room codes do not collide")

    # meet: the same passphrase (code) brings two players into one room
    m = "m" + "0123456789abcdef01234567"
    first = h({"op": "meet", "code": m, "pid": "a", "mode": "main", "st": "M0"})
    check(first["ok"] and first["made"] and first["slot"] == 0 and first["code"] == m and first["st"] == "M0" and not first["p1"],
          label + ": the first player to meet makes the room")
    second = h({"op": "meet", "code": m, "pid": "b", "mode": "main", "st": "OTHER"})
    check(second["ok"] and not second["made"] and second["slot"] == 1 and second["p1"] and second["st"] == "M0",
          label + ": the second player with the same passphrase joins it (and keeps its state)")
    check(h({"op": "meet", "code": m, "pid": "a", "st": "X"})["slot"] == 0 and h({"op": "meet", "code": m, "pid": "b", "st": "X"})["slot"] == 1,
          label + ": both come back to their seats with the same passphrase")
    check(h({"op": "meet", "code": m, "pid": "c", "st": "X"})["err"] == "full", label + ": a third player with the passphrase is refused")
    other = h({"op": "meet", "code": "m" + "f" * 24, "pid": "a", "st": "N"})
    check(other["ok"] and other["made"] and other["code"] != m, label + ": another passphrase makes another room")
    check(h({"op": "meet", "code": "1234", "pid": "a"})["err"] == "bad" and h({"op": "meet", "code": "m12", "pid": "a"})["err"] == "bad",
          label + ": meet does not reach the numbered rooms or short codes")
    check(h({"op": "join", "code": m, "pid": "b"})["slot"] == 1 and h({"op": "get", "code": m, "slot": 1})["ok"],
          label + ": a passphrase room works with join and get like any room")
    check(h({"op": "meet", "code": "m" + "1" * 40, "pid": "a"})["err"] == "nf", label + ": an overlong code is refused")
    again = h({"op": "meet", "code": m, "pid": "b", "st": "FRESH"}, now=late)
    check(again["ok"] and again["made"] and again["slot"] == 0 and again["st"] == "FRESH", label + ": an expired passphrase room is made anew")


class RaceStore(room.MemStore):
    """The partner makes the room between our look and our create."""

    def __init__(self, partner_room):
        super().__init__()
        self.partner_room = partner_room
        self.raced = False

    def create(self, r, now):
        if not self.raced:
            self.raced = True
            self.rooms[self.partner_room["code"]] = dict(self.partner_room)
            return False
        return super().create(r, now)


race_code = "m" + "a" * 24
race = RaceStore(room._new_room(race_code, "partner", "P0", "main", 1000))
r = room.handle({"op": "meet", "code": race_code, "pid": "me", "st": "MINE"}, race, now=1000, key="")
check(r["ok"] and not r["made"] and r["slot"] == 1 and r["st"] == "P0", "meet: two players meeting at once end up in one room")


scenario(room.MemStore(), "memory")
try:
    import boto3
    from moto import mock_aws
except ImportError:
    print("skip  DynamoDB checks (pip install boto3 'moto[dynamodb]')")
else:
    with mock_aws():
        boto3.client("dynamodb").create_table(
            TableName="T", AttributeDefinitions=[{"AttributeName": "code", "AttributeType": "S"}],
            KeySchema=[{"AttributeName": "code", "KeyType": "HASH"}], BillingMode="PROVISIONED",
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5})
        scenario(room.DynamoStore("T"), "dynamodb")
        room._store = room.DynamoStore("T")
        room.KEY = "K"
        ev = {"requestContext": {"http": {"method": "POST"}}, "body": '{"op":"create","k":"K","pid":"a","st":"S"}'}
        r = room.lambda_handler(ev, None)
        check(r["statusCode"] == 200 and '"ok": true' in r["body"], "lambda handler answers a Function URL event")
        check('"name"' in room.lambda_handler({"requestContext": {"http": {"method": "GET"}}}, None)["body"], "lambda handler answers a browser visit")
        get = lambda path: json.loads(room.lambda_handler({"requestContext": {"http": {"method": "GET"}}, "rawPath": path}, None)["body"])
        room.BUILD = {"tree": "abc123", "deployedAt": "2026-11-22T09:00:00Z"}
        check(get("/build.json") == room.BUILD and get("/k/SECRET/build.json") == room.BUILD, "build.json is served at the root and under a key path")
        check("tree" not in get("/") and "tree" not in get("/k/SECRET"), "other paths only show a sign of life")
        check("SECRET" not in json.dumps(get("/k/SECRET")), "a GET never echoes a key")

check(room.info("/build.json?t=1") == room.BUILD and room.info("/x/build.json/") == room.BUILD and room.info(None) == {"ok": True, "name": "exit-interview"},
      "build.json is found with a query string or a trailing slash")

print("ALL OK" if not FAILS else "%d FAILED" % len(FAILS))
sys.exit(1 if FAILS else 0)
