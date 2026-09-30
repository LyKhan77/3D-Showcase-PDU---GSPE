# =====================================================================
# build_blender_scene.py — Pipeline PBR & Hierarchical GLB Export
# APDU9953 NetShelter 9000 Switched Rack PDU
# Menghasilkan 2 production GLB:
#   1. exports/apdu9953/glb/gspe_pdu_apdu9953.glb (Assembled dengan hierarki 6 subsistem)
#   2. exports/apdu9953/glb/gspe_pdu_apdu9953_exploded.glb (Exploded view untuk showcase)
# Dilengkapi PBR Principled BSDF & Auto-Smooth Shading.
# =====================================================================
import os
import sys
import math
import bpy

STAGING_BASE = "/Users/leekhan/project/3D-Model-PDU/temp/blender_staging_apdu9953"
EXPORT_DIR   = "/Users/leekhan/project/3D-Model-PDU/exports/apdu9953/glb"
BLENDER_DIR  = "/Users/leekhan/project/3D-Model-PDU/cad/apdu9953/blender"

SUBSYSTEM_LABELS = [
    ("housing", "Chassis Housing"),
    ("mounting", "Mounting System"),
    ("power", "Power Whip Cord"),
    ("breakers", "Circuit Breakers"),
    ("outlet_banks", "24-Outlet Banks"),
    ("nmc3", "NMC3 Controller"),
    ("internal", "Internal Busbars & PCB"),
]

PBR_SPECS = {
    "mat_chassis_powdercoat": {
        "color": (0.012, 0.014, 0.018, 1.0), # #14171E sRGB linear
        "metallic": 0.85,
        "roughness": 0.55,
    },
    "mat_gspe_navy": {
        "color": (0.000, 0.038, 0.176, 1.0), # #003674 sRGB linear
        "metallic": 0.25,
        "roughness": 0.35,
    },
    "mat_gspe_cream": {
        "color": (0.957, 1.000, 0.655, 1.0), # #FAFFD8 sRGB linear
        "metallic": 0.05,
        "roughness": 0.30,
    },
    "mat_polyamide_dark": {
        "color": (0.024, 0.028, 0.045, 1.0), # #2A2E39 sRGB linear
        "metallic": 0.02,
        "roughness": 0.45,
    },
    "mat_steel_metal": {
        "color": (0.300, 0.325, 0.360, 1.0), # Stainless steel #939BA4
        "metallic": 0.95,
        "roughness": 0.25,
    },
    "mat_glass_clear": {
        "color": (0.700, 0.850, 0.900, 0.15),
        "alpha": 0.15,
        "metallic": 0.0,
        "roughness": 0.05,
    },
    "mat_copper_busbars": {
        "color": (0.550, 0.260, 0.070, 1.0), # Copper #C58B49
        "metallic": 0.98,
        "roughness": 0.22,
    },
    "mat_brass_gold": {
        "color": (0.680, 0.470, 0.090, 1.0), # Brass #D7B553
        "metallic": 0.95,
        "roughness": 0.25,
    },
    "mat_pcb_green": {
        "color": (0.008, 0.125, 0.055, 1.0), # FR-4 #176443
        "metallic": 0.10,
        "roughness": 0.40,
    },
    "mat_lcd_screen": {
        "color": (0.003, 0.007, 0.012, 1.0), # OLED deep black
        "metallic": 0.10,
        "roughness": 0.12,
        "emission": (0.0, 0.8, 0.3),
        "emission_strength": 0.8
    },
    "mat_plug_blue": {
        "color": (0.000, 0.070, 0.500, 1.0), # IEC 60309 32A Blue
        "metallic": 0.05,
        "roughness": 0.38,
    },
    "mat_led_white": {
        "color": (0.90, 0.90, 0.90, 1.0),
        "metallic": 0.0,
        "roughness": 0.2,
        "emission": (1.0, 1.0, 1.0),
        "emission_strength": 3.0
    },
    "mat_led_green": {
        "color": (0.1, 0.9, 0.3, 1.0),
        "metallic": 0.0,
        "roughness": 0.2,
        "emission": (0.0, 1.0, 0.3),
        "emission_strength": 4.0
    },
    "mat_led_amber": {
        "color": (1.0, 0.6, 0.0, 1.0),
        "metallic": 0.0,
        "roughness": 0.2,
        "emission": (1.0, 0.6, 0.0),
        "emission_strength": 4.0
    },
    "mat_led_red": {
        "color": (0.9, 0.1, 0.1, 1.0),
        "metallic": 0.0,
        "roughness": 0.2,
        "emission": (1.0, 0.1, 0.1),
        "emission_strength": 4.0
    },
    "mat_nylon_white": {
        "color": (0.75, 0.75, 0.70, 1.0),
        "metallic": 0.0,
        "roughness": 0.5,
    },
    "mat_fpc_amber": {
        "color": (0.45, 0.20, 0.04, 1.0),
        "metallic": 0.1,
        "roughness": 0.35,
    },
    "mat_cap_blue": {
        "color": (0.018, 0.055, 0.145, 1.0),
        "metallic": 0.3,
        "roughness": 0.3,
    },
    "mat_wire_brown": {
        "color": (0.18, 0.09, 0.04, 1.0),
        "metallic": 0.0,
        "roughness": 0.5,
    },
    "mat_wire_green": {
        "color": (0.11, 0.30, 0.04, 1.0),
        "metallic": 0.0,
        "roughness": 0.5,
    },
    "mat_rubber_black": {
        "color": (0.015, 0.018, 0.022, 1.0),
        "metallic": 0.0,
        "roughness": 0.65,
    },
}

