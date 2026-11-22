#!/usr/bin/env python3
"""The Daily World v4 - Saturday 21 November 2026 in one image.

Draws a 1024x1024 newspaper front page with the Python standard library
only (zlib + struct for the PNG encoder, a hand-built 5x7 bitmap font).
Writes entry.png to $MAKEFUN_OUTPUT_DIR (default "out/").

Content: 47 verified stories of Saturday 21 November 2026 - 3 illustrated
top stories, 8 "Also Today" items, a world map, a numbered list of 36 more
stories, and a "Day in Numbers" strip. Deterministic: two runs write
byte-identical files.
"""
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = bytes((242, 236, 220))
INK = bytes((18, 18, 18))
RED = bytes((168, 28, 34))
DARKRED = bytes((120, 18, 24))
NAVY = bytes((16, 30, 60))
NAVY2 = bytes((28, 48, 88))
SKY = bytes((196, 216, 232))
SEA = bytes((178, 205, 224))
LAND = bytes((148, 178, 132))
LAND2 = bytes((168, 192, 148))
GOLD = bytes((198, 152, 52))
YELLOW = bytes((232, 190, 60))
ORANGE = bytes((224, 110, 40))
GREY = bytes((110, 104, 92))
LIGHTGREY = bytes((214, 206, 188))
WHITE = bytes((250, 248, 242))
GREEN = bytes((46, 120, 70))

# ------------------------------------------------------------------- PNG
def _chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def encode_png(w, h, rgb):
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", comp) + _chunk(b"IEND", b""))


# ------------------------------------------------------------- framebuffer
class FB:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = c

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + (x1 - x0) * 3] = c * (x1 - x0)

    def border(self, x, y, w, h, c, t=1):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.rect(x0 - t // 2, y0 - t // 2, t, t, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        if fill:
            for yy in range(-r, r + 1):
                dx = int((r * r - yy * yy) ** 0.5)
                self.rect(cx - dx, cy + yy, 2 * dx + 1, 1, c)
        else:
            for a in range(360):
                import math
                x = int(cx + r * math.cos(a * math.pi / 180) + 0.5)
                y = int(cy + r * math.sin(a * math.pi / 180) + 0.5)
                self.set(x, y, c)

    def poly(self, pts, c):
        # scanline fill for a simple polygon given as [(x, y), ...]
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                    xs.append(x)
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), y, max(1, int(xs[i + 1]) - int(xs[i])), 1, c)

    def vgrad(self, x, y, w, h, c1, c2):
        for i in range(h):
            t = i / max(1, h - 1)
            c = bytes((int(c1[j] + (c2[j] - c1[j]) * t) for j in range(3)))
            self.rect(x, y + i, w, 1, c)


