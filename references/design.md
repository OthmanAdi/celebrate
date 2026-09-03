# Design

## What the card is

One claim, one proof, one set of numbers, one name. In that order of size. A viewer
scrolling past at speed should get the claim from the numeral alone; a viewer who
stops should find the evidence without clicking.

Anatomy, top to bottom:

1. **Eyebrow** — where this happened. Monospace, wide letter-spacing, accent
   coloured, with a small glowing dot. It reads as a source line, not a logo.
2. **Hero** — the number, as large as the format allows, with an optional prefix
   and a two-line label to its right behind a hairline rule.
3. **Headline** — what the thing is called. Not a sentence.
4. **Subtitle** — one sentence on what it does for the people using it.
5. **Proof panel** — the screenshot in a browser-ish frame with a caption bar.
6. **Stats** — three or four verified figures with monospace values and small caps
   labels, separated by hairlines.
7. **Author** — initials badge, name, role, links, and optionally the ask.

## Tokens

| Token | Default | Role |
|---|---|---|
| `bg` | `#0a0708` | Card ground. Near-black, warm rather than blue. |
| `panel` | `#140d0e` | Inside of the proof frame. |
| `line` | `#2a1c1d` | Every hairline and border. |
| `accent` | `#ff5a45` | The one colour. Numeral gradient, dot, rule, CTA. |
| `accent_dim` | `#b8392a` | The prefix glyph, and the frame's first dot. |
| `ink` | `#f6efec` | Headline and stat values. Off-white, never pure. |
| `mute` | `#9a8a86` | Subtitle, role, secondary values. |
| `faint` | `#6b5c59` | Stat labels, frame caption. |

Two type families: a tight sans for headline and subtitle, a monospace for every
label, number and URL. The split does real work. Monospace reads as "measured
value" and sans reads as "statement", so a viewer knows which parts are claims and
which are data without being told.

## Theming to the platform

When the win happened somewhere with a strong identity, sample that place's
background and accent into the theme. The card then reads as an extension of the
site the achievement is on. A generic quote-card palette makes the proof look
staged even when it is genuine.

Keep the accent to one hue. Two accents on a card this dense turns into decoration.

## The giant numeral

The single most fragile element, and the source of the ugliest bugs.

```css
.hero { display:flex; align-items:center; gap:.10em; line-height:1; }
.hero .val {
  font-weight:800; letter-spacing:-.04em; line-height:1; display:block;
  background:linear-gradient(180deg,#fff 8%,var(--accent) 96%);
  -webkit-background-clip:text; background-clip:text; color:transparent;
  filter:drop-shadow(0 6px 34px <accent>73);
}
```

- `line-height:1` on the container **and** the glyph. Anything tighter makes the
  line box shorter than the glyph and it overflows into whatever is above.
- `align-items:center`, not `baseline`. Baseline alignment between a 240px digit
  and a 20px label puts the label somewhere unhelpful and stretches the box.
- The gradient runs white to accent, top to bottom, so the numeral stays legible
  against a dark ground while still carrying the accent.
- The drop shadow is a glow, not a shadow: same hue as the accent, wide blur, low
  alpha. It separates the numeral from the ground without an outline.

## Background

A wide radial bloom of the accent at very low alpha behind the top of the card, a
second smaller one bottom right, and a 44px grid at about 3% white, masked to fade
out toward the edges. All three are near-invisible individually. Together they stop
the card from looking like a flat black rectangle, which is what a feed's own dark
mode already looks like.

## Restraint

- No emoji in the image. The caption is where those belong.
- No rounded-rectangle badge stack. One accent badge, the author's initials.
- No fake browser URL bar with a typed-out address. The caption bar in the frame
  names the source; a fabricated address bar is a small lie in an image whose whole
  job is to be true.
- No drop shadows on text apart from the numeral's glow.
- No more than four stats. Five is a table, and nobody reads a table in a feed.
