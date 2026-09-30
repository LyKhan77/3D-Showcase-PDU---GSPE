# =====================================================================
# sub_socket_4in1.py — Pasangan soket (1 Combo 4-in-1 + 1 C13/C15)
# Konversi B-Rep dari sub_socket_4in1.scad (Tahap 1, tervalidasi).
# PAIR_W x PAIR_H = 50 x 34 mm, muka soket y=0.5..2.5, well y=3..4.
# =====================================================================
from FreeCAD import Vector as V
import Part
from ._common import (P, validate, box, cyl, cbox, fuse_all, text3d,
                      polygon_prism, PLATE_GREY, WELL_DARK, FACE_GREY,
                      PIN_DARK, LATCH_CLEAR, LATCH_FRAME, LED_GREEN,
                      SCREW_BLACK, STRIP_DARK, TEXT_WHITE)

PAIR_W = 50.0
PAIR_H = 34.0
EPS = 0.05

# Profil muka soket (x, z) — identik polygon OpenSCAD
COMBO_PROFILE = [(-7.5, 11.0), (-9.0, 9.5), (-9.0, -9.5), (-7.5, -11.0),
                 (5.0, -11.0), (9.0, -7.0), (9.0, 7.0), (5.0, 11.0)]
C13_PROFILE = [(-3.7, 10.5), (-7.5, 6.7), (-7.5, -6.7), (-3.7, -10.5),
               (6.0, -10.5), (7.5, -9.0), (7.5, 9.0), (6.0, 10.5)]


def _face_with_notch(profile, notch_x, notch_r, notch_z=0.0):
    """Face profil XZ dengan U-notch setengah lingkaran di tepi."""
    pts = [V(x, 0.0, z) for x, z in profile]
    wire = Part.Wire(Part.makePolygon(pts + [pts[0]]).Edges)
    face = Part.Face(wire)
    notch = Part.Face(Part.Wire(Part.makeCircle(notch_r, V(notch_x, 0, notch_z),
                                                V(0, 1, 0)).Edges))
    return face.cut(notch)


def _socket_face(parts, prefix, profile, notch_x, notch_r, sx, sz, slots,
                 pin_blocks):
    """Pulau muka soket: profil extrude 2mm (y 0.5..2.5) dipotong slot pin."""
    face = _face_with_notch(profile, notch_x, notch_r)
    island = face.extrude(V(0, 2.0, 0))          # y 0 .. 2 -> nanti digeser
    island.translate(V(sx, 0.5, sz))             # y 0.5..2.5

    # Slot pin tembus (potong y 0.4..2.6 agar bersih tanpa koplanar)
    tools = []
    for (cx, cz, w, h) in slots:
        tools.append(box(w, 2.4, h, sx + cx - w / 2, 0.4, sz + cz - h / 2))
    if tools:
        island = island.cut(fuse_all(tools))
    validate(prefix, island)
    P(parts, prefix, island, FACE_GREY)

    # Blok terminal gelap di dasar slot
    blk_tools = []
    for (cx, cz, w, h) in pin_blocks:
        blk_tools.append(cbox(w, 1.2, h, sx + cx, 3.0, sz + cz))
    pins = fuse_all(blk_tools)
    validate(prefix + "_PINS", pins)
    P(parts, prefix + "_PINS", pins, PIN_DARK)


def _locking_latch(parts, prefix, x, y, z):
    """Dudukan engsel hitam + klip transparan miring -25 deg."""
    frame = box(15.0, 3.5, 3.5, x - 7.5, y - 2.5, z - 2.0)
    validate(prefix + "_FRAME", frame)
    P(parts, prefix + "_FRAME", frame, LATCH_FRAME)

    clip = box(14.0, 2.2, 8.5, 0, 0, 0)
    clip.rotate(V(0, 0, 0), V(1, 0, 0), -25)
    clip.translate(V(x - 7.0, y - 2.7, z + 0.5))
    validate(prefix + "_CLIP", clip)
    P(parts, prefix + "_CLIP", clip, LATCH_CLEAR)


def _screw(parts, prefix, x, y, z):
    """Baut Phillips: kepala silinder + palang (d 3.5)."""
    head = cyl(3.5, 1.0, x, y, z, dirv=(0, 1, 0))
    # palang di muka baut (arah -Y)
    a = box(2.4, 0.5, 0.6, x - 1.2, y - 0.5, z - 0.3)
    b = box(0.6, 0.5, 2.4, x - 0.3, y - 0.5, z - 1.2)
    s = fuse_all([head, a, b])
    validate(prefix, s)
    P(parts, prefix, s, SCREW_BLACK)


