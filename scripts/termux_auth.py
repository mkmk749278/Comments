#!/usr/bin/env python3
"""One-time YouTube sign-in, run on the owner's phone in Termux (docs/SETUP.md).

Asks for the OAuth client id and secret (a "Desktop app" client), opens Google's sign-in in the phone's browser once per
channel, catches the answer on 127.0.0.1, checks which channel signed in, and prints the environment secrets to paste
into the Claude cloud environment. Nothing is saved to disk or sent anywhere but Google. Stdlib only.

    python yt_auth.py                 # every channel below, plus YT_CLIENT_ID / YT_CLIENT_SECRET
    python yt_auth.py KEY [KEY ...]   # only these channels; prints YT_REFRESH_TOKEN_<KEY> for each

A KEY not listed below signs in whichever channel the owner picks (any channel not already signed in this run) and
prints its channel id and handle, so a new channel can be added to config/channels.yaml.
"""
import base64
import getpass
import hashlib
import http.server
import json
import secrets
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

CHANNELS = {  # key (config/channels.yaml) -> (channel id, label); secret = YT_REFRESH_TOKEN_<KEY IN CAPS>
    # Google's account chooser may still show this channel's old name, Giggle Patch (owner, 2026-10-29).
    "bepracticalwithkishore": ("UCPn8z0XQ2ykv3Rt_Oexn9wQ", "Be Practical with Kishore (old name: Giggle Patch)"),
    # This channel id was Built on Bharat's; renamed The Mechanical Paradox by 2026-11-04 (PLAYBOOK §7.1).
    "themechanicalparadox": ("UCgmnU_XgFuGD2MejCDmAnbA", "The Mechanical Paradox (old name: Built on Bharat)"),
}
SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
AUTH = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN = "https://oauth2.googleapis.com/token"


def post_form(url, form):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(form).encode())
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"\nGoogle said no: {e.read().decode(errors='replace')[:300]}")


def get_json(url, token):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def catch_code(state):
    """Serve one request on a free local port; return (redirect_uri, server) and the code via server.result."""
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
            ok = q.get("state") == state and "code" in q
            self.server.result = q.get("code") if ok else None
            self.server.error = None if ok else (q.get("error") or "wrong or missing answer")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            msg = "Done. Go back to Termux." if ok else f"Something went wrong: {self.server.error}. Go back to Termux."
            self.wfile.write(f"<h2 style='font-family:sans-serif'>{msg}</h2>".encode())

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    srv.result = srv.error = None
    return f"http://127.0.0.1:{srv.server_port}", srv


def sign_in(client_id, client_secret, label):
    state = secrets.token_urlsafe(16)
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    redirect, srv = catch_code(state)
    url = AUTH + "?" + urllib.parse.urlencode({
        "client_id": client_id, "redirect_uri": redirect, "response_type": "code", "scope": SCOPE,
        "access_type": "offline", "prompt": "consent select_account", "state": state,
        "code_challenge": challenge, "code_challenge_method": "S256"})
    print(f"\n=== {label} ===")
    print("Opening the browser. Pick your Google account, then THE CHANNEL for this round.")
    print("On 'Google hasn't verified this app': Advanced -> Go to Comments (unsafe) -> Continue.")
    input("Press Enter to open Chrome...")
    try:
        subprocess.run(["termux-open-url", url], check=False)
    except FileNotFoundError:
        pass
    print(f"\nIf the browser didn't open, copy this link into Chrome:\n{url}\n")
    while srv.result is None and srv.error is None:
        srv.handle_request()
    if srv.error:
        sys.exit(f"Sign-in stopped: {srv.error}")
    tok = post_form(TOKEN, {"client_id": client_id, "client_secret": client_secret, "code": srv.result,
                            "code_verifier": verifier, "grant_type": "authorization_code",
                            "redirect_uri": redirect})
    if "refresh_token" not in tok:
        sys.exit("Google gave no long-term token. Remove 'Comments' at myaccount.google.com -> Security -> "
                 "Third-party connections, then run this again.")
    items = get_json("https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true",
                     tok["access_token"]).get("items", [])
    if not items:
        return (None, None, None), tok["refresh_token"]
    sn = items[0]["snippet"]
    return (items[0]["id"], sn["title"].replace("\n", " "), sn.get("customUrl")), tok["refresh_token"]


def secret_name(key):
    return "YT_REFRESH_TOKEN_" + "".join(ch for ch in key.upper() if ch.isalnum() or ch == "_")


def wanted_channels(argv):
    """[(key, channel id or None, label)] in the order asked; None means 'any channel not yet signed in'."""
    keys = [a.strip().lower() for a in argv if a.strip()] or list(CHANNELS)
    if len(set(keys)) != len(keys):
        sys.exit("Each channel key once, please.")
    return [(k, *CHANNELS[k]) if k in CHANNELS else (k, None, f"the channel for '{k}'") for k in keys]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    want = wanted_channels(argv)
    print("YouTube access sign-in (docs/SETUP.md, step 4).")
    print("Channels this run: " + ", ".join(label for _, _, label in want))
    print("Paste from your Google Cloud 'Desktop app' client. The secret is hidden while you type.\n")
    client_id = input("Client ID: ").strip()
    client_secret = getpass.getpass("Client secret: ").strip()
    if not client_id.endswith(".apps.googleusercontent.com") or not client_secret:
        sys.exit("That doesn't look like a Client ID and secret. Check step 3 and run again.")
    known = {cid: key for key, cid, _ in want if cid}
    got, info = {}, {}  # key -> refresh token; key -> (channel id, title, handle)
    for key, wanted, label in want:
        while key not in got:
            (cid, title, handle), refresh = sign_in(client_id, client_secret, label)
            taken = {i[0] for i in info.values()}
            if cid and cid in taken:
                print(f"That was {title}, already signed in this run. Pick {label}.")
            elif cid and (cid == wanted or (wanted is None and cid not in {c for c, _ in CHANNELS.values()})):
                got[key], info[key] = refresh, (cid, title, handle)
                print(f"OK: signed in as {title}")
                continue
            elif cid in known and known[cid] not in got:
                other = known[cid]
                got[other], info[other] = refresh, (cid, title, handle)
                print(f"OK: signed in as {title} (a channel later in the list; saved it, now {label})")
            else:
                print(f"That was {title or 'no channel'}, not {label}. Let's try again; pick {label}.")
            input("Press Enter to reopen the browser...")
    print("\n" + "=" * 60)
    print("Copy everything between the lines into the Claude environment")
    print("(session title bar -> environment -> Edit -> secrets / environment variables).")
    print("Then clear this screen with:  clear")
    print("=" * 60)
    if not argv:
        print(f"YT_CLIENT_ID={client_id}")
        print(f"YT_CLIENT_SECRET={client_secret}")
    for key, _, _ in want:
        print(f"{secret_name(key)}={got[key]}")
    print("=" * 60)
    for key, (cid, title, handle) in info.items():
        if key not in CHANNELS:
            print(f"Also tell Claude (not a secret): {key} = {title}, {handle or 'no handle'}, channel id {cid}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nStopped.")
