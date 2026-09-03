# Formats

Every key accepted in `formats`. Sizes are CSS pixels; files are written at 2x.

| Key | Size | Layout | Use it for |
|---|---|---|---|
| `x` | 1600 x 900 | wide | X / Twitter in-feed. 16:9 is shown uncropped in the timeline. |
| `x-square` | 1200 x 1200 | square | X when you want more vertical space in the feed. |
| `linkedin` | 1200 x 627 | wide | LinkedIn in-feed, and the same file works as an OpenGraph image. |
| `linkedin-cover` | 1584 x 396 | banner | LinkedIn profile background. |
| `square` | 1080 x 1080 | square | Instagram and Mastodon in-feed. |
| `story` | 1080 x 1920 | story | Instagram/Facebook story, Reel cover, YouTube Short cover. |
| `email-banner` | 1200 x 400 | banner | Email header. Renders at 600pt wide on most clients. |
| `github-social` | 1280 x 640 | wide | GitHub repo social preview, in repo Settings. |
| `slide` | 1920 x 1080 | wide | A slide, a screen share, a conference deck. |

## The four layouts

**wide** — claim column on the left (hero number, headline, subtitle), proof panel
on the right, stats and author across the bottom. The default for anything from
16:9 to about 2:1.

**square** — hero and headline stacked above a full-width proof panel, stats as a
two-by-two grid, author at the foot. Four stat columns do not hold a line at 1080
wide, which is why the grid exists.

**story** — the same stack, centred vertically with the spacers doing the work, and
generous margins so nothing lands under a platform's own interface. Keep the
important content between roughly 15% and 85% of the height: stories put a profile
row at the top and a reply box at the bottom.

**banner** — one dense horizontal line: hero numeral, rule, eyebrow, headline,
one summary line of stats. No proof panel; at 400px tall an embedded screenshot is
present but unreadable, which is worse than absent. Headline and summary are
`nowrap` and the fit pass scales them to fit.

## Choosing

Two or three files, not nine. Rendering everything and posting everything reads as
spam and dilutes the moment.

- Posting to one place: that format, plus `email-banner` if a newsletter is coming.
- Announcing broadly: `x`, `linkedin`, `square`, `story`.
- A repository result: add `github-social` and set it in repo Settings.

## Adding a size

Add an entry to `FORMATS` in `scripts/render_cards.py` with `w`, `h`, `layout` and
a `label`, and add a row here. Reuse an existing layout unless the aspect ratio is
genuinely unlike all four.
