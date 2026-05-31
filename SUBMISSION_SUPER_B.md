Skill name: Pharos Mission Control Agent

Short description: An all-in-one Pharos Agent Center skill that turns normal language into a token launch workflow on Pharos Atlantic Testnet. It can prepare/deploy an ERC-20 token, prepare/execute liquidity, prepare/execute batch sends, and check wallet balances.

GitHub link: ADD_YOUR_GITHUB_REPO_LINK_HERE

Email: ADD_YOUR_EMAIL_HERE

Supported framework: Codex / Claude Code / OpenClaw style Agent Center skill.

Why it is unique: Mission Control feels like a launch desk for builders. A user asks in normal words, and the agent routes the task to the right safe action.

Main abilities:
- Token deploy package and executor
- Liquidity planner and executor
- Batch send planner and executor
- Wallet balance checker
- Natural-language prompt router
- CSV recipient validation
- Dry-run first safety flow

Prompt examples:
"Prepare an ERC-20 token on Pharos Atlantic Testnet named Orbit Token with symbol ORBIT, 18 decimals, and total supply 1000000."
"Prepare liquidity for token 0xToken using router 0xRouter with 1000 tokens and 0.1 PHRS."
"Prepare a batch send for token 0xToken using recipients in examples/recipients.csv."
"Check wallet balance for 0xWallet on Pharos Atlantic Testnet."

Setup: WSL2 + Ubuntu is recommended on Windows. Python 3.10+ is required. Foundry cast/forge are required for real write actions.

Safety: Private keys are never pasted into chat. Write actions use local PRIVATE_KEY only and require --execute --confirm. Liquidity requires a user-provided DEX router address.

Test result: Ran 3 tests - OK

No demo link included.
