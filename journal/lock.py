#!/usr/bin/env python3
"""MN. journal lock: the journal text never goes public, only an encrypted copy does.

  python3 journal/lock.py encrypt PATH/TO/journal.txt    writes journal/journal.lock.json
  python3 journal/lock.py decrypt > PATH/TO/journal.txt  gives the text back, to edit it

Both ask for the journal password (or read it from the JOURNAL_PW environment variable).
Spaces around it and capital letters don't matter, the same as on the site.

New entry: decrypt into a file OUTSIDE this folder, add the entry at the top, encrypt that file,
then commit journal.lock.json. Never commit the plain journal.txt (it is in .gitignore).

How it works: AES-256-GCM, the key comes from the password via PBKDF2-SHA256 (600,000 rounds).
The page asks for the password and decrypts in the browser. Only the dates and the entry
numbers stay readable, for the entry counter and the "new" dot in the menu.
Photos for an entry (folder journal/2026-11-20/) are NOT encrypted.

Format of journal.txt (newest at the top):
  20.11.2026 | title
  text ...
  ---
Lines starting with # are notes. A line with HIDDEN hides the commented-out entry right after it
("# 19.11.2026 | title"), but its number still counts, so the other entries keep theirs.
"""
import base64
import datetime
import getpass
import hashlib
import json
import os
import re
import sys

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

HERE = os.path.dirname(os.path.abspath(__file__))
LOCK = os.path.join(HERE, "journal.lock.json")
ITER = 600_000


def b64(b):
    return base64.b64encode(b).decode("ascii")


def unb64(s):
    return base64.b64decode(s)


def password():
    pw = os.environ.get("JOURNAL_PW")
    if pw is None:
        pw = getpass.getpass("journal password: ")
    return pw.strip().lower()


def derive(pw, salt, rounds):
    return hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), salt, rounds, 32)


def parse(text):
    hidden, flag = [], False
    for line in text.splitlines():
        if "HIDDEN" in line:
            flag = True
            continue
        h = re.match(r"^\s*#\s*(\d{1,2})\.(\d{1,2})\.(\d{4})\s*\|", line)
        if h and flag:
            hidden.append(datetime.date(int(h[3]), int(h[2]), int(h[1])).isoformat())
            flag = False
    raw = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))
    out = []
    for block in re.split(r"^\s*-{3,}\s*$", raw, flags=re.M):
        lines = [l.rstrip() for l in block.strip().splitlines()]
        if not lines:
            continue
        m = re.match(r"^\s*(\d{1,2})\.(\d{1,2})\.(\d{4})\s*\|?\s*(.*)$", lines[0])
        if not m:
            continue
        day = datetime.date(int(m[3]), int(m[2]), int(m[1]))
        out.append({"id": day.isoformat(), "date": day.strftime("%d.%m.%y"),
                    "title": m[4].strip() or "journal.", "caption": "\n".join(lines[1:]).strip()})
    out.sort(key=lambda j: j["id"], reverse=True)
    every = sorted([j["id"] for j in out] + hidden)
    for j in out:
        j["n"] = every.index(j["id"]) + 1
    return out


def read_lock():
    with open(LOCK, encoding="utf-8") as f:
        return json.load(f)


def open_lock(lock, pw):
    key = derive(pw, unb64(lock["salt"]), lock["iter"])
    return json.loads(AESGCM(key).decrypt(unb64(lock["iv"]), unb64(lock["data"]), None))


def encrypt(src):
    with open(src, encoding="utf-8-sig") as f:
        text = f.read()
    entries = parse(text)
    pw = password()
    if not pw:
        sys.exit("no password given")
    salt = None
    if os.path.exists(LOCK):
        # same password as before: keep the salt, so everyone who already opened the journal stays in
        old = read_lock()
        try:
            open_lock(old, pw)
            if old.get("iter") == ITER:
                salt = unb64(old["salt"])
        except Exception:
            print("note: this is a new password, everyone has to enter it again", file=sys.stderr)
    salt = salt or os.urandom(16)
    iv = os.urandom(12)
    payload = json.dumps({"source": text, "entries": entries}, ensure_ascii=False).encode("utf-8")
    data = AESGCM(derive(pw, salt, ITER)).encrypt(iv, payload, None)
    lock = {"v": 1, "kdf": "PBKDF2-SHA256", "iter": ITER, "cipher": "AES-256-GCM",
            "salt": b64(salt), "iv": b64(iv), "data": b64(data),
            "entries": [{"id": j["id"], "n": j["n"]} for j in entries]}
    with open(LOCK, "w", encoding="utf-8") as f:
        json.dump(lock, f, indent=1)
        f.write("\n")
    # check that it opens again with the same password
    if open_lock(read_lock(), pw)["source"] != text:
        sys.exit("check failed: the lock does not open again")
    print(f"locked {len(entries)} entries into journal/journal.lock.json", file=sys.stderr)


def decrypt():
    try:
        src = open_lock(read_lock(), password())["source"]
    except Exception:
        sys.exit("wrong password")
    sys.stdout.write(src)


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "encrypt":
        encrypt(sys.argv[2])
    elif len(sys.argv) == 2 and sys.argv[1] == "decrypt":
        decrypt()
    else:
        sys.exit(__doc__)
