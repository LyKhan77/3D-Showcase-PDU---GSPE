# =====================================================================
# _common.py — FreeCAD B-Rep Solid Helpers, 1:1 Primitives & Layout Single Truth
# APDU9953 NetShelter 9000 Switched Rack PDU (24-Outlet)
# Unit: mm. Sumbu: X = lebar (+/-28), Y = tebal (front = -Y, rear = +Y),
#                  Z = tinggi (0 s/d 1829).
# =====================================================================
import math
import FreeCAD as App
import Part
import Draft

V = App.Vector

# ---------------- Palet Warna GSPE & Material Industri ----------------
GSPE_NAVY    = (0.000, 0.212, 0.455)   # #003674 Primary Navy
GSPE_CREAM   = (0.980, 1.000, 0.847)   # #FAFFD8 Secondary Light Cream
CHASSIS_DARK = (0.100, 0.105, 0.115)   # #1A1B1C Powder-coated dark chassis
POLY_DARK    = (0.165, 0.180, 0.224)   # #2A2E39 Polyamide / socket body
METAL_STEEL  = (0.580, 0.600, 0.630)   # #939BA4 Stainless & steel fasteners
COPPER       = (0.773, 0.545, 0.286)   # #C58B49 Busbars & spring clips
BRASS_GOLD   = (0.843, 0.710, 0.325)   # #D7B553 Terminal lugs & ground stud
PCB_GREEN    = (0.090, 0.392, 0.263)   # #176443 FR-4 PCB substrate
LCD_SCREEN   = (0.040, 0.050, 0.070)   # OLED / TFT display face
PLUG_BLUE    = (0.000, 0.300, 0.750)   # IEC 60309 32A Blue
LED_WHITE    = (0.950, 0.950, 0.950)   # Translucent dome LED
LED_GREEN    = (0.000, 0.900, 0.450)   # Status OK LED
LED_AMBER    = (1.000, 0.700, 0.000)   # Warning LED
LED_RED      = (0.900, 0.200, 0.200)   # Overload LED
BAKELITE_BLK = (0.080, 0.085, 0.095)   # Breaker internal body
NYLON_WHITE  = (0.880, 0.880, 0.850)   # Busbar insulator saddles
FPC_AMBER    = (0.706, 0.490, 0.208)   # Kapton FPC ribbon cable

FONT_ARIAL = "/System/Library/Fonts/Supplemental/Arial.ttf"

# ---------------- Layout Single Source of Truth ----------------
LAYOUT_H       = 1829.0
LAYOUT_BANK_Z  = [1159.5, 669.5, 329.5]   # Bank 1, 2, 3 (center Z)
LAYOUT_BRK_Z   = [1329.5, 499.5]          # Breaker 1, 2
LAYOUT_NMC_Z   = 914.5                    # NMC3 Cassette
LAYOUT_FRONT_Y = -23.0
LAYOUT_REAR_Y  =  23.0

def bank_carrier_pts(zc):
    return [(x, zc + dz) for x in [-19.0, 19.0] for dz in [-110.0, 110.0]]

def bank_relay_pts(zc):
    return [(x, zc + dz) for x in [-20.0, 20.0] for dz in [-113.0, 113.0]]

def brk_retainer_pts(zc):
    return [(-7.0, zc + dz) for dz in [-14.0, 14.0]]

def nmc_tray_pts(zc):
    return [(x, zc + dz) for x in [-21.0, 21.0] for dz in [-101.0, 101.0]]

def nmc_pcb_pts(zc):
    return [(x, zc + dz) for x in [-21.0, 21.0] for dz in [-96.0, 96.0]]

def fascia_side_z(zc):
    return [zc - 100.0, zc + 100.0]

def terminal_bracket_pts():
    return [(x, y) for x in [-14.0, 14.0] for y in [-9.0, 9.0]]

# ---------------- Part Registry Helper ----------------
def P(parts, name, shape, color, offset=None):
    """Mendaftarkan solid part ke list master assembly."""
    if offset is not None and any(offset):
        shape.translate(V(*offset))
    parts.append({"name": name, "shape": shape, "color": color})
    return shape

def validate(name, shape):
    assert shape is not None and not shape.isNull(), f"Part {name} is null!"
    assert shape.isValid(), f"Part {name} is invalid solid!"
    return shape

# ---------------- Solid Geometri Primitif ----------------
def box(l, w, h, x, y, z):
    """Box dari sudut minimum (x, y, z)."""
    return Part.makeBox(l, w, h, V(x, y, z))

def cbox(l, w, h, cx, cy, cz):
    """Box berpusat pada (cx, cy, cz)."""
    return Part.makeBox(l, w, h, V(cx - l / 2, cy - w / 2, cz - h / 2))

