#!/usr/bin/env python3
"""Render one celebration into a full set of social and email image assets.

Reads a JSON config (see templates/celebration.json), renders every requested
format through headless Chrome at 2x device scale, and writes PNGs next to it.

    python render_cards.py --config celebration.json --out ./social

Design notes that are load-bearing, not decoration:

* Every card is laid out at its exact CSS pixel size and captured at 2x, so the
  file a platform receives is already retina and survives re-compression.
* A fit pass runs in the page after load. It grows the logical box and scales it
  back down until nothing overflows in either axis, so a long name or an extra
  stat shrinks the card instead of clipping it. Hand-budgeting pixel heights per
  format does not survive a copy change; this does.
* Children of the card never flex-shrink. A squashed child hides its overflow,
  and the fit pass can only react to overflow it can measure.
"""

import argparse
import base64
import json
import mimetypes
import os
import shutil
import subprocess
import sys
from typing import NoReturn

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(HERE)

# Canonical sizes. Keep these in sync with references/formats.md.
FORMATS = {
    "x":               dict(w=1600, h=900,  layout="wide",   label="X / Twitter in-feed"),
    "x-square":        dict(w=1200, h=1200, layout="square", label="X / Twitter square"),
    "linkedin":        dict(w=1200, h=627,  layout="wide",   label="LinkedIn / OpenGraph"),
    "linkedin-cover":  dict(w=1584, h=396,  layout="banner", label="LinkedIn profile cover"),
    "square":          dict(w=1080, h=1080, layout="square", label="Instagram / Mastodon square"),
    "story":           dict(w=1080, h=1920, layout="story",  label="Story / Reel / Short"),
    "email-banner":    dict(w=1200, h=400,  layout="banner", label="Email header"),
    "github-social":   dict(w=1280, h=640,  layout="wide",   label="GitHub repo social preview"),
    "slide":           dict(w=1920, h=1080, layout="wide",   label="Slide / screen share"),
}

DEFAULT_THEME = {
    "bg": "#0a0708",
    "panel": "#140d0e",
    "line": "#2a1c1d",
    "accent": "#ff5a45",
    "accent_dim": "#b8392a",
    "ink": "#f6efec",
    "mute": "#9a8a86",
    "faint": "#6b5c59",
    "mono": '"Cascadia Mono","Consolas",ui-monospace,monospace',
    "sans": '"Segoe UI Variable Display","Segoe UI",system-ui,-apple-system,sans-serif',
    "grid": True,
    "bloom": True,
}


def die(msg) -> NoReturn:
    sys.stderr.write("celebrate: " + msg + "\n")
    raise SystemExit(2)


def find_chrome(explicit=None):
    """Chrome, Edge or Chromium. Any of them renders these cards identically."""
    if explicit:
        if not os.path.exists(explicit):
            die("browser not found at " + explicit)
        return explicit
    env = os.environ.get("CELEBRATE_CHROME")
    if env and os.path.exists(env):
        return env
    candidates = [
        r"C:/Program Files/Google/Chrome/Application/chrome.exe",
        r"C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        r"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
        r"C:/Program Files/Microsoft/Edge/Application/msedge.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    for name in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge", "chrome"):
        found = shutil.which(name)
        if found:
            return found
    die("no Chrome/Chromium/Edge found. Set CELEBRATE_CHROME to the binary path.")


def data_uri(path, base):
    p = path if os.path.isabs(path) else os.path.join(base, path)
    if not os.path.exists(p):
        die("proof image not found: " + p)
    mime = mimetypes.guess_type(p)[0] or "image/png"
    with open(p, "rb") as fh:
        return "data:%s;base64,%s" % (mime, base64.b64encode(fh.read()).decode("ascii")), p


