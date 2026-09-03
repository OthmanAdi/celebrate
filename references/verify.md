# Verify

Every number on the card is a public claim with the author's name under it. Pull
each one from a live source at build time. Not from memory, not from a note, not
from the person's recollection of last week.

## Where the numbers come from

| Claim | Source |
|---|---|
| GitHub stars, forks, age | `gh api repos/OWNER/REPO --jq '{stars:.stargazers_count,forks:.forks_count,created:.created_at}'` |
| GitHub releases, contributors | `gh api repos/OWNER/REPO/releases --jq 'length'`, `.../contributors?per_page=100` |
| npm downloads | `curl -s https://api.npmjs.org/downloads/point/last-month/PACKAGE` |
| PyPI downloads | pypistats, or the BigQuery public dataset |
| Crate downloads | `curl -s https://crates.io/api/v1/crates/NAME` |
| Docker pulls | `curl -s https://hub.docker.com/v2/repositories/OWNER/NAME/` |
| Ranking or leaderboard position | The captured screenshot, plus the site's API if it has one |
| Registry download counts | The listing page and the site's API, which frequently disagree; see below |
| Users, revenue, customers | The person's own dashboard. You cannot verify these; attribute them. |

## When sources disagree

A site's own listing and its public API often report different figures, because they
count different things over different windows. Prefer the number visible in the
screenshot, because that is the number a reader can check against the proof panel.
If a stat has no visible counterpart in the proof, take it from the API and be ready
to say which endpoint.

## Rounding

Round down, never up. 26.612 stars can be written as "26.6k" or "26.612", never as
"almost 27k" and never as "27k". A rounded-up figure is the single easiest thing for
a sceptical reader to catch, and catching it discredits every other number on the
card.

Match the person's locale for separators and keep it consistent across the set.

## Claims to keep off the image

- **Superlatives you have not measured.** "The most popular X" needs a ranked list
  covering every X. "#1 trending on <site> on <date>" is checkable and enough.
- **Comparisons to named competitors.** The proof panel already shows what it
  outranked. Saying it in the copy turns a result into a fight.
- **Aggregate figures assembled from several sources** presented as one number,
  unless the card says how it was composed.
- **Anything about a person who has not agreed to appear.** Other people's handles
  in a leaderboard screenshot are public and fine; naming them in the copy is not.
- **Employment status the person has not confirmed for this post.** See the CTA note
  in `SKILL.md`.

## Record what you used

Put the source of every figure in the output folder's README, with the date it was
pulled. Six weeks later, when someone asks where a number came from, that line is
the difference between a fact and an assertion.
