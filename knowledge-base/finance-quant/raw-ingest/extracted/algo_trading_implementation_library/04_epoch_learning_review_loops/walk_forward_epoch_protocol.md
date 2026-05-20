# Walk-Forward Epoch Protocol

## Protocol

1. Define hypothesis and falsification rule.
2. Lock train/validation/test dates.
3. Train or select parameters only on train/validation.
4. Evaluate once on test.
5. Run stress and cost sensitivity.
6. Generate heatmaps.
7. Write review.
8. Decide: promote, reject, or hold.

## Example

| Epoch | Train | Validation | Test | Decision |
|---|---|---|---|---|
| E001 | 2018-2021 | 2022 | 2023 | hold |
| E002 | 2019-2022 | 2023 | 2024 | reject |
| E003 | 2020-2023 | 2024 | 2025 | promote to paper |
