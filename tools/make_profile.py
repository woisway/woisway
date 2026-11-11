#!/usr/bin/env python3
"""The whole profile in one banner: the island *is* the contribution garden.

    python3 tools/make_profile.py           → assets/island-light.svg, assets/island-dark.svg

Left: the dialog card, as on the site. On the island: a wooden sign with the year's contributions and best day.
Right: a round voxel island with one tile per day of the last year, oldest at the back and today at
the front (gold flag); busier days grow bigger plants. Sky, sun/moon, clouds and a balloon as on the site.
The workflow reruns this daily, so the garden keeps growing.
"""
import math, os, random, sys

sys.path.insert(0, os.path.dirname(__file__))
from make_banner import THEMES, pixel_text, text_width, shade, pixel_blob
from make_garden import fetch, cube, plant

USER = os.environ.get('GH_USER', 'woisway')
OUT = os.path.join(os.path.dirname(__file__), '..', 'assets')
W, H = 1200, 420


def island(t, days, cx, cy, s):
    rnd = random.Random(11)
    R = math.sqrt(len(days) / math.pi) + 0.35
    cells = [(x, z) for z in range(-13, 14) for x in range(-13, 14) if math.hypot(x, z) <= R]
    cells.sort(key=lambda c: (c[0] + c[1], c[0] - c[1]))       # back → front
    while len(cells) > len(days):
        cells.pop(0)
    plotted = dict(zip(cells, days[-len(cells):]))
    P = lambda x, y, z: (cx + (x - z) * s, cy + (x + z) * s / 2 - y * s)
    vox = {}
    for (x, z) in cells:
        r = math.hypot(x, z)
        vox[(x, 0, z)] = rnd.choice(t['grass'])
        for y in range(1, 2 + int((R - r) * 0.55)):
            vox[(x, -y, z)] = t['dirt'][y % 2] if y < 3 else t['rock'][y % 2]
    polys = []
    for (x, y, z), col in vox.items():
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
    cube(polys, P, today[0], 1, today[1], 0.12, 2.4, '#d8dbe6')
    polys.sort(key=lambda p: p[0])
    fx, fy = P(today[0] + 0.5, 3.4, today[1] + 0.5)
    flag = f'<path fill="{t["gold"]}" d="M{fx:.1f} {fy:.1f}h14l-4 5 4 5h-14z"/>'
    return ''.join(p[1] for p in polys) + flag


