# =====================================================================
# _common.py — Helper geometri B-Rep & palet warna GSPE
# Dipakai seluruh sub-modul FreeCAD PDU APDU11590SM.
# Konvensi sumbu (identik OpenSCAD): X = lebar, Y = kedalaman
# (front = -Y), Z = tinggi. Satuan: mm.
# =====================================================================
import math
import FreeCAD as App
import Part

# ---------------- Palet Warna Rebranding GSPE ----------------
GSPE_NAVY = (0.000, 0.212, 0.455)    # #003674 Deep Corporate Navy
GSPE_CREAM = (0.980, 1.000, 0.847)   # #FAFFD8 Soft Light Cream
GSPE_BLACK = (0.102, 0.106, 0.110)   # #1A1B1C Matte Dark Chassis
CAP_DARK = (0.090, 0.090, 0.100)
PLATE_GREY = (0.420, 0.440, 0.460)
FACE_GREY = (0.600, 0.620, 0.650)
WELL_DARK = (0.160, 0.170, 0.180)
PIN_DARK = (0.040, 0.040, 0.050)
LATCH_CLEAR = (0.850, 0.900, 0.950)
LATCH_FRAME = (0.120, 0.120, 0.130)
LED_GREEN = (0.000, 0.950, 0.350)
SCREW_BLACK = (0.100, 0.100, 0.100)
STRIP_DARK = (0.150, 0.150, 0.160)
TEXT_WHITE = (0.950, 0.950, 0.950)
BRK_BEZEL = (0.150, 0.150, 0.160)
ROCKER_BLACK = (0.100, 0.100, 0.110)
NMC_BODY = (0.160, 0.165, 0.175)
NMC_BEZEL = (0.110, 0.115, 0.120)
SCREEN_BG = (0.780, 0.860, 0.940)
PORT_METAL = (0.550, 0.570, 0.600)
PORT_DARK = (0.080, 0.080, 0.090)
GOLD_PIN = (0.880, 0.720, 0.240)
BTN_GREY = (0.720, 0.740, 0.760)
BTN_ICON = (0.280, 0.300, 0.320)
DOME_GREEN = (0.150, 0.950, 0.300)
RESET_GREEN = (0.150, 0.750, 0.350)
LED_AMBER = (0.980, 0.820, 0.100)
LED_RED = (0.950, 0.150, 0.120)
WHIP_BLACK = (0.040, 0.040, 0.045)
BOOT_BLACK = (0.050, 0.050, 0.055)
PLUG_RED = (0.650, 0.100, 0.120)
PLUG_REDDARK = (0.450, 0.070, 0.090)
PIN_SILVER = (0.720, 0.720, 0.740)
PEG_ZINC = (0.550, 0.560, 0.580)

FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"

V = App.Vector


def P(parts, name, shape, color, offset=None):
    """Daftarkan part ke daftar assembly. offset opsional (x,y,z) diterapkan
    sebelum registrasi."""
    if offset is not None and any(offset):
        shape.translate(V(*offset))
    parts.append({"name": name, "shape": shape, "color": color})
    return shape


def validate(name, shape):
    assert shape is not None and not shape.isNull(), "Part %s is null!" % name
    assert shape.isValid(), "Part %s is invalid!" % name
    return shape


# ---------------- Primitive B-Rep ----------------
def box(l, w, h, x, y, z):
    """Kotak dari sudut (x,y,z) — meniru translate+cube OpenSCAD."""
    return Part.makeBox(l, w, h, V(x, y, z))


def cbox(l, w, h, cx, cy, cz):
    """Kotak terpusat pada (cx,cy,cz)."""
    return Part.makeBox(l, w, h, V(cx - l / 2, cy - w / 2, cz - h / 2))


def cyl(d, h, x, y, z, dirv=(0, 0, 1)):
    return Part.makeCylinder(d / 2, h, V(x, y, z), V(*dirv))


def cone(d1, d2, h, x, y, z):
    return Part.makeCone(d1 / 2, d2 / 2, h, V(x, y, z))


def sph(d, x, y, z):
    return Part.makeSphere(d / 2, V(x, y, z))


