#!/usr/bin/env python3
"""Turn a raw screenshot into an embeddable proof crop.

    python prepare_proof.py shot.png --out proof/ --crop 600,352,1640,658 --ref-width 1998

The raw file is copied through untouched as the evidence of record. The cropped
and brightened derivative is what a card embeds:

* Crop away browser chrome, bookmark bars and sidebars. They are noise, they date
  the image, and a bookmark bar leaks whatever the author had open.
* Brighten. Dark product UI is legible on a monitor and turns into a black smear
  once a social platform re-encodes it.

--crop takes left,top,right,bottom. Give --ref-width when those numbers were read
off a scaled preview rather than the file itself; coordinates are scaled by
(actual width / ref width), which is the usual case on a HiDPI screen.
"""

import argparse
import os
import shutil
import sys
from typing import NoReturn


def die(msg) -> NoReturn:
    sys.stderr.write("celebrate: " + msg + "\n")
    raise SystemExit(2)


def main():
    ap = argparse.ArgumentParser(description="Crop and brighten a proof screenshot.")
    ap.add_argument("source", help="the raw screenshot")
    ap.add_argument("--out", default="proof", help="output directory (default: proof)")
    ap.add_argument("--crop", default=None, help="left,top,right,bottom in reference coordinates")
    ap.add_argument("--ref-width", type=float, default=None,
                    help="width the crop coordinates were measured against")
    ap.add_argument("--brightness", type=float, default=1.42, help="default 1.42")
    ap.add_argument("--contrast", type=float, default=1.16, help="default 1.16")
    ap.add_argument("--name", default="proof", help="basename for the derivative")
    args = ap.parse_args()

    try:
        from PIL import Image, ImageEnhance
    except ImportError:
        return die("Pillow is required: pip install pillow")

    if not os.path.exists(args.source):
        die("source not found: " + args.source)
    os.makedirs(args.out, exist_ok=True)

    raw_dst = os.path.join(args.out, "00-original" + os.path.splitext(args.source)[1])
    if os.path.abspath(raw_dst) != os.path.abspath(args.source):
        shutil.copy2(args.source, raw_dst)

    im = Image.open(args.source).convert("RGB")
    print("source      %dx%d" % im.size)

    if args.crop:
        parts = args.crop.split(",")
        if len(parts) != 4:
            return die("--crop must be four numbers: left,top,right,bottom")
        try:
            left, top, right, bottom = (float(x) for x in parts)
        except ValueError:
            return die("--crop must be four numbers: left,top,right,bottom")
        scale = (im.size[0] / args.ref_width) if args.ref_width else 1.0
        box = (int(round(left * scale)), int(round(top * scale)),
               int(round(right * scale)), int(round(bottom * scale)))
        if box[0] >= box[2] or box[1] >= box[3]:
            return die("--crop is empty: left must be < right and top < bottom")
        im = im.crop(box)
        print("cropped     %dx%d  (scale %.3f)" % (im.size + (scale,)))

    cropped = os.path.join(args.out, args.name + "-raw.png")
    im.save(cropped)

    lit = ImageEnhance.Brightness(im).enhance(args.brightness)
    lit = ImageEnhance.Contrast(lit).enhance(args.contrast)
    bright = os.path.join(args.out, args.name + ".png")
    lit.save(bright)

    print("evidence    " + raw_dst)
    print("crop        " + cropped)
    print("embed this  " + bright)


if __name__ == "__main__":
    main()
