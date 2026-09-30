# =====================================================================
# sub_socket_c13_c15.py — FreeCAD Solid B-Rep Hybrid C13/C15 Combo Outlet
# 1:1 REPLIKASI DETAIL OPENSCAD (sub_socket_c13_c15.scad)
# Termasuk:
#  - Bezel Polyamide 32x24 R1.8 dengan lubang ber-chamfer 28x20
#  - Inti Muka Soket Octagonal 23x17 chamfer 4.0
#  - Top C15 Key Notch (4.2x3.2) + circular notch relief Ø4.2 mm
#  - 3x Slot pin kontak nyata (2.2x5.5 mm)
#  - Indikator LED dome Ø2.2 mm + pinhole optik sensor Ø0.85 mm
#  - Housing internal nilon dengan moat floor 29x21, snap-fit latches & side wings
#  - 3x Folded phosphor-bronze spring contacts dengan rear solder tail
#  - Teks 3D silkscreen nomor outlet (mis. "1", "7")
# =====================================================================
import math
import FreeCAD as App
import Part
from ._common import (
    V, P, box, cbox, cyl, sph, rounded_prism_y, polygon_prism_xz,
    socket_octagon_pts, make_text_solid,
    POLY_DARK, CHASSIS_DARK, LED_WHITE, COPPER, GSPE_CREAM
)

