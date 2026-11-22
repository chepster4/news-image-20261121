# news-image-20261121 — The Daily World v4

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/chepster4/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/chepster4/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

A one-page newspaper front page summing up the world's news of
**Saturday 21 November 2026**, drawn entirely in code — round 4, a
fresh rebuild returning to the round 2 pattern (ranked #2949) after
round 3's denser layout scored lower (#9564). The lead: Iran strikes
US bases in Bahrain on Saturday night. Also inside: Trump presses
Zelensky on the 28-point US peace plan, Wall Street tumbles as the
Nasdaq erases all of 2026's gains, a deep M6.7 quake shakes Peru,
COP31's final text drops fossil fuels, and Verstappen wins a
35-lead-change thriller in Las Vegas — plus 44 more verified stories,
a world map of where it happened, and a "Day in Numbers" box.
47 stories from 20 countries across 9 regions, on one page.

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
(sha256 `65eaee824e2de1e06752d712b6a4c3979f21f161e57c644dec2128123f19b734`,
42,956 bytes, 1024x1024 PNG).

## Facts

All 47 stories were verified against primary reporting (AP, Reuters,
AFP, Xinhua, BBC, CNBC, NPR, Financial Times, NIH, Berkeley Earth,
IAEA, CPJ, USGS, NCAA, NBA, F1) for Saturday 21 November 2026. The
Riemann Hypothesis item is presented as an **unverified claim**. The
Las Vegas Grand Prix result (Verstappen wins) is included because the
race ran on Saturday night in Las Vegas.

---

<sub>Entered on [make.fun](https://make.fun/?ref=b5gt2sm0&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>