def image_size(path):
    """Intrinsic size, so the layout reserves the right box before decode."""
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except Exception:
        return None


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def css(theme):
    grid = """
body::after {
  content:""; position:absolute; inset:0; opacity:.35; pointer-events:none;
  background-image:
    linear-gradient(rgba(255,255,255,.028) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.028) 1px, transparent 1px);
  background-size:44px 44px;
  mask-image:radial-gradient(85% 70% at 50% 40%, #000 30%, transparent 100%);
}""" if theme.get("grid", True) else ""
    bloom = """
body::before {
  content:""; position:absolute; inset:0; pointer-events:none;
  background:
    radial-gradient(120%% 80%% at 50%% -10%%, %s, transparent 60%%),
    radial-gradient(70%% 50%% at 100%% 100%%, %s, transparent 70%%);
}""" % (theme["accent"] + "33", theme["accent"] + "12") if theme.get("bloom", True) else ""

    return """
* { margin:0; padding:0; box-sizing:border-box; }
:root {
  --bg:%(bg)s; --panel:%(panel)s; --line:%(line)s;
  --accent:%(accent)s; --accent-dim:%(accent_dim)s;
  --ink:%(ink)s; --mute:%(mute)s; --faint:%(faint)s;
  --mono:%(mono)s; --sans:%(sans)s;
}
html,body { width:100%%; height:100%%; }
body {
  background:var(--bg); color:var(--ink); font-family:var(--sans);
  overflow:hidden; position:relative; -webkit-font-smoothing:antialiased;
}
%(bloom)s
%(grid)s

/* Size and transform are driven by the fit pass. */
.wrap {
  position:relative; z-index:1; width:100%%; height:100%%;
  transform-origin:top left; display:flex; flex-direction:column;
}
/* Nothing shrinks: a squashed child hides overflow the fit pass needs to see. */
.wrap > * { flex:none; }
.wrap > .spacer { flex:1 1 auto; min-height:0; }
.row { display:flex; align-items:center; min-height:0; }

.eyebrow {
  font-family:var(--mono); letter-spacing:.22em; text-transform:uppercase;
  color:var(--accent); display:flex; align-items:center; gap:.7em; white-space:nowrap;
}
.eyebrow .dot { width:.55em; height:.55em; border-radius:50%%; background:var(--accent); box-shadow:0 0 12px var(--accent); }
.eyebrow .sep { color:var(--faint); }
.eyebrow .plain { color:var(--mute); letter-spacing:.18em; }

/* line-height 1 on the container AND the glyph. A tighter line box lets a big
   numeral bleed out of its own box and collide with whatever sits above it. */
.hero { display:flex; align-items:center; gap:.10em; line-height:1; }
.hero .pre { color:var(--accent-dim); font-weight:600; line-height:1; }
.hero .val {
  font-weight:800; letter-spacing:-.04em; line-height:1; display:block;
  background:linear-gradient(180deg,#fff 8%%,var(--accent) 96%%);
  -webkit-background-clip:text; background-clip:text; color:transparent;
  filter:drop-shadow(0 6px 34px %(accent)s73);
}
.hero .tag {
  font-family:var(--mono); color:var(--mute); letter-spacing:.16em;
  text-transform:uppercase; line-height:1.5; margin-left:.5em;
  padding-left:.9em; border-left:1px solid var(--line);
}
.hero .tag b { display:block; color:var(--accent); font-weight:600; }

h1 { font-weight:700; letter-spacing:-.025em; line-height:1.02; }
h1 em { font-style:normal; color:var(--accent); }
.sub { color:var(--mute); line-height:1.42; }

.shot {
  border:1px solid var(--line); border-radius:14px; overflow:hidden; background:var(--panel);
  box-shadow:0 34px 90px rgba(0,0,0,.75), 0 0 0 1px %(accent)s24, 0 0 70px %(accent)s1a;
}
.shot .bar {
  display:flex; align-items:center; gap:.6em; padding:.62em 1em;
  border-bottom:1px solid var(--line); background:var(--bg);
  font-family:var(--mono); color:var(--faint);
}
.shot .bar i { width:.62em; height:.62em; border-radius:50%%; background:var(--line); display:block; }
.shot .bar i:first-child { background:var(--accent-dim); }
.shot .bar span { margin-left:.5em; }
/* height:auto is required: the width/height attributes reserve the box before
   decode, and without it the attribute height wins and the shot is stretched. */
.shot img { display:block; width:100%%; height:auto; }

.stats { display:flex; align-items:stretch; border-top:1px solid var(--line); }
.stats .s { flex:1; padding:1.1em 0 0; min-width:0; }
.stats .s + .s { border-left:1px solid var(--line); padding-left:1.4em; }
.stats .v { font-family:var(--mono); font-weight:700; color:var(--ink); letter-spacing:-.02em; }
.stats .v small { color:var(--accent); font-weight:700; }
.stats .k { font-family:var(--mono); color:var(--faint); text-transform:uppercase; letter-spacing:.15em; margin-top:.5em; }
.stats.grid { display:grid; grid-template-columns:1fr 1fr; }
.stats.grid .s { border-left:0; padding-left:0; }

.who { display:flex; align-items:center; gap:1em; }
.who .badge {
  font-family:var(--mono); color:var(--bg); background:var(--accent);
  font-weight:700; border-radius:10px; display:grid; place-items:center; flex:none;
}
.who .n { font-weight:650; letter-spacing:-.01em; }
.who .r { font-family:var(--mono); color:var(--mute); }
.who .cta { color:var(--accent); font-family:var(--mono); letter-spacing:.1em; }
.spacer { flex:1; }
""" % dict(theme, bloom=bloom, grid=grid)


