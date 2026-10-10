import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import backend.database as database


TEST_DATA = tempfile.TemporaryDirectory()
TEST_DATABASE = Path(TEST_DATA.name) / "bilbo.db"
database.DATABASE_PATH = TEST_DATABASE

from fastapi.testclient import TestClient

from backend.api import routes
from backend.file_manager import find_large_files, is_protected
from backend.main import app
from frontend.chat_window import pet_mood_for


class BackendRouteTests(unittest.TestCase):
    def setUp(self):
        self.add_message = patch.object(routes, "add_message")
        get_history = patch.object(routes, "get_history", return_value=[])
        self.add_message.start()
        self.get_history = get_history.start()
        self.addCleanup(self.add_message.stop)
        self.addCleanup(get_history.stop)

    def test_startup_initializes_a_new_database(self):
        with TestClient(app):
            pass

        connection = sqlite3.connect(TEST_DATABASE)
        try:
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
        finally:
            connection.close()

        self.assertIn("messages", tables)

    def test_database_persists_messages_in_chronological_order(self):
        with TestClient(app):
            database.add_message("user", "first")
            database.add_message("assistant", "second")
            messages = database.get_history()

        self.assertEqual(
            [item["message"] for item in messages],
            ["first", "second"],
        )

    def test_chat_is_available_on_api_and_legacy_routes(self):
        with TestClient(app) as client:
            api_response = client.post("/api/chat", json={"message": "hello"})
            legacy_response = client.post("/chat", json={"message": "hello"})

        self.assertEqual(api_response.status_code, 200)
        self.assertEqual(legacy_response.status_code, 200)
        self.assertIn("reply", api_response.json())
        self.assertIn("reply", legacy_response.json())

    def test_history_api_returns_the_shape_expected_by_the_desktop(self):
        saved_messages = [
            {
                "speaker": "user",
                "message": "hello",
                "created_at": "2026-10-10T12:00:00",
            }
        ]
        self.get_history.return_value = saved_messages

        with TestClient(app) as client:
            response = client.get("/api/history")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"messages": saved_messages})

    def test_security_intent_precedes_general_laptop_status(self):
        security_report = {
            "windows_defender": "Unknown",
            "firewall": "Unknown",
            "notes": [],
        }
        with patch.object(
            routes, "get_security_report", return_value=security_report
        ), patch.object(routes, "get_system_status") as get_system_status:
            with TestClient(app) as client:
                response = client.post(
                    "/api/chat",
                    json={"message": "check my laptop security"},
                )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["command"], "security")
        get_system_status.assert_not_called()

    def test_free_storage_request_runs_read_only_scan(self):
        scan_result = {
            "storage": {"used_percent": 50, "free": "10 GB"},
            "large_downloads_total": "0 B",
            "temporary_files_total": "0 B",
        }
        with patch.object(routes, "scan_storage", return_value=scan_result) as scan:
            with TestClient(app) as client:
                response = client.post(
                    "/api/chat",
                    json={"message": "help me free up storage"},
                )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["command"], "storage_scan")
        scan.assert_called_once()

    def test_file_discard_endpoint_does_not_change_files(self):
        with TestClient(app) as client:
            response = client.post(
                "/files/discard",
                json={"path": "C:/example.txt"},
            )

        self.assertEqual(response.status_code, 501)
        self.assertIn("No files were changed", response.json()["detail"])

    def test_history_request_returns_saved_messages_in_order(self):
        saved_messages = [
            {
                "speaker": "user",
                "message": "hello",
                "created_at": "2026-10-10T12:00:00",
            },
            {
                "speaker": "assistant",
                "message": "Hi!",
                "created_at": "2026-10-10T12:00:01",
            },
        ]
        self.get_history.return_value = saved_messages

        with TestClient(app) as client:
            response = client.post(
                "/api/chat",
                json={"message": "show my conversation history"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["type"], "history")
        reply = response.json()["reply"]
        self.assertLess(reply.index("hello"), reply.index("Hi!"))
        self.assertIn("2026-10-10T12:00:00", reply)

    def test_laptop_report_handles_unavailable_battery(self):
        status = {
            "cpu": 10,
            "memory": {"percent": 20, "used_gb": 2, "total_gb": 8},
            "disk": {"percent": 40, "free_gb": 100},
            "battery": {"available": False},
            "uptime": {"hours": 1, "minutes": 2},
        }
        with patch.object(routes, "get_system_status", return_value=status):
            report = routes.laptop_report()

        self.assertIn("Battery information unavailable", report)


class ProtectedStoragePathTests(unittest.TestCase):
    def test_any_gurlene_path_is_protected(self):
        path = Path("C:/Users/example/gurlene/private-file.txt")

        self.assertTrue(is_protected(path))

    def test_large_file_walk_prunes_gurlene_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            walk_results = [(folder, ["gurlene", "safe"], [])]

            with patch("backend.file_manager.os.walk", return_value=walk_results):
                self.assertEqual(find_large_files(folder, minimum_mb=0), [])

        self.assertEqual(walk_results[0][1], ["safe"])

    def test_large_file_scan_does_not_follow_junctions(self):
        with patch.object(
            Path,
            "is_junction",
            autospec=True,
            side_effect=lambda candidate: candidate.name == "junction",
        ):
            self.assertTrue(
                is_protected(Path("C:/Downloads/junction/private-file.txt"))
            )

    def test_large_file_scan_handles_a_missing_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            missing = Path(folder) / "missing"

            self.assertEqual(find_large_files(missing), [])


class PetMoodTests(unittest.TestCase):
    def test_supported_moods_are_preserved_for_the_desktop_pet(self):
        for mood in ("happy", "sad", "stressed", "tired", "excited", "angry"):
            with self.subTest(mood=mood):
                self.assertEqual(pet_mood_for(mood), mood)

    def test_neutral_and_unknown_moods_have_safe_fallbacks(self):
        self.assertEqual(pet_mood_for("neutral"), "normal")
        self.assertEqual(pet_mood_for("unknown"), "happy")


if __name__ == "__main__":
    unittest.main()
