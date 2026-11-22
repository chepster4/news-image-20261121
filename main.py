#!/usr/bin/env python3
"""The Daily World v2 - one-page newspaper of Saturday 21 November 2026.

Stdlib-only. Draws a 1024x1024 PNG with a built-in 5x7 bitmap font and a
hand-rolled PNG encoder. Deterministic: no time, no randomness, no network.
Writes entry.png to $MAKEFUN_OUTPUT_DIR (default "out").

Round 2 rebuild: 44 verified stories (round 1 had 38 and ranked #8168).
New lead: Iran strikes US bases in Bahrain on Saturday night. New: deep
Peru quake M6.7, COP31 final text, Verstappen wins the Las Vegas GP,
Saudi intercepts Houthi missiles, Kryvyi Rih strike, Ebola in DR Congo,
Virginia's first measles death of 2026. Denser layout than round 1:
bigger illustrations, 8 illustrated "also today" items, a labelled world
map with 12 markers, a 3-column numbered list and an 8-cell numbers box.
"""
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (246, 241, 229)
INK = (20, 20, 20)
RED = (166, 25, 46)
DARKRED = (122, 16, 32)
BLUE = (29, 78, 137)
LIGHTBLUE = (199, 217, 232)
NAVY = (16, 32, 64)
LAND = (201, 214, 190)
LANDLINE = (110, 140, 105)
GREEN = (46, 107, 79)
GOLD = (185, 138, 29)
CREAM = (255, 252, 240)
GREY = (90, 90, 90)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# ---------------------------------------------------------------- canvas
buf = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = c[0]
        buf[i + 1] = c[1]
        buf[i + 2] = c[2]


