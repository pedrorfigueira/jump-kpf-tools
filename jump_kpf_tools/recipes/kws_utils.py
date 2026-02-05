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
