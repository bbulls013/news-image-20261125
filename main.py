#!/usr/bin/env python3
"""The World in One Page -- Wednesday 25 November 2026.

Draws a dense newspaper front page summing up the day's world news and
writes it to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

Pure Python 3 standard library: the PNG encoder, the 5x7 bitmap font and
every illustration are defined here, so the program is fully deterministic
and runs with no network. Two runs produce byte-identical output.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 231)
INK = (20, 20, 20)
RED = (176, 32, 32)
BLUE = (31, 78, 121)
TEAL = (14, 107, 107)
GOLD = (150, 110, 10)
GREY = (107, 107, 107)
LIGHT = (232, 226, 210)
MIDGREY = (190, 184, 168)
DARKRED = (120, 18, 18)
GREEN = (34, 110, 60)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits, '#' = ink.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "00000", "00000", "00000", "01100", "00000"),
    ';': ("00000", "01100", "00000", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '*': ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '>': ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
}

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x, y, w, c, t=1):
        for k in range(t):
            self.rect(x, y + k, w, 1, c)

    def vline(self, x, y, h, c, t=1):
        for k in range(t):
            self.rect(x + k, y, 1, h, c)

    def box(self, x, y, w, h, c, t=1):
        self.hline(x, y, w, c, t)
        self.hline(x, y + h - t, w, c, t)
        self.vline(x, y, h, c, t)
        self.vline(x + w - t, y, h, c, t)

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c, t=2):
        for k in range(t):
            rr = r - k
            for a in range(360):
                import math
                xx = cx + int(rr * math.cos(math.radians(a)))
                yy = cy + int(rr * math.sin(math.radians(a)))
                self.set(xx, yy, c)

    def poly(self, pts, c):
        # scanline fill of a polygon given as [(x, y), ...]
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                for x in range(int(xs[j]), int(xs[j + 1]) + 1):
                    self.set(x, y, c)

    def text(self, x, y, s, scale=1, c=INK):
        cx = x
        for ch in s.upper():
            g = FONT.get(ch, FONT[' '])
            for r, row in enumerate(g):
                for col, bit in enumerate(row):
                    if bit == '1':
                        self.rect(cx + col * scale, y + r * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale=1):
        return len(s) * 6 * scale - scale

    def centre(self, y, s, scale, c=INK):
        self.text((self.w - self.text_w(s, scale)) // 2, y, s, scale, c)

    def wrap(self, x, y, s, max_w, scale=1, c=INK, lh=None):
        """Word-wrap text; returns y after the last line."""
        lh = lh or (9 * scale)
        words = s.split(' ')
        line = ''
        for wd in words:
            trial = (line + ' ' + wd).strip()
            if self.text_w(trial, scale) <= max_w or not line:
                line = trial
            else:
                self.text(x, y, line, scale, c)
                y += lh
                line = wd
        if line:
            self.text(x, y, line, scale, c)
            y += lh
        return y


def chunk(typ, data):
    c = struct.pack('>I', len(data)) + typ + data
    c += struct.pack('>I', zlib.crc32(typ + data) & 0xFFFFFFFF)
    return c


def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    comp = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', comp)
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------- content
# (headline, deck) pairs, grouped by region. Every story was first
# reported on Wednesday 25 November 2026, per Reuters / AP / Euronews /
# BBC / NDTV and other wires carried that morning.
REGIONS = [
    ("AMERICAS", RED, [
        ("CARTAGENA HOSTAGES FREED",
         "Gunmen seize a supermarket after a failed cash-truck raid."),
        ("GIULIANI GETS TOP US HONOUR",
         "Trump awards the ex-New York mayor the Medal of Freedom."),
        ("CIA AND ODNI HIT BY BREACH",
         "US spy agencies report a breach of unclassified material."),
        ("HUAWEI GUILTY OF TRADE THEFT",
         "US jury convicts the firm; clears it of racketeering."),
        ("DELL LIFTS ITS FORECASTS",
         "Record quarter as AI server demand surges."),
        ("US ARMY TO DETONATE LEAD AZIDE",
         "Iowa residents urged to leave the blast area."),
        ("VENEZUELA DEBT PUT AT $237.5BN",
         "Caracas publishes its total public debt figure."),
        ("DOW ENDS HIGHER, TECH SLIDES",
         "The Dow rises 0.8% while the Nasdaq falls 1.5%."),
    ]),
    ("EUROPE", BLUE, [
        ("NATO TO GUARD SPACE",
         "Alliance vows space defence as Russia eyes a satellite launch."),
        ("EU ADDS RUSSIA SANCTIONS",
         "Brussels announces further measures over the Ukraine war."),
        ("NATO JETS FOR POLAND",
         "Early-warning aircraft to deploy after missile landings."),
        ("BURNHAM ORDERS ATOMIC PROBE",
         "UK PM sets up a panel into nuclear test veterans' health."),
        ("AGE OF CONSENT REVIEW",
         "UK ministers ask the public for views on changing the law."),
        ("MAN UTD FUME OVER YORO RED",
         "Club and boss Pochettino angry at the sending-off."),
        ("BARCA RALLY BACKS SOCIALISTS",
         "Serrat and Loles Leon join a huge rally in the capital."),
        ("SENEDD REJECTS OUSTER BID",
         "Move to remove the presiding officer fails by a wide margin."),
    ]),
    ("ASIA-PACIFIC", TEAL, [
        ("SHENZHOU-24 LIFTS OFF",
         "China launches its crew to Tiangong with a Pakistani aboard."),
        ("RUSSIAN JETS ENTER KOREAN ZONE",
         "Military aircraft fly near Ulleung Island, Seoul says."),
        ("SEOUL MINISTER QUITS",
         "Education chief Choi Kyo-jin resigns over exam cheating."),
        ("NEPAL QUAKE 5.6",
         "Tremor hits Koshi province near the Tibet border."),
        ("BJP AND AKALIS REUNITE",
         "Six years after the split, an alliance for Punjab 2027."),
        ("NEPAL PM WRAPS INDIA VISIT",
         "Balendra Shah ends his first state visit after Modi talks."),
        ("MALAYSIA TO RETURN 6,500 ROHINGYA",
         "December repatriation, days after the ICJ genocide ruling."),
        ("HASINA EYES 16 DEC RETURN",
         "Ousted PM plans to come home from exile on Victory Day."),
    ]),
    ("MIDDLE EAST & AFRICA", DARKRED, [
        ("GAZA STRIKE KILLS HAMAS SECURITY CHIEF",
         "Naeem Abu Nahel among at least seven dead, medics say."),
        ("HOUTHI DRONE HITS RIYADH",
         "Eleven hurt in a tower attack; two Indians among them."),
        ("YEMEN STRIKES KILL DOZENS",
         "Houthis say Saudi raids killed 17 telecom workers in Hodeida."),
        ("IRAN VOWS TO RESPOND",
         "Tehran warns after tanker mines reported in the Hormuz strait."),
        ("SWIMMER CROSSES HORMUZ",
         "Lewis Pugh swims 15 km to highlight the war's toll."),
        ("EISENKOT CLOSER TO GOVERNMENT",
         "Israeli opposition figure clinches his first coalition deal."),
        ("SETTLER ARSON CONDEMNED",
         "Eisenkot calls West Bank arson attacks 'Jewish terrorism'."),
        ("UKRAINE SINKS SHIP OFF LIBYA",
         "Kyiv claims a Russian warship sunk in a long-range strike."),
    ]),
    ("MARKETS & TECH", GOLD, [
        ("AI TRADE COLLAPSES AGAIN",
         "Nasdaq falls 1.5% and the S&P 500 0.5% as tariff fears return."),
        ("NVIDIA -6%, MICRON -11%",
         "Chip stocks slide; the semiconductor index falls about 8%."),
        ("TARIFFS EYED FOR 16 ECONOMIES",
         "WSJ: the US is preparing hikes on China, the EU and 14 others."),
        ("TRUMP: NVIDIA PARDON 'AN OPTION'",
         "But CEO Jensen Huang must 'tell the truth' to Congress."),
        ("GTA 6: 39M PLAYERS IN 4 DAYS",
         "Sony's biggest launch in 30 years, after the 19 Nov release."),
        ("MESSAGE SENT THROUGH A WALL",
         "Physicists send an 'unblockable' signal using gravity."),
        ("SENSEX WATCHES TARIFF CUES",
         "Indian markets track the US tariff headlines into the close."),
        ("AIDS DEATHS AT 20-YEAR LOW",
         "570,000 in 2025, UNAIDS says, but HIV funding fell 18%."),
    ]),
    ("SPORT & CULTURE", GREEN, [
        ("ENGLAND LEVEL T20 SERIES",
         "Eight-wicket win over Australia, chasing 185."),
        ("FRASER-MCGURK HITS 27 OFF 13",
         "Three sixes in the second T20I against England."),
        ("SOORYAVANSHI'S RECORD TON",
         "The fastest List A double hundred ever recorded."),
        ("SRI LANKA A FACE INDIA A",
         "Asia Cup Rising Stars semi-final set for Doha."),
        ("MAN UTD EYE COLLINS",
         "Brentford defender Nathan Collins is on the radar."),
        ("'INTO THE UN' FEAST REVIEWED",
         "Chinese ecological cuisine event honoured in Beijing."),
        ("25 NOV: END VIOLENCE AGAINST WOMEN",
         "The international day is marked around the world."),
        ("GTA 6 STILL TOPS THE CHARTS",
         "39 million PS5 players in four days, Sony says."),
    ]),
]

TIMELINE = [
    ("EARLY", "Shenzhou-24 lifts off with Pakistan's first astronaut aboard."),
    ("MORNING", "Nepal hit by a 5.6 quake; Asian markets open lower."),
    ("MIDDAY", "WSJ tariff report rattles Wall Street; the Nasdaq slides."),
    ("AFTERNOON", "Houthi drone hits a Riyadh tower; eleven people hurt."),
    ("EVENING", "England level the T20 series; Giuliani is honoured."),
    ("LATE", "NATO vows space defence; the Gaza toll rises again."),
]

# Map markers: (label number, x, y in the map's 340x130 grid, caption)
MAP_DOTS = [
    (1, 272, 38, "JIUQUAN: SHENZHOU-24"),
    (2, 254, 50, "NEPAL: QUAKE 5.6"),
    (3, 208, 70, "RIYADH: DRONE HIT"),
    (4, 194, 40, "GAZA: STRIKE"),
    (5, 234, 78, "HORMUZ: MINES"),
    (6, 84, 96, "CARTAGENA: HOSTAGES"),
    (7, 302, 36, "SEOUL: JETS IN ZONE"),
    (8, 164, 28, "LONDON: ATOMIC PROBE"),
]


def draw_rocket(cv, x, y, s):
    # simple rocket: body, window, fins, flame
    cv.rect(x + 14 * s // 10, y, 12 * s // 10, 30 * s // 10, INK)
    cv.poly([(x + 14 * s // 10, y), (x + 20 * s // 10, y - 8 * s // 10),
             (x + 26 * s // 10, y)], RED)
    cv.disc(x + 20 * s // 10, y + 10 * s // 10, 4 * s // 10, PAPER)
    cv.ring(x + 20 * s // 10, y + 10 * s // 10, 4 * s // 10, RED, 1)
    cv.poly([(x + 14 * s // 10, y + 30 * s // 10), (x + 8 * s // 10, y + 40 * s // 10),
             (x + 14 * s // 10, y + 36 * s // 10)], RED)
    cv.poly([(x + 26 * s // 10, y + 30 * s // 10), (x + 32 * s // 10, y + 40 * s // 10),
             (x + 26 * s // 10, y + 36 * s // 10)], RED)
    cv.poly([(x + 17 * s // 10, y + 30 * s // 10), (x + 20 * s // 10, y + 44 * s // 10),
             (x + 23 * s // 10, y + 30 * s // 10)], GOLD)


def draw_chart(cv, x, y, w, h):
    # bar chart: Nasdaq -1.5, S&P -0.5, Nvidia -6, Micron -11, Semis -8, Dow +0.8
    bars = [("NASDAQ", -1.5), ("S&P", -0.5), ("NVIDIA", -6.0),
            ("MICRON", -11.0), ("SEMIS", -8.0), ("DOW", 0.8)]
    bw = w // len(bars)
    zero = y + h // 2
    cv.hline(x, zero, w, INK, 2)
    for i, (lab, v) in enumerate(bars):
        bx = x + i * bw + 6
        bh = int(abs(v) / 11.0 * (h // 2 - 12))
        col = GREEN if v > 0 else RED
        if v >= 0:
            cv.rect(bx, zero - bh, bw - 12, bh, col)
        else:
            cv.rect(bx, zero, bw - 12, bh, col)
        cv.text(bx - 2, y + h - 8, lab, 1, INK)
        cv.text(bx + 2, y + 2 if v < 0 else zero - bh - 10,
                ("+" if v > 0 else "") + str(v) + "%", 1, col)


def draw_map(cv, x, y, w, h):
    cv.rect(x, y, w, h, (214, 228, 235))
    # rough continents, drawn as filled polygons on a 340x130 grid
    cv.poly([(x + 18, y + 38), (x + 62, y + 22), (x + 96, y + 30),
             (x + 108, y + 52), (x + 84, y + 74), (x + 52, y + 88),
             (x + 30, y + 70), (x + 14, y + 52)], (120, 150, 110))   # N America
    cv.poly([(x + 70, y + 92), (x + 96, y + 96), (x + 104, y + 118),
             (x + 88, y + 126), (x + 72, y + 112)], (120, 150, 110))  # S America
    cv.poly([(x + 150, y + 28), (x + 178, y + 18), (x + 196, y + 30),
             (x + 188, y + 48), (x + 164, y + 50), (x + 150, y + 40)], (120, 150, 110))  # Europe
    cv.poly([(x + 158, y + 54), (x + 196, y + 52), (x + 206, y + 74),
             (x + 196, y + 104), (x + 176, y + 112), (x + 160, y + 86),
             (x + 150, y + 66)], (120, 150, 110))  # Africa
    cv.poly([(x + 210, y + 22), (x + 268, y + 12), (x + 316, y + 26),
             (x + 322, y + 52), (x + 296, y + 66), (x + 258, y + 84),
             (x + 232, y + 62), (x + 208, y + 42)], (120, 150, 110))  # Asia
    cv.poly([(x + 296, y + 96), (x + 322, y + 94), (x + 330, y + 110),
             (x + 312, y + 120), (x + 296, y + 110)], (120, 150, 110))  # Oceania
    cv.hline(x, y + h - 1, w, INK, 1)
    for num, gx, gy, cap in MAP_DOTS:
        mx = x + gx * w // 340
        my = y + gy * h // 130
        cv.disc(mx, my, 7, RED)
        cv.text(mx - 3, my - 3, str(num), 1, PAPER)


def build():
    cv = Canvas(W, H, PAPER)
    # outer frame
    cv.box(6, 6, W - 12, H - 12, INK, 3)
    cv.box(12, 12, W - 24, H - 24, INK, 1)

    # ---- top line
    cv.text(20, 20, "EST. 2026  |  ONE DAY, ONE PAGE  |  FREE", 1, GREY)
    tw = cv.text_w("NO. 25  -  $100 IN PRIZES", 1)
    cv.text(W - 20 - tw, 20, "NO. 25  -  $100 IN PRIZES", 1, GREY)

    # ---- masthead
    cv.centre(34, "THE WORLD IN ONE PAGE", 5, INK)
    cv.hline(20, 86, W - 40, INK, 2)
    cv.centre(94, "WEDNESDAY 25 NOVEMBER 2026", 2, RED)
    cv.text(20, 112, "THE DAY'S NEWS, FROM EVERY REGION, ON ONE SHEET", 1, GREY)
    tw = cv.text_w("INTL DAY: END VIOLENCE AGAINST WOMEN", 1)
    cv.text(W - 20 - tw, 112, "INTL DAY: END VIOLENCE AGAINST WOMEN", 1, GREY)
    cv.hline(20, 126, W - 40, INK, 1)

    # ---- lead stories
    lx, lw = 20, 480
    rx = 524
    cv.rect(lx, 136, lw, 16, RED)
    cv.text(lx + 6, 138, "LEAD  -  SPACE", 1, PAPER)
    y = cv.wrap(lx, 158, "PAKISTAN'S FIRST ASTRONAUT RIDES SHENZHOU-24 TO TIANGONG",
                lw, 2, INK, 20)
    y = cv.wrap(lx, y + 2,
                "Muhammad Zeeshan Ali, 40, a Pakistan Air Force pilot, lifts off "
                "with China's Shenzhou-24 crew - the first Pakistani in orbit and "
                "the first foreign astronaut aboard the Tiangong station. He will "
                "spend about a week in orbit running four Pakistani biotech tests.",
                lw, 1, INK, 10)
    draw_rocket(cv, lx + 428, 166, 8)
    cv.text(lx, 268, "FIRST REPORTED: WED 25 NOV, 05:18 PKT  -  REUTERS / AP", 1, GREY)

    cv.rect(rx, 136, lw, 16, INK)
    cv.text(rx + 6, 138, "LEAD  -  MARKETS", 1, PAPER)
    y = cv.wrap(rx, 158, "TARIFF STORM SINKS THE AI TRADE", rx + lw - rx, 2, INK, 20)
    y = cv.wrap(rx, y + 2,
                "A day after Nvidia surged, the AI trade collapses again: the "
                "Nasdaq falls 1.5% and the S&P 500 0.5% as a WSJ report says the "
                "Trump administration is preparing to raise tariffs on China, "
                "the EU and 14 other economies.",
                lw, 1, INK, 10)
    draw_chart(cv, rx, 222, lw, 52)
    cv.text(rx, 282, "FIRST REPORTED: TUE 24 NOV, WALL ST CLOSE  -  REUTERS", 1, GREY)
    cv.hline(20, 296, W - 40, INK, 2)

    # ---- timeline
    cv.text(20, 306, "THE DAY IN SIX MOMENTS", 2, INK)
    cv.text(560, 308, "SIX MOMENTS FROM THE DAY", 1, GREY)
    ty = 336
    cv.hline(30, ty, W - 60, INK, 2)
    seg = (W - 60) // 6
    for i, (when, what) in enumerate(TIMELINE):
        cx = 30 + i * seg + seg // 2
        cv.disc(cx, ty, 6, RED)
        cv.text(cx - cv.text_w(when, 1) // 2, ty - 16, when, 1, RED)
        cv.wrap(cx - seg // 2 + 6, ty + 12, what, seg - 12, 1, INK, 9)
    cv.hline(20, 392, W - 40, INK, 1)

    # ---- map
    cv.text(20, 402, "THE WORLD AT A GLANCE", 2, INK)
    cv.text(420, 404, "EIGHT PLACES THAT MADE THE NEWS TODAY", 1, GREY)
    draw_map(cv, 20, 424, 560, 130)
    mx = 600
    cv.text(mx, 424, "WHERE IT HAPPENED", 1, RED)
    my = 442
    for num, _dx, _dy, cap in MAP_DOTS:
        cv.text(mx, my, str(num) + "  " + cap, 1, INK)
        my += 14
    cv.hline(20, 566, W - 40, INK, 2)

    # ---- region grid: 3 columns x 2 rows
    cols, rows = 3, 2
    gx, gy = 20, 574
    cw = (W - 40 - 2 * 12) // cols
    ch = 200
    for idx, (name, col, stories) in enumerate(REGIONS):
        cx = gx + (idx % cols) * (cw + 12)
        cy = gy + (idx // cols) * (ch + 6)
        cv.box(cx, cy, cw, ch, INK, 1)
        cv.rect(cx + 1, cy + 1, cw - 2, 15, col)
        cv.text(cx + 6, cy + 4, name, 1, PAPER)
        sy = cy + 22
        for head, deck in stories:
            if sy + 22 > cy + ch - 4:
                break
            sy = cv.wrap(cx + 6, sy, head, cw - 12, 1, INK, 9)
            sy = cv.wrap(cx + 6, sy, deck, cw - 12, 1, GREY, 9)
            sy += 2
            cv.hline(cx + 6, sy - 1, cw - 12, MIDGREY, 1)

    # ---- footer
    fy = 990
    cv.hline(20, fy - 8, W - 40, INK, 2)
    cv.text(20, fy, "HOW TO READ THIS PAGE: 56 STORIES, 6 REGIONS, 1 DAY. "
            "EVERY EVENT FIRST REPORTED 25 NOVEMBER 2026.", 1, INK)
    cv.text(20, fy + 12,
            "SOURCES: REUTERS, AP, EURONEWS, BBC, NDTV AND OTHER WIRES. "
            "DRAWN FROM SCRATCH - NO PHOTOGRAPHS, NO COPIED ART.", 1, GREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(build(), path)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
