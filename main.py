#!/usr/bin/env python3
"""news-image-20261121 -- The Daily World front page for Saturday 21 November 2026.

Stdlib-only (zlib/struct/os). Draws a 1024x1024 newspaper front page with a
built-in 5x7 bitmap font and a hand-rolled PNG encoder. Deterministic: no
randomness, no time, no network, no external assets.
"""
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 232)
INK = (18, 18, 18)
RED = (178, 34, 34)
DARKRED = (130, 20, 20)
BLUE = (28, 68, 140)
LIGHTBLUE = (176, 205, 228)
GREY = (110, 108, 100)
LIGHTGREY = (225, 220, 205)
GOLD = (176, 132, 30)
GREEN = (34, 110, 60)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 chars, '#' = pixel on.
_G = {
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
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ':': ("00000", "01100", "00000", "00000", "00000", "01100", "00000"),
    ';': ("00000", "01100", "00000", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
}


def glyph(ch):
    return _G.get(ch.upper(), _G['?'])


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x, y, w, c, t=1):
        for k in range(t):
            for xx in range(x, x + w):
                self.set(xx, y + k, c)

    def vline(self, x, y, h, c, t=1):
        for k in range(t):
            for yy in range(y, y + h):
                self.set(x + k, yy, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill and d <= r * r:
                    self.set(xx, yy, c)
                elif not fill and abs(d - r * r) <= r * 2:
                    self.set(xx, yy, c)

    def poly(self, pts, c, fill=True):
        if not pts:
            return
        if fill:
            ys = [p[1] for p in pts]
            for y in range(min(ys), max(ys) + 1):
                xs = []
                n = len(pts)
                for i in range(n):
                    x0, y0 = pts[i]
                    x1, y1 = pts[(i + 1) % n]
                    if (y0 <= y < y1) or (y1 <= y < y0):
                        xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
                xs.sort()
                for i in range(0, len(xs) - 1, 2):
                    for x in range(int(xs[i]), int(xs[i + 1]) + 1):
                        self.set(x, y, c)
        else:
            n = len(pts)
            for i in range(n):
                self.line(pts[i][0], pts[i][1], pts[(i + 1) % n][0],
                          pts[(i + 1) % n][1], c)

    # ---- text ----
    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            g = glyph(ch)
            for r in range(7):
                for col in range(5):
                    if g[r][col] == '1':
                        for a in range(scale):
                            for b in range(scale):
                                self.set(cx + col * scale + a,
                                         y + r * scale + b, c)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def text_center(self, cx, y, s, scale, c):
        self.text(cx - self.text_w(s, scale) // 2, y, s, scale, c)

    def wrap(self, s, max_chars):
        words, lines, cur = s.split(), [], ""
        for wd in words:
            if cur and len(cur) + 1 + len(wd) > max_chars:
                lines.append(cur)
                cur = wd
            else:
                cur = (cur + " " + wd).strip()
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, scale, c, max_chars, max_lines=None, lh=None):
        lines = self.wrap(s, max_chars)
        if max_lines:
            lines = lines[:max_lines]
        lh = lh or (7 * scale + 3)
        for i, ln in enumerate(lines):
            self.text(x, y + i * lh, ln, scale, c)
        return y + len(lines) * lh


# ---------------------------------------------------------------- PNG
def png_bytes(cv):
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
            + chunk(b"IEND", b""))


