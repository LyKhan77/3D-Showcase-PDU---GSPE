# =====================================================================
# export_mesh_for_blender.py
# Mengekspor rakitan B-Rep FreeCAD PDU APDU11590SM menjadi mesh OBJ
# terpisah per kelompok material PBR ke temp/blender_staging/
# =====================================================================
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import FreeCAD as App
import Mesh
import MeshPart
from pdu_assembly import collect_parts
from modules._common import (
    GSPE_NAVY, GSPE_CREAM, GSPE_BLACK, CAP_DARK, PLATE_GREY, FACE_GREY,
    WELL_DARK, PIN_DARK, LATCH_CLEAR, LATCH_FRAME, LED_GREEN, SCREW_BLACK,
    STRIP_DARK, TEXT_WHITE, BRK_BEZEL, ROCKER_BLACK, NMC_BODY, NMC_BEZEL,
    SCREEN_BG, PORT_METAL, PORT_DARK, GOLD_PIN, BTN_GREY, BTN_ICON,
    DOME_GREEN, RESET_GREEN, LED_AMBER, LED_RED, WHIP_BLACK, BOOT_BLACK,
    PLUG_RED, PLUG_REDDARK, PIN_SILVER, PEG_ZINC
)

STAGING_DIR = "/Users/leekhan/project/3D-Model-PDU/temp/blender_staging"
os.makedirs(STAGING_DIR, exist_ok=True)

# Pemetaan warna part ke ID material Blender
MAT_MAPPING = {
    # 1. Matte powdercoat chassis & caps
    "mat_chassis_powdercoat": [GSPE_BLACK, CAP_DARK],
    # 2. Rebranding GSPE Primary Corporate Navy (#003674)
    "mat_gspe_navy": [GSPE_NAVY],
    # 3. Rebranding GSPE Secondary Light Cream (#FAFFD8)
    "mat_gspe_cream": [GSPE_CREAM],
    # 4. Shielding steel / zinc plated hardware
    "mat_shielding_steel": [PORT_METAL, PEG_ZINC, PIN_SILVER],
    # 5. Gold contact pins 8P8C & USB fingers
    "mat_gold_pin": [GOLD_PIN],
    # 6. Socket well & dark plastics
    "mat_socket_body_dark": [WELL_DARK, STRIP_DARK, NMC_BODY, NMC_BEZEL,
                             ROCKER_BLACK, BRK_BEZEL, PORT_DARK],
    # 7. Socket 4-in-1 hybrid faceplates
    "mat_socket_face_grey": [FACE_GREY, PLATE_GREY],
    # 8. Pin cavity dark
    "mat_pin_dark": [PIN_DARK],
    # 9. Clear polycarbonate latch
    "mat_latch_clear": [LATCH_CLEAR, LATCH_FRAME],
    # 10. Black Phillips screws
    "mat_screw_black": [SCREW_BLACK],
    # 11. White printed text & button icons
    "mat_text_white": [TEXT_WHITE, BTN_ICON],
    # 12. Navigation buttons light grey
    "mat_btn_grey": [BTN_GREY],
    # 13. LCD screen display
    "mat_lcd_screen": [SCREEN_BG],
    # 14. Dome LED 3D (green power indicator)
    "mat_led_dome_green": [DOME_GREEN],
    # 15. Status LED Okay & Reset
    "mat_led_okay_green": [LED_GREEN, RESET_GREEN],
    # 16. Status LED Warning & Link Amber
    "mat_led_warn_amber": [LED_AMBER],
    # 17. Status LED Overload Red
    "mat_led_overload_red": [LED_RED],
    # 18. Rubber cable jacket & boot
    "mat_whip_cable": [WHIP_BLACK, BOOT_BLACK],
    # 19. Red industrial plug IEC 60309
    "mat_plug_red": [PLUG_RED, PLUG_REDDARK],
}


def color_matches(c1, c2, tol=0.01):
    return (abs(c1[0] - c2[0]) < tol and
            abs(c1[1] - c2[1]) < tol and
            abs(c1[2] - c2[2]) < tol)


def get_material_group(col):
    for mat_name, colors in MAT_MAPPING.items():
        for c in colors:
            if color_matches(col, c):
                return mat_name
    return "mat_default_grey"


def main():
    t0 = time.time()
    print("[MESH EXPORT] Mengumpulkan rakitan solid B-Rep...")
    parts = collect_parts()
    print("[MESH EXPORT] %d part berhasil dirakit (%.2fs)" % (len(parts), time.time() - t0))

    # Kelompokkan part berdasarkan material
    groups = {}
    for p in parts:
        mat = get_material_group(p["color"])
        groups.setdefault(mat, []).append(p)

    print("[MESH EXPORT] Ditemukan %d kelompok material. Mulai tesselasi mesh..." % len(groups))

    total_facets = 0
    for mat_name, p_list in groups.items():
        t_mat = time.time()
        combined_mesh = None

        for p in p_list:
            sh = p["shape"]
            # Tesselasi solid B-Rep ke triangulated mesh
            # LinearDeflection = 0.08mm untuk kurva halus (pin, dome, fillet)
            try:
                m = MeshPart.meshFromShape(sh, LinearDeflection=0.08, AngularDeflection=0.45)
                if combined_mesh is None:
                    combined_mesh = m
                else:
                    combined_mesh.addMesh(m)
            except Exception as e:
                print("  [WARN] Gagal tesselasi %s: %s" % (p["name"], str(e)))

        if combined_mesh and combined_mesh.CountFacets > 0:
            out_path = os.path.join(STAGING_DIR, "%s.obj" % mat_name)
            combined_mesh.write(out_path)
            total_facets += combined_mesh.CountFacets
            print("  -> %-24s: %4d part, %7d facets, %.2fs" %
                  (mat_name, len(p_list), combined_mesh.CountFacets, time.time() - t_mat))

    print("[MESH EXPORT] SELESAI. Total facets: %d dalam %.2f detik" % (total_facets, time.time() - t0))


if __name__ == "__main__" or __name__ == "export_mesh_for_blender":
    main()
