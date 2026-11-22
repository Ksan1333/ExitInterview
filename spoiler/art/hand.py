"""Hand-drawn look: wobbly ink outlines over flat fills, rendered to pictures with rsvg-convert."""
import io
import math
import random
import subprocess

from PIL import Image

W, H = 960, 540
SCALE = 2
FONT = "Yomogi"

INK = "#101316"
BG = "#2e4a49"
WAIN = "#243a3b"
FLOOR = "#3b2d27"
WOOD, WOOD_D, WOOD_L = "#5b4633", "#4b3a2a", "#6a5138"
METAL, METAL_D = "#6d7b7d", "#4a595c"
PAPER, PAPER_L = "#c9c2a8", "#e9e4d2"
BRASS = "#c9a44a"
RED, RED_L = "#8a3b32", "#d0503f"
LIGHT = "#f0d98a"
BLUE, BLUE_L = "#3f6f8f", "#7fb0d0"
GREEN = "#5f8a4a"
PINK = "#e39ab0"
BROWN = "#8a5a2e"
WHITE = "#ecebe4"
BLACK = "#15191b"
ORANGE = "#e08a2e"
TXT = "#e9e4d2"


def f(v):
    s = "%.1f" % v
    if s.endswith(".0"):
        s = s[:-2]
    return "0" if s == "-0" else s


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def smooth_d(pts, closed=False):
    n = len(pts)
    if n < 2:
        return ""

    def P(i):
        return pts[i % n] if closed else pts[max(0, min(n - 1, i))]

    d = "M%s %s" % (f(pts[0][0]), f(pts[0][1]))
    for i in range(n if closed else n - 1):
        p0, p1, p2, p3 = P(i - 1), P(i), P(i + 1), P(i + 2)
        d += "C%s %s %s %s %s %s" % (
            f(p1[0] + (p2[0] - p0[0]) / 6.0), f(p1[1] + (p2[1] - p0[1]) / 6.0),
            f(p2[0] - (p3[0] - p1[0]) / 6.0), f(p2[1] - (p3[1] - p1[1]) / 6.0), f(p2[0]), f(p2[1]))
    return d + ("Z" if closed else "")


def ell_pts(cx, cy, rx, ry, n=24):
    return [(cx + math.cos(2 * math.pi * i / n) * rx, cy + math.sin(2 * math.pi * i / n) * ry) for i in range(n)]


