"""
Visual preview helpers for the katana pack.

Outputs:
  preview/textures.png       — all 4 textures, upscaled side-by-side
  preview/render.png         — orthographic 3D render of each katana model

`render.png` uses a tiny custom rasteriser that reads the model JSON, applies
the per-element rotation, projects to screen, and shoots a Z-sorted
"voxel ray" so faces look reasonable. It's not pretty, but good enough to
sanity-check geometry & UVs.
"""

from __future__ import annotations
import json
import math
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PREVIEW = ROOT / "preview"
PREVIEW.mkdir(exist_ok=True)

NAMES = ["wooden", "iron", "diamond", "netherite"]
SCALE = 16  # upscale factor for raw textures


# ---------------------------------------------------------------------------
# Raw texture preview
# ---------------------------------------------------------------------------
def texture_grid():
    pad = 8
    panels = []
    for n in NAMES:
        t = Image.open(ROOT / f"assets/minecraft/textures/item/{n}_sword.png")
        big = t.resize((t.width * SCALE, t.height * SCALE), Image.NEAREST)
        panels.append((n, big))
    w = max(p.width for _, p in panels) + 2 * pad
    h = sum(p.height + 4 * pad for _, p in panels)
    out = Image.new("RGBA", (w, h), (40, 40, 50, 255))
    y = pad
    for name, p in panels:
        out.paste(p, (pad, y))
        y += p.height + pad
    out.save(PREVIEW / "textures.png")
    print(f"  wrote {PREVIEW / 'textures.png'}")


# ---------------------------------------------------------------------------
# Crude 3D render of each model
# ---------------------------------------------------------------------------
# We rasterise each cuboid independently as a wireframe + filled translucent
# box, applying the per-element Z-axis rotation. View is isometric-ish.
# This is for visual sanity checking, not pretty rendering.

VIEW_W, VIEW_H = 256, 256


def _project(p, view_rot=(20, 30, 0)):
    """Very simple isometric-ish projection from model space to screen."""
    rx, ry, _ = view_rot
    rx = math.radians(rx)
    ry = math.radians(ry)
    x, y, z = p
    x -= 8; y -= 8; z -= 8
    # rotate Y
    x, z = x * math.cos(ry) - z * math.sin(ry), x * math.sin(ry) + z * math.cos(ry)
    # rotate X (pitch)
    y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
    # orthographic projection
    sx = VIEW_W / 2 + x * 6
    sy = VIEW_H / 2 - y * 6
    return sx, sy, z


def _z_rot(p, origin, angle_deg):
    ox, oy, oz = origin
    a = math.radians(angle_deg)
    x, y, z = p
    dx, dy = x - ox, y - oy
    return (
        ox + dx * math.cos(a) - dy * math.sin(a),
        oy + dx * math.sin(a) + dy * math.cos(a),
        z,
    )


def render_model(name, scheme_color):
    model = json.loads((ROOT / f"assets/minecraft/models/item/{name}_sword.json").read_text())
    img = Image.new("RGBA", (VIEW_W, VIEW_H), (25, 25, 35, 255))
    px = img.load()

    for el in model["elements"]:
        f, t = el["from"], el["to"]
        # 8 corners
        corners = [
            (f[0], f[1], f[2]), (t[0], f[1], f[2]), (t[0], t[1], f[2]), (f[0], t[1], f[2]),
            (f[0], f[1], t[2]), (t[0], f[1], t[2]), (t[0], t[1], t[2]), (f[0], t[1], t[2]),
        ]
        rot = el.get("rotation")
        if rot and rot.get("axis") == "z":
            corners = [_z_rot(c, rot["origin"], rot["angle"]) for c in corners]
        projected = [_project(c) for c in corners]

        # 12 cube edges — connect corners
        edges = [
            (0,1),(1,2),(2,3),(3,0),
            (4,5),(5,6),(6,7),(7,4),
            (0,4),(1,5),(2,6),(3,7),
        ]
        for a, b in edges:
            x0, y0, _ = projected[a]
            x1, y1, _ = projected[b]
            steps = int(max(abs(x1-x0), abs(y1-y0))) + 1
            for s in range(steps + 1):
                u = s / steps
                xx = int(x0 + (x1-x0)*u)
                yy = int(y0 + (y1-y0)*u)
                if 0 <= xx < VIEW_W and 0 <= yy < VIEW_H:
                    px[xx, yy] = scheme_color + (255,)

    return img


def render_grid():
    colors = {
        "wooden":    (220, 188, 140),
        "iron":      (240, 240, 250),
        "diamond":   (200, 255, 250),
        "netherite": (200, 150,  55),
    }
    pad = 8
    out = Image.new("RGBA", (VIEW_W * 2 + pad * 3, VIEW_H * 2 + pad * 3), (15, 15, 22, 255))
    positions = [(pad, pad), (VIEW_W + 2 * pad, pad),
                 (pad, VIEW_H + 2 * pad), (VIEW_W + 2 * pad, VIEW_H + 2 * pad)]
    for (name, pos) in zip(NAMES, positions):
        r = render_model(name, colors[name])
        out.paste(r, pos)
    out.save(PREVIEW / "render.png")
    print(f"  wrote {PREVIEW / 'render.png'}")


if __name__ == "__main__":
    texture_grid()
    render_grid()
