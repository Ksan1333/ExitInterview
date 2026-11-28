"""Collects views, items and puzzles, renders the pictures and writes the encrypted stage pack."""
import hashlib
import json
import os
import struct
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from art.hand import *  # noqa: E402,F401,F403
from art import hand  # noqa: E402

VIEWS = {}
ITEMS = {}
SPRITES = {}
PUZZLES = []
MAZES = {}
STAGES = {}
INIT = {"f": {}, "i": {}}
START = {"main": 1, "test": 9}
META = {}  # episode 2 on: {"title": ..., "tagline": ...} for the title screen
ASKS = {}  # episode 2 on: questions answered by typing
COMBOS = []  # episode 2 on: two held things that go together
KEY_TEXT = "exit-interview/kotatsu#2026"


def _seed(name):
    return int(hashlib.md5(name.encode("utf-8")).hexdigest()[:8], 16)


class View:
    def __init__(self, vid, stage, name, l=None, r=None, back=None, when=None):
        self.id, self.st, self.name = vid, stage, name
        self.l, self.r, self.back, self.when = l, r, back, when
        self.s = Scene(_seed(vid))
        self.variants = {}
        self.order = []
        self.texts = []
        self.spots = []
        VIEWS[vid] = self

    def variant(self, name, rect, when, draw, deps=(), layer=True):
        """A patch drawn over the base picture while `when` holds."""
        s = Scene(_seed(self.id + "." + name))
        draw(s)
        self.variants[name] = dict(rect=tuple(rect), when=when, out=s.out, deps=tuple(deps))
        if layer:
            self.order.append(("img", name))
        return name

    def anim(self, names, rect, when, ms):
        self.order.append(("anim", list(names), tuple(rect), when, ms))

    def sprite(self, img, w, h, flag, positions, when=None):
        self.order.append(("sprite", img, w, h, flag, positions, when))

    def spot(self, rect, ops, when=None, swipe=None):
        """A place that reacts to a tap, or with swipe (0 up, 1 right, 2 down, 3 left, 4 any: rubbing) only to a
        finger drawn across it."""
        d = dict(r=[round(v, 1) for v in rect], ops=ops)
        if when is not None:
            d["when"] = when
        if swipe is not None:
            d["sw"] = swipe
        self.spots.append(d)

    def text(self, x, y, size, flag, kind="num", color=INK, map=None, when=None):
        d = dict(p=[x, y], sz=size, c=color, f=flag, k=kind)
        if map:
            d["m"] = map
        if when is not None:
            d["when"] = when
        self.texts.append(d)


def item(iid, draw, name=None, desc=None, zoom=None, back=None, zsize=(480, 360)):
    """A thing to hold; draw paints it in a 96x96 box. Episode 2 on: a name and lines of text shown when it is picked,
    zoom (drawn in a zsize box) shown when it is looked at closely, and back, its other side (also zsize). A named
    thing without zoom is shown large from its own drawing."""
    ITEMS[iid] = dict(draw=draw, name=name, desc=list(desc or []), zoom=zoom, back=back, zsize=tuple(zsize))


def ask(aid, prompt, answers, ok, ng=None, when=None):
    """A question answered by typing. Open it with ["ask", aid]. when must stop holding once it is answered."""
    if when is None:
        raise ValueError("ask %s needs a when that closes it once answered" % aid)
    ASKS[aid] = dict(q=prompt, ans=list(answers), when=when, ok=ok,
                     ng=ng if ng is not None else [["sfx", "buzz"], ["shake"], ["msg", "ちがうみたい"]])


def combo(a, b, ops, when=None):
    """Picking a and tapping b (or the other way round) runs ops."""
    d = dict(a=a, b=b, ops=ops)
    if when is not None:
        d["when"] = when
    COMBOS.append(d)


def sprite(sid, w, h, draw):
    SPRITES[sid] = (w, h, draw)


def puzzle(pid, stage, name, avail, done, hints, ans, skip):
    PUZZLES.append(dict(id=pid, st=stage, name=name, avail=avail, done=done, hints=hints, ans=ans, skip=skip))


