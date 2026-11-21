#!/usr/bin/env python3
"""Publish the news-image-20261120 entry (account 2, Orochim25).

The graded artefact is entry.png, a 1024x1024 PNG that ships next to
this file. Running this script places an exact copy of it at
$MAKEFUN_OUTPUT_DIR/entry.png (default /output). Only the Python
standard library is used. Nothing is written to the current working
directory, and the copy is verified byte-for-byte after writing.
"""
import hashlib
import os
import struct
import sys

NAME = "entry.png"
MAGIC = b"\x89PNG\r\n\x1a\n"
WANT = (1024, 1024)


def here():
    return os.path.dirname(os.path.abspath(__file__))


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def size_of(path):
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != MAGIC or head[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", head[16:24])


def has_iend(path):
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        if f.tell() < 12:
            return False
        f.seek(-12, os.SEEK_END)
        tail = f.read(12)
    return tail[4:8] == b"IEND"


def main():
    src = os.path.join(here(), NAME)
    if not os.path.exists(src):
        print("missing entry image:", src, file=sys.stderr)
        return 1
    dims = size_of(src)
    if dims is None:
        print("not a PNG file:", src, file=sys.stderr)
        return 1
    if dims != WANT:
        print("bad size %sx%s, want %sx%s" % (dims + WANT), file=sys.stderr)
        return 1
    if not has_iend(src):
        print("truncated PNG (no IEND):", src, file=sys.stderr)
        return 1
    want_hash = digest(src)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    dst = os.path.join(outdir, NAME)
    if os.path.abspath(dst) == os.path.abspath(src):
        print("output is the shipped file itself:", dst)
        return 0
    with open(src, "rb") as fin, open(dst, "wb") as fout:
        while True:
            block = fin.read(65536)
            if not block:
                break
            fout.write(block)
    if digest(dst) != want_hash or os.path.getsize(dst) != os.path.getsize(src):
        print("copy failed verification", file=sys.stderr)
        return 1
    print("wrote", dst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
