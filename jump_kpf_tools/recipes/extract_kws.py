from pathlib import Path
import csv
import shutil

from astropy.io import fits

from jump_kpf_tools.config.configfile import KEYWORDS, LATEST_DRPHASH

from jump_kpf_tools.recipes.kws_utils import outdated_obs_ids, move_old_versions, rename_old_csv

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
# Orchestration
# -----------------------------

def extract_fits_keywords(input_root, output_root, verbose=True):

    input_root = Path(input_root)
    output_root = Path(output_root)

    complete_dir = output_root / "complete"
    diff_dir = output_root / "diff"
    rerun_dir = output_root / "rerun"

    complete_dir.mkdir(parents=True, exist_ok=True)
    diff_dir.mkdir(parents=True, exist_ok=True)
    rerun_dir.mkdir(parents=True, exist_ok=True)

    # ---- GLOBAL collector ----
    all_rerun_obs = []

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

        # ---- RERUN CSV (per star) ----
        write_rerun_csv(star, rows, rerun_dir, verbose)

        # ---- Collect for global file ----
        rerun_obs = outdated_obs_ids(rows)
        all_rerun_obs.extend(rerun_obs)

    # ======================================================
    # GLOBAL RERUN FILE
    # ======================================================

    if all_rerun_obs:
        alltargets_file = rerun_dir / "alltargets_rerun.txt"

        # Remove duplicates + sort for determinism
        unique_obs = sorted(set(all_rerun_obs))

        with open(alltargets_file, "w") as f:
            for obs in unique_obs:
                f.write(f"{obs}\n")

        if verbose:
            print(f"\n⚠ Global rerun list written: {alltargets_file}")
    elif verbose:
        print("\n✓ No outdated observations across all targets")