def all_(*c):
    return ["all"] + list(c)


def eq(flag, v):
    return ["eq", flag, v]


def seq_dots(v, buf, n, xs, y, when=None, deps=(), r=7):
    """Small lamps that light up as a sequence is being entered."""
    for k in range(1, n + 1):
        cx = xs[k - 1]

        def draw(s, cx=cx):
            s.glow(cx, y, r * 2.2, LIGHT, 0.12)
            s.fell(cx, y, r, r, LIGHT, sw=1.8)

        cond = ["ge", buf + "_n", k]
        v.variant("%s_d%d" % (buf, k), (cx - r * 2.4, y - r * 2.4, r * 4.8, r * 4.8),
                  all_(when, cond) if when is not None else cond, draw, deps)


# ---------------------------------------------------------------- checks

def _walk_cond(c, flags, items_used):
    if not isinstance(c, list) or not c:
        return
    op = c[0]
    if op in ("eq", "ne", "ge", "le", "gt", "lt", "cool", "within"):
        flags.add(c[1])
    elif op in ("has", "sel"):
        items_used.add(c[1])
    elif op in ("all", "any", "not"):
        for x in c[1:]:
            _walk_cond(x, flags, items_used)
    else:
        raise ValueError("unknown condition %r" % (c,))


def _walk_ops(ops, set_flags, used_flags, items_used, views_used):
    for o in ops:
        op = o[0]
        if op in ("set", "add", "cyc", "cool"):
            set_flags.add(o[1])
        elif op in ("give", "take", "takeall"):
            items_used.add(o[1])
        elif op == "givef":
            items_used.add(o[1])
            used_flags.add(o[2])
        elif op == "go":
            views_used.add(o[1])
        elif op == "if":
            _walk_cond(o[1], used_flags, items_used)
            _walk_ops(o[2], set_flags, used_flags, items_used, views_used)
            if len(o) > 3:
                _walk_ops(o[3], set_flags, used_flags, items_used, views_used)
        elif op == "seq":
            set_flags.add(o[1])
            set_flags.add(o[1] + "_n")
            _walk_ops(o[5], set_flags, used_flags, items_used, views_used)
            _walk_ops(o[6], set_flags, used_flags, items_used, views_used)
        elif op == "maze":
            if o[1] not in MAZES:
                raise ValueError("unknown maze " + o[1])
            set_flags.add(MAZES[o[1]]["pos"])
        elif op == "stage":
            if str(o[1]) not in STAGES:
                raise ValueError("unknown stage %r" % o[1])
        elif op in ("sfx", "shake", "unsel"):
            pass
        elif op == "msg":
            if not isinstance(o[1], str) or not o[1]:
                raise ValueError("msg needs a line: %r" % (o,))
        elif op == "ask":
            if o[1] not in ASKS:
                raise ValueError("unknown ask %r" % (o[1],))
        else:
            raise ValueError("unknown op %r" % (o,))


SFX = {"tick", "ok", "buzz", "get", "door", "move", "coin", "water", "meow", "lever", "plop", "boing", "launch"}


