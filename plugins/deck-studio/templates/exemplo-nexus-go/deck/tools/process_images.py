"""Copy the thesis figures into deck/build/img as web-sized WebP files.

Usage: python -I deck/tools/process_images.py <thesis_dir> <out_dir>

Originals are never touched. Each figure is downscaled so its longest side is at most
MAX_SIDE, then saved as lossless WebP when that is not much larger than lossy q88
(line art), otherwise lossy q88 (photos, heat maps). Figure 5.6 is cropped above its
late-fusion box (see docs/FIGURES.md).
"""
import io, sys
from pathlib import Path
from PIL import Image

MAX_SIDE = 2400

FIGS = {
    "fig4_go_hierarchy_EN.png": "fig_2_1",
    "fig1_protein_EN.png": "fig_2_2",
    "fig_graph_notation.png": "fig_2_3",
    "fig2_cnn_EN.png": "fig_2_6",
    "fig3_autoencoder_EN.png": "fig_2_7",
    "fig_cap4_score_and_degree.png": "fig_4_1",
    "fig_cap4_isolated_by_split.png": "fig_4_2",
    "fig_cap4_isolated_vs_threshold.png": "fig_4_3",
    "cap5/fig_5_01_chapter_map.png": "fig_5_1",
    "cap5/fig_5_02_learning_regime.png": "fig_5_2",
    "cap5/fig_5_04_network_only_pipeline.png": "fig_5_3",
    "cap5/fig_5_03_outer_difference.png": "fig_5_4",
    "cap5/fig_5_05_isolated_vs_connected.png": "fig_5_5",
    "cap5/fig_5_06_hybrid_pipeline.png": "fig_5_6",
    "cap5/fig_5_07_prott5_extraction.png": "fig_5_7",
    "cap5/fig_5_08_fixed_propagation.png": "fig_5_8",
    "cap5/fig_5_09_reshape_to_image.png": "fig_5_9",
    "cap5/fig_5_10_early_late_fusion.png": "fig_5_10",
    "fig_hops_vetorial.png": "fig_6_1",
    "fig_alpha_vetorial.png": "fig_6_2",
    "fig_hops_visual.png": "fig_6_3",
    "fig_alpha_visual.png": "fig_6_4",
    "fig_custo.png": "fig_6_5",
    "fig_grau.png": "fig_6_6",
}


def is_green(p):
    r, g, b = p[:3]
    return g > 140 and r < 80 and 90 < b < 160


def is_grey_border(p):
    r, g, b = p[:3]
    return 80 < r < 130 and abs(r - g) < 12 and 110 < b < 150


def crop_5_6(im):
    """Cut just below the grey '500 logits' box, i.e. above the late-fusion box."""
    rgb = im.convert("RGB")
    w, h = rgb.size
    px = rgb.load()
    row_count = lambda y, test: sum(1 for x in range(0, w, 2) if test(px[x, y]))
    green_top = next(y for y in range(h // 2, h) if row_count(y, is_green) > w // 6
                     and y > h * 0.8)
    grey_bottom = next(y for y in range(green_top - 1, 0, -1) if row_count(y, is_grey_border) > w // 20)
    return im.crop((0, 0, w, grey_bottom + 6)), green_top, grey_bottom


def encode(im):
    lossy, lossless = io.BytesIO(), io.BytesIO()
    im.save(lossy, "WEBP", quality=88, method=6)
    im.save(lossless, "WEBP", lossless=True, method=6)
    return lossless.getvalue() if lossless.tell() < 1.3 * lossy.tell() else lossy.getvalue()


def main(src, out):
    out.mkdir(parents=True, exist_ok=True)
    total = 0
    for name, key in FIGS.items():
        im = Image.open(src / name)
        im.load()
        if key == "fig_5_6":
            im, gt, gb = crop_5_6(im)
            print(f"  fig_5_6 crop: late-fusion top border at y={gt}, grey box bottom at y={gb}")
        if max(im.size) > MAX_SIDE:
            im.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA" if "A" in im.getbands() or im.mode == "P" else "RGB")
        data = encode(im)
        (out / f"{key}.webp").write_bytes(data)
        total += len(data)
        print(f"{key:9s} {im.size[0]:5d}x{im.size[1]:<5d} {len(data)/1024:7.0f} KiB  <- {name}")
    print(f"total {total/1024/1024:.2f} MiB")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
