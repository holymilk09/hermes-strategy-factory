"""Strategy Factory v0 research-intel layer (claude/v0-build).

Research-only. No broker, no orders, no execution paths. Every public result
carries an evidence label and the sample size it was computed on.
"""

RESEARCH_ONLY = True
SENT_TO_BROKER = False  # invariant for this whole package; there is nothing to send
