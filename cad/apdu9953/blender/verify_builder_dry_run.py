# verify_builder_dry_run.py: run build_blender_scene.py into temp/builder-dry-run and check the result.
# It needs the FreeCAD staging (run export_mesh_for_blender.py first) and never touches exports/ or cad/.
#   /Applications/Blender.app/Contents/MacOS/Blender -b --python-exit-code 1 \
#       --python cad/apdu9953/blender/verify_builder_dry_run.py
# Use the app binary: /opt/homebrew/bin/blender fails with "No module named '_bpy_types'".
import os
import runpy
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT = os.path.join(ROOT, "temp", "builder-dry-run")

builder = runpy.run_path(os.path.join(HERE, "build_blender_scene.py"), run_name="dry_run")
builder["main"].__globals__["EXPORT_DIR"] = os.path.join(OUT, "glb")
builder["main"].__globals__["BLENDER_DIR"] = os.path.join(OUT, "blend")
builder["main"]()

for name in ("gspe_pdu_apdu9953", "gspe_pdu_apdu9953_exploded"):
    glb = os.path.join(OUT, "glb", name + ".glb")
    blend = os.path.join(OUT, "blend", name + ".blend")
    assert os.path.getsize(glb) > 1_000_000, f"{glb} is missing or too small"
    bpy.ops.wm.open_mainfile(filepath=blend)
    stray = [o.name for o in bpy.data.objects if o.name in ("Cube", "Camera", "Light")]
    assert not stray, f"{blend} still holds default objects: {stray}"
print("DRY RUN OK: builder output is clean")
