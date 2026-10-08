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
- `relationship_map()` — PLANNED, returns pending status until the relationship engine is built
- `hypothesis_status()` — forward-test state, bars, progress
- `scan_setups()` — GATED until the hypothesis passes its preregistered bars
