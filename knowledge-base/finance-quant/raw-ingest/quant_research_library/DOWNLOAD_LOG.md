# DOWNLOAD_LOG

## Runtime result

PDF byte downloads were not completed inside this environment.

The direct download attempt failed at the filesystem/network layer with DNS resolution failure, for example while trying to fetch an arXiv PDF. Because the environment could not resolve outbound hosts from the file-writing side, embedding PDFs in the final zip would be dishonest.

## What was still completed

- Official/primary source pages were identified for the priority backbone.
- Direct legal PDF URLs were captured where available.
- A manifest and local downloader were created.
- Every group A-R has an `index.md`, `paywalled.md`, and `papers/` placeholder.

## Validation path

Run:

```bash
python3 download_open_pdfs.py
```

The downloader validates downloaded files by checking that the file starts with `%PDF-` and has a non-trivial size. Failures are recorded in `DOWNLOAD_RESULTS.csv` for manual follow-up.
