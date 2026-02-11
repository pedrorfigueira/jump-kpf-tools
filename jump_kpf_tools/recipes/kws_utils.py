# kws_utils.py
from pathlib import Path
import shutil
from jump_kpf_tools.config.configfile import LATEST_DRPHASH

def outdated_obs_ids(rows):
    return [
        row["filename"].replace("_L2.fits", "")
        for row in rows
        if row.get("PRIMARY.DRPHASH") != LATEST_DRPHASH
    ]

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
    return moved

def rename_old_csv(csv_dir, star, verbose=True):
    csv_dir = Path(csv_dir)
    src = csv_dir / f"{star}_rv.csv"
    dst = csv_dir / f"{star}_rv_oldversion.csv"

    if src.exists() and not dst.exists():
        src.rename(dst)
        if verbose:
            print(f"→ Renamed CSV: {src.name} → {dst.name}")

def rename_old_md_tables(summary_root, star, verbose=True):
    """
    Rename existing Markdown keyword summary tables to *_oldversion.md
    """
    summary_root = Path(summary_root)

    subdirs = ["complete", "diff", "rerun"]

    for sub in subdirs:
        subdir = summary_root / sub
        if not subdir.exists():
            continue

        # .md files
        md_file = subdir / f"{star}.md"
        if md_file.exists():
            new_name = subdir / f"{star}_oldversion.md"
            if not new_name.exists():
                md_file.rename(new_name)
                if verbose:
                    print(f"→ Renamed summary: {md_file.name} → {new_name.name}")

        # rerun CSV
        rerun_file = subdir / f"{star}_rerun.csv"
        if rerun_file.exists():
            new_name = subdir / f"{star}_rerun_oldversion.csv"
            if not new_name.exists():
                rerun_file.rename(new_name)
                if verbose:
                    print(f"→ Renamed rerun list: {rerun_file.name} → {new_name.name}")

def rename_global_rerun(summary_root, verbose=True):
    summary_root = Path(summary_root)
    rerun_dir = summary_root / "rerun"

    global_file = rerun_dir / "alltargets_rerun.txt"
    if global_file.exists():
        new_name = rerun_dir / "alltargets_rerun_oldversion.txt"
        if not new_name.exists():
            global_file.rename(new_name)
            if verbose:
                print(f"→ Renamed global rerun list: {new_name.name}")