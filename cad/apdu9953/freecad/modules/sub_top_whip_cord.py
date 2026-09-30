# =====================================================================
# sub_top_whip_cord.py — FreeCAD Solid B-Rep Top Whip Cord & IEC 60309 Plug
# 1:1 REPLIKASI DETAIL OPENSCAD (sub_top_whip_cord.scad)
# Termasuk:
#  - Internal power terminal block dengan 3x brass clamps & 3x Torx clamp screws
#  - Silkscreen "L", "N", "PE"
#  - Mounting bracket dengan 4 standoffs ke top cap, wire saddle, & 4x M3 vertical Torx screws
#  - Cable Gland M25 dengan 3 thread rings & 32 mm AF Hex Nut
#  - Strain-relief boot (mengerucut 24 -> 20 mm)
#  - Kabel karet Ø20 mm
#  - Steker IEC 60309 32A 2P+E (Biru 230V) dengan locking ring & 3 pin kuningan
# =====================================================================
import FreeCAD as App
import Part
from ._common import (
    V, P, box, cbox, cyl, cone, hex_prism, torx_screw, torx_screw_csk,
    make_text_solid, terminal_bracket_pts,
    PLUG_BLUE, METAL_STEEL, BRASS_GOLD, GSPE_CREAM
)

GLAND_COLLAR_D = 26.0
GLAND_COLLAR_H = 4.0
GLAND_HEX_AF   = 32.0
GLAND_HEX_H    = 12.0
BOOT_D_BOT     = 24.0
BOOT_D_TOP     = 20.0
BOOT_H         = 22.0
CORD_DIA       = 20.0

PLUG_DIA      = 56.0
PLUG_LEN      = 90.0
PLUG_RING_DIA = 62.0
PLUG_RING_H   = 14.0

