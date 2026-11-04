# One-time setup: YouTube access (phone only, about 20 minutes)

This lets Claude read comments and post **only the replies you approve** on the channels. You do it once. Everything
is done in **Chrome on the phone**; tap **⋮ → Desktop site** whenever a Google page looks cramped.

You will end with these values, which go into the cloud environment's secrets (step 5), **never into the chat**:
`YT_CLIENT_ID`, `YT_CLIENT_SECRET`, and one `YT_REFRESH_TOKEN_<KEY>` per channel (key = the channel's name in
`config/channels.yaml`): `YT_REFRESH_TOKEN_BEPRACTICALWITHKISHORE`, `YT_REFRESH_TOKEN_THEMECHANICALPARADOX`.

## 1. Create the Google Cloud project
1. Open **console.cloud.google.com** and sign in with the Google account that owns the channels.
2. Top bar → project picker → **New project**. Name: `Comments`. **Create**, then select it.
3. ☰ menu → **APIs & Services → Library** → search **YouTube Data API v3** → **Enable**.
   (Free: 10,000 units a day. Reading comments costs ~1 unit a page, a reply ~50. No billing account needed.)

## 2. The sign-in screen (Google Auth Platform)
1. ☰ → **APIs & Services → OAuth consent screen** (it may open as **Google Auth Platform**) → **Get started**.
2. App name `Comments`, support email: yours. Audience: **External**. Contact email: yours. Agree → **Create**.
3. **Data access → Add or remove scopes** → filter `youtube.force-ssl` → tick
   `.../auth/youtube.force-ssl` → **Update → Save**.
4. **Audience → Publish app → Confirm** (status becomes *In production*).
   *Why:* while the app is in *Testing*, Google cancels the sign-in after 7 days. Published, it lasts. You will see a
   "Google hasn't verified this app" warning when you sign in; that is normal for an app only you use.

## 3. The client
1. **Clients → Create client** → Application type **Desktop app**, name `Comments` → **Create**.
2. Keep the page open: Termux asks for the **Client ID** and **Client secret** next
   (`YT_CLIENT_ID` and `YT_CLIENT_SECRET`).

## 4. Sign in once per channel: one Termux command
Paste this in Termux:

```
pkg install -y python && curl -fsSL -o ~/yt_auth.py https://raw.githubusercontent.com/mkmk749278/Comments/main/scripts/termux_auth.py && python ~/yt_auth.py; rm -f ~/yt_auth.py
```

It asks for the Client ID and secret (the secret stays hidden while you type), then opens Chrome once per
channel. Each time: pick your Google account, then **the channel it names** (Be Practical with Kishore may appear under
its old name, **Giggle Patch**). Press Enter in Termux before each sign-in to open Chrome; if it doesn't open, long-press in Termux → More… → Select URL → the last link. On the "hasn't
verified" page: **Advanced → Go to Comments (unsafe) → Continue**. Chrome shows *Done. Go back to Termux.* Termux
checks which channel signed in (picking the wrong one just asks again) and at the end prints the `NAME=value` lines,
ready for step 5. Nothing is saved on the phone.

**Adding one channel later** (the client already exists, so only its token is new): put the channel keys after the
command, e.g. `python ~/yt_auth.py themechanicalparadox`. It then signs in only those channels and prints only their
`YT_REFRESH_TOKEN_<KEY>` lines. A key the script doesn't know yet signs in whichever new channel you pick and also
prints that channel's id and handle to tell Claude.

### 4b. Fallback without Termux (OAuth Playground)
Only if Termux can't be used: create a second client of type **Web application** with the redirect URI
`https://developers.google.com/oauthplayground`, and use that client's id and secret here.
Do this once per channel.

1. Open **developers.google.com/oauthplayground**.
2. Tap the **⚙ gear** (top right) → tick **Use your own OAuth credentials** → paste the Client ID and Client secret →
   close the gear.
3. **Step 1**, in the box *Input your own scopes*, type
   `https://www.googleapis.com/auth/youtube.force-ssl` → **Authorize APIs**.
4. Pick your Google account. **When Google asks which channel (account or brand account), pick the channel for this
   round.** On the "hasn't verified" page: **Advanced → Go to Comments (unsafe)** → **Continue / Allow**.
5. Back in the Playground, **Step 2 → Exchange authorization code for tokens**. Copy the **Refresh token**.
   It is `YT_REFRESH_TOKEN_<KEY>` for the channel you picked (e.g. `YT_REFRESH_TOKEN_THEMECHANICALPARADOX`).
6. For the next channel, go back to Step 1 and repeat 3–5, choosing that channel.

## 5. Save the four values as secrets
1. In the **Claude app**, open a Claude Code session in the `Comments` environment → tap the **environment menu in the
   session's title bar → Edit**.
2. Under **Network secrets** (or **API credentials**; in older apps, **Environment variables**) add each name
   with its value (the `NAME=value` lines Termux printed). Save, then type `clear` in Termux.
3. Start a **new session** (secrets load when a session starts) and say *"check YouTube access"*. Claude runs
   `scripts/yt.py whoami`, which prints `OK` for each channel when the right channel signed in, without ever showing
   the secrets.
4. If you copied the values anywhere else (Keep, notes), delete them.

Steps 1–3 stay in the browser: Google has no command for creating this kind of sign-in client, so those taps can't
be scripted.

## If something goes wrong
- **`BAD … signed in as <other channel>`**: in step 4 the wrong channel was picked. Redo step 4 for that channel and
  replace its secret.
- **`invalid_grant`**: the sign-in expired or was revoked (or the app was still in *Testing*). Check step 2.4, then redo
  step 4 for that channel.
- **`quotaExceeded`**: the daily 10,000 units ran out; it resets at midnight Pacific time (12:30 pm IST).
- To cut Claude's access at any time: **myaccount.google.com → Security → Third-party connections → Comments → Delete**.
