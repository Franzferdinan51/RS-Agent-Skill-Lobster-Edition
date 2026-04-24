import contextlib
import importlib.util
import io
import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch


ROOT_DIR = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    module_path = ROOT_DIR / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ReportingToolTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.citadel_module = load_module("citadel_cap_tracker_module", "tools/citadel-cap-tracker.py")
        cls.auto_report_module = load_module("auto_report_module", "tools/auto-report.py")
        cls.ge_arbitrage_module = load_module("ge_arbitrage_module", "tools/ge-arbitrage.py")
        cls.collection_log_module = load_module("collection_log_module", "tools/collection-log.py")
        cls.inactive_members_module = load_module("inactive_members_module", "tools/inactive-members.py")

    def test_citadel_json_mode_outputs_only_json(self):
        stdout = io.StringIO()
        sample_member = {
            "player": "Alice",
            "cap_date": datetime(2026, 4, 20, 12, 0, 0),
            "visit_date": None,
            "total_xp": 123456789,
            "rank": "42",
        }

        with patch.object(self.citadel_module, "get_clan_members", return_value=["Alice"]), \
             patch.object(self.citadel_module, "check_player_citadel_activity", return_value=sample_member), \
             patch("sys.argv", ["citadel-cap-tracker.py", "--clan", "Lords of Arcadia", "--json", "--rate-limit", "0"]), \
             contextlib.redirect_stdout(stdout):
            self.citadel_module.main()

        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["clan"], "Lords of Arcadia")
        self.assertEqual(payload["capped"][0]["player"], "Alice")
        self.assertEqual(payload["capped"][0]["cap_date"], "2026-04-20T12:00:00")

    def test_auto_report_json_alias_outputs_only_json(self):
        stdout = io.StringIO()

        with patch.object(self.auto_report_module, "get_clan_data", return_value={"total_members": 170, "total_xp": 555}), \
             patch("sys.argv", ["auto-report.py", "--type", "clan", "--clan", "Lords of Arcadia", "--json"]), \
             contextlib.redirect_stdout(stdout):
            self.auto_report_module.main()

        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["clan_name"], "Lords of Arcadia")
        self.assertEqual(payload["total_members"], 170)

    def test_ge_arbitrage_json_mode_outputs_only_json(self):
        stdout = io.StringIO()
        opportunity = {
            "item_id": 1779,
            "item_name": "Flax",
            "buy_price": 10,
            "target_sell": 12,
            "profit": 1000,
            "roi": 10.0,
        }

        with patch.object(self.ge_arbitrage_module, "scan_items", return_value=[opportunity]), \
             patch("sys.argv", ["ge-arbitrage.py", "--scan-all", "--json", "--min-profit", "0"]), \
             contextlib.redirect_stdout(stdout):
            self.ge_arbitrage_module.main()

        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["items_scanned"], 10)
        self.assertEqual(payload["opportunities"][0]["item_name"], "Flax")

    def test_collection_log_empty_view_json_outputs_only_json(self):
        stdout = io.StringIO()

        with tempfile.TemporaryDirectory() as temp_dir, \
             patch.object(self.collection_log_module, "COLLECTION_FILE", Path(temp_dir) / "collection-log.json"), \
             patch("sys.argv", ["collection-log.py", "--view", "--json"]), \
             contextlib.redirect_stdout(stdout):
            self.collection_log_module.main()

        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["entries"], [])
        self.assertEqual(payload["categories"], {})

    def test_inactive_members_json_mode_outputs_only_json(self):
        stdout = io.StringIO()
        members = [
            {"name": "Alice", "rank": "Admin", "total_xp": 1000},
            {"name": "Bob", "rank": "Recruit", "total_xp": 2000},
        ]
        activities = [
            {"player": "Alice", "days_inactive": 120, "last_activity": datetime(2026, 1, 1), "total_xp": 1000},
            {"player": "Bob", "error": "Profile private or not found"},
        ]

        with patch.object(self.inactive_members_module, "get_clan_members", return_value=members), \
             patch.object(self.inactive_members_module, "check_player_activity", side_effect=activities), \
             patch("sys.argv", ["inactive-members.py", "--clan", "Lords of Arcadia", "--json", "--workers", "1"]), \
             contextlib.redirect_stdout(stdout):
            self.inactive_members_module.main()

        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["total_members"], 2)
        self.assertEqual(payload["inactive_count"], 1)
        self.assertEqual(payload["error_count"], 1)
        self.assertEqual(payload["inactive_members"][0]["last_activity"], "2026-01-01T00:00:00")