def cyl(d, h, x, y, z, dirv=(0, 0, 1)):
    """Silinder sepanjang dirv dengan diameter d dan tinggi h."""
    return Part.makeCylinder(d / 2, h, V(x, y, z), V(*dirv))

def cone(d1, d2, h, x, y, z, dirv=(0, 0, 1)):
    """Kerucut/cone terpancung."""
    return Part.makeCone(d1 / 2, d2 / 2, h, V(x, y, z), V(*dirv))

def sph(d, x, y, z):
    """Bola terpusat pada (x, y, z)."""
    return Part.makeSphere(d / 2, V(x, y, z))

def hex_prism(af, h, x, y, z, dirv=(0, 0, 1)):
    """Prisma segienam (across-flats af) sepanjang dirv."""
    r = af / 2 / math.cos(math.radians(30))
    dv = V(*dirv).normalize()
    if abs(dv.z) > 0.9:
        pts = [V(x + r * math.cos(math.radians(a)),
                 y + r * math.sin(math.radians(a)), z) for a in range(0, 360, 60)]
    elif abs(dv.y) > 0.9:
        pts = [V(x + r * math.cos(math.radians(a)),
                 y, z + r * math.sin(math.radians(a))) for a in range(0, 360, 60)]
    else:
        pts = [V(x, y + r * math.cos(math.radians(a)),
                 z + r * math.sin(math.radians(a))) for a in range(0, 360, 60)]
    wire = Part.Wire(Part.makePolygon(pts + [pts[0]]).Edges)
    return Part.Face(wire).extrude(dv * h)

def rounded_rect_wire(w, h, r, z=0.0):
    """Wire persegi rounded di bidang XY."""
    lines = [
        Part.makeLine(V(-w / 2 + r, -h / 2, z), V(w / 2 - r, -h / 2, z)),
        Part.makeCircle(r, V(w / 2 - r, -h / 2 + r, z), V(0, 0, 1), 270, 360),
        Part.makeLine(V(w / 2, -h / 2 + r, z), V(w / 2, h / 2 - r, z)),
        Part.makeCircle(r, V(w / 2 - r, h / 2 - r, z), V(0, 0, 1), 0, 90),
        Part.makeLine(V(w / 2 - r, h / 2, z), V(-w / 2 + r, h / 2, z)),
        Part.makeCircle(r, V(-w / 2 + r, h / 2 - r, z), V(0, 0, 1), 90, 180),
        Part.makeLine(V(-w / 2, h / 2 - r, z), V(-w / 2, -h / 2 + r, z)),
        Part.makeCircle(r, V(-w / 2 + r, -h / 2 + r, z), V(0, 0, 1), 180, 270),
    ]
    return Part.Wire(lines)

def rounded_prism_z(w, d, r, h, z0=0.0):
    """Prisma rounded di bidang XY, diekstrusi ke +Z."""
    return Part.Face(rounded_rect_wire(w, d, r, z0)).extrude(V(0, 0, h))

def rounded_prism_y(w, h, r, depth, y0=0.0):
    """Prisma rounded di bidang XZ, diekstrusi ke arah Y."""
    w_wire = rounded_rect_wire(w, h, r, 0.0)
    solid = Part.Face(w_wire).extrude(V(0, 0, depth))
    solid.rotate(V(0, 0, 0), V(1, 0, 0), -90)
    solid.translate(V(0, y0, 0))
    return solid

def polygon_prism_xz(pts_xz, depth, y0=0.0):
    """Prisma dari 2D polygon pada bidang XZ, diekstrusi sepanjang +Y dari y0."""
    pts = [V(float(px), y0, float(pz)) for px, pz in pts_xz]
    poly = Part.makePolygon(pts + [pts[0]])
    wire = Part.Wire(poly.Edges)
    return Part.Face(wire).extrude(V(0.0, depth, 0.0))

def wire_between(p1, p2, diameter):
    """Round straight wire segment, matching OpenSCAD wire_between."""
    start, end = V(*p1), V(*p2)
    delta = end - start
    return Part.makeCylinder(diameter / 2, delta.Length, start, delta.normalize()).fuse(
        [Part.makeSphere(diameter / 2, start), Part.makeSphere(diameter / 2, end)])

def socket_octagon_pts(w, h, chamfer=4.0):
    """Profil poligon 8 sisi untuk inti soket IEC C13/C15/C19/C21."""
    return [
        (-w / 2 + 1, h / 2),
        (w / 2 - 1, h / 2),
        (w / 2, h / 2 - 1),
        (w / 2, -h / 2 + chamfer),
        (w / 2 - chamfer, -h / 2),
        (-w / 2 + chamfer, -h / 2),
        (-w / 2, -h / 2 + chamfer),
        (-w / 2, h / 2 - 1)
    ]

