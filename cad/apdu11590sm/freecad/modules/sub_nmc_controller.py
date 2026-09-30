# =====================================================================
# sub_nmc_controller.py — NMC3 Controller Cassette (54 x 150 x 45 mm)
# Rebranding GSPE. Konversi B-Rep dari sub_nmc_controller.scad (Tahap 1).
# Frame lokal: pusat cassette; body y=-45..0 (muka depan y=-45).
# Ikon piktogram kecil (kunci pas, trident USB, tree jaringan) dihilangkan
# pada konversi B-Rep; seluruh teks & port berlubang tembus dipertahankan.
# =====================================================================
from FreeCAD import Vector as V
import Part
from ._common import (P, validate, box, cyl, cbox, fuse_all, text3d,
                      prism_neg_y,
                      GSPE_NAVY, GSPE_CREAM, NMC_BODY, NMC_BEZEL, SCREEN_BG,
                      TEXT_WHITE, PORT_METAL, PORT_DARK, GOLD_PIN, BTN_GREY,
                      BTN_ICON, DOME_GREEN, RESET_GREEN, LED_GREEN,
                      LED_AMBER, LED_RED, STRIP_DARK, ROCKER_BLACK)

NMC_W = 54.0
NMC_H = 150.0
NMC_D = 45.0
EPS = 0.05

NMC_PROFILE = [(-22.5, 75.0), (22.5, 75.0), (27.0, 70.5),
               (27.0, -75.0), (-27.0, -75.0), (-27.0, 70.5)]

# Lubang tembus port pada body (cx, cz, w, h, d) — y center -41
PORT_HOLES = [
    (-12.0, -9.0, 13.5, 9.5, 9.0),    # USB Micro-B console
    (12.0, -9.0, 16.5, 10.5, 9.0),    # USB-A host
    (-13.0, -22.0, 13.4, 11.6, 9.0),  # Sensor 2
    (13.0, -22.0, 13.4, 11.6, 9.0),   # Sensor 1
    (-13.0, -36.0, 13.4, 11.6, 9.0),  # Link 2
    (13.0, -36.0, 13.4, 11.6, 9.0),   # Link 1
    (7.0, -53.0, 13.4, 11.6, 9.0),    # GbE network
]

USB_MICRO_B_TRAP = [(-3.8, 1.6), (3.8, 1.6), (3.8, -0.6),
                    (2.8, -1.6), (-2.8, -1.6), (-3.8, -0.6)]
USB_MICRO_B_CAV = [(-3.2, 1.1), (3.2, 1.1), (3.2, -0.4),
                   (2.3, -1.1), (-2.3, -1.1), (-3.2, -0.4)]


def _rj45(parts, prefix, x0, z0, has_leds,
          led_left=(0.95, 0.85, 0.1), led_right=(0.1, 0.95, 0.2)):
    # Kerah logam luar dengan bevel masuk (potong tembus 2.5mm agar tidak tertutup plat 0.1mm)
    collar = box(13.2, 1.1, 11.4, x0 - 6.6, -46.0, z0 - 5.7)
    collar = collar.cut(box(11.2, 2.5, 8.6, x0 - 5.6, -46.5, z0 - 4.5))
    validate(prefix + "_COLLAR", collar)
    P(parts, prefix + "_COLLAR", collar, PORT_METAL)

    # Dinding dalam plastik hitam + rongga tembus
    wall = box(11.2, 8.5, 8.6, x0 - 5.6, -45.0, z0 - 4.5)
    wall = wall.cut(box(9.8, 8.7, 7.2, x0 - 4.9, -45.1, z0 - 3.8))
    validate(prefix + "_WALL", wall)
    P(parts, prefix + "_WALL", wall, STRIP_DARK)

    # Dasar rongca gelap pekat
    P(parts, prefix + "_BASE",
      box(9.8, 0.5, 7.2, x0 - 4.9, -36.9, z0 - 3.8), PORT_DARK)

    # 8 pin kontak emas miring 12 deg
    pins = []
    for p in range(8):
        b = box(0.45, 7.3, 0.4, -0.225, -3.65, -0.2)
        b.rotate(V(0, 0, 0), V(1, 0, 0), 12)
        b.translate(V(x0 - 3.8 + p * 1.08, -40.75, z0 + 3.1))
        pins.append(b)
    pin = fuse_all(pins)
    validate(prefix + "_PINS", pin)
    P(parts, prefix + "_PINS", pin, GOLD_PIN)

    # Latch notch di atas rongga
    P(parts, prefix + "_LATCH",
      cbox(4.8, 8.7, 1.2, x0, -40.65, z0 + 4.6), PORT_DARK)

    # LED indikator
    if has_leds:
        P(parts, prefix + "_LED_L",
          cbox(1.8, 0.4, 1.1, x0 - 4.8, -46.1, z0 + 4.6), led_left)
        P(parts, prefix + "_LED_R",
          cbox(1.8, 0.4, 1.1, x0 + 4.8, -46.1, z0 + 4.6), led_right)


