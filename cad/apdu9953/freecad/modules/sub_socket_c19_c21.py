# =====================================================================
# sub_socket_c19_c21.py — FreeCAD Solid B-Rep Hybrid C19/C21 Combo Outlet (16A)
# 1:1 REPLIKASI DETAIL OPENSCAD (sub_socket_c19_c21.scad)
# Termasuk:
#  - Bezel Polyamide 42x28 R1.8 dengan lubang ber-chamfer 36x23
#  - Inti Muka Soket Octagonal 32x19 chamfer 3.5
#  - C21 circular notch relief Ø5.0 mm di Z = +8.8
#  - 3x Slot pin kontak horisontal nyata (6.2x1.9 mm)
#  - Indikator LED dome Ø2.2 mm + pinhole optik sensor di Z = +16.2 mm
#  - Housing internal nilon 38x24x18 dengan moat floor 37x24, snap latches & side wings
#  - 3x Klip kontak pegas tembaga/kuningan 16A terotasi 90 derajat
#  - Teks 3D silkscreen nomor outlet (mis. "8", "16", "24")
# =====================================================================
import FreeCAD as App
import Part
from .sub_socket_c13_c15 import build_socket_modular

def build_socket_c19_c21(parts, prefix, outlet_num, center_z, front_y=-23.0,
                         explode=0.0, doc=None, show_number=True,
                         show_fascia_external=True, show_internals=True):
    build_socket_modular(parts, prefix, outlet_num, center_z, front_y,
                         large=True, explode=explode, doc=doc, show_number=show_number,
                         show_fascia_external=show_fascia_external, show_internals=show_internals)
