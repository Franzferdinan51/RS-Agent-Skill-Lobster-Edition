import importlib.util
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock


ROOT_DIR = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT_DIR / "tools" / "runescape-api.py"


def load_module():
    spec = importlib.util.spec_from_file_location("runescape_api_module", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(self, status_code=200, text="", json_data=None):
        self.status_code = status_code
        self.text = text
        self._json_data = json_data

    def json(self):
        return self._json_data


class RuneScapeAPITests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def test_search_prefers_exact_match_from_results_page(self):
        api = self.module.RuneScapeAPI(rate_limit_ms=0)
        api.session.get = MagicMock(side_effect=[
            FakeResponse(
                text=(
                    "<a class='table-item-link' "
                    'href="https://secure.runescape.com/m=itemdb_rs/Bale+of+flax/viewitem?obj=31045" '
                    'title="Bale of flax"></a>'
                    "<a class='table-item-link' "
                    'href="https://secure.runescape.com/m=itemdb_rs/Flax/viewitem?obj=1779" '
                    'title="Flax"></a>'
                )
            ),
            FakeResponse(json_data={"item": {"id": 1779, "name": "Flax"}}),
        ])

        result = api.search_item_by_name("Flax")

        self.assertEqual(result, {"id": 1779, "name": "Flax"})
        urls = [call.args[0] for call in api.session.get.call_args_list]
        self.assertEqual(urls[0], "https://secure.runescape.com/m=itemdb_rs/results?query=Flax")
        self.assertEqual(urls[1], "https://secure.runescape.com/m=itemdb_rs/api/catalogue/detail.json?item=1779")

    def test_osrs_search_uses_oldschool_endpoints(self):
        api = self.module.RuneScapeAPI(rate_limit_ms=0, game="osrs")
        api.session.get = MagicMock(side_effect=[
            FakeResponse(
                text=(
                    "<a class='table-item-link' "
                    'href="https://secure.runescape.com/m=itemdb_oldschool/Flax/viewitem?obj=1779" '
                    'title="Flax"></a>'
                )
            ),
            FakeResponse(json_data={"item": {"id": 1779, "name": "Flax"}}),
        ])

        result = api.search_item_by_name("Flax")

        self.assertEqual(result, {"id": 1779, "name": "Flax"})
        urls = [call.args[0] for call in api.session.get.call_args_list]
        self.assertEqual(urls[0], "https://secure.runescape.com/m=itemdb_oldschool/results?query=Flax")
        self.assertEqual(urls[1], "https://secure.runescape.com/m=itemdb_oldschool/api/catalogue/detail.json?item=1779")

    def test_search_returns_none_when_results_page_has_no_candidates(self):
        api = self.module.RuneScapeAPI(rate_limit_ms=0)
        api.session.get = MagicMock(return_value=FakeResponse(text="<html>No results</html>"))

        result = api.search_item_by_name("Dragon whip")

        self.assertIsNone(result)
        self.assertEqual(api.session.get.call_count, 1)
