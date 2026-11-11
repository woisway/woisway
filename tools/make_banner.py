#!/usr/bin/env python3
"""Generate the profile banner: a floating voxel island in the portfolio's pixel style.

    python3 tools/make_banner.py        → assets/banner-light.svg, assets/banner-dark.svg

Everything is drawn with plain SVG shapes (GitHub won't load web fonts inside README images),
including the 5×7 pixel lettering. Clouds drift, stars twinkle, the balloon bobs (CSS in the SVG).
"""
import math, random, os

OUT = os.path.join(os.path.dirname(__file__), '..', 'assets')
W, H = 1200, 340

THEMES = {
    'light': dict(sky=('#86c9ec', '#c9e6ef', '#f3eddf'), panel='#fffaf0', line='#1d1b26', shadow='#1d1b26',
                  text='#1d1b26', text2='#57525f', gold='#f2b33d', primary='#3f8f4e', cloud='#ffffff', cloudOp=0.95,
                  grass=('#5fb14a', '#4fa33e', '#6cbd55'), dirt=('#8a5a36', '#7a4e2f'), rock=('#8b91a6', '#767c90'),
                  win='#9fd3e6', night=False),
    'dark': dict(sky=('#0b0a24', '#1b1840', '#14131d'), panel='#232131', line='#5b5674', shadow='#06050b',
                 text='#ece6d6', text2='#aaa4b8', gold='#f2b33d', primary='#4fae5f', cloud='#3a3760', cloudOp=0.75,
                 grass=('#2f6b3a', '#285e33', '#357541'), dirt=('#5a3b26', '#4c3221'), rock=('#5a5f72', '#4b4f60'),
                 win='#e8c46e', night=True),
}

# ── 5×7 pixel font (only the glyphs used) ─────────────────────────────
FONT = {
    'A': ['01110', '10001', '10001', '11111', '10001', '10001', '10001'],
    'C': ['01110', '10001', '10000', '10000', '10000', '10001', '01110'],
    'D': ['11110', '10001', '10001', '10001', '10001', '10001', '11110'],
    'E': ['11111', '10000', '10000', '11110', '10000', '10000', '11111'],
    'F': ['11111', '10000', '10000', '11110', '10000', '10000', '10000'],
    'H': ['10001', '10001', '10001', '11111', '10001', '10001', '10001'],
    'I': ['01110', '00100', '00100', '00100', '00100', '00100', '01110'],
    'L': ['10000', '10000', '10000', '10000', '10000', '10000', '11111'],
    'M': ['10001', '11011', '10101', '10101', '10001', '10001', '10001'],
    'N': ['10001', '11001', '10101', '10011', '10001', '10001', '10001'],
    'O': ['01110', '10001', '10001', '10001', '10001', '10001', '01110'],
    'P': ['11110', '10001', '10001', '11110', '10000', '10000', '10000'],
    'R': ['11110', '10001', '10001', '11110', '10100', '10010', '10001'],
    'S': ['01111', '10000', '10000', '01110', '00001', '00001', '11110'],
    'T': ['11111', '00100', '00100', '00100', '00100', '00100', '00100'],
    'U': ['10001', '10001', '10001', '10001', '10001', '10001', '01110'],
    'W': ['10001', '10001', '10001', '10101', '10101', '10101', '01010'],
    'Y': ['10001', '10001', '01010', '00100', '00100', '00100', '00100'],
    '0': ['01110', '10001', '10011', '10101', '11001', '10001', '01110'],
    '1': ['00100', '01100', '00100', '00100', '00100', '00100', '01110'],
    '2': ['01110', '10001', '00001', '00010', '00100', '01000', '11111'],
    '3': ['11110', '00001', '00001', '01110', '00001', '00001', '11110'],
    '4': ['00010', '00110', '01010', '10010', '11111', '00010', '00010'],
    '5': ['11111', '10000', '11110', '00001', '00001', '10001', '01110'],
    '6': ['00110', '01000', '10000', '11110', '10001', '10001', '01110'],
    '7': ['11111', '00001', '00010', '00100', '01000', '01000', '01000'],
    '8': ['01110', '10001', '10001', '01110', '10001', '10001', '01110'],
    '9': ['01110', '10001', '10001', '01111', '00001', '00010', '01100'],
    'B': ['11110', '10001', '10001', '11110', '10001', '10001', '11110'],
    'G': ['01110', '10001', '10000', '10111', '10001', '10001', '01111'],
    'K': ['10001', '10010', '10100', '11000', '10100', '10010', '10001'],
    'V': ['10001', '10001', '10001', '10001', '10001', '01010', '00100'],
    '-': ['00000', '00000', '00000', '11111', '00000', '00000', '00000'],
    ',': ['00000', '00000', '00000', '00000', '00000', '00100', '01000'],
    '!': ['00100', '00100', '00100', '00100', '00100', '00000', '00100'],
    '.': ['00000', '00000', '00000', '00000', '00000', '00000', '00100'],
    '>': ['10000', '11000', '11100', '11110', '11100', '11000', '10000'],
    '·': ['00000', '00000', '00000', '00100', '00000', '00000', '00000'],
    ' ': ['000', '000', '000', '000', '000', '000', '000'],
}


