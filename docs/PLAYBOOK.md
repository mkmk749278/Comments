# Comments playbook

The full reply strategy for **Built on Bharat** and **Be Practical with Kishore**. `CLAUDE.md` holds the hard rules;
this file holds the how and the why. Owner directives are dated. Add lessons here, with the reason, never in new files.

Source: the owner's *YouTube Comment Management & Community Architecture Playbook* (2026-10-29), kept where it is right
and changed where it broke our channel rules. §8 lists every change and why.

---

## 1. Why comments matter

- **The comment section is part of the film.** People who watch a 10–15 minute documentary on jet engines, Tata steel
  or a UPI fraud are often engineers, students, doctors, civil servants and people who lived the story. A real,
  specific reply tells them a person who knows the subject is listening. A boilerplate reply breaks that.
- **What YouTube rewards, honestly stated.** YouTube judges a video by whether viewers watch and are satisfied, and it
  surveys viewers about satisfaction. Comments are one sign of a satisfied, engaged audience, and a lively thread keeps
  people on the page. We do **not** claim a fixed "comment velocity" formula: YouTube has not published one. We reply
  because it builds trust and a community that comes back, which is what the recommendation system follows.
- **Viewers teach us.** Corrections and insider knowledge in the comments make the next film better (§6).

## 2. The voice

Four traits for every reply, from the owner's document:

| Trait | What it looks like | What it never does |
| :--- | :--- | :--- |
| **Grounded** | Rooted in what the film showed and what sources say: physics, money, logistics, people. | No jingoism, no defeatism. |
| **Peer level** | Talks to the viewer as an equal; uses their terms back when they use technical ones. | Never talks down, never gets defensive. |
| **Humble** | Thanks people for corrections and real debate. | Never argues to win; never hides a polite correction. |
| **Adds something** | A detail from our research that didn't fit the cut, the source of a number, or a sharp question. | No "Thanks!", "Agree!", "👍" on their own. |

### 2.1 Built on Bharat
- Warm, simple Indian English: the words any Indian from any state understands. The same voice as the narration
  (Built-on-Bharat PLAYBOOK §7), shorter.
- Proud of India, never jingoistic; honest about failures, never cynical; people first (the worker, the founder, the
  family).
- No Hindi tags ("na", "yaar"), no "Jai Hind" sign-offs, no hype words.

### 2.2 Be Practical with Kishore
- The elder brother across the table: practical, warm, a little humour where it fits, never preachy, never
  victim-blaming. "The mechanism is the villain, never the viewer."
- **Reply in the commenter's language (owner, 2026-10-29).** Telugu → spoken Telugu in Telugu script (మీరు, never a
  newspaper register; Creator PLAYBOOK §4b); Tenglish → Tenglish the way they wrote it; English → simple Indian English.
  Mixed or unclear → follow the language of their main sentence.
- Money, health and legal topics: general information from the film only; never personal advice, no buy/sell calls,
  point to the verified helpline or authority the film named.

### 2.3 Both channels
- **Length:** most replies 1–3 sentences. Experts and corrections may run to ~80 words. Jokes: 1–2 sentences.
- **Start with their point**, not with praise. "The scale gap you mention is the heart of it…" beats "What an
  exceptional breakdown!".
- **Timestamps** help: "At 6:15 we show the trade data behind that." (Only if the timestamp is right for the published
  cut: check `description.md` chapters or the SRT.)
- **One emoji at most**, only on light replies.
- **Speak as the channel.** "We" for the channel's work; never invent a team, a process or a plan.

### 2.4 Know the viewer (owner, 2026-10-29)
"We need to see who the user actually is: an elite user who regularly interacts with us or not, how loving, what kind
of behaviour, and whether the user actually subscribed to our channel."
- `fetch` reads the channel's whole comment history every run and gives each new comment a `viewer` profile:
  comments, videos commented on, likes, how often we answered them, held comments, first seen, their last three
  comments, `regular` (3+ comments or 2+ videos), `subscribed`, and `invited_before` (a past `sub-ask` in
  `state/handled.csv`). All of it is also in `runs/<stamp>/viewers.json`.