def check():
    set_flags, used_flags, items_used, views_used = set(INIT["f"]), set(), set(), set()
    set_flags |= {"stage", "t0", "t1", "n_hint", "n_skip"}
    for m in MAZES.values():
        _walk_ops(m["ok"], set_flags, used_flags, items_used, views_used)
    for v in VIEWS.values():
        for t in (v.l, v.r, v.back):
            if t:
                views_used.add(t)
        _walk_cond(v.when, used_flags, items_used)
        for var in v.variants.values():
            _walk_cond(var["when"], used_flags, items_used)
            for d in var["deps"]:
                if d not in v.variants:
                    raise ValueError("%s: unknown dep %s" % (v.id, d))
        for e in v.order:
            if e[0] == "anim":
                _walk_cond(e[3], used_flags, items_used)
            if e[0] == "sprite":
                used_flags.add(e[4])
                _walk_cond(e[6], used_flags, items_used)
                if e[1] not in SPRITES:
                    raise ValueError("unknown sprite " + e[1])
        for t in v.texts:
            used_flags.add(t["f"])
            _walk_cond(t.get("when"), used_flags, items_used)
        for sp in v.spots:
            _walk_cond(sp.get("when"), used_flags, items_used)
            _walk_ops(sp["ops"], set_flags, used_flags, items_used, views_used)
            x, y, w, h = sp["r"]
            if w <= 0 or h <= 0 or x < 0 or y < 0 or x + w > W or y + h > H:
                raise ValueError("%s: spot out of range %r" % (v.id, sp["r"]))
    for p in PUZZLES:
        _walk_cond(p["avail"], used_flags, items_used)
        _walk_cond(p["done"], used_flags, items_used)
        _walk_ops(p["skip"], set_flags, used_flags, items_used, views_used)
        if len(p["hints"]) != 3:
            raise ValueError("puzzle %s needs 3 hints" % p["id"])
    for q in ASKS.values():
        _walk_cond(q["when"], used_flags, items_used)
        _walk_ops(q["ok"], set_flags, used_flags, items_used, views_used)
        _walk_ops(q["ng"], set_flags, used_flags, items_used, views_used)
        if not q["ans"]:
            raise ValueError("an ask needs an answer")
    for c in COMBOS:
        items_used.add(c["a"])
        items_used.add(c["b"])
        _walk_cond(c.get("when"), used_flags, items_used)
        _walk_ops(c["ops"], set_flags, used_flags, items_used, views_used)
    for v in VIEWS.values():
        for sp in v.spots:
            if sp.get("sw") not in (None, 0, 1, 2, 3, 4):
                raise ValueError("%s: bad swipe %r" % (v.id, sp.get("sw")))
    for st in STAGES.values():
        if st.get("start"):
            views_used.add(st["start"])
    bad = [v for v in views_used if v not in VIEWS]
    if bad:
        raise ValueError("unknown views: %s" % bad)
    bad = [i for i in items_used if i not in ITEMS]
    if bad:
        raise ValueError("unknown items: %s" % bad)
    never_set = sorted(f for f in used_flags if f not in set_flags and not f.startswith("h_"))
    if never_set:
        raise ValueError("flags read but never set: %s" % never_set)
    for o in _flat_ops(_all_ops()):
        if o[0] == "sfx" and o[1] not in SFX:
            raise ValueError("unknown sfx " + o[1])


def _all_ops():
    """Every op list of the episode, as one list."""
    out = []
    for v in VIEWS.values():
        for sp in v.spots:
            out += sp["ops"]
    for m in MAZES.values():
        out += m["ok"]
    for p in PUZZLES:
        out += p["skip"]
    for q in ASKS.values():
        out += q["ok"] + q["ng"]
    for c in COMBOS:
        out += c["ops"]
    return out


def _flat_ops(ops):
    for o in ops:
        yield o
        if o[0] == "if":
            yield from _flat_ops(o[2])
            if len(o) > 3:
                yield from _flat_ops(o[3])
        elif o[0] == "seq":
            yield from _flat_ops(o[5])
            yield from _flat_ops(o[6])


# ---------------------------------------------------------------- build

