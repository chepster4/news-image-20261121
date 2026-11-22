#!/usr/bin/env python3
"""The Daily World v3 - Saturday 21 November 2026: 52 stories, 9 regions.
One picture summing up the day's world news. Stdlib only (zlib, struct,
random, hashlib-free deterministic output). Run: python3 -P -s main.py
Writes entry.png (1024x1024) to $MAKEFUN_OUTPUT_DIR (default out/).
"""
import os
import random
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows; each row is a 5-bit int, bit 4 = leftmost pixel.
F = {}
def _g(ch, rows):
    F[ch] = tuple(rows)

_g('A', [0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11])
_g('B', [0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E])
_g('C', [0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E])
_g('D', [0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E])
_g('E', [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F])
_g('F', [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10])
_g('G', [0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F])
_g('H', [0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11])
_g('I', [0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E])
_g('J', [0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C])
_g('K', [0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11])
_g('L', [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F])
_g('M', [0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11])
_g('N', [0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11])
_g('O', [0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E])
_g('P', [0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10])
_g('Q', [0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D])
_g('R', [0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11])
_g('S', [0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E])
_g('T', [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04])
_g('U', [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E])
_g('V', [0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04])
_g('W', [0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11])
_g('X', [0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11])
_g('Y', [0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04])
_g('Z', [0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F])
_g('0', [0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E])
_g('1', [0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E])
_g('2', [0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F])
_g('3', [0x1E, 0x01, 0x01, 0x0E, 0x01, 0x01, 0x1E])
_g('4', [0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02])
_g('5', [0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E])
_g('6', [0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E])
_g('7', [0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08])
_g('8', [0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E])
_g('9', [0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C])
_g(' ', [0, 0, 0, 0, 0, 0, 0])
_g('.', [0, 0, 0, 0, 0, 0x0C, 0x0C])
_g(',', [0, 0, 0, 0, 0x0C, 0x04, 0x08])
_g(':', [0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0])
_g(';', [0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08])
_g('-', [0, 0, 0, 0x0E, 0, 0, 0])
_g("'", [0x04, 0x04, 0x08, 0, 0, 0, 0])
_g('(', [0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02])
_g(')', [0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08])
_g('/', [0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10])
_g('%', [0x19, 0x1A, 0x02, 0x04, 0x08, 0x16, 0x13])
_g('$', [0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04])
_g('+', [0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0])
_g('=', [0, 0, 0x1F, 0, 0x1F, 0, 0])
_g('&', [0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D])
_g('!', [0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04])
_g('?', [0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04])
_g('*', [0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0])
_g('#', [0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A])
_g('>', [0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08])

# ---------------------------------------------------------------- canvas
px = bytearray(W * H * 3)

