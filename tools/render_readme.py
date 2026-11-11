#!/usr/bin/env python3
"""Write README.md for the current time of day on the island (WIB, UTC+7).

    python3 tools/render_readme.py          → day 06:00–17:59 WIB, night otherwise
    python3 tools/render_readme.py night    → force a mode

Day and night swap the banner, the 3D contribution island and the streak card together,
so the whole profile looks like one scene. The workflow runs this at 06:00 and 18:00 WIB.
"""
import datetime, os, sys

ROOT = os.path.join(os.path.dirname(__file__), '..')
USER = 'woisway'

STREAK = {
    'day': 'background=fffaf0&border=1d1b26&stroke=e8e0cb&ring=f2b33d&fire=e0533d&currStreakNum=1d1b26'
           '&sideNums=3f8f4e&currStreakLabel=3f8f4e&sideLabels=57525f&dates=8a8494&border_radius=12',
    'night': 'background=232131&border=5b5674&stroke=3a3760&ring=f2b33d&fire=e0533d&currStreakNum=ece6d6'
             '&sideNums=4fae5f&currStreakLabel=4fae5f&sideLabels=aaa4b8&dates=726c84&border_radius=12',
}


def mode_now():
    hour = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=7)).hour
    return 'day' if 6 <= hour < 18 else 'night'


def render(mode):
    banner = 'assets/banner-light.svg' if mode == 'day' else 'assets/banner-dark.svg'
    island = f'profile-3d-contrib/island-{mode}.svg'
    sky = 'daytime' if mode == 'day' else 'night-time'
    parts = [
        f'<img alt="A small floating pixel island at {sky}, with a dialog box that reads: Hello, world! Welcome to the island. Press start." src="{banner}" width="100%">',
        '',
    ]
    if os.path.exists(os.path.join(ROOT, island)):          # appears after the workflow's first run
        parts += [f'<img alt="Contributions drawn as a little voxel town" src="{island}" width="100%">', '']
    parts += [
        '<p align="center">',
        f'  <img alt="Contribution streak" src="https://streak-stats.demolab.com/?user={USER}&{STREAK[mode]}">',
        '</p>',
        '',
    ]
    return '\n'.join(parts)


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else mode_now()
    with open(os.path.join(ROOT, 'README.md'), 'w') as f:
        f.write(render(mode))
    print('README.md →', mode)
