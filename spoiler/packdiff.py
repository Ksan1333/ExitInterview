#!/usr/bin/env python3
"""Tells whether two stage packs hold the same definitions: everything but the bytes of the pictures.

    python3 spoiler/packdiff.py A.pack B.pack

Pictures drawn by another SVG renderer differ by a few bytes, so a pack rebuilt on another machine is compared by its
definitions and picture names. Exit code 0 when they match. Prints only the names of the parts that differ.
"""
import hashlib
import json
import struct
import sys

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY_TEXT = "exit-interview/kotatsu#2026"  # same as game/core.py


def root_of(path):
    raw = open(path, "rb").read()
    if raw[:4] != b"EIX1":
        sys.exit("%s: not a stage pack" % path)
    plain = AESGCM(hashlib.sha256(KEY_TEXT.encode("utf-8")).digest()).decrypt(raw[4:16], raw[16:], None)
    n = struct.unpack(">I", plain[4:8])[0]
    return json.loads(plain[8:8 + n].decode("utf-8"))


a, b = root_of(sys.argv[1]), root_of(sys.argv[2])
differ = []
for k in sorted(set(a) | set(b)):
    if k == "imgs":
        if sorted(a.get(k, {})) != sorted(b.get(k, {})):
            differ.append("picture names")
    elif json.dumps(a.get(k), ensure_ascii=False) != json.dumps(b.get(k), ensure_ascii=False):
        differ.append(k)
if differ:
    print("different: " + ", ".join(differ))
    sys.exit(1)
