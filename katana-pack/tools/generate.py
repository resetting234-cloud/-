"""
Generates the 3D katana resource pack.

Output: assets/minecraft/{models,textures,items}/...

Run:  python3 tools/generate.py
(execute from katana-pack/ directory)
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent  # katana-pack/
ASSETS = ROOT / "assets" / "minecraft"

# ----------------------------------------------------------------------------
# Color schemes per material
# ----------------------------------------------------------------------------
# Each scheme defines RGB for the different parts of the katana so material
# identity reads at a glance.
SCHEMES = {
    "wooden": {
        # Bokken (wooden practice katana): light wood blade, dark wood handle
        "blade":      (188, 152, 105),
        "blade_hi":   (220, 188, 140),
        "blade_back": (135, 102,  65),
        "tsuba":      ( 75,  52,  30),
        "tsuba_hi":   (115,  85,  50),
        "wrap":       ( 95,  62,  35),
        "wrap_hi":    (135,  95,  60),
    },
    "iron": {
        "blade":      (210, 210, 220),
        "blade_hi":   (250, 250, 255),
        "blade_back": (140, 140, 150),
        "tsuba":      (108,  72,  35),  # brass
        "tsuba_hi":   (148, 105,  50),
        "wrap":       ( 38,  28,  22),  # dark leather
        "wrap_hi":    ( 78,  58,  48),
    },
    "diamond": {
        "blade":      (130, 240, 235),
        "blade_hi":   (210, 255, 250),
        "blade_back": ( 70, 180, 175),
        "tsuba":      (210, 175,  55),  # gold
        "tsuba_hi":   (245, 215, 100),
        "wrap":       ( 30,  50,  72),  # midnight blue
        "wrap_hi":    ( 70, 110, 145),
    },
    "netherite": {
        "blade":      ( 78,  68,  68),
        "blade_hi":   (140, 125, 120),
        "blade_back": ( 42,  38,  38),
        "tsuba":      (200, 150,  55),  # gold
        "tsuba_hi":   (235, 185,  85),
        "wrap":       ( 52,  35,  30),  # dark
        "wrap_hi":    ( 92,  68,  55),
    },
}

# ----------------------------------------------------------------------------
# Texture generation
# ----------------------------------------------------------------------------
# We use a 16x32 texture, declared as texture_size=[16,32] in the model JSON.
# Layout (x,y) — y grows downward in PNG, but we treat the texture as a UV
# atlas where each face has its own region:
#
#   (0,0)..(2,4)    : handle (tsuka) wrap pattern, 2x4 — used by all 4 sides
#   (2,0)..(4,2)    : handle top/bottom cap, 2x2
#   (4,0)..(8,4)    : guard (tsuba) top/bottom, 4x4
#   (0,4)..(4,5)    : guard sides, 4x1
#   (0,5)..(1,16)   : blade BACK (mune), 1x11
#   (1,5)..(2,16)   : blade FACE (front side), 1x11
#   (2,5)..(3,16)   : blade EDGE (cutting side), 1x11
#   (3,5)..(4,6)    : blade TIP/BASE caps, 1x1 (just a small bright square)
#
# (Anything past x=8 or y past 16 is unused but PIL still saves it.)

TEX_W, TEX_H = 16, 32


def _set(px, x, y, color):
    px[x, y] = color + (255,)


def _stripe(px, x0, y0, w, h, base, hi, vertical=False):
    """Paint a striped wrap/grip pattern."""
    for dy in range(h):
        for dx in range(w):
            i = (dy if vertical else dx) // 1
            color = hi if i % 2 == 0 else base
            _set(px, x0 + dx, y0 + dy, color)


def _solid(px, x0, y0, w, h, color):
    for dy in range(h):
        for dx in range(w):
            _set(px, x0 + dx, y0 + dy, color)


def make_texture(scheme: dict) -> Image.Image:
    img = Image.new("RGBA", (TEX_W, TEX_H), (0, 0, 0, 0))
    px = img.load()

    blade      = scheme["blade"]
    blade_hi   = scheme["blade_hi"]
    blade_back = scheme["blade_back"]
    tsuba      = scheme["tsuba"]
    tsuba_hi   = scheme["tsuba_hi"]
    wrap       = scheme["wrap"]
    wrap_hi    = scheme["wrap_hi"]

    # ----- Handle wrap (2x4) -----
    # Diagonal weave look: alternating 1-px diagonal bands.
    for dy in range(4):
        for dx in range(2):
            color = wrap_hi if (dx + dy) % 2 == 0 else wrap
            _set(px, dx, dy, color)

    # ----- Handle cap (2x2) -----
    _solid(px, 2, 0, 2, 2, wrap)
    _set(px, 2, 0, wrap_hi)  # tiny highlight

    # ----- Guard top/bottom (4x4) -----
    # Decorative: dark border, lighter center, single highlight pixel.
    _solid(px, 4, 0, 4, 4, tsuba)
    _solid(px, 5, 1, 2, 2, tsuba_hi)
    _set(px, 5, 1, tsuba)  # asymmetry pixel

    # ----- Guard side (4x1) -----
    for dx in range(4):
        _set(px, dx, 4, tsuba_hi if dx % 2 == 0 else tsuba)

    # ----- Blade back / mune (1x11) -----
    for dy in range(11):
        _set(px, 0, 5 + dy, blade_back)
    # subtle highlight near tip
    _set(px, 0, 5, blade)

    # ----- Blade face (1x11) -----
    for dy in range(11):
        _set(px, 1, 5 + dy, blade)
    _set(px, 1, 5, blade_hi)

    # ----- Blade edge / ha (1x11), cutting edge — brightest -----
    for dy in range(11):
        _set(px, 2, 5 + dy, blade_hi)
    _set(px, 2, 15, blade)  # base tinted slightly

    # ----- Tip cap (1x1) -----
    _set(px, 3, 5, blade_hi)

    return img


# ----------------------------------------------------------------------------
# Model JSON generation
# ----------------------------------------------------------------------------
# Geometry (axis-aligned, will be rotated into hand by display transforms):
#   Handle (tsuka):  2 x 4 x 2  — at [7..9, 0..4, 7..9]
#   Guard  (tsuba):  4 x 1 x 4  — at [6..10, 4..5, 6..10]
#   Blade            1 x 11 x 0.5 at [7.5..8.5, 5..16, 7.75..8.25]


def _face(uv, tex="#0", **extra):
    f = {"uv": uv, "texture": tex}
    f.update(extra)
    return f


def _diag_rot():
    """45° clockwise rotation around Z, centered at model midpoint.

    Re-orients each axis-aligned cuboid so the whole katana points along the
    bottom-left → top-right diagonal — the same orientation that vanilla
    `item/handheld` display transforms expect.
    """
    return {"origin": [8, 8, 8], "axis": "z", "angle": -45}


def make_model(name: str) -> dict:
    tex = f"item/{name}_sword"
    rot = _diag_rot()
    return {
        "credit": "MeetionRC 3D katana pack — generated",
        "texture_size": [TEX_W, TEX_H],
        "textures": {
            "0": tex,
            "particle": tex,
        },
        "elements": [
            # ---- Handle (tsuka): 2x4x2 ----
            {
                "name": "handle",
                "from":     [7, 0, 7],
                "to":       [9, 4, 9],
                "rotation": rot,
                "faces": {
                    "north": _face([0, 0, 2, 4]),
                    "east":  _face([0, 0, 2, 4]),
                    "south": _face([0, 0, 2, 4]),
                    "west":  _face([0, 0, 2, 4]),
                    "down":  _face([2, 0, 4, 2]),
                    "up":    _face([2, 0, 4, 2]),
                },
            },
            # ---- Guard (tsuba): 4x1x4 ----
            {
                "name": "guard",
                "from":     [6, 4, 6],
                "to":       [10, 5, 10],
                "rotation": rot,
                "faces": {
                    "north": _face([0, 4, 4, 5]),
                    "east":  _face([0, 4, 4, 5]),
                    "south": _face([0, 4, 4, 5]),
                    "west":  _face([0, 4, 4, 5]),
                    "down":  _face([4, 0, 8, 4]),
                    "up":    _face([4, 0, 8, 4]),
                },
            },
            # ---- Blade: 1 wide x 11 tall x 0.5 deep ----
            {
                "name": "blade",
                "from":     [7.5, 5,  7.75],
                "to":       [8.5, 16, 8.25],
                "rotation": rot,
                "faces": {
                    "north": _face([1, 5, 2, 16]),  # face (front)
                    "south": _face([1, 5, 2, 16]),  # face (back)
                    "east":  _face([2, 5, 3, 16]),  # cutting edge (ha)
                    "west":  _face([0, 5, 1, 16]),  # spine (mune)
                    "up":    _face([3, 5, 4, 6]),   # tip
                    "down":  _face([3, 5, 4, 6]),   # base
                },
            },
        ],
        # The model is already diagonal (bottom-left → top-right), so we can
        # reuse vanilla `item/handheld` display values verbatim.
        "display": {
            "thirdperson_righthand": {
                "rotation":    [0, -90, 55],
                "translation": [0, 4, 0.5],
                "scale":       [0.85, 0.85, 0.85],
            },
            "thirdperson_lefthand": {
                "rotation":    [0,  90, -55],
                "translation": [0, 4, 0.5],
                "scale":       [0.85, 0.85, 0.85],
            },
            "firstperson_righthand": {
                "rotation":    [0, -90, 25],
                "translation": [1.13, 3.2, 1.13],
                "scale":       [0.68, 0.68, 0.68],
            },
            "firstperson_lefthand": {
                "rotation":    [0,  90, -25],
                "translation": [1.13, 3.2, 1.13],
                "scale":       [0.68, 0.68, 0.68],
            },
            "ground": {
                "rotation":    [0, 0, 0],
                "translation": [0, 2, 0],
                "scale":       [0.5, 0.5, 0.5],
            },
            "head": {
                "rotation":    [0, 180, 0],
                "translation": [0, 13, 7],
                "scale":       [1, 1, 1],
            },
            "fixed": {
                "rotation":    [0, 180, 0],
                "translation": [0, 0, 0],
                "scale":       [1, 1, 1],
            },
            "gui": {
                "rotation":    [0, 0, 0],
                "translation": [0, 0, 0],
                "scale":       [1, 1, 1],
            },
        },
    }


def make_item_definition(name: str) -> dict:
    """1.21.4+ items/ entry. Pre-1.21.4 ignores this file."""
    return {
        "model": {
            "type": "minecraft:model",
            "model": f"minecraft:item/{name}_sword",
        },
    }


# ----------------------------------------------------------------------------
# Pack metadata
# ----------------------------------------------------------------------------

def make_pack_mcmeta() -> dict:
    return {
        "pack": {
            "pack_format": 15,
            "supported_formats": {"min_inclusive": 15, "max_inclusive": 64},
            "description": "MeetionRC \u00a76\u00a7l3D Katanas\u00a7r\n\u00a77wooden / iron / diamond / netherite",
        }
    }


def make_pack_icon() -> Image.Image:
    """Simple 64x64 pack icon: a stylized katana on dark background."""
    s = SCHEMES["netherite"]
    img = Image.new("RGBA", (64, 64), (15, 15, 22, 255))
    px = img.load()
    # Quick & dirty diagonal blade for the icon
    for i in range(46):
        x = 8 + i
        y = 56 - i
        for d in range(-1, 2):
            if 0 <= x + d < 64 and 0 <= y + d < 64:
                px[x + d, y + d] = s["blade"] + (255,)
        if 0 <= x < 64 and 0 <= y < 64:
            px[x, y] = s["blade_hi"] + (255,)
    # Tsuba
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            if abs(dx) + abs(dy) <= 4:
                xx, yy = 9 + dx, 55 + dy
                if 0 <= xx < 64 and 0 <= yy < 64:
                    px[xx, yy] = s["tsuba"] + (255,)
    # Handle
    for i in range(8):
        for d in range(-2, 3):
            xx, yy = 4 + i + d, 60 - i + d
            if 0 <= xx < 64 and 0 <= yy < 64 and (xx + yy) % 2 == 0:
                px[xx, yy] = s["wrap"] + (255,)
            elif 0 <= xx < 64 and 0 <= yy < 64:
                if abs(d) <= 1:
                    px[xx, yy] = s["wrap_hi"] + (255,)
    return img


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main() -> None:
    # Ensure dirs
    (ASSETS / "models" / "item").mkdir(parents=True, exist_ok=True)
    (ASSETS / "textures" / "item").mkdir(parents=True, exist_ok=True)
    (ASSETS / "items").mkdir(parents=True, exist_ok=True)

    for name, scheme in SCHEMES.items():
        # Texture
        tex_img = make_texture(scheme)
        tex_path = ASSETS / "textures" / "item" / f"{name}_sword.png"
        tex_img.save(tex_path)

        # Model
        model = make_model(name)
        model_path = ASSETS / "models" / "item" / f"{name}_sword.json"
        model_path.write_text(json.dumps(model, indent=2, ensure_ascii=False) + "\n")

        # Item definition (1.21.4+)
        item_def = make_item_definition(name)
        item_path = ASSETS / "items" / f"{name}_sword.json"
        item_path.write_text(json.dumps(item_def, indent=2, ensure_ascii=False) + "\n")

        print(f"  generated {name:9s}  -> {tex_path.relative_to(ROOT)}, "
              f"{model_path.relative_to(ROOT)}, {item_path.relative_to(ROOT)}")

    # pack.mcmeta
    pmc = ROOT / "pack.mcmeta"
    pmc.write_text(json.dumps(make_pack_mcmeta(), indent=2, ensure_ascii=False) + "\n")
    print(f"  wrote {pmc.relative_to(ROOT)}")

    # pack.png
    icon = make_pack_icon()
    icon_path = ROOT / "pack.png"
    icon.save(icon_path)
    print(f"  wrote {icon_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
