# VPS Extraction Checklist — run at the laptop

Goal: pull every irreplaceable Strategy Factory file off the VPS **before**
anything else happens there. No resolver runs, no writes, no "fixes" during
extraction. Reads only.

Do this the moment the gateway is back up.

## 0. Confirm what you're looking at

```bash
ssh <vps>
cd ~/hermes-strategy-factory   # or wherever the repo lives on the VPS
git status --short
git log --oneline -3
git rev-parse HEAD
```

Expected: clean tree at `1f1a238eb8c17f2340699ed6d6a30017fe3eeb13`.
If the VPS tree is dirty or ahead of that commit, STOP and report what differs
before copying anything — the working tree may be newer than the last
reconciled state.

## 1. Copy the ledgers (the irreplaceable files)

```bash
mkdir -p ~/sf-recovery-20260929
cd ~/hermes-strategy-factory
cp data/paper_observation/relative_strength_continuation_observation_ledger.csv ~/sf-recovery-20260929/
cp data/paper_observation/relative_strength_continuation_outcome_ledger.csv   ~/sf-recovery-20260929/
cp data/trust_calibration/ghost_ledger.csv                                     ~/sf-recovery-20260929/
```

## 2. Verify integrity on the spot

```bash
cd ~/sf-recovery-20260929
sha256sum *.csv
```

Compare against these anchors (from the last reconciled checkpoint):

- observation ledger: `37f6b3388538a93bf156aa7e75e7b4dd2281be7aca285b81fe2a1575da928281`
- outcome ledger:     `b1f02f9cfd23f7c919e4d8cd62647b2c46478bf72733ea63c6b00ec5de8d62a9`
- ghost ledger:       `d55510a51f37fc41c58f62e91268642915c48b1bd75419a612b55bf2a21e8d58`

- All three match → recovery is complete. Skip to §5.
- Any mismatch → STOP. Do not rerun anything. Photograph/screenshot the
  `sha256sum` output and the row counts (`wc -l *.csv`), then report. A
  mismatch means the disk state moved past the last checkpoint and needs
  analysis, not a rerun.

## 3. Copy the supporting state (only if §2 passed)

```bash
cd ~/hermes-strategy-factory
# cache manifest: which symbols have data, and how fresh
ls data/cache/ohlcv_1d/ | head -30
ls data/cache/ohlcv_1d/ | wc -l
# per-symbol freshness for the pending cohort
for s in ARQQ ASML LLY MU SNOW UNH; do
  echo "== $s =="
  tail -3 data/cache/ohlcv_1d/${s}.csv 2>/dev/null || echo "MISSING FILE"
done
# key material — list only, then copy to a SEPARATE secure location
ls -la /opt/data/backups/ | grep -i "key\|.env"
```

Copy any `*key*` files to `~/sf-recovery-20260929/keys/` (mode 600), then move
them into the password manager and delete the plaintext copies. **Never paste
key contents into any chat.**

## 4. Private backups repo (fallback if disk is stale)

The July 8 encrypted backup lives at
`github.com/holymilk09/hermes-strategy-factory-backups`,
release `backup-phase7d-20260708-164414` (15,584 bytes, SHA
`f5aec2bd96974ff2119d520784acc0294a070fc936821f44755d2fca8fc867a1`).
Download the release asset via the browser if git auth is awkward. It is only
useful together with `/opt/data/backups/.phase7d_key` from §3.

## 5. Get the files to Muse

`scp` (or any transfer) the `~/sf-recovery-20260929/` directory contents —
CSVs only, never keys — to the laptop, then hand them to Muse. Muse will
re-verify hashes, diff row counts against the 13/7/6 manifest, and only then
discuss next steps.

## Stop conditions

- Hashes don't match → stop, report, don't rerun.
- VPS tree dirty/ahead → stop, report the diff first.
- Any urge to "just run the resolver to fix it" → stop. Resolution is a
  separate controlled procedure (`RESOLUTION_RUNBOOK.md`), never part of
  extraction.