def _usb_micro_b(parts, prefix, x0, z0):
    # Bingkai & rongga persegi + aksen navy dengan ceruk tembus trapesium
    frame = box(13.0, 0.7, 9.0, x0 - 6.5, -45.6, z0 - 4.5)
    frame = frame.cut(box(8.2, 1.0, 4.0, x0 - 4.1, -45.7, z0 - 2.0))
    validate(prefix + "_FRAME", frame)
    P(parts, prefix + "_FRAME", frame, NMC_BODY)

    accent = box(11.6, 0.4, 7.6, x0 - 5.8, -45.2, z0 - 3.8)
    accent = accent.cut(box(8.0, 0.6, 3.8, x0 - 4.0, -45.3, z0 - 1.9))
    validate(prefix + "_ACCENT", accent)
    P(parts, prefix + "_ACCENT", accent, GSPE_NAVY)

    # Selubung logam trapesium + rongca dalam
    shell = prism_neg_y(USB_MICRO_B_TRAP, -44.0, 3.0)
    shell.translate(V(x0, 0, z0))
    shell = shell.cut(prism_neg_y(USB_MICRO_B_CAV, -43.0, 5.0).translate(V(x0, 0, z0)))
    validate(prefix + "_SHELL", shell)
    P(parts, prefix + "_SHELL", shell, PORT_METAL)

    # Lidah plastik + pin emas
    P(parts, prefix + "_TONGUE", cbox(5.0, 4.0, 0.6, x0, -42.5, z0 + 0.1),
      PORT_DARK)
    pins = fuse_all([cbox(0.3, 3.5, 0.2, x0 + p * 0.9, -42.5, z0 + 0.45)
                     for p in range(-2, 3)])
    P(parts, prefix + "_PINS", pins, GOLD_PIN)


def _usb_a(parts, prefix, x0, z0):
    # Bezel frame hitam (chamfered pocket)
    bez = box(16.0, 1.2, 10.0, x0 - 8.0, -45.6, z0 - 5.0)
    bez = bez.cut(box(13.0, 2.0, 7.0, x0 - 6.5, -46.0, z0 - 3.5))
    validate(prefix + "_BEZEL", bez)
    P(parts, prefix + "_BEZEL", bez, NMC_BEZEL)

    # Selubung logam + rongca + klip pegas atas
    shell = box(12.5, 9.0, 6.5, x0 - 6.25, -45.0, z0 - 3.25)
    shell = shell.cut(box(11.3, 9.2, 5.3, x0 - 5.65, -45.1, z0 - 2.65))
    shell = shell.fuse(cbox(6.0, 2.5, 0.5, x0, -43.0, z0 + 3.25))
    validate(prefix + "_SHELL", shell)
    P(parts, prefix + "_SHELL", shell, PORT_METAL)

    P(parts, prefix + "_BASE", cbox(11.3, 1.0, 5.3, x0, -36.5, z0), PORT_DARK)
    P(parts, prefix + "_TONGUE", cbox(10.5, 8.0, 1.4, x0, -41.0, z0 - 1.45),
      GSPE_CREAM)
    pins = fuse_all([cbox(0.6, 7.0, 0.3, x0 + i * 1.2, -41.0, z0 - 0.65)
                     for i in (-3, -1, 1, 3)])
    P(parts, prefix + "_PINS", pins, GOLD_PIN)


