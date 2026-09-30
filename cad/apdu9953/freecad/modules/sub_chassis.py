# =====================================================================
# sub_chassis.py — FreeCAD Solid B-Rep Main Chassis & End Caps
# 1:1 REPLIKASI DETAIL OPENSCAD (sub_chassis.scad & pdu_apdu9953_assembly.scad)
# Termasuk:
#  - Extruded hollow body 1829x56x46 mm plat 1.5 mm fillet R2
#  - Front zone cutouts (3x Banks, NMC3, 2x Breakers)
#  - Rear mounting holes (12x bank carrier, 4x breaker retainer, 4x NMC tray,
#    2x top cap return lip, 1x ground stud)
#  - Side holes & 16x pressed brass threaded inserts
#  - Bottom end cap & Top end cap (3 mm) dengan gland hole & terminal bracket holes
#  - Top cap rear return lip dengan 2x M3 Torx countersunk screws
#  - 3D Branding Plate di leher (Z = 1560) dengan frame & 3D text (GSPE, APDU9953, dll.)
#  - 3D Rating Plate di dasar (Z = 110) dengan frame & spesifikasi elektrikal
# =====================================================================
import FreeCAD as App
import Part
from ._common import (
    V, P, box, cbox, cyl, rounded_prism_z, torx_screw_csk,
    threaded_insert, make_text_solid,
    LAYOUT_H, LAYOUT_BANK_Z, LAYOUT_BRK_Z, LAYOUT_NMC_Z,
    bank_carrier_pts, brk_retainer_pts, nmc_tray_pts, fascia_side_z,
    terminal_bracket_pts,
    GSPE_NAVY, GSPE_CREAM, CHASSIS_DARK, METAL_STEEL, BRASS_GOLD
)

CHASSIS_H    = LAYOUT_H
CHASSIS_W    = 56.0
CHASSIS_D    = 46.0
CHASSIS_WALL = 1.5
CHASSIS_R    = 2.0
CAP_T        = 3.0
GLAND_HOLE_D = 23.0

CHASSIS_FRONT_ZONES = [
    (LAYOUT_BANK_Z[0], 241.0, 52.5), # Bank 1
    (LAYOUT_NMC_Z,      211.0, 52.5), # NMC3 Controller
    (LAYOUT_BANK_Z[1], 241.0, 52.5), # Bank 2
    (LAYOUT_BANK_Z[2], 241.0, 52.5), # Bank 3
    (LAYOUT_BRK_Z[0],   38.0, 37.0), # Breaker 1
    (LAYOUT_BRK_Z[1],   38.0, 37.0), # Breaker 2
]

