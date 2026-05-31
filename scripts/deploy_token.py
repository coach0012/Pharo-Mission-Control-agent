from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

from common import PHAROS_ATLANTIC


def missing_tools() -> list[str]:
    return [tool for tool in ("forge", "cast") if shutil.which(tool) is None]


def main() -> int:
    parser = argparse.ArgumentParser(description="Deploy a prepared Mission Control token package.")
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm", action="store_true")
    args = parser.parse_args()
    project = Path(args.project_dir).resolve()
    plan_path = project / "mission_token_plan.json"
    contract_path = project / "src" / "MissionERC20.sol"
    if not plan_path.exists() or not contract_path.exists():
        raise SystemExit("missing mission_token_plan.json or src/MissionERC20.sol")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    tools = missing_tools()
    summary = {
        "status": "ready" if not tools else "missing_foundry",
        "action": "deploy-token",
        "network": PHAROS_ATLANTIC,
        "project_dir": str(project),
        "token": plan["token"],
        "private_key_env_set": bool(os.environ.get("PRIVATE_KEY")),
        "missing_tools": tools,
        "safety": "PRIVATE_KEY is never printed. Do not paste private keys in chat.",
    }
    print(json.dumps(summary, indent=2), flush=True)
    if not args.execute:
        return 0
    if not args.confirm:
        raise SystemExit("deployment requires --confirm")
    if tools:
        raise SystemExit("install Foundry forge and cast first")
    private_key = os.environ.get("PRIVATE_KEY")
    if not private_key:
        raise SystemExit("PRIVATE_KEY is not set locally")
    build = subprocess.run(["forge", "build"], cwd=project, check=False)
    if build.returncode != 0:
        raise SystemExit("forge build failed")
    deploy = subprocess.run(
        [
            "forge",
            "create",
            "--rpc-url",
            PHAROS_ATLANTIC["rpc_url"],
            "--private-key",
            private_key,
            "src/MissionERC20.sol:MissionERC20",
        ],
        cwd=project,
        check=False,
    )
    return deploy.returncode


if __name__ == "__main__":
    raise SystemExit(main())
