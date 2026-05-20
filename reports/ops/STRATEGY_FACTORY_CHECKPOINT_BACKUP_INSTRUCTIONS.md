# Strategy Factory Checkpoint Backup Instructions

## Package
- Path: /opt/data/checkpoints/strategy_factory_v0_14_0_checkpoint.tar.gz
- SHA256: 83a91e76dc454efd66a44d69f65517a3296508ac000d21e9e19fb902d4f75efa
- Size: 1.7 MB
- Created: 2026-05-20T01:26:04.916653+00:00

## Recommended Backup Destinations
1. GitHub — create new repo, upload as release asset or commit extracted contents
2. External drive — copy to external storage
3. Cloud storage — upload to S3, GCS, or similar
4. Local backup — copy to /opt/data/backups/

## Restore Note
To restore from this checkpoint:
```bash
cd /opt/data
tar xzf checkpoints/strategy_factory_v0_14_0_checkpoint.tar.gz
```
This restores: feature_factory/, config/, reports/, docs/, alpha_graveyard/, 
checkpoints/, knowledge-base/, README.md, .gitignore

Warning: This is NOT a full system backup. It preserves the strategy factory 
research state only. Hermes Agent itself, session DB, cached data, and .env 
are NOT included.

## Current Research State
- trend-extension: REJECTED, permanently archived
- residual reversion: CONTROLLED_RESEARCH_CANDIDATE_EVENT_BLOCKED
- FMP: SANDBOX_ONLY / FMP_API_KEY missing
- production migration: BLOCKED
- live trading: BLOCKED

## Next Allowed Step After Backup
1. Set FMP_API_KEY externally:
   ```bash
   export FMP_API_KEY="your_key_here"
   ```
2. Rerun Phase 13.5 FMP dry run and coverage audit
3. If FMP coverage + PIT pass, run event-overlay trial
4. Production and live trading remain BLOCKED

No emoji. No hype. No profitability claims. No live-readiness claims.