def build_chassis(parts, prefix="Chassis", explode=0.0, doc=None,
                  show_housing=True, show_front_cover=True):
    if not show_housing:
        return

    e = explode
    chassis_ey = 200.0 * e
    rear_y = CHASSIS_D / 2.0 + chassis_ey
    front_y = -CHASSIS_D / 2.0 + chassis_ey

    # 1. Badan Ekstrusi Tabung Berongga (1829 x 56 x 46 mm)
    outer = rounded_prism_z(CHASSIS_W, CHASSIS_D, CHASSIS_R, CHASSIS_H, z0=0.0)
    inner = rounded_prism_z(CHASSIS_W - 2 * CHASSIS_WALL, CHASSIS_D - 2 * CHASSIS_WALL,
                            max(CHASSIS_R - CHASSIS_WALL, 0.2), CHASSIS_H + 2.0, z0=-1.0)
    body = outer.cut(inner)

    # Detachable front channel jika cover dibuka
    if not show_front_cover:
        f_open = box(CHASSIS_W + 2.0, CHASSIS_WALL + 2.0, CHASSIS_H + 2.0,
                     -(CHASSIS_W + 2.0) / 2.0, -CHASSIS_D / 2.0 - 1.0, -1.0)
        body = body.cut(f_open)

    # Front zone cutouts
    for zc, zh, zw in CHASSIS_FRONT_ZONES:
        cut = box(zw, CHASSIS_WALL + 2.0, zh,
                  -zw / 2.0, -CHASSIS_D / 2.0 - 1.0, zc - zh / 2.0)
        body = body.cut(cut)

    # Breaker screw clearance holes di front face
    for zc in LAYOUT_BRK_Z:
        for x in [-19.0, 19.0]:
            for dz in [-28.5, 28.5]:
                bh = cyl(3.1, CHASSIS_WALL + 2.0, x, -CHASSIS_D / 2.0 - 1.0, zc + dz, dirv=(0, 1, 0))
                body = body.cut(bh)

    # Rear mounting holes
    rear_pts = [p for zc in LAYOUT_BANK_Z for p in bank_carrier_pts(zc)]
    rear_pts += [p for zc in LAYOUT_BRK_Z for p in brk_retainer_pts(zc)]
    rear_pts += nmc_tray_pts(LAYOUT_NMC_Z)

    for px, pz in rear_pts:
        rh = cyl(3.2, CHASSIS_WALL + 2.0, px, CHASSIS_D / 2.0 - CHASSIS_WALL - 1.0, pz, dirv=(0, 1, 0))
        body = body.cut(rh)

    # Top return lip holes (2x di belakang atas)
    for x in [-19.0, 19.0]:
        th = cyl(3.2, CHASSIS_WALL + 2.0, x, CHASSIS_D / 2.0 - CHASSIS_WALL - 1.0, CHASSIS_H - 7.0, dirv=(0, 1, 0))
        body = body.cut(th)

    # Ground stud hole di Z = 150
    gh = cyl(5.2, CHASSIS_WALL + 2.0, 10.0, CHASSIS_D / 2.0 - CHASSIS_WALL - 1.0, 150.0, dirv=(0, 1, 0))
    body = body.cut(gh)

    # Side-wall press holes untuk brass threaded inserts
    side_pts = [z for zc in (LAYOUT_BANK_Z + [LAYOUT_NMC_Z]) for z in fascia_side_z(zc)]
    for z in side_pts:
        for d in [-1, 1]:
            sx = (CHASSIS_W / 2.0 - CHASSIS_WALL - 1.0) if d > 0 else (-CHASSIS_W / 2.0 - 1.0)
            dv = (1, 0, 0)
            sh = cyl(5.05, CHASSIS_WALL + 2.0, sx, -20.0, z, dirv=dv)
            body = body.cut(sh)

    body.translate(V(0.0, chassis_ey, 0.0))
    P(parts, f"{prefix}_ExtrusionBody", body, CHASSIS_DARK)

    # 16x Pressed brass threaded inserts di lubang samping
    inserts = []
    for z in side_pts:
        for d in [-1, 1]:
            ins = threaded_insert(dir=d, y=-20.0 + chassis_ey, z=z)
            inserts.append(ins)
    all_inserts = inserts[0].fuse(inserts[1:])
    P(parts, f"{prefix}_ThreadedInserts", all_inserts, BRASS_GOLD)

    # 2. Bottom End Plate (Z = 0)
    bot_cap = rounded_prism_z(CHASSIS_W - 0.6, CHASSIS_D - 0.6,
                              max(CHASSIS_R - 0.3, 0.2), CAP_T, z0=0.0)
    bot_cap.translate(V(0.0, chassis_ey, 0.0))
    P(parts, f"{prefix}_BottomCap", bot_cap, (0.118, 0.133, 0.176))

    # 3. Top End Plate (Z = CHASSIS_H - CAP_T)
    top_cap = rounded_prism_z(CHASSIS_W - 0.6, CHASSIS_D - 0.6,
                              max(CHASSIS_R - 0.3, 0.2), CAP_T, z0=CHASSIS_H - CAP_T)
    # Lubang cable gland Ø23 mm
    gland_h = cyl(GLAND_HOLE_D, CAP_T + 2.0, 0.0, 0.0, CHASSIS_H - CAP_T - 1.0, dirv=(0, 0, 1))
    top_cap = top_cap.cut(gland_h)

    # 4 lubang baut terminal block bracket
    for px, py in terminal_bracket_pts():
        tbh = cyl(3.2, CAP_T + 2.0, px, py, CHASSIS_H - CAP_T - 1.0, dirv=(0, 0, 1))
        top_cap = top_cap.cut(tbh)

    top_cap.translate(V(0.0, chassis_ey, 0.0))
    P(parts, f"{prefix}_TopCap", top_cap, (0.118, 0.133, 0.176))

    # Rear return lip pada top cap & 2x Torx countersunk screws
    lip = box(46.0, 1.2, 7.0, -23.0, CHASSIS_D / 2.0 - CHASSIS_WALL - 1.2, CHASSIS_H - 7.0)
    for x in [-19.0, 19.0]:
        lh = cyl(3.2, 5.0, x, CHASSIS_D / 2.0 - 2.0, CHASSIS_H - 7.0, dirv=(0, 1, 0))
        lip = lip.cut(lh)
    lip.translate(V(0.0, chassis_ey, 0.0))
    P(parts, f"{prefix}_TopCapReturnLip", lip, (0.118, 0.133, 0.176))

    top_screws = []
    for x in [-19.0, 19.0]:
        sc = torx_screw_csk(head_d=6.0, shaft_d=2.8, length=4.0,
                            x=x, y=rear_y + 0.12, z=CHASSIS_H - 7.0, dirv=(0, -1, 0))
        top_screws.append(sc)
    all_top_screws = top_screws[0].fuse(top_screws[1])
    P(parts, f"{prefix}_TopCapTorxScrews", all_top_screws, METAL_STEEL)

    # 4. Plat Branding GSPE di Leher Atas (Z = 1560)
    plate_ey = -12.0 * e
    if show_front_cover:
        brand_base = cbox(44.0, 0.8, 120.0, 0.0, front_y - 0.8 + plate_ey, 1560.0)
        P(parts, f"{prefix}_BrandingPlate_Base", brand_base, GSPE_NAVY)

        frame_outer = cbox(42.0, 0.25, 118.0, 0.0, front_y - 1.22 + plate_ey, 1560.0)
        frame_inner = cbox(40.4, 0.5, 116.4, 0.0, front_y - 1.22 + plate_ey, 1560.0)
        brand_frame = frame_outer.cut(frame_inner)
        P(parts, f"{prefix}_BrandingPlate_Frame", brand_frame, GSPE_CREAM)

        if doc is not None:
            tb_gspe = make_text_solid("GSPE", 8.5, 0.35, 0.0, front_y - 1.25 + plate_ey, 1602.0, doc=doc)
            tb_div1 = cbox(32.0, 0.35, 0.8, 0.0, front_y - 1.25 + plate_ey, 1592.0)
            tb_sku  = make_text_solid("APDU9953", 4.2, 0.35, 0.0, front_y - 1.25 + plate_ey, 1582.0, doc=doc)
            tb_ns   = make_text_solid("NETSHELTER", 3.0, 0.35, 0.0, front_y - 1.25 + plate_ey, 1570.0, doc=doc)
            tb_9k   = make_text_solid("9000 SERIES", 3.0, 0.35, 0.0, front_y - 1.25 + plate_ey, 1563.0, doc=doc)
            tb_sw   = make_text_solid("SWITCHED PDU", 2.6, 0.35, 0.0, front_y - 1.25 + plate_ey, 1555.0, doc=doc)
            tb_div2 = cbox(28.0, 0.35, 0.6, 0.0, front_y - 1.25 + plate_ey, 1545.0)
            tb_pwr  = make_text_solid("230 V - 32 A", 3.2, 0.35, 0.0, front_y - 1.25 + plate_ey, 1536.0, doc=doc)
            tb_hz   = make_text_solid("50/60 Hz 1-PHASE", 2.2, 0.35, 0.0, front_y - 1.25 + plate_ey, 1528.0, doc=doc)
            tb_cap  = make_text_solid("7.36 kW CAPACITY", 2.5, 0.35, 0.0, front_y - 1.25 + plate_ey, 1518.0, doc=doc)

            all_brand_txt = tb_gspe.fuse([tb_div1, tb_sku, tb_ns, tb_9k, tb_sw, tb_div2, tb_pwr, tb_hz, tb_cap])
            P(parts, f"{prefix}_BrandingPlate_Text", all_brand_txt, GSPE_CREAM)

        # 5. Label Rating di Dasar Bodi (Z = 110)
        rate_base = cbox(44.0, 0.8, 68.0, 0.0, front_y - 0.8 + plate_ey, 110.0)
        P(parts, f"{prefix}_RatingPlate_Base", rate_base, GSPE_NAVY)

        rframe_outer = cbox(41.6, 0.25, 65.6, 0.0, front_y - 1.22 + plate_ey, 110.0)
        rframe_inner = cbox(40.2, 0.5, 64.2, 0.0, front_y - 1.22 + plate_ey, 110.0)
        rate_frame = rframe_outer.cut(rframe_inner)
        P(parts, f"{prefix}_RatingPlate_Frame", rate_frame, GSPE_CREAM)

        if doc is not None:
            tr_title = make_text_solid("GSPE RACK PDU", 3.2, 0.35, 0.0, front_y - 1.25 + plate_ey, 134.0, doc=doc)
            tr_model = make_text_solid("MODEL: APDU9953", 2.4, 0.35, 0.0, front_y - 1.25 + plate_ey, 127.0, doc=doc)
            tr_div1  = cbox(36.0, 0.35, 0.5, 0.0, front_y - 1.25 + plate_ey, 122.0)
            tr_in    = make_text_solid("INPUT: 200-240V ~ 32A", 2.2, 0.35, 0.0, front_y - 1.25 + plate_ey, 116.0, doc=doc)
            tr_out   = make_text_solid("OUTPUT: 24 OUTLETS", 2.2, 0.35, 0.0, front_y - 1.25 + plate_ey, 110.0, doc=doc)
            tr_cfg   = make_text_solid("21x C13/C15 - 3x C19/C21", 1.9, 0.35, 0.0, front_y - 1.25 + plate_ey, 104.0, doc=doc)
            tr_plug  = make_text_solid("PLUG: IEC 60309 32A 2P+E", 1.9, 0.35, 0.0, front_y - 1.25 + plate_ey, 98.0, doc=doc)
            tr_div2  = cbox(36.0, 0.35, 0.5, 0.0, front_y - 1.25 + plate_ey, 93.0)
            tr_cert  = make_text_solid("CE - RoHS - IP20", 2.2, 0.35, 0.0, front_y - 1.25 + plate_ey, 87.0, doc=doc)

            all_rate_txt = tr_title.fuse([tr_model, tr_div1, tr_in, tr_out, tr_cfg, tr_plug, tr_div2, tr_cert])
            P(parts, f"{prefix}_RatingPlate_Text", all_rate_txt, GSPE_CREAM)
