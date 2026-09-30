# =====================================================================
# build_pbr_scene.py
# Script otomasi Blender 5.2 LTS:
# 1. Impor seluruh kelompok mesh OBJ dari temp/blender_staging/
# 2. Terapkan shader PBR Principled BSDF & Emission
# 3. Setup pencahayaan studio 3-point & kamera berorientasi CAD presisi
# 4. Render 3 foto studio ke previews/
# 5. Ekspor master Web 3D GLB ke exports/glb/gspe_pdu_apdu11590sm.glb
# =====================================================================
import os
import sys
import glob
import math
import time
import bpy

STAGING_DIR = "/Users/leekhan/project/3D-Model-PDU/temp/blender_staging"
OUTPUT_GLB = "/Users/leekhan/project/3D-Model-PDU/exports/glb/gspe_pdu_apdu11590sm.glb"
PREVIEW_DIR = "/Users/leekhan/project/3D-Model-PDU/previews"
os.makedirs(PREVIEW_DIR, exist_ok=True)
os.makedirs(os.path.dirname(OUTPUT_GLB), exist_ok=True)


def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def srgb_tuple(r, g, b):
    return (srgb_to_lin(r), srgb_to_lin(g), srgb_to_lin(b), 1.0)


# Konfigurasi PBR Material Dictionary
MAT_SPECS = {
    "mat_chassis_powdercoat": {
        "color": srgb_tuple(0.102, 0.106, 0.110),
        "metallic": 0.0,
        "roughness": 0.65,
    },
    "mat_gspe_navy": {
        "color": srgb_tuple(0.000, 0.212, 0.455),   # #003674 Deep Navy
        "metallic": 0.08,
        "roughness": 0.35,
    },
    "mat_gspe_cream": {
        "color": srgb_tuple(0.980, 1.000, 0.847),   # #FAFFD8 Soft Cream
        "metallic": 0.0,
        "roughness": 0.28,
    },
    "mat_shielding_steel": {
        "color": srgb_tuple(0.68, 0.70, 0.73),
        "metallic": 0.88,
        "roughness": 0.28,
    },
    "mat_gold_pin": {
        "color": srgb_tuple(0.92, 0.76, 0.18),
        "metallic": 0.95,
        "roughness": 0.20,
    },
    "mat_socket_body_dark": {
        "color": srgb_tuple(0.06, 0.065, 0.07),
        "metallic": 0.0,
        "roughness": 0.55,
    },
    "mat_socket_face_grey": {
        "color": srgb_tuple(0.58, 0.60, 0.63),
        "metallic": 0.0,
        "roughness": 0.38,
    },
    "mat_pin_dark": {
        "color": srgb_tuple(0.04, 0.04, 0.05),
        "metallic": 0.0,
        "roughness": 0.80,
    },
    "mat_latch_clear": {
        "color": srgb_tuple(0.85, 0.90, 0.95),
        "metallic": 0.0,
        "roughness": 0.15,
        "transmission": 0.85,
        "ior": 1.52,
    },
    "mat_screw_black": {
        "color": srgb_tuple(0.10, 0.10, 0.10),
        "metallic": 0.80,
        "roughness": 0.40,
    },
    "mat_text_white": {
        "color": srgb_tuple(0.95, 0.95, 0.95),
        "metallic": 0.0,
        "roughness": 0.25,
    },
    "mat_btn_grey": {
        "color": srgb_tuple(0.72, 0.74, 0.76),
        "metallic": 0.0,
        "roughness": 0.32,
    },
    "mat_lcd_screen": {
        "color": srgb_tuple(0.78, 0.86, 0.94),
        "emission": srgb_tuple(0.78, 0.86, 0.94),
        "emission_strength": 1.5,
        "metallic": 0.0,
        "roughness": 0.35,
    },
    "mat_led_dome_green": {
        "color": srgb_tuple(0.08, 0.95, 0.25),
        "emission": srgb_tuple(0.08, 0.95, 0.25),
        "emission_strength": 5.0,
        "roughness": 0.15,
    },
    "mat_led_okay_green": {
        "color": srgb_tuple(0.08, 0.95, 0.25),
        "emission": srgb_tuple(0.08, 0.95, 0.25),
        "emission_strength": 4.0,
        "roughness": 0.20,
    },
    "mat_led_warn_amber": {
        "color": srgb_tuple(1.00, 0.70, 0.08),
        "emission": srgb_tuple(1.00, 0.70, 0.08),
        "emission_strength": 4.0,
        "roughness": 0.20,
    },
    "mat_led_overload_red": {
        "color": srgb_tuple(1.00, 0.12, 0.08),
        "emission": srgb_tuple(1.00, 0.12, 0.08),
        "emission_strength": 4.0,
        "roughness": 0.20,
    },
    "mat_whip_cable": {
        "color": srgb_tuple(0.04, 0.04, 0.045),
        "metallic": 0.0,
        "roughness": 0.70,
    },
    "mat_plug_red": {
        "color": srgb_tuple(0.65, 0.10, 0.12),
        "metallic": 0.0,
        "roughness": 0.40,
    },
    "mat_default_grey": {
        "color": srgb_tuple(0.5, 0.5, 0.5),
        "metallic": 0.0,
        "roughness": 0.5,
    }
}


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    world = bpy.data.worlds.new("StudioWorld")
    bpy.context.scene.world = world
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs["Color"].default_value = srgb_tuple(0.12, 0.13, 0.15)
        bg_node.inputs["Strength"].default_value = 1.0


