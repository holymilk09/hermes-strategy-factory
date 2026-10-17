# Strategy Factory MCP server — P1 prototype

Research layer only. Read-only: no execution, no broker, no ledger writes.

## Setup

```bash
python3 -m venv ~/workspace/venvs/sf-mcp
~/workspace/venvs/sf-mcp/bin/pip install -r requirements.txt
```

`requirements.txt` pins `mcp<2` (v2 renamed FastMCP → MCPServer; the prototype targets the v1 API).

## Run

Stdio (for Claude Desktop / any MCP client):

```json
{
  "mcpServers": {
    "strategy-factory": {
      "command": "/home/hatch/workspace/venvs/sf-mcp/bin/python",
      "args": [
        "/home/hatch/workspace/hermes-strategy-factory/docs/v0/tools/mcp_server/mcp_server.py",
        "--forward-dir", "/home/hatch/workspace/goals/strategy-factory-v0-research-intel/hidden_files/forward_ret5d_ma50_v1",
        "--research-root", "/home/hatch/workspace/goals/strategy-factory-v0-research-intel"
      ]
    }
  }
}
```

Self-test:

```bash
~/workspace/venvs/sf-mcp/bin/python mcp_server.py --forward-dir <dir> --research-root <dir> --self-test
```

## Tools

- `brief(interest_profile)` — interest-ranked research brief; ranking is explainable (`why_shown`)
- `cohort_summary()` — resolved record with sample sizes and caveats
- `relationship_map()` — BUILT (2026-10-17): serves the relationship engine's point-in-time clusters / betas / lead-lag when the server is started with `--relationship-json <map.json>` (built by `docs/v0/tools/relationship_engine.py` from Massive bars); returns the pending status when no map is supplied
- `hypothesis_status()` — forward-test state, bars, progress
- `scan_setups()` — GATED until the hypothesis passes its preregistered bars