# Runs after load, once images have their real boxes. Both axes are checked so
# a nowrap headline shrinks the card instead of running off the edge.
FIT = """<script>
function fit() {
  var w = document.querySelector('.wrap');
  var W = document.documentElement.clientWidth;
  var H = document.documentElement.clientHeight;
  var s = 1, guard = 0;
  var over = function () {
    return w.scrollHeight > w.clientHeight + 1 || w.scrollWidth > w.clientWidth + 1;
  };
  while (over() && guard++ < 90) {
    s *= 0.985;
    w.style.width = (W / s) + 'px';
    w.style.height = (H / s) + 'px';
    w.style.transform = 'scale(' + s + ')';
  }
  document.title = 'fit s=' + s.toFixed(3) + (over() ? ' OVERFLOW' : ' ok');
}
if (document.readyState === 'complete') fit();
else window.addEventListener('load', fit);
</script>"""


class Card(object):
    def __init__(self, cfg, base):
        self.c = cfg
        self.base = base
        self.theme = dict(DEFAULT_THEME, **cfg.get("theme", {}))
        self.proof_uri = None
        self.proof_dim = None
        proof = cfg.get("proof") or {}
        if proof.get("image"):
            self.proof_uri, path = data_uri(proof["image"], base)
            self.proof_dim = image_size(path)

    # -- pieces -----------------------------------------------------------
    def eyebrow(self, fs):
        e = self.c.get("eyebrow") or {}
        brand = esc(e.get("brand", ""))
        ctx = esc(e.get("context", ""))
        ctx_html = '<span class="sep">/</span><span class="plain">%s</span>' % ctx if ctx else ""
        return ('<div class="eyebrow" style="font-size:%dpx"><span class="dot"></span>%s%s</div>'
                % (fs, brand, ctx_html))

    def hero(self, fs, tag_fs, tag=True):
        """tag=False for the banner, where the eyebrow already carries the context."""
        h = self.c.get("hero") or {}
        pre = esc(h.get("prefix", ""))
        val = esc(h.get("value", ""))
        pre_html = '<span class="pre" style="font-size:.44em">%s</span>' % pre if pre else ""
        tag_top, tag_bot = h.get("tag_top", ""), h.get("tag_bottom", "")
        tag_html = ""
        if tag and (tag_top or tag_bot):
            tag_html = ('<span class="tag" style="font-size:%dpx">%s<b>%s</b></span>'
                        % (tag_fs, esc(tag_top), esc(tag_bot)))
        return ('<div class="hero" style="font-size:%dpx">%s<span class="val">%s</span>%s</div>'
                % (fs, pre_html, val, tag_html))

    def shot(self, bar_fs):
        if not self.proof_uri:
            return ""
        cap = esc((self.c.get("proof") or {}).get("caption", ""))
        dim = ""
        if self.proof_dim:
            dim = ' width="%d" height="%d"' % self.proof_dim
        alt = esc((self.c.get("proof") or {}).get("alt", cap or "proof screenshot"))
        return ('<div class="shot"><div class="bar" style="font-size:%dpx">'
                '<i></i><i></i><i></i><span>%s</span></div>'
                '<img%s src="%s" alt="%s"></div>' % (bar_fs, cap, dim, self.proof_uri, alt))

    def stats(self, v_fs, k_fs, pad, grid=False):
        items = self.c.get("stats") or []
        if not items:
            return ""
        cells = []
        for it in items:
            mark = it.get("mark")
            mark_html = '<small> %s</small>' % esc(mark) if mark else ""
            cells.append('<div class="s"><div class="v" style="font-size:%dpx">%s%s</div>'
                         '<div class="k" style="font-size:%dpx">%s</div></div>'
                         % (v_fs, esc(it.get("value", "")), mark_html, k_fs, esc(it.get("label", ""))))
        cls = "stats grid" if grid else "stats"
        style = "font-size:%dpx" % pad
        if grid:
            style += ";column-gap:%dpx" % int(v_fs * 0.9)
        return '<div class="%s" style="%s">%s</div>' % (cls, style, "".join(cells))

    def who(self, size, cta, stacked=False):
        p = self.c.get("person") or {}
        if not p:
            return ""
        links = [esc(x) for x in (p.get("links") or [])]
        cta_html = ('<div class="cta" style="font-size:%dpx">%s</div>' % (int(size * 0.60), esc(cta))) if cta else ""
        badge = ('<div class="badge" style="width:%dpx;height:%dpx;font-size:%dpx">%s</div>'
                 % (int(size * 2.05), int(size * 2.05), int(size * 0.95), esc(p.get("initials", ""))))
        if stacked:
            link_html = "".join('<div class="r" style="font-size:%dpx">%s</div>' % (int(size * 0.58), l)
                                for l in links)
            return ('<div class="who">%s<div style="min-width:0">'
                    '<div class="n" style="font-size:%dpx;white-space:nowrap">%s</div>'
                    '<div class="r" style="font-size:%dpx;margin-top:.25em">%s</div>%s%s</div></div>'
                    % (badge, int(size * 0.92), esc(p.get("name", "")), int(size * 0.58),
                       esc(p.get("role", "")), link_html, cta_html))
        right = "".join('<div class="r" style="font-size:%dpx">%s</div>' % (int(size * 0.62), l)
                        for l in links) + cta_html
        return ('<div class="who">%s<div><div class="n" style="font-size:%dpx">%s</div>'
                '<div class="r" style="font-size:%dpx">%s</div></div>'
                '<div class="spacer"></div><div style="text-align:right">%s</div></div>'
                % (badge, int(size * 0.95), esc(p.get("name", "")), int(size * 0.62),
                   esc(p.get("role", "")), right))

    def title(self, fs):
        return '<h1 style="font-size:%dpx">%s</h1>' % (fs, self.c.get("headline_html") or esc(self.c.get("headline", "")))

    def subtitle(self, fs):
        s = self.c.get("subtitle")
        return '<div class="sub" style="font-size:%dpx">%s</div>' % (fs, esc(s)) if s else ""

    # -- layouts ----------------------------------------------------------
    def page(self, w, h, body):
        return ("<!doctype html><html><meta charset=\"utf-8\"><title>card</title>"
                "<style>%s\nhtml,body{width:%dpx;height:%dpx;}</style>"
                "<body>%s%s</body></html>" % (css(self.theme), w, h, body, FIT))

    def wide(self, w, h, cta):
        pad = int(h * 0.072)
        body = ('<div class="wrap" style="padding:%dpx;gap:%dpx">%s'
                '<div class="row" style="gap:%dpx;flex:1">'
                '<div style="width:%s;display:flex;flex-direction:column;gap:%dpx;min-height:0">%s%s%s</div>'
                '<div style="flex:1;min-width:0">%s</div></div>%s%s</div>'
                % (pad, int(h * 0.032), self.eyebrow(int(h * 0.024)), int(w * 0.045),
                   "37%" if self.proof_uri else "100%", int(h * 0.028),
                   self.hero(int(h * 0.235), int(h * 0.021)),
                   self.title(int(h * 0.062)), self.subtitle(int(h * 0.028)),
                   self.shot(int(h * 0.021)),
                   self.stats(int(h * 0.048), int(h * 0.019), int(h * 0.018)),
                   self.who(int(h * 0.042), cta)))
        return self.page(w, h, body)

    def square(self, w, h, cta):
        pad = int(h * 0.068)
        body = ('<div class="wrap" style="padding:%dpx;gap:%dpx">%s%s'
                '<div>%s%s</div>%s<div class="spacer"></div>%s<div style="height:%dpx"></div>%s</div>'
                % (pad, int(h * 0.030), self.eyebrow(int(h * 0.021)),
                   self.hero(int(h * 0.195), int(h * 0.019)),
                   self.title(int(h * 0.056)), self.subtitle(int(h * 0.026)),
                   self.shot(int(h * 0.018)),
                   self.stats(int(h * 0.044), int(h * 0.017), int(h * 0.016), grid=True),
                   int(h * 0.010), self.who(int(h * 0.038), cta, stacked=True)))
        return self.page(w, h, body)

    def story(self, w, h, cta):
        body = ('<div class="wrap" style="padding:%dpx %dpx;gap:%dpx">%s<div class="spacer"></div>'
                '%s%s%s%s<div class="spacer"></div>%s<div style="height:%dpx"></div>%s</div>'
                % (int(h * 0.062), int(w * 0.072), int(h * 0.020), self.eyebrow(int(w * 0.025)),
                   self.hero(int(w * 0.30), int(w * 0.028)),
                   self.title(int(w * 0.078)), self.subtitle(int(w * 0.034)),
                   self.shot(int(w * 0.020)),
                   self.stats(int(w * 0.052), int(w * 0.020), int(w * 0.020), grid=True),
                   int(h * 0.010), self.who(int(w * 0.044), cta, stacked=True)))
        return self.page(w, h, body)

    def banner(self, w, h, cta):
        """One dense line. No proof shot: there is no room for a legible one."""
        p = self.c.get("person") or {}
        bits = [s.get("value", "") + " " + s.get("label", "").lower() for s in (self.c.get("stats") or [])]
        if p.get("name"):
            bits.append(p["name"])
        line = " &middot; ".join(esc(b) for b in bits)
        head = self.c.get("banner_headline_html") or (
            esc(self.c.get("headline", "")) + ' <em>&middot; ' + esc(self.c.get("banner_suffix", "")) + '</em>'
            if self.c.get("banner_suffix") else esc(self.c.get("headline", "")))
        body = ('<div class="wrap" style="padding:%dpx %dpx;justify-content:center;gap:%dpx">'
                '<div class="row" style="gap:%dpx">%s'
                '<div style="border-left:1px solid var(--line);padding-left:%dpx">%s'
                '<h1 style="font-size:%dpx;margin-top:.34em;white-space:nowrap">%s</h1>'
                '<div class="sub" style="font-size:%dpx;margin-top:.42em;white-space:nowrap">%s</div>'
                '%s</div></div></div>'
                % (int(h * 0.20), int(w * 0.05), int(h * 0.05), int(w * 0.03),
                   self.hero(int(h * 0.62), int(h * 0.062), tag=False),
                   int(w * 0.028), self.eyebrow(int(h * 0.062)),
                   int(h * 0.150), head, int(h * 0.068), line,
                   ('<div class="cta" style="font-size:%dpx;margin-top:.4em;white-space:nowrap">%s</div>'
                    % (int(h * 0.060), esc(cta))) if cta else ""))
        return self.page(w, h, body)

    def render_html(self, layout, w, h, cta):
        return getattr(self, layout)(w, h, cta)