def create_pbr_material(name, spec):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")

    if bsdf:
        if "color" in spec:
            bsdf.inputs["Base Color"].default_value = spec["color"]
        if "metallic" in spec:
            bsdf.inputs["Metallic"].default_value = spec["metallic"]
        if "roughness" in spec:
            bsdf.inputs["Roughness"].default_value = spec["roughness"]
        if "emission" in spec:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = spec["emission"]
                bsdf.inputs["Emission Strength"].default_value = spec.get("emission_strength", 1.0)
            elif "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = spec["emission"]
                if "Emission Strength" in bsdf.inputs:
                    bsdf.inputs["Emission Strength"].default_value = spec.get("emission_strength", 1.0)
        if "transmission" in spec:
            if "Transmission Weight" in bsdf.inputs:
                bsdf.inputs["Transmission Weight"].default_value = spec["transmission"]
            elif "Transmission" in bsdf.inputs:
                bsdf.inputs["Transmission"].default_value = spec["transmission"]
        if "ior" in spec and "IOR" in bsdf.inputs:
            bsdf.inputs["IOR"].default_value = spec["ior"]

    return mat


def setup_lighting():
    # 1. Key Light (Area light besar dari kanan depan di +Y)
    key_data = bpy.data.lights.new(name="KeyLight", type='AREA')
    key_data.energy = 220.0
    key_data.size = 1.2
    key_data.color = (1.0, 0.98, 0.95)
    key_obj = bpy.data.objects.new(name="KeyLight", object_data=key_data)
    key_obj.location = (0.6, 1.2, 1.5)
    bpy.context.collection.objects.link(key_obj)

    # 2. Fill Light (Area light lembut dari kiri depan di +Y)
    fill_data = bpy.data.lights.new(name="FillLight", type='AREA')
    fill_data.energy = 110.0
    fill_data.size = 1.5
    fill_data.color = (0.95, 0.98, 1.0)
    fill_obj = bpy.data.objects.new(name="FillLight", object_data=fill_data)
    fill_obj.location = (-0.7, 1.0, 1.1)
    bpy.context.collection.objects.link(fill_obj)

    # 3. Rim / Edge Light (Strip light dari belakang di -Y untuk kontur chassis)
    rim_data = bpy.data.lights.new(name="RimLight", type='AREA')
    rim_data.energy = 160.0
    rim_data.size = 1.8
    rim_data.color = (1.0, 1.0, 1.0)
    rim_obj = bpy.data.objects.new(name="RimLight", object_data=rim_data)
    rim_obj.location = (0.3, -0.8, 1.8)
    bpy.context.collection.objects.link(rim_obj)


def setup_tracked_camera(name, loc, target_loc, focal_length=50):
    cam_data = bpy.data.cameras.new(name=name)
    cam_data.lens = focal_length
    cam_data.clip_start = 0.01
    cam_data.clip_end = 20.0
    cam_obj = bpy.data.objects.new(name=name, object_data=cam_data)
    cam_obj.location = loc
    bpy.context.collection.objects.link(cam_obj)

    target = bpy.data.objects.new(name=name + "_Target", object_data=None)
    target.location = target_loc
    bpy.context.collection.objects.link(target)

    track = cam_obj.constraints.new(type='TRACK_TO')
    track.target = target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'
    return cam_obj