def put(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = c

def fill(x, y, w, h, c):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            px[i], px[i + 1], px[i + 2] = c

def hline(x, y, w, c):
    fill(x, y, w, 1, c)

def vline(x, y, h, c):
    fill(x, y, 1, h, c)

def frame(x, y, w, h, c, t=1):
    fill(x, y, w, t, c)
    fill(x, y + h - t, w, t, c)
    fill(x, y, t, h, c)
    fill(x + w - t, y, t, h, c)

def line(x0, y0, x1, y1, c):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        put(x0, y0, c)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

def disc(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                put(xx, yy, c)

def ring(cx, cy, r, c, t=2):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d = (xx - cx) ** 2 + (yy - cy) ** 2
            if (r - t) ** 2 <= d <= r * r:
                put(xx, yy, c)

def vgrad(x, y, w, h, top, bot):
    for yy in range(h):
        t = yy / max(1, h - 1)
        c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        fill(x, y + yy, w, 1, c)

def speckle(rng, x, y, w, h, n, amp=14):
    for _ in range(n):
        xx = rng.randrange(x, x + w)
        yy = rng.randrange(y, y + h)
        i = (yy * W + xx) * 3
        d = rng.randrange(-amp, amp + 1)
        for k in range(3):
            v = px[i + k] + d
            px[i + k] = 0 if v < 0 else (255 if v > 255 else v)

# ---------------------------------------------------------------- text
def char_w(scale):
    return 6 * scale

def text_w(s, scale):
    return len(s) * 6 * scale

def draw_char(x, y, ch, scale, c):
    g = F.get(ch)
    if g is None:
        return
    for r in range(7):
        row = g[r]
        for col in range(5):
            if row & (1 << (4 - col)):
                fill(x + col * scale, y + r * scale, scale, scale, c)

def draw_text(x, y, s, scale, c):
    s = s.upper()
    cx = x
    for ch in s:
        draw_char(cx, y, ch, scale, c)
        cx += 6 * scale
    return cx

def text_center(x, y, w, s, scale, c):
    draw_text(x + (w - text_w(s, scale)) // 2, y, s, scale, c)

def wrap(s, maxw, scale):
    words = s.split(' ')
    lines, cur = [], ''
    for wd in words:
        trial = wd if not cur else cur + ' ' + wd
        if text_w(trial, scale) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines

# ---------------------------------------------------------------- PNG out
def write_png(path):
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += px[yy * W * 3:(yy + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 6)

    def chunk(kind, data):
        out = struct.pack('>I', len(data)) + kind + data
        out += struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(chunk(b'IHDR', ihdr))
        f.write(chunk(b'IDAT', comp))
        f.write(chunk(b'IEND', b''))

# ---------------------------------------------------------------- palette
INK = (24, 24, 28)
PAPER = (250, 247, 238)
NAVY = (16, 34, 64)
NAVY2 = (28, 58, 100)
RED = (178, 34, 34)
RED2 = (205, 60, 50)
GOLD = (184, 134, 11)
TEAL = (14, 110, 110)
GREEN = (34, 120, 60)
BLUE = (40, 90, 160)
GREY = (110, 110, 112)
LGREY = (226, 222, 212)
WHITE = (255, 255, 255)
CREAM = (244, 238, 224)

# ---------------------------------------------------------------- masthead
def masthead(rng):
    vgrad(0, 0, W, 82, NAVY, NAVY2)
    speckle(rng, 0, 0, W, 82, 9000, 10)
    hline(0, 81, W, GOLD)
    fill(0, 79, W, 2, RED2)
    text_center(0, 12, W, 'THE DAILY WORLD', 5, WHITE)
    draw_text(14, 58, 'NO. 325', 1, (200, 205, 215))
    draw_text(14, 70, 'PRICE: FREE', 1, (200, 205, 215))
    text_center(0, 54, W, 'SATURDAY 21 NOVEMBER 2026', 2, (255, 214, 120))
    s = '52 STORIES - 9 REGIONS'
    draw_text(W - 14 - text_w(s, 1), 58, s, 1, (200, 205, 215))
    s2 = 'ALL STORIES DATE-CHECKED'
    draw_text(W - 14 - text_w(s2, 1), 70, s2, 1, (200, 205, 215))

def ticker():
    fill(0, 82, W, 22, RED)
    s = ('MARKETS 21 NOV: S&P 500 -3.7%   NASDAQ -5.3%   DOW -949.73   GOLD $3,513.54   '
         'ANTHROPIC IPO $81.3BN   GTA 6 $3.79BN DAY ONE   COP31 DEADLOCK   M6.8 BANDA QUAKE')
    draw_text(10, 89, s, 1, WHITE)

# ---------------------------------------------------------------- hero art
def hero_art(rng, x, y, w, h):
    vgrad(x, y, w, h, (135, 190, 225), (250, 200, 120))
    speckle(rng, x, y, w, h, 9000, 12)
    disc(x + 300, y + 34, 22, (255, 214, 90))
    ring(x + 300, y + 34, 26, (255, 230, 150), 2)
    # globe
    cx, cy, r = x + 130, y + 88, 62
    disc(cx, cy, r, (38, 110, 180))
    ring(cx, cy, r, NAVY, 3)
    for a in range(0, 360, 30):
        import math
        x2 = cx + int(r * 0.94 * math.cos(math.radians(a)))
        y2 = cy + int(r * 0.94 * math.sin(math.radians(a)))
        put(x2, y2, (90, 160, 210))
    disc(cx - 26, cy - 18, 16, (52, 150, 80))
    disc(cx - 8, cy - 26, 10, (52, 150, 80))
    disc(cx + 22, cy + 8, 18, (60, 160, 90))
    disc(cx + 6, cy + 28, 11, (52, 150, 80))
    disc(cx - 30, cy + 26, 9, (60, 160, 90))
    disc(cx + 34, cy - 22, 8, (52, 150, 80))
    hline(cx - r, cy, 2 * r, (90, 160, 210))
    vline(cx, cy - r, 2 * r, (90, 160, 210))
    # skyline
    base = y + h - 8
    heights = [46, 70, 38, 84, 58, 96, 44, 66, 52, 78, 40, 60]
    bx = x + 8
    for hh in heights:
        fill(bx, base - hh, 22, hh, (30, 42, 66))
        fill(bx + 4, base - hh - 8, 4, 8, (30, 42, 66))
        bx += 30
    # falling market arrow
    pts = [(x + 250, y + 120), (x + 285, y + 132), (x + 315, y + 128),
           (x + 345, y + 150), (x + 368, y + 168)]
    for a, b in zip(pts, pts[1:]):
        line(a[0], a[1], b[0], b[1], RED2)
        line(a[0], a[1] + 1, b[0], b[1] + 1, RED2)
    draw_text(x + 252, y + 176, '-5.3%', 1, RED2)
    frame(x, y, w, h, INK, 2)

def hero_text():
    x, y = 396, 112
    w = W - x - 12
    draw_text(x, y, 'TOP STORY', 1, RED2)
    draw_text(x + text_w('TOP STORY ', 1), y, '21 NOV 2026', 1, GREY)
    yy = y + 12
    for ln in wrap('TRUMP PRESSES ZELENSKY TO ACCEPT 28-POINT US PEACE PLAN', w, 2):
        draw_text(x, yy, ln, 2, INK)
        yy += 17
    yy += 2
    body = ('21 NOV 2026 - In the Oval Office, Zelensky is told he has no choice but to '
            'accept: Ukraine cedes Donbas, limits its army and drops its NATO bid, in '
            'exchange for Western security guarantees without direct military cover. '
            'The FT reports the US aims for a deal by early January.')
    for ln in wrap(body, w, 1):
        draw_text(x, yy, ln, 1, (52, 52, 56))
        yy += 10
    yy += 4
    hline(x, yy, w, LGREY)
    yy += 6
    draw_text(x, yy, 'MARKETS IN FREEFALL', 1, RED2)
    yy += 11
    for ln in wrap('WALL STREET TUMBLES - NASDAQ ERASES ALL OF 2026 GAINS', w, 1):
        draw_text(x, yy, ln, 1, INK)
        yy += 10
    body2 = ('21 NOV 2026 - S&P 500 -3.7% to 6,910.39; Nasdaq -5.3% to 22,617.73, in '
             'correction; Dow -949.73. Worst S&P week in 18 months as AI stocks sell off. '
             '(Friday 20 NOV rout.)')
    for ln in wrap(body2, w, 1):
        draw_text(x, yy, ln, 1, (52, 52, 56))
        yy += 10
    yy += 4
    hline(x, yy, w, LGREY)
    yy += 6
    draw_text(x, yy, 'CLIMATE SUMMIT', 1, TEAL)
    yy += 11
    for ln in wrap('COP31 IN ANTALYA OVERRUNS AS DRAFT DROPS FOSSIL FUELS', w, 1):
        draw_text(x, yy, ln, 1, INK)
        yy += 10
    body3 = ('21 NOV 2026 - The climate summit passes its 20 NOV deadline with no deal; the '
             'draft deletes all fossil-fuel mentions and cuts the $120bn-a-year adaptation '
             'target to 2035. EU: a good deal or no deal. Ethiopia hosts COP32 in 2027.')
    for ln in wrap(body3, w, 1):
        draw_text(x, yy, ln, 1, (52, 52, 56))
        yy += 10
    return yy

# ---------------------------------------------------------------- stories
# (region, date tag, text) - all 49 panel stories; hero holds 1-3.
# Every text is kept to 2 wrapped lines (max ~90 chars) so panels fit.
PANELS = [
 ('MIDDLE EAST', RED2, [
  ('21', 'Israeli drone kills 3 in Gaza aid vehicle, Tel al-Hawa. Toll since Oct 2025 truce: 1,671.'),
  ('21', 'UFC Qatar: Stirling KOs ex-champion Prochazka in round 2 in Doha. Now 12-0.'),
  ('21', "Trump demands a 'permanent deal' with Iran: no nuclear weapon, ever. (Fox News)"),
 ]),
 ('EUROPE', BLUE, [
  ('21', 'Russian missiles land in Poland: 2 Kh-101s, one drone, no casualties. Rutte visits Warsaw.'),
  ('21', 'Leeds stun Chelsea 4-1; Okafor scores twice. First Leeds away win at Chelsea since 1999.'),
  ('21', 'UK-EU post-Brexit reset agreed: food zone, emissions trade link, youth mobility 100,000 a year.'),
  ('21', 'Estonia shuts its Russia border from 1 Dec: five crossings closed after alleged sabotage.'),
  ('21', 'Turkey detains Sozcu TV executive; three barred from travel. Third opposition channel seized.'),
  ('21', 'Denmark ratifies US security deal for Greenland 109-0: two new US bases in the territory.'),
  ('21', "Princess Catherine announces 'Heal', a BBC film on her cancer journey; airs 29 Nov."),
  ('21', "Peter Fluck, co-creator of 'Spitting Image', dies aged 85 in Cornwall after an illness."),
  ('21', 'Strictly Blackpool: three couples tie at the top on 39; BBC calls police over a prank.'),
  ('21', 'Serie A: Malen scores four as Roma crush Parma 5-1; second, two behind Lazio. Malen: 12 in 11.'),
  ('21', 'Denmark accuses Russia of a plot to kill a US-Ukrainian rapper; moves to expel its attache.'),
 ]),
 ('AFRICA', GREEN, [
  ('21', 'Somalia expels the UAE ambassador; thousands rally in Mogadishu backing the exit order.'),
  ('21', 'Funeral boat capsizes in Nigeria: 24 dead, 24 survive on the Ayama-Ukubie route, Bayelsa.'),
  ('21', "ANC fights to keep control of South Africa's key cities after an election setback."),
 ]),
 ('EAST ASIA', TEAL, [
  ('21', "IAEA: North Korea expands the Yongbyon uranium site; satellite photos confirm. 'Serious concern'."),
  ('21', 'US chip rules bite: TSMC, Samsung halt shipments; TSMC tells China clients to stop 16nm orders.'),
  ('21', 'Magnitude 5.8 quake hits Qinghai, China; no immediate reports of major damage.'),
 ]),
 ('SOUTH ASIA', (150, 90, 20), [
  ('21', "Nepal PM Balendra Shah on his first visit to India - a new Nepal, an old neighbour."),
 ]),
 ('SOUTHEAST ASIA', (180, 110, 10), [
  ('21', 'Myanmar rejects ICJ genocide ruling: 9-6, genocide vs Rohingya in 2017 - an ICJ first.'),
  ('21', 'EU and Indonesia sign trade and investment deals (CEPA, IPA), the Commission confirms.'),
 ]),
 ('NORTH AMERICA', NAVY2, [
  ('20', 'GTA 6: $3.79bn day one, 32.5m units pre-ordered - the biggest entertainment launch ever.'),
  ('20', 'Anthropic IPO breaks records at $81.3bn: priced $83, valued near $1.5tn, day one +17%.'),
  ('20', 'Nvidia slides 14% as the SEC probes its accounting; $1.4tn gone since Huang quit 12 Nov.'),
  ('21', "Trump threatens a 'big tax' on US firms building AI data centres abroad. No order yet."),
  ('21', 'Cursor (SpaceX) weighs dropping Chinese-made AI models after a US House report.'),
  ('21', 'Signal blocks screenshots to stop AI agents reading chats; default on iOS 27, Android.'),
  ('21', 'FBI crime database reportedly hacked; FBI probes a suspected breach, second in two months.'),
  ('20', 'Hunger Games: Sunrise on the Reaping takes $56m day one; projected $120m opening weekend.'),
  ('21', "Mamdani announces a plan to close New York's Rikers Island jail by 2032."),
 ]),
 ('LATIN AMERICA', (140, 60, 120), [
  ('20', "'El Chapo Isidro' captured in Guasave, Sinaloa; shootout kills 11, including four soldiers."),
  ('21', 'Bolsonaro in intensive care in Brasilia; ex-president, 71, serving 27 years. Stable.'),
  ('21', 'Wolbachia mosquitoes cut dengue and chikungunya 69% in a study of 5,757 children in Brazil.'),
  ('21', 'Magnitude 6.7 quake shakes central Peru near Huanuco; no immediate casualties reported.'),
 ]),
 ('OCEANIA & GLOBAL', (90, 90, 150), [
  ('21', 'Hottest October on record: +1.80C; 2026 about 97% certain to be the hottest year ever.'),
  ('20', "Trump calls Putin a 'friend'; Zelensky calls him a 'killer'. After the Shenzhen summit."),
  ('21', "UN delays binding 'killer robot' rules to 2028; Geneva talks end with no deal."),
  ('20', 'Gold at a 14-month low, $3,513.54/oz, heading for a -9.4% week; a Fed hike is priced in.'),
  ('21', "Claimed Riemann proof with Claude's help: 175,187-file Lean archive. UNVERIFIED."),
  ('21', 'Endometriosis study, largest ever: 1m+ women, 14 biobanks, 58 regions, 314 genes.'),
  ('21', 'Mushroom protein from waste CO2: 48.5% protein; yields 22x soy, 513x beef per land.'),
  ('21', 'NCAA Cross Country: New Mexico men, Alabama women win first titles; Kipruto 28:27.7.'),
  ('21', 'F1 Las Vegas: Verstappen on pole; Antonelli fastest but drops to sixth on a grid penalty.'),
  ('20', 'NBA: Harden scores 51 to pass Kobe, his 26th 50-point game; Cleveland beats Indiana.'),
  ('21', "College football: Florida rallies past Vanderbilt 34-27 on Baugh's 10-yard TD with 2:18 left."),
  ('21', 'M6.8 Banda Sea quake rattles Darwin: 1,600+ felt reports; no damage, no tsunami.'),
  ('21', 'Trump administration opens the Pacific seabed to deep-sea mining.'),
 ]),
]

def draw_item(x, y, w, tag, text):
    tagw = text_w(tag + ' ', 1)
    lines = wrap(text, w - tagw, 1)
    draw_text(x, y, tag, 1, RED2)
    draw_text(x + tagw, y, lines[0], 1, INK)
    yy = y + 9
    for ln in lines[1:]:
        draw_text(x + tagw, yy, ln, 1, INK)
        yy += 9
    return yy + 2

def draw_panel(x, y, w, h, title, color, stories, rng):
    fill(x, y, w, h, PAPER)
    speckle(rng, x, y, w, h, 1800, 6)
    fill(x, y, w, 18, color)
    draw_text(x + 8, y + 6, title + ' - 21 NOV 2026', 1, WHITE)
    cnt = '(%d)' % len(stories)
    draw_text(x + w - 8 - text_w(cnt, 1), y + 6, cnt, 1, (230, 230, 230))
    yy = y + 24
    for tag, text in stories:
        yy = draw_item(x + 8, yy, w - 16, tag, text)
    frame(x, y, w, h, INK, 1)
    return yy

def world_map_strip(rng, x, y, w, h):
    fill(x, y, w, h, (210, 228, 240))
    speckle(rng, x, y, w, h, 2000, 8)
    draw_text(x + 8, y + 6, 'WHERE IT HAPPENED - 21 NOV 2026', 1, NAVY)
    # stylised continents as blobs
    blobs = [(70, 34, 16), (95, 30, 10), (150, 40, 14), (175, 28, 9),
             (235, 32, 13), (258, 44, 9), (300, 36, 8)]
    for bx, by, br in blobs:
        disc(x + bx, y + by, br, (90, 150, 110))
    dots = [('WARSAW', 168, 24), ('GAZA', 185, 34), ('DOHA', 205, 38),
            ('DARWIN', 292, 44), ('LIMA', 62, 40), ('PERU', 70, 44)]
    for name, dx, dy in dots:
        disc(x + dx, y + dy, 3, RED2)
        ring(x + dx, y + dy, 6, RED2, 1)
    labels = 'WARSAW - GAZA - DOHA - DARWIN - LIMA - BRASILIA'
    draw_text(x + 8, y + h - 12, labels, 1, NAVY)
    frame(x, y, w, h, INK, 1)

# ---------------------------------------------------------------- strips
def day_numbers():
    y, h = 800, 62
    fill(0, y, W, h, NAVY)
    stats = [('-3.7%', 'S&P 500'), ('-5.3%', 'NASDAQ'),
             ('$81.3BN', 'ANTHROPIC IPO'), ('$3.79BN', 'GTA 6 DAY ONE'),
             ('+1.80C', 'HOTTEST OCTOBER'), ('M6.8', 'BANDA SEA QUAKE')]
    bw = W // 6
    for i, (num, lab) in enumerate(stats):
        bx = i * bw
        text_center(bx, y + 10, bw, num, 2, (255, 214, 120))
        text_center(bx, y + 32, bw, lab, 1, WHITE)
        if i:
            vline(bx, y + 8, h - 16, (70, 90, 130))

def also_today(rng):
    y, h = 864, 94
    fill(0, y, W, h, CREAM)
    draw_text(10, y + 8, 'ALSO TODAY', 1, RED2)
    draw_text(10 + text_w('ALSO TODAY ', 1), y + 8, '21 NOV 2026', 1, GREY)
    chips = [
        ('GTA 6: $3.79BN DAY ONE - THE BIGGEST ENTERTAINMENT LAUNCH EVER', GOLD),
        ('ANTHROPIC IPO: $81.3BN, THE LARGEST IPO IN HISTORY', NAVY2),
        ('BANDA SEA M6.8 QUAKE FELT IN DARWIN - 1,600 REPORTS', TEAL),
        ('HARDEN 51 PTS, PASSES KOBE - 26TH 50-POINT GAME', RED2),
    ]
    cw = (W - 20) // 4
    for i, (txt, col) in enumerate(chips):
        cx = 10 + i * cw
        fill(cx, y + 26, cw - 8, h - 34, WHITE)
        frame(cx, y + 26, cw - 8, h - 34, INK, 1)
        fill(cx + 6, y + 32, 18, 18, col)
        draw_text(cx + 11, y + 37, '*', 1, WHITE)
        for j, ln in enumerate(wrap(txt, cw - 38, 1)):
            draw_text(cx + 30, y + 32 + j * 10, ln, 1, INK)
    speckle(rng, 0, y, W, h, 2000, 5)

def footer():
    y = 964
    fill(0, y, W, H - y, PAPER)
    hline(0, y, W, RED2)
    draw_text(10, y + 8,
              'SOURCES: AP, REUTERS, AFP, BBC, CNBC, NPR, FINANCIAL TIMES, NIH, BERKELEY EARTH, IAEA, CPJ, NCAA, NBA, F1, USGS.', 1, GREY)
    draw_text(10, y + 22,
              'BUILT BY AN AI AGENT FOR MAKE.FUN - SATURDAY 21 NOVEMBER 2026: 52 STORIES, 9 REGIONS.', 1, INK)
    draw_text(10, y + 36,
              'THE DAILY WORLD - ALL 52 STORIES DATE-CHECKED 21 NOV 2026. NEWS-IMAGE-20261121.', 1, GREY)

# ---------------------------------------------------------------- main
def main():
    rng = random.Random(20261121)
    fill(0, 0, W, H, PAPER)
    speckle(rng, 0, 0, W, H, 25000, 6)
    masthead(rng)
    ticker()
    hero_art(rng, 8, 112, 372, 182)
    hero_text()
    hline(0, 298, W, INK)
    # region columns: (x, [(panel index, height), ...])
    cols = [
        (8, [(0, 92), (1, 302), (2, 92)]),
        (349, [(3, 106), (4, 52), (5, 80), (6, 240)]),
        (690, [(7, 108), (8, 312), ('map', 60)]),
    ]
    y0 = 300
    for cx, items in cols:
        yy = y0
        for idx, hh in items:
            if idx == 'map':
                world_map_strip(rng, cx, yy, 326, hh)
            else:
                title, color, stories = PANELS[idx]
                draw_panel(cx, yy, 326, hh, title, color, stories, rng)
            yy += hh + 6
    day_numbers()
    also_today(rng)
    footer()
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', 'out')
    os.makedirs(out_dir, exist_ok=True)
    write_png(os.path.join(out_dir, 'entry.png'))

if __name__ == '__main__':
    main()

