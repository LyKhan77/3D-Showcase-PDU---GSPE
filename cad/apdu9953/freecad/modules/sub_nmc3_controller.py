# =====================================================================
# sub_nmc3_controller.py — FreeCAD Solid B-Rep Network Management Card (NMC3)
# 1:1 REPLIKASI DETAIL OPENSCAD (sub_nmc3_controller.scad)
# Termasuk:
#  - NMC3 Faceplate 57.4 mm dengan wrap-around side flanges & 4 side Torx screws
#  - 3D Silkscreen lengkap (GSPE, NETSHELTER 9000, APDU9953, port labels, status LEDs)
#  - OLED LCD display dengan green header bar ("Phase Info"), menu list, bottom status bar, dan clear lens
#  - 3x Tactile navigation buttons (ring + dome) & reset switch
#  - 4x RJ45 ports (Universal I/O terotasi 180°, Link A/B, Network) dengan stepped aperture, folded shell & contact comb
#  - USB-A Host port dengan 4 gold contact pins & side retention detents
#  - USB Micro-B Console port dengan 5 gold pins
#  - Folded sheet metal shielding tray dengan ventilation louvers & standoff bosses
#  - 4x M3 Rear tray countersunk Torx screws
#  - Main PCB FR-4 dengan SoC + pins, RAM + pins, LAN transformer, 25 MHz crystal,
#    FPC ribbon connector, filter capacitors, silkscreen "GSPE NMC3"
#  - 4x M2.5 Main PCB Torx screws
# =====================================================================
import FreeCAD as App
import Part
from ._common import (
    V, P, box, cbox, cyl, sph, rounded_prism_y, rounded_rect_wire,
    polygon_prism_xz, wire_between, torx_screw, torx_screw_csk,
    side_torx_screw, make_text_solid, nmc_tray_pts, nmc_pcb_pts,
    GSPE_NAVY, GSPE_CREAM, POLY_DARK, METAL_STEEL, COPPER, BRASS_GOLD,
    PCB_GREEN, LCD_SCREEN, LED_GREEN, LED_AMBER, LED_RED, FPC_AMBER
)

NMC_PORT_X = 12.0
NMC_PORT_Z = [10.0, -18.0, -46.0]

def _port_result(features, center, parts=None, prefix="Port"):
    """Keep solids/materials separate in the registry; return a compatible compound."""
    solids = []
    for name, shape, color in features:
        shape.translate(V(*center))
        solids.append(shape)
        if parts is not None:
            P(parts, f"{prefix}_{name}", shape, color)
    return Part.makeCompound(solids)

def _aperture(depth, y0, clearance=0.0):
    outline = [(-6.7, -3), (6.7, -3), (6.7, 7), (3.2, 7),
               (3.2, 8.6), (1.75, 8.6), (1.75, 9.55), (-1.75, 9.55),
               (-1.75, 8.6), (-3.2, 8.6), (-3.2, 7), (-6.7, 7)]
    profile = polygon_prism_xz(outline, depth, y0)
    if clearance:
        # Reference offset(delta=0.18) expands every edge of the stepped outline.
        wire = Part.Wire(Part.makePolygon([V(x, y0, z) for x, z in outline] + [V(*(-6.7, y0, -3))]).Edges)
        face = Part.Face(wire.makeOffset2D(clearance))
        profile = face.extrude(V(0, depth, 0))
    return profile

def _flipped(shape, inverted):
    if inverted:
        shape.rotate(V(0, 0, 0), V(0, 1, 0), 180)
    return shape

