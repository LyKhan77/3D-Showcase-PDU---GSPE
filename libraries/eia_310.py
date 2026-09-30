"""
EIA-310 Standard Constants (in millimeters)
Reference standard for 19-inch Server Racks and Rackmount Equipment
"""

U_HEIGHT = 44.45              # 1U = 1.75 inches
RACK_PANEL_WIDTH = 482.6       # 19.0 inches
RACK_MOUNTING_PITCH = 465.1    # Distance between rail hole centers
RACK_INTERNAL_CLEARANCE = 450.0# Clearance between vertical rails

# Vertical hole offsets from the bottom edge of any 1U slot:
HOLE_OFFSETS_IN_U = [6.35, 22.225, 38.10]

# Standard hole dimensions
CAGE_NUT_HOLE_SIZE = 9.5       # 9.5mm x 9.5mm square
M6_CLEARANCE_HOLE_DIA = 6.4    # M6 mounting bolt clearance hole
M5_CLEARANCE_HOLE_DIA = 5.3

# Standard sheet metal thicknesses for racks & PDUs
SHEET_METAL_16GA = 1.5         # 1.5mm (common for brackets & chassis)
SHEET_METAL_14GA = 2.0         # 2.0mm (heavy-duty vertical rails)
SHEET_METAL_18GA = 1.2         # 1.2mm (internal covers / covers)

def get_u_holes(u_index: int):
    """Mengembalikan posisi Z vertikal (mm) untuk 3 lubang pada slot U tertentu (0-indexed)."""
    base_z = u_index * U_HEIGHT
    return [base_z + offset for offset in HOLE_OFFSETS_IN_U]
