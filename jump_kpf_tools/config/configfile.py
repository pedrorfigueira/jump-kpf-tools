# config/config.py

from pathlib import Path

STAR_LIST = [
    # regular THIRSTEE list
    #"k2-155",
    #"toi-1346",
    #"toi-1432",
    #"toi-1466",
    #"toi-1748",
    #"toi-2079",
    #"toi-2274",
    #"toi-2470",
    #"toi-4363",
    # OrCAS
    "toi-1180",
    "toi-1184",
    "toi-1630",
    "toi-1691",
    "toi-1716",
    "toi-1723",
    "toi-1739",
    "toi-1744",
    "toi-1758",
    "toi-1772",
    "toi-1777",
    "toi-2211",
    "toi-5726",
    "toi-6054",
]

# ---- Default paths for folders ----
DEFAULT_CSV_DIR = Path("data/jumpRVs/")
DEFAULT_KIMA_OUTPUT_DIR = Path("data/kimaRVs/")
DEFAULT_FITS_DIR = Path("data/L2FITS/")
DEFAULT_SUMMARY_DIR = Path("data/processed/")
DEFAULT_PLOT_DIR = Path("data/plots/")

# Path to the installed package directory
PACKAGE_ROOT = Path(__file__).resolve().parent.parent

# ---- jump cookies folder ----
DEFAULT_COOKIE_FILE = PACKAGE_ROOT / "config" / "jump_cookies.txt"

# ---- jump base URLs ----
RV_BASE_URL = "https://jump.caltech.edu/star/{star}/rv/"
L2_BASE_URL = "https://jump.caltech.edu/api/fits/kpf/L2"

# ---- KWs to be extracted and checked for change ----
KEYWORDS = {
    "PRIMARY": [
        "OBJECT", "OCTAGON", "SCI-OBJ", "CAL-OBJ", "SKY-OBJ",
        "BIASDONE", "DARKDONE", "FLATDONE", "DRFCOR", "DRFTRV", "MOONSEP",
        "DRPHASH", "DRPTAG", "DRPTAGMB", "DRPTAGMD", "DRPTAGMF",
        "BIASFILE", "DARKFILE", "FLATFILE", "PIXMASK",
        "WLSFILE", "WLSFILE2", "STATWREF",
    ],
}

# ---- HASH of the latest pipeline ----
LATEST_DRPHASH = '81609b0ac0ab6d12536fb771bfdd0112001340c3'