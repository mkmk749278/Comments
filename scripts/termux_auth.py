#!/usr/bin/env python3
"""One-time YouTube sign-in for both channels, run on the owner's phone in Termux (docs/SETUP.md).

Asks for the OAuth client id and secret (a "Desktop app" client), opens Google's sign-in in the phone's browser once per
channel, catches the answer on 127.0.0.1, checks which channel signed in, and prints the four environment secrets
to paste into the Claude cloud environment. Nothing is saved to disk or sent anywhere but Google.
Stdlib only.
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

CHANNELS = {  # channel id -> secret name (config/channels.yaml)
    "UCgmnU_XgFuGD2MejCDmAnbA": ("Built on Bharat", "YT_REFRESH_TOKEN_BUILTONBHARAT"),
    # Google's account chooser may still show this channel's old name, Giggle Patch (owner, 2026-10-29).
    "UCPn8z0XQ2ykv3Rt_Oexn9wQ": ("Be Practical with Kishore (old name: Giggle Patch)",
                                 "YT_REFRESH_TOKEN_BEPRACTICALWITHKISHORE"),
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
    return (items[0]["id"], items[0]["snippet"]["title"]) if items else (None, None), tok["refresh_token"]


def main():
    print("YouTube access for the Comments repo (docs/SETUP.md, step 4).")
    print("Paste from your Google Cloud 'Desktop app' client. The secret is hidden while you type.\n")
    client_id = input("Client ID: ").strip()
    client_secret = getpass.getpass("Client secret: ").strip()
    if not client_id.endswith(".apps.googleusercontent.com") or not client_secret:
        sys.exit("That doesn't look like a Client ID and secret. Check step 3 and run again.")
    got = {}
    for wanted, (label, _) in CHANNELS.items():
        while wanted not in got:
            (cid, title), refresh = sign_in(client_id, client_secret, label)
            if cid == wanted:
                got[wanted] = refresh
                print(f"OK: signed in as {title}")
            elif cid in CHANNELS and cid not in got:
                got[cid] = refresh
                print(f"OK: signed in as {title} (the other channel; saved it, now the one still missing)")
            else:
                print(f"That was {title or 'no channel'}, not {label}. Let's try again; pick {label}.")
                input("Press Enter to reopen the browser...")
    print("\n" + "=" * 60)
    print("Copy everything between the lines into the Claude environment")
    print("(session title bar -> environment -> Edit -> secrets / environment variables).")
    print("Then clear this screen with:  clear")
    print("=" * 60)
    print(f"YT_CLIENT_ID={client_id}")
    print(f"YT_CLIENT_SECRET={client_secret}")
    for cid, (_, name) in CHANNELS.items():
        print(f"{name}={got[cid]}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nStopped.")
