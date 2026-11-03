import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import server

class ArchitekTests(unittest.TestCase):
    def test_slug(self):
        self.assertEqual(server.slugify("Meine App 2026"), "meine-app-2026")
        for invalid in ("", "../", "   ", "x" * 65):
            with self.assertRaises(ValueError):
                server.slugify(invalid)

    def test_offline_fallback(self):
        with patch("server.urllib.request.urlopen", side_effect=OSError("offline")):
            text, route = server.ask_local_model("Baue eine Test-App")
        self.assertEqual(route, "offline-template")
        self.assertIn("Baue eine Test-App", text)

    def test_create_and_list(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(server, "WORKSPACE", Path(temp)):
                with patch.object(server, "ask_local_model", return_value=("Plan", "test-model")):
                    created = server.create_project("Demo App", "Baue eine einfache App")
                self.assertEqual(created["slug"], "demo-app")
                self.assertEqual(len(server.list_projects()), 1)
                self.assertEqual((Path(temp) / "demo-app" / "PLAN.md").read_text(), "Plan")
                with self.assertRaises(FileExistsError):
                    server.create_project("Demo App", "Baue eine weitere App")

    def test_invalid_prompt(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(server, "WORKSPACE", Path(temp)):
                with self.assertRaises(ValueError):
                    server.create_project("Demo", "x")
                self.assertFalse((Path(temp) / "demo").exists())

if __name__ == "__main__":
    unittest.main()
