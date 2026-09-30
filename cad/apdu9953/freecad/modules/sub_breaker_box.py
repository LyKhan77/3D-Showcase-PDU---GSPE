# =====================================================================
# sub_breaker_box.py — FreeCAD Solid B-Rep Hydraulic-Magnetic Circuit Breaker
# 1:1 REPLIKASI DETAIL OPENSCAD (sub_breaker_box.scad)
# Termasuk:
#  - Fascia plat hitam 48x70 mm dengan 4x Torx T15 screws
#  - Silkscreen "Bank 1" / "Bank 2" warna Cream
#  - Raised barrier guard wings dengan rounded ears & crossbars
#  - Stepped cylindrical rocker toggle dengan concave finger scoop & 3D text ("20", "ON", "OFF")
#  - Bakelite body dengan heat ribs & terminal pockets
#  - Rear retainer plate clamping body ke rear wall
#  - 2x M3 Rear retainer countersunk Torx screws
#  - 2x Copper terminal lugs dengan vertical Torx clamp screws
# =====================================================================
import FreeCAD as App
import Part
from ._common import (
    V, P, box, cbox, cyl, rounded_prism_y, torx_screw, torx_screw_csk,
    make_text_solid, brk_retainer_pts,
    GSPE_CREAM, METAL_STEEL, COPPER, BAKELITE_BLK
)

