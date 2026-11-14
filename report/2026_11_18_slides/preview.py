"""Local preview: stack all slides (deck order) into one HTML page, then screenshot each slide with Firefox.

python3 preview.py [id ...]   -> screenshots ~/snap/firefox/common/shot/slide_<n>.png (all slides, or only the ids given)
Browser default margins are reset so the layout matches the Slides runtime (which has no margins).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHOT = Path.home() / "snap/firefox/common/shot"
FONTS = ("https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700"
         "&family=Noto+Serif+TC:wght@600;700&family=JetBrains+Mono:wght@400;600&display=swap")


def main():
    order = json.loads((HERE / "project/deck.json").read_text())["order"]
    only = set(sys.argv[1:])
    global PROFILE
    PROFILE = SHOT / f"prof_{os.getpid()}"
    PROFILE.mkdir(exist_ok=True)
    for i, sid in enumerate(order, 1):
        if only and sid not in only:
            continue
        if not (HERE / f"project/slides/{sid}.html").exists():
            continue
        sec = (HERE / f"project/slides/{sid}.html").read_text(encoding="utf-8")
        sec = sec.replace("<section ", '<section data-x="1" ', 1).replace('style="', 'style="position:relative; width:1920px; height:1080px; box-sizing:border-box; ', 1)
        html = (f'<html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONTS}">'
                '<style>body{margin:0} p,h1,h2,h3,ul,ol{margin:0} aside{display:none}</style></head>'
                f"<body>{sec}</body></html>")
        page = SHOT / f"slide_{i:02d}.html"
        page.write_text(html, encoding="utf-8")
        subprocess.run(["timeout", "90", "firefox", "--headless", "--no-remote", "--profile", str(PROFILE),
                        "--window-size=1920,1080", "--screenshot", str(SHOT / f"slide_{i:02d}.png"), f"file://{page}"],
                       capture_output=True)
        print(i, sid, SHOT / f"slide_{i:02d}.png")


if __name__ == "__main__":
    main()
