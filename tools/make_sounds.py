#!/usr/bin/env python3
"""Synthesises the short sound effects into app/src/main/res/raw (no recordings, no licences)."""
import math
import os
import random
import struct
import wave

RATE = 22050
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app", "src", "main", "res", "raw")
rnd = random.Random(7)


def tone(freq, dur, vol=0.5, shape="sine", decay=4.0, freq_end=None, attack=0.004):
    n = int(RATE * dur)
    out, phase = [], 0.0
    for i in range(n):
        t = i / RATE
        fr = freq if freq_end is None else freq + (freq_end - freq) * (i / n)
        phase += 2 * math.pi * fr / RATE
        v = math.sin(phase)
        if shape == "square":
            v = 0.6 if v > 0 else -0.6
        elif shape == "noise":
            v = rnd.uniform(-1, 1)
        env = min(1.0, t / attack) * math.exp(-decay * t / dur)
        out.append(v * vol * env)
    return out


def mix(*parts):
    n = max(len(p) for p in parts)
    return [sum(p[i] for p in parts if i < len(p)) for i in range(n)]


def seq(*parts):
    out = []
    for p in parts:
        out += p
    return out


def lowpass(x, k):
    out, y = [], 0.0
    for v in x:
        y += (v - y) * k
        out.append(y)
    return out


def save(name, samples):
    os.makedirs(OUT, exist_ok=True)
    with wave.open(os.path.join(OUT, "sfx_%s.wav" % name), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, v)) * 30000)) for v in samples))


save("tick", tone(1100, 0.05, 0.45, decay=6))
save("move", tone(620, 0.07, 0.35, decay=5))
save("pon", tone(520, 0.14, 0.3, decay=4, freq_end=640))
save("ok", seq(tone(660, 0.11, 0.45, decay=2.5), tone(880, 0.11, 0.45, decay=2.5), tone(1320, 0.26, 0.45, decay=4)))
save("buzz", mix(tone(140, 0.32, 0.5, "square", decay=1.2), tone(147, 0.32, 0.3, "square", decay=1.2)))
save("get", seq(tone(880, 0.07, 0.4, decay=2), tone(1320, 0.16, 0.4, decay=4)))
save("door", seq(lowpass(tone(90, 0.12, 0.9, "noise", decay=5), 0.25), tone(300, 0.35, 0.3, decay=3, freq_end=180)))
save("coin", mix(tone(1480, 0.35, 0.35, decay=5), tone(2220, 0.35, 0.25, decay=6)))
save("water", lowpass(tone(0, 0.35, 0.7, "noise", decay=2.5, attack=0.05), 0.35))
save("meow", seq(tone(620, 0.16, 0.4, decay=0.6, freq_end=920), tone(920, 0.3, 0.4, decay=2.5, freq_end=520)))
save("lever", seq(lowpass(tone(0, 0.05, 0.9, "noise", decay=4), 0.3), tone(210, 0.12, 0.5, decay=4)))
save("plop", tone(340, 0.13, 0.5, decay=3, freq_end=140))
save("boing", seq(tone(220, 0.14, 0.45, decay=0.8, freq_end=460), tone(460, 0.2, 0.4, decay=3, freq_end=240)))
save("launch", mix(lowpass(tone(0, 1.3, 0.6, "noise", decay=0.6, attack=0.5), 0.2), tone(110, 1.3, 0.35, decay=0.4, freq_end=880, attack=0.3)))
print("sounds:", sorted(os.listdir(OUT)))
