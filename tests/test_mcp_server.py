import importlib.util
import json
import subprocess
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch


ROOT_DIR = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT_DIR / "mcp-server.py"


def load_module():
    spec = importlib.util.spec_from_file_location("mcp_server_module", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class MCPServerTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def test_runescape_api_passes_game_flag_to_cli(self):
        server = self.module.RS_Agent_MCP_Server()
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=json.dumps({"ok": True}),
            stderr="",
        )

        with patch.object(self.module.subprocess, "run", return_value=completed) as mock_run:
            result = server._run_tool("runescape-api", {"item": "Flax", "game": "osrs"})

        self.assertEqual(result, {"ok": True})
        cmd = mock_run.call_args.args[0]
        self.assertIn("--game", cmd)
        self.assertNotIn("--osrs", cmd)
        self.assertEqual(cmd[cmd.index("--game") + 1], "osrs")

    def test_handle_tools_call_marks_error_results(self):
        server = self.module.RS_Agent_MCP_Server()

        with patch.object(server, "_run_tool", return_value={"error": "Item not found", "query": "Dragon whip"}):
            result = server.handle_tools_call({"name": "runescape_api", "arguments": {"item": "Dragon whip"}})

        self.assertTrue(result["isError"])
        self.assertIn("Item not found", result["content"][0]["text"])

    def test_initialized_notification_returns_no_response(self):
        server = self.module.RS_Agent_MCP_Server()

        response = server.handle_request({"jsonrpc": "2.0", "method": "notifications/initialized"})

        self.assertIsNone(response)