# These four source groups retain their established presentation material.
# The FreeCAD nearest-colour fallback can otherwise move them into a nearby
# palette; import aliases merge those OBJ groups back into the legacy target.
IMPORT_ALIASES = {
    ("internal", "nmc3_pcb", "mat_polyamide_dark"): "mat_chassis_powdercoat",
    ("nmc3", "nmc3_console", "mat_polyamide_dark"): "mat_chassis_powdercoat",
    ("nmc3", "nmc3_usbhost", "mat_polyamide_dark"): "mat_chassis_powdercoat",
    ("outlet_banks", "outlets", "mat_led_white"): "mat_gspe_cream",
}

def clear_scene():
    # Keep the running MCP addon enabled when rebuilding through Blender GUI.
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    for material in list(bpy.data.materials):
        bpy.data.materials.remove(material)

def create_pbr_material(name, spec):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    if not bsdf:
        bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")

    if "color" in spec:
        bsdf.inputs["Base Color"].default_value = spec["color"]
    if "metallic" in spec:
        bsdf.inputs["Metallic"].default_value = spec["metallic"]
    if "roughness" in spec:
        bsdf.inputs["Roughness"].default_value = spec["roughness"]
    if "alpha" in spec and "Alpha" in bsdf.inputs:
        bsdf.inputs["Alpha"].default_value = spec["alpha"]
    if "emission" in spec:
        bsdf.inputs["Emission Color"].default_value = (*spec["emission"], 1.0)
        bsdf.inputs["Emission Strength"].default_value = spec.get("emission_strength", 1.0)

    if "alpha" in spec:
        # Blender 5.2 renamed blend_method to surface_render_method. Read the
        # enum before assigning so this remains compatible with nearby versions.
        surface_prop = bpy.types.Material.bl_rna.properties.get("surface_render_method")
        if surface_prop:
            valid = set(surface_prop.enum_items.keys())
            for value in ("BLENDED", "BLEND"):
                if value in valid:
                    mat.surface_render_method = value
                    break
        elif hasattr(mat, "blend_method"):
            mat.blend_method = "BLEND"

    return mat