# ---------------------------------------------------------------- content
TOP = [
    ("1", "TRUMP PRESSES ZELENSKY TO ACCEPT 28-POINT PEACE PLAN",
     "In the Oval Office, Trump told Zelensky he has \"no choice\" but to "
     "accept the US plan: Ukraine gives up Donbas, limits its army and drops "
     "NATO hopes, for Western security guarantees. The US aims for a deal "
     "by early January.",
     "doc"),
    ("2", "WALL STREET TUMBLES AS NASDAQ ERASES ALL OF 2026'S GAINS",
     "Friday's AI-led sell-off: S and P 500 down 3.7% to 6,910.39, Nasdaq down "
     "5.3% to 22,617.73 and in correction, Dow down 949.73. Worst S and P week "
     "in 18 months; worst Nasdaq week since March 2020.",
     "chart"),
    ("3", "COP31 IN ANTALYA OVERRUNS AS DRAFT DROPS FOSSIL FUELS",
     "Climate talks passed their deadline and ran on into Saturday with no "
     "deal. The draft deletes every mention of fossil fuels and cuts the "
     "US$120 billion-a-year adaptation finance target to 2035. Ethiopia to "
     "host COP32 in 2027.",
     "globe"),
]

SMALL = [
    ("4", "RUSSIAN MISSILES LAND IN POLAND", "Two Kh-101 missiles and a drone fell in south-east Poland; NATO chief Rutte visits Warsaw.", "missile"),
    ("5", "GTA 6: $3.79BN ON DAY ONE", "Take-Two: 32.5m units pre-ordered; the biggest entertainment launch ever.", "game"),
    ("6", "ANTHROPIC IPO SMASHES RECORDS", "US$81.3bn IPO, priced at US$83, valued near US$1.5tn; fell 9.1% on Friday.", "ipo"),
    ("7", "NVIDIA DOWN 14%, SEC PROBES BOOKS", "Longest losing run since 2008; US$1.4tn of value gone since the CEO quit.", "chip"),
    ("8", "ISRAELI STRIKE KILLS 3 IN GAZA AID VEHICLE", "Drone hit a food vehicle in Tel al-Hawa; 1,671 Palestinians killed since the October truce.", "aid"),
    ("9", "UFC QATAR: STIRLING KOs PROCHAZKA", "Navajo Stirling, 12-0, stopped the ex-champion with a right hook in round 2 in Doha.", "ufc"),
    ("10", "LEEDS STUN CHELSEA 4-1", "Noah Okafor scored twice at Stamford Bridge; first Leeds away win there since 1999.", "ball"),
    ("11", "OCTOBER 2026: HOTTEST EVER RECORDED", "Berkeley Earth: +1.80C above pre-industrial; 2026 almost certain to be the hottest year.", "heat"),
]

LISTED = [
    "12  Trump calls Putin a \"friend\"; Zelensky calls Putin a \"killer\"",
    "13  Trump demands a \"permanent\" deal with Iran: never a nuclear weapon",
    "14  Myanmar rejects ICJ genocide verdict over the Rohingya (9-6)",
    "15  UK and EU agree post-Brexit reset; youth mobility 100,000 a year",
    "16  Mexico arrests \"El Chapo Isidro\"; shootout kills 11 in Sinaloa",
    "17  Bolsonaro in intensive care with a bowel obstruction, aged 71",
    "18  Somalia expels the UAE ambassador; thousands march in Mogadishu",
    "19  Estonia to shut its land border with Russia from 1 December",
    "20  Turkey detains Sozcu TV executives; third opposition channel seized",
    "21  UN delays binding \"killer robot\" rules until 2028 after Geneva talks",
    "22  IAEA: North Korea expands uranium enrichment at Yongbyon",
    "23  Denmark approves US security deal for Greenland, 109-0",
    "24  Gold falls to a 14-month low, US$3,513.54 an ounce",
    "25  Trump threatens a \"big tax\" on US firms building AI centres abroad",
    "26  US chip export rules: TSMC and Samsung halt shipments to China",
    "27  Cursor, owned by SpaceX, may drop Chinese-made AI models",
    "28  Signal blocks screenshots to stop AI agents reading chats",
    "29  FBI national crime database NCIC reported hacked, says CNN",
    "30  CLAIM: Riemann Hypothesis proof with Claude's help - UNVERIFIED",
    "31  Biggest endometriosis gene study: 1m women, 58 genomic regions",
    "32  Mushroom protein from waste CO2: 48.5% protein, 22x soy yield",
    "33  Hunger Games: Sunrise on the Reaping takes $56m on day one",
    "34  Princess Catherine announces \"Heal\" film on her cancer journey",
    "35  Peter Fluck, Spitting Image co-creator, dies aged 85",
    "36  Strictly Blackpool: three couples tie at the top on 39 points",
    "37  Funeral boat capsizes in Nigeria; 24 dead, 24 survive",
    "38  Wolbachia mosquitoes cut dengue and chikungunya by 69%",
]

