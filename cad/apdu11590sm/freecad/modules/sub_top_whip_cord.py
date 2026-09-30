# =====================================================================
# sub_top_whip_cord.py — Gland nut hex, strain-relief boot taper
# 36->28, kabel fleksibel Ø28, plug IEC 60309 100A 415V 3P+N+PE (merah).
# Konversi dari sub_top_whip_cord.scad. Origin: bidang top cap (z=0 lokal).
# =====================================================================
import math
from FreeCAD import Vector as V
from ._common import (P, validate, cyl, cone, hex_prism, SCREW_BLACK,
                      BOOT_BLACK, WHIP_BLACK, PLUG_RED, PLUG_REDDARK,
                      PIN_SILVER)

GLAND_HEX_AF = 36.0
GLAND_H = 10.0
BOOT_D_BOT = 36.0
BOOT_D_TOP = 28.0
BOOT_H = 50.0
CORD_DIA = 28.0
CORD_LEN = 300.0          # stub preview (sesuai OpenSCAD tahap 1)

PLUG_DIA = 80.0
PLUG_LEN = 160.0
PLUG_RING_DIA = 88.0
PLUG_RING_H = 18.0
PLUG_PIN_DIA = 6.0
PLUG_PIN_H = 15.0
PLUG_PIN_R = 25.0
PLUG_PIN_ANGLES = (90, 162, 234, 306, 18)


def build_whip_cord(parts, prefix="WHIP", offset=(0, 0, 0)):
    z0 = offset[2]

    # ---- Gland nut hex ----
    gland = hex_prism(GLAND_HEX_AF, GLAND_H, offset[0], offset[1], z0)
    validate(prefix + "_GLAND", gland)
    P(parts, prefix + "_GLAND", gland, SCREW_BLACK)

    # ---- Rubber strain-relief boot (taper) ----
    boot = cone(BOOT_D_BOT, BOOT_D_TOP, BOOT_H,
                offset[0], offset[1], z0 + GLAND_H)
    validate(prefix + "_BOOT", boot)
    P(parts, prefix + "_BOOT", boot, BOOT_BLACK)

    # ---- Kabel fleksibel ----
    cord = cyl(CORD_DIA, CORD_LEN, offset[0], offset[1], z0 + GLAND_H + BOOT_H)
    validate(prefix + "_CORD", cord)
    P(parts, prefix + "_CORD", cord, WHIP_BLACK)

    z_plug = z0 + GLAND_H + BOOT_H + CORD_LEN

    # ---- Plug IEC 60309: kerah kabel, barrel, locking ring, 5 pin ----
    collar = cone(CORD_DIA + 4, PLUG_DIA, 20, offset[0], offset[1], z_plug)
    P(parts, prefix + "_PLUG_COLLAR", collar, PLUG_REDDARK)

    barrel = cyl(PLUG_DIA, PLUG_LEN, offset[0], offset[1], z_plug)
    validate(prefix + "_PLUG_BARREL", barrel)
    P(parts, prefix + "_PLUG_BARREL", barrel, PLUG_RED)

    ring = cyl(PLUG_RING_DIA, PLUG_RING_H, offset[0], offset[1],
               z_plug + PLUG_LEN - PLUG_RING_H - 12)
    validate(prefix + "_PLUG_RING", ring)
    P(parts, prefix + "_PLUG_RING", ring, PLUG_REDDARK)

    pins = []
    for a in PLUG_PIN_ANGLES:
        r = math.radians(a)
        pins.append(cyl(PLUG_PIN_DIA, PLUG_PIN_H,
                        offset[0] + PLUG_PIN_R * math.cos(r),
                        offset[1] + PLUG_PIN_R * math.sin(r),
                        z_plug + PLUG_LEN - 0.5))
    P(parts, prefix + "_PLUG_PINS", pins[0].fuse(pins[1:]), PIN_SILVER)

    return parts