def polygon_prism(points_xz, y0, depth):
    """Prisma dari poligon XZ (list [(x,z),...]) pada bidang y=y0,
    diekstrusi ke arah +Y sejauh depth."""
    pts = [V(x, y0, z) for x, z in points_xz]
    wire = Part.Wire(Part.makePolygon(pts + [pts[0]]).Edges)
    return Part.Face(wire).extrude(V(0, depth, 0))


def prism_neg_y(points_xz, y_front, depth):
    """Prisma poligon XZ, diekstrusi ke arah -Y dari y_front."""
    pts = [V(x, y_front, z) for x, z in points_xz]
    wire = Part.Wire(Part.makePolygon(pts + [pts[0]]).Edges)
    return Part.Face(wire).extrude(V(0, -depth, 0))


def hex_prism(af, h, x, y, z):
    """Prisma heksagon (across-flats af) dari sudut (x,y,z)."""
    r = af / 2 / math.cos(math.radians(30))
    pts = [V(x + r * math.cos(math.radians(a)),
             y + r * math.sin(math.radians(a)), z) for a in range(0, 360, 60)]
    wire = Part.Wire(Part.makePolygon(pts + [pts[0]]).Edges)
    return Part.Face(wire).extrude(V(0, 0, h))


def rounded_rect_wire(w, d, r, z=0.0):
    """Wire rounded-rectangle di bidang XY (tertutup, CCW)."""
    lines = [
        Part.makeLine(V(-w / 2 + r, -d / 2, z), V(w / 2 - r, -d / 2, z)),
        Part.makeCircle(r, V(w / 2 - r, -d / 2 + r, z), V(0, 0, 1), 270, 360),
        Part.makeLine(V(w / 2, -d / 2 + r, z), V(w / 2, d / 2 - r, z)),
        Part.makeCircle(r, V(w / 2 - r, d / 2 - r, z), V(0, 0, 1), 0, 90),
        Part.makeLine(V(w / 2 - r, d / 2, z), V(-w / 2 + r, d / 2, z)),
        Part.makeCircle(r, V(-w / 2 + r, d / 2 - r, z), V(0, 0, 1), 90, 180),
        Part.makeLine(V(-w / 2, d / 2 - r, z), V(-w / 2, -d / 2 + r, z)),
        Part.makeCircle(r, V(-w / 2 + r, -d / 2 + r, z), V(0, 0, 1), 180, 270),
    ]
    return Part.Wire(lines)


def rounded_prism(w, d, r, h, z=0.0):
    return Part.Face(rounded_rect_wire(w, d, r, z)).extrude(V(0, 0, h))


def fuse_all(shapes):
    if len(shapes) == 1:
        return shapes[0]
    return shapes[0].fuse(shapes[1:])


def cut_epsilon(tool, eps=0.05):
    """Kembali tidak dipakai langsung — dokumentasi offset boolean."""
    return tool


# ---------------- Teks ukir (Draft ShapeString) ----------------
_TEXT_DOC = None


def text3d(string, size, depth, x, y, z, rotz=0.0, halign="center"):
    """Solid teks extrude. Teks di bidang XY (terbaca dari +Z),
    diputar Rx90 (menghadap -Y/front), rotasi bidang rotz CCW.
    halign: 'center', 'left', atau 'right'."""
    global _TEXT_DOC
    if _TEXT_DOC is None:
        _TEXT_DOC = App.newDocument("_txt")
    App.setActiveDocument("_txt")
    import Draft
    obj = Draft.makeShapeString(string, FONT, size, 0.0)
    _TEXT_DOC.recompute()
    bb = obj.Shape.BoundBox
    sh = obj.Shape.extrude(V(0, 0, depth))
    comp = Part.makeCompound(list(sh.Solids))
    _TEXT_DOC.removeObject(obj.Name)
    if halign == "center":
        comp.translate(V(-bb.XLength / 2, -bb.YLength / 2, 0))
    elif halign == "right":
        comp.translate(V(-bb.XLength, -bb.YLength / 2, 0))
    elif halign == "left":
        comp.translate(V(0, -bb.YLength / 2, 0))
    if rotz:
        comp.rotate(V(0, 0, 0), V(0, 0, 1), rotz)
    comp.rotate(V(0, 0, 0), V(1, 0, 0), 90)
    comp.translate(V(x, y, z))
    return comp
