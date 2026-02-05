from pathlib import Path
import requests
import pandas as pd

from jump_kpf_tools.config.configfile import RV_BASE_URL, L2_BASE_URL


# -----------------------------
# Session and authentication
# -----------------------------

def make_jump_session(cookie_file=None):
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})

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
    """
    Download STAR_rv.csv files for a list of stars.
    """
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

        r = session.get(url, stream=True)
        if r.status_code != 200:
            print(f"✗ Failed {star} (HTTP {r.status_code})")
            continue

        with open(out_file, "wb") as f:
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
