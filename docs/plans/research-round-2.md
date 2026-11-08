# Channel research, round 2

Round 1 (8 Nov 2026) researched all 40 subjects and subscribed Noam to 188 new channels, but every
research agent hit the session's shared 200-web-search limit partway through. Round 2 fills the gaps.

**Rules that don't change**
- **Never unsubscribe** from any channel, including ones research criticises. Flag them in text only.
- Evidence bar: each pick needs 2+ independent real recommendations (Reddit, forums, expert blogs,
  podcasts, interviews); a credentialed expert counts double; SEO listicles don't count. Drop channels
  experts flag as inaccurate or plagiarising. Active = an upload in the last 12 months.
- Hebrew channels count in every subject (Noam is Israeli).
- Up to 10 picks per subject; fewer is fine, never pad.

## Where things are (local, git-ignored)

| What | Where |
|---|---|
| Round 1 results (picks, rejected, notes/leads per subject) | `research/*.json` |
| Review page generator + template | `research/build_review.py`, `research/review_template.html` |
| Review page (approvals saved in its `decisions` db) | https://claude.ai/artifact/JbZTj3vEMLVqExyYiWarzr |
| Add-only subscribe script | `research/subscribe.py <client_secret.json>` |
| OAuth client for subscribing (Cloud project `youtube-mixer-subscribe`, testing mode, test user noamros9@gmail.com) | `client_secret.json` |
| Round 1 run report | `research/subscribe_report.json` |

## Tickets

| # | Ticket | Tier | Blocked by | Branch | Status |
|---|---|---|---|---|---|
| 0 | Finish round 1: subscribe the last 6 picks (The Anfield Wrap onward), stopped by the daily API quota on 8 Nov | ship | none | none (local) | todo |
| 1 | Refresh the exclusion list: current subscriptions (~740) + every round-1 pick and rejection | prep | none | none (local) | todo |
| 2 | Research the thin subjects (below) with more, smaller agents | research | 1 | none (local) | todo |
| 3 | Merge round-2 results into the review page, republish to the same URL | review | 2 | none (local) | todo |
| 4 | Noam approves; subscribe the approved ones; add them to `categories.txt` | ship | 3 | `feature/round-2-channels` | todo |
| 5 | Shut down Cloud project `youtube-mixer-subscribe`, delete `client_secret.json` | cleanup | 4 | none | todo |

**0. Finish round 1.** Run `python research/subscribe.py client_secret.json` again after the quota
resets (midnight Pacific, 10:00 Israel). The script skips channels already subscribed, so it only adds
the last 6. Noam signs in again. Nick Zentner has no YouTube channel URL; Noam subscribes to him by hand.
Done when: the run reports 0 to add, or only quota-free successes.

**1. Exclusion list.** Test first: n/a (data prep). Done when: one file lists every subscribed channel id
(from the public subscriptions API, as `update.py` reads it) plus every handle in `research/*.json`, and
no round-2 pick appears in it.

**2. Research.** Round 1 found these thin (picks so far):

- 0: Productivity & Learning
- 2: 20th Century & World Wars, Basketball, Fitness & Health, General Science, Travel, Wine
- 3: Books, Documentaries, Fantasy & Sci-Fi Books, Geography & Geopolitics
- 4: Beer (only homebrewing so far; beer appreciation still to do), Biology & Nature, DevOps & Cloud,
  Earth & Climate, Psychology & Medicine
- **Hebrew: every subject.** Only Ran Levi and the Davidson Institute were verified.

Start from each subject's `notes` in `research/*.json`. They list the leads round 1 found but couldn't
verify, e.g. Battle Order, The Operations Room, Imperial War Museums, Townsends, Modern History TV,
Hello Future Me, Ben Reads Good, Christian Lempa, Techno Tim, Lawrence Systems, Just Have a Think,
GeologyHub, Kati Morton, YUV AI, Yam Olisker, Reversim, Weizmann Institute, Academy on the Net, Yad Vashem.

Budget: `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION=500` is set in `~/.claude/settings.json` (8 Nov 2026),
shared by all agents in the session. Use 3–4 subjects per agent and give each agent about 60 searches.
Done when: each subject above has its picks, or a note saying why there are none.

**Hebrew leads tier (decided 8 Nov 2026).** A Hebrew channel that misses the 2-source bar can still be
listed as a *lead* if it has one strong source (an expert, institution or well-known podcast) and an
upload in the last 12 months. Record it under a separate `leads` list per subject (same fields as a
pick, with `strength` ≤ 2). Ticket 3 shows leads in their own section, apart from the full picks.

**3. Review page.** Write the results to `research/round2/*.json` in round 1's schema, extend
`build_review.py` to merge them, then republish `research/review.html` to the same artifact URL.
Done when: the page shows round-2 picks marked as new, Hebrew leads in their own "Leads" section, and
earlier decisions are kept.

**4. Subscribe.** Run `python research/subscribe.py client_secret.json` against the approved picks only.
The script currently takes every pick; change it to read the `decisions` collection, status `approve`.
Noam signs in himself and clicks Allow. Then add the picks to `categories.txt` (`research/new_categories.json`
maps handle → subjects), run `python test_update.py`, and push with Noam's OK.
Test first: a `subscribe.py` dry-run flag listing exactly the approved channels.
Done when: the run report shows 0 failures and the site shows the channels in their subjects.

**5. Cleanup.** Done when: the project is listed as pending deletion and `client_secret.json` is gone.

## Resume here

**State at handoff (8 Nov 2026, late):** 182 of 188 round-1 channels are subscribed, and all 188 are
placed in `categories.txt` (pushed). Nothing is in progress. The subscribe quota resets at 10:00 Israel time.

Plan for the next session (evening of 9 Nov):
1. **Ticket 0:** `cd C:\Users\noamr\youtube-mixer && python research/subscribe.py client_secret.json`
   Noam signs in (noamros9@gmail.com → Continue → Allow). Expect about 6 added.
2. **Tickets 1–3:** research the thin subjects, then republish the review page. Noam approves picks there.
3. **Ticket 4** (subscribe the approved picks and add them to subjects), then **ticket 5** (cleanup).

Start the session with: *"Read docs/plans/research-round-2.md and continue from Resume here"*.

## Challenge round

- **Weakest assumption:** that more searches will find Hebrew channels that meet the bar. Round 1
  looked and found almost nothing that had two independent endorsements. This wasn't verified. If round
  2 confirms it, consider a lower bar for Hebrew (one strong source plus an activity check), shown as a
  separate "leads" tier on the review page, not mixed with the full picks. Noam approved the leads tier
  up front (8 Nov 2026), so tickets 2 and 3 now include it.
- **What I hadn't read:** I hadn't checked the round-1 per-subject `notes`. Opening them showed they
  already name about 20 concrete leads, so ticket 2 now starts from them instead of searching from
  scratch.
- **The lazier version, not proposed:** reuse round 1's "subscribe to every pick" flow with no review.
  Noam approved that once, for round 1 only. Approval doesn't carry over, so ticket 4 keeps the review step.