def build_socket_modular(parts, prefix, outlet_num, center_z, front_y=-23.0,
                         large=False, explode=0.0, doc=None, show_number=True,
                         show_fascia_external=True, show_internals=True):
    bezel_ey   = -42.0 * explode
    core_ey    = -27.0 * explode
    ind_ey     = -12.0 * explode
    body_ey    =   8.0 * explode
    contact_ey =  42.0 * explode

    bw = 42.0 if large else 32.0
    bh = 28.0 if large else 24.0
    ow = 36.0 if large else 28.0
    oh = 23.0 if large else 20.0
    och = 4.0

    # 1. Bezel Luar Polyamide
    if show_fascia_external:
        bezel = rounded_prism_y(bw, bh, 1.8, 3.5, y0=front_y - 4.9 + bezel_ey)
        bezel_cut = polygon_prism_xz(socket_octagon_pts(ow, oh, och), 4.0, y0=front_y - 5.1 + bezel_ey)
        bezel.translate(V(0, 0, center_z))
        bezel_cut.translate(V(0, 0, center_z))
        bezel = bezel.cut(bezel_cut)
        P(parts, f"{prefix}_Bezel", bezel, POLY_DARK)

        # 2. Inti Muka Soket Ber-Chamfer (Octagonal Face)
        fw = 32.0 if large else 23.0
        fh = 19.0 if large else 17.0
        fch = 3.5 if large else 4.0
        face = polygon_prism_xz(socket_octagon_pts(fw, fh, fch), 2.76, y0=front_y - 4.25 + core_ey)

        if large:
            # C21 circular notch relief Ø5.0 at Z = +8.8
            c21_relief = cyl(5.0, 3.5, 0, front_y - 4.5 + core_ey, 8.8, dirv=(0, 1, 0))
            face = face.cut(c21_relief)
            # 3 horizontal slots [6.2 x 1.9]
            slot_pts = [(-7.5, 4.0), (7.5, 4.0), (0.0, -5.0)]
            for px, pz in slot_pts:
                slot = cbox(6.2, 4.8, 1.9, px, front_y - 4.4 + 2.4 + core_ey, pz)
                face = face.cut(slot)
        else:
            # C15 notch square + circular relief
            c15_notch = cbox(4.2, 3.5, 3.2, 0, front_y - 4.25 + 1.38 + core_ey, 8.2)
            c15_relief = cyl(4.2, 3.5, 0, front_y - 4.5 + core_ey, 6.6, dirv=(0, 1, 0))
            face = face.cut(c15_notch).cut(c15_relief)
            # 3 vertical slots [2.2 x 5.5]
            slot_pts = [(-6.0, 2.0), (6.0, 2.0), (0.0, -4.2)]
            for px, pz in slot_pts:
                slot = cbox(2.2, 4.8, 5.5, px, front_y - 4.4 + 2.4 + core_ey, pz)
                face = face.cut(slot)

        face.translate(V(0, 0, center_z))
        P(parts, f"{prefix}_CoreFace", face, (0.255, 0.271, 0.290)) # #41454A

        # 3. Indikator LED dome Ø2.2 mm + Pinhole sensor optik Ø0.85 mm
        ind_z = center_z + (16.2 if large else 14.2)
        led_dome = sph(2.2, 0, front_y - 1.52 + ind_ey, ind_z)
        P(parts, f"{prefix}_DomeLED", led_dome, LED_WHITE)

        pinhole = cyl(0.85, 0.5, -3.5, front_y - 1.6 + ind_ey, ind_z, dirv=(0, 1, 0))
        P(parts, f"{prefix}_OpticPinhole", pinhole, CHASSIS_DARK)

        # 4. Housing Soket Internal Nilon
        hw = 38.0 if large else 28.0
        hh = 24.0 if large else 20.0
        hd = 18.0 if large else 16.0
        housing = rounded_prism_y(hw, hh, 1.3, hd, y0=front_y + 0.2 + body_ey)
        cavity = polygon_prism_xz(socket_octagon_pts(hw - 2.0, hh - 2.0, 3.0), hd - 2.0, y0=front_y + 0.1 + body_ey)
        housing = housing.cut(cavity)

        # Through slots in housing
        for px, pz in slot_pts:
            if large:
                tslot = cbox(6.2, hd + 2.0, 1.9, px, front_y + 0.2 + hd / 2 + body_ey, pz)
            else:
                tslot = cbox(2.2, hd + 2.0, 5.5, px, front_y + 0.2 + hd / 2 + body_ey, pz)
            housing = housing.cut(tslot)

        # Recessed moat floor
        mw = 37.0 if large else 29.0
        mh = 24.0 if large else 21.0
        moat = polygon_prism_xz(socket_octagon_pts(mw, mh, 4.0), 1.85, y0=front_y - 1.45 + body_ey)
        for px, pz in slot_pts:
            if large:
                mslot = cbox(6.2, 2.5, 1.9, px, front_y - 1.45 + 1.0 + body_ey, pz)
            else:
                mslot = cbox(2.2, 2.5, 5.5, px, front_y - 1.45 + 1.0 + body_ey, pz)
            moat = moat.cut(mslot)

        housing = housing.fuse(moat)

        # Side latch wings & snap-fit latch arms
        w_l = cbox(1.4, 5.0, 5.0, -(hw / 2 + 0.5), front_y + 5.0 + body_ey, 0)
        w_r = cbox(1.4, 5.0, 5.0, (hw / 2 + 0.5), front_y + 5.0 + body_ey, 0)
        latch_top = cbox(3.2, 2.2, 1.2, 0, front_y + 4.7 + body_ey, hh / 2 - 0.3)
        latch_bot = cbox(3.2, 2.2, 1.2, 0, front_y + 4.7 + body_ey, -(hh / 2 - 0.3))

        housing = housing.fuse([w_l, w_r, latch_top, latch_bot])
        housing.translate(V(0, 0, center_z))
        P(parts, f"{prefix}_InternalHousing", housing, (0.114, 0.133, 0.165)) # #1D222A

        # Silkscreen nomor outlet
        if show_number and doc is not None:
            num_x = -23.5 if large else -20.5
            num_size = 2.6 if large else 2.8
            t_num = make_text_solid(str(outlet_num), num_size, 0.15, num_x,
                                    front_y - 1.52 + ind_ey, center_z, angle_deg=-90.0, doc=doc)
            P(parts, f"{prefix}_SilkNum", t_num, GSPE_CREAM)

    # 5. 3x Klip Kontak Pegas Tembaga/Phosphor-Bronze
    if show_internals:
        clips = []
        for px, pz in slot_pts:
            if large:
                # Rotated 90 deg horizontal contacts
                c_ch1 = cbox(8.0, 0.45, 4.5, px, front_y + 12.0 + contact_ey, pz - 1.0)
                c_ch2 = cbox(8.0, 0.45, 4.5, px, front_y + 12.0 + contact_ey, pz + 1.0)
                c_bridge = cbox(5.0, 0.6, 3.6, px, front_y + 16.0 + contact_ey, pz)
                c_tail = cbox(0.7, 8.2, 1.4, px, front_y + 20.0 + contact_ey, pz)
            else:
                c_ch1 = cbox(0.45, 8.0, 4.5, px - 1.0, front_y + 12.0 + contact_ey, pz)
                c_ch2 = cbox(0.45, 8.0, 4.5, px + 1.0, front_y + 12.0 + contact_ey, pz)
                c_bridge = cbox(3.6, 0.6, 5.0, px, front_y + 16.0 + contact_ey, pz)
                c_tail = cbox(1.4, 8.2, 0.7, px, front_y + 20.0 + contact_ey, pz)
            clip = c_ch1.fuse([c_ch2, c_bridge, c_tail])
            clip.translate(V(0, 0, center_z))
            clips.append(clip)

        all_clips = clips[0].fuse(clips[1:])
        P(parts, f"{prefix}_SpringClips", all_clips, COPPER)

def build_socket_c13_c15(parts, prefix, outlet_num, center_z, front_y=-23.0,
                         explode=0.0, doc=None, show_number=True,
                         show_fascia_external=True, show_internals=True):
    build_socket_modular(parts, prefix, outlet_num, center_z, front_y,
                         large=False, explode=explode, doc=doc, show_number=show_number,
                         show_fascia_external=show_fascia_external, show_internals=show_internals)
