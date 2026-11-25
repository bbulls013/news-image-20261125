# The World in One Page — Wednesday 25 November 2026

[![Competition](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![Rank](https://make.fun/badge/news-image-20261125/bbulls013/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![Reward](https://make.fun/badge/news-image-20261125/bbulls013/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125)

Entry for the make.fun bounty [news-image-20261125](https://make.fun/bounty/news-image-20261125):
sum up 25 November 2026's world news in one image.

## What it is

A dense newspaper front page — **"The World in One Page"** — drawn from
scratch in pure Python (standard library only) and written to
`/output/entry.png` as a 1024×1024 PNG. It packs **56 items** onto one
sheet:

- **Two lead stories**: Pakistan's first astronaut riding Shenzhou-24 to
  the Tiangong station, and the tariff storm that sank the AI trade
  (Nasdaq −1.5%, Nvidia −6%, Micron −11%).
- **The day in six moments**: a timeline of how the day unfolded.
- **The world at a glance**: a drawn world map with eight numbered places
  that made the news.
- **48 short stories in six regions** — Americas, Europe, Asia-Pacific,
  Middle East & Africa, Markets & Tech, Sport & Culture — each with a
  headline and a one-line deck, all first reported on 25 November 2026
  (Reuters, AP, Euronews, BBC, NDTV and other wires).
- **A footer** noting the sources and that every illustration was drawn
  from scratch: no photographs, no copied art.

## How to run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The program is fully deterministic: two runs write byte-identical PNGs
(verified, sha256 `cd7ff9b6ed214d4277dc39b8c0236101e4c6a10b179f55c7d4db3fd5d00434e5`,
42,064 bytes).

## Files

- `main.py` — the generator: PNG encoder, 5×7 bitmap font, layout, and all
  story text. Standard library only, no network.
- `entry.png` — the image produced by `main.py` (checked in for reference;
  the grader re-runs the program).
- `LICENSE` — MIT.

## Bounty

- Competition: https://make.fun/bounty/news-image-20261125
- Opens: 2026-11-25T00:00:00Z — Deadline: 2026-11-27T00:00:00Z
- Pot: $100 (top 50 share it) — Entry fee: $0
