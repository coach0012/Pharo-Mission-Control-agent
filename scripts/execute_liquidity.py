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


def run_cast(command: list[str]) -> dict:
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    match = TX_RE.search(completed.stdout)
    return {"returncode": completed.returncode, "tx_hash": match.group(0) if match else None}


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute a Mission Control liquidity plan.")
    parser.add_argument("--plan", required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm", action="store_true")
    args = parser.parse_args()
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    tools = missing_tools()
    summary = {
        "status": "ready" if not tools else "missing_foundry",
        "action": "add-liquidity-native",
        "network": PHAROS_ATLANTIC,
        "router": plan["router"],
        "token": plan["token"],
        "raw_token_amount": plan["raw_token_amount"],
        "raw_native_amount": plan["raw_native_amount"],
        "warnings": plan.get("warnings", []),
        "private_key_env_set": bool(os.environ.get("PRIVATE_KEY")),
        "missing_tools": tools,
    }
    print(json.dumps(summary, indent=2), flush=True)
    if not args.execute:
        return 0
    if not args.confirm:
        raise SystemExit("liquidity execution requires --confirm")
    if tools:
        raise SystemExit("install Foundry cast first")
    private_key = os.environ.get("PRIVATE_KEY")
    if not private_key:
        raise SystemExit("PRIVATE_KEY is not set locally")
    chain = subprocess.run(["cast", "chain-id", "--rpc-url", PHAROS_ATLANTIC["rpc_url"]], capture_output=True, text=True, check=False)
    if chain.returncode != 0 or chain.stdout.strip() != str(PHAROS_ATLANTIC["chain_id"]):
        raise SystemExit("RPC chain ID check failed")
    wallet = subprocess.run(["cast", "wallet", "address", "--private-key", private_key], capture_output=True, text=True, check=False)
    if wallet.returncode != 0:
        raise SystemExit("could not derive address from PRIVATE_KEY")
    recipient = wallet.stdout.strip() if plan["recipient"] == "deployer_from_PRIVATE_KEY" else plan["recipient"]
    approve = run_cast(
        [
            "cast",
            "send",
            "--rpc-url",
            PHAROS_ATLANTIC["rpc_url"],
            "--private-key",
            private_key,
            plan["token"],
            "approve(address,uint256)",
            plan["router"],
            plan["raw_token_amount"],
        ]
    )
    print(json.dumps({"step": "approve", **approve}), flush=True)
    if approve["returncode"] != 0:
        return approve["returncode"]
    add_liquidity = run_cast(
        [
            "cast",
            "send",
            "--rpc-url",
            PHAROS_ATLANTIC["rpc_url"],
            "--private-key",
            private_key,
            "--value",
            plan["raw_native_amount"],
            plan["router"],
            "addLiquidityETH(address,uint256,uint256,uint256,address,uint256)",
            plan["token"],
            plan["raw_token_amount"],
            plan["amount_token_min"],
            plan["amount_native_min"],
            recipient,
            str(plan["deadline"]),
        ]
    )
    print(json.dumps({"step": "addLiquidityETH", **add_liquidity}), flush=True)
    return add_liquidity["returncode"]


if __name__ == "__main__":
    raise SystemExit(main())