def text_width(s, px):
    return sum((len(FONT[c][0]) + 1) * px for c in s) - px


def pixel_text(s, x, y, px, fill, cls=''):
    """Pixel lettering as one <path> of px×px squares."""
    d = []
    for c in s:
        rows = FONT[c]
        for j, row in enumerate(rows):
            for i, bit in enumerate(row):
                if bit == '1':
                    d.append(f'M{x + i * px:.0f} {y + j * px:.0f}h{px}v{px}h-{px}z')
        x += (len(rows[0]) + 1) * px
    c = f' class="{cls}"' if cls else ''
    return f'<path{c} fill="{fill}" d="{"".join(d)}"/>'


def shade(hex_, k):
    r, g, b = (int(hex_[i:i + 2], 16) for i in (1, 3, 5))
    return '#%02x%02x%02x' % (int(r * k), int(g * k), int(b * k))


# ── voxel island ──────────────────────────────────────────────────────
def build_island(t, seed=7):
    rnd = random.Random(seed)
    vox = {}                                   # (x, y, z) -> colour
    R = 8.6
    for x in range(-9, 10):
        for z in range(-9, 10):
            r = math.hypot(x, z) + rnd.uniform(-0.5, 0.5)
            if r > R:
                continue
            depth = 1 + int((R - r) * 0.55)    # thicker in the middle: a floating island tapers underneath
            vox[(x, 0, z)] = rnd.choice(t['grass'])
            for y in range(1, depth + 1):
                vox[(x, -y, z)] = t['dirt'][y % 2] if y < 3 else t['rock'][y % 2]
    # little lake, a path, a mountain at the back
    for x, z in [(-4, 2), (-5, 2), (-4, 3), (-5, 3), (-3, 3), (-4, 4)]:
        vox[(x, 0, z)] = '#3b8ed8' if not t['night'] else '#2a5c9a'
    for k in range(-6, 7):
        if (k, 0, 0) in vox:
            vox[(k, 0, 0)] = '#d9c79a' if not t['night'] else '#6b6250'
    for x in range(-6, -1):
        for z in range(-7, -3):
            hgt = 4 - abs(x + 4) - abs(z + 5)
            for y in range(1, hgt + 1):
                vox[(x, y, z)] = ('#f4f6fb' if y == hgt and hgt >= 3 else rnd.choice(t['rock']))

    def house(x0, z0, wall, roof, h=2):
        for x in range(x0, x0 + 2):
            for z in range(z0, z0 + 2):
                for y in range(1, h + 1):
                    vox[(x, y, z)] = wall
                vox[(x, h + 1, z)] = roof
        vox[(x0 + 1, 1, z0 + 1)] = t['win']   # a lit window on the visible corner

    house(1, -5, '#eeeae0', '#e0533d')
    house(4, -2, '#cfd3de', '#3b6fd8')
    house(-1, 3, '#f4efe3', '#1d9e75', 1)
    house(3, 3, '#e8e2d4', '#8a5cd8')
    for x, z in [(6, 1), (-7, -1), (0, 6), (-2, -1), (6, -5), (-6, 5)]:
        if (x, 0, z) not in vox:
            continue
        vox[(x, 1, z)] = '#7a4b26'
        vox[(x, 2, z)] = '#7a4b26'
        leaf = rnd.choice(['#2f7d4a', '#3a8f52', '#f4a7c4', '#e6c14a'])
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                if abs(dx) + abs(dz) < 2:
                    vox[(x + dx, 3, z + dz)] = leaf
        vox[(x, 4, z)] = leaf
    return vox


def draw_island(vox, cx, cy, s):
    P = lambda x, y, z: (cx + (x - z) * s, cy + (x + z) * s / 2 - y * s)
    polys = []
    for (x, y, z) in sorted(vox, key=lambda v: (v[0] + v[2], v[1])):
        col = vox[(x, y, z)]
        faces = []
        if (x, y + 1, z) not in vox:
            faces.append(([P(x, y + 1, z), P(x + 1, y + 1, z), P(x + 1, y + 1, z + 1), P(x, y + 1, z + 1)], col))
        if (x + 1, y, z) not in vox:
            faces.append(([P(x + 1, y, z), P(x + 1, y + 1, z), P(x + 1, y + 1, z + 1), P(x + 1, y, z + 1)], shade(col, 0.78)))
        if (x, y, z + 1) not in vox:
            faces.append(([P(x, y, z + 1), P(x + 1, y, z + 1), P(x + 1, y + 1, z + 1), P(x, y + 1, z + 1)], shade(col, 0.62)))
        for pts, c in faces:
            polys.append(f'<path fill="{c}" d="M{"L".join(f"{a:.1f} {b:.1f}" for a, b in pts)}z"/>')
    return ''.join(polys)