def _sheet(v, base_im, layers, preview_dir):
    """Review picture: left = base, right = every layer on, with tap areas outlined."""
    from PIL import Image, ImageDraw, ImageFont
    full = base_im.convert("RGB").resize((W, H))
    on = full.copy()
    for d in layers:
        iid = d.get("i") or d["fr"][0]
        pim = Image.open(os.path.join(preview_dir, iid + ".png")) if os.path.exists(os.path.join(preview_dir, iid + ".png")) else None
        x, y, w, h = d["r"]
        if "ps" in d:
            x, y = d["ps"][0]
            w, h, draw = SPRITES[iid[3:]]
            sc = Scene(_seed(iid))
            draw(sc)
            pim = hand.render(sc.out, 0, 0, w, h, scale=1)
            on.paste(pim, (int(x), int(y)), pim)
            continue
        if pim is not None:
            on.paste(pim.convert("RGB").resize((int(round(w)), int(round(h)))), (int(round(x)), int(round(y))))
    dr = ImageDraw.Draw(on)
    for t in v.texts:
        font = ImageFont.truetype(hand.FONT_FILE, int(t["sz"]))
        dr.text((t["p"][0], t["p"][1]), "8", font=font, fill=t["c"], anchor="mm")
    for sp in v.spots:
        x, y, w, h = sp["r"]
        dr.rectangle([x, y, x + w, y + h], outline=(255, 80, 200), width=1)
    out = Image.new("RGB", (W * 2 + 6, H), (255, 255, 255))
    out.paste(full, (0, 0))
    out.paste(on, (W + 6, 0))
    out.resize((W + 3, H // 2)).save(os.path.join(preview_dir, "_sheet_" + v.id + ".png"))
    out.save(os.path.join(preview_dir, "_sheetbig_" + v.id + ".png"))


def check_font():
    """Every letter that is drawn or shown must exist in the handwriting font."""
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        print("note: fontTools is missing, letters were not checked against the font")
        return
    if hand.renderer() == "rsvg":
        path = subprocess.run(["fc-match", "-f", "%{file}", hand.FONT], capture_output=True, text=True).stdout
        if hand.FONT.lower() not in os.path.basename(path).lower():
            raise ValueError("font %s is not installed (fc-match gave %s)" % (hand.FONT, path))
    else:
        path = hand.FONT_FILE  # resvg is given the app's own font file
    cmap = TTFont(path).getBestCmap()
    texts = list(hand.TEXT_LOG) + [v.name for v in VIEWS.values()]
    for p in PUZZLES:
        texts += [p["name"], p["ans"]] + p["hints"]
    for st in STAGES.values():
        texts += st.get("cap", []) + st.get("credits", []) + st.get("letter", [])
    for it in ITEMS.values():
        texts += [it["name"] or ""] + it["desc"]
    for q in ASKS.values():
        texts.append(q["q"])
    texts += [o[1] for o in _flat_ops(_all_ops()) if o[0] == "msg"]
    texts += [str(v) for v in META.values()]
    missing = sorted({c for t in texts for c in t if ord(c) > 32 and c != "\u3000" and ord(c) not in cmap})
    if missing:
        raise ValueError("letters missing from the font: %s" % "".join(missing))


def build(pack_path, preview_dir=None, quiet=False):
    check()
    check_font()
    imgs = {}
    views = {}
    for v in VIEWS.values():
        base = v.s.out
        im = hand.render(base, bg=BG)
        imgs[v.id] = hand.webp(im, 82)
        if preview_dir:
            im.convert("RGB").resize((W, H)).save(os.path.join(preview_dir, v.id + ".png"))

        def elems(name):
            var = v.variants[name]
            out = list(base)
            for d in var["deps"]:
                out += v.variants[d]["out"]
            return out + var["out"]

        def patch(name):
            iid = "%s.%s" % (v.id, name)
            if iid not in imgs:
                x, y, w, h = v.variants[name]["rect"]
                pim = hand.render(elems(name), x, y, w, h, bg=BG)
                imgs[iid] = hand.webp(pim, 86)
                if preview_dir:
                    pim.convert("RGB").save(os.path.join(preview_dir, iid + ".png"))
            return iid

        layers = []
        for e in v.order:
            if e[0] == "img":
                var = v.variants[e[1]]
                d = dict(i=patch(e[1]), r=[round(c, 1) for c in var["rect"]])
                if var["when"] is not None:
                    d["when"] = var["when"]
                layers.append(d)
            elif e[0] == "anim":
                d = dict(fr=[patch(n) for n in e[1]], ms=e[4], r=list(e[2]))
                if e[3] is not None:
                    d["when"] = e[3]
                layers.append(d)
            else:
                _, sid, w, h, flag, positions, when = e
                d = dict(i="sp." + sid, r=[0, 0, w, h], pf=flag, ps=[[round(a, 1), round(b, 1)] for a, b in positions])
                if when is not None:
                    d["when"] = when
                layers.append(d)
        if preview_dir:
            _sheet(v, im, layers, preview_dir)
        vd = dict(st=v.st, bg=v.id, name=v.name, layers=layers, texts=v.texts, spots=v.spots)
        for k, val in (("l", v.l), ("r", v.r), ("back", v.back), ("when", v.when)):
            if val is not None:
                vd[k] = val
        views[v.id] = vd
        if not quiet:
            print("view %-10s layers %2d spots %2d" % (v.id, len(layers), len(v.spots)))

    for sid, (w, h, draw) in SPRITES.items():
        s = Scene(_seed("sp." + sid))
        draw(s)
        im = hand.render(s.out, 0, 0, w, h)
        imgs["sp." + sid] = hand.webp(im, 90)
        if preview_dir:
            im.save(os.path.join(preview_dir, "sp." + sid + ".png"))
    items = {}
    for iid, it in ITEMS.items():
        s = Scene(_seed("it." + iid))
        it["draw"](s)
        im = hand.render(s.out, 0, 0, 96, 96)
        imgs["it." + iid] = hand.webp(im, 90)
        items[iid] = dict(img="it." + iid)
        if preview_dir:
            im.save(os.path.join(preview_dir, "it." + iid + ".png"))
        if it["name"]:
            items[iid]["name"] = it["name"]
            if it["desc"]:
                items[iid]["desc"] = it["desc"]
            zw, zh = it["zsize"]
            if it["zoom"] is not None:
                z = Scene(_seed("itz." + iid))
                it["zoom"](z)
                zim = hand.render(z.out, 0, 0, zw, zh)
            else:
                z = Scene(_seed("it." + iid))
                it["draw"](z)
                zim = hand.render(z.out, 0, 0, 96, 96, scale=5)
            imgs["itz." + iid] = hand.webp(zim, 88)
            items[iid]["big"] = "itz." + iid
            if preview_dir:
                zim.save(os.path.join(preview_dir, "itz." + iid + ".png"))
            if it["back"] is not None:
                b = Scene(_seed("itb." + iid))
                it["back"](b)
                bim = hand.render(b.out, 0, 0, zw, zh)
                imgs["itb." + iid] = hand.webp(bim, 88)
                items[iid]["back"] = "itb." + iid
                if preview_dir:
                    bim.save(os.path.join(preview_dir, "itb." + iid + ".png"))
        elif it["desc"] or it["zoom"] is not None or it["back"] is not None:
            raise ValueError("item %s: a text or a large picture needs a name" % iid)

    index, blobs, off = {}, [], 0
    for iid, data in imgs.items():
        index[iid] = [off, len(data)]
        blobs.append(data)
        off += len(data)
    root = dict(v=1, start=START, stages=STAGES, views=views, items=items, puzzles=PUZZLES, mazes=MAZES, init=INIT, imgs=index)
    # only episode 2 on has these, so that the first pack builds exactly as before
    for k, val in (("asks", ASKS), ("combos", COMBOS), ("meta", META)):
        if val:
            root[k] = val
    js = json.dumps(root, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    plain = b"EIP1" + struct.pack(">I", len(js)) + js + b"".join(blobs)

    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    key = hashlib.sha256(KEY_TEXT.encode("utf-8")).digest()
    nonce = hashlib.sha256(plain).digest()[:12]
    data = b"EIX1" + nonce + AESGCM(key).encrypt(nonce, plain, None)
    os.makedirs(os.path.dirname(pack_path), exist_ok=True)
    with open(pack_path, "wb") as fh:
        fh.write(data)
    if not quiet:
        print("pack: %d views, %d pictures, %.1f MB -> %s" % (len(views), len(imgs), len(data) / 1e6, pack_path))
    return root