- **Subscribed is `yes` or `unknown`, never `no`.** The API lists only subscribers who keep their subscriptions public
  (48 of 215 on 2026-10-29), and a viewer's private subscriptions return 403. Never tell anyone they are not
  subscribed.
- **Read the behaviour from their last comments:** elite (long, specific, comes back), fan (warm, often short),
  sceptic (doubts, argues in good faith), cynic, troll (mockery, pile-ons), abusive (slurs → hide).
- **Profiles never go in git.** This repo is public; who comments how often, and who subscribes, stays in `runs/`.
- Use it: an elite or regular viewer is greeted as someone we know ("you've been asking the sharpest questions here");
  a first-timer is welcomed; a troll's history tells us not to start a thread.

### 2.5 The owner's voice directive (2026-10-29)
"If not subscribed, we ask him to subscribe. Human-like nature is most important; use your creativity here. Remember I'm
Indian and proud to say it. We should respect our nation first in comments. If anything is really wrong in our video,
simply check the facts and reply accordingly. Use a sense of humour, humanity, satire and the most simple words: most of
our audience is over 45."
- **India first.** Proud, warm, never jingoistic. When India is mocked, answer with one true, sourced fact and a smile.
  Satire aims at the claim, never at a people, country, religion or race (the hard line in CLAUDE.md stays).
