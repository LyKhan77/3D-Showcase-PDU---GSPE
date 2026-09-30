import importlib.util
import unittest

FREECAD = importlib.util.find_spec("FreeCAD")


@unittest.skipUnless(FREECAD, "FreeCAD Python modules unavailable")
class GeometryRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from modules._common import make_text_solid
        from modules.sub_nmc3_controller import (
            build_rj45_port,
            build_usb_micro_port,
            build_usb_a_port,
        )

        cls.make_text_solid = staticmethod(make_text_solid)
        cls.build_rj45_port = staticmethod(build_rj45_port)
        cls.build_usb_micro_port = staticmethod(build_usb_micro_port)
        cls.build_usb_a_port = staticmethod(build_usb_a_port)

    def test_text_positive_local_y_maps_to_positive_model_z(self):
        import FreeCAD as App

        doc = App.newDocument("text_orientation_test")
        shape = self.make_text_solid("L", 10.0, 0.15, 0, 0, 0, doc=doc)
        self.assertGreater(shape.BoundBox.ZMax, shape.BoundBox.ZMin)
        self.assertLess(shape.BoundBox.YMax, 0.01)
        weighted_z = sum(s.Volume * s.CenterOfMass.z for s in shape.Solids) / sum(
            s.Volume for s in shape.Solids
        )
        self.assertLess(weighted_z, 0.0)
        App.closeDocument(doc.Name)

    def test_micro_b_has_trapezoid_width_change(self):
        import FreeCAD as App
        shape = self.build_usb_micro_port(0, -23, 0)
        self.assertGreater(shape.BoundBox.XLength, 7.5)
        self.assertLess(shape.BoundBox.XLength, 9.0)
        self.assertGreater(shape.BoundBox.ZLength, 2.5)
        self.assertFalse(shape.isInside(App.Vector(3.8, -23, -1.4), 1e-7, True))
        self.assertTrue(shape.isInside(App.Vector(3.8, -23, 1.4), 1e-7, True))

    def test_rj45_aperture_remains_open_at_nonzero_world_depth(self):
        import FreeCAD as App
        for inverted in (False, True):
            with self.subTest(inverted=inverted):
                shape = self.build_rj45_port(12, -23, 914.5, inverted=inverted)
                self.assertFalse(shape.isInside(App.Vector(12, -26.6, 914.5), 1e-7, True))

    def test_polygon_prism_preserves_asymmetric_z_profile(self):
        import FreeCAD as App
        from modules._common import polygon_prism_xz
        shape = polygon_prism_xz([(-4, 2), (4, 2), (2, -2), (-2, -2)], 2, -1)
        self.assertTrue(shape.isInside(App.Vector(3.5, 0, 1.7), 1e-7, True))
        self.assertFalse(shape.isInside(App.Vector(3.5, 0, -1.7), 1e-7, True))

    def test_universal_io_and_link_port_have_distinct_inversion_bounds(self):
        normal = self.build_rj45_port(0, -23, 0, inverted=False)
        inverted = self.build_rj45_port(0, -23, 0, inverted=True)
        normal_contacts = sorted(
            (round(s.BoundBox.ZMin, 3), round(s.BoundBox.ZMax, 3))
            for s in normal.Solids
            if abs(s.BoundBox.XLength - .4) < .001
        )
        inverted_contacts = sorted(
            (round(s.BoundBox.ZMin, 3), round(s.BoundBox.ZMax, 3))
            for s in inverted.Solids
            if abs(s.BoundBox.XLength - .4) < .001
        )
        self.assertEqual(len(normal_contacts), 8)
        self.assertEqual(len(inverted_contacts), 8)
        self.assertNotEqual(normal_contacts, inverted_contacts)
        self.assertGreater(normal_contacts[0][1] - normal_contacts[0][0], 1.0)

    def test_usb_a_contains_retention_windows_and_side_detents(self):
        import FreeCAD as App
        shape = self.build_usb_a_port(0, -23, 0)
        self.assertGreater(shape.Volume, 0)
        self.assertGreater(shape.BoundBox.YLength, 10)
        self.assertFalse(shape.isInside(App.Vector(4, -21, 3.5), 1e-7, True))
        self.assertTrue(shape.isInside(App.Vector(0, -21, 3.5), 1e-7, True))


if __name__ == "__main__":
    unittest.main()
