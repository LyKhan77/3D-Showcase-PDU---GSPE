import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "freecad"))
from presentation import classify

class PresentationTests(unittest.TestCase):
    def test_electronics_separate_from_external_module(self):
        pcb = classify(dict(name="NMC3_MainPCB", group="GRP_NMC3_CONTROLLER"))
        face = classify(dict(name="NMC3_Faceplate", group="GRP_NMC3_CONTROLLER"))
        self.assertEqual(pcb["layer"], "internal")
        self.assertEqual(face["layer"], "nmc3")
        self.assertEqual(pcb["owner"], face["owner"])

    def test_contacts_and_relay_fasteners_follow_internal_layer(self):
        for name in ("BANK1_Out1_SpringClips", "BANK2_RelayTorxScrews", "BANK3_Busbars"):
            self.assertEqual(classify(dict(name=name, group="GRP_SOCKET_BANKS"))["layer"], "internal")

    def test_breaker_body_stays_with_breaker(self):
        self.assertEqual(classify(dict(name="BRK1_Body", group="GRP_BREAKERS"))["layer"], "breakers")

if __name__ == "__main__":
    unittest.main()
