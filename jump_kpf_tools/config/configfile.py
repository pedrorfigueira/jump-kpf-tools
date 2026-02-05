# config/config.py

from pathlib import Path

STAR_LIST = [
    "k2-155",
    "toi-1346",
    "toi-1432",
    "toi-1466",
    "toi-1748",
    "toi-2079",
    "toi-2274",
    "toi-2470",
    "toi-4363",
]

# ---- Default paths for folders ----
DEFAULT_CSV_DIR = Path("data/jumpRVs/")
DEFAULT_KIMA_OUTPUT_DIR = Path("data/kimaRVs/")
DEFAULT_FITS_DIR = Path("data/L2FITS/")
DEFAULT_SUMMARY_DIR = Path("data/processed/")

# ---- jump cookies folder ----
DEFAULT_COOKIE_FILE = Path("jump_kpf_tools/config/jump_cookies.txt")

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
LATEST_DRPHASH = 'fff22091d425c0b20d98c1bb8932a17f0ce64744'