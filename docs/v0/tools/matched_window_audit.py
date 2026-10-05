#!/usr/bin/env python3
"""
Matched-window audit: accepted (13 resolved) vs ghost (159 rejected)
Strategy Factory relative-strength continuation. Operator: Muse, 2026-10-05.

Convention (pre-registered, per QC_CONTINUITY_2026-10-04.md):
- Horizon: 10 completed trading bars after signal, signal bar excluded.
- Price: raw close series used consistently within one source (Yahoo Close, auto_adjust=False).
  IMPORTANT (found 2026-10-05): Yahoo retroactively split-adjusts historical Close. CRWD split 4:1 on 2026-07-02 and HON had a 0.9535 factor on 2026-06-29, so ledger signal prices (recorded pre-split, e.g. CRWD 650.11) differ in LEVEL from current Yahoo signal closes (162.53). Mixing ledger signal price with Yahoo outcome price produces false returns (CRWD -72% artifact). Therefore return = Yahoo outcome_close / Yahoo signal_close, both from the same fetched series. Ledger returns are used only as a replication check; level mismatches are flagged and explained, not silently used.
- Replication first: recompute the 18 MATURE ghost outcome_10d values and all 13 accepted outcomes; only proceed if they tie out.
Outputs: audit_rows.csv (per-observation), summary printed to stdout.
No ledger is modified.
"""
import csv, pathlib, statistics, collections, hashlib, json

HOME = pathlib.Path.home()
REC = HOME/"workspace/goals/strategy-factory-v0-research-intel/hidden_files/recovery-2026-10-03"
RES = HOME/"workspace/goals/strategy-factory-v0-research-intel/hidden_files/resolution-2026-10-04"
AUD = HOME/"workspace/goals/strategy-factory-v0-research-intel/hidden_files/audit-2026-10-05"
RAW = AUD/"raw_yf"

def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def pct(s):
    s=(s or "").strip().replace('%','')
    return float(s) if s else None

def load_yf(sym):
    with open(RAW/f"{sym}.csv", newline='') as f:
        rows=list(csv.DictReader(f))
    series=[]  # (date, close)
    for r in rows:
        series.append((r['Date'][:10], float(r['Close'])))
    series.sort()
    return series

CACHE={}
def closes(sym):
    if sym not in CACHE: CACHE[sym]=load_yf(sym)
    return CACHE[sym]

def tenth_bar(sym, signal_date):
    s=closes(sym)
    dates=[d for d,_ in s]
    if signal_date not in dates: return None, None, f"signal date {signal_date} missing in series"
    i=dates.index(signal_date)
    if i+10 >= len(s): return None, None, "fewer than 10 future bars"
    d,c = s[i+10]
    return d, c, None

def spy_ret(signal_date):
    d,c,_ = tenth_bar("SPY", signal_date)
    s=dict(closes("SPY"))
    return (c/s[signal_date]-1)*100, d

# ---------- load ledgers, verify hashes ----------
expected = {
 REC/"relative_strength_continuation_observation_ledger.csv":"37f6b3388538a93bf156aa7e75e7b4dd2281be7aca285b81fe2a1575da928281",
 REC/"relative_strength_continuation_outcome_ledger.csv":"b1f02f9cfd23f7c919e4d8cd62647b2c46478bf72733ea63c6b00ec5de8d62a9",
 REC/"ghost_ledger.csv":"d55510a51f37fc41c58f62e91268642915c48b1bd75419a612b55bf2a21e8d58",
 RES/"relative_strength_continuation_outcome_ledger_RESOLVED_2026-10-04.csv":"9320d53cad242a2c155ef356289d8d77cc5b9b627b635db32bb89a9fcd2dddd7",
}
for p,h in expected.items():
    assert sha(p)==h, f"hash mismatch {p}"
print("HASHES OK")

ghosts=list(csv.DictReader(open(REC/"ghost_ledger.csv")))
accepted=list(csv.DictReader(open(RES/"relative_strength_continuation_outcome_ledger_RESOLVED_2026-10-04.csv")))

rows=[]  # audit rows
flags=[]

# ---------- accepted ----------
for r in accepted:
    sym=r['symbol']; sdate=r['signal_timestamp'][:10]
    sig=float(r['signal_close'])  # ledger level (pre-split for CRWD)
    series=dict(closes(sym))
    yf_sig=series.get(sdate)
    out_date,out_close,err=tenth_bar(sym,sdate)
    ret=(out_close/yf_sig-1)*100 if (out_close and yf_sig) else None
    ledger_ret=float(r['outcome_return'])*100
    spy,_=spy_ret(sdate)
    rows.append(dict(group="accepted", symbol=sym, signal_date=sdate, outcome_date=out_date,
                     signal_close=sig, outcome_close=out_close, return_pp=ret,
                     ledger_return_pp=ledger_ret, diff_pp=(ret-ledger_ret) if ret is not None else None,
                     spy_return_pp=spy, excess_vs_spy_pp=(ret-spy) if ret is not None else None,
                     failed_gate="", rejection_reason="", data_status="RESOLVED",
                     signal_price_match=("OK" if yf_sig and abs(yf_sig-sig)<0.011 else f"yf_sig={yf_sig} ledger={sig}"),
                     outcome_date_ledger=r['outcome_timestamp'][:10]))
    if out_date != r['outcome_timestamp'][:10]: flags.append(f"accepted {sym} {sdate} outcome date {out_date} != ledger {r['outcome_timestamp'][:10]}")
    if ret is None or abs(ret-ledger_ret)>0.01: flags.append(f"accepted {sym} {sdate} ret {ret} vs ledger {ledger_ret}")

