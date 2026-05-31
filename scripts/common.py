from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from pathlib import Path


PHAROS_ATLANTIC = {
    "name": "Pharos Atlantic Testnet",
    "chain_id": 688689,
    "rpc_url": "https://atlantic.dplabs-internal.com",
    "explorer": "https://atlantic.pharosscan.xyz/",
    "native_token": "PHRS",
}

ADDRESS_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
NAME_RE = re.compile(r"^[A-Za-z0-9 _.-]{1,64}$")
SYMBOL_RE = re.compile(r"^[A-Z0-9]{1,12}$")


def is_address(value: str) -> bool:
    return bool(ADDRESS_RE.fullmatch(value or ""))


def normalize_address(value: str) -> str:
    if not is_address(value):
        raise ValueError(f"invalid address: {value}")
    return "0x" + value[2:].lower()


def validate_name(value: str) -> str:
    value = (value or "").strip()
    if not NAME_RE.fullmatch(value):
        raise ValueError("token name must be 1-64 simple characters")
    return value


def validate_symbol(value: str) -> str:
    symbol = (value or "").strip().upper()
    if not SYMBOL_RE.fullmatch(symbol):
        raise ValueError("symbol must be 1-12 uppercase letters or numbers")
    return symbol


def validate_decimals(value: int) -> int:
    if value < 0 or value > 18:
        raise ValueError("decimals must be between 0 and 18")
    return value


def parse_amount(value: str, decimals: int) -> tuple[str, int]:
    try:
        amount = Decimal(str(value).strip())
    except InvalidOperation as exc:
        raise ValueError(f"invalid amount: {value}") from exc
    if amount <= 0:
        raise ValueError("amount must be greater than zero")
    raw = amount * (Decimal(10) ** decimals)
    if raw != raw.to_integral_value():
        raise ValueError(f"amount has too many decimals for token decimals={decimals}")
    human = format(amount.normalize(), "f")
    return human, int(raw)


def parse_percent_to_bps(value: str) -> int:
    try:
        percent = Decimal(str(value).strip())
    except InvalidOperation as exc:
        raise ValueError("slippage percent must be numeric") from exc
    if percent < 0 or percent > 50:
        raise ValueError("slippage percent must be between 0 and 50")
    return int(percent * Decimal(100))


def safe_dir(path: str) -> Path:
    output = Path(path).expanduser().resolve()
    if output.name in {"", ".", ".."}:
        raise ValueError("invalid directory")
    return output


def solidity_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')
