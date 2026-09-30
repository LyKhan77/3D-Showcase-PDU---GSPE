# =====================================================================
# sub_socket_bank.py — FreeCAD Solid B-Rep Socket Bank Assembly
# 1:1 REPLIKASI DETAIL OPENSCAD (sub_socket_bank.scad)
# Termasuk:
#  - Bank Fascia 57.4 mm dengan wrap-around side flanges & 8 socket cutouts
#  - Guide stripes & guide arrow triangle
#  - Silkscreen "Bank 1/2/3"
#  - 4x Side Torx T15 countersunk screws
#  - Continuous copper busbars (N & PE) dengan solder tabs & teks "N", "PE"
#  - Rear carrier plate 49x2x236 mm dengan standoff bosses & mounting holes
#  - 4x M3 Rear carrier countersunk Torx screws
#  - 2x Nylon insulator saddles & mounting screws
#  - FR-4 Green Relay Board 46x1.6x236 mm dengan 8x Power Relays (K1..K8),
#    filter capacitors, ribbon connector dengan gold pins, silkscreen "GSPE SW8 / B{id}"
#  - 4x M2.5 Relay Board Torx screws
# =====================================================================
import FreeCAD as App
import Part
from ._common import (
    V, P, box, cbox, cyl, rounded_prism_y, torx_screw, torx_screw_csk,
    side_torx_screw, make_text_solid, bank_carrier_pts, bank_relay_pts,
    GSPE_CREAM, POLY_DARK, METAL_STEEL, COPPER, BRASS_GOLD, PCB_GREEN,
    NYLON_WHITE, CHASSIS_DARK
)
from .sub_socket_c13_c15 import build_socket_c13_c15
from .sub_socket_c19_c21 import build_socket_c19_c21

def bank_socket_z(i):
    return 104.0 - i * 28.5 if i < 7 else -99.0