NUMBERS = [
    ("-3.7%", "S and P 500, Friday"),
    ("-5.3%", "Nasdaq, in correction"),
    ("$81.3BN", "Anthropic IPO, a record"),
    ("$3.79BN", "GTA 6 day-one sales"),
    ("+1.80C", "October 2026, hottest ever"),
    ("51 PTS", "James Harden, past Kobe"),
]


def draw_illustration(cv, kind, x, y, w, h):
    cv.rect(x, y, w, h, LIGHTBLUE)
    cv.rect(x, y, w, 2, BLUE)
    cv.rect(x, y + h - 2, w, 2, BLUE)
    if kind == "doc":
        cv.rect(x + 28, y + 12, w - 56, h - 24, WHITE)
        cv.rect(x + 28, y + 12, w - 56, 16, BLUE)
        cv.text(x + 40, y + 15, "28-POINT PLAN", 1, WHITE)
        for i in range(4):
            cv.hline(x + 40, y + 38 + i * 9, w - 80, GREY)
        cv.circle(x + w - 52, y + h - 30, 13, RED)
        cv.text(x + w - 60, y + h - 36, "US", 1, WHITE)
        cv.rect(x + 40, y + h - 26, 60, 3, INK)
    elif kind == "chart":
        base = y + h - 14
        cv.hline(x + 8, base, w - 16, INK, 2)
        pts = [(x + 14, y + 14), (x + 44, y + 20), (x + 74, y + 17),
               (x + 104, y + 30), (x + 134, y + 26), (x + 164, y + 44),
               (x + 194, y + 40), (x + 224, y + 56), (x + 254, y + 52),
               (x + 284, y + 68)]
        for i in range(len(pts) - 1):
            cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], RED, 3)
        for px, py in pts:
            cv.circle(px, py, 3, DARKRED)
        cv.text(x + w - 64, y + 6, "-5.3%", 2, RED)
    elif kind == "globe":
        cx, cy, r = x + w // 2, y + h // 2 + 4, 32
        cv.circle(cx, cy, r, (90, 160, 200))
        cv.poly([(cx - 30, cy - 18), (cx - 8, cy - 26), (cx + 6, cy - 12),
                 (cx - 6, cy + 2), (cx - 26, cy + 2)], GREEN)
        cv.poly([(cx + 12, cy + 10), (cx + 30, cy + 6), (cx + 26, cy + 26),
                 (cx + 8, cy + 30), (cx + 4, cy + 18)], GREEN)
        cv.circle(cx, cy, r, INK, fill=False)
        cv.text(x + 10, y + 6, "ANTALYA", 1, INK)
        cv.text(x + w - 62, y + h - 16, "NO DEAL", 1, RED)


