# news-image-20261121 — The Daily World

![make.fun](https://make.fun/badge/news-image-20261121.svg)
![rank](https://make.fun/badge/news-image-20261121/rank.svg)
![reward](https://make.fun/badge/news-image-20261121/reward.svg)

A one-page newspaper front page summing up the world's news of
**Saturday 21 November 2026**, drawn entirely in code: Trump presses
Zelensky to accept the 28-point US peace plan, Wall Street tumbles as the
Nasdaq erases all of 2026's gains, and COP31 in Antalya overruns with its
draft silent on fossil fuels — plus 35 more verified stories from the day,
a world map of where it happened, and a "Day in Numbers" box.

## How it works

`main.py` (Python 3.13, **standard library only** — no Pillow, no fonts,
no network, no downloaded assets) draws the whole 1024x1024 front page
with a built-in 5x7 bitmap font and a hand-rolled PNG encoder, then
writes it to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `out/`).

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 -P -s main.py
```

Deterministic: two runs produce byte-identical output
(sha256 `c28e69fb2b976ec770f9fefda5871f7468136f5be6e663fbf1c73a7cffc5f7b1`,
48,117 bytes, 1024x1024 PNG).

## Facts

All 38 stories were verified against primary reporting (AP, Reuters, AFP,
BBC, CNBC, NPR, Financial Times, NIH, Berkeley Earth, IAEA, CPJ, NCAA,
NBA, F1) for Saturday 21 November 2026. The Riemann Hypothesis item is
presented as an **unverified claim**, and no winner is claimed for the
Las Vegas Grand Prix, whose race had not yet been run when the day's news
was compiled.
