---
name: pharos-mission-control-agent
description: All-in-one Pharos Agent Center skill for launching ERC-20 tokens, preparing liquidity pool actions, batch sending tokens, and checking wallet balances on Pharos Atlantic Testnet.
---

# Pharos Mission Control Agent

Pharos Mission Control Agent is an all-in-one launch desk for Pharos Atlantic Testnet. It helps an agent move from idea to token launch workflow:

- deploy a fixed-supply ERC-20 token
- prepare a liquidity pool action for that token
- batch send tokens to a community list
- check wallet balances

## Network

- Network: Pharos Atlantic Testnet
- Chain ID: `688689`
- RPC: `https://atlantic.dplabs-internal.com`
- Explorer: `https://atlantic.pharosscan.xyz/`
- Native token: PHRS

## Safety Rules

- Never ask the user to paste a private key in chat.
- Never print, save, log, or commit private keys.
- Write actions require local `PRIVATE_KEY` only.
- Default mode is plan/dry-run.
- Real write actions require `--execute --confirm`.
- Warn that token deploy, liquidity, and batch sends spend PHRS gas.
- Liquidity support is router-configurable. The user must provide the target DEX router address.
- Mainnet is not supported by this version.

## Natural Prompt Examples

```text
Prepare an ERC-20 token on Pharos Atlantic Testnet named Orbit Token with symbol ORBIT, 18 decimals, and total supply 1000000.
```

```text
Prepare liquidity for token 0xToken on Pharos Atlantic Testnet using router 0xRouter with 1000 tokens and 0.1 PHRS, token decimals 18, and 1 percent slippage.
```

```text
Prepare a batch send on Pharos Atlantic Testnet for token 0xToken with decimals 18 using recipients in examples/recipients.csv.
```

```text
Check wallet balance for 0xWallet on Pharos Atlantic Testnet.
```

## Local Prompt Test

```bash
python scripts/agent_prompt_runner.py --prompt-file examples/prompt_deploy.txt
```

## Outputs

- token deploy package in `build/<symbol>-token`
- liquidity plan in `build/liquidity-plan`
- batch send plan in `build/batch-plan`
- balance report JSON in terminal

## Real Write Commands

These require local `PRIVATE_KEY` and explicit confirmation:

```bash
python scripts/deploy_token.py --project-dir build/orbit-token --execute --confirm
python scripts/execute_liquidity.py --plan build/liquidity-plan/liquidity_plan.json --execute --confirm
python scripts/execute_batch.py --plan build/batch-plan/batch_plan.json --execute --confirm
```