def draw_icon(cv, kind, x, y, s=34):
    c = BLUE
    if kind == "missile":
        cv.poly([(x + 4, y + s - 4), (x + s - 4, y + 4), (x + s - 4, y + s - 4)], RED)
        cv.line(x + 6, y + s - 6, x + s - 6, y + 6, WHITE, 2)
    elif kind == "game":
        cv.rect(x + 2, y + 8, s - 4, s - 16, INK)
        cv.circle(x + 8, y + s - 6, 4, RED)
        cv.circle(x + s - 8, y + s - 6, 4, RED)
        cv.text(x + 10, y + 12, "GTA", 1, WHITE)
    elif kind == "ipo":
        cv.line(x + 6, y + s - 6, x + s // 2, y + 6, GREEN, 3)
        cv.line(x + s // 2, y + 6, x + s - 6, y + s - 14, GREEN, 3)
        cv.poly([(x + s - 14, y + s - 16), (x + s - 4, y + s - 16), (x + s - 9, y + s - 26)], GREEN)
    elif kind == "chip":
        cv.rect(x + 7, y + 7, s - 14, s - 14, INK)
        cv.rect(x + 12, y + 12, s - 24, s - 24, GREEN)
        for k in range(3):
            cv.hline(x + 4, y + 11 + k * 8, s - 8, INK, 2)
    elif kind == "aid":
        cv.rect(x + 4, y + 10, s - 8, s - 18, WHITE)
        cv.hline(x + 4, y + 10, s - 8, INK)
        cv.hline(x + 4, y + s - 9, s - 8, INK)
        cv.vline(x + 4, y + 10, s - 18, INK)
        cv.vline(x + s - 5, y + 10, s - 18, INK)
        cv.text(x + s // 2 - 3, y + 14, "+", 1, RED)
        cv.circle(x + 10, y + s - 6, 3, INK)
        cv.circle(x + s - 10, y + s - 6, 3, INK)
    elif kind == "ufc":
        cv.circle(x + s // 2, y + s // 2, s // 2 - 4, RED)
        cv.text(x + s // 2 - 6, y + s // 2 - 4, "KO", 1, WHITE)
    elif kind == "ball":
        cv.circle(x + s // 2, y + s // 2, s // 2 - 4, WHITE)
        cv.circle(x + s // 2, y + s // 2, s // 2 - 4, INK, fill=False)
        cv.circle(x + s // 2, y + s // 2, 4, INK)
    elif kind == "heat":
        cv.circle(x + s // 2, y + s - 8, 7, RED)
        cv.rect(x + s // 2 - 3, y + 6, 6, s - 14, RED)
        cv.circle(x + s // 2, y + 8, 6, RED, fill=False)


def build():
    cv = Canvas(W, H, PAPER)
    # frame
    cv.rect(0, 0, W, 8, INK)
    cv.rect(0, H - 8, W, 8, INK)
    cv.rect(0, 0, 8, H, INK)
    cv.rect(W - 8, 0, 8, H, INK)

    # ---- masthead ----
    cv.text_center(W // 2, 20, "THE DAILY WORLD", 6, INK)
    cv.hline(24, 92, W - 48, INK, 3)
    cv.text_center(W // 2, 100, "SATURDAY 21 NOVEMBER 2026  -  THE WORLD IN ONE PAGE", 2, RED)
    cv.text_center(W // 2, 122, "PEACE PLAN  -  MARKET ROUT  -  CLIMATE TALKS STALL", 1, INK)
    cv.hline(24, 140, W - 48, INK, 2)

    # ---- top 3 stories ----
    col_w = 312
    x0s = [24, 356, 688]
    for (num, head, body, kind), x0 in zip(TOP, x0s):
        y = 150
        cv.rect(x0, y, col_w, 18, RED)
        cv.text(x0 + 6, y + 5, "TOP STORY " + num, 1, WHITE)
        y += 24
        draw_illustration(cv, kind, x0, y, col_w, 80)
        y += 88
        y = cv.para(x0, y, head, 2, INK, 26, max_lines=3, lh=17)
        y += 4
        cv.para(x0, y, body, 1, INK, 52, max_lines=5, lh=10)
    cv.hline(24, 376, W - 48, INK, 2)

    # ---- stories 4-11 ----
    cv.text(24, 384, "ALSO TODAY", 2, RED)
    cell_w, cell_h = 238, 78
    for i, (num, head, body, kind) in enumerate(SMALL):
        cx = 24 + (i % 4) * (cell_w + 8)
        cy = 404 + (i // 4) * (cell_h + 6)
        draw_icon(cv, kind, cx, cy + 4)
        tx = cx + 42
        lines = cv.wrap(num + ". " + head, 30)
        yy = cy + 2
        for ln in lines[:2]:
            cv.text(tx, yy, ln, 1, INK)
            yy += 10
        cv.para(tx, yy + 1, body, 1, GREY, 30, max_lines=4, lh=10)
    cv.hline(24, 572, W - 48, INK, 2)

    # ---- map strip ----
    cv.text(24, 580, "WHERE IT HAPPENED", 2, RED)
    my0, my1 = 600, 660
    cv.rect(24, my0, W - 48, my1 - my0, (232, 240, 244))
    cv.poly([(60, 640), (150, 612), (260, 616), (280, 640), (230, 652), (140, 654), (80, 648)], (150, 180, 150))
    cv.poly([(250, 644), (300, 642), (310, 656), (280, 658), (255, 652)], (150, 180, 150))
    cv.poly([(500, 612), (560, 608), (580, 624), (540, 634), (505, 624)], (150, 180, 150))
    cv.poly([(500, 636), (570, 634), (590, 650), (560, 658), (520, 652)], (150, 180, 150))
    cv.poly([(600, 612), (760, 608), (860, 618), (880, 644), (800, 652), (660, 650), (610, 634)], (150, 180, 150))
    cv.poly([(840, 648), (900, 646), (910, 656), (860, 658)], (150, 180, 150))
    dots = [("WASHINGTON", 150, 626, 156, 623), ("KYIV", 545, 616, 551, 613),
            ("ANTALYA", 585, 626, 591, 623), ("GAZA", 600, 638, 594, 646),
            ("DOHA", 640, 640, 646, 637), ("LONDON", 505, 614, 469, 602),
            ("BRASILIA", 275, 648, 281, 645), ("MOGADISHU", 585, 648, 575, 656),
            ("SEOUL", 830, 622, 836, 619), ("LAS VEGAS", 110, 632, 116, 629)]
    for name, dx, dy, lx, ly in dots:
        cv.circle(dx, dy, 4, RED)
        cv.circle(dx, dy, 4, WHITE, fill=False)
        cv.text(lx, ly, name, 1, INK)
    cv.hline(24, 668, W - 48, INK, 2)

    # ---- numbered list 12-38 (two columns) ----
    cv.text(24, 676, "MORE FROM 21 NOVEMBER", 2, RED)
    left = LISTED[:14]
    right = LISTED[14:]
    for i, s in enumerate(left):
        cv.text(24, 700 + i * 10, s, 1, INK)
    for i, s in enumerate(right):
        cv.text(516, 700 + i * 10, s, 1, INK)
    cv.hline(24, 846, W - 48, INK, 2)

    # ---- day in numbers ----
    cv.text(24, 854, "DAY IN NUMBERS", 2, RED)
    bw, bh = 312, 44
    for i, (num, lab) in enumerate(NUMBERS):
        bx = 24 + (i % 3) * (bw + 8)
        by = 876 + (i // 3) * (bh + 6)
        cv.rect(bx, by, bw, bh, WHITE)
        cv.rect(bx, by, bw, 2, RED)
        cv.text(bx + 8, by + 6, num, 2, RED)
        cv.text(bx + 8, by + 26, lab, 1, INK)
    cv.hline(24, 978, W - 48, INK, 2)

    # ---- footer ----
    cv.text_center(W // 2, 986, "DATE CHECK: ALL STORIES VERIFIED TO SATURDAY 21 NOVEMBER 2026", 1, INK)
    cv.text_center(W // 2, 1000, "SOURCES: AP, REUTERS, AFP, BBC, CNBC, NPR, FINANCIAL TIMES, NIH, BERKELEY EARTH, IAEA, CPJ, NCAA, NBA, F1", 1, GREY)
    return cv


def main():
    cv = build()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(png_bytes(cv))


if __name__ == "__main__":
    main()
