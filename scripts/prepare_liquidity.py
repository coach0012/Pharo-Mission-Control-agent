from __future__ import annotations

import argparse
import json
import shutil
import time

from common import PHAROS_ATLANTIC, normalize_address, parse_amount, parse_percent_to_bps, safe_dir, validate_decimals


def apply_slippage(raw: int, slippage_bps: int) -> int:
    return raw * (10_000 - slippage_bps) // 10_000


def write_liquidity_plan(args: argparse.Namespace) -> dict:
    token = normalize_address(args.token)
    router = normalize_address(args.router)
    decimals = validate_decimals(args.token_decimals)
    token_amount, raw_token = parse_amount(args.token_amount, decimals)
    native_amount, raw_native = parse_amount(args.native_amount, 18)
    slippage_bps = parse_percent_to_bps(args.slippage_percent)
    deadline = int(time.time()) + args.deadline_seconds
    output = safe_dir(args.output)
    if output.exists():
        if not args.overwrite:
            raise FileExistsError(f"{output} exists; pass --overwrite")
        shutil.rmtree(output)
    output.mkdir(parents=True)
    plan = {
        "status": "review",
        "action": "add-liquidity-native",
        "network": PHAROS_ATLANTIC,
        "router": router,
        "token": token,
        "token_amount": token_amount,
        "raw_token_amount": str(raw_token),
        "native_amount_phrs": native_amount,
        "raw_native_amount": str(raw_native),
        "slippage_bps": slippage_bps,
        "amount_token_min": str(apply_slippage(raw_token, slippage_bps)),
        "amount_native_min": str(apply_slippage(raw_native, slippage_bps)),
        "deadline": deadline,
        "recipient": args.recipient or "deployer_from_PRIVATE_KEY",
        "warnings": ["Requires a Uniswap-V2-compatible router supplied by the user.", "Spends PHRS gas and native liquidity amount."],
        "steps": ["approve token to router", "call addLiquidityETH on router"],
    }
    (output / "liquidity_plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare an ERC-20 + PHRS liquidity plan.")
    parser.add_argument("--token", required=True)
    parser.add_argument("--router", required=True)
    parser.add_argument("--token-decimals", type=int, required=True)
    parser.add_argument("--token-amount", required=True)
    parser.add_argument("--native-amount", required=True)
    parser.add_argument("--slippage-percent", default="1")
    parser.add_argument("--recipient")
    parser.add_argument("--deadline-seconds", type=int, default=1800)
    parser.add_argument("--output", required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    plan = write_liquidity_plan(args)
    print(json.dumps({"status": "review", "output": args.output, "plan": plan}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
