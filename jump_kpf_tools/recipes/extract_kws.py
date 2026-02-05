from pathlib import Path
import csv
import shutil

from astropy.io import fits

from jump_kpf_tools.config.configfile import KEYWORDS, LATEST_DRPHASH
from jump_kpf_tools.recipes.downloader import download_l2, make_jump_session


# -----------------------------
# Core keyword extraction
# -----------------------------

def extract_keywords(fits_file, keyword_map):
    values = {}

    with fits.open(fits_file) as hdul:
        for ext, keys in keyword_map.items():
            header = None
            try:
                header = hdul[ext].header
            except Exception:
                pass

            for key in keys:
                if header is None:
                    values[f"{ext}.{key}"] = "MISSING_EXT"
                else:
                    values[f"{ext}.{key}"] = header.get(key, "MISSING")

    return values


# -----------------------------
# Output helpers
# -----------------------------

def write_markdown_table(star, rows, outpath, verbose=True):
    if not rows:
        if verbose:
            print(f"⚠ No data for {star}")
        return

    headers = ["filename"] + [k for k in rows[0].keys() if k != "filename"]

    with open(outpath, "w") as f:
        f.write(f"# {star}\n\n")
        f.write("| " + " | ".join(headers) + " |\n")
        f.write("|" + "|".join(["---"] * len(headers)) + "|\n")

        for row in rows:
            f.write("| " + " | ".join(str(row[h]) for h in headers) + " |\n")

    if verbose:
        print(f"✓ Wrote {outpath}")


def filter_constant_columns(rows):
    if not rows:
        return rows

    keys = list(rows[0].keys())
    keep = ["filename"]

    for key in keys:
        if key == "filename":
            continue
        values = {row[key] for row in rows}
        if len(values) > 1:
            keep.append(key)

    return [{k: row[k] for k in keep} for row in rows]


def write_rerun_csv(star, rows, outdir, verbose=True):
    rerun_obs = outdated_obs_ids(rows)

    if not rerun_obs:
        if verbose:
            print(f"✓ No reruns needed for {star}")
        return

    outpath = outdir / f"{star}_rerun.csv"

    with open(outpath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["observation_id"])
        for obs in rerun_obs:
            writer.writerow([obs])

    if verbose:
        print(f"⚠ Rerun list written: {outpath}")


# -----------------------------
# DRPHASH logic
# -----------------------------

def outdated_obs_ids(rows):
    obs_ids = []
    for row in rows:
        if row.get("PRIMARY.DRPHASH") != LATEST_DRPHASH:
            obs_ids.append(row["filename"].replace("_L2.fits", ""))
    return obs_ids


# -----------------------------
# File management
# -----------------------------

def move_old_versions(star_dir, rows, verbose=True):
    old_dir = star_dir / "oldversions"
    old_dir.mkdir(exist_ok=True)

    moved = False
    for row in rows:
        if row.get("PRIMARY.DRPHASH") != LATEST_DRPHASH:
            fits_name = row["filename"]
            src = star_dir / fits_name
            dst = old_dir / fits_name

            if src.exists():
                shutil.move(src, dst)
                moved = True
                if verbose:
                    print(f"→ Moved outdated FITS: {fits_name}")
            elif verbose:
                print(f"⚠ Missing FITS on disk: {fits_name}")

    if not moved and verbose:
        print("✓ No outdated FITS to move")

    return moved


def rename_old_csv(csv_dir, star, verbose=True):
    csv_dir = Path(csv_dir)
    src = csv_dir / f"{star}_rv.csv"
    dst = csv_dir / f"{star}_rv_oldversion.csv"

    if not src.exists():
        if verbose:
            print(f"⚠ CSV not found: {src}")
        return

    if dst.exists():
        if verbose:
            print(f"⚠ Oldversion CSV already exists: {dst}")
        return

    src.rename(dst)
    if verbose:
        print(f"→ Renamed CSV: {src.name} → {dst.name}")


# -----------------------------
# Re-download logic
# -----------------------------

def redownload_l2(obs_ids, outdir, cookie_file=None, overwrite=True, verbose=True):
    if not obs_ids:
        return

    session = make_jump_session(cookie_file)

    for obs_id in obs_ids:
        download_l2(
            session=session,
            obs_id=obs_id,
            outdir=outdir,
            overwrite=overwrite,
            verbose=verbose
        )


# -----------------------------
# Orchestration
# -----------------------------

def extract_fits_keywords(input_root, output_root, csv_root=None,
                          cookie_file=None, repeatdownload=False, verbose=True):

    input_root = Path(input_root)
    output_root = Path(output_root)

    complete_dir = output_root / "complete"
    diff_dir = output_root / "diff"
    rerun_dir = output_root / "rerun"

    complete_dir.mkdir(parents=True, exist_ok=True)
    diff_dir.mkdir(parents=True, exist_ok=True)
    rerun_dir.mkdir(parents=True, exist_ok=True)

    for star_dir in input_root.iterdir():
        if not star_dir.is_dir():
            continue

        star = star_dir.name
        if verbose:
            print(f"\nProcessing {star}")

        rows = []
        for fits_file in sorted(star_dir.glob("*.fits")):
            data = extract_keywords(fits_file, KEYWORDS)
            rows.append({"filename": fits_file.name, **data})

        # ---- COMPLETE ----
        write_markdown_table(star, rows, complete_dir / f"{star}.md", verbose)

        # ---- DIFF ----
        diff_rows = filter_constant_columns(rows)
        if diff_rows and len(diff_rows[0]) > 1:
            write_markdown_table(star, diff_rows, diff_dir / f"{star}.md", verbose)
        elif verbose:
            print(f"ℹ No varying keywords for {star}")

        # ---- RERUN CSV ----
        write_rerun_csv(star, rows, rerun_dir, verbose)

        # ---- REPEATDOWNLOAD ----
        if repeatdownload:
            if verbose:
                print(f"↻ repeatdownload enabled for {star}")

            moved_any = move_old_versions(star_dir, rows, verbose)
            obs_ids = outdated_obs_ids(rows)

            redownload_l2(
                obs_ids=obs_ids,
                outdir=star_dir,
                cookie_file=cookie_file,
                overwrite=True,
                verbose=verbose
            )

            if moved_any and csv_root is not None:
                rename_old_csv(csv_root, star, verbose)