def rect_pts(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def star_pts(cx, cy, r, inner=0.45, n=5, rot=-90):
    pts = []
    for i in range(n * 2):
        a = math.radians(rot + i * 180.0 / n)
        rr = r if i % 2 == 0 else r * inner
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    return pts


class Scene:
    def __init__(self, seed=1, stroke=INK, sw=3.0, rough=1.3, passes=2, opacity=0.95):
        self.r = random.Random(seed)
        self.stroke, self.sw, self.rough, self.passes, self.opacity = stroke, sw, rough, passes, opacity
        self.out = []

    # ---- low level
    def raw(self, s):
        self.out.append(s)

    def _emit(self, d, kw):
        if not d:
            return
        a = 'd="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round" stroke-linejoin="round"' % (
            d, kw.get("stroke", self.stroke), f(kw.get("sw", self.sw)))
        op = kw.get("opacity", self.opacity)
        if op < 1:
            a += ' opacity="%.2f"' % op
        self.out.append("<path %s/>" % a)

    def solid(self, pts, color, opacity=1.0, jit=0.0):
        d = ""
        for i, (x, y) in enumerate(pts):
            d += ("M" if i == 0 else "L") + "%s %s" % (f(x + self.r.uniform(-1, 1) * jit), f(y + self.r.uniform(-1, 1) * jit))
        a = 'd="%sZ" fill="%s"' % (d, color)
        if opacity < 1:
            a += ' opacity="%.2f"' % opacity
        self.out.append("<path %s/>" % a)

    def _line_pts(self, x1, y1, x2, y2, over, rough):
        L = math.hypot(x2 - x1, y2 - y1)
        if L < 0.01:
            return [(x1, y1), (x2, y2)]
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        nx, ny = -uy, ux
        k = min(1.0, L / 40.0)
        n = max(1, int(L / 80))
        r = self.r
        o1, o2 = over * r.uniform(0.2, 1.0), over * r.uniform(0.2, 1.0)
        pts = [(x1 - ux * o1 + r.uniform(-1, 1) * rough * k * 0.7, y1 - uy * o1 + r.uniform(-1, 1) * rough * k * 0.7)]
        bow = r.uniform(-1, 1) * rough * k * 1.2
        for i in range(1, n + 1):
            t = i / (n + 1.0)
            b = math.sin(math.pi * t) * bow + r.uniform(-1, 1) * rough * k * 0.6
            pts.append((x1 + (x2 - x1) * t + nx * b, y1 + (y2 - y1) * t + ny * b))
        pts.append((x2 + ux * o2 + r.uniform(-1, 1) * rough * k * 0.7, y2 + uy * o2 + r.uniform(-1, 1) * rough * k * 0.7))
        return pts

    def _line_d(self, x1, y1, x2, y2, over, kw):
        return "".join(smooth_d(self._line_pts(x1, y1, x2, y2, over, kw.get("rough", self.rough)))
                       for _ in range(kw.get("passes", self.passes)))

    def line(self, x1, y1, x2, y2, over=0.0, **kw):
        self._emit(self._line_d(x1, y1, x2, y2, over, kw), kw)

    def poly(self, pts, closed=True, over=1.5, **kw):
        n = len(pts)
        d = ""
        for i in range(n if closed else n - 1):
            (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
            d += self._line_d(x1, y1, x2, y2, over, kw)
        self._emit(d, kw)

    def rect(self, x, y, w, h, **kw):
        self.poly(rect_pts(x, y, w, h), True, **kw)

    def ellipse(self, cx, cy, rx, ry, **kw):
        rough = kw.get("rough", self.rough)
        r = self.r
        d = ""
        for _ in range(kw.get("passes", self.passes)):
            n = max(8, min(22, int((rx + ry) / 8) + 8))
            a0 = r.uniform(0, 2 * math.pi)
            steps = int(n * (1 + r.uniform(0.03, 0.10))) + 1
            k = min(1.0, (rx + ry) / 40.0)
            pts = []
            for i in range(steps + 1):
                a = a0 + 2 * math.pi * i / n
                jr = 1 + r.uniform(-1, 1) * rough * k * 0.5 / max(rx, ry, 1.0)
                pts.append((cx + math.cos(a) * rx * jr + r.uniform(-1, 1) * rough * k * 0.3,
                            cy + math.sin(a) * ry * jr + r.uniform(-1, 1) * rough * k * 0.3))
            d += smooth_d(pts)
        self._emit(d, kw)

    def curve(self, pts, closed=False, **kw):
        rough = kw.get("rough", self.rough)
        d = ""
        for _ in range(kw.get("passes", self.passes)):
            d += smooth_d([(x + self.r.uniform(-1, 1) * rough * 0.5, y + self.r.uniform(-1, 1) * rough * 0.5) for x, y in pts], closed)
        self._emit(d, kw)

    # ---- flat shapes with an ink outline
    def frect(self, x, y, w, h, color, sw=None, op=1.0, outline=True):
        self.solid(rect_pts(x, y, w, h), color, op, 1.0)
        if outline:
            self.rect(x, y, w, h, **({"sw": sw} if sw else {}))

    def fell(self, cx, cy, rx, ry, color, sw=None, op=1.0, outline=True):
        self.solid(ell_pts(cx, cy, rx, ry), color, op, 0.5)
        if outline:
            self.ellipse(cx, cy, rx, ry, **({"sw": sw} if sw else {}))

    def fpoly(self, pts, color, sw=None, op=1.0, outline=True):
        self.solid(pts, color, op, 0.8)
        if outline:
            self.poly(pts, True, **({"sw": sw} if sw else {}))

    def dot(self, cx, cy, r, color=INK):
        self.solid(ell_pts(cx, cy, r, r, 12), color, 1.0, min(0.5, r * 0.12))

    def glow(self, cx, cy, r, color=LIGHT, strength=0.10, rings=5):
        for i in range(rings, 0, -1):
            self.solid(ell_pts(cx, cy, r * i / rings, r * i / rings), color, strength)

    # ---- text (Yomogi). (x, y) is the centre of the line unless anchor says otherwise.
    def text(self, x, y, t, size=20, color=INK, anchor="middle", rot=0.0, op=1.0):
        a = 'x="%s" y="%s" font-family="%s" font-size="%s" fill="%s" text-anchor="%s"' % (
            f(x), f(y + size * 0.35), FONT, f(size), color, anchor)
        if rot:
            a += ' transform="rotate(%s %s %s)"' % (f(rot), f(x), f(y))
        if op < 1:
            a += ' opacity="%.2f"' % op
        self.out.append("<text %s>%s</text>" % (a, esc(t)))

    def paper(self, x, y, w, h, lines, size=18, color=PAPER, rot=0.0, gap=1.35, align="left", pin=True, pad=12, ink=INK):
        """A sheet of paper with handwritten lines."""
        if rot:
            self.raw('<g transform="rotate(%s %s %s)">' % (f(rot), f(x + w / 2), f(y + h / 2)))
        self.frect(x, y, w, h, color, sw=2.2)
        if pin:
            self.dot(x + w / 2, y + 7, 3.2, RED)
        ty = y + pad + size * 0.6 + (8 if pin else 0)
        for ln in lines:
            sz = size
            if isinstance(ln, tuple):
                ln, sz = ln
            if align == "left":
                self.text(x + pad, ty, ln, sz, ink, "start")
            else:
                self.text(x + w / 2, ty, ln, sz, ink, "middle")
            ty += sz * gap
        if rot:
            self.raw("</g>")

    def sym(self, kind, cx, cy, r, color=INK, sw=3.0, fill=None):
        """Marks used on buttons and notes: o, tri, sq, star, dia, x."""
        if kind == "o":
            pts = ell_pts(cx, cy, r, r, 20)
        elif kind == "tri":
            pts = [(cx, cy - r), (cx + r * 0.95, cy + r * 0.8), (cx - r * 0.95, cy + r * 0.8)]
        elif kind == "sq":
            pts = rect_pts(cx - r * 0.85, cy - r * 0.85, r * 1.7, r * 1.7)
        elif kind == "star":
            pts = star_pts(cx, cy, r * 1.1)
        elif kind == "dia":
            pts = [(cx, cy - r), (cx + r * 0.8, cy), (cx, cy + r), (cx - r * 0.8, cy)]
        else:
            self.line(cx - r, cy - r, cx + r, cy + r, stroke=color, sw=sw)
            self.line(cx + r, cy - r, cx - r, cy + r, stroke=color, sw=sw)
            return
        if fill:
            self.solid(pts, fill)
        if kind == "o":
            self.ellipse(cx, cy, r, r, stroke=color, sw=sw)
        else:
            self.poly(pts, True, 1.0, stroke=color, sw=sw)

    def room(self, wall=BG, floor_y=400, floor=FLOOR, wain=WAIN, wain_h=90, planks=True):
        """Back wall, wainscot and floor."""
        self.solid(rect_pts(0, 0, W, floor_y), wall)
        if wain:
            self.solid(rect_pts(0, floor_y - wain_h, W, wain_h), wain)
            self.line(0, floor_y - wain_h, W, floor_y - wain_h)
        self.solid(rect_pts(0, floor_y, W, H - floor_y), floor)
        self.line(0, floor_y, W, floor_y)
        if planks:
            for x in range(60, W, 120):
                self.line(x, floor_y + 3, W / 2 + (x - W / 2) * 1.4, H, sw=1.8, opacity=0.5, passes=1)

    def vignette(self, strength=0.17):
        for rx, ry in ((640, 370), (560, 320)):
            hole = "".join(("M" if i == 0 else "L") + "%s %s" % (f(x), f(y))
                           for i, (x, y) in enumerate(ell_pts(W / 2, H / 2, rx, ry, 40))) + "Z"
            self.raw('<path d="M0 0H%dV%dH0Z%s" fill="#05080a" fill-rule="evenodd" opacity="%.2f"/>' % (W, H, hole, strength))


def svg_doc(elems, x=0, y=0, w=W, h=H, bg=None, scale=SCALE):
    head = '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="%s %s %s %s">' % (
        round(w * scale), round(h * scale), f(x), f(y), f(w), f(h))
    back = '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (f(x), f(y), f(w), f(h), bg) if bg else ""
    return head + back + "".join(elems) + "</svg>"


def render(elems, x=0, y=0, w=W, h=H, bg=None, scale=SCALE):
    """Returns a PIL image of the given region."""
    p = subprocess.run(["rsvg-convert", "-f", "png"], input=svg_doc(elems, x, y, w, h, bg, scale).encode("utf-8"),
                       capture_output=True, check=True)
    return Image.open(io.BytesIO(p.stdout))


def webp(im, quality=84):
    buf = io.BytesIO()
    if im.mode == "RGBA" and im.getextrema()[3][0] == 255:
        im = im.convert("RGB")
    im.save(buf, "WEBP", quality=quality, method=6)
    return buf.getvalue()