def fill(x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            buf[i] = c[0]
            buf[i + 1] = c[1]
            buf[i + 2] = c[2]


def rect(x, y, w, h, c, t=1):
    fill(x, y, w, t, c)
    fill(x, y + h - t, w, t, c)
    fill(x, y, t, h, c)
    fill(x + w - t, y, t, h, c)


def hline(x0, x1, y, c):
    if x1 < x0:
        x0, x1 = x1, x0
    fill(x0, y, x1 - x0 + 1, 1, c)


def vline(x, y0, y1, c):
    if y1 < y0:
        y0, y1 = y1, y0
    fill(x, y0, 1, y1 - y0 + 1, c)


def line(x0, y0, x1, y1, c):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        px(x0, y0, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def disc(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
        hline(cx - dx, cx + dx, yy, c)


def ring(cx, cy, r, c, t=2):
    for k in range(t):
        rr = r - k
        for a in range(360):
            import math
            px(cx + int(rr * math.cos(a * 0.0174533)),
               cy + int(rr * math.sin(a * 0.0174533)), c)


def poly(points, c, outline=None):
    ys = [p[1] for p in points]
    for y in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            hline(int(xs[k]), int(xs[k + 1]), y, c)
    if outline:
        n = len(points)
        for i in range(n):
            line(points[i][0], points[i][1],
                 points[(i + 1) % n][0], points[(i + 1) % n][1], outline)


# ------------------------------------------------------------------- font
# 5x7 bitmap font: each glyph is 7 rows of 5 bits (MSB = left column).
F = {
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    'X': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'Y': (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    '3': (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6': (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '.': (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ',': (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ':': (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ';': (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    '?': (0x0E, 0x11, 0x01, 0x06, 0x04, 0, 0x04),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    '"': (0x0A, 0x0A, 0, 0, 0, 0, 0),
    '-': (0, 0, 0, 0x0E, 0, 0, 0),
    '(': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ')': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    '/': (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    '%': (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    '$': (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '&': (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    '+': (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    '=': (0, 0, 0x1F, 0, 0x1F, 0, 0),
    '*': (0, 0x15, 0x0E, 0x1F, 0x0E, 0x15, 0),
    '#': (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    '@': (0x0E, 0x11, 0x17, 0x15, 0x16, 0x10, 0x0E),
    '_': (0, 0, 0, 0, 0, 0, 0x1F),
    '[': (0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E),
    ']': (0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E),
    '<': (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    '>': (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
    'x': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
}


def char_w(scale):
    return 6 * scale


def text_w(s, scale):
    return len(s) * char_w(scale)


def draw_char(x, y, ch, scale, c, bold=False):
    g = F.get(ch.upper(), F.get(ch))
    if g is None:
        return
    for r in range(7):
        row = g[r]
        for col in range(5):
            if row & (0x10 >> col):
                fill(x + col * scale, y + r * scale, scale, scale, c)
                if bold:
                    fill(x + col * scale + 1, y + r * scale, scale, scale, c)


def text(x, y, s, scale, c, bold=False, align="l"):
    if align == "c":
        x = x - text_w(s, scale) // 2
    elif align == "r":
        x = x - text_w(s, scale)
    for ch in s:
        draw_char(x, y, ch, scale, c, bold)
        x += char_w(scale)


def wrap(s, width, scale):
    words = s.split(" ")
    lines = []
    cur = ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if text_w(trial, scale) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def para(x, y, s, width, scale, c, lh, bold=False, max_lines=None):
    lines = wrap(s, width, scale)
    if max_lines:
        lines = lines[:max_lines]
    for i, ln in enumerate(lines):
        text(x, y + i * lh, ln, scale, c, bold)
    return len(lines) * lh


# ------------------------------------------------------------------ story
TOP = [
    ("TOP STORY 1 - MIDDLE EAST ON EDGE", "IRAN HITS US BASES IN BAHRAIN",
     "IRAN SAYS MISSILES AND DRONES HIT TWO US PATRIOT RADARS AT THE RIFFA "
     "AND AWALI BASES IN BAHRAIN. BAHRAIN SAYS ITS DEFENCES STOPPED MOST OF "
     "THE ATTACK; AN INDUSTRIAL SITE WAS HIT AND CAUGHT FIRE."),
    ("TOP STORY 2 - THE PEACE PLAN", "TRUMP PRESSES ZELENSKY TO ACCEPT 28-POINT PEACE PLAN",
     "IN THE OVAL OFFICE, TRUMP TOLD ZELENSKY HE HAD 'NO CHOICE' BUT TO ACCEPT "
     "THE US PLAN: UKRAINE GIVES UP DONBAS, LIMITS ITS ARMY AND DROPS NATO "
     "HOPES, FOR WESTERN SECURITY GUARANTEES. THE US AIMS FOR A DEAL BY JANUARY."),
    ("TOP STORY 3 - MARKETS IN FREEFALL", "WALL STREET TUMBLES AS NASDAQ ERASES ALL OF 2026'S GAINS",
     "FRIDAY'S AI-LED SELL-OFF: S&P 500 DOWN 3.7% TO 6,910.39; NASDAQ DOWN "
     "5.3% TO 22,617.73 AND IN CORRECTION; DOW DOWN 949.73. WORST S&P WEEK IN "
     "18 MONTHS; WORST NASDAQ WEEK SINCE MARCH 2020."),
]

ALSO = [
    ("4", "PERU QUAKE M6.7, 129 KM DEEP",
     "DEEP QUAKE IN JUNIN SHAKES LIMA; NO DEATHS OR MAJOR DAMAGE REPORTED."),
    ("5", "COP31 OVERTIME INTO SUNDAY",
     "NO FOSSIL FUELS, NO $120BN AID; 1.5C 'WILL BE MISSED'."),
    ("6", "VERSTAPPEN WINS LAS VEGAS GP",
     "35 LEAD CHANGES; NORRIS 2ND, PIASTRI 3RD, RUSSELL CRASHES."),
    ("7", "GTA 6: $3.79BN ON DAY ONE",
     "32.5M UNITS; BIGGEST ENTERTAINMENT LAUNCH EVER."),
    ("8", "ANTHROPIC IPO SMASHES RECORDS",
     "$81.3BN RAISED AT A $1.5TN VALUE; UP 17% DAY ONE, THEN DOWN 9.1%."),
    ("9", "SAUDI STOPS HOUTHI MISSILES",
     "SAUDI ARABIA SAYS IT INTERCEPTED HOUTHI MISSILES HEADED FOR RIYADH."),
    ("10", "NVIDIA DOWN 14%, SEC PROBES",
     "LONGEST LOSING RUN SINCE 2008; $1.4TN GONE SINCE THE CEO QUIT."),
    ("11", "OCTOBER 2026: HOTTEST EVER",
     "+1.80C ABOVE PRE-INDUSTRIAL; 2026 SET TO BE THE HOTTEST YEAR."),
]

MORE = [
    "RUSSIAN MISSILES LAND IN POLAND; NATO CHIEF RUTTE VISITS WARSAW, ALLIES PLEDGE 'FULL SOLIDARITY'.",
    "TRUMP CALLS PUTIN A 'FRIEND'; ZELENSKY CALLS PUTIN A 'KILLER' AFTER THE SHENZHEN SUMMIT.",
    "TRUMP DEMANDS A 'PERMANENT' DEAL WITH IRAN: TEHRAN MUST NEVER HAVE A NUCLEAR WEAPON.",
    "RUSSIA STRIKES KRYVYI RIH: 2 KILLED, 60 WOUNDED IN A MISSILE AND DRONE ATTACK.",
    "ISRAELI STRIKE KILLS 3 IN AN AID VEHICLE IN GAZA CITY; 1,671 PALESTINIANS KILLED SINCE THE TRUCE.",
    "MYANMAR REJECTS THE ICJ GENOCIDE VERDICT (9-6), THE FIRST TIME THE COURT FOUND A STATE GUILTY.",
    "UK AND EU AGREE A POST-BREXIT RESET: FOOD, EMISSIONS TRADING AND 100,000 YOUTH EXCHANGES A YEAR.",
    "MEXICO ARRESTS 'EL CHAPO ISIDRO'; A SHOOTOUT IN SINALOA KILLS 11, INCLUDING 4 SOLDIERS.",
    "BOLSONARO IN INTENSIVE CARE WITH A BOWEL OBSTRUCTION; AWAKE AND STABLE, AGED 71.",
    "SOMALIA EXPELS THE UAE AMBASSADOR; THOUSANDS MARCH IN MOGADISHU BACKING THE ORDER.",
    "ESTONIA TO SHUT ITS LAND BORDER WITH RUSSIA FROM 1 DECEMBER AFTER A SUSPECTED GRU PLOT.",
    "TURKIYE DETAINES SOZCU TV EXECUTIVES; THE THIRD OPPOSITION CHANNEL SEIZED IN 13 MONTHS.",
    "UN DELAYS BINDING 'KILLER ROBOT' RULES UNTIL 2028; 128 STATES AGREE TO KEEP TALKING.",
    "IAEA: NORTH KOREA IS EXPANDING ITS URANIUM ENRICHMENT SITE AT YONGBYON.",
    "DENMARK RATIFIES A US SECURITY DEAL FOR GREENLAND 109-0; TWO NEW US BASES PLANNED.",
    "GOLD FALLS TO A 14-MONTH LOW OF $3,513.54 AN OUNCE AS MARKETS BET ON A FED RATE RISE.",
    "TRUMP THREATENS A 'BIG TAX' ON US FIRMS THAT BUILD AI DATA CENTRES ABROAD.",
    "US CHIP CURBS BITE: TSMC AND SAMSUNG HALT SHIPMENTS TO CHINA UNDER NEW EXPORT RULES.",
    "CURSOR, OWNED BY SPACEX, MAY DROP CHINESE-MADE AI MODELS AFTER A US HOUSE REPORT.",
    "SIGNAL BLOCKS SCREENSHOTS SO AI AGENTS CANNOT READ YOUR CHATS.",
    "THE FBI'S NATIONAL CRIME DATABASE IS REPORTED HACKED; THE FBI IS INVESTIGATING.",
    "CLAIM: A MATHEMATICIAN SAYS HE PROVED THE RIEMANN HYPOTHESIS WITH CLAUDE'S HELP. UNVERIFIED.",
    "EBOLA IN DR CONGO: MORE THAN 11,600 CASES AND 5,678 DEATHS IN THE ONGOING OUTBREAK.",
    "VIRGINIA REPORTS ITS FIRST MEASLES DEATH OF 2026, A CHILD UNDER FIVE; 290 CASES THIS YEAR.",
    "SPORTS: LEEDS STUN CHELSEA 4-1; MALEN SCORES 4 IN ROMA'S 5-1 WIN; STIRLING KOS PROCHAZKA.",
    "SPORTS: HARDEN SCORES 51 TO PASS KOBE; FLORIDA BEATS VANDERBILT 34-27; NCAA XC TITLES FOR NEW MEXICO AND ALABAMA.",
    "HUNGER GAMES: SUNRISE ON THE REAPING TAKES $56M ON DAY ONE IN 4,018 US CINEMAS.",
    "PRINCESS CATHERINE ANNOUNCES 'HEAL', A BBC FILM ON HER CANCER JOURNEY, AIRING 29 NOVEMBER.",
    "PETER FLUCK, CO-CREATOR OF SPITTING IMAGE, DIES AGED 85 IN CORNWALL.",
    "NIGERIA BOAT CAPSIZES CARRYING MOURNERS: 24 DEAD, 24 SURVIVE IN BAYELSA STATE.",
    "WOLBACHIA MOSQUITOES CUT DENGUE AND CHIKUNGUNYA INFECTIONS BY 69% IN A BRAZIL TRIAL.",
    "ENDOMETRIOSIS: LARGEST GENOMIC STUDY FINDS 58 REGIONS IN MORE THAN 1M WOMEN.",
    "FUNGAL PROTEIN GROWN FROM WASTE CO2 IS 48.5% PROTEIN, WITH 22X THE YIELD OF SOY.",
]

NUMBERS = [
    ("-5.3%", "NASDAQ, FRIDAY - IN CORRECTION"),
    ("-3.7%", "S&P 500 FRIDAY - WORST WEEK IN 18 MO"),
    ("$81.3BN", "ANTHROPIC IPO - THE BIGGEST EVER"),
    ("$3.79BN", "GTA 6 DAY-ONE SALES - 32.5M UNITS"),
    ("M6.7", "PERU QUAKE - 129 KM DEEP, NO DEATHS"),
    ("+1.80C", "OCTOBER 2026 - HOTTEST MONTH EVER"),
    ("5,678", "EBOLA DEATHS IN DR CONGO"),
    ("35", "LEAD CHANGES IN THE LAS VEGAS GP"),
]

# map markers: (label, x, y, dx, dy) - label offset from dot
MARKERS = [
    ("LAS VEGAS", 198, 569, -62, -12),
    ("MEXICO", 241, 581, -58, 8),
    ("LIMA", 302, 604, -8, 12),
    ("BRASILIA", 381, 607, -14, 12),
    ("WASHINGTON", 301, 566, -30, -14),
    ("LONDON", 512, 557, -44, -2),
    ("WARSAW", 569, 557, -44, 8),
    ("KYIV", 595, 560, 6, -2),
    ("ANTALYA", 585, 575, -46, 6),
    ("GAZA", 610, 578, 8, 6),
    ("RIYADH", 640, 577, -8, 14),
    ("DOHA", 653, 577, 8, -2),
    ("BAHRAIN", 650, 576, 0, 0),
    ("MOGADISHU", 636, 594, -30, 12),
    ("SEOUL", 859, 568, -10, -14),
]

# ------------------------------------------------------------------ art
def art_bahrain(x, y, w, h):
    fill(x, y, w, h, NAVY)
    for sx, sy in ((12, 10), (40, 26), (90, 8), (150, 20), (210, 12), (260, 28),
                   (300, 10), (70, 40), (180, 44), (240, 44)):
        px(x + sx, y + sy, WHITE)
        px(x + sx + 1, y + sy, WHITE)
    # ground / sea
    fill(x, y + h - 18, w, 18, (30, 60, 90))
    fill(x, y + h - 18, w, 2, GOLD)
    # missile arcs from the sea
    for (ax, ay, bx, by) in ((30, h - 18, 150, 18), (w - 30, h - 18, 180, 12),
                             (90, h - 18, 165, 30)):
        line(x + ax, y + ay, x + bx, y + by, (255, 200, 90))
        line(x + ax, y + ay + 1, x + bx, y + by + 1, (255, 200, 90))
    # explosion starburst
    cx, cy = x + w // 2, y + 26
    disc(cx, cy, 12, (255, 190, 60))
    disc(cx, cy, 7, (255, 240, 160))
    for dx, dy in ((-22, -8), (22, -8), (-26, 4), (26, 4), (-14, 12), (14, 12),
                   (0, -20), (-8, -18), (8, -18)):
        line(cx, cy, cx + dx, cy + dy, (255, 200, 90))
    text(x + 8, y + h - 15, "BAHRAIN - HOME OF THE US 5TH FLEET", 1, WHITE, True)
    fill(x + w - 128, y + 6, 122, 14, RED)
    text(x + w - 122, y + 8, "2 RADARS HIT", 1, WHITE, True)


def art_peace(x, y, w, h):
    fill(x, y, w, h, (232, 226, 205))
    # document
    dx, dy, dw, dh = x + 14, y + 8, 150, h - 16
    fill(dx, dy, dw, dh, WHITE)
    rect(dx, dy, dw, dh, INK, 2)
    poly([(dx + dw, dy), (dx + dw + 16, dy + 16), (dx + dw, dy + 16)],
         (200, 200, 200), INK)
    for i in range(6):
        fill(dx + 10, dy + 12 + i * 9, dw - 20 - (i * 6), 3, (120, 120, 120))
    # big 28
    text(x + 190, y + 6, "28", 4, RED, True)
    text(x + 190, y + 38, "POINT PLAN", 2, INK, True)
    # flags: US stripes + UA blue/yellow
    fx = x + 190
    fy = y + 60
    for i in range(3):
        fill(fx, fy + i * 5, 46, 3, RED if i % 2 == 0 else WHITE)
    rect(fx, fy, 46, 15, INK, 1)
    fill(fx + 52, fy, 46, 7, BLUE)
    fill(fx + 52, fy + 7, 46, 8, GOLD)
    rect(fx + 52, fy, 46, 15, INK, 1)
    text(x + 190, y + h - 11, "OVAL OFFICE", 1, INK, True)


def art_market(x, y, w, h):
    fill(x, y, w, h, (250, 244, 230))
    for gx in range(0, w, 32):
        vline(x + gx, y + 4, y + h - 4, (220, 215, 200))
    for gy in range(0, h, 22):
        hline(x + 4, x + w - 4, y + gy, (220, 215, 200))
    pts = [(10, 14), (50, 22), (90, 16), (130, 30), (170, 28), (210, 44),
           (250, 52), (290, 66), (w - 12, 82)]
    for i in range(len(pts) - 1):
        line(x + pts[i][0], y + pts[i][1], x + pts[i + 1][0],
             y + pts[i + 1][1], RED)
        line(x + pts[i][0], y + pts[i][1] + 1, x + pts[i + 1][0],
             y + pts[i + 1][1] + 1, RED)
    for (pxx, pyy) in pts:
        disc(x + pxx, y + pyy, 3, DARKRED)
    text(x + 8, y + 6, "-5.3%", 3, RED, True)
    text(x + w - 118, y + h - 18, "NASDAQ -5.3%", 1, DARKRED, True)


def icon(x, y, num, kind):
    fill(x, y, 36, 36, LIGHTBLUE)
    rect(x, y, 36, 36, INK, 1)
    text(x + 3, y + 2, num, 1, RED, True)
    if kind == "quake":
        line(x + 6, y + 16, x + 12, y + 26, INK)
        line(x + 12, y + 26, x + 18, y + 14, INK)
        line(x + 18, y + 14, x + 24, y + 28, INK)
        line(x + 24, y + 28, x + 30, y + 18, INK)
        text(x + 8, y + 30, "M6.7", 1, DARKRED, True)
    elif kind == "cop":
        disc(x + 18, y + 22, 10, GREEN)
        disc(x + 18, y + 22, 6, LAND)
        text(x + 11, y + 28, "COP31", 1, WHITE, True)
    elif kind == "f1":
        for r in range(3):
            for c in range(3):
                if (r + c) % 2 == 0:
                    fill(x + 8 + c * 6, y + 12 + r * 6, 6, 6, INK)
        text(x + 8, y + 30, "VER", 1, RED, True)
    elif kind == "gta":
        text(x + 10, y + 12, "VI", 3, RED, False)
        disc(x + 29, y + 12, 2, GOLD)
    elif kind == "ipo":
        line(x + 8, y + 30, x + 28, y + 12, GREEN)
        line(x + 28, y + 12, x + 22, y + 12, GREEN)
        line(x + 28, y + 12, x + 28, y + 18, GREEN)
        text(x + 10, y + 12, "$", 2, GREEN, True)
    elif kind == "saudi":
        poly([(x + 18, y + 10), (x + 28, y + 16), (x + 28, y + 26),
              (x + 18, y + 34), (x + 8, y + 26), (x + 8, y + 16)], BLUE, INK)
        text(x + 15, y + 19, "S", 2, WHITE, True)
    elif kind == "nvidia":
        poly([(x + 18, y + 10), (x + 28, y + 30), (x + 8, y + 30)], GREEN, INK)
        disc(x + 18, y + 22, 3, WHITE)
        text(x + 8, y + 31, "-14%", 1, DARKRED, True)
    elif kind == "heat":
        fill(x + 15, y + 12, 6, 14, RED)
        disc(x + 18, y + 28, 6, RED)
        rect(x + 15, y + 12, 6, 16, INK, 1)


# ------------------------------------------------------------------ page
def draw():
    fill(0, 0, W, H, PAPER)
    rect(8, 8, W - 16, H - 16, INK, 3)
    rect(14, 14, W - 28, H - 28, INK, 1)

    # masthead
    text(W // 2, 24, "THE DAILY WORLD", 10, INK, True, "c")
    fill(24, 100, W - 48, 3, RED)
    text(W // 2, 108, "SATURDAY 21 NOVEMBER 2026", 3, RED, True, "c")
    text(W // 2, 132, "44 STORIES - 20 COUNTRIES - 5 CONTINENTS - THE WORLD IN ONE PAGE",
         1, INK, True, "c")
    fill(24, 148, W - 48, 2, INK)

    # ---- top stories
    cols = [24, 352, 680]
    cw = 320
    arts = [art_bahrain, art_peace, art_market]
    for i, (kick, head, body) in enumerate(TOP):
        x = cols[i]
        fill(x, 158, cw, 20, RED)
        text(x + 6, 162, kick, 1, WHITE, True)
        arts[i](x, 180, cw, 88)
        rect(x, 180, cw, 88, INK, 1)
        hl = wrap(head, cw, 2)
        for j, ln in enumerate(hl[:3]):
            text(x, 274 + j * 16, ln, 2, INK, True)
        para(x, 274 + len(hl[:3]) * 16 + 4, body, cw, 1, INK, 9, max_lines=4)
    fill(24, 366, W - 48, 2, INK)

    # ---- also today: 8 items, 4 x 2
    text(24, 372, "ALSO TODAY", 2, RED, True)
    kinds = ["quake", "cop", "f1", "gta", "ipo", "saudi", "nvidia", "heat"]
    for i, (num, head, body) in enumerate(ALSO):
        col = i % 4
        row = i // 4
        x = 24 + col * 246
        y = 396 + row * 62
        icon(x, y, num, kinds[i])
        tx = x + 42
        tw = 246 - 48
        para(tx, y, head, tw, 1, INK, 9, bold=True, max_lines=2)
        hl = wrap(head, tw, 1)
        para(tx, y + len(hl[:2]) * 9 + 2, body, tw, 1, (40, 40, 40), 9,
             max_lines=2)
    fill(24, 524, W - 48, 2, INK)

    # ---- map
    text(24, 530, "WHERE IT HAPPENED", 2, RED, True)
    mx, my, mw, mh = 24, 546, 976, 96
    fill(mx, my, mw, mh, LIGHTBLUE)
    rect(mx, my, mw, mh, INK, 1)
    continents = [
        [(150, 554), (230, 548), (300, 552), (330, 566), (310, 590),
         (260, 598), (200, 594), (150, 576)],
        [(330, 546), (360, 544), (365, 556), (340, 561)],
        [(300, 606), (340, 602), (355, 620), (330, 642), (305, 630)],
        [(490, 554), (540, 550), (560, 562), (540, 576), (500, 572)],
        [(495, 578), (545, 576), (570, 596), (550, 630), (515, 634),
         (495, 606)],
        [(565, 552), (700, 546), (800, 554), (830, 571), (780, 596),
         (720, 606), (660, 601), (600, 581), (570, 566)],
        [(800, 611), (850, 606), (865, 624), (830, 638), (795, 628)],
    ]
    for c in continents:
        poly(c, LAND, LANDLINE)
    for (label, lx, ly, ox, oy) in MARKERS:
        if label == "BAHRAIN":
            disc(lx, ly, 7, RED)
            disc(lx, ly, 3, WHITE)
            ring(lx, ly, 10, RED, 2)
            line(lx + 8, ly + 4, lx + 50, ly + 14, RED)
            fill(lx + 50, ly + 8, 140, 14, RED)
            text(lx + 54, ly + 10, "BAHRAIN: IRAN STRIKES", 1, WHITE, True)
            continue
        disc(lx, ly, 4, RED)
        disc(lx, ly, 2, WHITE)
        text(lx + ox, ly + oy, label, 1, INK, True)
    fill(24, 648, W - 48, 2, INK)

    # ---- numbered list, 3 columns
    text(24, 656, "MORE FROM 21 NOVEMBER", 2, RED, True)
    per = 11
    for ci in range(3):
        x = 24 + ci * 330
        for ri in range(per):
            idx = ci * per + ri
            if idx >= len(MORE):
                break
            num = 12 + idx
            y = 682 + ri * 18
            text(x, y, str(num) + ".", 1, RED, True)
            lines = wrap(MORE[idx], 330 - 26, 1)
            for j, ln in enumerate(lines[:2]):
                text(x + 26, y + j * 9, ln, 1, INK)
    fill(24, 884, W - 48, 2, INK)

    # ---- day in numbers: 8 cells, 4 x 2
    text(24, 890, "DAY IN NUMBERS", 2, RED, True)
    for i, (val, lab) in enumerate(NUMBERS):
        col = i % 4
        row = i // 4
        x = 24 + col * 246
        y = 908 + row * 34
        fill(x, y, 240, 30, CREAM)
        rect(x, y, 240, 30, INK, 1)
        fill(x, y, 4, 30, RED)
        text(x + 10, y + 2, val, 2, RED, True)
        ll = wrap(lab, 228, 1)
        text(x + 10, y + 18, ll[0], 1, INK)

    # ---- footer
    text(W // 2, 978, "DATE CHECK: ALL 44 STORIES VERIFIED TO SATURDAY 21 NOVEMBER 2026",
         1, INK, True, "c")
    text(W // 2, 990,
         "SOURCES: AP, REUTERS, AFP, XINHUA, BBC, CNBC, NPR, FINANCIAL TIMES, NIH, "
         "BERKELEY EARTH, IAEA, CPJ, USGS, NCAA, NBA, F1",
         1, GREY, False, "c")
    text(W // 2, 1002, "THE DAILY WORLD - ONE PAGE, ONE DAY - NOT AFFILIATED WITH MAKE.FUN",
         1, GREY, False, "c")


def chunk(typ, data):
    c = struct.pack(">I", len(data)) + typ + data
    return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)


def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw.extend(buf[y * W * 3:(y + 1) * W * 3])
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out, exist_ok=True)
    draw()
    n = write_png(os.path.join(out, "entry.png"))
    print("wrote entry.png", n, "bytes")


if __name__ == "__main__":
    main()
