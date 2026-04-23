import contextlib
import importlib.util
import io
import json
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
             patch.object(self.citadel_module.time, "sleep", return_value=None), \
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