def main():
    ap = argparse.ArgumentParser(description="Render celebration cards.")
    ap.add_argument("--config", required=True, help="path to the celebration JSON")
    ap.add_argument("--out", default=None, help="output directory (default: <config dir>/social)")
    ap.add_argument("--only", default=None, help="comma-separated format keys to render")
    ap.add_argument("--chrome", default=None, help="path to Chrome/Chromium/Edge")
    ap.add_argument("--scale", type=int, default=2, help="device scale factor (default 2)")
    ap.add_argument("--keep-html", action="store_true", help="keep the intermediate HTML")
    args = ap.parse_args()

    cfg_path = os.path.abspath(args.config)
    if not os.path.exists(cfg_path):
        die("config not found: " + cfg_path)
    with open(cfg_path, encoding="utf-8") as fh:
        cfg = json.load(fh)
    base = os.path.dirname(cfg_path)

    for required in ("headline",):
        if not cfg.get(required):
            die('config is missing "%s"' % required)

    out = os.path.abspath(args.out) if args.out else os.path.join(base, "social")
    os.makedirs(out, exist_ok=True)
    tmp = os.path.join(out, ".html")
    os.makedirs(tmp, exist_ok=True)

    chrome = find_chrome(args.chrome)
    card = Card(cfg, base)
    slug = cfg.get("slug") or os.path.splitext(os.path.basename(cfg_path))[0]

    wanted = cfg.get("formats") or list(FORMATS)
    if args.only:
        wanted = [k.strip() for k in args.only.split(",") if k.strip()]
    unknown = [k for k in wanted if k not in FORMATS]
    if unknown:
        die("unknown format(s): %s. Known: %s" % (", ".join(unknown), ", ".join(sorted(FORMATS))))

    cta = cfg.get("cta")
    variants = [("", None)]
    if cta:
        # The plain set states the achievement. The -cta set adds the ask, so the
        # author can decide per channel whether to broadcast availability.
        variants.append(("-cta", cta))

    failures = []
    for key in wanted:
        f = FORMATS[key]
        for suffix, cta_text in variants:
            name = "%s-%s%s" % (slug, key, suffix)
            html_path = os.path.join(tmp, name + ".html")
            png_path = os.path.join(out, name + ".png")
            with open(html_path, "w", encoding="utf-8") as fh:
                fh.write(card.render_html(f["layout"], f["w"], f["h"], cta_text))
            cmd = [
                chrome, "--headless", "--disable-gpu", "--hide-scrollbars",
                "--force-device-scale-factor=%d" % args.scale,
                "--virtual-time-budget=3000",  # let the load handler finish its fit pass
                "--window-size=%d,%d" % (f["w"], f["h"]),
                "--screenshot=" + png_path,
                "file:///" + html_path.replace("\\", "/"),
            ]
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            except subprocess.TimeoutExpired:
                failures.append(name + " (browser timed out)")
                print("FAIL  " + name)
                continue
            if os.path.exists(png_path):
                dim = image_size(png_path)
                print("OK    %-42s %s  %s" % (name, "%dx%d" % dim if dim else "", f["label"]))
            else:
                failures.append(name)
                print("FAIL  " + name)
                tail = (proc.stderr or "").strip().splitlines()[-1:] or [""]
                print("      " + tail[0][:200])

    if not args.keep_html:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n%d file(s) in %s" % (len(os.listdir(out)), out))
    if failures:
        die("%d render(s) failed: %s" % (len(failures), ", ".join(failures)))


if __name__ == "__main__":
    main()