# ---------------- Fasteners: True Torx T15 Star Drive ----------------
def make_torx_t15_cutter(p0, dv, depth=0.85):
    """Pemotong soket bintang 6-lobe Torx T15."""
    if abs(dv.y) > 0.9:
        u = V(1, 0, 0)
        v = V(0, 0, 1)
    elif abs(dv.x) > 0.9:
        u = V(0, 1, 0)
        v = V(0, 0, 1)
    else:
        u = V(1, 0, 0)
        v = V(0, 1, 0)

    cutter = Part.makeCylinder(3.27 / 2, depth + 0.1, p0 - dv * 0.05, dv)
    for a in range(0, 360, 60):
        rad = math.radians(a)
        cx = 1.88 * math.cos(rad)
        cy = 1.88 * math.sin(rad)
        cp = p0 + u * cx + v * cy - dv * 0.1
        cut_cyl = Part.makeCylinder(0.75, depth + 0.2, cp, dv)
        cutter = cutter.cut(cut_cyl)
    return cutter

def torx_screw_csk(head_d=6.0, shaft_d=2.8, length=6.0, x=0.0, y=0.0, z=0.0, dirv=(0, 1, 0)):
    """Sekrup countersunk Torx T15 bintang 6-lobe."""
    dv = V(*dirv).normalize()
    p0 = V(x, y, z)
    c = Part.makeCone(head_d / 2, shaft_d / 2, 1.2, p0, dv)
    s = Part.makeCylinder(shaft_d / 2, length, p0 + dv * 1.2, dv)
    screw = c.fuse(s)
    cutter = make_torx_t15_cutter(p0, dv, 0.75)
    return screw.cut(cutter)

def torx_screw(head_d=5.4, shaft_d=2.8, length=6.0, x=0.0, y=0.0, z=0.0, dirv=(0, 1, 0)):
    """Sekrup pan head Torx T15 bintang 6-lobe."""
    dv = V(*dirv).normalize()
    p0 = V(x, y, z)
    head = Part.makeCylinder(head_d / 2, 1.25, p0, dv)
    shaft = Part.makeCylinder(shaft_d / 2, length, p0 + dv * 1.2, dv)
    screw = head.fuse(shaft)
    cutter = make_torx_t15_cutter(p0, dv, 0.75)
    return screw.cut(cutter)

def side_torx_screw(dir=1, length=4.5, head_d=5.4, shaft_d=2.8, y=0.0, z=0.0):
    """Sekrup countersunk samping Torx T15 pada sumbu X."""
    x = 29.5 if dir > 0 else -29.5
    dirv = (-1, 0, 0) if dir > 0 else (1, 0, 0)
    return torx_screw_csk(head_d=head_d, shaft_d=shaft_d, length=length, x=x, y=y, z=z, dirv=dirv)

def threaded_insert(dir=1, y=0.0, z=0.0):
    """Insert kuningan berulir press-fit pada dinding samping (sumbu X)."""
    x = 24.5 if dir > 0 else -24.5
    dirv = (-1, 0, 0) if dir > 0 else (1, 0, 0)
    dv = V(*dirv)
    p0 = V(x, y, z)
    outer = Part.makeCylinder(2.5, 3.5, p0, dv)
    inner = Part.makeCylinder(1.2, 4.0, p0 - dv * 0.1, dv)
    return outer.cut(inner)

# ---------------- Solid Typography & 3D Silkscreen ----------------
def make_text_solid(text, size, thickness, x, y, z, angle_deg=0.0, doc=None):
    """Menghasilkan teks 3D solid menghadap -Y (bidang muka)."""
    if doc is None:
        doc = App.ActiveDocument
        if doc is None:
            doc = App.newDocument("TextDoc")
    ss = Draft.make_shapestring(text, FONT_ARIAL, size)
    doc.recompute()
    sh = ss.Shape.copy()
    bb = sh.BoundBox
    # Tengahkan teks
    sh.translate(V(-(bb.XMin + bb.XMax) / 2.0, -(bb.YMin + bb.YMax) / 2.0, 0.0))
    if angle_deg != 0.0:
        sh.rotate(V(0.0, 0.0, 0.0), V(0.0, 0.0, 1.0), angle_deg)
    # Putar ke bidang XZ menghadap -Y; +90 preserves OpenSCAD face_print reading direction.
    sh.rotate(V(0.0, 0.0, 0.0), V(1.0, 0.0, 0.0), 90.0)
    solid = sh.extrude(V(0.0, -thickness, 0.0))
    solid.translate(V(x, y, z))
    return solid

def fuse_all(shapes):
    if not shapes:
        return None
    if len(shapes) == 1:
        return shapes[0]
    return shapes[0].fuse(shapes[1:])
