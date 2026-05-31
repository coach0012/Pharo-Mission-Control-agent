from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from common import PHAROS_ATLANTIC


TX_RE = re.compile(r"0x[a-fA-F0-9]{64}")


def missing_tools() -> list[str]:
    return [tool for tool in ("cast",) if shutil.which(tool) is None]


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute a Mission Control batch token send.")
    parser.add_argument("--plan", required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm", action="store_true")
    args = parser.parse_args()
    plan_path = Path(args.plan).resolve()
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    tools = missing_tools()
    summary = {
        "status": "ready" if not tools else "missing_foundry",
        "action": "batch-send",
        "network": PHAROS_ATLANTIC,
        "token": plan["token"],
        "recipient_count": plan["recipient_count"],
        "total_raw_amount": plan["total_raw_amount"],
        "private_key_env_set": bool(os.environ.get("PRIVATE_KEY")),
        "missing_tools": tools,
    }
    print(json.dumps(summary, indent=2), flush=True)
    if not args.execute:
        return 0
    if not args.confirm:
        raise SystemExit("batch send requires --confirm")
    if tools:
        raise SystemExit("install Foundry cast first")
    private_key = os.environ.get("PRIVATE_KEY")
    if not private_key:
        raise SystemExit("PRIVATE_KEY is not set locally")
    results = []
    for index, row in enumerate(plan["recipients"]):
        completed = subprocess.run(
            [
                "cast",
                "send",
                "--rpc-url",
                PHAROS_ATLANTIC["rpc_url"],
                "--private-key",
                private_key,
                plan["token"],
                "transfer(address,uint256)",
                row["address"],
                row["raw_amount"],
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        match = TX_RE.search(completed.stdout)
        result = {"index": index, "address": row["address"], "returncode": completed.returncode, "tx_hash": match.group(0) if match else None}
        print(json.dumps(result), flush=True)
        results.append(result)
        if completed.returncode != 0:
            break
    plan_path.with_name("batch_send_results.json").write_text(json.dumps({"results": results}, indent=2), encoding="utf-8")
    return 0 if results and all(item["returncode"] == 0 for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
