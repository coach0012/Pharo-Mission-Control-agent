from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADDR = r"0x[a-fA-F0-9]{40}"


def m(pattern: str, text: str) -> str | None:
    found = re.search(pattern, text, re.IGNORECASE)
    return found.group(1).strip() if found else None


def display(command: list[str]) -> str:
    items = []
    for item in command:
        if item == sys.executable:
            items.append("python")
        elif item.endswith(".py"):
            items.append(str(Path(item).relative_to(ROOT)))
        else:
            items.append(item)
    return " ".join(f'"{item}"' if any(char.isspace() for char in item) else item for item in items)


def route(prompt: str) -> dict:
    lowered = prompt.lower()
    command: list[str] = []
    action = None
    errors: list[str] = []
    if "balance" in lowered:
        action = "check-balance"
        wallet = m(f"({ADDR})", prompt)
        if not wallet:
            errors.append("missing wallet address")
        else:
            command = [sys.executable, str(ROOT / "scripts" / "check_balance.py"), "--wallet", wallet]
    elif "liquidity" in lowered or "pool" in lowered:
        action = "prepare-liquidity"
        addresses = re.findall(ADDR, prompt)
        token = addresses[0] if len(addresses) > 0 else None
        router = addresses[1] if len(addresses) > 1 else None
        token_amount = m(r"with\s+([0-9]+(?:\.[0-9]+)?)\s+tokens", prompt)
        native_amount = m(r"and\s+([0-9]+(?:\.[0-9]+)?)\s+PHRS", prompt)
        decimals = m(r"token decimals\s+(\d{1,2})", prompt) or m(r"decimals\s+(\d{1,2})", prompt)
        slippage = m(r"([0-9]+(?:\.[0-9]+)?)\s+percent slippage", prompt) or "1"
        for label, value in {"token": token, "router": router, "token amount": token_amount, "native amount": native_amount, "decimals": decimals}.items():
            if not value:
                errors.append(f"missing {label}")
        if not errors:
            command = [sys.executable, str(ROOT / "scripts" / "prepare_liquidity.py"), "--token", token, "--router", router, "--token-decimals", decimals, "--token-amount", token_amount, "--native-amount", native_amount, "--slippage-percent", slippage, "--output", "build/liquidity-plan", "--overwrite"]
    elif "batch" in lowered or "airdrop" in lowered:
        action = "prepare-batch-send"
        token = m(f"({ADDR})", prompt)
        decimals = m(r"decimals\s+(\d{1,2})", prompt)
        csv_file = m(r"recipients in\s+([^\s.]+\.csv)", prompt) or "examples/recipients.csv"
        if not token:
            errors.append("missing token address")
        if not decimals:
            errors.append("missing decimals")
        if not errors:
            command = [sys.executable, str(ROOT / "scripts" / "prepare_batch.py"), "--token", token, "--decimals", decimals, "--input", csv_file, "--output", "build/batch-plan", "--overwrite"]
    elif "token" in lowered and any(word in lowered for word in ("deploy", "prepare", "create")):
        action = "prepare-token"
        name = m(r"named\s+(.+?)\s+with\s+symbol", prompt)
        symbol = m(r"symbol\s+([A-Za-z0-9]{1,12})", prompt)
        decimals = m(r"(\d{1,2})\s+decimals", prompt)
        supply = m(r"total supply\s+([0-9]+(?:\.[0-9]+)?)", prompt)
        for label, value in {"name": name, "symbol": symbol, "decimals": decimals, "total supply": supply}.items():
            if not value:
                errors.append(f"missing {label}")
        if not errors:
            command = [sys.executable, str(ROOT / "scripts" / "prepare_token.py"), "--name", name, "--symbol", symbol, "--decimals", decimals, "--total-supply", supply, "--output", f"build/{symbol.lower()}-token", "--overwrite"]
    else:
        errors.append("prompt did not match Mission Control actions")
    if "pharos" not in lowered and "atlantic" not in lowered:
        errors.append("prompt should mention Pharos or Atlantic Testnet")
    return {
        "agent_selected_skill": "pharos-mission-control-agent" if not errors else None,
        "status": "ready" if not errors else "needs_input",
        "action": action,
        "network": "Pharos Atlantic Testnet" if ("pharos" in lowered or "atlantic" in lowered) else None,
        "planned_action": display(command) if command else None,
        "_execution_command": command,
        "safety_message": "Mission Control plans first. Private keys stay local. Writes require --execute --confirm.",
        "errors": errors,
        "user_prompt": prompt,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Route a natural-language prompt to a Mission Control action.")
    parser.add_argument("--prompt")
    parser.add_argument("--prompt-file")
    parser.add_argument("--execute", action="store_true", help="Run the selected prepare/check action.")
    args = parser.parse_args()
    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text(encoding="utf-8").strip()
    elif args.prompt:
        prompt = args.prompt.strip()
    else:
        raise SystemExit("provide --prompt or --prompt-file")
    result = route(prompt)
    printable = dict(result)
    printable.pop("_execution_command", None)
    print(json.dumps(printable, indent=2, sort_keys=True), flush=True)
    if result["status"] != "ready":
        return 1
    if args.execute and result["_execution_command"]:
        return subprocess.run(result["_execution_command"], cwd=ROOT, check=False).returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