def build_scene_for_mode(mode_name="assembled"):
    print(f"\n==========================================")
    print(f"BUILDING BLENDER SCENE: {mode_name.upper()}")
    print(f"==========================================")
    clear_scene()

    staging_dir = os.path.join(STAGING_BASE, mode_name)
    if not os.path.exists(staging_dir):
        print(f"Error: {staging_dir} does not exist!")
        return

    # Root collection
    col_root = bpy.data.collections.new(f"GSPE_PDU_{mode_name.upper()}")
    bpy.context.scene.collection.children.link(col_root)

    # Material cache
    materials = {}
    for mat_id, spec in PBR_SPECS.items():
        materials[mat_id] = create_pbr_material(mat_id, spec)

    # Buat parent empty untuk setiap subsistem
    group_empties = {}
    for gid, glabel in SUBSYSTEM_LABELS:
        emp = bpy.data.objects.new(gid, None)
        emp.empty_display_type = 'PLAIN_AXES'
        emp.empty_display_size = 0.1
        # FreeCAD/OpenSCAD use Z as the product vertical axis. glTF viewers
        # use Y-up, so rotate the shared root once before export.
        emp.rotation_euler[0] = math.radians(-90.0)
        col_root.objects.link(emp)
        group_empties[gid] = emp

    imported_count = 0
    grouped_objects = {}
    # Impor semua file OBJ yang ada di staging_dir
    for fname in sorted(os.listdir(staging_dir)):
        if not fname.endswith(".obj") or "__" not in fname:
            continue

        layer, role, source_mat_id = fname[:-4].split("__", 2)
        mat_id = IMPORT_ALIASES.get((layer, role, source_mat_id), source_mat_id)
        obj_path = os.path.join(staging_dir, fname)
        if os.path.getsize(obj_path) == 0:
            continue

        # Deselect all
        for o in bpy.context.selected_objects:
            o.select_set(False)

        bpy.ops.wm.obj_import(filepath=obj_path)
        sel = bpy.context.selected_objects
        if not sel:
            continue

        if len(sel) > 1:
            bpy.context.view_layer.objects.active = sel[0]
            bpy.ops.object.join()
            target_obj = sel[0]
        else:
            target_obj = sel[0]

        target_obj.name = f"LAYER_{layer}__ROLE_{role}__MAT_{mat_id}__PART_{imported_count}"
        # Pindahkan ke root collection
        for c in list(target_obj.users_collection):
            c.objects.unlink(target_obj)
        col_root.objects.link(target_obj)

        # Pasang PBR material
        base_mat = materials.get(mat_id, materials["mat_steel_metal"])
        target_mat = base_mat.copy()
        target_mat.name = f"{layer}__{role}__{mat_id}"
        target_obj.data.materials.clear()
        target_obj.data.materials.append(target_mat)

        # Auto smooth normals
        target_obj.select_set(True)
        bpy.context.view_layer.objects.active = target_obj
        bpy.ops.object.shade_smooth()

        # Skala mm ke meter (0.001)
        target_obj.scale = (0.001, 0.001, 0.001)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        # Parent ke group empty yang bersangkutan
        if layer in group_empties:
            target_obj.parent = group_empties[layer]

        grouped_objects.setdefault((layer, role, mat_id), []).append(target_obj)
        imported_count += 1

    # Merge aliased source groups with their established target group so each
    # exported mesh has one stable material-qualified name.
    for (layer, role, mat_id), objects in grouped_objects.items():
        if not objects:
            continue
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        for obj in objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        if len(objects) > 1:
            bpy.ops.object.join()
        target_obj = objects[0]
        target_obj.name = f"LAYER_{layer}__ROLE_{role}__MAT_{mat_id}"
        target_obj.data.name = f"{layer}__{role}__{mat_id}"

    print(f"Total {imported_count} meshes linked across 7 subsystems.")

    # Simpan file .blend
    blend_path = os.path.join(BLENDER_DIR, f"gspe_pdu_apdu9953{'_exploded' if mode_name=='exploded' else ''}.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved .blend: {blend_path} ({os.path.getsize(blend_path)/1024:.1f} KB)")

    # Ekspor GLB
    glb_path = os.path.join(EXPORT_DIR, f"gspe_pdu_apdu9953{'_exploded' if mode_name=='exploded' else ''}.glb")
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format="GLB",
        use_selection=False,
        export_apply=True,
        export_yup=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False
    )
    print(f"Exported GLB: {glb_path} ({os.path.getsize(glb_path)/1024:.1f} KB)")

def main():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    os.makedirs(BLENDER_DIR, exist_ok=True)

    # 1. Assembled model
    build_scene_for_mode("assembled")

    # 2. Exploded model
    build_scene_for_mode("exploded")

if __name__ in ("__main__", "<run_path>"):
    main()
