from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path

from common import PHAROS_ATLANTIC, normalize_address, parse_amount, safe_dir, validate_decimals


def load_rows(path: Path, decimals: int) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not {"address", "amount"}.issubset(reader.fieldnames):
            raise ValueError("CSV must include address and amount columns")
        rows = []
        for index, row in enumerate(reader, start=2):
            amount, raw = parse_amount(row["amount"], decimals)
            rows.append({"row": index, "address": normalize_address(row["address"]), "amount": amount, "raw_amount": str(raw)})
    if not rows:
        raise ValueError("no recipients")
    return rows


def write_batch_plan(token: str, decimals: int, input_path: Path, output: Path, overwrite: bool) -> dict:
    token = normalize_address(token)
    decimals = validate_decimals(decimals)
    rows = load_rows(input_path, decimals)
    if output.exists():
        if not overwrite:
            raise FileExistsError(f"{output} exists; pass --overwrite")
        shutil.rmtree(output)
    output.mkdir(parents=True)
    total_raw = sum(int(row["raw_amount"]) for row in rows)
    plan = {
        "status": "safe",
        "action": "batch-send",
        "network": PHAROS_ATLANTIC,
        "token": token,
        "decimals": decimals,
        "recipient_count": len(rows),
        "total_raw_amount": str(total_raw),
        "recipients": rows,
        "safety": "Dry-run by default. Real sends require PRIVATE_KEY plus --execute --confirm.",
    }
    (output / "batch_plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare Mission Control batch send plan.")
    parser.add_argument("--token", required=True)
    parser.add_argument("--decimals", type=int, required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    plan = write_batch_plan(args.token, args.decimals, Path(args.input), safe_dir(args.output), args.overwrite)
    print(json.dumps({"status": plan["status"], "output": args.output, "summary": {"recipient_count": plan["recipient_count"], "total_raw_amount": plan["total_raw_amount"]}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
