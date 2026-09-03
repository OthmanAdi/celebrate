---
name: celebrate
description: >-
  Turn a real win into a set of designed, on-brand image assets for social media,
  email and a profile, in every size those channels need, built around a verified
  screenshot as proof. Use whenever someone lands a ranking, a milestone, a launch,
  a star count, an award, an acceptance, a shipped release, a chart position or any
  other public result and wants to post it, show it off, put it in a newsletter, or
  use it as hiring or fundraising evidence. Triggers on "make a screenshot I can
  post", "turn this into a social card", "banner for LinkedIn", "we hit #1",
  "we just crossed N users", "announcement image", "show off", "brag post",
  "celebrate this", or a pasted screenshot of a leaderboard, dashboard or chart.
---

# Celebrate

A win is only worth what the evidence shows. A raw screenshot of a browser window
is evidence, but it is cropped wrong for every channel, it leaks the author's
bookmark bar, its dark UI turns to mud once a feed re-encodes it, and it says
nothing about who did the work.

This skill takes the moment and produces a set of assets that survive contact
with a feed: correct pixel sizes, retina, the proof embedded and legible, the
verified numbers next to it, and the author's name attached.

## The order of work

Do these in order. Steps 1 and 2 are the ones people skip, and they are the ones
that make the difference between a post that lands and a post that gets a
correction in the replies.

### 1. Capture the moment, before it moves

Rankings, trending lists and live counters are **snapshots**. By the time the
assets are built, the number may have changed. That is normal and it is not a
failure.

- If the person already sent a screenshot, that screenshot is the record. Use it.
  Do not go re-capture a live page hoping the moment held; if it did not, you have
  destroyed the evidence and the claim with it.
- If nothing was captured yet, capture immediately, before any other step.
- Always keep the untouched original. Everything else is a derivative.
- Timestamp the claim in the copy and in the folder name. "Trending #1 on
  ClawHub, 3 September 2026" is honest and stays true forever. "Trending #1 on
  ClawHub" rots the moment the list moves.
- If the live position has already changed by the time you build, say so plainly
  once, in the report to the person, and keep building from the captured moment.
  It is their achievement either way.

### 2. Verify every number against a live source

Never take a figure from memory, from an old file, or from the person's own
recollection. Pull it and cite where it came from.

```bash
gh api repos/OWNER/REPO --jq '{stars:.stargazers_count,forks:.forks_count,created:.created_at}'
curl -s "https://api.npmjs.org/downloads/point/last-month/PACKAGE"
```

Read `references/verify.md` for the sources worth checking per kind of win, and
for the claims to refuse to put on an image.

### 3. Prepare the proof crop

```bash
python scripts/prepare_proof.py shot.png --out proof/ \
    --crop 600,352,1640,658 --ref-width 1998
```

`--crop` is `left,top,right,bottom`. Pass `--ref-width` when you read the
coordinates off a scaled preview rather than the file itself, which is the normal
case: the script rescales them for you.

What to crop to, and why, is in `references/proof.md`. The short version: keep the
part of the interface that proves the claim, plus enough surrounding chrome that
it is recognisably that product. Remove browser tabs, bookmark bars, sidebars and
anything else personal.

### 4. Write the config

Copy `templates/celebration.json`, fill it in, put it next to the proof folder.
Only `headline` is required. Guidance on the copy, especially the subtitle and
the choice of stats, is in `references/copy.md`.

### 5. Render

```bash
python scripts/render_cards.py --config celebration.json --out ./social
```

Every requested format is rendered at its exact size and captured at 2x. If the
config has a `cta`, each format is rendered twice: once plain, once with the ask.
Formats and their sizes are in `references/formats.md`.

### 6. Look at what you rendered

**Open the images. Every one of them.** A card can render, report OK, and still be
broken: a headline colliding with a stat row, a screenshot stretched out of
proportion, a name wrapping onto two lines. The renderer cannot see any of that.

`references/rendering.md` lists the failure modes this design has actually hit,
each with its cause and its fix. Read it when something looks wrong before you
start changing numbers at random.

### 7. Write the captions

The images carry the claim. The caption carries the story: what the thing does,
who it is for, what the person is open to next. Formulas and worked examples are
in `references/copy.md`.

### 8. Hand it over

Write a short `README.md` into the output folder listing what each file is, where
each number came from, and the captions ready to paste. The person should be able
to open that folder in three months and still know what they are looking at.

## The one judgement call to hand back

If the config carries a `cta` such as "open to work", the renderer produces both
sets. **Do not decide for the person which one to post.** Someone currently
employed may be delighted with the achievement post and not want an availability
line on it. Produce both, say which is which, let them choose.

## Design

The look is a dark editorial card: one enormous number, a headline, the proof in a
framed panel, a row of verified stats, and the author's line at the bottom.
Everything is themeable through `theme` in the config.

The default palette is deliberately near-black with a single warm accent. When
celebrating a result on a specific platform, sample that platform's own accent
colour and background into the theme, so the card reads as an extension of the
place the win happened rather than a generic quote card.

`references/design.md` has the full system: tokens, layout anatomy, and the rules
that keep the giant numeral from colliding with everything around it.

## Files

```
scripts/render_cards.py    config in, PNG set out
scripts/prepare_proof.py   raw screenshot in, embeddable crop out
templates/celebration.json the config, commented
references/formats.md      every size, and what it is for
references/design.md       tokens, anatomy, and the numeral rules
references/rendering.md    headless capture, the fit pass, and the real bugs
references/proof.md        what to crop, what to remove, what to keep
references/verify.md       where each kind of number comes from
references/copy.md         headline, subtitle, stats and caption formulas
examples/                  a complete worked example, config and all
```

## Requirements

Python 3.8+, Pillow, and Chrome, Chromium or Edge. The renderer finds the browser
itself; override with `CELEBRATE_CHROME` or `--chrome`.
