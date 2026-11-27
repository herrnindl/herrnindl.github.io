#!/usr/bin/env python3
"""red. lock: the red. chapter page stays secret until it goes public, only an encrypted copy is online.

  python3 red/lock.py encrypt PATH/TO/red.src.html    writes red/red.lock.json
  python3 red/lock.py decrypt > PATH/TO/red.src.html  gives the page back, to edit it

Both ask for the red. password (or read it from the RED_PW environment variable).
Spaces around it and capital letters don't matter, the same as on the page.
Keep red.src.html OUTSIDE this folder (red/*.html is in .gitignore anyway).

How it works: the same as the journal, AES-256-GCM with a key from the password
(PBKDF2-SHA256, 600,000 rounds). red.html asks for the password and decrypts in the browser.
"""
import base64
import getpass
import hashlib
import json
import os
import sys

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

HERE = os.path.dirname(os.path.abspath(__file__))
LOCK = os.path.join(HERE, "red.lock.json")
ITER = 600_000


def password():
    pw = os.environ.get("RED_PW")
    if pw is None:
        pw = getpass.getpass("red. password: ")
    return pw.strip().lower()


def derive(pw, salt, rounds):
    return hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), salt, rounds, 32)


def encrypt(path):
    with open(path, encoding="utf-8") as f:
        html = f.read()
    salt, iv = os.urandom(16), os.urandom(12)
    data = AESGCM(derive(password(), salt, ITER)).encrypt(iv, html.encode("utf-8"), None)
    with open(LOCK, "w") as f:
        json.dump({"salt": base64.b64encode(salt).decode(), "iv": base64.b64encode(iv).decode(),
                   "iter": ITER, "data": base64.b64encode(data).decode()}, f)
    print("wrote", LOCK)


def decrypt():
    with open(LOCK) as f:
        L = json.load(f)
    key = derive(password(), base64.b64decode(L["salt"]), L["iter"])
    sys.stdout.write(AESGCM(key).decrypt(base64.b64decode(L["iv"]), base64.b64decode(L["data"]), None).decode("utf-8"))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "encrypt":
        encrypt(sys.argv[2])
    elif len(sys.argv) == 2 and sys.argv[1] == "decrypt":
        decrypt()
    else:
        print(__doc__)
