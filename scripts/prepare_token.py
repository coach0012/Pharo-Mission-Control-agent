from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from common import PHAROS_ATLANTIC, parse_amount, safe_dir, solidity_string, validate_decimals, validate_name, validate_symbol


CONTRACT = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MissionERC20 {{
    string public constant name = "{name}";
    string public constant symbol = "{symbol}";
    uint8 public constant decimals = {decimals};
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    constructor() {{
        totalSupply = {raw_supply};
        balanceOf[msg.sender] = {raw_supply};
        emit Transfer(address(0), msg.sender, {raw_supply});
    }}
    function transfer(address to, uint256 value) external returns (bool) {{
        require(to != address(0), "zero address");
        require(balanceOf[msg.sender] >= value, "balance");
        balanceOf[msg.sender] -= value;
        balanceOf[to] += value;
        emit Transfer(msg.sender, to, value);
        return true;
    }}
    function approve(address spender, uint256 value) external returns (bool) {{
        allowance[msg.sender][spender] = value;
        emit Approval(msg.sender, spender, value);
        return true;
    }}
    function transferFrom(address from, address to, uint256 value) external returns (bool) {{
        require(to != address(0), "zero address");
        require(balanceOf[from] >= value, "balance");
        uint256 allowed = allowance[from][msg.sender];
        require(allowed >= value, "allowance");
        if (allowed != type(uint256).max) allowance[from][msg.sender] = allowed - value;
        balanceOf[from] -= value;
        balanceOf[to] += value;
        emit Transfer(from, to, value);
        return true;
    }}
}}
"""


def write_token_project(name: str, symbol: str, decimals: int, supply: str, output: Path, overwrite: bool) -> dict:
    name = validate_name(name)
    symbol = validate_symbol(symbol)
    decimals = validate_decimals(decimals)
    human_supply, raw_supply = parse_amount(supply, decimals)
    if output.exists():
        if not overwrite:
            raise FileExistsError(f"{output} exists; pass --overwrite")
        shutil.rmtree(output)
    (output / "src").mkdir(parents=True)
    (output / "src" / "MissionERC20.sol").write_text(
        CONTRACT.format(name=solidity_string(name), symbol=symbol, decimals=decimals, raw_supply=raw_supply),
        encoding="utf-8",
    )
    (output / "foundry.toml").write_text('[profile.default]\nsrc = "src"\nout = "out"\nsolc_version = "0.8.20"\n', encoding="utf-8")
    plan = {
        "status": "safe",
        "action": "deploy-token",
        "network": PHAROS_ATLANTIC,
        "token": {"name": name, "symbol": symbol, "decimals": decimals, "total_supply": human_supply, "raw_total_supply": str(raw_supply)},
        "deploy_preview": "forge create --rpc-url https://atlantic.dplabs-internal.com --private-key $PRIVATE_KEY src/MissionERC20.sol:MissionERC20",
        "safety": "Set PRIVATE_KEY locally. Do not paste it in chat.",
    }
    (output / "mission_token_plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a Mission Control ERC-20 deploy package.")
    parser.add_argument("--name", required=True)
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--decimals", type=int, required=True)
    parser.add_argument("--total-supply", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    output = safe_dir(args.output)
    plan = write_token_project(args.name, args.symbol, args.decimals, args.total_supply, output, args.overwrite)
    print(json.dumps({"status": "safe", "output": str(output), "plan": plan}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
