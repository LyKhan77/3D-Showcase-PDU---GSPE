"""Behavior checks against actual OpenSCAD CSG, including CLI overrides."""
from pathlib import Path
import hashlib
import re
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parent / "openscad/pdu_apdu9953_assembly.scad"
FLAGS = ["SHOW_HOUSING", "SHOW_MOUNTING", "SHOW_POWER_ENTRY",
         "SHOW_FASCIA_EXTERNAL", "SHOW_INTERNALS"]

def compile_csg(**settings):
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "result.csg"
        cmd = ["openscad", "--hardwarnings", "-o", str(output)]
        for key, value in settings.items():
            value = str(value).lower() if isinstance(value, bool) else repr(value).replace("'", '"')
            cmd += ["-D", f"{key}={value}"]
        result = subprocess.run(cmd + [str(SOURCE)], capture_output=True, text=True)
        if result.returncode or re.search(r"WARNING:|ERROR:", result.stderr):
            raise AssertionError(result.stderr)
        return re.sub(r"\s+", "", output.read_text())

class ShowcaseTests(unittest.TestCase):
    def test_all_manual_groups_can_be_hidden(self):
        csg = compile_csg(**dict.fromkeys(FLAGS, False))
        self.assertIsNone(re.search(r"cube\(|cylinder\(|sphere\(|linear_extrude\(", csg), "Hidden assembly still has geometry")

    def test_presets_override_manual_flags_and_explosion(self):
        stages = ["HOUSING", "MOUNTING", "POWER", "INTERNALS", "CONTROLS", "COMPLETE", "EXPLODED"]
        for index, name in enumerate(stages, 1):
            with self.subTest(stage=name):
                expected = dict(zip(FLAGS, [True, index >= 2, index >= 3, index >= 5, index >= 4]))
                expected.update(SHOW_FRONT_COVER=index >= 5, EXPLODE_FACTOR=0.6 if index == 7 else 0)
                actual = dict.fromkeys(FLAGS, False)
                actual.update(VIEW_STAGE=f"STAGE{index}_{name}", SHOW_FRONT_COVER=False,
                              SHOW_WHIP=False, EXPLODE_FACTOR=1)
                self.assertEqual(hashlib.sha256(compile_csg(**actual).encode()).hexdigest(),
                                 hashlib.sha256(compile_csg(**expected).encode()).hexdigest())

    def test_each_manual_group_changes_geometry(self):
        full = compile_csg()
        for flag in FLAGS + ["SHOW_FRONT_COVER", "SHOW_WHIP"]:
            with self.subTest(flag=flag):
                self.assertNotEqual(full, compile_csg(**{flag: False}))

    def test_invalid_stage_is_rejected(self):
        with self.assertRaisesRegex(AssertionError, "Unknown VIEW_STAGE"):
            compile_csg(VIEW_STAGE="STAGE8_TYPO")

if __name__ == "__main__":
    unittest.main()