def build_socket_pair(parts, prefix, num_left, num_right, offset=(0, 0, 0)):
    """Satu baris pasangan soket. Origin: tengah plat dasar."""
    reg = []
    # ---- Plat dasar + jendela soket ----
    plate = box(PAIR_W, 1.2, PAIR_H, -PAIR_W / 2, -0.2, -PAIR_H / 2)
    w1 = box(22.2, 2.0, 25.2, -PAIR_W / 4 - 0.5 - 11.1, -0.6, -1.0 - 12.6)
    w2 = box(20.2, 2.0, 25.2, PAIR_W / 4 + 0.5 - 10.1, -0.6, -1.0 - 12.6)
    plate = plate.cut(fuse_all([w1, w2]))
    validate(prefix + "_PLATE", plate)
    P(reg, prefix + "_PLATE", plate, PLATE_GREY)

    # ---- Baut tengah atas ----
    _screw(reg, prefix + "_SCREW", 0, -0.6, PAIR_H / 2 - 4.0)

    # ---- SOKET KIRI: Combo 4-in-1 (x=-13, z=-1) ----
    sx, sz = -PAIR_W / 4 - 0.5, -1.0
    P(reg, prefix + "_L_WELL",
      cbox(22.0, 1.0, 25.0, sx, 3.5, sz), WELL_DARK)
    combo_slots = [(2.8, 0.0, 5.0, 2.0), (1.8, 0.0, 2.0, 4.6),
                   (-3.0, 5.2, 4.8, 2.0), (-3.8, 5.2, 2.0, 4.6),
                   (-3.0, -5.2, 4.8, 2.0), (-3.8, -5.2, 2.0, 4.6)]
    combo_pins = [(2.8, 0.0, 5.0, 2.0), (1.8, 0.0, 2.0, 4.6),
                  (-3.0, 5.2, 4.8, 2.0), (-3.8, 5.2, 2.0, 4.6),
                  (-3.0, -5.2, 4.8, 2.0), (-3.8, -5.2, 2.0, 4.6)]
    _socket_face(reg, prefix + "_L_FACE", COMBO_PROFILE, -9.0, 2.6,
                 sx, sz, combo_slots, combo_pins)
    _locking_latch(reg, prefix + "_L_LATCH", sx, 0, sz + 14.0)

    # ---- SOKET KANAN: Standar C13/C15 (x=+13, z=-1) ----
    sx, sz = PAIR_W / 4 + 0.5, -1.0
    P(reg, prefix + "_R_WELL",
      cbox(20.0, 1.0, 25.0, sx, 3.5, sz), WELL_DARK)
    c13_slots = [(-3.0, 0.0, 4.6, 1.8), (3.0, 5.2, 4.6, 1.8),
                 (3.0, -5.2, 4.6, 1.8)]
    c13_pins = c13_slots
    _socket_face(reg, prefix + "_R_FACE", C13_PROFILE, 7.5, 2.5,
                 sx, sz, c13_slots, c13_pins)
    _locking_latch(reg, prefix + "_R_LATCH", sx, 0, sz + 14.0)

    # ---- Strip bawah: LED & nomor outlet ----
    P(reg, prefix + "_STRIP",
      box(PAIR_W - 4.0, 1.2, 3.8, -PAIR_W / 2 + 2.0, -0.8, -PAIR_H / 2 + 1.0),
      STRIP_DARK)
    led_z = -PAIR_H / 2 + 2.9
    P(reg, prefix + "_LED_L",
      cbox(3.2, 0.6, 1.8, -PAIR_W / 2 + 4.5, -1.2, led_z), LED_GREEN)
    P(reg, prefix + "_LED_R",
      cbox(3.2, 0.6, 1.8, PAIR_W / 2 - 4.5, -1.2, led_z), LED_GREEN)

    # Nomor outlet (putar 90 deg, extrude 0.4 ke -Y dari y=-1.2)
    P(reg, prefix + "_NUM_L",
      text3d(str(num_left), 2.4, 0.4, -PAIR_W / 4 - 0.5, -1.2, led_z,
             rotz=90), TEXT_WHITE)
    P(reg, prefix + "_NUM_R",
      text3d(str(num_right), 2.4, 0.4, PAIR_W / 4 + 0.5, -1.2, led_z,
             rotz=90), TEXT_WHITE)

    if any(offset):
        for p in reg:
            p["shape"].translate(V(*offset))
    parts.extend(reg)
    return parts
