# Agent Center Guide

## Install Path

Codex:

```text
~/.codex/skills/pharos-mission-control-agent/
```

Windows Codex path:

```text
C:\Users\user\.codex\skills\pharos-mission-control-agent
```

Claude Code:

```text
~/.claude/skills/pharos-mission-control-agent/
```

OpenClaw:

```text
~/.openclaw/skills/pharos-mission-control-agent/
```

## Verify

Start a new agent session and check skills:

```text
/skills
```

Look for:

```text
pharos-mission-control-agent
```

## How The Agent Uses It

The user writes a normal prompt. The agent selects Mission Control, validates the request, prepares a transparent plan, and only performs write actions after local key setup plus explicit confirmation.