def build_top_whip_cord(parts, prefix="Whip", cord_len=500.0, top_z=1829.0,
                        explode=0.0, doc=None, show_power_entry=True, show_whip=True):
    e = explode
    entry_ey = 110.0 * e
    whip_ey  = 200.0 * e

    pts_bracket = terminal_bracket_pts()

    # 1. Internal Power Terminal Block (Di bawah top cap)
    if show_power_entry:
        # Enclosure isolator hitam 40x24x30 mm
        block = cbox(40.0, 24.0, 30.0, 0.0, 0.0, top_z - 54.0 + entry_ey)
        for x in [-13.0, 0.0, 13.0]:
            bore = cyl(7.0, 13.0, x, -12.1, top_z - 54.0 + entry_ey, dirv=(0, 1, 0))
            block = block.cut(bore)
        P(parts, f"{prefix}_TerminalBlockHousing", block, (0.145, 0.176, 0.208))

        # 3x Brass Clamp Blocks & Torx Clamp Screws
        clamps = []
        c_screws = []
        conductors = []
        wire_colors = [(0.463, 0.325, 0.227), (0.129, 0.467, 0.675), (0.365, 0.580, 0.220)] # L (Brown), N (Blue), PE (Green)
        for idx, x in enumerate([-13.0, 0.0, 13.0]):
            cl = cbox(8.0, 3.0, 20.0, x, -2.0, top_z - 54.0 + entry_ey)
            clamps.append(cl)

            sc = torx_screw(head_d=5.4, shaft_d=2.8, length=9.0,
                            x=x, y=-13.0, z=top_z - 47.0 + entry_ey, dirv=(0, 1, 0))
            c_screws.append(sc)

            wire = cyl(4.5, 30.0, x, 0.0, top_z - 37.0 + entry_ey, dirv=(0, 0, 1))
            P(parts, f"{prefix}_InternalWire_{['L','N','PE'][idx]}", wire, wire_colors[idx])

        all_clamps = clamps[0].fuse(clamps[1:])
        all_c_screws = c_screws[0].fuse(c_screws[1:])
        P(parts, f"{prefix}_TerminalClamps", all_clamps, BRASS_GOLD)
        P(parts, f"{prefix}_TerminalClampScrews", all_c_screws, METAL_STEEL)

        # Silkscreen "L", "N", "PE"
        if doc is not None:
            t_l = make_text_solid("L", 2.8, 0.15, -13.0, -12.05, top_z - 63.0 + entry_ey, doc=doc)
            t_n = make_text_solid("N", 2.8, 0.15, 0.0, -12.05, top_z - 63.0 + entry_ey, doc=doc)
            t_pe = make_text_solid("PE", 2.8, 0.15, 13.0, -12.05, top_z - 63.0 + entry_ey, doc=doc)
            P(parts, f"{prefix}_SilkL", t_l, GSPE_CREAM)
            P(parts, f"{prefix}_SilkN", t_n, GSPE_CREAM)
            P(parts, f"{prefix}_SilkPE", t_pe, GSPE_CREAM)

        # 2. Mounting Bracket & Standoffs ke Top Cap
        b_plate = cbox(44.0, 26.0, 3.0, 0.0, 0.0, top_z - 38.0 + entry_ey)
        standoffs = [cyl(6.0, 33.0, p[0], p[1], top_z - 36.0 + entry_ey, dirv=(0, 0, 1)) for p in pts_bracket]
        center_bosses = [cyl(4.0, 10.0, x, 0.0, top_z - 36.0 + entry_ey, dirv=(0, 0, 1)) for x in [-12.0, 12.0]]
        bracket = b_plate.fuse(standoffs + center_bosses)

        for p in pts_bracket:
            bhole = cyl(2.2, 11.0, p[0], p[1], top_z - 13.5 + entry_ey, dirv=(0, 0, 1))
            bracket = bracket.cut(bhole)
        for x in [-13.0, 0.0, 13.0]:
            pass_hole = cyl(5.0, 4.0, x, 0.0, top_z - 38.0 + entry_ey, dirv=(0, 0, 1))
            bracket = bracket.cut(pass_hole)

        P(parts, f"{prefix}_TerminalBracket", bracket, (0.227, 0.255, 0.286))

        # Wire Saddle
        saddle = cbox(30.0, 16.0, 6.0, 0.0, 0.0, top_z - 23.0 + entry_ey)
        for x in [-13.0, 0.0, 13.0]:
            shole = cyl(5.2, 7.0, x, 0.0, top_z - 23.0 + entry_ey, dirv=(0, 0, 1))
            saddle = saddle.cut(shole)
        P(parts, f"{prefix}_WireSaddle", saddle, (0.145, 0.176, 0.208))

        # 4x M3 Baut Countersunk Vertikal dari Top Cap (arah -Z)
        b_screws = []
        for p in pts_bracket:
            sc = torx_screw_csk(head_d=5.4, shaft_d=2.8, length=4.0,
                                x=p[0], y=p[1], z=top_z, dirv=(0, 0, -1))
            b_screws.append(sc)
        all_b_screws = b_screws[0].fuse(b_screws[1:])
        P(parts, f"{prefix}_BracketTorxScrews", all_b_screws, METAL_STEEL)

    # 3. Cable Gland M25, Cord & Plug IEC 60309
    if show_whip:
        z0 = top_z + whip_ey
        # Collar & Thread rings
        g_collar = cyl(GLAND_COLLAR_D, GLAND_COLLAR_H, 0.0, 0.0, z0, dirv=(0, 0, 1))
        rings = [cyl(GLAND_COLLAR_D + 1.0, 0.9, 0.0, 0.0, z0 + GLAND_COLLAR_H + i * 1.4, dirv=(0, 0, 1)) for i in range(3)]
        all_rings = rings[0].fuse(rings[1:])
        gland_base = g_collar.fuse(all_rings)

        # Hex Nut 32 mm AF
        g_hex = hex_prism(GLAND_HEX_AF, GLAND_HEX_H, 0.0, 0.0, z0 + GLAND_COLLAR_H + 4.6, dirv=(0, 0, 1))
        gland = gland_base.fuse(g_hex)
        P(parts, f"{prefix}_CableGland", gland, (0.118, 0.133, 0.176))

        # Strain-relief boot (mengerucut 24 -> 20 mm)
        z_boot = z0 + GLAND_COLLAR_H + 4.6 + GLAND_HEX_H
        boot = cone(BOOT_D_BOT, BOOT_D_TOP, BOOT_H, 0.0, 0.0, z_boot, dirv=(0, 0, 1))
        P(parts, f"{prefix}_StrainReliefBoot", boot, (0.045, 0.050, 0.058))

        # Kabel karet Ø20 mm
        z_cord = z_boot + BOOT_H
        cord = cyl(CORD_DIA, cord_len, 0.0, 0.0, z_cord, dirv=(0, 0, 1))
        P(parts, f"{prefix}_RubberCord", cord, (0.045, 0.050, 0.058))

        # Steker Industri IEC 60309 32A 2P+E (Biru)
        z_plug = z_cord + cord_len
        p_collar = cone(CORD_DIA + 3.0, PLUG_DIA, 16.0, 0.0, 0.0, z_plug, dirv=(0, 0, 1))
        p_barrel = cyl(PLUG_DIA, PLUG_LEN - PLUG_RING_H - 16.0, 0.0, 0.0, z_plug + 16.0, dirv=(0, 0, 1))
        plug_body = p_collar.fuse(p_barrel)
        P(parts, f"{prefix}_IECPlugBody", plug_body, PLUG_BLUE)

        # Locking Ring & Muka Plug
        p_ring = cyl(PLUG_RING_DIA, PLUG_RING_H, 0.0, 0.0, z_plug + PLUG_LEN - PLUG_RING_H, dirv=(0, 0, 1))
        p_face = cyl(PLUG_DIA - 6.0, 4.0, 0.0, 0.0, z_plug + PLUG_LEN, dirv=(0, 0, 1))
        plug_ring = p_ring.fuse(p_face)
        P(parts, f"{prefix}_IECPlugRing", plug_ring, (0.100, 0.350, 0.580))

        # 3 Pin Kuningan (PE di jam 6 Ø6 mm panjang 24 mm; L & N di jam 10 & 2 Ø5 mm panjang 20 mm)
        pin_pe = cyl(6.0, 24.0, 0.0, -17.0, z_plug + PLUG_LEN + 4.0, dirv=(0, 0, 1))
        pin_l = cyl(5.0, 20.0, -17.0 * 0.866, 17.0 * 0.5, z_plug + PLUG_LEN + 4.0, dirv=(0, 0, 1))
        pin_n = cyl(5.0, 20.0,  17.0 * 0.866, 17.0 * 0.5, z_plug + PLUG_LEN + 4.0, dirv=(0, 0, 1))
        pins = pin_pe.fuse([pin_l, pin_n])
        P(parts, f"{prefix}_IECPlugPins", pins, BRASS_GOLD)
