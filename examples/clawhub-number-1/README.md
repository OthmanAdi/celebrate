# Example: Planning with Files, #1 on ClawHub

A complete run, kept as the reference for what the skill produces.

**The moment.** On 3 September 2026 the skill `planning-with-files` by
[@othmanadi](https://clawhub.ai/othmanadi) sat first on the ClawHub Skills
Trending list, showing 266 downloads. The cards in `social/` are built around a
crop of that list.

**The screenshot itself is not in this repo, on purpose.** A raw capture is a
picture of somebody's actual screen, and it carries their tabs, bookmarks and
whatever else was open. `proof/` is in `.gitignore` for that reason. Point
`celebration.json` at your own capture when you rebuild.

**The numbers.** Stars and forks came from the GitHub API on the build date:

```bash
gh api repos/OthmanAdi/planning-with-files \
  --jq '{stars:.stargazers_count,forks:.forks_count,created:.created_at}'
# {"created":"2026-01-03T07:37:28Z","forks":2219,"stars":26612}
```

The rank and the download count are what the screenshot shows. A trending position
is a snapshot: it had already moved by the following day, which is normal and is
why the claim is dated everywhere it appears.

**Rebuild it:**

```bash
python ../../scripts/prepare_proof.py proof/00-original.png --out proof \
       --crop 600,352,1640,658 --ref-width 1998 --name trending
python ../../scripts/render_cards.py --config celebration.json --out ./social
```

Twelve files: six formats, each with and without the call to action.
