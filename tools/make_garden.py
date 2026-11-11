#!/usr/bin/env python3
"""Contribution garden: a year of GitHub contributions, planted on a little round voxel island.

    python3 tools/make_garden.py            → assets/garden-light.svg, assets/garden-dark.svg

Each day is one tile (oldest at the back, today at the front). The busier the day, the more grew:
bare grass → sprout → bush → tree → tree in blossom. Today's tile carries a small gold flag.
Data comes from the public contribution calendar (github.com/users/<user>/contributions), no token needed.
"""
import math, os, re, sys, random, urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from make_banner import THEMES, pixel_text, text_width, shade, pixel_blob   # same palette and lettering as the banner

USER = os.environ.get('GH_USER', 'woisway')
OUT = os.path.join(os.path.dirname(__file__), '..', 'assets')
W, H = 1200, 340


def fetch(user):
    req = urllib.request.Request(f'https://github.com/users/{user}/contributions', headers={'User-Agent': 'profile-garden'})
    html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
    counts = {}
    for m in re.finditer(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        txt = m.group(2)
        n = 0 if txt.startswith('No ') else int(re.match(r'([\d,]+)', txt).group(1).replace(',', '')) if re.match(r'[\d,]+', txt) else 0
        counts[m.group(1)] = n
    days = []
    for m in re.finditer(r'<td[^>]*data-date="([\d-]+)"[^>]*id="(contribution-day-component-(\d)-(\d+))"[^>]*data-level="(\d)"', html):
        date, cid, wd, wk, lvl = m.groups()
        days.append(dict(date=date, weekday=int(wd), week=int(wk), level=int(lvl), count=counts.get(cid, 0)))
    return days


def cube(polys, P, x, y, z, w, h, col, d=None):
    """An axis-aligned box w wide/deep (centred in its tile at x+.5, z+.5), h tall, sitting on y."""
    d = d or w
    x0, x1, z0, z1 = x + 0.5 - w / 2, x + 0.5 + w / 2, z + 0.5 - d / 2, z + 0.5 + d / 2
    y0, y1 = y, y + h
    key = (x + z + 1, y)
    faces = [
        ([P(x0, y1, z0), P(x1, y1, z0), P(x1, y1, z1), P(x0, y1, z1)], col),
        ([P(x1, y0, z0), P(x1, y1, z0), P(x1, y1, z1), P(x1, y0, z1)], shade(col, 0.78)),
        ([P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)], shade(col, 0.62)),
    ]
    polys.append((key, ''.join(f'<path fill="{c}" d="M{"L".join(f"{a:.1f} {b:.1f}" for a, b in pts)}z"/>' for pts, c in faces)))


def plant(polys, P, x, z, level, t, rnd):
    leaf = rnd.choice(t['grass'][:2])
    if level == 1:
        cube(polys, P, x, 1, z, 0.22, 0.35, '#8fd16a' if not t['night'] else '#4f9a45')
    elif level == 2:
        cube(polys, P, x, 1, z, 0.55, 0.5, shade(leaf, 0.85))
    elif level == 3:
        cube(polys, P, x, 1, z, 0.2, 0.55, '#7a4b26')
        cube(polys, P, x, 1.55, z, 0.8, 0.75, '#2f7d4a' if not t['night'] else '#25603a')
    elif level >= 4:
        cube(polys, P, x, 1, z, 0.2, 0.7, '#7a4b26')
        cube(polys, P, x, 1.7, z, 0.9, 0.7, '#f4a7c4' if not t['night'] else '#c77a9a')
        cube(polys, P, x, 2.4, z, 0.5, 0.35, '#f8c4d8' if not t['night'] else '#d98fae')