# ---------- ghosts ----------
for r in ghosts:
    sym=r['symbol']; sdate=r['signal_date'][:10]
    sig=float(r['price_at_signal'])  # ledger level
    series=dict(closes(sym)) if (RAW/f"{sym}.csv").exists() else {}
    yf_sig=series.get(sdate)
    out_date,out_close,err=tenth_bar(sym,sdate) if series else (None,None,"no data")
    ret=(out_close/yf_sig-1)*100 if (out_close and yf_sig) else None
    ledger10=pct(r['outcome_10d'])
    spy,_=spy_ret(sdate) if sdate in dict(closes("SPY")) else (None,None)
    rows.append(dict(group="ghost", symbol=sym, signal_date=sdate, outcome_date=out_date or "",
                     signal_close=sig, outcome_close=out_close or "", return_pp=ret,
                     ledger_return_pp=ledger10, diff_pp=(ret-ledger10) if (ret is not None and ledger10 is not None) else "",
                     spy_return_pp=spy, excess_vs_spy_pp=(ret-spy) if (ret is not None and spy is not None) else "",
                     failed_gate=r['failed_gate'], rejection_reason=r['rejection_reason'], data_status=r['data_status'],
                     signal_price_match=("OK" if yf_sig and abs(yf_sig-sig)<0.011 else f"yf_sig={yf_sig} ledger={sig}"),
                     outcome_date_ledger=""))
    if err: flags.append(f"ghost {sym} {sdate} {err}")

# ---------- replication checks ----------
mat=[x for x in rows if x['group']=='ghost' and x['data_status']=='MATURE']
print(f"\nREPLICATION ghost MATURE: n={len(mat)}")
bad=[x for x in mat if x['diff_pp']=="" or abs(x['diff_pp'])>0.06]
for x in mat: print(f"  {x['signal_date']} {x['symbol']:5s} recomputed {x['return_pp']:+.2f}% ledger {x['ledger_return_pp']:+.2f}% diff {x['diff_pp']:+.3f}pp signal_match={x['signal_price_match']}")
print("  replication failures (>0.06pp):", len(bad))
acc=[x for x in rows if x['group']=='accepted']
badacc=[x for x in acc if abs(x['diff_pp'])>0.01]
print(f"REPLICATION accepted: n={len(acc)} failures(>0.01pp): {len(badacc)}")
sigbad=[x for x in rows if x['signal_price_match']!="OK"]
print(f"SIGNAL PRICE mismatches: {len(sigbad)}")
for x in sigbad[:20]: print("  ", x['group'], x['symbol'], x['signal_date'], x['signal_price_match'])

# ---------- summaries ----------
def summ(label, xs):
    vals=[x['return_pp'] for x in xs if isinstance(x['return_pp'],(int,float))]
    if not vals: print(f"{label}: no values"); return
    exc=[x['excess_vs_spy_pp'] for x in xs if isinstance(x['excess_vs_spy_pp'],(int,float))]
    print(f"{label}: n={len(vals)} mean {statistics.mean(vals):+.4f}% median {statistics.median(vals):+.4f}% hit {sum(v>0 for v in vals)}/{len(vals)} ({sum(v>0 for v in vals)/len(vals)*100:.1f}%) >+5% {sum(v>5 for v in vals)} <-5% {sum(v<-5 for v in vals)} mean_excess_vs_SPY {statistics.mean(exc):+.4f}pp" if exc else f"{label}: n={len(vals)} mean {statistics.mean(vals):+.4f}%")

print("\n== PRIMARY: same signal date, 10-bar, raw close ==")
for d in ['2026-06-05','2026-07-01']:
    summ(f"accepted {d}", [x for x in acc if x['signal_date']==d])
    summ(f"ghost    {d}", [x for x in rows if x['group']=='ghost' and x['signal_date']==d])

print("\n== SECONDARY: pooled matched-horizon (NOT date-matched) ==")
summ("accepted all", acc)
summ("ghost all", [x for x in rows if x['group']=='ghost'])
summ("ghost MATURE-ledger subset", mat)

print("\n== Ghost by failed gate (pooled, 10-bar recomputed) ==")
for gate, xs in sorted(collections.defaultdict(list, {g:[x for x in rows if x['group']=='ghost' and x['failed_gate']==g] for g in set(x['failed_gate'] for x in rows if x['group']=='ghost')}).items()):
    summ(f"ghost gate={gate}", xs)

print("\n== Ghost by signal date ==")
for d in sorted(set(x['signal_date'] for x in rows if x['group']=='ghost')):
    summ(f"ghost {d}", [x for x in rows if x['group']=='ghost' and x['signal_date']==d])

print("\n== Accepted by signal date ==")
for d in sorted(set(x['signal_date'] for x in acc)):
    summ(f"accepted {d}", [x for x in acc if x['signal_date']==d])

print("\nFLAGS:", len(flags))
for f in flags[:40]: print(" -",f)

with open(AUD/"audit_rows.csv","w",newline='') as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print("\nwrote audit_rows.csv rows", len(rows))
