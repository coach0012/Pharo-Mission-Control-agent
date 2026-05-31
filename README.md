# Pharos Mission Control Agent

All-in-one Agent Center skill for Pharos Atlantic Testnet.

## Features

- ERC-20 token deploy package generator
- Liquidity pool action planner for Uniswap-V2-style routers
- ERC-20 batch send planner
- Wallet native/token balance checker
- Natural-language prompt router
- Dry-run first, explicit confirmation for real write actions

## Setup

Recommended for Windows users:

```text
WSL2 + Ubuntu
Python 3.10+
Foundry: forge and cast
```

Native Windows Python can run the planning and balance scripts, but WSL + Ubuntu is recommended for write workflows.

Never paste private keys in chat. Use local environment variables only:

```bash
export PRIVATE_KEY="YOUR_PRIVATE_KEY"
```

PowerShell:

```powershell
$env:PRIVATE_KEY="YOUR_PRIVATE_KEY"
```

## Prompt Routing

```bash
python scripts/agent_prompt_runner.py --prompt-file examples/prompt_deploy.txt
python scripts/agent_prompt_runner.py --prompt-file examples/prompt_liquidity.txt
python scripts/agent_prompt_runner.py --prompt-file examples/prompt_batch.txt
python scripts/agent_prompt_runner.py --prompt-file examples/prompt_balance.txt
```

Add `--execute` to run the safe prepare/check action selected by the prompt. Write transactions still require their own `--execute --confirm` command.

## Real Write Commands

Deploy a prepared token:

```bash
python scripts/deploy_token.py --project-dir build/orbit-token --execute --confirm
```

Execute a prepared liquidity action:

```bash
python scripts/execute_liquidity.py --plan build/liquidity-plan/liquidity_plan.json --execute --confirm
```

Execute a prepared batch send:

```bash
python scripts/execute_batch.py --plan build/batch-plan/batch_plan.json --execute --confirm
```

## Tests

```bash
python -m unittest discover -s tests
```
