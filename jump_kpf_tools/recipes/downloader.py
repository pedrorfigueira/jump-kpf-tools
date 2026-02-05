from pathlib import Path
import requests
import subprocess

import pandas as pd

from jump_kpf_tools.config.configfile import RV_BASE_URL, L2_BASE_URL, KEYWORDS

from jump_kpf_tools.recipes.kws_utils import (
    outdated_obs_ids,
    move_old_versions,
    rename_old_csv,
)

from jump_kpf_tools.recipes.extract_kws import extract_keywords


# -----------------------------
# Session and authentication
# -----------------------------

def auth_check(cookie_file, test_star=None, verbose=True):
    """
    Check whether JUMP authentication cookies are valid by requesting
    a known RV endpoint.
    """
    session = make_jump_session(cookie_file)

    # Use a harmless test target; optionally configurable
    if test_star is None:
        test_star = "toi-1346"  # any known star

    url = RV_BASE_URL.format(star=test_star)
    r = session.get(url, allow_redirects=True, stream=True)

    content_type = r.headers.get("Content-Type", "").lower()

    # ---- HTTP-level failure ----
    if r.status_code != 200:
        raise RuntimeError(f"Auth check failed (HTTP {r.status_code})")

    # ---- HTML login page masquerading as data ----
    if "text/html" in content_type:
        raise RuntimeError(
            "Auth check failed: received HTML (login page). "
            "Cookie is likely expired; re-export cookies from browser."
        )

    # ---- Unexpected content-type ----
    if not any(ct in content_type for ct in ("text/csv", "application/octet-stream")):
        raise RuntimeError(
            f"Auth check failed: unexpected Content-Type '{content_type}'. "
            "This usually indicates an auth or server-side error."
        )

    # ---- Payload sanity check (peek header) ----
    first_chunk = next(r.iter_content(512), b"").strip()
    if not (first_chunk.startswith(b"time,") or first_chunk.startswith(b"#")):
        raise RuntimeError(
            "Auth check failed: response does not look like an RV CSV file. "
            "Authentication or endpoint may be broken."
        )

    if verbose:
        print("✓ Authentication OK (cookie is valid)")


def make_jump_session(cookie_file=None):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0",
        "Accept": "text/csv,application/octet-stream;q=0.9,*/*;q=0.8",
        "Referer": "https://jump.caltech.edu/",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Upgrade-Insecure-Requests": "1",
    })

    if cookie_file:
        session.cookies = load_cookies(cookie_file)

    return session


def load_cookies(cookie_file):
    """Load Netscape-format cookies into requests."""
    jar = requests.cookies.RequestsCookieJar()

    with open(cookie_file) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            fields = line.strip().split("\t")
            if len(fields) >= 7:
                domain, _, path, secure, expiry, name, value = fields
                jar.set(name, value, domain=domain, path=path)

    return jar


def download_rv_csvs(stars, output_dir, cookie_file=None, overwrite=False, verbose=True):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    session = make_jump_session(cookie_file)

    for star in stars:
        url = RV_BASE_URL.format(star=star)
        out_file = output_dir / f"{star}_rv.csv"

        if out_file.exists() and not overwrite:
            if verbose:
                print(f"✓ Exists: {out_file.name}")
            continue

        if verbose:
            print(f"↓ Downloading RV CSV for {star}")

        r = session.get(
            url,
            stream=True,
            allow_redirects=True,
            headers={"Accept": "text/csv,application/octet-stream;q=0.9,*/*;q=0.8"}
        )

        if r.status_code != 200:
            print(f"✗ Failed {star} (HTTP {r.status_code})")
            continue

        content_type = r.headers.get("Content-Type", "").lower()

        # ---- Detect HTML login pages masquerading as CSV ----
        if "text/html" in content_type:
            print(f"✗ Authentication failure for {star}: received HTML instead of CSV")
            if verbose:
                print("  → Check cookies file / login session")
            continue

        # ---- Light sanity check on CSV header ----
        first_chunk = next(r.iter_content(1024))
        if not first_chunk.strip().startswith(b"time,") and not first_chunk.strip().startswith(b"#"):
            print(f"✗ Unexpected content for {star}: does not look like RV CSV")
            continue

        # ---- Write file (we already consumed first chunk) ----
        with open(out_file, "wb") as f:
            f.write(first_chunk)
            for chunk in r.iter_content(8192):
                f.write(chunk)

        if verbose:
            print(f"✓ Saved: {out_file}")