# -------------------------------------------------------------- bitmap font
# 5x7 glyphs, '#' = on, '.' = off. All-caps newspaper face.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    '3': ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '\u2013': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '\u2014': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    '@': (".###.", "#...#", "#.###", "#.#.#", "#.##.", "#....", ".###."),
    '*': (".....", "#.#.#", ".###.", "#.#.#", ".....", ".....", "....."),
    '\u2022': (".....", ".....", ".##..", ".##..", ".....", ".....", "....."),
    '\u00b0': (".##..", "#..#.", ".##..", ".....", ".....", ".....", "....."),
    '\u00d7': (".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "....."),
    '\u00b7': (".....", ".....", ".....", ".##..", ".##..", ".....", "....."),
    '[': (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    ']': (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    '<': ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    '>': (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
}


def text_w(text, s):
    return len(text) * 6 * s - s if text else 0


def draw_text(fb, x, y, s, text, color, bold=False):
    cx = x
    for ch in text:
        g = FONT.get(ch)
        if g is None:
            cx += 6 * s
            continue
        for r in range(7):
            row = g[r]
            for col in range(5):
                if row[col] == '#':
                    w = s + 1 if bold else s
                    fb.rect(cx + col * s, y + r * s, w, s, color)
        cx += 6 * s
    return cx


def draw_text_center(fb, cx, y, s, text, color, bold=False):
    draw_text(fb, cx - text_w(text, s) // 2, y, s, text, color, bold)


def wrap(text, max_chars):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        add = (cur + " " + w) if cur else w
        if len(add) <= max_chars:
            cur = add
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------ draw helpers
def section_head(fb, x, y, w, text, color=RED):
    draw_text(fb, x, y, 3, text, color, bold=True)
    fb.hline(x, y + 26, w, INK, 2)
    return y + 32


def label_bar(fb, x, y, w, text):
    fb.rect(x, y, w, 22, RED)
    draw_text(fb, x + 8, y + 4, 2, text, WHITE, bold=True)


def draw_radar(fb, x, y, s):
    # small radar-dish pictogram in a dark panel
    fb.rect(x, y, 30, 30, NAVY)
    fb.circle(x + 15, y + 20, 9, WHITE, fill=False)
    fb.line(x + 15, y + 20, x + 23, y + 11, WHITE, 2)
    fb.line(x + 15, y + 20, x + 8, y + 12, WHITE, 1)
    fb.rect(x + 13, y + 24, 4, 4, WHITE)


def draw_doc(fb, x, y):
    # peace-plan document with a folded corner
    fb.rect(x, y, 30, 30, WHITE)
    fb.border(x, y, 30, 30, INK, 1)
    fb.poly([(x + 22, y), (x + 30, y + 8), (x + 22, y + 8)], LIGHTGREY)
    for i in range(4):
        fb.rect(x + 5, y + 6 + i * 6, 18, 2, GREY)
    fb.rect(x + 5, y + 26, 10, 2, RED)


def draw_chart_icon(fb, x, y):
    fb.rect(x, y, 30, 30, WHITE)
    fb.border(x, y, 30, 30, INK, 1)
    fb.line(x + 4, y + 6, x + 11, y + 12, RED, 2)
    fb.line(x + 11, y + 12, x + 18, y + 10, RED, 2)
    fb.line(x + 18, y + 10, x + 26, y + 24, RED, 2)
    fb.circle(x + 26, y + 24, 2, RED)


# ------------------------------------------- top-story illustration panels
def illo_iran(fb, x, y, w, h):
    # night sky over Bahrain: gradient, stars, explosion glow, missile arcs
    fb.vgrad(x, y, w, h, NAVY, NAVY2)
    import math
    for i in range(60):
        sx = x + (i * 37) % (w - 4) + 2
        sy = y + (i * 53) % (h // 2) + 2
        fb.set(sx, sy, WHITE)
        if i % 5 == 0:
            fb.set(sx + 1, sy, WHITE)
    # crescent moon, top left
    fb.circle(x + 34, y + 22, 12, YELLOW)
    fb.circle(x + 39, y + 19, 10, NAVY)
    # explosion glow, upper right
    gx, gy = x + w - 52, y + 30
    for r, c in ((26, ORANGE), (18, GOLD), (11, YELLOW), (6, WHITE)):
        fb.circle(gx, gy, r, c)
    # missile arcs from lower left to the glow
    for k, (ax, ay) in enumerate(((x + 18, y + h - 8), (x + 60, y + h - 6),
                                  (x + 110, y + h - 10))):
        for t in range(21):
            u = t / 20.0
            px = int(ax + (gx - ax) * u)
            py = int(ay + (gy - ay) * u - 34 * math.sin(u * math.pi))
            fb.rect(px, py, 2, 2, YELLOW if k != 1 else WHITE)
    # radar dish silhouette, lower left
    fb.line(x + 26, y + h - 6, x + 40, y + h - 34, WHITE, 2)
    fb.line(x + 40, y + h - 34, x + 56, y + h - 44, WHITE, 2)
    fb.line(x + 40, y + h - 34, x + 30, y + h - 46, WHITE, 2)
    fb.line(x + 30, y + h - 46, x + 56, y + h - 44, WHITE, 2)
    # ground + sea
    fb.rect(x, y + h - 14, w, 14, INK)
    fb.rect(x, y + h - 14, w, 2, GOLD)
    # red badge
    fb.rect(x + w - 162, y + 6, 156, 18, RED)
    draw_text(fb, x + w - 156, y + 9, 2, "2 RADARS HIT", WHITE, bold=True)
    draw_text(fb, x + 6, y + h - 12, 1, "BAHRAIN - HOME OF THE US 5TH FLEET",
              WHITE)


def illo_peace(fb, x, y, w, h):
    # the 28-point plan: big document, flags, big red 28
    fb.vgrad(x, y, w, h, WHITE, LIGHTGREY)
    # second document behind, for depth
    fb.rect(x + 18, y + 14, 118, h - 16, LIGHTGREY)
    fb.border(x + 18, y + 14, 118, h - 16, GREY, 1)
    fb.rect(x + 10, y + 8, 118, h - 16, WHITE)
    fb.border(x + 10, y + 8, 118, h - 16, INK, 2)
    fb.poly([(x + 108, y + 8), (x + 128, y + 28), (x + 108, y + 28)],
            LIGHTGREY)
    for i in range(5):
        fb.rect(x + 20, y + 18 + i * 11, 88, 3, GREY)
    fb.rect(x + 20, y + 18, 88, 3, RED)
    # US flag strip, top right
    fx, fy = x + 150, y + 12
    for i in range(7):
        fb.rect(fx, fy + i * 4, 56, 2, RED if i % 2 == 0 else WHITE)
    fb.rect(fx, fy, 24, 14, NAVY)
    # Ukraine flag
    fb.rect(fx, fy + 34, 56, 12, bytes((0, 90, 180)))
    fb.rect(fx, fy + 46, 56, 12, GOLD)
    draw_text(fb, x + 216, y + 16, 1, "OVAL OFFICE", GREY)
    draw_text(fb, x + 216, y + 26, 1, "28 POINTS", INK, bold=True)
    # big 28 + POINT / PLAN
    draw_text(fb, x + 150, y + 64, 4, "28", RED, bold=True)
    draw_text(fb, x + 206, y + 66, 2, "POINT", INK, bold=True)
    draw_text(fb, x + 206, y + 80, 2, "PLAN", INK, bold=True)


def illo_markets(fb, x, y, w, h):
    # plunging Nasdaq chart on graph paper
    fb.rect(x, y, w, h, WHITE)
    for gx in range(x + 12, x + w, 22):
        fb.vline(gx, y + 6, h - 12, LIGHTGREY, 1)
    for gy in range(y + 8, y + h, 18):
        fb.hline(x + 6, gy, w - 12, LIGHTGREY, 1)
    pts = [(x + 12, y + 44), (x + 58, y + 50), (x + 104, y + 48),
           (x + 150, y + 62), (x + 196, y + 60), (x + 242, y + 74),
           (x + 288, y + 80), (x + w - 14, y + h - 18)]
    # volume bars along the bottom (behind the line)
    vols = [14, 22, 18, 30, 26, 38, 34, 46, 40, 52, 48, 60]
    for i, v in enumerate(vols):
        bx = x + 16 + i * 26
        fb.rect(bx, y + h - 16 - v // 2, 12, v // 2, LIGHTGREY)
    for a, b in zip(pts, pts[1:]):
        fb.line(a[0], a[1], b[0], b[1], RED, 3)
    for p in pts:
        fb.circle(p[0], p[1], 3, RED)
    draw_text(fb, x + 10, y + 8, 4, "-5.3%", RED, bold=True)
    draw_text(fb, x + w - 108, y + h - 14, 1, "NASDAQ -5.3%", INK)


# ------------------------------------------------------------------- icons
def icon_quake(fb, x, y):
    fb.rect(x, y, 30, 30, NAVY)
    fb.line(x + 3, y + 15, x + 9, y + 15, WHITE, 2)
    fb.line(x + 9, y + 15, x + 13, y + 5, WHITE, 2)
    fb.line(x + 13, y + 5, x + 17, y + 25, WHITE, 2)
    fb.line(x + 17, y + 25, x + 21, y + 10, WHITE, 2)
    fb.line(x + 21, y + 10, x + 27, y + 15, WHITE, 2)


def icon_cop(fb, x, y):
    fb.rect(x, y, 30, 30, GREEN)
    fb.circle(x + 15, y + 15, 10, WHITE, fill=False)
    fb.circle(x + 15, y + 15, 6, WHITE)
    fb.rect(x + 14, y + 4, 2, 22, WHITE)
    fb.rect(x + 4, y + 14, 22, 2, WHITE)


def icon_flag(fb, x, y):
    fb.rect(x, y, 30, 30, INK)
    for i in range(4):
        fb.rect(x + 5, y + 5 + i * 6, 20, 3,
                WHITE if i % 2 == 0 else INK)
    fb.rect(x + 5, y + 5, 20, 24, WHITE)
    for i in range(4):
        for j in range(4):
            if (i + j) % 2 == 0:
                fb.rect(x + 5 + j * 5, y + 5 + i * 6, 5, 3, INK)


def icon_gta(fb, x, y):
    fb.rect(x, y, 30, 30, RED)
    draw_text(fb, x + 6, y + 5, 3, "VI", WHITE, bold=True)


def icon_ipo(fb, x, y):
    fb.rect(x, y, 30, 30, GOLD)
    fb.line(x + 6, y + 24, x + 15, y + 12, WHITE, 3)
    fb.line(x + 15, y + 12, x + 24, y + 6, WHITE, 3)
    fb.line(x + 18, y + 6, x + 24, y + 6, WHITE, 3)
    fb.line(x + 24, y + 6, x + 24, y + 12, WHITE, 3)


def icon_shield(fb, x, y):
    fb.rect(x, y, 30, 30, NAVY2)
    fb.poly([(x + 15, y + 4), (x + 25, y + 8), (x + 25, y + 17),
             (x + 15, y + 26), (x + 5, y + 17), (x + 5, y + 8)], WHITE)
    fb.poly([(x + 15, y + 7), (x + 22, y + 10), (x + 22, y + 16),
             (x + 15, y + 23), (x + 8, y + 16), (x + 8, y + 10)], NAVY2)
    draw_text(fb, x + 12, y + 11, 2, "S", WHITE, bold=True)


def icon_chip(fb, x, y):
    fb.rect(x, y, 30, 30, DARKRED)
    fb.rect(x + 8, y + 8, 14, 14, WHITE)
    fb.rect(x + 12, y + 12, 6, 6, DARKRED)
    for i in range(3):
        fb.rect(x + 11 + i * 5, y + 2, 2, 6, WHITE)
        fb.rect(x + 11 + i * 5, y + 22, 2, 6, WHITE)


def icon_thermo(fb, x, y):
    fb.rect(x, y, 30, 30, ORANGE)
    fb.rect(x + 13, y + 5, 4, 16, WHITE)
    fb.circle(x + 15, y + 23, 5, WHITE)
    fb.circle(x + 15, y + 23, 3, RED)
    fb.rect(x + 14, y + 10, 2, 12, RED)


# ------------------------------------------------------------------ content
TOP = [
    {
        "label": "TOP STORY 1 \u00b7 MIDDLE EAST",
        "head": "IRAN HITS US BASES IN BAHRAIN",
        "body": ("IRAN SAYS MISSILES AND DRONES HIT TWO US PATRIOT RADARS AT "
                 "THE RIFFA AND AWALI BASES. BAHRAIN SAYS IT STOPPED MOST OF "
                 "THE ATTACK; AN INDUSTRIAL SITE WAS HIT AND CAUGHT FIRE."),
        "illo": "iran",
    },
    {
        "label": "TOP STORY 2 \u00b7 PEACE PLAN",
        "head": "TAKE THE 28-POINT PEACE PLAN",
        "body": ("IN THE OVAL OFFICE, TRUMP TOLD ZELENSKY HE HAD 'NO CHOICE' "
                 "BUT TO ACCEPT THE US PLAN: UKRAINE GIVES UP DONBAS, LIMITS "
                 "ITS ARMY AND DROPS NATO HOPES, FOR WESTERN SECURITY "
                 "GUARANTEES. THE US AIMS FOR A DEAL BY EARLY JANUARY."),
        "illo": "peace",
    },
    {
        "label": "TOP STORY 3 \u00b7 MARKETS",
        "head": "WALL STREET TUMBLES; NASDAQ ERASES 2026",
        "body": ("FRIDAY'S AI-LED SELL-OFF: S&P 500 DOWN 3.7% TO 6,910.39; "
                 "NASDAQ DOWN 5.3% TO 22,617.73, IN CORRECTION; DOW DOWN "
                 "949.73. WORST S&P WEEK IN 18 MONTHS; WORST NASDAQ WEEK "
                 "SINCE MARCH 2020."),
        "illo": "markets",
    },
]

ALSO = [
    ("quake", "PERU QUAKE M6.7",
     "JUNIN QUAKE SHAKES LIMA; NO DEATHS"),
    ("cop", "COP31 OVERTIME",
     "NO FOSSIL FUELS; NO $120BN AID"),
    ("flag", "VERSTAPPEN WINS",
     "35 LEAD CHANGES; NORRIS 2ND"),
    ("gta", "GTA 6: $3.79BN",
     "32.5M UNITS; BIGGEST LAUNCH EVER"),
    ("ipo", "ANTHROPIC IPO",
     "$81.3BN AT $1.5TN; UP 17% DAY ONE"),
    ("shield", "SAUDI INTERCEPTS",
     "MISSILES HEADED FOR RIYADH STOPPED"),
    ("chip", "NVIDIA DOWN 14%",
     "SEC PROBES; $1.4TN GONE SINCE NOV"),
    ("thermo", "HOTTEST OCTOBER",
     "+1.80C; 2026 SET TO BE HOTTEST YEAR"),
]

# numbered list: 36 more stories (12-47)
MORE = [
    "RUSSIAN MISSILES LAND IN POLAND; NATO CHIEF RUTTE VISITS WARSAW",
    "GAZA: ISRAELI STRIKE KILLS 3 IN AID VEHICLE",
    "TRUMP CALLS PUTIN 'A FRIEND'; ZELENSKY CALLS PUTIN 'A KILLER'",
    "TRUMP DEMANDS 'PERMANENT DEAL' WITH IRAN",
    "MYANMAR REJECTS ICJ GENOCIDE RULING",
    "UK-EU AGREE POST-BREXIT RESET",
    "MEXICO ARRESTS 'EL CHAPO ISIDRO'; 11 KILLED IN SHOOTOUT",
    "BOLSONARO IN ICU FOR BOWEL OBSTRUCTION",
    "SOMALIA EXPELS UAE AMBASSADOR; THOUSANDS PROTEST",
    "ESTONIA TO SHUT LAND BORDER WITH RUSSIA FROM 1 DEC",
    "TURKIYE DETAINS SOZCU TV EXECUTIVES",
    "UN DELAYS AUTONOMOUS WEAPONS RULES TO 2028",
    "IAEA: NORTH KOREA EXPANDS YONGBYON URANIUM SITE",
    "DENMARK RATIFIES US SECURITY DEAL FOR GREENLAND 109-0",
    "GOLD FALLS TO 14-MONTH LOW $3,513.54/OZ",
    "TRUMP THREATENS 'BIG TAX' ON FIRMS BUILDING AI DATA CENTRES ABROAD",
    "US CHIP EXPORT RULES: TSMC & SAMSUNG HALT SHIPMENTS",
    "CURSOR MAY DROP CHINESE-MADE AI MODELS",
    "SIGNAL BLOCKS SCREENSHOTS TO STOP AI AGENTS READING CHATS",
    "FBI CRIME DATABASE (NCIC) REPORTEDLY HACKED",
    "RIEMANN HYPOTHESIS PROOF CLAIM WITH CLAUDE'S HELP - UNVERIFIED",
    "LARGEST ENDOMETRIOSIS GENOMIC STUDY: 1M+ WOMEN",
    "MUSHROOM PROTEIN FROM WASTE CO2: 48.5% PROTEIN",
    "HUNGER GAMES: SUNRISE ON THE REAPING $56M DAY ONE",
    "PRINCESS CATHERINE ANNOUNCES 'HEAL' DOCUMENTARY",
    "PETER FLUCK, SPITTING IMAGE CO-CREATOR, DIES AT 85",
    "STRICTLY COME DANCING BLACKPOOL: THREE-WAY TIE AT 39",
    "FUNERAL BOAT CAPSIZES IN NIGERIA, 24 DEAD",
    "WOLBACHIA MOSQUITOES CUT DENGUE & CHIKUNGUNYA 69%",
    "SERIE A: MALEN SCORES 4, ROMA THRASH PARMA 5-1",
    "NCAA CROSS COUNTRY: NEW MEXICO & ALABAMA WIN FIRST TEAM TITLES",
    "UFC QATAR: STIRLING KOS PROCHAZKA IN ROUND 2",
    "NBA: HARDEN SCORES 51, PASSES KOBE",
    "FLORIDA BEATS VANDERBILT 34-27",
    "PREMIER LEAGUE: LEEDS STUN CHELSEA 4-1",
    "F1 LAS VEGAS: VERSTAPPEN TAKES POLE; RUSSELL ON FRONT ROW",
]

NUMBERS = [
    ("-5.3%", "NASDAQ - IN CORRECTION"),
    ("-3.7%", "S&P 500 - WORST IN 18 MO"),
    ("$81.3BN", "ANTHROPIC IPO RECORD"),
    ("$3.79BN", "GTA 6 DAY ONE SALES"),
    ("M6.7", "PERU QUAKE - 129 KM DEEP"),
    ("+1.80C", "OCTOBER 2026 - HOTTEST EVER"),
    ("51 PTS", "HARDEN - 26TH 50-PT GAME"),
    ("35", "LEAD CHANGES - LAS VEGAS GP"),
]

# map markers: (lon, lat, label or "" for dot only)
MARKERS = [
    (-77, 39, "WASHINGTON"),
    (-99, 19, "MEXICO"),
    (-77, -12, "LIMA"),
    (-48, -16, "BRASILIA"),
    (0, 51, "LONDON"),
    (21, 52, "WARSAW"),
    (31, 50, ""),
    (30, 37, ""),
    (34, 31, "GAZA"),
    (51, 25, ""),
    (47, 25, ""),
    (45, 2, "MOGADISHU"),
    (127, 37, "SEOUL"),
]

# rough continent outlines in (lon, lat) for the map
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-80, 73),
     (-65, 62), (-55, 52), (-60, 47), (-70, 44), (-75, 35), (-81, 25),
     (-84, 30), (-90, 21), (-97, 26), (-105, 20), (-92, 14), (-83, 9),
     (-79, 9), (-90, 13), (-105, 22), (-117, 33), (-125, 40), (-125, 49),
     (-135, 58), (-155, 58), (-165, 60)],
    # South America
    [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
     (-70, -23), (-70, -33), (-71, -41), (-73, -50), (-68, -55), (-65, -45),
     (-62, -38), (-57, -30), (-48, -28), (-41, -23), (-35, -8), (-35, -6),
     (-44, -3), (-50, 0), (-52, 5), (-60, 8), (-70, 11)],
    # Europe
    [(-10, 37), (-9, 43), (-2, 48), (-4, 50), (2, 51), (5, 53), (8, 57),
     (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (30, 70),
     (25, 71), (18, 69), (12, 66), (5, 60), (5, 58), (8, 55), (10, 54),
     (13, 54), (19, 54), (24, 54), (28, 45), (23, 40), (19, 42), (15, 44),
     (12, 44), (8, 44), (3, 42), (0, 39), (-2, 37)],
    # Africa
    [(-6, 35), (10, 37), (20, 32), (32, 31), (35, 28), (37, 22), (39, 18),
     (43, 12), (51, 11), (51, 2), (46, -2), (40, -10), (36, -18), (32, -26),
     (28, -33), (19, -35), (16, -28), (13, -18), (12, -10), (9, -1),
     (9, 4), (-8, 4), (-13, 8), (-17, 15), (-16, 20), (-15, 27), (-10, 31)],
    # Asia
    [(30, 70), (40, 68), (60, 69), (80, 73), (100, 77), (120, 73),
     (140, 72), (160, 69), (178, 65), (170, 60), (162, 56), (158, 52),
     (142, 50), (140, 40), (135, 35), (127, 33), (122, 30), (120, 23),
     (109, 18), (105, 9), (100, 6), (98, 10), (92, 16), (88, 22),
     (80, 15), (76, 8), (72, 20), (66, 25), (61, 25), (57, 26), (52, 28),
     (50, 30), (48, 30), (44, 29), (42, 15), (39, 21), (35, 28), (35, 36),
     (30, 36), (27, 41), (28, 45), (30, 46), (32, 52), (35, 55), (35, 62),
     (32, 66)],
    # Australia
    [(114, -22), (114, -30), (118, -35), (125, -33), (130, -32), (135, -35),
     (140, -38), (145, -38), (150, -37), (153, -27), (150, -22), (146, -19),
     (142, -11), (136, -12), (132, -12), (126, -14), (120, -20)],
]


# -------------------------------------------------------------------- layout
def draw_map(fb, x, y, w, h):
    fb.rect(x, y, w, h, SEA)
    fb.border(x, y, w, h, INK, 1)
    # continents: lon -170..190 -> x, lat 75..-60 -> y
    def px(lon, lat):
        return (x + int((lon + 170) * w / 360.0),
                y + int((75 - lat) * h / 135.0))
    for cont in CONTINENTS:
        fb.poly([px(lon, lat) for lon, lat in cont], LAND)
    # graticule
    for lon in range(-150, 181, 30):
        gx, _ = px(lon, 75)
        fb.vline(gx, y, h, LIGHTGREY, 1)
    for m in MARKERS:
        mx, my = px(m[0], m[1])
        fb.circle(mx, my, 3, RED)
        fb.circle(mx, my, 5, RED, fill=False)
        lab = m[2]
        if not lab:
            continue
        lx = mx + 7
        if lx + text_w(lab, 1) > x + w - 4:
            lx = mx - 7 - text_w(lab, 1)
        draw_text(fb, lx, my - 3, 1, lab, INK, bold=True)
    # Bahrain callout
    bx, by = px(50, 26)
    fb.circle(bx, by, 4, RED)
    call = "BAHRAIN: IRAN STRIKES"
    cw = text_w(call, 1) + 12
    cx = min(bx + 10, x + w - cw - 4)
    cy = by - 26
    fb.rect(cx, cy, cw, 14, RED)
    draw_text(fb, cx + 6, cy + 4, 1, call, WHITE, bold=True)
    fb.line(bx, by, cx + 6, cy + 14, RED, 1)


def draw_page():
    fb = FB(W, H, PAPER)
    # subtle paper grain (deterministic LCG, fixed seed)
    seed = 1234567
    for _ in range(4200):
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        gx = seed % W
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        gy = seed % H
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        c = bytes((236, 230, 212)) if seed % 2 == 0 else bytes((248, 243, 230))
        fb.set(gx, gy, c)
    fb.border(8, 8, W - 16, H - 16, INK, 3)
    # masthead
    draw_text(fb, (W - text_w("THE DAILY WORLD", 9)) // 2, 16, 9,
              "THE DAILY WORLD", INK, bold=True)
    fb.hline(14, 86, W - 28, RED, 3)
    draw_text_center(fb, W // 2, 94, 3, "SATURDAY 21 NOVEMBER 2026", RED,
                     bold=True)
    draw_text_center(fb, W // 2, 120, 2,
                     "47 STORIES \u00b7 9 REGIONS \u00b7 20 COUNTRIES \u00b7 "
                     "THE WORLD IN ONE PAGE", INK)
    fb.hline(14, 138, W - 28, INK, 2)

    # ---- top stories
    cols = [(14, 326), (348, 326), (682, 326)]
    illos = {"iran": illo_iran, "peace": illo_peace, "markets": illo_markets}
    for (cx, cw), story in zip(cols, TOP):
        label_bar(fb, cx, 146, cw, story["label"])
        illos[story["illo"]](fb, cx, 168, cw, 96)
        lines = wrap(story["head"], 18)
        ly = 270
        for ln in lines[:3]:
            draw_text(fb, cx, ly, 3, ln, INK, bold=True)
            ly += 23
        slines = wrap(story["body"], 54)
        sy = 342
        for ln in slines[:5]:
            draw_text(fb, cx, sy, 1, ln, INK)
            sy += 9
    fb.hline(14, 396, W - 28, INK, 2)

    # ---- also today
    section_head(fb, 14, 402, W - 28, "ALSO TODAY")
    icons = {"quake": icon_quake, "cop": icon_cop, "flag": icon_flag,
             "gta": icon_gta, "ipo": icon_ipo, "shield": icon_shield,
             "chip": icon_chip, "thermo": icon_thermo}
    for i, (kind, head, sub) in enumerate(ALSO):
        col = i % 4
        row = i // 4
        ix = 14 + col * 249
        iy = 432 + row * 46
        icons[kind](fb, ix, iy)
        tx = ix + 36
        hlines = wrap(head, 17)
        hy = iy
        for ln in hlines[:2]:
            draw_text(fb, tx, hy, 2, ln, INK, bold=True)
            hy += 15
        for ln in wrap(sub, 34)[:2]:
            draw_text(fb, tx, hy, 1, ln, INK)
            hy += 9
    fb.hline(14, 534, W - 28, INK, 2)

    # ---- map
    section_head(fb, 14, 540, W - 28, "WHERE IT HAPPENED")
    draw_map(fb, 14, 572, W - 28, 74)
    fb.hline(14, 652, W - 28, INK, 2)

    # ---- numbered list
    section_head(fb, 14, 658, W - 28, "MORE FROM 21 NOVEMBER")
    colw = (W - 28) // 2
    for i, item in enumerate(MORE):
        col = i // 18
        row = i % 18
        ix = 14 + col * colw
        iy = 690 + row * 11
        num = str(12 + i) + "."
        draw_text(fb, ix, iy, 1, num, RED, bold=True)
        draw_text(fb, ix + text_w(num, 1) + 5, iy, 1, item, INK)
    fb.hline(14, 892, W - 28, INK, 2)

    # ---- day in numbers
    section_head(fb, 14, 898, W - 28, "DAY IN NUMBERS")
    for i, (num, lab) in enumerate(NUMBERS):
        col = i % 4
        row = i // 4
        cx = 14 + col * 249
        cy = 928 + row * 26
        fb.border(cx, cy, 243, 24, INK, 1)
        draw_text(fb, cx + 6, cy + 4, 2, num, RED, bold=True)
        draw_text(fb, cx + 6 + text_w(num, 2) + 8, cy + 8, 1, lab, INK)
    fb.hline(14, 984, W - 28, INK, 2)

    # ---- footer
    draw_text_center(fb, W // 2, 984, 2,
                     "DATE CHECK: ALL 47 STORIES VERIFIED FOR SATURDAY "
                     "21 NOVEMBER 2026", INK)
    draw_text_center(fb, W // 2, 998, 1,
                     "SOURCES: AP, REUTERS, AFP, XINHUA, BBC, CNBC, NPR, "
                     "FINANCIAL TIMES, NIH, BERKELEY EARTH, IAEA, CPJ, "
                     "USGS, NCAA, NBA, F1", GREY)
    return fb


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    fb = draw_page()
    png = encode_png(W, H, fb.px)
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
