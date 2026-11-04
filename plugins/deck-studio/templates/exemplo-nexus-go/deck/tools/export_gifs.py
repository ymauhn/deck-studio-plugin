"""Export the animated components as GIF (and MP4 for INT-PIPE and INT-PROP if ffmpeg exists).

Each frame is drawn by the component's deterministic render(t) and captured with
locator.screenshot(); frames are assembled with Pillow at 20 fps.
Usage: python -I deck/tools/export_gifs.py [ID ...]     -> gifs/<id>.gif, gifs/<id>.mp4
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
URL = (ROOT / "deck" / "dist" / "nexus-go-defense.html").as_uri()
OUT = ROOT / "gifs"
FPS = 20
# id: (duration in s or None for the component's own, output width, step to show, mp4)
JOBS = {
    "INT-FOLD": (12, 480, None, False),
    "INT-PROP": (None, 900, None, True),
    "INT-PIPE": (10, 1200, None, True),
    "INT-MP": (7.2, 696, [2, 3, 4], False),   # 2.4 s per step: 1 hop, 2 hops, oversmoothing
    "INT-GBA": (4, 520, 2, False),
}


def export(page, cid, dur, width, step, mp4):
    k = page.evaluate(f"[...document.querySelectorAll('section.slide')].indexOf(document.querySelector('[data-component=\"{cid}\"]').closest('section')) + 1")
    seq = step if isinstance(step, list) else None
    first = seq[0] if seq else step
    page.evaluate(f"deck.go({k}, {first if first is not None else 'deck.steps()[' + str(k - 1) + ']'})")
    page.wait_for_timeout(800)
    comp = f"deck.component('{cid}', {k})"
    page.evaluate(f"{comp}.pause()")
    if dur is None:
        dur = page.evaluate(f"{comp}.duration || {comp}.state().cycle || 10")
    loc = page.locator(f'[data-component="{cid}"]').first
    n = int(round(dur * FPS))
    tmp = Path(tempfile.mkdtemp(prefix=cid.lower()))
    frames = []
    for i in range(n):
        t = i / FPS
        if seq:  # one equal slice of the duration per step
            j = min(len(seq) - 1, int(t / (dur / len(seq))))
            page.evaluate(f"{comp}.step({seq[j]})")
            t -= j * dur / len(seq)
        page.evaluate(f"{comp}.render({t})")
        f = tmp / f"f{i:04d}.png"
        loc.screenshot(path=str(f), animations="disabled")
        frames.append(f)
    imgs = []
    for f in frames:
        im = Image.open(f).convert("RGB")
        if im.width != width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        imgs.append(im)
    OUT.mkdir(exist_ok=True)
    gif = OUT / f"{cid.lower()}.gif"
    pal = [im.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for im in imgs]
    pal[0].save(gif, save_all=True, append_images=pal[1:], duration=int(1000 / FPS), loop=0, optimize=True, disposal=1)
    msg = f"{gif.name}: {n} frames, {imgs[0].width}×{imgs[0].height}, {gif.stat().st_size / 1024 / 1024:.1f} MB"
    if mp4 and shutil.which("ffmpeg"):
        for i, im in enumerate(imgs):
            w, h = im.width // 2 * 2, im.height // 2 * 2
            im.crop((0, 0, w, h)).save(tmp / f"m{i:04d}.png")
        out = OUT / f"{cid.lower()}.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(tmp / "m%04d.png"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(out)], check=True)
        msg += f"; {out.name} {out.stat().st_size / 1024 / 1024:.1f} MB"
    shutil.rmtree(tmp, ignore_errors=True)
    print(msg)


def main(ids):
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1600, "height": 900})
        page.goto(URL)
        page.wait_for_function("window.deck !== undefined")
        page.evaluate("document.fonts.ready")
        page.evaluate("document.documentElement.dataset.theme = 'light'")
        for cid in ids or JOBS:
            export(page, cid, *JOBS[cid])
        b.close()


if __name__ == "__main__":
    main(sys.argv[1:])
