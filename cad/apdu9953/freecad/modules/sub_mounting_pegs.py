# =====================================================================
# sub_mounting_pegs.py — FreeCAD Solid B-Rep Rear Mounting System
# 1:1 REPLIKASI DETAIL OPENSCAD (sub_mounting_pegs.scad)
# Termasuk:
#  - Dual Mounting Pads (Primary dengan counterbore peg seat, Secondary tanpa lubang)
#  - Toolless Mounting Peg (Base pin Ø6 mm, Flange Ø16 mm, Neck Ø6 mm,
#    Mushroom head Ø12 mm dengan 6-lobe Torx T15 drive recess)
#  - M5 Brass Grounding Stud dengan washer & 8 mm AF Hex Nut
#  - Brass Ground Symbol plate 3D
# =====================================================================
import FreeCAD as App
import Part
from ._common import (
    V, P, box, cbox, cyl, cone, hex_prism, rounded_prism_y,
    make_torx_t15_cutter,
    METAL_STEEL, BRASS_GOLD
)

PAD_W = 42.0
PAD_H = 42.0
PAD_T = 6.0
PAD_R = 2.5
PAD_STEP = 52.0
PEG_SPACING = 1680.0

def build_mounting_pad(center_z, rear_y=23.0, primary=True, explode=0.0):
    """Membangun bantalan dudukan (mounting pad) dengan bevel keliling."""
    pad_ey = 35.0 * explode
    pad_base = rounded_prism_y(PAD_W, PAD_H, PAD_R, PAD_T - 0.9, y0=rear_y + pad_ey)
    pad_bevel = rounded_prism_y(PAD_W - 1.8, PAD_H - 1.8, PAD_R - 0.9, 0.9, y0=rear_y + PAD_T - 0.9 + pad_ey)
    pad = pad_base.fuse(pad_bevel)

    if primary:
        bore = cyl(6.4, PAD_T + 2.0, 0.0, rear_y - 1.0 + pad_ey, 0.0, dirv=(0, 1, 0))
        cbore = cyl(16.4, 2.6, 0.0, rear_y + PAD_T - 2.58 + pad_ey, 0.0, dirv=(0, 1, 0))
        pad = pad.cut(bore).cut(cbore)

    pad.translate(V(0.0, 0.0, center_z))
    return pad

def build_toolless_peg(center_z, rear_y=23.0, explode=0.0):
    """Membangun pasak toolless peg dengan Torx T15 drive recess."""
    peg_ey = (PAD_T - 2.55) + 85.0 * explode
    y_base = rear_y + peg_ey

    p1 = cyl(6.0, 3.9, 0.0, y_base - 3.9, center_z, dirv=(0, 1, 0))
    p2 = cyl(16.0, 2.5, 0.0, y_base, center_z, dirv=(0, 1, 0))
    p3 = cyl(6.0, 17.5, 0.0, y_base + 2.5, center_z, dirv=(0, 1, 0))

    # Mushroom head
    y_head = y_base + 20.0
    c1 = cone(10.6, 12.0, 0.7, 0.0, y_head, center_z, dirv=(0, 1, 0))
    c2 = cyl(12.0, 3.6, 0.0, y_head + 0.7, center_z, dirv=(0, 1, 0))
    c3 = cone(12.0, 10.6, 0.7, 0.0, y_head + 4.3, center_z, dirv=(0, 1, 0))
    head = c1.fuse([c2, c3])

    peg = p1.fuse([p2, p3, head])

    # Torx T15 drive recess di puncak head (arah -Y)
    cutter = make_torx_t15_cutter(V(0.0, y_head + 5.0, center_z), V(0.0, -1.0, 0.0), depth=1.7)
    return peg.cut(cutter)

def build_ground_stud(ground_z=-764.5, rear_y=23.0, explode=0.0):
    """Membangun stud grounding kuningan M5 dengan washer dan 8 mm AF nut."""
    e = explode
    stud = cyl(5.0, 13.0, 10.0, rear_y + 25.0 * e, ground_z, dirv=(0, 1, 0))

    # Cincin ulir
    rings = [cyl(5.3, 0.35, 10.0, rear_y + 25.0 * e + z, ground_z, dirv=(0, 1, 0)) for z in range(1, 13, 2)]
    all_rings = rings[0].fuse(rings[1:])
    stud = stud.fuse(all_rings)

    # Washer
    w_base = cyl(12.0, 1.2, 10.0, rear_y + 1.0 + (25.0 + 8.0) * e, ground_z, dirv=(0, 1, 0))
    w_hole = cyl(5.4, 1.4, 10.0, rear_y + 0.9 + (25.0 + 8.0) * e, ground_z, dirv=(0, 1, 0))
    washer = w_base.cut(w_hole)

    # 8 mm AF Hex Nut
    n_base = hex_prism(8.0, 4.0, 10.0, rear_y + 2.6 + (25.0 + 16.0) * e, ground_z, dirv=(0, 1, 0))
    n_hole = cyl(5.4, 4.2, 10.0, rear_y + 2.5 + (25.0 + 16.0) * e, ground_z, dirv=(0, 1, 0))
    nut = n_base.cut(n_hole)

    return stud.fuse([washer, nut])

def build_ground_symbol(ground_z=-764.5, rear_y=23.0):
    """Membangun simbol grounding kuningan timbul."""
    s1 = cbox(0.8, 0.4, 5.0, -11.0, rear_y + 0.2, ground_z + 2.0)
    s2 = cbox(8.0, 0.4, 0.8, -11.0, rear_y + 0.2, ground_z)
    s3 = cbox(6.0, 0.4, 0.8, -11.0, rear_y + 0.2, ground_z - 2.0)
    s4 = cbox(4.0, 0.4, 0.8, -11.0, rear_y + 0.2, ground_z - 4.0)
    return s1.fuse([s2, s3, s4])

def build_mounting_pegs(parts, prefix="Mounting", spacing=PEG_SPACING,
                        rear_y=23.0, explode=0.0, doc=None, show_mounting=True):
    if not show_mounting:
        return

    e = explode
    chassis_ey = 200.0 * e

    for idx, dz in enumerate([spacing / 2.0, -spacing / 2.0]):
        pz = dz
        tag = "Top" if idx == 0 else "Bot"

        # Primary Pad & Secondary Pad
        pad_pri = build_mounting_pad(pz, rear_y=rear_y + chassis_ey, primary=True, explode=e)
        pad_sec = build_mounting_pad(pz - PAD_STEP, rear_y=rear_y + chassis_ey, primary=False, explode=e)
        pads = pad_pri.fuse(pad_sec)
        P(parts, f"{prefix}_{tag}_Pads", pads, (0.118, 0.133, 0.176))

        # Toolless Peg
        peg = build_toolless_peg(pz, rear_y=rear_y + chassis_ey, explode=e)
        P(parts, f"{prefix}_{tag}_Peg", peg, METAL_STEEL)

    # Grounding Stud & Symbol (Z = -764.5 relatif terhadap PDU_H / 2)
    ground_z = -764.5
    g_stud = build_ground_stud(ground_z, rear_y=rear_y + chassis_ey, explode=e)
    g_sym = build_ground_symbol(ground_z, rear_y=rear_y + chassis_ey)
    P(parts, f"{prefix}_GroundStud", g_stud, BRASS_GOLD)
    P(parts, f"{prefix}_GroundSymbol", g_sym, BRASS_GOLD)
