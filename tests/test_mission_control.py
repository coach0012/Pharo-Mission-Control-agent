from __future__ import annotations

import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from agent_prompt_runner import route
from common import parse_amount, parse_percent_to_bps
from prepare_batch import write_batch_plan
from prepare_liquidity import write_liquidity_plan
from prepare_token import write_token_project


class MissionControlTests(unittest.TestCase):
    def test_common_amounts(self):
        self.assertEqual(parse_amount("1.5", 6), ("1.5", 1500000))
        self.assertEqual(parse_percent_to_bps("1"), 100)

    def test_routes(self):
        prompts = [
            Path(ROOT / "examples" / "prompt_deploy.txt").read_text(),
            Path(ROOT / "examples" / "prompt_liquidity.txt").read_text(),
            Path(ROOT / "examples" / "prompt_batch.txt").read_text(),
            Path(ROOT / "examples" / "prompt_balance.txt").read_text(),
        ]
        for prompt in prompts:
            result = route(prompt)
            self.assertEqual(result["status"], "ready", result)
            self.assertEqual(result["agent_selected_skill"], "pharos-mission-control-agent")

    def test_prepare_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_plan = write_token_project("Orbit Token", "ORBIT", 18, "1000000", root / "token", False)
            self.assertEqual(token_plan["token"]["symbol"], "ORBIT")
            csv_path = root / "recipients.csv"
            csv_path.write_text("address,amount\n0x1111111111111111111111111111111111111111,1\n", encoding="utf-8")
            batch_plan = write_batch_plan("0x2222222222222222222222222222222222222222", 18, csv_path, root / "batch", False)
            self.assertEqual(batch_plan["recipient_count"], 1)
            liq_args = Namespace(
                token="0x1111111111111111111111111111111111111111",
                router="0x2222222222222222222222222222222222222222",
                token_decimals=18,
                token_amount="1000",
                native_amount="0.1",
                slippage_percent="1",
                recipient=None,
                deadline_seconds=1800,
                output=str(root / "liq"),
                overwrite=False,
            )
            liq_plan = write_liquidity_plan(liq_args)
            self.assertEqual(liq_plan["action"], "add-liquidity-native")


if __name__ == "__main__":
    unittest.main()
