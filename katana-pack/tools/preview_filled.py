"""
3D preview rendering: rasterise each cuboid as proper polygons (real
rotated quads), not AABBs. Looks roughly like Minecraft GUI render.
"""

from __future__ import annotations
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
PREVIEW = ROOT / "preview"
PREVIEW.mkdir(exist_ok=True)
NAMES = ["wooden", "iron", "diamond", "netherite"]

VIEW = 256
SCALE = 13


def _z_rot(p, origin, angle_deg):
    ox, oy, _ = origin
    a = math.radians(angle_deg)
    x, y, z = p
    dx, dy = x - ox, y - oy
    return (
        ox + dx * math.cos(a) - dy * math.sin(a),
        oy + dx * math.sin(a) + dy * math.cos(a),
        z,
    )


def _to_screen(p):
    x, y, _ = p
    sx = int(20 + x * SCALE)
    sy = int(VIEW - 20 - y * SCALE)
    return (sx, sy)


def _avg_uv_color(tex, uv):
    u0, v0, u1, v1 = uv
    cu = max(0, min(tex.width - 1, int((u0 + u1) / 2)))
    cv = max(0, min(tex.height - 1, int((v0 + v1) / 2)))
    return tex.getpixel((cu, cv))


def _shade(color, factor):
    if len(color) == 4:
        r, g, b, a = color
    else:
        r, g, b = color
        a = 255
    return (
        max(0, min(255, int(r * factor))),
        max(0, min(255, int(g * factor))),
        max(0, min(255, int(b * factor))),
        a,
    )


def render_model(name):
    model = json.loads((ROOT / f"assets/minecraft/models/item/{name}_sword.json").read_text())
    tex = Image.open(ROOT / f"assets/minecraft/textures/item/{name}_sword.png").convert("RGBA")

    img = Image.new("RGBA", (VIEW, VIEW), (40, 42, 54, 255))
    draw = ImageDraw.Draw(img)

    # Render order: handle (back), guard (middle), blade (front).
    # Each cuboid: draw the 6 faces in order from "back" to "front" using
    # a simple z-sort.
    for el in model["elements"]:
        f, t = el["from"], el["to"]
        c = [
            (f[0], f[1], f[2]), (t[0], f[1], f[2]), (t[0], t[1], f[2]), (f[0], t[1], f[2]),
            (f[0], f[1], t[2]), (t[0], f[1], t[2]), (t[0], t[1], t[2]), (f[0], t[1], t[2]),
        ]
        rot = el.get("rotation")
        if rot and rot.get("axis") == "z":
            c = [_z_rot(p, rot["origin"], rot["angle"]) for p in c]

        # Define faces by their corner indices and which face name they map to
        # Standard Minecraft cuboid corner order:
        #   0=fff 1=tff 2=ttf 3=ftf  (z=f, "north")
        #   4=fft 5=tft 6=ttt 7=ftt  (z=t, "south")
        face_defs = [
            ("north", [0, 1, 2, 3], 0.75),  # z=from (back), darker
            ("down",  [0, 1, 5, 4], 0.65),  # y=from (bottom), darkest
            ("east",  [1, 2, 6, 5], 0.85),
            ("west",  [0, 3, 7, 4], 0.85),
            ("up",    [3, 2, 6, 7], 1.05),  # top, brightest
            ("south", [4, 5, 6, 7], 1.0),   # z=to (front)
        ]
        for fname, idxs, shade in face_defs:
            face = el["faces"].get(fname)
            if not face:
                continue
            poly = [_to_screen(c[i]) for i in idxs]
            base_color = _avg_uv_color(tex, face["uv"])
            color = _shade(base_color, shade)
            if color[3] == 0:
                continue
            draw.polygon(poly, fill=color, outline=_shade(color, 0.6))

    return img


def main():
    pad = 8
    out = Image.new("RGBA", (VIEW * 2 + pad * 3, VIEW * 2 + pad * 3), (15, 15, 22, 255))
    positions = [(pad, pad), (VIEW + 2 * pad, pad),
                 (pad, VIEW + 2 * pad), (VIEW + 2 * pad, VIEW + 2 * pad)]
    for name, pos in zip(NAMES, positions):
        out.paste(render_model(name), pos)
    out.save(PREVIEW / "render_filled.png")
    print(f"  wrote {PREVIEW / 'render_filled.png'}")


if __name__ == "__main__":
    main()
