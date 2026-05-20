# FMP Justification After Residual Random Pruning

Decision: ADD_FMP_NEXT_FOR_EVENT_BLOCKER

## Why
Residual_z + GOOD/ACCEPTABLE fit BEATS strategy-conditioned random pruning for both
mean_reversion and structural_mr. The filter has demonstrated statistical value beyond
random selection. However, residual_z remains vulnerable to earnings, guidance, and
fundamental repricing events that current price/volume proxies cannot detect.

FMP is now justified to:
- Add earnings calendar (block entries 5d before earnings)
- Detect guidance cuts (block entries for 10d)
- Flag major EPS surprises (skip fading real repricing)
- Improve sector/industry classification for residual mapping

## Status
Integration: NOT PERFORMED (Phase 13)