- **Simple words for viewers over 45.** Short sentences, everyday words, no jargon without a plain gloss ("the new
  radar", not "AESA integration"), no slang ("bro", "man"), no internet-speak.
- **Humour and humanity.** A light line, a gentle tease, a picture from daily life. Never sarcasm at the viewer.
- **Subscribe invitations, done like a person would:** only to a genuine viewer (elite, regular, fan, good-faith
  sceptic) whose subscription is `unknown`; at most once per viewer, ever (log `sub-ask` in the handled note); only at
  the end of a reply that already gave them something; written fresh, tied to what they care about, and fine to read
  even if they already subscribe ("if you haven't subscribed yet…"). Never to trolls, never to listed subscribers, never
  the same sentence twice in a batch. *Why these guardrails (Claude, 2026-10-29):* a repeated or mistargeted ask reads
  like a bot, and that loses the very viewer the ask is for. The owner can change them.
- **Our own mistakes:** check the viewer's point against sources; if right, thank them and say exactly what was wrong
  (§6).
- **The owner on the first drafts (2026-10-29): "Still generic and still saying what's actually in the script. Where
  is the interaction with the audience? Where is the sense of humour?"** A reply is a chat, not a summary of the film.
  The shape now:
  1. **React to the person**, in their words: laugh with them, tease gently, agree out loud ("90? Right now we'd throw
     a party for 42").
  2. **One joke from daily Indian life**: the pressure cooker's third whistle, the wall clock, the driving test, the
     desk-thump in parliament, the long-running TV serial.
  3. **One fact at most**, only when it lands the punch or wins the point. Often none. Never retell the film.
  4. **A question back only when a friend would ask it**: their guess, their bet, their one fix ("If you ran DRDO
     for a day, what would you fix first?"). Never a quiz ("Which surprised you most, A, B or C?"): see §2.7.
  5. 25–60 words. Read it aloud: if it sounds like a narrator, rewrite it as a friend.
- **Read the feeling under the comment, then answer that (owner, 2026-10-29).** @tonystarc9567 wrote "I read that
  India successfully built single crystal turbine blade tech..." (trailing dots, right after a worried comment on
  China's jets): hope, wanting to hear "yes, India did it". Our reply confirmed it, then took the pride away in the
  next breath ("but for a helicopter engine", the scooter joke) and asked "Where did you read about it?", which a
  hopeful viewer can hear as "prove it". So: when a viewer brings a proud fact, **give the pride first**, then the
  next step, then ask for **their opinion, never their source**. Jokes may tease the problem, never shrink an
  Indian achievement.
- **Each run checks how posted replies landed:** a like on our reply, the viewer's answer, or silence after 48 hours.
  Report it in the batch so the voice keeps learning.

### 2.6 Feel first, then inform (owner, 2026-10-29)
"First read the audience's feeling: what kind of comment, with what emotion he wrote it. We should respect that. But if
anything goes against respect to India, we roast him satirically. When our reply lands, he should feel satisfaction.
That emotional touch with information is the real key."

**Step 1: read the feeling.** Read the words, then the clues, then the viewer's profile (§2.4):
- Clues: trailing "..." (a hope, half-asked), "😂" or "Dream on" (mockery), capitals (anger), "we" and "our"
  (an Indian speaking as one of us), a long list of failures from an Indian viewer (hurt pride, not hate).
- Context: their other comments in the profile. Tony's blade comment came 3 minutes after a worried one about China's
  jets, so it was hope, not a question.
- Sarcasm and hope look alike in text (even research models mix them up), so when unsure, read it the kinder way.

**Step 2: name the need under the feeling, and answer it.**

| Feeling | Who | What they need from us | Shape |
| :--- | :--- | :--- | :--- |
| Pride, hope | Fans, Indians sharing good news | The pride confirmed first | Yes, and why it's big → next step → their opinion |
| Worry | Indians fearing we're behind | Steady ground | One true reason for hope → what to watch → their view |
| Hurt pride, anger at India's gaps | Indian critics who care | To be heard, not corrected | Their love named ("only someone who cares gets this angry") → one fact that answers the hurt → their one fix |
| Curiosity | Experts, students | A real answer, being taken seriously | Answer → a detail → a question only they can answer |
| Mockery of India | Mostly foreign pile-on accounts | A smile from the readers, not a fight | **Satirical roast** (below) |
| Hate, slurs | Anyone | Nothing | Hide |

**Step 3: acknowledge, validate, then inform.** Never "I understand, but…": the "but" wipes out the acknowledgement.
End the thought, start a new sentence.

**The roast, Amul-style.** Wit and wordplay aimed at the **claim**, never cruel to a person, never at a country, race
or religion. One true, sourced fact is the punchline ("Can't build anything? Then who parked a lander near the
Moon's south pole?"). One roast per thread; we never answer their comeback. Roast only plain mockery of India;
a good-faith sceptic gets respect, not a roast. *Why so careful:* a 2022 study found roasting raises engagement but
lowers persuasion, because readers judge it inappropriate, and practitioners advise small brands to "toast" more than
they "roast". Our roast is mainly for the Indian readers watching the thread, so it must make them smile, not wince.

**Step 4: the satisfaction test.** Before a draft goes to the owner, write one line on how it should land ("he feels
his pride was right", "she feels heard and learns one thing"). If the reply doesn't do that, rewrite it.

Sources (2026-10-29): Sewak, Humphrey and Sinha, AMTP Proceedings 2022 (roasting raises engagement, lowers persuasion),
https://digitalcommons.georgiasouthern.edu/amtp-proceedings_2022/70/ ; Northern Kentucky University, roasting vs
toasting ; acknowledge-validate-act and the "but" rule from customer-empathy guides (textexpander.com) and validation
research (arXiv 2402.12770) ; hope vs sarcasm detection (arXiv 2504.17974) ; Amul's gentle topical humour
(exchange4media.com, storyboard18.com).

### 2.7 Answer what they actually said (owner, 2026-10-29)
"For that simple comment why that much to explain?" … "Use sense of humour and think what actually he said and what
reply actually satisfies him."

@NECATR4D wrote "Superb detailing. My appreciations". We answered with a paragraph on Vande Bharat braking distance,
numbers spelled out like the narration. He had asked nothing: he was paying a compliment, and what satisfies a
compliment is knowing it reached a real person, with a smile. The reply now in place:
> Thank you. You noticed the detailing, so all those railway rulebooks we read were worth it. Our eyes are still
> recovering 😄

So, before drafting, answer three questions in the draft's `Feeling` line:
1. **What did they actually say?** A thank-you, a joke, a question, a point, a story. Answer *that*, not the film.
2. **What would satisfy them?** A compliment wants to be received; a question wants an answer; a joke wants a laugh
   back; a point wants to be taken seriously.
3. **Is the reply the size of the comment?** A few words of praise get one or two short lines back (about 10–25
   words), warm and with a light touch of humour, no film fact, and a question only if it comes naturally. Long,
   thoughtful comments earn the longer shapes in §2.5 and §3.1.

Two smaller lessons from the same reply:
- **Digits in replies.** Spelled-out numbers ("one hundred and thirty km per hour") are a narration rule for the voice;
  in a written comment "130 km/h" is easier to read, most of all for readers over 45.
- **One voice per reply.** Speak as "we" (the channel) all the way through; don't switch to "my" halfway.

**The second lesson the same day: no quiz, no tacked-on lines (owner, 2026-10-29).** On "The magic of metals." we
replied with the blade fact, then "Which trick surprised you most, the single crystal, the cooling air or the ceramic
coat? If machines like this are your kind of magic, you may like to subscribe." The owner: "Explaining the magic of
metal is fine, asking after that it feels generic robotic reply. Use natural simple words, simple kind of sentence
formation." So:
- **Simple sentences, the way people talk.** Short subject-verb lines, everyday words ("the blade should melt, but it
  doesn't"), no written-English build-ups ("Rolls-Royce says its blades work in heat up to…").
- **No quiz questions.** A multiple-choice question after a reply sounds like a teacher or a bot. Ask only what a
  friend at the tea stall would ask, or don't ask.
- **No tacked-on subscribe line.** If an invitation doesn't flow from the sentence before it, leave it out; one fewer
  ask beats one robotic ask.
- **Stop when the point has landed.** Fact plus smile is often the whole reply.

`scripts/yt.py edit` replaces the text of a reply we already posted (owner-approved only), and notes the edit in
`state/handled.csv`.

## 3. The comment types

Every comment gets one type. The type decides the action.

| Type | Who | Action |
| :--- | :--- | :--- |
| **A. Expert** | Engineers, insiders, people who worked there; long, specific comments. | Heart. Pin if it is the best comment on the video. Reply at peer level with one detail from our research and a question. |
| **B. Strategist** | Viewers proposing a workaround or another angle. | Agree with what is right, add the counterweight the film's facts support, keep it calm. |
| **C. Fact-checker** | Viewers who catch an error: a wrong photo, date, map, a repeated line. | Check it against sources first (§6). Right → thank them plainly, say exactly what was wrong, log it. Wrong → thank them and show the source, kindly. |
| **D. Joker** | Witty one-liners about a moment. | Heart. A short reply with the same wit, rooted in the subject. |
| **E. Cynic** | "Nothing will change", "India can never…". | Accept the frustration is earned where it is; answer with a fact from the film; end grounded, not preachy. One reply, no thread war. |
| **F. Personal** | Viewers sharing their own story, or asking for help with their own case (fraud, insurance, health). | Heart. Reply with warmth. For help: the general route the film showed and the verified helpline; never personal advice; never ask for private details in public. |
| **G. Spam / abuse** | Links, scams, impersonators ("WhatsApp me"), slurs, bad-faith trolls. | No reply. List under *Hide* for the owner; scams and impersonators are hidden at once. |

Plain praise ("Great video", "Best channel") gets a heart and, only when there is something real to add, a short reply
that gives them a reason to stay ("If you liked the Tata steel part, the Jamshedpur chapter at 7:40 is my favourite
moment."). Questions about a fact are type A/B/C by tone: answer from sources.

### 3.1 Reply shapes (shapes, not scripts)

Templates are a **shape** only. Every fact in a real reply comes from the film's sources, and every reply is written
fresh for that comment. The `[…]` parts are filled from the comment and the film's `claims.csv`.

- **Expert:** [their exact point, in their words] → [why it matters, one line] → [a sourced detail from our research
  that didn't make the cut] → [a question only an expert can answer].
  > The workforce gap you point to is the heart of it. [Sourced figure from claims row N] was the number that stopped
  > us during research. From your side, is the harder gap the people or the test facilities?
- **Strategist:** [what they get right] → [the counterweight, sourced] → [the balance].
  > True, a fighter is only as good as its radar and missiles. But [sourced fact on engine dependence], which is why
  > the film keeps coming back to engines. Both matter, on different timescales.
- **Fact-checker (right):** [thank them] → [what exactly was wrong] → [what we did].
  > You're right, thank you. That photo is from after [sourced year], so it shouldn't sit in the [year] scene. We've
  > noted it, and the correction is pinned.
- **Fact-checker (wrong):** [thank them] → [the source] → [leave room].
  > Good question to raise. The figure comes from [named source, year]. Some reports give [other figure], and the
  > difference is [reason from sources].
- **Joker:**
  > On a slide it's four steps. In a foundry, step one alone takes a decade.
- **Cynic:**
  > The frustration is fair: [the failure the film itself showed]. But [the sourced change the film showed]. That's
  > not a promise, it's [what is actually built or signed].
- **Personal (help):**
  > Sorry this happened to you. The first step the film shows is [route]; the official helpline is [verified number
  > from the film]. Please don't share account details here in the comments.

## 4. Never say

| Never | Why | Instead |
| :--- | :--- | :--- |
| "Thanks for watching! Please subscribe!" (or "hit subscribe", "stick around") as a stock line | Sounds like a bot; adds nothing. | Add something first; then, if §2.5 allows, a fresh personal invitation. |
| "YouTube videos have a time limit." | Defensive. | "We had to keep that part short. You've filled in what we left out." |
| "You didn't watch the full video." | Starts a fight in public. | "At 6:15 we go through the numbers behind that." |
| "Jai Hind! India will beat everyone!" | Flattens a careful film into chest-thumping. | A grounded line about what is actually built. |
| "Incredible eye!", "Honoured to have minds like yours", "Exceptional breakdown" | Gushing; reads as flattery or a bot. | Start with their point. |
| "Our team…", "in our remastered version…", "I read every comment" | Untrue unless it is. | Say only what is real. |
| Facts from memory | Our fact rule (CLAUDE.md). | A fact from `claims.csv` or a checked source. |

## 5. The workflow

### 5.1 One run
1. Fetch new comments and replies on both channels since the last run (`scripts/yt.py fetch`, §5.5). Skip ids in
   `state/handled.csv`. Also fetch replies under our own replies: a viewer answering us gets a turn too.
2. Match each video id to its film folder (`config/videos.yaml`) and read that film's `claims.csv`, script and
   `youtube/description.md` (chapters, for timestamps).
3. Sort every comment (§3), draft replies (§2, §3.1), check every fact against the film's sources, and run the
   checks in §5.3.
4. Send the batch in the chat (§5.2). Wait for the owner.
5. Post exactly what was approved; log every comment (posted, skipped, heart-only, hidden) in `state/handled.csv`.
6. Commit the state files, PR to `main`, merge.

### 5.2 The batch message (phone-first)
One message per run. Newest videos first; inside a video, the most valuable comments first.

```
Built on Bharat · <video title> (3 new)

#1 · Expert · @name · 2 h · <profile: regular / new, subscribed yes / unknown>
"<their comment, trimmed to ~300 characters>"
Feeling: <what they felt when they wrote it> · Lands as: <how it should feel to them> (§2.6)
→ <draft reply>
  source: claims.csv row 14

#2 · Joker · @name · 5 h
"<comment>"
→ <draft reply>

Be Practical with Kishore · <video title> (2 new)
#3 · Personal · @name · Telugu
"<comment>"
→ <draft reply in Telugu>

Studio (do these in the YouTube Studio app):
❤ heart: #1, #2, #3
📌 pin: #1 (best comment on <video>)
🚫 hide: @spamname on <video> (WhatsApp scam)
```

Owner replies, for example: `approve 1,3` · `2: <new text>` · `skip 2` · `all` · `hide @name`. Anything not named is
left unposted and stays in the next batch once, then is logged as skipped.

### 5.3 Checks before a draft reaches the owner
- Every fact traces to a source shown under the draft. No fact without a source.
- No banned phrase (§4), no link, no Hindi tag on Built on Bharat. A subscribe invitation only as §2.5 allows.
- The viewer's profile (§2.4) was read, and the reply fits who they are.
- Language matches the commenter (Be Practical with Kishore) or is English (Built on Bharat).
- Timestamps are right for the published cut.
- Read it aloud in your head as the narrator: warm, short, human. Not a teacher, not a press release.

### 5.4 Cadence
- **Normal:** two runs a day, around 1 pm and 9 pm IST (the evening run catches the 6:30–10:30 pm viewing wave). The
  scheduled task (owner, 2026-10-29) fires at 12:47 and 21:41 IST, each in a fresh cloud session that runs §5.1 and
  brings the batch to the owner in that session's chat. Off-minute times dodge the busy top of the hour.
- **Launch window (first 48 hours after an upload):** extra runs at about 1, 3 and 8 hours after the video goes public.
  Early replies matter most: they set the tone of the thread.
- Runs share the usage limit with video work; when the owner is mid-render, skip a normal run rather than starve it.

### 5.5 Commands (`scripts/yt.py`, Python 3 + `pip install -r requirements.txt`)
| Step | Command | Notes |
| :--- | :--- | :--- |
| Check access | `python3 scripts/yt.py whoami` | `OK` per channel when its token signs in as the right channel. |
| New uploads | `python3 scripts/yt.py videos` | Adds new video ids to `config/videos.yaml` with `film: null` (public feed, latest 15; `--api` lists every upload). Map each to its film folder by title before drafting. |
| Fetch | `python3 scripts/yt.py fetch` | Writes `runs/<stamp>/new.json` (gitignored): new comments and replies not in `state/handled.csv`, our own excluded, YouTube's held-for-review queue flagged `held: true`, plus new answers under threads we replied to in the last 14 days. Each comment carries `our_last_reply` (when the channel last replied in that thread, also by hand in Studio) and `after_our_reply`. `--days` sets how far back to page (default 7). |
| Post | `python3 scripts/yt.py post approved.json --confirm` | Only after the owner's approval. JSON list of `{comment_id, thread_id, channel, video_id, author, type, language, text}`. Replies go under the thread (YouTube has one level of replies); to answer a reply, start the text with `@their-handle`. Already-replied ids are skipped, so a re-run never double-posts. |
| Edit | `python3 scripts/yt.py edit --channel C --reply REPLY_ID --text "…" --confirm` | Replaces the text of one of our logged replies (the `reply_id` in `state/handled.csv`) after the owner approves the new text; adds `edited <time>` to that row's note. |
| Hide | `python3 scripts/yt.py hide --channel C --comment ID [--ban] --confirm` | Rejects the comment (gone from public view). `--ban` also hides the author from the channel. Owner's call only. |
| Log | `python3 scripts/yt.py record --channel C --comment ID --action skipped\|heart\|pin\|heart+pin\|held\|no-reply` | Every comment in a batch gets a row, posted or not. |

Channel keys: `builtonbharat`, `bepracticalwithkishore`. Secrets: `docs/SETUP.md`. Offline tests:
`python3 -m unittest tests/test_yt.py`.

`config/videos.yaml` notes: the two Moon/jet-engine uploads (`_4G7-vTadZQ`, `m4h_2gXESp0`) both map to
`projects/jet-engine-paradox`; check which cut each is before quoting a timestamp.

### 5.6 Lessons from the first run (2026-10-29)
- **The owner also replies by hand in Studio.** Before this repo, most top-level comments already had a channel reply.
  `fetch` now marks `our_last_reply` / `after_our_reply` on every comment: draft only for threads with no channel reply
  and for viewer replies posted after ours, so we never answer twice or contradict a hand reply. The first run logged
  the 64 already-answered comments as `no-reply`.
- **Hand replies broke a few rules** (subscribe asks, numbers from memory such as toilet and tap-water counts). They
  stay as they are; new replies go through the batch so every fact has a row.
- **Pile-ons from foreign accounts** (the rare-earth film drew dozens of "toilets", "brag" and racist one-liners): no
  thread wars. Since the owner's directive (§2.5), one or two of the most-seen jabs per batch may get a single witty,
  sourced reply. Hide slurs and racist or sexist lines; leave plain mockery alone; never step into
  viewer-against-viewer fights, even when a viewer defends India rudely. Reply to the few real arguments with one
  sourced fact.
- **Two fetch bugs fixed:** replies read through `comments.list` carry no `videoId` (now taken from the thread), and a
  thread holding one held comment came back in both listings (now listed once; only comments seen in the held listing
  alone are `held`).
- **Uploads older than the film repo** (`mh1rfSrl6fA`, 2026-10-03) have no `claims.csv`: heart or a non-factual reply only.

## 6. Corrections (errata)
1. Check the viewer's claim against the film's sources and a fresh source if needed. Never agree or disagree from
   memory.
2. **Right:** reply with thanks and exactly what was wrong; add a row to `state/errata.csv`; tell the owner in the batch
   so the film repo logs it (its `review/` notes) and the next film avoids it. If it changes a fact viewers rely on, the
   owner pins a short correction comment (draft one for him).
3. **Wrong:** reply kindly with the source. Never mock.
4. **Unclear:** tell the owner what you found; don't reply until it's settled.

## 7. Launch kit for every new film
Each film's YouTube package (in its film repo, `youtube/`) gains a **pinned opening comment** ready before upload:
- The film's central question in one or two lines, then a real question with two clear sides the viewer can pick,
  drawn from the film. No link, no subscribe ask, no "I'm reading every response".
- Written in the channel's voice; for Be Practical with Kishore, in the film's language.
- By about hour 8, if a viewer has posted a better comment (type A), the owner pins theirs instead, and we reply under it.

Example shape (facts must come from the film):
> [The paradox from the film, one line]. So which matters more: [side A] or [side B]? Tell us where you stand.

KPIs per release (a guide, not a target): opening comment pinned at launch; the first thoughtful comments answered in
the first few hours; the best viewer comment pinned by hour 8; every correct correction acknowledged; spam hidden.

## 8. What we changed from the owner's document, and why (2026-10-29)
- **Template numbers removed.** The document's examples carried figures with no sources (workforce counts, plant
  capacities, scheme sizes). A reply is public like the film, so the same fact rule applies.
- **Subscribe asks removed.** The document bans "please subscribe" but three templates ended with "hit subscribe /
  stick around". We dropped them all. *Changed by the owner on 2026-10-29:* personal invitations are back, within §2.5.
- **No untrue claims.** "Our visual team", "noted for our remastered pass" and "I'm reading every response" are said
  only when true.
- **Toned down.** "Incredible eye", "Honored to have minds like yours", "man" → start with their point, warm and plain.
- **Two voices, not one.** Built on Bharat and Be Practical with Kishore sound different; Be Practical with Kishore
  replies in the commenter's language.
- **"Algorithmic weapon" claims softened.** We don't claim a published comment-velocity formula (§1).
- **Added type F (personal stories and help requests)** and safety rules for money, health and legal questions.
- **Kept:** the four traits, the types, de-escalation, hiding spam and trolls, the opening comment, early replies,
  pinning the best viewer comment, the errata habit.

## 9. What the YouTube API can and can't do
- **Can:** read comment threads on a channel's videos; post a reply under a comment; set a comment's moderation status
  (publish, hold, reject) and ban its author from the channel.
- **Can't:** heart a comment, pin a comment. These stay manual in the YouTube Studio app; every batch lists them.
- **Quota:** 10,000 free units a day per Google Cloud project. Reading a page of comments costs about 1 unit, posting a
  reply about 50, so a day's work fits easily.
- **Access:** one OAuth sign-in per channel, done once by the owner on the phone (`docs/SETUP.md`). Tokens live in
  environment secrets only.