def build_rj45_port(center_x, center_y, center_z, inverted=False, leds=False,
                    light_pipes=True, parts=None, prefix="RJ45"):
    """Local connector solids reproduce nmc_rj45 before world translation."""
    sections = []
    for width, height, radius, y in [(19.2, 21.6, .35, -3.95), (20, 22.4, .6, -3.10)]:
        w = rounded_rect_wire(width, height, radius)
        w.rotate(V(0, 0, 0), V(1, 0, 0), 90)
        w.translate(V(0, y, 0))
        sections.append(w)
    housing = Part.makeLoft(sections, True).cut(_flipped(_aperture(1.2, -4.1, .18), inverted))
    if light_pipes:
        for x in (-5.9, 5.9):
            housing = housing.cut(cbox(3.2, 1.5, 1.9, x, -3.5, 9.05))
    shell = rounded_prism_y(19.6, 22, .4, 17.4, -3.15).cut(
        rounded_prism_y(18.5, 20.9, .25, 17.7, -3.3))
    for x in (-9.6, 9.6):
        shell = shell.cut(cbox(1, 3, 5, x, 4, 0))
    insert = rounded_prism_y(18.4, 20.8, .3, 17.7, -3.14).cut(_aperture(15.7, -3.3))
    features = [("Housing", housing, (.243, .267, .282)),
                ("FoldedShell", shell, (.259, .286, .306)),
                ("Insulator", _flipped(insert, inverted), (.090, .110, .125))]
    # Convex hull of the two reference support blocks, in the YZ plane.
    yz = [(-2.2, -3.7), (-1.8, -3.7), (8.2, -2.5),
          (8.2, -2.1), (7.8, -2.1), (-2.2, -3.3)]
    points = [V(-5.1, y, z) for y, z in yz]
    ramp = Part.Face(Part.Wire(Part.makePolygon(points + [points[0]]).Edges)).extrude(V(10.2, 0, 0))
    features.append(("SpringSupport", _flipped(ramp, inverted), (.133, .169, .161)))
    for i in range(8):
        x = -3.57 + i * 1.02
        points = [(x, -3.05, -2.85), (x, -2.75, -2.35), (x, 5.4, -1.75), (x, 7.8, -1.75)]
        wire = wire_between(points[0], points[1], .4).fuse(
            [wire_between(points[1], points[2], .4), wire_between(points[2], points[3], .4)])
        features.append((f"Contact{i+1}", _flipped(wire, inverted), (.541, .796, .612)))
    for sx in (-1, 1):
        ledge = cbox(.65, 11.5, .65, sx*6.3, 4, .2)
        bearing = cbox(.5, 8, 1.1, sx*2.4, 1.5, 7.8)
        features.append((f"Bearing{sx}", _flipped(ledge.fuse(bearing), inverted), (.204, .227, .243)))
        detent = cbox(.45, 4.3, 2.4, 0, 0, 0)
        detent.rotate(V(0, 0, 0), V(0, 0, 1), sx*10)
        detent.translate(V(sx*9.1, 5.3, -5.2))
        seam = wire_between((sx*8.3, -3.32, -10.6), (sx*9.6, -2.9, -8.8), .18)
        features.append((f"Fold{sx}", detent.fuse(seam), (.322, .357, .380)))
        if light_pipes:
            features.extend([(f"PipeFrame{sx}", cbox(3.1, .35, 1.8, sx*5.9, -3.72, 9.05), (.439, .482, .502)),
                             (f"LightPipe{sx}", cbox(2.6, .30, 1.35, sx*5.9, -4.02, 9.05), (.886, .945, .933))])
            if leds:
                features.append((f"Emitter{sx}", cbox(1.7, .3, .9, sx*5.9, -2.8, 9.05), LED_GREEN if sx < 0 else LED_AMBER))
    return _port_result(features, (center_x, center_y, center_z), parts, prefix)

def build_usb_a_port(center_x, center_y, center_z, parts=None, prefix="USBHost"):
    shell = rounded_prism_y(14.4, 7.4, .6, 12.8, -2.5).cut(
        rounded_prism_y(13.2, 6.2, .25, 13, -2.6))
    for x in (-4, 4):
        shell = shell.cut(cbox(2, 2.7, 1, x, 2, 3.6))
    features = [("Shell", shell, METAL_STEEL),
                ("Tongue", cbox(11.7, 10, 1.2, 0, 4, -1.4), GSPE_CREAM),
                ("RearStop", cbox(13, 1, 6, 0, 10.5, 0), (.080, .085, .095))]
    for sx in (-1, 1):
        detent = cbox(.45, 3, 1.6, 0, 0, 0)
        detent.rotate(V(0, 0, 0), V(0, 0, 1), sx*12)
        detent.translate(V(sx*6.5, .8, 0))
        features.append((f"Detent{sx}", detent, METAL_STEEL))
    for i, x in enumerate((-3.75, -1.25, 1.25, 3.75)):
        features.append((f"Contact{i+1}", cbox(.7, 5.8, .18, x, 2, -.72), BRASS_GOLD))
    return _port_result(features, (center_x, center_y, center_z), parts, prefix)

