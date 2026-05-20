# Point-in-Time and Bias Controls

## Bias checklist

| Bias | Control |
|---|---|
| Look-ahead | Features only use data observable before decision time. |
| Survivorship | Include delisted/failed assets where relevant. |
| Selection | Universe rule must be defined before evaluation. |
| Data snooping | Lock validation/test sets before parameter search. |
| Multiple testing | Track number of trials and use PSR/DSR/PBO-style controls. |
| Publication/revision | Use release timestamps, not final revised values. |
| Corporate action | Explicit raw vs adjusted policy. |
| Calendar | Exchange-specific sessions and holidays. |
| Fill optimism | Realistic spread/slippage/impact model. |

## Rule

Every feature must answer: “Could the bot legally know this exact value at this exact timestamp?”