def _nav_button(parts, prefix, x, z, kind):
    # Tombol silindris chamfer (cone d1=9.2 -> d2=8.4, h=1.4, sumbu -Y)
    btn = Part.makeCone(4.6, 4.2, 1.4, V(0, 0, 0))
    btn.rotate(V(0, 0, 0), V(1, 0, 0), 90)
    btn.translate(V(x, -45.0, z))
    validate(prefix, btn)
    P(parts, prefix, btn, BTN_GREY)

    # Ikon ukir di muka tombol
    if kind == "menu":
        icon = fuse_all([box(5.0, 0.3, 0.55, x - 2.5, -46.6, z + i * 0.9 - 0.275)
                         for i in (-3, -1, 1, 3)])
    elif kind == "chevron":
        icon = prism_neg_y([(-3.0, 1.6), (0.0, -1.4), (3.0, 1.6),
                            (2.2, 2.2), (0.0, 0.0), (-2.2, 2.2)], -46.45, 0.3)
        icon.translate(V(x, 0, z + 0.2))
    else:  # check
        icon = prism_neg_y([(-2.8, -0.4), (-1.0, -2.2), (3.0, 1.8),
                            (2.2, 2.4), (-1.0, -0.8), (-2.0, 0.2)], -46.45, 0.3)
        icon.translate(V(x, 0, z + 0.2))
    validate(prefix + "_ICON", icon)
    P(parts, prefix + "_ICON", icon, BTN_ICON)


def _wrench_icon(x, y, z):
    handle = cbox(0.7, 0.2, 3.2, 0, 0, -0.6)
    head = cyl(2.4, 0.2, 0, -0.1, 0.8, dirv=(0, 1, 0))
    jaw = cbox(1.0, 0.4, 1.4, 0, 0, 1.1)
    wrench = handle.fuse(head).cut(jaw)
    wrench.rotate(V(0, 0, 0), V(0, 1, 0), -45)
    wrench.translate(V(x, y, z))
    return wrench


def _usb_trident_icon(x, y, z):
    stem = cbox(0.45, 0.2, 3.5, 0, 0, -0.4)
    tri = Part.Face(Part.Wire(Part.makePolygon([V(-0.8, 0, 0), V(0.8, 0, 0), V(0, 0, 1.1), V(-0.8, 0, 0)]).Edges)).extrude(V(0, 0.2, 0))
    tri.translate(V(0, -0.1, 1.6))
    b_left1 = cbox(0.35, 0.2, 1.6, -1.0, 0, 0.1)
    b_left2 = cbox(1.2, 0.2, 0.35, -0.5, 0, -0.6)
    b_left3 = cbox(0.8, 0.2, 0.8, -1.0, 0, 1.1)
    b_rt1 = cbox(0.35, 0.2, 1.6, 1.0, 0, 0.1)
    b_rt2 = cbox(1.2, 0.2, 0.35, 0.5, 0, -0.6)
    b_rt3 = cyl(0.85, 0.2, 1.0, -0.1, 1.1, dirv=(0, 1, 0))
    usb = stem.fuse([tri, b_left1, b_left2, b_left3, b_rt1, b_rt2, b_rt3])
    usb.translate(V(x, y, z))
    return usb