def main():
    t0 = time.time()
    print("[BLENDER] Memulai setup scene PBR & Studio Lighting...")
    clear_scene()

    # Buat seluruh material PBR
    materials = {}
    for mat_name, spec in MAT_SPECS.items():
        materials[mat_name] = create_pbr_material(mat_name, spec)

    # Impor seluruh OBJ dari staging dengan orientasi CAD (Z-Up, -Y Forward, scale=0.001)
    obj_files = sorted(glob.glob(os.path.join(STAGING_DIR, "*.obj")))
    print("[BLENDER] Ditemukan %d file mesh OBJ di staging." % len(obj_files))

    imported_objects = []
    for filepath in obj_files:
        base = os.path.splitext(os.path.basename(filepath))[0]
        bpy.ops.wm.obj_import(filepath=filepath, up_axis='Z', forward_axis='NEGATIVE_Y', global_scale=0.001)
        new_objs = [o for o in bpy.context.selected_objects if o.type == 'MESH']
        for o in new_objs:
            o.name = base
            imported_objects.append(o)
            mat = materials.get(base, materials["mat_default_grey"])
            o.data.materials.clear()
            o.data.materials.append(mat)

    print("[BLENDER] %d objek mesh berhasil diimpor & diberi material PBR." % len(imported_objects))

    setup_lighting()

    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.film_transparent = False

    # -------------------------------------------------------------
    # 1. CAMERA 1: Full Isometric Studio View
    # PDU setinggi ~2.03m (Z: 0 .. 2.03m). Target tengah di Z = 1.05m.
    # Muka depan PDU di Blender menghadap +Y (+0.043m)
    # -------------------------------------------------------------
    cam_iso = setup_tracked_camera("Cam_Studio_Iso",
                                  loc=(0.9, 1.8, 1.4),
                                  target_loc=(0.0, 0.04, 1.05),
                                  focal_length=50)

    # -------------------------------------------------------------
    # 2. CAMERA 2: Closeup NMC Controller Display (Z = 1.00m)
    # -------------------------------------------------------------
    cam_disp = setup_tracked_camera("Cam_Display_Closeup",
                                   loc=(0.0, 0.28, 1.00),
                                   target_loc=(0.0, 0.043, 1.00),
                                   focal_length=65)

    # -------------------------------------------------------------
    # 3. CAMERA 3: Closeup Socket Bank & Breaker Box (Z = 0.65m)
    # -------------------------------------------------------------
    cam_sock = setup_tracked_camera("Cam_Socket_Closeup",
                                   loc=(0.18, 0.38, 0.68),
                                   target_loc=(0.0, 0.043, 0.65),
                                   focal_length=55)

    # Render Preview 1: Studio Isometric Full PDU
    scene.camera = cam_iso
    scene.render.resolution_x = 900
    scene.render.resolution_y = 1800
    scene.render.filepath = os.path.join(PREVIEW_DIR, "pdu_studio_iso.png")
    print("[BLENDER] Rendering Studio Isometric...")
    bpy.ops.render.render(write_still=True)

    # Render Preview 2: Display Controller Closeup
    scene.camera = cam_disp
    scene.render.resolution_x = 900
    scene.render.resolution_y = 1600
    scene.render.filepath = os.path.join(PREVIEW_DIR, "pdu_display_pbr.png")
    print("[BLENDER] Rendering Display Closeup...")
    bpy.ops.render.render(write_still=True)

    # Render Preview 3: Socket Bank Closeup
    scene.camera = cam_sock
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.filepath = os.path.join(PREVIEW_DIR, "pdu_socket_bank_pbr.png")
    print("[BLENDER] Rendering Socket Bank Closeup...")
    bpy.ops.render.render(write_still=True)

    # -------------------------------------------------------------
    # 4. EKSPOR WEB 3D GLB
    # -------------------------------------------------------------
    print("[BLENDER] Mengekspor Web 3D GLB ke %s..." % OUTPUT_GLB)
    bpy.ops.object.select_all(action='DESELECT')
    for o in imported_objects:
        o.select_set(True)

    bpy.ops.export_scene.gltf(
        filepath=OUTPUT_GLB,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_materials='EXPORT',
        export_cameras=False,
        export_lights=False
    )

    glb_size = os.path.getsize(OUTPUT_GLB)
    print("[BLENDER] EKSPOR GLB SUKSES: %s (%d bytes, %.2f MB)" %
          (OUTPUT_GLB, glb_size, glb_size / (1024 * 1024)))
    print("[BLENDER] Pipeline Tahap 3 Selesai dalam %.2f detik." % (time.time() - t0))


if __name__ == "__main__":
    main()
