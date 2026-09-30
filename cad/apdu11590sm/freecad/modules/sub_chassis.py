# =====================================================================
# sub_chassis.py — Enclosure sheet metal 2030 x 85 x 85 mm, wall 1.5,
# sudut luar R2 (via profil rounded), 3 zona cutout muka, top/bottom cap.
# Konversi B-Rep dari sub_chassis.scad (Tahap 1 OpenSCAD, tervalidasi).
# =====================================================================
from ._common import (P, validate, box, cyl, rounded_prism,
                      GSPE_BLACK, CAP_DARK)

CHASSIS_H = 2030.0
CHASSIS_W = 85.0
CHASSIS_D = 85.0
CHASSIS_WALL = 1.5
CHASSIS_R = 2.0
CAP_T = 2.0                 # tebal end cap (per handoff Tahap 2)
GLAND_HOLE_DIA = 34.0       # lubang cable gland di top cap
GROUND_HOLE_DIA = 6.2       # lubang grounding stud M6 di bottom cap

# Zona cutout muka (z_center, tinggi, lebar)
CHASSIS_FRONT_ZONES = [
    (654.0, 410.0, 78.5),    # Bank Bawah (Soket 1-24 + Breaker B1-B6)
    (1000.0, 152.0, 56.5),   # NMC3 Controller Cassette
    (1454.0, 410.0, 78.5),   # Bank Atas (Soket 25-48 + Breaker B7-B12)
]

EPS = 0.05


def build_chassis(parts, prefix="CHASSIS"):
    # ---- Badan ekstrusi (tabung persegi rounded berongga) ----
    outer = rounded_prism(CHASSIS_W, CHASSIS_D, CHASSIS_R, CHASSIS_H + 2 * EPS, z=-EPS)
    inner = rounded_prism(CHASSIS_W - 2 * CHASSIS_WALL,
                          CHASSIS_D - 2 * CHASSIS_WALL,
                          max(CHASSIS_R - CHASSIS_WALL, 0.1),
                          CHASSIS_H + 4 * EPS, z=-2 * EPS)
    shell = outer.cut(inner)

    # Cutout zona muka (front = -Y): hanya tembus dinding depan
    tools = []
    for zc, zh, zw in CHASSIS_FRONT_ZONES:
        tools.append(box(zw + 2 * EPS, CHASSIS_WALL + 2 * EPS, zh + 2 * EPS,
                         -zw / 2 - EPS,
                         -CHASSIS_D / 2 - EPS,
                         zc - zh / 2 - EPS))
    zone_tool = tools[0]
    for t in tools[1:]:
        zone_tool = zone_tool.fuse(t)
    shell = shell.cut(zone_tool)
    validate(prefix + "_SHELL", shell)
    P(parts, prefix + "_SHELL", shell, GSPE_BLACK)

    # ---- Bottom cap (Z = 0 .. CAP_T), lubang grounding M6 (0, +20) ----
    cap_w = CHASSIS_W - 0.6
    cap_r = max(CHASSIS_R - 0.3, 0.1)
    bottom = rounded_prism(cap_w, cap_w, cap_r, CAP_T + EPS, z=-EPS * 0.5)
    bottom = bottom.cut(cyl(GROUND_HOLE_DIA, CAP_T + 2 * EPS, 0, 20, -EPS))
    validate(prefix + "_CAP_BOTTOM", bottom)
    P(parts, prefix + "_CAP_BOTTOM", bottom, CAP_DARK)

    # ---- Top cap (Z = H-CAP_T .. H), lubang cable gland Ø34 di pusat ----
    top = rounded_prism(cap_w, cap_w, cap_r, CAP_T + EPS, z=CHASSIS_H - CAP_T - EPS * 0.5)
    top = top.cut(cyl(GLAND_HOLE_DIA, CAP_T + 2 * EPS, 0, 0, CHASSIS_H - CAP_T - EPS))
    validate(prefix + "_CAP_TOP", top)
    P(parts, prefix + "_CAP_TOP", top, CAP_DARK)

    return parts