def build_breaker_box(parts, prefix, bank_label, center_z, front_y=-23.0,
                      explode=0.0, doc=None, show_housing=True,
                      show_fascia_external=True, show_internals=True,
                      show_front_cover=True):
    e = explode
    fascia_ey = -12.0 * e
    guard_ey  = -24.0 * e
    rocker_ey = -43.0 * e
    screw_ey  = -65.0 * e
    body_ey   =  15.0 * e
    lug_ey    =  60.0 * e

    # 1. Breaker Fascia & 4x Torx Screws
    if show_housing and show_front_cover:
        fascia = rounded_prism_y(48.0, 70.0, 1.5, 2.8, y0=front_y - 2.8 + fascia_ey)
        cutout = rounded_prism_y(22.0, 38.0, 1.5, 3.2, y0=front_y - 3.0 + fascia_ey)
        cutout.translate(V(-7.0, 0.0, 0.0))
        fascia = fascia.cut(cutout)

        for x in [-19.0, 19.0]:
            for z in [-28.5, 28.5]:
                h1 = cyl(3.1, 3.3, x, front_y - 3.0 + fascia_ey, z, dirv=(0, 1, 0))
                h2 = cyl(6.0, 1.55, x, front_y - 2.82 + fascia_ey, z, dirv=(0, 1, 0))
                fascia = fascia.cut(h1).cut(h2)

        fascia.translate(V(0.0, 0.0, center_z))
        P(parts, f"{prefix}_Fascia", fascia, (0.078, 0.090, 0.118)) # #14171E

        # 4x Fascia Torx screws
        screws = []
        for x in [-19.0, 19.0]:
            for z in [-28.5, 28.5]:
                sc = torx_screw(head_d=5.4, shaft_d=2.8, length=6.0,
                                x=x, y=front_y - 2.6 + screw_ey, z=center_z + z,
                                dirv=(0, 1, 0))
                screws.append(sc)
        all_screws = screws[0].fuse(screws[1:])
        P(parts, f"{prefix}_FasciaTorxScrews", all_screws, METAL_STEEL)

        # Silkscreen "Bank 1" / "Bank 2"
        if doc is not None:
            t_label = make_text_solid(bank_label, 4.5, 0.2, 16.8,
                                      front_y - 2.81 + fascia_ey, center_z,
                                      angle_deg=-90.0, doc=doc)
            P(parts, f"{prefix}_SilkBankLabel", t_label, GSPE_CREAM)

    # 2. Raised Barrier Guard Wings
    if show_fascia_external:
        guards = []
        for x in [-18.0, 4.0]:
            vbar = cbox(2.8, 2.6, 38.0, x, front_y - 4.1 + guard_ey, center_z)
            ear_t = cyl(8.0, 2.8, x - 1.4, front_y - 8.0 + guard_ey, center_z + 15.0, dirv=(1, 0, 0))
            ear_b = cyl(8.0, 2.8, x - 1.4, front_y - 8.0 + guard_ey, center_z - 15.0, dirv=(1, 0, 0))
            wing = vbar.fuse([ear_t, ear_b])
            guards.append(wing)

        cbar_t = cbox(23.0, 2.8, 2.0, -7.0, front_y - 4.2 + guard_ey, center_z + 18.0)
        cbar_b = cbox(23.0, 2.8, 2.0, -7.0, front_y - 4.2 + guard_ey, center_z - 18.0)
        guard = guards[0].fuse([guards[1], cbar_t, cbar_b])
        P(parts, f"{prefix}_Guard", guard, (0.161, 0.176, 0.196)) # #292D32

        # 3. Breaker Rocker Toggle dengan Concave Finger Scoop
        c = cyl(38.0, 17.0, -15.5, front_y + 9.5 + rocker_ey, center_z + 1.0, dirv=(1, 0, 0))
        c = c.cut(box(25.0, 30.0, 50.0, -19.5, front_y + 1.5 + rocker_ey, center_z - 25.0))
        c = c.cut(box(25.0, 30.0, 50.0, -19.5, front_y - 40.5 + rocker_ey, center_z - 25.0))
        c = c.cut(box(25.0, 50.0, 30.0, -19.5, front_y - 25.0 + rocker_ey, center_z + 16.0))
        c = c.cut(box(25.0, 50.0, 30.0, -19.5, front_y - 25.0 + rocker_ey, center_z - 44.0))

        scoop = cyl(26.0, 25.0, -19.5, front_y - 20.0 + rocker_ey, center_z + 7.0, dirv=(1, 0, 0))
        c = c.cut(scoop)

        step = cbox(17.0, 7.0, 5.0, -7.0, front_y - 6.0 + rocker_ey, center_z - 12.0)
        rocker = c.fuse(step)
        P(parts, f"{prefix}_Rocker", rocker, (0.216, 0.231, 0.251)) # #373B40

        # Teks 3D pada rocker: "20", "ON", "OFF"
        if doc is not None:
            t_20 = make_text_solid("20", 3.2, 0.2, -7.0, front_y - 9.51 + rocker_ey, center_z - 12.0, doc=doc)
            t_on = make_text_solid("ON", 1.6, 0.15, -7.0, front_y - 8.5 + rocker_ey, center_z + 3.0, doc=doc)
            t_off = make_text_solid("OFF", 1.45, 0.15, -7.0, front_y - 8.0 + rocker_ey, center_z + 11.0, doc=doc)
            P(parts, f"{prefix}_Silk20", t_20, (0.957, 0.957, 0.949))
            P(parts, f"{prefix}_SilkON", t_on, (0.957, 0.957, 0.949))
            P(parts, f"{prefix}_SilkOFF", t_off, (0.957, 0.957, 0.949))

    # 4. Bakelite Body, Retainer Plate & Screws
    if show_internals:
        # Body bakelite hitam
        body = cbox(20.0, 36.8, 35.0, -7.0, front_y + 18.6 + body_ey, center_z)
        flange = cbox(22.0, 1.0, 38.0, -7.0, front_y + 0.5 + body_ey, center_z)
        body = body.fuse(flange)

        for z in [-10.0, 10.0]:
            pock = cbox(9.5, 4.5, 9.5, -7.0, front_y + 35.4 + body_ey, center_z + z)
            body = body.cut(pock)

        # Heat ribs
        for y in [6.0, 15.0, 24.0]:
            rib = cbox(20.6, 0.8, 34.0, -7.0, front_y + y + body_ey, center_z)
            body = body.fuse(rib)

        P(parts, f"{prefix}_BakeliteBody", body, BAKELITE_BLK)

        # Rear Retainer Plate
        ret = cbox(22.0, 2.0, 38.0, -7.0, front_y + 38.0 + body_ey, center_z)
        for z in [-10.0, 10.0]:
            pock = cbox(9.5, 2.6, 9.5, -7.0, front_y + 38.0 + body_ey, center_z + z)
            ret = ret.cut(pock)
        P(parts, f"{prefix}_RetainerPlate", ret, (0.227, 0.255, 0.286))

        # 2x Retainer Torx Countersunk Screws dari belakang
        ret_screws = []
        for dz in [-14.0, 14.0]:
            sc = torx_screw_csk(head_d=6.0, shaft_d=2.8, length=7.0,
                                x=-7.0, y=front_y + 46.5, z=center_z + dz,
                                dirv=(0, -1, 0))
            ret_screws.append(sc)
        all_ret_screws = ret_screws[0].fuse(ret_screws[1])
        P(parts, f"{prefix}_RetainerTorxScrews", all_ret_screws, METAL_STEEL)

        # 2x Copper Terminal Lugs dengan Vertical Torx Clamp Screws
        lugs = []
        clamp_screws = []
        for dz in [-10.0, 10.0]:
            lz = center_z + dz
            lug = cbox(8.0, 3.0, 7.0, -7.0, front_y + 36.3 + lug_ey, lz)
            lbore = cyl(2.8, 4.0, -7.0, front_y + 34.5 + lug_ey, lz, dirv=(0, 1, 0))
            lug = lug.cut(lbore)
            lugs.append(lug)

            # Clamp screw vertikal dari atas/bawah
            dv = (0, 0, -1) if dz > 0 else (0, 0, 1)
            sz = lz + (3.5 if dz > 0 else -3.5)
            csc = torx_screw(head_d=4.5, shaft_d=2.4, length=3.0,
                             x=-7.0, y=front_y + 36.3 + lug_ey, z=sz, dirv=dv)
            clamp_screws.append(csc)

        all_lugs = lugs[0].fuse(lugs[1])
        all_clamp_screws = clamp_screws[0].fuse(clamp_screws[1])
        P(parts, f"{prefix}_TerminalLugs", all_lugs, COPPER)
        P(parts, f"{prefix}_LugTorxScrews", all_clamp_screws, METAL_STEEL)
