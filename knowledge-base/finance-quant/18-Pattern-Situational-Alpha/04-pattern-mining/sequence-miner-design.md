---
title: Sequence Miner Design
pillar: 18
---

# Pattern Mining Engine Design

## Purpose
Discover recurring price-path sequences without pre-imposed visual labels.

## Components
1. swing_point_detector.py — zigzag/swing detection at configurable N-bar sensitivity
2. wave_shape_features.py — encode wave geometry into numeric vectors
3. sequence_miner.py — find recurring subsequences in swing/return sequences
4. motif_search.py — identify statistically significant motifs vs random null
5. parameter_grid_logger.py — log all parameter variants tested (data snooping guard)

## Key Design Principle
Avoid subjective trendlines. Every detected pattern must output numeric geometry.
Every mined candidate must pass validation (Section 05) before becoming alert-ready.