def scene(name, days):
    t = THEMES[name]
    rnd = random.Random(3)
    days = sorted(days, key=lambda d: d['date'])
    total = sum(d['count'] for d in days)
    best = max((d['count'] for d in days), default=0)

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" shape-rendering="crispEdges">']
    out.append('<style>'
               '@keyframes drift{from{transform:translateX(-260px)}to{transform:translateX(1460px)}}.cl{animation:drift linear infinite}'
               '@keyframes tw{0%,100%{opacity:.9}50%{opacity:.15}}.st{animation:tw 3s ease-in-out infinite}'
               '@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}.bob{animation:bob 4s ease-in-out infinite}'
               '@keyframes isl{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}.isl{animation:isl 6s ease-in-out infinite}'
               '@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}.blink{animation:blink 1.2s steps(1) infinite}'
               '@media (prefers-reduced-motion:reduce){.cl,.st,.bob,.isl,.blink{animation:none}}'
               '</style>')
    sky = t['sky']
    out.append('<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
               f'<stop offset="0" stop-color="{sky[0]}"/><stop offset=".55" stop-color="{sky[1]}"/><stop offset="1" stop-color="{sky[2]}"/>'
               '</linearGradient></defs>')
    out.append(f'<rect width="{W}" height="{H}" rx="18" fill="url(#sky)"/>')
    if t['night']:
        for i in range(80):
            x, y = rnd.randrange(10, W - 10), rnd.randrange(8, 240)
            out.append(f'<rect class="st" style="animation-delay:-{rnd.uniform(0, 3):.2f}s" x="{x}" y="{y}" width="{rnd.choice([2, 2, 3])}" height="2" fill="#fff6d8"/>')
        moon = ['..####..', '.######.', '##.#####', '########', '#####.##', '########', '.######.', '..####..']
        out.append('<circle cx="1124" cy="58" r="42" fill="#cfd8ff" opacity=".12"/>' + pixel_blob(1100, 34, 6, moon, '#f2f1ea'))
    else:
        sun = ['..####..', '.######.', '########', '########', '########', '########', '.######.', '..####..']
        out.append('<circle cx="1124" cy="58" r="46" fill="#fff1b8" opacity=".35"/>' + pixel_blob(1100, 34, 6, sun, '#ffd84a'))
    cloud = ['...####.....', '.########...', '############', '.##########.']
    for i in range(6):
        y = 26 + i * 40 + rnd.randrange(-8, 8)
        dur = rnd.uniform(55, 95)
        out.append(f'<g class="cl" style="animation-duration:{dur:.0f}s;animation-delay:-{rnd.uniform(0, dur):.0f}s" opacity="{t["cloudOp"]}">'
                   + pixel_blob(0, y, rnd.choice([5, 6, 7]), cloud, t['cloud']) + '</g>')

    # the island = the garden
    out.append('<g class="isl">' + island(t, days, 905, 206, 12) + '</g>')
    # balloon drifting between the card and the island
    balloon = ['..####..', '.#####@#', '###@@###', '##@@@@##', '###@@###', '.######.', '..#..#..', '...##...']
    b = []
    for j, row in enumerate(balloon):
        for i, ch in enumerate(row):
            if ch == '.':
                continue
            col = '#7a4b26' if j >= 6 else {'#': '#e0533d', '@': '#f2b33d'}[ch]
            b.append(f'<rect x="{652 + i * 6}" y="{40 + j * 6}" width="6" height="6" fill="{col}"/>')
    out.append('<g class="bob">' + ''.join(b) + '</g>')

    # wooden sign planted at the front-left of the island: the year's numbers belong to the garden
    wood, woodDark, ink = ('#a0703f', '#5a3b26', '#fff6d8') if not t['night'] else ('#6e4c2c', '#3a2618', '#f2e6c8')
    num = str(total)
    tw = text_width(num, 5) + 14 + max(text_width('CONTRIBUTIONS', 2), text_width(f'BEST DAY {best}', 2))
    bw, bh = tw + 32, 64
    sx, sy = 772 - bw // 2, 150
    out.append(f'<rect x="{sx + bw // 2 - 6}" y="{sy + bh}" width="12" height="34" fill="{woodDark}"/>')       # post
    out.append(f'<rect x="{sx + 5}" y="{sy + 5}" width="{bw}" height="{bh}" rx="6" fill="{t["shadow"]}" opacity=".35"/>')
    out.append(f'<rect x="{sx}" y="{sy}" width="{bw}" height="{bh}" rx="6" fill="{wood}" stroke="{woodDark}" stroke-width="4"/>')
    for k in (1, 2):                                                                                       # plank seams
        out.append(f'<rect x="{sx + 4}" y="{sy + k * bh // 3}" width="{bw - 8}" height="2" fill="{woodDark}" opacity=".45"/>')
    for nx, ny in ((sx + 8, sy + 8), (sx + bw - 12, sy + 8), (sx + 8, sy + bh - 12), (sx + bw - 12, sy + bh - 12)):
        out.append(f'<rect x="{nx}" y="{ny}" width="4" height="4" fill="{woodDark}"/>')                        # nails
    out.append(pixel_text(num, sx + 16, sy + 15, 5, ink))
    out.append(pixel_text('CONTRIBUTIONS', sx + 30 + text_width(num, 5), sy + 17, 2, ink))
    out.append(pixel_text(f'BEST DAY {best}', sx + 30 + text_width(num, 5), sy + 35, 2, ink))

    # dialog card, like the site's hero: just hello
    x0, y0, w, h = 56, 118, 560, 172
    out.append(f'<rect x="{x0 + 7}" y="{y0 + 7}" width="{w}" height="{h}" rx="14" fill="{t["shadow"]}"/>')
    out.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="14" fill="{t["panel"]}" stroke="{t["line"]}" stroke-width="4"/>')
    badge = 'WOI · SOFTWARE · DATA · CLOUD'
    bw2 = text_width(badge, 2) + 28
    out.append(f'<rect x="{x0 + 18}" y="{y0 - 18}" width="{bw2}" height="34" rx="9" fill="{t["gold"]}" stroke="{t["line"]}" stroke-width="3"/>')
    out.append(pixel_text(badge, x0 + 32, y0 - 8, 2, '#1d1b26'))
    out.append(pixel_text('HELLO, WORLD!', x0 + 34, y0 + 46, 6, t['text']))
    out.append(pixel_text('WELCOME TO THE ISLAND.', x0 + 36, y0 + 114, 3, t['primary']))
    out.append('</svg>')
    return ''.join(out)


if __name__ == '__main__':
    days = fetch(USER)
    if not days:
        sys.exit('no contribution data found')
    os.makedirs(OUT, exist_ok=True)
    import hashlib
    digest = hashlib.sha1()
    for n in THEMES:
        p = os.path.join(OUT, f'island-{n}.svg')
        svg = scene(n, days)
        digest.update(svg.encode())
        with open(p, 'w') as f:
            f.write(svg)
        print(p, os.path.getsize(p), 'bytes')
    # the README points at the images with a version tag, so a redrawn banner is never stuck in a browser cache
    v = digest.hexdigest()[:8]
    with open(os.path.join(OUT, '..', 'README.md'), 'w') as f:
        f.write(f'''<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/island-dark.svg?v={v}">
  <img alt="A floating pixel island whose garden is a year of contributions, next to a dialog box that says hello." src="assets/island-light.svg?v={v}" width="100%">
</picture>
''')
    print('README.md → v', v)
