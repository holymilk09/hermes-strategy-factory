# Next Steps

Priority order — execute only after current state is checkpointed:

1. **Set FMP_API_KEY externally** (if using FMP)
   ```bash
   export FMP_API_KEY=<your_key>
   # Or add to ~/.hermes/.env (never commit .env)
   ```

2. **Run FMP Phase 13.5 dry run and coverage audit**
   - 3-symbol API test (AAPL, NVDA, MSFT)
   - 12-field coverage audit
   - 76-symbol universe coverage check
   - Point-in-time validation

3. **Build event blocker**
   - earnings_within_5d / earnings_day as primary blockers
   - Sector/industry metadata from FMP
   - Manual CSV event tracker as optional fallback

4. **Test residual event overlay**
   - Only after event blocker is validated
   - Controlled research backtest with event blocking
   - Random pruning with event-filtered trades

5. **Production consideration**
   - Only after: event blocker works, event overlay backtest passes, all gates cleared
   - Currently: MONTHS away at minimum
