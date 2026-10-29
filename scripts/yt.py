#!/usr/bin/env python3
"""YouTube comment tooling for Built on Bharat and Be Practical with Kishore (PLAYBOOK §5, §9).

Subcommands:
  whoami                 check each channel's OAuth token signs in as the right channel
  videos                 add new uploads to config/videos.yaml (film: null until mapped)
  fetch                  write new comments (not yet in state/handled.csv) to runs/<stamp>/new.json
  post FILE --confirm    post owner-approved replies from FILE, log them
  edit --channel C --reply ID --text T --confirm
                         replace the text of one of our posted replies (owner-approved), note it in the log
  hide --channel C --comment ID [--ban] --confirm
                         reject a comment (hidden from the public); --ban hides the author from the channel
  record ...             log a decision that posts nothing (skipped, heart, pin, held)

Secrets come from the environment only: YT_CLIENT_ID, YT_CLIENT_SECRET and one refresh token per channel,
YT_REFRESH_TOKEN_<CHANNEL KEY IN CAPS> (e.g. YT_REFRESH_TOKEN_BUILTONBHARAT). They are never printed.
Stdlib + PyYAML only (requirements.txt).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CHANNELS = ROOT / "config" / "channels.yaml"
VIDEOS = ROOT / "config" / "videos.yaml"
HANDLED = ROOT / "state" / "handled.csv"
RUNS = ROOT / "runs"
API = "https://www.googleapis.com/youtube/v3/"
TOKEN_URL = "https://oauth2.googleapis.com/token"
HANDLED_FIELDS = ["comment_id", "channel", "video_id", "author", "type", "language", "action", "reply_id",
                  "decided_at", "note"]
VIDEOS_HEADER = ("# YouTube video id -> film folder in the channel's film repo (CLAUDE.md, PLAYBOOK §5.1).\n"
                 "# `scripts/yt.py videos` adds new uploads with film: null; the session maps them by title.\n")
EPOCH = dt.datetime(2005, 1, 1, tzinfo=dt.timezone.utc)  # before YouTube: page every thread
REPLY_LOOKBACK_DAYS = 14  # threads we replied to in this window are re-read for answers to us


class ApiError(RuntimeError):
    pass


# ---------- config and state ----------

def load_channels() -> dict:
    return yaml.safe_load(CHANNELS.read_text())["channels"]


def load_videos() -> dict:
    return yaml.safe_load(VIDEOS.read_text()).get("videos") or {}


def save_videos(videos: dict) -> None:
    VIDEOS.write_text(VIDEOS_HEADER + yaml.safe_dump({"videos": videos}, sort_keys=True, allow_unicode=True,
                                                     width=120))


def handled_rows() -> list[dict]:
    with HANDLED.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def append_handled(row: dict) -> None:
    row = {k: row.get(k, "") for k in HANDLED_FIELDS}
    row["decided_at"] = row["decided_at"] or now_iso()
    with HANDLED.open("a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=HANDLED_FIELDS).writerow(row)


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_time(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


# ---------- HTTP ----------

def http_json(url: str, *, data: dict | None = None, form: dict | None = None, token: str | None = None,
              method: str | None = None) -> dict:
    headers = {"Accept": "application/json"}
    body = None
    if form is not None:
        body = urllib.parse.urlencode(form).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    elif data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:500]
        raise ApiError(f"HTTP {e.code} on {url.split('?')[0]}: {detail}") from None
    return json.loads(raw) if raw else {}


class Client:
    """One signed-in channel."""

    def __init__(self, key: str):
        self.key = key
        cid, secret = os.environ.get("YT_CLIENT_ID"), os.environ.get("YT_CLIENT_SECRET")
        refresh = os.environ.get(f"YT_REFRESH_TOKEN_{key.upper()}")
        missing = [n for n, v in [("YT_CLIENT_ID", cid), ("YT_CLIENT_SECRET", secret),
                                  (f"YT_REFRESH_TOKEN_{key.upper()}", refresh)] if not v]
        if missing:
            raise ApiError(f"{key}: missing environment secret(s) {', '.join(missing)} (docs/SETUP.md)")
        tok = http_json(TOKEN_URL, form={"client_id": cid, "client_secret": secret, "refresh_token": refresh,
                                         "grant_type": "refresh_token"})
        self.token = tok["access_token"]

    def get(self, path: str, **params) -> dict:
        return http_json(API + path + "?" + urllib.parse.urlencode(params), token=self.token)

    def post(self, path: str, body: dict | None = None, **params) -> dict:
        return http_json(API + path + "?" + urllib.parse.urlencode(params), data=body or {}, token=self.token,
                         method="POST")


def clients(only: str | None) -> dict[str, Client]:
    out = {}
    for key in load_channels():
        if only and key != only:
            continue
        try:
            out[key] = Client(key)
        except ApiError as e:  # fail soft per channel, loud in the output
            print(f"!! {e}", file=sys.stderr)
    return out


# ---------- subcommands ----------

def cmd_whoami(args) -> int:
    chans, ok = load_channels(), True
    for key, c in clients(args.channel).items():
        items = c.get("channels", part="snippet", mine="true").get("items", [])
        got = items[0]["id"] if items else None
        want = chans[key]["channel_id"]
        title = items[0]["snippet"]["title"] if items else "?"
        good = got == want
        ok &= good
        print(f"{'OK ' if good else 'BAD'} {key}: signed in as {title} ({got}); expected {want}")
    return 0 if ok else 1


def rss_uploads(channel_id: str) -> list[dict]:
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    with urllib.request.urlopen(url, timeout=30) as r:
        x = r.read().decode()
    out = []
    for e in re.findall(r"<entry>(.*?)</entry>", x, re.S):
        out.append({"id": re.search(r"<yt:videoId>(.*?)<", e).group(1),
                    "title": re.search(r"<title>(.*?)</title>", e).group(1),
                    "published": re.search(r"<published>(.*?)<", e).group(1)[:10]})
    return out


def api_uploads(c: Client, channel_id: str) -> list[dict]:
    out, page = [], None
    while True:
        params = {"part": "snippet", "playlistId": "UU" + channel_id[2:], "maxResults": 50}
        if page:
            params["pageToken"] = page
        r = c.get("playlistItems", **params)
        for it in r.get("items", []):
            s = it["snippet"]
            out.append({"id": s["resourceId"]["videoId"], "title": s["title"], "published": s["publishedAt"][:10]})
        page = r.get("nextPageToken")
        if not page:
            return out


def cmd_videos(args) -> int:
    import html
    videos, added = load_videos(), 0
    signed = clients(args.channel) if args.api else {}
    for key, ch in load_channels().items():
        if args.channel and key != args.channel:
            continue
        ups = api_uploads(signed[key], ch["channel_id"]) if key in signed else rss_uploads(ch["channel_id"])
        for v in ups:
            if v["id"] not in videos:
                videos[v["id"]] = {"channel": key, "film": None, "title": html.unescape(v["title"]),
                                   "published": v["published"]}
                added += 1
                print(f"+ {key} {v['id']} {v['published']} {html.unescape(v['title'])}")
    save_videos(videos)
    unmapped = [vid for vid, v in videos.items() if not v.get("film")]
    print(f"{added} new; {len(unmapped)} without a film folder: {' '.join(unmapped) or '-'}")
    return 0


def flatten(c: dict, *, channel: str, thread_id: str, held: bool = False, video_id: str | None = None) -> dict:
    s = c["snippet"]
    return {"id": c["id"], "thread_id": thread_id, "is_reply": c["id"] != thread_id, "channel": channel,
            "video_id": s.get("videoId") or video_id, "author": s.get("authorDisplayName"),
            "author_channel_id": (s.get("authorChannelId") or {}).get("value"),
            "text": s.get("textOriginal") or s.get("textDisplay"), "published": s.get("publishedAt"),
            "likes": s.get("likeCount", 0), "held": held}


def fetch_channel(c: Client, key: str, ch: dict, done: set[str], since: dt.datetime,
                  replied_threads: dict[str, str]):
    own, out, seen = ch["channel_id"], [], set()

    def keep(item: dict) -> bool:
        return item["id"] not in done and item["author_channel_id"] != own

    def thread_items(t: dict, held: bool) -> list[dict]:
        # replies read through comments.list carry no videoId: take it from the thread
        top, video = t["snippet"]["topLevelComment"], t["snippet"].get("videoId")
        items = [flatten(top, channel=key, thread_id=t["id"], held=held, video_id=video)]
        replies = (t.get("replies") or {}).get("comments", [])
        if t["snippet"].get("totalReplyCount", 0) > len(replies):
            replies = all_replies(c, t["id"])
        items += [flatten(r, channel=key, thread_id=t["id"], held=held, video_id=video) for r in replies]
        # the owner also replies by hand in Studio: mark what the channel already answered
        ours = max((i["published"] or "" for i in items if i["author_channel_id"] == own), default="")
        for i in items:
            i["our_last_reply"] = ours or None
            i["after_our_reply"] = bool(ours) and (i["published"] or "") > ours
        return items

    # a thread holding one held comment comes back in both listings: published goes first, so only the
    # comments seen in the held listing alone are flagged held
    for status in ("published", "heldForReview"):
        page = None
        while True:
            params = {"part": "snippet,replies", "allThreadsRelatedToChannelId": own, "maxResults": 100,
                      "order": "time", "textFormat": "plainText", "moderationStatus": status}
            if page:
                params["pageToken"] = page
            r = c.get("commentThreads", **params)
            threads = r.get("items", [])
            for t in threads:
                for i in thread_items(t, status != "published"):
                    if keep(i) and i["id"] not in seen:
                        seen.add(i["id"])
                        out.append(i)
            page = r.get("nextPageToken")
            oldest = min((parse_time(t["snippet"]["topLevelComment"]["snippet"]["publishedAt"]) for t in threads),
                         default=since)
            if not page or oldest < since:
                break
    # answers to our own replies on older threads
    for tid, video in replied_threads.items():
        for r in all_replies(c, tid):
            item = flatten(r, channel=key, thread_id=tid, video_id=video or None)
            item["our_last_reply"], item["after_our_reply"] = None, True
            if keep(item) and item["id"] not in seen:
                seen.add(item["id"])
                out.append(item)
    return out


def all_replies(c: Client, thread_id: str) -> list[dict]:
    out, page = [], None
    while True:
        params = {"part": "snippet", "parentId": thread_id, "maxResults": 100, "textFormat": "plainText"}
        if page:
            params["pageToken"] = page
        r = c.get("comments", **params)
        out += r.get("items", [])
        page = r.get("nextPageToken")
        if not page:
            return out


def public_subscribers(c: Client) -> set[str] | None:
    """Channel ids of subscribers who keep their subscriptions public (the API shows no others)."""
    out, page = set(), None
    try:
        while True:
            params = {"part": "subscriberSnippet", "mySubscribers": "true", "maxResults": 50}
            if page:
                params["pageToken"] = page
            r = c.get("subscriptions", **params)
            out |= {(i.get("subscriberSnippet") or {}).get("channelId") for i in r.get("items", [])}
            page = r.get("nextPageToken")
            if not page:
                return out - {None}
    except ApiError as e:
        print(f"!! subscriber list unavailable, every viewer shows as unknown: {e}", file=sys.stderr)
        return None


def viewer_profiles(history: list[dict], subs: set[str] | None) -> dict[str, dict]:
    """Every commenter's record on the channel, so a draft knows who it is talking to (PLAYBOOK §2.4).

    subscribed is "yes" only when the subscription is public; "unknown" never means "no"."""
    prof = {}
    for i in sorted(history, key=lambda i: i["published"] or ""):
        a = i["author_channel_id"]
        if not a:
            continue
        p = prof.setdefault(a, {"author": i["author"], "comments": 0, "videos": set(), "likes": 0, "held": 0,
                                "answered_by_us": 0, "first_seen": i["published"], "recent": []})
        p["comments"] += 1
        p["videos"].add(i["video_id"])
        p["likes"] += i["likes"] or 0
        p["held"] += bool(i["held"])
        p["answered_by_us"] += bool(i["our_last_reply"]) and not i["after_our_reply"]
        p["last_seen"] = i["published"]
        p["recent"] = (p["recent"] + [" ".join((i["text"] or "").split())[:160]])[-3:]
    for a, p in prof.items():
        p["videos"] = len(p["videos"] - {None})
        p["subscribed"] = "yes" if subs and a in subs else "unknown"
        p["regular"] = p["comments"] >= 3 or p["videos"] >= 2
    return prof


def cmd_fetch(args) -> int:
    rows = handled_rows()
    done = {r["comment_id"] for r in rows}
    since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=args.days)
    lookback = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=REPLY_LOOKBACK_DAYS)
    videos, chans = load_videos(), load_channels()
    found, failed, profiles = [], [], {}
    signed = clients(args.channel)
    if not signed:
        print("!! no channel signed in; nothing fetched (docs/SETUP.md)", file=sys.stderr)
        return 1
    for key, c in signed.items():
        replied = {r["note"].split("thread=")[1].split()[0]: r["video_id"] for r in rows
                   if r["channel"] == key and r["action"] == "replied" and "thread=" in r["note"]
                   and parse_time(r["decided_at"]) >= lookback}
        try:
            items = fetch_channel(c, key, chans[key], done, since, replied)
            history = fetch_channel(c, key, chans[key], set(), EPOCH, {})
        except ApiError as e:
            failed.append(f"{key}: {e}")
            continue
        prof = viewer_profiles(history, public_subscribers(c))
        invited = {r["author"] for r in rows if r["channel"] == key and "sub-ask" in r["note"]}
        for v in prof.values():
            v["invited_before"] = v["author"] in invited  # one subscribe invitation per viewer, ever (PLAYBOOK §2.5)
        profiles[key] = prof
        for i in items:
            v = videos.get(i["video_id"]) or {}
            i["video_title"], i["film"] = v.get("title"), v.get("film")
            i["viewer"] = prof.get(i["author_channel_id"])
        found += items
    found.sort(key=lambda i: (i["channel"], i["video_id"] or "", i["published"] or ""))
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%MZ")
    out = RUNS / stamp / "new.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(found, ensure_ascii=False, indent=1))
    # viewer profiles stay in runs/ (gitignored): the repo is public, so who subscribes never goes in git
    (out.parent / "viewers.json").write_text(json.dumps(profiles, ensure_ascii=False, indent=1))
    per = {}
    for i in found:
        per[(i["channel"], i["video_title"] or i["video_id"])] = per.get((i["channel"], i["video_title"] or
                                                                          i["video_id"]), 0) + 1
    for (ch, title), n in per.items():
        print(f"{ch} · {title}: {n} new")
    print(f"{len(found)} new comment(s) → {os.path.relpath(out, ROOT)}")
    unmapped = sorted({i["video_id"] or "(no video id)" for i in found if not i["film"]})
    if unmapped:
        print(f"videos without a film folder (map them in config/videos.yaml): {' '.join(unmapped)}")
    for f in failed:
        print(f"!! fetch failed: {f}", file=sys.stderr)
    return 1 if failed else 0


def cmd_post(args) -> int:
    """FILE: JSON list of {comment_id, thread_id, channel, video_id, author, type, language, text}."""
    if not args.confirm:
        print("Refusing to post without --confirm (only owner-approved replies go up).", file=sys.stderr)
        return 2
    approved = json.loads(Path(args.file).read_text())
    replied = {r["comment_id"] for r in handled_rows() if r["action"] == "replied"}
    signed, bad = {}, 0
    for a in approved:
        if a["comment_id"] in replied:
            print(f"skip {a['comment_id']}: already replied")
            continue
        text = a["text"].strip()
        # YouTube has one level of replies: answering a reply needs their handle first, or it reads as aimed at the
        # thread's first commenter
        if a["comment_id"] != a["thread_id"] and a.get("author", "").startswith("@") \
                and not text.startswith(a["author"]):
            text = f"{a['author']} {text}"
        if not text or len(text) > 9000:
            print(f"!! {a['comment_id']}: empty or too long", file=sys.stderr)
            bad += 1
            continue
        key = a["channel"]
        try:
            signed[key] = signed.get(key) or Client(key)
            r = signed[key].post("comments", {"snippet": {"parentId": a["thread_id"], "textOriginal": text}},
                                 part="snippet")
        except ApiError as e:
            print(f"!! {a['comment_id']}: {e}", file=sys.stderr)
            bad += 1
            continue
        append_handled({**{k: a.get(k, "") for k in HANDLED_FIELDS}, "action": "replied", "reply_id": r["id"],
                        "decided_at": "", "note": f"thread={a['thread_id']} {a.get('note', '')}".strip()})
        print(f"posted {a['comment_id']} → reply {r['id']}")
    return 1 if bad else 0


def cmd_edit(args) -> int:
    if not args.confirm:
        print("Refusing to edit without --confirm (only owner-approved text goes up).", file=sys.stderr)
        return 2
    rows = handled_rows()
    mine = [r for r in rows if r["reply_id"] == args.reply]
    if not mine:
        print(f"!! {args.reply}: not one of our logged replies", file=sys.stderr)
        return 1
    text = args.text.strip()
    if not text or len(text) > 9000:
        print(f"!! {args.reply}: empty or too long", file=sys.stderr)
        return 1
    c = Client(args.channel)
    http_json(API + "comments?part=snippet", data={"id": args.reply, "snippet": {"textOriginal": text}},
              token=c.token, method="PUT")
    mine[0]["note"] = f"{mine[0]['note']} edited {now_iso()}".strip()
    header = HANDLED.read_text(encoding="utf-8").splitlines(keepends=True)[0]  # keep its line ending
    with HANDLED.open("w", newline="", encoding="utf-8") as f:
        f.write(header)
        csv.DictWriter(f, fieldnames=HANDLED_FIELDS).writerows(rows)
    print(f"edited {args.reply}")
    return 0


def cmd_hide(args) -> int:
    if not args.confirm:
        print("Refusing to hide without --confirm (owner decides).", file=sys.stderr)
        return 2
    c = Client(args.channel)
    params = {"id": args.comment, "moderationStatus": "rejected"}
    if args.ban:
        params["banAuthor"] = "true"
    try:
        c.post("comments/setModerationStatus", None, **params)
    except ApiError as e:
        print(f"!! {e}", file=sys.stderr)
        return 1
    append_handled({"comment_id": args.comment, "channel": args.channel, "video_id": args.video or "",
                    "author": args.author or "", "type": "G", "action": "banned" if args.ban else "hidden",
                    "note": args.note or ""})
    print(f"{'banned author of' if args.ban else 'hid'} {args.comment}")
    return 0


def cmd_record(args) -> int:
    if args.comment in {r["comment_id"] for r in handled_rows()}:
        print(f"{args.comment} already logged")
        return 0
    append_handled({"comment_id": args.comment, "channel": args.channel, "video_id": args.video or "",
                    "author": args.author or "", "type": args.type or "", "language": args.language or "",
                    "action": args.action, "note": args.note or ""})
    print(f"logged {args.comment}: {args.action}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("whoami"); s.add_argument("--channel"); s.set_defaults(fn=cmd_whoami)
    s = sub.add_parser("videos"); s.add_argument("--channel")
    s.add_argument("--api", action="store_true", help="use the signed-in API (all uploads) instead of the RSS feed")
    s.set_defaults(fn=cmd_videos)
    s = sub.add_parser("fetch"); s.add_argument("--channel")
    s.add_argument("--days", type=float, default=7, help="how far back to page for new threads (default 7)")
    s.set_defaults(fn=cmd_fetch)
    s = sub.add_parser("post"); s.add_argument("file"); s.add_argument("--confirm", action="store_true")
    s.set_defaults(fn=cmd_post)
    s = sub.add_parser("edit")
    for a in ("--channel", "--reply", "--text"):
        s.add_argument(a, required=True)
    s.add_argument("--confirm", action="store_true")
    s.set_defaults(fn=cmd_edit)
    s = sub.add_parser("hide")
    for a in ("--channel", "--comment"):
        s.add_argument(a, required=True)
    for a in ("--video", "--author", "--note"):
        s.add_argument(a)
    s.add_argument("--ban", action="store_true"); s.add_argument("--confirm", action="store_true")
    s.set_defaults(fn=cmd_hide)
    s = sub.add_parser("record")
    for a in ("--channel", "--comment"):
        s.add_argument(a, required=True)
    s.add_argument("--action", required=True, choices=["skipped", "heart", "pin", "heart+pin", "held", "no-reply"])
    for a in ("--video", "--author", "--type", "--language", "--note"):
        s.add_argument(a)
    s.set_defaults(fn=cmd_record)
    args = p.parse_args(argv)
    try:
        return args.fn(args)
    except ApiError as e:
        print(f"!! {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