def garden(name, days):
    t = THEMES[name]
    rnd = random.Random(11)
    days = sorted(days, key=lambda d: d['date'])
    total = sum(d['count'] for d in days)
    best = max((d['count'] for d in days), default=0)

    # a round island with one tile per day: oldest at the back, today at the front
    R = math.sqrt(len(days) / math.pi) + 0.35
    cells = [(x, z) for z in range(-12, 13) for x in range(-12, 13) if math.hypot(x, z) <= R]
    cells.sort(key=lambda c: (c[0] + c[1], c[0] - c[1]))          # back → front in screen space
    while len(cells) > len(days):
        cells.pop(0)
    plotted = dict(zip(cells, days[-len(cells):]))

    s = 12
    cx, cy = 345, 168
    P = lambda x, y, z: (cx + (x - z) * s, cy + (x + z) * s / 2 - y * s)
    vox = {}
    for (x, z) in cells:
        r = math.hypot(x, z)
        vox[(x, 0, z)] = rnd.choice(t['grass'])
        for y in range(1, 2 + int((R - r) * 0.55)):
            vox[(x, -y, z)] = t['dirt'][y % 2] if y < 3 else t['rock'][y % 2]
    polys = []
    for (x, y, z), col in vox.items():                      # terrain: only faces that can be seen
        faces = []
        if (x, y + 1, z) not in vox:
            faces.append(([P(x, y + 1, z), P(x + 1, y + 1, z), P(x + 1, y + 1, z + 1), P(x, y + 1, z + 1)], col))
        if (x + 1, y, z) not in vox:
            faces.append(([P(x + 1, y, z), P(x + 1, y + 1, z), P(x + 1, y + 1, z + 1), P(x + 1, y, z + 1)], shade(col, 0.78)))
        if (x, y, z + 1) not in vox:
            faces.append(([P(x, y, z + 1), P(x + 1, y, z + 1), P(x + 1, y + 1, z + 1), P(x, y + 1, z + 1)], shade(col, 0.62)))
        if faces:
            polys.append(((x + z, y), ''.join(f'<path fill="{c}" d="M{"L".join(f"{a:.1f} {b:.1f}" for a, b in pts)}z"/>' for pts, c in faces)))
    for (x, z), d in plotted.items():
        plant(polys, P, x, z, d['level'], t, rnd)
    today = cells[-1]
    cube(polys, P, today[0], 1, today[1], 0.12, 2.2, '#d8dbe6')
    polys.sort(key=lambda p: p[0])

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" shape-rendering="crispEdges">']
    out.append('<style>@keyframes drift{from{transform:translateX(-200px)}to{transform:translateX(1400px)}}.cl{animation:drift linear infinite}'
               '@keyframes isl{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}.isl{animation:isl 6s ease-in-out infinite}'
               '@keyframes flap{0%,100%{transform:scaleX(1)}50%{transform:scaleX(.8)}}'
               '@media (prefers-reduced-motion:reduce){.cl,.isl{animation:none}}</style>')
    sky = t['sky']
    out.append('<defs><linearGradient id="gsky" x1="0" y1="0" x2="0" y2="1">'
               f'<stop offset="0" stop-color="{sky[0]}"/><stop offset=".6" stop-color="{sky[1]}"/><stop offset="1" stop-color="{sky[2]}"/></linearGradient></defs>')
    out.append(f'<rect width="{W}" height="{H}" rx="18" fill="url(#gsky)"/>')
    if t['night']:
        for i in range(45):
            out.append(f'<rect x="{rnd.randrange(10, W - 10)}" y="{rnd.randrange(8, 170)}" width="2" height="2" fill="#fff6d8" opacity="{rnd.uniform(.3, .9):.2f}"/>')
    cloud = ['..####....', '.#######..', '##########']
    for i in range(3):
        dur = rnd.uniform(60, 90)
        out.append(f'<g class="cl" style="animation-duration:{dur:.0f}s;animation-delay:-{rnd.uniform(0, dur):.0f}s" opacity="{t["cloudOp"]}">'
                   + pixel_blob(0, 26 + i * 52, 5, cloud, t['cloud']) + '</g>')
    fpx, fpy = P(today[0] + 0.5, 3.2, today[1] + 0.5)
    flag = f'<path fill="{t["gold"]}" d="M{fpx:.1f} {fpy:.1f}h13l-4 5 4 5h-13z"/>'
    out.append('<g class="isl">' + ''.join(p[1] for p in polys) + flag + '</g>')

    # HUD card, like the site's panels
    x0, y0, w, h = 690, 66, 450, 200
    out.append(f'<rect x="{x0 + 7}" y="{y0 + 7}" width="{w}" height="{h}" rx="14" fill="{t["shadow"]}"/>')
    out.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="14" fill="{t["panel"]}" stroke="{t["line"]}" stroke-width="4"/>')
    label = 'CONTRIBUTION GARDEN'
    bw = text_width(label, 2) + 28
    out.append(f'<rect x="{x0 + 18}" y="{y0 - 18}" width="{bw}" height="34" rx="9" fill="{t["gold"]}" stroke="{t["line"]}" stroke-width="3"/>')
    out.append(pixel_text(label, x0 + 32, y0 - 8, 2, '#1d1b26'))
    num = str(total)
    out.append(pixel_text(num, x0 + 32, y0 + 36, 7, t['text']))
    out.append(pixel_text('CONTRIBUTIONS', x0 + 44 + text_width(num, 7), y0 + 54, 3, t['primary']))
    out.append(pixel_text('IN THE LAST YEAR', x0 + 32, y0 + 102, 3, t['text2']))
    out.append(pixel_text(f'BEST DAY {best}', x0 + 32, y0 + 130, 3, t['text2']))
    # legend: less → more, the same plants in miniature
    ly = y0 + 172
    out.append(pixel_text('LESS', x0 + 32, ly - 4, 2, t['text2']))
    for i in range(5):
        lp = []
        bx = x0 + 96 + i * 30
        LP = lambda x, y, z, bx=bx: (bx + (x - z) * 8, ly - 6 + (x + z) * 4 - y * 8)
        cube(lp, LP, 0, 0, 0, 1, 0.5, t['grass'][0])
        plant(lp, LP, 0, 0, i, t, random.Random(i))
        lp.sort(key=lambda p: p[0])
        out.append(''.join(p[1] for p in lp))
    out.append(pixel_text('MORE', x0 + 96 + 5 * 30 + 4, ly - 4, 2, t['text2']))
    out.append('</svg>')
    return ''.join(out)


if __name__ == '__main__':
    days = fetch(USER)
    if not days:
        sys.exit('no contribution data found')
    os.makedirs(OUT, exist_ok=True)
    for n in THEMES:
        p = os.path.join(OUT, f'garden-{n}.svg')
        with open(p, 'w') as f:
            f.write(garden(n, days))
        print(p, os.path.getsize(p), 'bytes')