def _network_tree_icon(x, y, z):
    node_top = cbox(2.0, 0.2, 2.0, 0, 0, 4.0)
    node_l = cbox(2.0, 0.2, 2.0, -2.5, 0, 0.5)
    node_r = cbox(2.0, 0.2, 2.0, 2.5, 0, 0.5)
    stem_v = cbox(0.5, 0.2, 2.0, 0, 0, 2.5)
    stem_h = cbox(5.0, 0.2, 0.5, 0, 0, 1.5)
    tree = node_top.fuse([node_l, node_r, stem_v, stem_h])
    tree.translate(V(x, y, z))
    return tree


def build_nmc_controller(parts, prefix="NMC"):
    # ---- 1. Body kaset + lubang tembus port ----
    pts = [V(x, 0.0, z) for x, z in NMC_PROFILE]
    wire = Part.Wire(Part.makePolygon(pts + [pts[0]]).Edges)
    body = Part.Face(wire).extrude(V(0, -NMC_D, 0))
    holes = fuse_all([cbox(w, d, h, cx, -41.0, cz)
                      for (cx, cz, w, h, d) in PORT_HOLES])
    body = body.cut(holes)
    validate(prefix + "_BODY", body)
    P(parts, prefix + "_BODY", body, NMC_BODY)

    # ---- 2. Bezel tepi luar ----
    bz = Part.Face(wire.copy()).extrude(V(0, -0.6, 0))
    bz.translate(V(0, -NMC_D, 0))
    bz = bz.cut(cbox(52.0, 1.2, 148.0, 0, -45.3, 0))
    validate(prefix + "_BEZEL", bz)
    P(parts, prefix + "_BEZEL", bz, NMC_BEZEL)

    # ---- Brand GSPE & status dome LED ----
    P(parts, prefix + "_LOGO",
      text3d("GSPE", 7.0, 0.5, 0, -45.2, 63.5), GSPE_CREAM)
    P(parts, prefix + "_DOME_RING",
      cyl(4.6, 0.4, 0, -45.3, 58.0, dirv=(0, 1, 0)), ROCKER_BLACK)
    P(parts, prefix + "_DOME",
      Part.makeSphere(1.8, V(0, -45.2, 58.0)), DOME_GREEN)

    # 3 status LED vertikal + label
    for dz, col, lbl in ((2.8, LED_GREEN, "Okay"), (0.0, LED_AMBER, "Warning"),
                         (-2.8, LED_RED, "Overload")):
        P(parts, prefix + "_ST_" + lbl.upper(),
          Part.makeSphere(0.9, V(-1.0, -45.2, 52.5 + dz)), col)
        P(parts, prefix + "_LBL_" + lbl.upper(),
          text3d(lbl, 1.5, 0.3, -4.5, -45.2, 52.5 + dz, halign="right"), TEXT_WHITE)

    # ---- LCD grafis portrait ----
    P(parts, prefix + "_LCD_FRAME", box(31.0, 0.6, 48.0, -21.0, -45.1, -1.0),
      ROCKER_BLACK)
    P(parts, prefix + "_LCD_SCREEN", box(29.0, 0.2, 46.0, -20.0, -45.5, 0.0),
      SCREEN_BG)
    P(parts, prefix + "_LCD_HEADER", box(29.0, 0.25, 6.5, -20.0, -45.8, 39.0),
      GSPE_NAVY)
    P(parts, prefix + "_LCD_TITLE",
      text3d("Phase Info", 2.4, 0.25, -5.5, -46.05, 42.0), GSPE_CREAM)
    for i, item in enumerate(("Bank Info", "Outlet Current", "Alarm Status",
                              "Network", "Software Info")):
        P(parts, prefix + "_MENU_%d" % i,
          text3d(item, 2.2, 0.2, -5.5, -45.75, 33.0 - i * 6.0), GSPE_NAVY)

    # ---- Reset pinhole + label R ----
    P(parts, prefix + "_RESET",
      cyl(2.4, 0.5, 20.0, -45.7, 42.0, dirv=(0, 1, 0)), RESET_GREEN)
    P(parts, prefix + "_RESET_R",
      text3d("R", 1.8, 0.2, 22.6, -45.2, 42.0), RESET_GREEN)

    # ---- 3 tombol navigasi + ikon ----
    _nav_button(parts, prefix + "_BTN_MENU", 20.0, 31.5, "menu")
    _nav_button(parts, prefix + "_BTN_CHEVRON", 20.0, 21.0, "chevron")
    _nav_button(parts, prefix + "_BTN_CHECK", 20.0, 10.5, "check")

    # Ikon USB trident di bawah tombol centang mengarah ke port host
    P(parts, prefix + "_ICO_TRIDENT",
      _usb_trident_icon(13.0, -45.2, 0.0), TEXT_WHITE)

    # ---- Port USB Micro-B console & USB-A host (baris z=-9) ----
    _usb_micro_b(parts, prefix + "_USB_CON", -12.0, -9.0)
    _usb_a(parts, prefix + "_USB_HOST", 12.0, -9.0)

    # Ikon Kunci Pas & label Console
    P(parts, prefix + "_ICO_WRENCH",
      _wrench_icon(-22.5, -45.2, -5.5), TEXT_WHITE)
    P(parts, prefix + "_LBL_CONSOLE",
      text3d("Console", 1.3, 0.2, -22.5, -45.2, -9.5), TEXT_WHITE)

    # ---- 2x2 grid RJ-45 sensor & link + GbE ----
    _rj45(parts, prefix + "_RJ_SENSOR2", -13.0, -22.0, False)
    _rj45(parts, prefix + "_RJ_SENSOR1", 13.0, -22.0, False)
    _rj45(parts, prefix + "_RJ_LINK2", -13.0, -36.0, True)
    _rj45(parts, prefix + "_RJ_LINK1", 13.0, -36.0, True)
    _rj45(parts, prefix + "_RJ_GBE", 7.0, -53.0, True,
          led_left=(0.95, 0.95, 0.95), led_right=(0.95, 0.95, 0.95))

    P(parts, prefix + "_LBL_SENSOR",
      text3d("Sensor", 1.6, 0.2, 0, -45.2, -22.0), TEXT_WHITE)
    P(parts, prefix + "_LBL_SEP",
      text3d("-", 2.0, 0.2, 0, -45.2, -29.0), TEXT_WHITE)
    P(parts, prefix + "_LBL_LINK",
      text3d("Link", 1.6, 0.2, 0, -45.2, -36.0), TEXT_WHITE)
    P(parts, prefix + "_NUM_2",
      text3d("2", 1.8, 0.2, -22.5, -45.2, -45.0), TEXT_WHITE)
    P(parts, prefix + "_NUM_1",
      text3d("1", 1.8, 0.2, 22.5, -45.2, -45.0), TEXT_WHITE)

    # Diagram pohon jaringan + angka kecepatan 10 / 100 / 1000
    P(parts, prefix + "_ICO_NET_TREE",
      _network_tree_icon(-12.0, -45.2, -47.0), TEXT_WHITE)
    P(parts, prefix + "_SPD_10",
      text3d("10", 1.4, 0.2, -12.0, -45.2, -50.5), LED_GREEN)
    P(parts, prefix + "_SPD_100",
      text3d("100", 1.4, 0.2, -12.0, -45.2, -52.7), LED_AMBER)
    P(parts, prefix + "_SPD_1000",
      text3d("1000", 1.4, 0.2, -12.0, -45.2, -54.9), LED_GREEN)

    # ---- Logo GSPE kanan bawah & pull tab ----
    P(parts, prefix + "_LOGO_SM",
      text3d("GSPE", 3.8, 0.35, 23.5, -45.2, -67.5, halign="right"), GSPE_CREAM)
    P(parts, prefix + "_PULLTAB", box(16.0, 3.5, 5.0, -8.0, -44.0, -79.0),
      ROCKER_BLACK)

    return parts
