import unittest

from modules.mechanical_scripts import build_create_bolt_script, build_spur_gear_script


class TestMechanicalValidation(unittest.TestCase):
    def test_create_bolt_script_verifies_body_validity(self):
        script = build_create_bolt_script()
        self.assertIn("if body and body.isValid:", script)
        self.assertIn('returnValue.append("ERR_VERIFICATION_FAILED")', script)
        self.assertIn("adsk.fusion.FeatureOperations.NewBodyFeatureOperation", script)
        self.assertIn("cyl_faces = [f for f in body.faces if f.geometry and f.geometry.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType]", script)
        self.assertIn("face = max(cyl_faces, key=lambda f: f.area, default=None)", script)

    def test_create_gear_script_verifies_created_body_lookup(self):
        script = build_spur_gear_script()
        self.assertIn('gear_base.name = f"Gear_M{m}_Z{n}"', script)
        self.assertIn("if find_body_recursive(root, gear_base.name):", script)
        self.assertIn('returnValue.append("ERR_VERIFICATION_FAILED")', script)


if __name__ == '__main__':
    unittest.main()
