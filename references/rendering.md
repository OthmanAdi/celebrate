# Rendering

How the PNGs are produced, and every failure this design has actually hit.

## The capture

```bash
chrome --headless --disable-gpu --hide-scrollbars \
       --force-device-scale-factor=2 \
       --virtual-time-budget=3000 \
       --window-size=1600,900 \
       --screenshot=out.png \
       "file:///abs/path/card.html"
```

Each flag earns its place:

| Flag | Why |
|---|---|
| `--force-device-scale-factor=2` | The card is authored at post size and captured at twice the pixels. Feeds re-encode aggressively; a 1x capture of small mono type comes back mushy. |
| `--virtual-time-budget=3000` | The fit pass runs on `load`. Without a budget the capture can happen before it settles. |
| `--hide-scrollbars` | A 15px scrollbar otherwise eats the right edge of the design. |
| `--window-size=W,H` | Exact post dimensions. Never crop to size afterwards; type hinting is chosen at layout time. |

Embed images as `data:` URIs. A `file://` page loading sibling files is subject to
local-file rules that differ across Chrome versions, and a card that silently
renders without its proof is worse than one that fails.

## The fit pass

Hand-budgeting pixel heights per format works exactly until the copy changes. The
fit pass removes that whole class of bug:

```js
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
    w.style.width  = (W / s) + 'px';
    w.style.height = (H / s) + 'px';
    w.style.transform = 'scale(' + s + ')';
  }
}
```

It lays the card out in a **larger logical box** and scales that box back into the
frame. Because type sizes are fixed pixels, a bigger logical box means the text
occupies a smaller share of the card, so the loop converges instead of oscillating.

Four things it depends on:

1. **Run it on `load`, not during parsing.** Before images decode, a panel with an
   undecoded image measures as near zero, the pass concludes everything fits, and
   the card ships clipped.
2. **Check both axes.** A `white-space:nowrap` headline overflows horizontally
   without adding a single pixel of height. Height-only checks let it run off the edge.
3. **Nothing may shrink.** `.wrap > * { flex:none }`. A flex child that shrinks
   absorbs the overflow silently and the pass sees a card that fits.
4. **No `overflow:hidden` on inner rows.** Hidden overflow does not propagate to
   the ancestor's `scrollHeight`. The pass cannot react to what it cannot measure.

## Failures seen in practice

Each of these shipped a broken-looking card that the renderer reported as OK.

**A giant numeral bleeding into the line above it.**
`line-height` below 1 makes the line box shorter than the glyph, so the glyph
overflows its own box in both directions. Set `line-height:1` on the container and
on the numeral, and use `align-items:center`, not `baseline`, when mixing a 240px
digit with 20px labels.

**The proof screenshot stretched vertically.**
`width`/`height` attributes on the `<img>` reserve the box before decode, which the
fit pass needs. But CSS `width:100%` alone overrides only the width, so the
attribute height stays and the image distorts. Always pair it:

```css
.shot img { display:block; width:100%; height:auto; }
```

**A panel collapsed to two thin lines.**
The container was a flex child, the column overflowed, and flex shrank the panel to
nothing. `flex:none` on card children.

**A screenshot clipped top and bottom inside a centred row.**
The row had `overflow:hidden` and `align-items:center`, so an over-tall child was
trimmed at both ends and the fit pass never saw it. Remove the inner
`overflow:hidden`.

**Four stat columns wrapping into confetti on a vertical card.**
Below roughly 1200px of card width, four columns of monospace numbers cannot hold a
line. Use the two-by-two grid for `square` and `story`.

**Nothing rendered at all, browser already running.**
Chrome refuses a second launch against a profile that is in use
(`The browser is already running for ...`). Point at a different profile, or stop
the running one first.

## Regenerating

Rendering is pure: same config plus same proof gives the same PNGs. Keep the config
and the proof crop in the folder and the assets can be rebuilt at any time, in a
new size, with a corrected number, or in a different theme.
