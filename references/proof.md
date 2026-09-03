# Proof

The screenshot is the reason anyone believes the card. Treat it as evidence, and
handle it the way evidence is handled: keep the original, work on copies, and
change only what you can justify.

## Capture

Capture the moment as soon as it exists. Leaderboards, trending lists and live
counters move within hours.

- A screenshot the person already took beats one you go and re-take later. If the
  position has since changed, re-capturing destroys the only record of the claim.
- Full window, at native resolution. A phone photo of a monitor is not evidence.
- Include enough of the surrounding interface to identify the product. A single
  cropped row with a number could be anything.

If nothing was captured and the moment has passed, say so and build the assets from
the verified numbers alone, without a proof panel. Do not reconstruct a screenshot
of a state you did not observe. A rebuilt "screenshot" is a fabricated record, and
that is true no matter how accurate you believe it to be.

## What to crop to

Keep:

- The element that proves the claim: the ranked row, the counter, the chart point.
- Its column header, so the number has a name.
- Enough neighbouring rows to show what it beat. A first place with nothing under it
  is far less convincing than one with the next three entries visible.
- The product's own tab or section labels, which identify the source.

Remove:

- Browser tabs, address bar, bookmark bar, extension icons.
- Sidebars, reading lists, open-tab panels. These leak what the author was doing and
  are pure noise.
- Account menus, avatars, notification badges.
- Anything showing another person's private data.

## Coordinates

Read crop coordinates off whatever preview you have, note that preview's width, and
let the script rescale:

```bash
python scripts/prepare_proof.py shot.png --out proof/ \
    --crop 600,352,1640,658 --ref-width 1998
```

On a HiDPI screen the file is commonly 1.25x to 2x the size of the preview you
measured against, and cropping with unscaled numbers silently produces the wrong
region.

## Brightening

Dark product interfaces are legible on a monitor and turn into a black smear after a
feed's re-encoding. The script applies brightness 1.42 and contrast 1.16 by default.

This is the one alteration the skill makes to evidence, so keep it honest:

- Brightness and contrast only. No cropping out an inconvenient neighbour, no
  retouching a number, no cloning a row.
- The unmodified original stays in `proof/00-original.png` and ships with the folder.
- If a number is genuinely unreadable after brightening, the crop is too wide.
  Tighten it rather than pushing the adjustment further.

## Framing

The renderer puts the crop in a panel with a caption bar. Name the real source in
the caption, for example `clawhub.ai — Skills · Trending`. Do not draw a fake
address bar with a typed URL: the panel's job is to say where this came from, and an
invented address undermines the one thing the image is for.

## Never commit the raw capture

A full-window screenshot is a picture of somebody's actual screen. It carries
their open tabs, their bookmark bar, their account name, whatever notification
happened to be up. Keep the original in the working folder as the record, and keep
that folder out of any repository you publish.

Ship the cards. The crop inside them shows only the part that proves the claim,
which is the part that was public anyway.