def build_usb_micro_port(center_x, center_y, center_z, parts=None, prefix="Console"):
    outer = [(-4, 1.65), (4, 1.65), (4, -.7), (3, -1.65), (-3, -1.65), (-4, -.7)]
    inner = [(-3.45, 1.1), (3.45, 1.1), (3.45, -.45), (2.7, -1.1), (-2.7, -1.1), (-3.45, -.45)]
    shell = polygon_prism_xz(outer, 6.5, -2.3).cut(polygon_prism_xz(inner, 6.7, -2.4))
    features = [("Shell", shell, METAL_STEEL),
                ("Tongue", cbox(5.7, 5, .6, 0, 1, -.4), (.133, .153, .176))]
    for i in range(-2, 3):
        features.append((f"Contact{i+3}", cbox(.32, 3.8, .16, i*.85, .6, -.05), BRASS_GOLD))
    return _port_result(features, (center_x, center_y, center_z), parts, prefix)

def build_nmc3_controller(parts, prefix, center_z=914.5, front_y=-23.0,
                          explode=0.0, doc=None, show_fascia_external=True,
                          show_internals=True):
    e = explode
    fascia_ey = -12.0 * e
    disp_ey   = -26.0 * e
    btn_ey    = -43.0 * e
    port_ey   =   8.0 * e
    pcb_ey    =  55.0 * e
    tray_ey   = 105.0 * e

    pts_tray = nmc_tray_pts(0.0)
    pts_pcb  = nmc_pcb_pts(0.0)

    # 1. NMC Faceplate (Wrap-around dengan side flanges)
    if show_fascia_external:
        plate = rounded_prism_y(57.4, 212.0, 1.8, 1.5, y0=front_y - 1.4 + fascia_ey)
        flange_l = cbox(1.5, 4.5, 212.0, -28.75, front_y + 3.75 + fascia_ey, 0.0)
        flange_r = cbox(1.5, 4.5, 212.0,  28.75, front_y + 3.75 + fascia_ey, 0.0)
        faceplate = plate.fuse([flange_l, flange_r])

        # Cutout Display LCD
        lcd_cut = rounded_prism_y(30.0, 32.0, 0.6, 1.7, y0=front_y - 1.5 + fascia_ey)
        lcd_cut.translate(V(-6.0, 0.0, 63.0))
        faceplate = faceplate.cut(lcd_cut)

        # Cutouts untuk 4x RJ45 ports
        for px, pz in [(-NMC_PORT_X, NMC_PORT_Z[0]), (-NMC_PORT_X, NMC_PORT_Z[1]),
                       (-NMC_PORT_X, NMC_PORT_Z[2]), (NMC_PORT_X, NMC_PORT_Z[2])]:
            rcut = rounded_prism_y(19.7, 22.1, 0.4, 1.7, y0=front_y - 1.5 + fascia_ey)
            rcut.translate(V(px, 0.0, pz))
            faceplate = faceplate.cut(rcut)

        # Cutout Console (Micro-B) & USB-A Host
        c_cut = cbox(9.0, 1.7, 4.6, NMC_PORT_X, front_y - 0.65 + fascia_ey, NMC_PORT_Z[0])
        u_cut = cbox(14.8, 1.7, 7.8, NMC_PORT_X, front_y - 0.65 + fascia_ey, NMC_PORT_Z[1])
        faceplate = faceplate.cut(c_cut).cut(u_cut)

        # 3x Lubang tombol navigasi & reset pinhole
        for x in [-11.0, 0.0, 11.0]:
            bhole = cyl(7.2, 1.7, x, front_y - 1.5 + fascia_ey, 32.0, dirv=(0, 1, 0))
            faceplate = faceplate.cut(bhole)
        rhole = cyl(1.4, 1.7, -3.0, front_y - 1.5 + fascia_ey, 24.0, dirv=(0, 1, 0))
        faceplate = faceplate.cut(rhole)

        # 4 lubang baut samping (axis X)
        for d in [-1, 1]:
            for dz in [-100.0, 100.0]:
                sx = 28.75 if d > 0 else -28.75
                dv = (-1, 0, 0) if d > 0 else (1, 0, 0)
                hole_cyl = cyl(3.4, 3.0, sx + (1.5 if d > 0 else -1.5), front_y + 3.0 + fascia_ey, dz, dirv=dv)
                faceplate = faceplate.cut(hole_cyl)

        faceplate.translate(V(0.0, 0.0, center_z))
        P(parts, f"{prefix}_Faceplate", faceplate, (0.118, 0.133, 0.176)) # #1E222D

        # 4x Side Torx screws
        side_screws = []
        for d in [-1, 1]:
            for dz in [-100.0, 100.0]:
                sc = side_torx_screw(dir=d, length=4.5, head_d=5.4, shaft_d=2.8,
                                     y=front_y + 3.0 + fascia_ey, z=center_z + dz)
                side_screws.append(sc)
        all_side_screws = side_screws[0].fuse(side_screws[1:])
        P(parts, f"{prefix}_SideTorxScrews", all_side_screws, METAL_STEEL)

        # Silkscreen Faceplate
        if doc is not None:
            t_gspe = make_text_solid("GSPE", 6.5, 0.15, 0.0, front_y - 1.42 + fascia_ey, center_z + 94.0, doc=doc)
            t_ns9k = make_text_solid("NETSHELTER 9000 SWITCHED", 1.8, 0.15, 0.0, front_y - 1.42 + fascia_ey, center_z + 87.5, doc=doc)
            P(parts, f"{prefix}_SilkGSPE", t_gspe, GSPE_CREAM)
            P(parts, f"{prefix}_SilkNS9000", t_ns9k, (0.957, 0.957, 0.949))

            # Port Labels (vertical)
            labels = [
                (-24.0, NMC_PORT_Z[0], "Universal I/O"),
                (-24.0, NMC_PORT_Z[1], "Link A"),
                (-24.0, NMC_PORT_Z[2], "Link B"),
                ( 24.0, NMC_PORT_Z[0], "Console"),
                ( 24.0, NMC_PORT_Z[1], "USB"),
                ( 24.0, NMC_PORT_Z[2], "Network")
            ]
            for lx, lz, txt in labels:
                t_lbl = make_text_solid(txt, 2.0, 0.15, lx, front_y - 1.42 + fascia_ey, center_z + lz, angle_deg=-90.0, doc=doc)
                P(parts, f"{prefix}_Silk_{txt.replace(' ', '_').replace('/', '_')}", t_lbl, (0.957, 0.957, 0.949))

            # Network legend numbers
            for idx, num_str in enumerate(["1000", "100", "10"]):
                col = (0.659, 0.875, 0.294) if idx == 0 else (0.894, 0.675, 0.298)
                t_spd = make_text_solid(num_str, 2.15, 0.15, 12.0 + idx * 3.4, front_y - 1.43 + fascia_ey, center_z - 30.0, angle_deg=-90.0, doc=doc)
                P(parts, f"{prefix}_SilkSpeed_{num_str}", t_spd, col)

            # Button silkscreen
            t_m = make_text_solid("Main", 1.8, 0.15, -11.0, front_y - 1.42 + fascia_ey, center_z + 26.4, doc=doc)
            t_v = make_text_solid("v", 1.8, 0.15, 0.0, front_y - 1.42 + fascia_ey, center_z + 26.4, doc=doc)
            t_s = make_text_solid("Select", 1.8, 0.15, 11.0, front_y - 1.42 + fascia_ey, center_z + 26.4, doc=doc)
            t_r = make_text_solid("R", 2.1, 0.15, -7.0, front_y - 1.42 + fascia_ey, center_z + 24.0, doc=doc)
            P(parts, f"{prefix}_SilkBtnMain", t_m, (0.957, 0.957, 0.949))
            P(parts, f"{prefix}_SilkBtnDown", t_v, (0.957, 0.957, 0.949))
            P(parts, f"{prefix}_SilkBtnSelect", t_s, (0.957, 0.957, 0.949))
            P(parts, f"{prefix}_SilkResetR", t_r, (0.957, 0.957, 0.949))

            # APDU9953 rating plate bar
            t_sku = make_text_solid("APDU9953 / 230 V 32 A", 2.3, 0.15, 0.0, front_y - 1.42 + fascia_ey, center_z - 86.0, doc=doc)
            P(parts, f"{prefix}_SilkSKU", t_sku, GSPE_CREAM)

        accent_bar = cbox(50.0, 0.2, 6.0, 0.0, front_y - 1.51 + fascia_ey, center_z - 78.0)
        P(parts, f"{prefix}_NavyAccentBar", accent_bar, GSPE_NAVY)

        # 3x Status LEDs & labels (Ok, Warning, Overload)
        led_cols = [LED_GREEN, LED_AMBER, LED_RED]
        led_names = ["Ok", "Warning", "Overload"]
        for idx, col in enumerate(led_cols):
            lz = center_z + 72.0 - idx * 8.0
            led = cyl(2.2, 0.6, 21.5, front_y - 2.0 + fascia_ey, lz, dirv=(0, 1, 0))
            P(parts, f"{prefix}_StatusLED_{led_names[idx]}", led, col)
            if doc is not None:
                t_st = make_text_solid(led_names[idx], 1.5, 0.15, 15.0, front_y - 1.42 + fascia_ey, lz, doc=doc)
                P(parts, f"{prefix}_SilkStatus_{led_names[idx]}", t_st, (0.957, 0.957, 0.949))

        # 2. OLED Display Subassembly
        disp_bezel = cbox(31.0, 1.2, 33.0, -6.0, front_y - 1.45 + disp_ey, center_z + 63.0)
        disp_cut = cbox(28.6, 1.4, 28.6, -6.0, front_y - 1.5 + disp_ey, center_z + 63.0)
        disp_bezel = disp_bezel.cut(disp_cut)
        P(parts, f"{prefix}_DisplayBezel", disp_bezel, (0.071, 0.102, 0.133))

        screen = cbox(28.0, 0.6, 28.0, -6.0, front_y - 0.5 + disp_ey, center_z + 63.0)
        P(parts, f"{prefix}_DisplayScreen", screen, LCD_SCREEN)

        header_bar = cbox(27.7, 0.12, 4.8, -6.0, front_y - 0.86 + disp_ey, center_z + 74.0)
        status_bar = cbox(27.7, 0.12, 3.3, -6.0, front_y - 0.86 + disp_ey, center_z + 50.9)
        P(parts, f"{prefix}_DisplayHeaderBar", header_bar, (0.000, 0.812, 0.412))
        P(parts, f"{prefix}_DisplayStatusBar", status_bar, GSPE_CREAM)

        if doc is not None:
            t_hdr = make_text_solid("Phase Info", 2.2, 0.15, -6.0, front_y - 0.94 + disp_ey, center_z + 74.0, doc=doc)
            P(parts, f"{prefix}_DisplayHeaderTxt", t_hdr, GSPE_NAVY)

            menu_items = ["Network", "Software Info", "SKU/Serial #", "Display Settings", "Log to Flash"]
            for idx, item in enumerate(menu_items):
                t_menu = make_text_solid(item, 1.8, 0.15, -6.0, front_y - 0.94 + disp_ey, center_z + 69.5 - idx * 3.45, doc=doc)
                P(parts, f"{prefix}_DisplayMenu_{idx+1}", t_menu, GSPE_CREAM)

            t_bot = make_text_solid("Main   v   Select", 1.6, 0.15, -6.0, front_y - 0.94 + disp_ey, center_z + 50.9, doc=doc)
            P(parts, f"{prefix}_DisplayFooterTxt", t_bot, GSPE_NAVY)

        lens = cbox(28.4, 0.16, 28.4, -6.0, front_y - 1.25 + disp_ey - 12.0*e, center_z + 63.0)
        P(parts, f"{prefix}_DisplayLens", lens, (0.700, 0.850, 0.900))

        # 3. 3x Tactile Navigation Buttons
        btn_rings = []
        btn_domes = []
        for x in [-11.0, 0.0, 11.0]:
            r_outer = cyl(8.0, 0.8, x, front_y - 1.5 + btn_ey, center_z + 32.0, dirv=(0, 1, 0))
            r_inner = cyl(6.9, 1.0, x, front_y - 1.6 + btn_ey, center_z + 32.0, dirv=(0, 1, 0))
            btn_rings.append(r_outer.cut(r_inner))

            scale = App.Matrix()
            scale.A22 = .52
            dome = sph(7, 0, 0, 0).transformGeometry(scale)
            dome.translate(V(0, .35, 0))
            dome = dome.common(cbox(8, 2.4, 8, 0, -1.1, 0))
            dome.translate(V(x, front_y - 1.4 + btn_ey, center_z + 32))
            btn_domes.append(dome)

        all_rings = btn_rings[0].fuse(btn_rings[1:])
        all_domes = btn_domes[0].fuse(btn_domes[1:])
        P(parts, f"{prefix}_NavButtonRings", all_rings, (0.271, 0.302, 0.341))
        P(parts, f"{prefix}_NavButtonDomes", all_domes, (0.733, 0.757, 0.776))

        # 4. Realistic Ports
        # RJ45 Universal I/O (inverted)
        build_rj45_port(-NMC_PORT_X, front_y + port_ey, center_z + NMC_PORT_Z[0], inverted=True,
                       light_pipes=False, parts=parts, prefix=f"{prefix}_Port_UniversalIO")
        # RJ45 Link A
        build_rj45_port(-NMC_PORT_X, front_y + port_ey, center_z + NMC_PORT_Z[1],
                       parts=parts, prefix=f"{prefix}_Port_LinkA")
        # RJ45 Link B
        build_rj45_port(-NMC_PORT_X, front_y + port_ey, center_z + NMC_PORT_Z[2],
                       parts=parts, prefix=f"{prefix}_Port_LinkB")
        # RJ45 Network
        build_rj45_port(NMC_PORT_X, front_y + port_ey, center_z + NMC_PORT_Z[2], leds=True,
                       parts=parts, prefix=f"{prefix}_Port_Network")

        # USB Micro-B Console
        build_usb_micro_port(NMC_PORT_X, front_y + port_ey, center_z + NMC_PORT_Z[0],
                             parts=parts, prefix=f"{prefix}_Port_Console")

        # USB-A Host
        build_usb_a_port(NMC_PORT_X, front_y + port_ey, center_z + NMC_PORT_Z[1],
                         parts=parts, prefix=f"{prefix}_Port_USBHost")
        P(parts, f"{prefix}_ResetPlunger", cyl(1.1, 1.8, -3, front_y + .5 + port_ey,
          center_z + 24, dirv=(0, 1, 0)), (.080, .085, .095))

    # 5. Internals: Shield Enclosure, Tray Screws, Main PCB, IC Chips
    if show_internals:
        # Sheet metal shielding tray
        tray = cbox(50.0, 28.0, 208.0, 0.0, front_y + 24.0 + tray_ey, center_z)
        tcavity = cbox(48.4, 28.2, 206.4, 0.0, front_y + 23.1 + tray_ey, center_z)
        tray = tray.cut(tcavity)
        for z in (-90, -80, -70, -60):
            for x in (-15, 0, 15):
                tray = tray.cut(cbox(7, 1.4, 2, x, front_y + 37.7 + tray_ey, center_z + z))

        # 4 Standoff bosses bridging tray rear -> main PCB
        standoffs = []
        for p in pts_pcb:
            boss = cyl(5.5, 13.8, p[0], front_y + 23.6 + tray_ey, center_z + p[1], dirv=(0, 1, 0))
            bh = cyl(2.2, 14.2, p[0], front_y + 23.4 + tray_ey, center_z + p[1], dirv=(0, 1, 0))
            standoffs.append(boss.cut(bh))
        all_standoffs = standoffs[0].fuse(standoffs[1:])
        tray = tray.fuse(all_standoffs)
        P(parts, f"{prefix}_ShieldTray", tray, METAL_STEEL)

        # 4x M3 Rear tray countersunk Torx screws
        t_screws = []
        for p in pts_tray:
            sc = torx_screw_csk(head_d=6.0, shaft_d=2.8, length=8.0,
                                x=p[0], y=front_y + 46.5 + tray_ey, z=center_z + p[1],
                                dirv=(0, -1, 0))
            t_screws.append(sc)
        all_t_screws = t_screws[0].fuse(t_screws[1:])
        P(parts, f"{prefix}_TrayTorxScrews", all_t_screws, METAL_STEEL)

        # Main PCB FR-4
        pcb = cbox(46.0, 1.6, 200.0, 0.0, front_y + 23.0 + pcb_ey, center_z)
        for p in pts_pcb:
            phole = cyl(2.7, 2.0, p[0], front_y + 22.0 + pcb_ey, center_z + p[1], dirv=(0, 1, 0))
            pcb = pcb.cut(phole)
        P(parts, f"{prefix}_MainPCB", pcb, PCB_GREEN)

        # IC Chips: SoC, RAM, LAN Transformer, Crystal
        soc = cbox(16.0, 4.2, 16.0, -6.0, front_y + 19.5 + pcb_ey, center_z + 38.0)
        ram = cbox(7.0, 2.6, 13.0, 12.0, front_y + 20.8 + pcb_ey, center_z + 37.0)
        lan = cbox(12.0, 6.0, 10.0, 11.0, front_y + 19.0 + pcb_ey, center_z - 70.0)
        xtal = cbox(8.0, 3.2, 4.0, -12.0, front_y + 20.5 + pcb_ey, center_z + 20.0)
        fpc_conn = cbox(18.0, 3.2, 4.8, -6.0, front_y + 20.5 + pcb_ey, center_z + 80.0)
        fpc_ribbon = cbox(15.0, 0.25, 12.0, -6.0, front_y + 13.0 + pcb_ey, center_z + 81.0)

        # Filter Caps
        caps = [cyl(5.0, 5.6, -15.0, front_y + 16.5 + pcb_ey, center_z + z, dirv=(0, 1, 0)) for z in [-88.0, -77.0, 0.0]]
        all_caps = caps[0].fuse(caps[1:])

        P(parts, f"{prefix}_SoC_Chip", soc, (0.141, 0.161, 0.188))
        P(parts, f"{prefix}_RAM_Chip", ram, (0.141, 0.161, 0.188))
        P(parts, f"{prefix}_LAN_Transformer", lan, (0.141, 0.161, 0.188))
        P(parts, f"{prefix}_CrystalOscillator", xtal, METAL_STEEL)
        P(parts, f"{prefix}_FPC_Connector", fpc_conn, GSPE_CREAM)
        P(parts, f"{prefix}_FPC_Ribbon", fpc_ribbon, FPC_AMBER)
        P(parts, f"{prefix}_ElectrolyticCaps", all_caps, (0.137, 0.263, 0.416))

        if doc is not None:
            t_soc = make_text_solid("SoC", 2.4, 0.15, -6.0, front_y + 17.35 + pcb_ey, center_z + 38.0, doc=doc)
            t_ram = make_text_solid("RAM", 1.5, 0.15, 12.0, front_y + 19.45 + pcb_ey, center_z + 37.0, doc=doc)
            t_lan = make_text_solid("LAN", 1.8, 0.15, 11.0, front_y + 15.95 + pcb_ey, center_z - 70.0, doc=doc)
            t_xtl = make_text_solid("25 MHz", 1.2, 0.15, -12.0, front_y + 18.85 + pcb_ey, center_z + 20.0, doc=doc)
            t_nmcp = make_text_solid("GSPE NMC3", 2.6, 0.15, 0.0, front_y + 22.17 + pcb_ey, center_z + 92.0, doc=doc)
            P(parts, f"{prefix}_SilkSoC", t_soc, GSPE_CREAM)
            P(parts, f"{prefix}_SilkRAM", t_ram, GSPE_CREAM)
            P(parts, f"{prefix}_SilkLAN", t_lan, GSPE_CREAM)
            P(parts, f"{prefix}_SilkCrystal", t_xtl, (0.957, 0.957, 0.949))
            P(parts, f"{prefix}_SilkNMC3PCB", t_nmcp, GSPE_CREAM)

        # 4x M2.5 Main PCB Torx screws
        p_screws = []
        for p in pts_pcb:
            sc = torx_screw(head_d=4.2, shaft_d=2.4, length=9.0,
                            x=p[0], y=front_y + 21.9 + pcb_ey, z=center_z + p[1],
                            dirv=(0, 1, 0))
            p_screws.append(sc)
        all_p_screws = p_screws[0].fuse(p_screws[1:])
        P(parts, f"{prefix}_PCBTorxScrews", all_p_screws, METAL_STEEL)
