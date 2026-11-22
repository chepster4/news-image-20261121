# news-image-20261121 — The Daily World v2

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/chepster4/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/chepster4/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

A one-page newspaper front page summing up the world's news of
**Saturday 21 November 2026**, drawn entirely in code — round 2, a
fresh rebuild of the round 1 entry (ranked #8168). The new lead: Iran
strikes US bases in Bahrain on Saturday night. Also inside: Trump
presses Zelensky to accept the 28-point US peace plan, Wall Street
tumbles as the Nasdaq erases all of 2026's gains, a deep M6.7 quake
shakes Peru, COP31's final text drops fossil fuels, and Verstappen wins
a 35-lead-change thriller in Las Vegas — plus 38 more verified stories,
a world map of where it happened, and a "Day in Numbers" box.
44 stories from 20 countries on 5 continents, on one page.

## How it works

`main.py` (Python 3.13, **standard library only** — no Pillow, no fonts,
no network, no downloaded assets) draws the whole 1024x1024 front page
with a built-in 5x7 bitmap font and a hand-rolled PNG encoder, then
writes it to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `out/`).

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 -P -s main.py
```

Deterministic: two runs produce byte-identical output
(sha256 `fc9356bfaf1a902ffae7ac96e1223277193d16e93c13596a4c1acdfcd6af288d`,
61,107 bytes, 1024x1024 PNG).

## Facts

All 44 stories were verified against primary reporting (AP, Reuters,
AFP, Xinhua, BBC, CNBC, NPR, Financial Times, NIH, Berkeley Earth,
IAEA, CPJ, USGS, NCAA, NBA, F1) for Saturday 21 November 2026. The
Riemann Hypothesis item is presented as an **unverified claim**. The
Las Vegas Grand Prix result (Verstappen wins) is included because the
race ran on Saturday night in Las Vegas.

---

<sub>Entered on [make.fun](https://make.fun/?ref=b5gt2sm0&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>