def pixel_blob(cx, cy, px, rows, fill, cls='', extra=''):
    d = []
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch != '.':
                d.append(f'M{cx + i * px} {cy + j * px}h{px}v{px}h-{px}z')
    c = f' class="{cls}"' if cls else ''
    return f'<path{c}{extra} fill="{fill}" d="{"".join(d)}"/>'


def banner(name):
    t = THEMES[name]
    rnd = random.Random(3)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" shape-rendering="crispEdges">']
    out.append('<style>'
               '@keyframes drift{from{transform:translateX(-260px)}to{transform:translateX(1460px)}}'
               '.cl{animation:drift linear infinite}'
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
    # stars or sun
    if t['night']:
        for i in range(70):
            x, y = rnd.randrange(10, W - 10), rnd.randrange(8, 200)
            sz = rnd.choice([2, 2, 3])
            out.append(f'<rect class="st" style="animation-delay:-{rnd.uniform(0, 3):.2f}s" x="{x}" y="{y}" width="{sz}" height="{sz}" fill="#fff6d8"/>')
        moon = ['..####..', '.######.', '##.#####', '########', '#####.##', '########', '.######.', '..####..']
        out.append(f'<circle cx="{1080 + 24}" cy="{58 + 24}" r="42" fill="#cfd8ff" opacity=".12"/>')
        out.append(pixel_blob(1080, 58, 6, moon, '#f2f1ea'))
    else:
        sun = ['..####..', '.######.', '########', '########', '########', '########', '.######.', '..####..']
        out.append(f'<circle cx="{1080 + 24}" cy="{58 + 24}" r="46" fill="#fff1b8" opacity=".35"/>')
        out.append(pixel_blob(1080, 58, 6, sun, '#ffd84a'))
    # clouds, drifting at different heights and speeds
    cloud = ['...####.....', '.########...', '############', '.##########.']
    for i in range(6):
        y = 30 + i * 34 + rnd.randrange(-8, 8)
        px = rnd.choice([5, 6, 7])
        dur = rnd.uniform(55, 95)
        out.append(f'<g class="cl" style="animation-duration:{dur:.0f}s;animation-delay:-{rnd.uniform(0, dur):.0f}s" opacity="{t["cloudOp"]}">'
                   + pixel_blob(0, y, px, cloud, t['cloud']) + '</g>')
    # the island
    out.append('<g class="isl">' + draw_island(build_island(t), 880, 160, 11) + '</g>')
    # hot-air balloon bobbing beside it
    balloon = ['..####..', '.#####@#', '###@@###', '##@@@@##', '###@@###', '.######.', '..#..#..', '...##...']
    b = []
    for j, row in enumerate(balloon):
        for i, ch in enumerate(row):
            if ch == '.':
                continue
            col = {'#': '#e0533d', '@': '#f2b33d'}[ch]
            if j >= 6:
                col = '#7a4b26'
            b.append(f'<rect x="{1080 + i * 6}" y="{150 + j * 6}" width="6" height="6" fill="{col}"/>')
    out.append('<g class="bob">' + ''.join(b) + '</g>')
    # dialog card, like the site's hero card
    x0, y0, w, h = 56, 78, 560, 200
    out.append(f'<rect x="{x0 + 7}" y="{y0 + 7}" width="{w}" height="{h}" rx="14" fill="{t["shadow"]}"/>')
    out.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="14" fill="{t["panel"]}" stroke="{t["line"]}" stroke-width="4"/>')
    badge = 'WOI · SOFTWARE · DATA · CLOUD'
    bw = text_width(badge, 2) + 28
    out.append(f'<rect x="{x0 + 18}" y="{y0 - 18}" width="{bw}" height="34" rx="9" fill="{t["gold"]}" stroke="{t["line"]}" stroke-width="3"/>')
    out.append(pixel_text(badge, x0 + 32, y0 - 8, 2, '#1d1b26'))
    out.append(pixel_text('HELLO, WORLD!', x0 + 34, y0 + 46, 6, t['text']))
    out.append(pixel_text('WELCOME TO THE ISLAND.', x0 + 36, y0 + 112, 3, t['primary']))
    out.append(pixel_text('> PRESS START', x0 + 36, y0 + 152, 3, t['text2'], 'blink'))
    out.append('</svg>')
    return ''.join(out)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for n in THEMES:
        p = os.path.join(OUT, f'banner-{n}.svg')
        with open(p, 'w') as f:
            f.write(banner(n))
        print(p, os.path.getsize(p), 'bytes')
