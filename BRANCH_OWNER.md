# Branch owner: Claude (Anthropic) — `claude/v0-build`

**This branch belongs to Claude.** Other AI agents/operators: do not commit to,
rebase, force-push, or delete this branch. Read it freely; work on your own branch.

- **Owner:** Claude (Anthropic), model Claude Opus 5.5, working for Matt (holymilk09)
- **Created:** 2026-10-08
- **Forked from:** `v0-research-intel` @ `2c08108` ("v0: add MCP server build spec for research-intel layer")
- **Purpose:** an independent, parallel build of the v0 research-intel scope, so Matt can
  grade it against the `v0-research-intel` branch at completion.
- **Every commit by Claude on this branch** carries the trailer
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
  A commit on this branch without that trailer was not made by Claude.

## Target scope (same finish line as the other branch's own docs)

- M2 — relationship engine (`docs/v0/BUILD_DOC.md` §3.3)
- M3 — interest graph + portfolio context (§3.1, §3.2)
- MCP server P1 (`docs/v0/MCP_BUILD_SPEC.md` §9): `brief`, `cohort_summary`,
  `relationship_map`, `hypothesis_status` — read-only, `scan_setups` stays gated

## Rules inherited unchanged

Everything in `docs/v0/HANDOFF_NEXT_OPERATOR.md` and `QC_CONTINUITY_2026-10-04.md`
applies: research-only, no broker/live/shadow, no ledger or cache CSVs in git,
frozen lineage untouched, evidence labels on every claim, exact test counts.

## Status

- 2026-10-08 — Step 1 data layer + step 2 relationship engine (M2): IMPLEMENTED — CODE VERIFIED.
  Real-data sanity gate passed on Robinhood daily bars. See `docs/claude-v0/M2_SANITY_2026-10-08.md`.
- 2026-10-08 — Products built (M3–M6 + research record): IMPLEMENTED — CODE VERIFIED, but
  the brief's claims are NOT validated. Status: BUILT — UNDER VALIDATION. Phased plan and
  frozen gates: `docs/claude-v0/VALIDATION_PLAN.md`. Not connected.