# -----------------------------
# L2 single FITS download
# -----------------------------

def download_l2(session, obs_id, outdir, overwrite=False, verbose=True):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    url = f"{L2_BASE_URL}/{obs_id}_L2.fits"
    outfile = outdir / f"{obs_id}_L2.fits"

    if outfile.exists() and not overwrite:
        if verbose:
            print(f"✓ Exists: {outfile.name}")
        return

    if verbose:
        print(f"↓ Downloading {obs_id}")

    r = session.get(url, stream=True)
    if r.status_code != 200:
        print(f"✗ Failed {obs_id} (HTTP {r.status_code})")
        return

    content_type = r.headers.get("Content-Type", "").lower()
    if "text/html" in content_type:
        print(f"✗ Authentication failure for {obs_id}: received HTML instead of FITS")
        if verbose:
            print("  → Check cookies file / login session")
        return

    with open(outfile, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

    if verbose:
        print(f"✓ Saved: {outfile}")

# -----------------------------
# Bulk L2 FITS download
# -----------------------------

def download_from_csv(
    csv_dir,
    output_dir,
    cookie_file,
    overwrite=False,
    verbose=True
):
    """
    Download KPF L2 FITS files listed in the observation_id column
    of *_rv.csv files.
    """
    csv_dir = Path(csv_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    session = make_jump_session(cookie_file)

    csv_files = csv_dir.glob("*_rv.csv")

    for csv_file in csv_files:
        if verbose:
            print(f"\nProcessing {csv_file.name}")

        try:
            df = pd.read_csv(
                csv_file,
                comment="#",
                skip_blank_lines=True
            )
        except Exception as e:
            if verbose:
                print(f"Skipping {csv_file}: {e}")
            continue

        if "observation_id" not in df.columns:
            if verbose:
                print("Missing observation_id column")
            continue

        # Create target directory
        target = csv_file.stem.replace("_rv", "")
        target_dir = output_dir / target
        target_dir.mkdir(exist_ok=True)

        # Download each observation
        for obs_id in df["observation_id"].dropna().unique():
            download_l2(
                session,
                obs_id,
                target_dir,
                overwrite=overwrite,
                verbose=verbose
            )


def redownload_outdated_l2(fits_root, csv_root=None, cookie_file=None, verbose=True):
    """
    Move outdated L2 FITS files to oldversions/ and re-download fresh versions.
    """
    fits_root = Path(fits_root)
    session = make_jump_session(cookie_file)

    for star_dir in fits_root.iterdir():
        if not star_dir.is_dir():
            continue

        star = star_dir.name
        if verbose:
            print(f"\nRe-downloading outdated FITS for {star}")

        rows = []
        for fits_file in sorted(star_dir.glob("*.fits")):
            data = extract_keywords(fits_file, KEYWORDS)
            rows.append({"filename": fits_file.name, **data})

        obs_ids = outdated_obs_ids(rows)
        if not obs_ids:
            if verbose:
                print(f"✓ {star}: no outdated FITS")
            continue

        moved_any = move_old_versions(star_dir, rows, verbose)

        for obs_id in obs_ids:
            download_l2(
                session=session,
                obs_id=obs_id,
                outdir=star_dir,
                overwrite=True,
                verbose=verbose
            )

        if moved_any and csv_root is not None:
            rename_old_csv(csv_root, star, verbose)
