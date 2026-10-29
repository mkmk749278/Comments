"""Offline tests for scripts/yt.py: the YouTube API is faked, nothing touches the network."""
import json
import os
import shutil
import sys
import tempfile
import unittest
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import yt  # noqa: E402

OWN = "UCgmnU_XgFuGD2MejCDmAnbA"
NOW = "2099-01-01T10:00:00Z"


def comment(cid, text, author="viewer", author_ch="UCviewer", video="VID00000001"):
    return {"id": cid, "snippet": {"videoId": video, "authorDisplayName": author, "textOriginal": text,
                                   "authorChannelId": {"value": author_ch}, "publishedAt": NOW, "likeCount": 2}}


def thread(tid, text, replies=(), total=None):
    return {"id": tid, "snippet": {"videoId": "VID00000001", "topLevelComment": comment(tid, text),
                                   "totalReplyCount": len(replies) if total is None else total},
            "replies": {"comments": list(replies)}}


class FakeApi:
    def __init__(self):
        self.calls = []

    def __call__(self, url, *, data=None, form=None, token=None, method=None):
        self.calls.append((url, data, method))
        if url == yt.TOKEN_URL:
            return {"access_token": "fake"}
        path, _, q = url[len(yt.API):].partition("?")
        p = dict(urllib.parse.parse_qsl(q))
        if path == "commentThreads":
            if p["moderationStatus"] == "heldForReview":
                # t1 also comes back here: it holds one held reply beside its public ones
                return {"items": [thread("held1", "WhatsApp me for profit +91…"),
                                  thread("t1", "Great point on the blades", [comment("r1", "Agree with this"),
                                                                             comment("r1h", "held reply")])]}
            return {"items": [
                thread("t1", "Great point on the blades", [comment("r_own", "Thanks", author_ch=OWN),
                                                           comment("r1", "Agree with this")]),
                thread("t2", "Old one we already handled"),
                thread("t3", "Long thread", [comment("r3a", "first")], total=2),
            ]}
        if path == "comments" and method is None:
            # comments.list replies carry no videoId
            items = [comment("r3a", "first"), comment("r3b", "second")]
            for i in items:
                del i["snippet"]["videoId"]
            return {"items": items}
        if path == "comments" and method == "POST":
            return {"id": "reply_" + data["snippet"]["parentId"]}
        if path == "subscriptions":
            return {"items": [{"subscriberSnippet": {"channelId": "UCviewer"}}]}
        if path == "comments/setModerationStatus":
            return {}
        raise AssertionError(f"unexpected call {url}")


class YtTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.orig = {k: getattr(yt, k) for k in ("HANDLED", "RUNS", "http_json")}
        yt.HANDLED = self.tmp / "handled.csv"
        shutil.copy(self.orig["HANDLED"], yt.HANDLED)
        yt.RUNS = self.tmp / "runs"
        self.api = FakeApi()
        yt.http_json = self.api
        os.environ.update({"YT_CLIENT_ID": "x", "YT_CLIENT_SECRET": "y", "YT_REFRESH_TOKEN_BUILTONBHARAT": "z"})
        os.environ.pop("YT_REFRESH_TOKEN_BEPRACTICALWITHKISHORE", None)
        yt.append_handled({"comment_id": "t2", "channel": "builtonbharat", "action": "skipped"})

    def tearDown(self):
        for k, v in self.orig.items():
            setattr(yt, k, v)
        shutil.rmtree(self.tmp)

    def fetched(self):
        self.assertEqual(yt.main(["fetch", "--channel", "builtonbharat"]), 0)
        return json.loads(next(yt.RUNS.glob("*/new.json")).read_text())

    def test_fetch_skips_handled_and_own_and_reads_full_threads(self):
        got = self.fetched()
        ids = {i["id"]: i for i in got}
        self.assertEqual(len(got), len(ids), "a comment was listed twice")
        self.assertEqual(set(ids), {"t1", "r1", "t3", "r3a", "r3b", "held1", "r1h"})
        self.assertEqual({i["video_id"] for i in got}, {"VID00000001"})
        self.assertFalse(ids["t1"]["held"] or ids["r1"]["held"])
        self.assertTrue(ids["r1h"]["held"])
        self.assertEqual(ids["t1"]["our_last_reply"], NOW)  # the channel already answered thread t1
        self.assertIsNone(ids["t3"]["our_last_reply"])
        v = ids["t1"]["viewer"]  # every fake comment is by UCviewer, a public subscriber
        self.assertEqual((v["subscribed"], v["regular"], v["answered_by_us"]), ("yes", True, 2))
        self.assertGreaterEqual(v["comments"], 8)  # history includes t2, already handled
        self.assertFalse(v["invited_before"])
        self.assertTrue(ids["r1"]["is_reply"])
        self.assertEqual(ids["r1"]["thread_id"], "t1")
        self.assertTrue(ids["held1"]["held"])

    def test_post_needs_confirm_then_posts_once_and_logs(self):
        f = self.tmp / "approved.json"
        f.write_text(json.dumps([{"comment_id": "r1", "thread_id": "t1", "channel": "builtonbharat",
                                  "type": "A", "language": "en", "text": "The blade point is the heart of it."}]))
        self.assertEqual(yt.main(["post", str(f)]), 2)
        self.assertFalse([c for c in self.api.calls if c[2] == "POST"])
        self.assertEqual(yt.main(["post", str(f), "--confirm"]), 0)
        self.assertEqual(yt.main(["post", str(f), "--confirm"]), 0)  # second run: already replied
        posts = [c for c in self.api.calls if c[2] == "POST" and "setModeration" not in c[0]]
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0][1]["snippet"]["parentId"], "t1")
        row = [r for r in yt.handled_rows() if r["comment_id"] == "r1"][0]
        self.assertEqual((row["action"], row["reply_id"]), ("replied", "reply_t1"))
        self.assertIn("thread=t1", row["note"])
        self.assertNotIn("r1", {i["id"] for i in self.fetched()})

    def test_hide_and_record(self):
        self.assertEqual(yt.main(["hide", "--channel", "builtonbharat", "--comment", "held1"]), 2)
        self.assertEqual(yt.main(["hide", "--channel", "builtonbharat", "--comment", "held1", "--ban",
                                  "--confirm"]), 0)
        self.assertIn("banAuthor=true", self.api.calls[-1][0])
        self.assertEqual(yt.main(["record", "--channel", "builtonbharat", "--comment", "t3",
                                  "--action", "heart"]), 0)
        actions = {r["comment_id"]: r["action"] for r in yt.handled_rows()}
        self.assertEqual((actions["held1"], actions["t3"]), ("banned", "heart"))

    def test_missing_secret_fails_loud(self):
        self.assertEqual(yt.main(["fetch", "--channel", "bepracticalwithkishore"]), 1)


if __name__ == "__main__":
    unittest.main()
