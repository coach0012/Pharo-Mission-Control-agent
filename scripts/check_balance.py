from __future__ import annotations

import argparse
import json
import urllib.request

from common import PHAROS_ATLANTIC, normalize_address


BALANCE_OF = "70a08231"
DECIMALS = "313ce567"
SYMBOL = "95d89b41"


def rpc(method: str, params: list) -> str:
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(PHAROS_ATLANTIC["rpc_url"], data=payload, headers={"content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as response:
        body = json.loads(response.read().decode())
    if "error" in body:
        raise RuntimeError(body["error"])
    return body["result"]


def pad(address: str) -> str:
    return normalize_address(address)[2:].rjust(64, "0")


def hex_int(value: str) -> int:
    return int(value, 16)


def decode_symbol(value: str) -> str:
    raw = bytes.fromhex(value[2:])
    if len(raw) >= 96:
        size = int.from_bytes(raw[32:64], "big")
        return raw[64 : 64 + size].decode("utf-8", "ignore") or "UNKNOWN"
    if len(raw) == 32:
        return raw.rstrip(b"\x00").decode("utf-8", "ignore") or "UNKNOWN"
    return "UNKNOWN"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check wallet balance on Pharos Atlantic Testnet.")
    parser.add_argument("--wallet", required=True)
    parser.add_argument("--token", action="append", default=[], help="Optional ERC-20 token address. Repeatable.")
    args = parser.parse_args()
    wallet = normalize_address(args.wallet)
    native_raw = hex_int(rpc("eth_getBalance", [wallet, "latest"]))
    report = {
        "network": PHAROS_ATLANTIC,
        "wallet": wallet,
        "native": {"symbol": "PHRS", "raw_balance": str(native_raw), "balance": str(native_raw / 10**18)},
        "tokens": [],
    }
    for token in args.token:
        token = normalize_address(token)
        decimals = hex_int(rpc("eth_call", [{"to": token, "data": "0x" + DECIMALS}, "latest"]))
        symbol = decode_symbol(rpc("eth_call", [{"to": token, "data": "0x" + SYMBOL}, "latest"]))
        raw = hex_int(rpc("eth_call", [{"to": token, "data": "0x" + BALANCE_OF + pad(wallet)}, "latest"]))
        report["tokens"].append({"token": token, "symbol": symbol, "decimals": decimals, "raw_balance": str(raw), "balance": str(raw / (10**decimals))})
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
