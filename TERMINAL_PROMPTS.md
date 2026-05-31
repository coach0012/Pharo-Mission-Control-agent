# Pharos Mission Control Agent - Terminal Prompts

## # 1. Deploy Token

```text
Prepare an ERC-20 token on Pharos Atlantic Testnet named Orbit Token with symbol ORBIT, 18 decimals, and total supply 1000000.
```

## # 2. Prepare Liquidity

```text
Prepare liquidity for token 0xToken on Pharos Atlantic Testnet using router 0xRouter with 1000 tokens and 0.1 PHRS, token decimals 18, and 1 percent slippage.
```

## # 3. Batch Send

```text
Prepare a batch send on Pharos Atlantic Testnet for token 0xToken with decimals 18 using recipients in examples/recipients.csv.
```

## # 4. Check Balance

```text
Check wallet balance for 0xWallet on Pharos Atlantic Testnet.
```

## Safety Line

```text
Private keys stay local. The agent plans first and only writes after --execute --confirm.
```

## Real Write Commands

```bash
python scripts/deploy_token.py --project-dir build/orbit-token --execute --confirm
python scripts/execute_liquidity.py --plan build/liquidity-plan/liquidity_plan.json --execute --confirm
python scripts/execute_batch.py --plan build/batch-plan/batch_plan.json --execute --confirm
```