def build_socket_bank(parts, prefix, bank_id, center_z, front_y=-23.0,
                      explode=0.0, doc=None, show_housing=True,
                      show_fascia_external=True, show_internals=True,
                      show_front_cover=True, show_busbars=True):
    e = explode
    fascia_ey   = -12.0 * e
    busbar_ey   =  70.0 * e
    pcb_ey      = 110.0 * e

    pts_carrier = bank_carrier_pts(0.0)
    pts_relay   = bank_relay_pts(0.0)

    # 1. Bank Fascia (Wrap-around plate dengan side flanges)
    if show_housing and show_front_cover:
        # Plat muka 57.4 x 1.5 x 244 mm
        f_plate = cbox(57.4, 1.5, 244.0, 0.0, front_y - 0.65 + fascia_ey, center_z)
        # Side flanges
        flange_l = cbox(1.5, 4.5, 244.0, -28.75, front_y + 3.75 + fascia_ey, center_z)
        flange_r = cbox(1.5, 4.5, 244.0,  28.75, front_y + 3.75 + fascia_ey, center_z)
        fascia = f_plate.fuse([flange_l, flange_r])

        # Cutout untuk 8 soket
        for i in range(8):
            sz = center_z + bank_socket_z(i)
            cw = 40.0 if i == 7 else 30.0
            ch = 26.0 if i == 7 else 22.0
            scut = rounded_prism_y(cw, ch, 1.4, 2.5, y0=front_y - 1.5 + fascia_ey)
            scut.translate(V(0, 0, sz))
            fascia = fascia.cut(scut)

            # Lubang LED & pinhole
            ind_z = sz + (16.2 if i == 7 else 14.2)
            led_hole = cyl(1.8, 2.5, 0.0, front_y - 1.5 + fascia_ey, ind_z, dirv=(0, 1, 0))
            pin_hole = cyl(0.85, 2.5, -3.5, front_y - 1.5 + fascia_ey, ind_z, dirv=(0, 1, 0))
            fascia = fascia.cut(led_hole).cut(pin_hole)

            # Snap-fit latch arm slots
            edge = 12.0 if i == 7 else 10.0
            slot1 = cbox(4.0, 2.5, 1.75, 0.0, front_y - 0.65 + fascia_ey, sz + edge + 0.875)
            slot2 = cbox(4.0, 2.5, 1.75, 0.0, front_y - 0.65 + fascia_ey, sz - edge - 0.875)
            fascia = fascia.cut(slot1).cut(slot2)

        # 4 lubang countersunk baut samping (axis X)
        for d in [-1, 1]:
            for dz in [-100.0, 100.0]:
                sx = 28.75 if d > 0 else -28.75
                dv = (-1, 0, 0) if d > 0 else (1, 0, 0)
                hole_cyl = cyl(3.4, 3.0, sx + (1.5 if d > 0 else -1.5), front_y + 3.0 + fascia_ey, center_z + dz, dirv=dv)
                fascia = fascia.cut(hole_cyl)

        P(parts, f"{prefix}_Fascia", fascia, (0.118, 0.133, 0.176)) # #1E222D

        # Guide stripes & arrow
        gs1 = cbox(0.5, 0.15, 94.0, -25.0, front_y - 1.45 + fascia_ey, center_z - 48.0)
        gs2 = cbox(0.5, 0.15, 94.0, -25.0, front_y - 1.45 + fascia_ey, center_z + 66.0)
        arrow = cbox(3.0, 0.15, 3.5, -25.0, front_y - 1.45 + fascia_ey, center_z + 115.0)
        stripes = gs1.fuse([gs2, arrow])
        P(parts, f"{prefix}_GuideStripes", stripes, (0.957, 0.957, 0.949))

        # Silkscreen "Bank {id}"
        if doc is not None:
            t_bank = make_text_solid(f"Bank {bank_id}", 2.3, 0.15, -24.5,
                                     front_y - 1.51 + fascia_ey, center_z + 8.0,
                                     angle_deg=-90.0, doc=doc)
            P(parts, f"{prefix}_SilkBankLabel", t_bank, GSPE_CREAM)

        # 4x Side Torx screws
        side_screws = []
        for d in [-1, 1]:
            for dz in [-100.0, 100.0]:
                sc = side_torx_screw(dir=d, length=4.5, head_d=5.4, shaft_d=2.8,
                                     y=front_y + 3.0 + fascia_ey, z=center_z + dz)
                side_screws.append(sc)
        all_side_screws = side_screws[0].fuse(side_screws[1:])
        P(parts, f"{prefix}_SideTorxScrews", all_side_screws, METAL_STEEL)

    # 2. 8 Soket Outlet (7x C13/C15 + 1x C19/C21)
    for i in range(7):
        out_num = (bank_id - 1) * 8 + i + 1
        sz = center_z + bank_socket_z(i)
        build_socket_c13_c15(parts, f"{prefix}_Out{out_num}", out_num, sz,
                             front_y=front_y, explode=e, doc=doc,
                             show_number=True,
                             show_fascia_external=show_fascia_external,
                             show_internals=show_internals)

    # Outlet ke-8: C19/C21
    out_num8 = bank_id * 8
    sz8 = center_z + bank_socket_z(7)
    build_socket_c19_c21(parts, f"{prefix}_Out{out_num8}", out_num8, sz8,
                         front_y=front_y, explode=e, doc=doc,
                         show_number=True,
                         show_fascia_external=show_fascia_external,
                         show_internals=show_internals)

    # 3. Busbars Tembaga (N & PE)
    if show_internals and show_busbars:
        bb_list = []
        for x in [-18.0, 18.0]:
            bar = cbox(4.0, 1.8, 225.0, x, front_y + 26.0 + busbar_ey, center_z + 2.5)
            # Lubang clearance terminal
            for i in range(8):
                bcut = cyl(1.8, 2.5, x, front_y + 24.9 + busbar_ey, center_z + bank_socket_z(i), dirv=(0, 1, 0))
                bar = bar.cut(bcut)
            # Solder tabs
            for i in range(8):
                tx = 9.0 if x > 0 else -12.0
                tw = 18.0 if x > 0 else 12.0
                tz = center_z + bank_socket_z(i) + (-4.2 if x > 0 else 2.0)
                tab = cbox(tw, 0.8, 1.3, tx, front_y + 24.0 + busbar_ey, tz)
                bar = bar.fuse(tab)
            bb_list.append(bar)

        busbars = bb_list[0].fuse(bb_list[1])
        P(parts, f"{prefix}_Busbars", busbars, COPPER)

        if doc is not None:
            t_n = make_text_solid("N", 2.5, 0.15, -18.0, front_y + 24.98 + busbar_ey, center_z + 112.0, doc=doc)
            t_pe = make_text_solid("PE", 2.3, 0.15, 18.0, front_y + 24.98 + busbar_ey, center_z + 112.0, doc=doc)
            P(parts, f"{prefix}_SilkBusbarN", t_n, GSPE_CREAM)
            P(parts, f"{prefix}_SilkBusbarPE", t_pe, GSPE_CREAM)

    # 4. Plat Carrier Belakang (Rear Carrier Plate)
    if show_internals:
        c_plate = cbox(49.0, 2.0, 236.0, 0.0, front_y + 41.0, center_z)
        # Bosses untuk standoffs PCB relay
        r_bosses = [cyl(5.0, 4.6, p[0], front_y + 35.4, center_z + p[1], dirv=(0, 1, 0)) for p in pts_relay]
        # Bosses untuk saddle busbar
        s_bosses = [cyl(5.0, 2.2, x, front_y + 42.0, center_z, dirv=(0, 1, 0)) for x in [-24.0, 24.0]]
        carrier = c_plate.fuse(r_bosses + s_bosses)

        # Lubang baut carrier ke chassis rear wall
        for p in pts_carrier:
            hole = cyl(2.4, 2.5, p[0], front_y + 39.9, center_z + p[1], dirv=(0, 1, 0))
            carrier = carrier.cut(hole)
        # Lubang standoff relay
        for p in pts_relay:
            hole = cyl(2.2, 5.0, p[0], front_y + 35.3, center_z + p[1], dirv=(0, 1, 0))
            carrier = carrier.cut(hole)
        # Lubang saddle busbar
        for x in [-24.0, 24.0]:
            hole = cyl(2.4, 5.0, x, front_y + 39.9, center_z, dirv=(0, 1, 0))
            carrier = carrier.cut(hole)

        P(parts, f"{prefix}_CarrierPlate", carrier, (0.290, 0.318, 0.345)) # #4A5158

        # 4x M3 Baut countersunk carrier dari belakang (+Y = 46.5 mm, arah -Y)
        c_screws = []
        for p in pts_carrier:
            sc = torx_screw_csk(head_d=6.0, shaft_d=2.8, length=4.0,
                                x=p[0], y=front_y + 46.5, z=center_z + p[1],
                                dirv=(0, -1, 0))
            c_screws.append(sc)
        all_c_screws = c_screws[0].fuse(c_screws[1:])
        P(parts, f"{prefix}_CarrierTorxScrews", all_c_screws, METAL_STEEL)

        # 5. Busbar Saddles (Nylon insulator saddles)
        saddles = []
        s_screws = []
        for d in [-1, 1]:
            x = d * 24.0
            arm = cbox(2.8, 13.0, 4.0, d * 24.6, front_y + 33.5, center_z)
            clamp = cbox(6.0, 4.2, 6.0, x, front_y + 26.5, center_z)
            saddle = arm.fuse(clamp)
            channel = cbox(3.4, 2.0, 7.0, x, front_y + 26.0, center_z)
            shole = cyl(3.0, 13.0, x, front_y + 27.0, center_z, dirv=(0, 1, 0))
            saddle = saddle.cut(channel).cut(shole)
            saddles.append(saddle)

            ssc = torx_screw(head_d=5.4, shaft_d=2.8, length=4.5,
                             x=x, y=front_y + 38.6, z=center_z, dirv=(0, 1, 0))
            s_screws.append(ssc)

        all_saddles = saddles[0].fuse(saddles[1])
        all_s_screws = s_screws[0].fuse(s_screws[1])
        P(parts, f"{prefix}_BusbarSaddles", all_saddles, NYLON_WHITE)
        P(parts, f"{prefix}_SaddleTorxScrews", all_s_screws, METAL_STEEL)

        # 6. Relay Board PCB (FR-4) dengan Relays & Komponen
        pcb = cbox(46.0, 1.6, 236.0, 0.0, front_y + 36.2 + pcb_ey, center_z)
        for p in pts_relay:
            hole = cyl(2.7, 2.0, p[0], front_y + 35.3 + pcb_ey, center_z + p[1], dirv=(0, 1, 0))
            pcb = pcb.cut(hole)
        P(parts, f"{prefix}_RelayPCB", pcb, PCB_GREEN)

        # 8 Relays (Black box) + Terminal Pins + Caps
        relays = []
        caps = []
        cap_tops = []
        r_pins = []
        for i in range(8):
            rz = center_z + bank_socket_z(i)
            rel = cbox(16.0, 10.2, 14.0, 0.0, front_y + 30.5 + pcb_ey, rz)
            relays.append(rel)

            for x in [-9.0, 9.0]:
                for zz in [-4.0, 4.0]:
                    pin = cbox(2.0, 1.4, 1.0, x, front_y + 34.7 + pcb_ey, rz + zz)
                    r_pins.append(pin)

            # Cap can (Blue) + silver top
            cap_can = cyl(4.0, 6.0, -16.0, front_y + 28.0 + pcb_ey, rz - 6.0, dirv=(0, 1, 0))
            cap_top = cyl(3.2, 0.15, -16.0, front_y + 27.95 + pcb_ey, rz - 6.0, dirv=(0, 1, 0))
            caps.append(cap_can)
            cap_tops.append(cap_top)

            if doc is not None:
                t_k = make_text_solid(f"K{i+1}", 2.2, 0.15, 0.0,
                                      front_y + 25.38 + pcb_ey, rz, doc=doc)
                P(parts, f"{prefix}_SilkK{i+1}", t_k, GSPE_CREAM)

        all_relays = relays[0].fuse(relays[1:])
        all_caps = caps[0].fuse(caps[1:])
        all_cap_tops = cap_tops[0].fuse(cap_tops[1:])
        all_pins = r_pins[0].fuse(r_pins[1:])
        P(parts, f"{prefix}_PowerRelays", all_relays, (0.125, 0.145, 0.173)) # #20252C
        P(parts, f"{prefix}_FilterCapacitors", all_caps, (0.141, 0.247, 0.404)) # #243F67
        P(parts, f"{prefix}_CapacitorTops", all_cap_tops, METAL_STEEL)
        P(parts, f"{prefix}_RelayPins", all_pins, METAL_STEEL)

        # Ribbon Connector & Gold Pins
        r_conn = cbox(18.0, 7.0, 5.0, 10.0, front_y + 30.5 + pcb_ey, center_z + 116.0)
        gold_pins = [cyl(0.6, 8.0, x, front_y + 26.0 + pcb_ey, center_z + 116.0, dirv=(0, 1, 0)) for x in range(3, 18, 2)]
        all_gp = gold_pins[0].fuse(gold_pins[1:])
        P(parts, f"{prefix}_RibbonConnector", r_conn, (0.153, 0.173, 0.192))
        P(parts, f"{prefix}_RibbonGoldPins", all_gp, BRASS_GOLD)

        # Silkscreen GSPE SW8 / B{id}
        if doc is not None:
            t_sw = make_text_solid(f"GSPE  SW8 / B{bank_id}", 1.8, 0.15, 0.0,
                                   front_y + 35.37 + pcb_ey, center_z - 115.0, doc=doc)
            P(parts, f"{prefix}_SilkPCBSW8", t_sw, GSPE_CREAM)

        # 4x M2.5 Baut Standoff Relay Board
        r_screws = []
        for p in pts_relay:
            sc = torx_screw(head_d=4.2, shaft_d=2.4, length=5.0,
                            x=p[0], y=front_y + 35.1 + pcb_ey, z=center_z + p[1],
                            dirv=(0, 1, 0))
            r_screws.append(sc)
        all_r_screws = r_screws[0].fuse(r_screws[1:])
        P(parts, f"{prefix}_RelayTorxScrews", all_r_screws, METAL_STEEL)
