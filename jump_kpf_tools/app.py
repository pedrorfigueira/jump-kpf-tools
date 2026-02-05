#!/usr/bin/env python3

import argparse

from jump_kpf_tools.recipes.rv_processing import csv_to_rdb
from jump_kpf_tools.recipes.downloader import auth_check, download_from_csv, download_rv_csvs, redownload_outdated_l2
from jump_kpf_tools.recipes.extract_kws import extract_fits_keywords

from jump_kpf_tools.config.configfile import (
    STAR_LIST,
    DEFAULT_CSV_DIR,
    DEFAULT_KIMA_OUTPUT_DIR,
    DEFAULT_FITS_DIR,
    DEFAULT_SUMMARY_DIR,
    DEFAULT_COOKIE_FILE,
)

def main():
    parser = argparse.ArgumentParser(
        description="JUMP / KPF data processing toolkit"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    auth_parser = subparsers.add_parser(
        "auth-check",
        help="Verify JUMP authentication cookies"
    )
    auth_parser.add_argument(
        "--cookies",
        default=str(DEFAULT_COOKIE_FILE),
        help="jump interface cookies.txt file (see README)"
    )
    auth_parser.add_argument(
        "--test-star",
        default=None,
        help="Star name to test RV endpoint (optional)"
    )
    auth_parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress success output"
    )

    # ---- RV CSV downloader command ----
    rvdl_parser = subparsers.add_parser(
        "download-rv",
        help="Download *_rv.csv files for stars listed in configfile.py"
    )
    rvdl_parser.add_argument(
        "--stars",
        default=None,
        help="Comma-separated list of stars to download (overrides config STAR_LIST)"
    )
    rvdl_parser.add_argument(
        "--csv-dir",
        default=str(DEFAULT_CSV_DIR),
        help="Directory where *_rv.csv files will be stored"
    )
    rvdl_parser.add_argument(
        "--cookies",
        default=str(DEFAULT_COOKIE_FILE),
        help="jump interface cookies.txt file (see README)"
    )
    rvdl_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Redownload existing CSV files"
    )
    rvdl_parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output"
    )

    # ---- RV conversion command ----
    rv_parser = subparsers.add_parser(
        "conv-kima",
        help="Convert jump *_rv.csv files into kima-compatible .rdb files"
    )
    rv_parser.add_argument(
        "--csv-dir",
        default=str(DEFAULT_CSV_DIR),
        help="Directory with *_rv.csv files"
    )
    rv_parser.add_argument(
        "--kima-output-dir",
        default=str(DEFAULT_KIMA_OUTPUT_DIR),
        help="Output directory for kima-ready .rdb files"
    )
    rv_parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output"
    )

    # ---- FITS downloader command ----
    dl_parser = subparsers.add_parser(
        "download-L2",
        help="Download KPF L2 FITS files listed in *_rv.csv files"
    )
    dl_parser.add_argument(
        "--csv-dir",
        default=str(DEFAULT_CSV_DIR),
        help="Directory with *_rv.csv files"
    )
    dl_parser.add_argument(
        "--fits-dir",
        default=str(DEFAULT_FITS_DIR),
        help="Directory where FITS files will be stored"
    )
    dl_parser.add_argument(
        "--cookies",
        default=str(DEFAULT_COOKIE_FILE),
        help="jump interface cookies.txt file (see README)"
    )
    dl_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Redownload existing FITS files"
    )
    dl_parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output"
    )

    # ---- FITS keyword extraction command ----
    kw_parser = subparsers.add_parser(
        "check-KWs",
        help="Extract and check FITS header keywords; associated housekeeping: create Md summaries, rename *_rv.csv with old versions"
    )
    kw_parser.add_argument(
        "--fits-dir",
        default=str(DEFAULT_FITS_DIR),
        help="Directory containing STAR/ FITS subfolders"
    )
    kw_parser.add_argument(
        "--csv-dir",
        default=str(DEFAULT_CSV_DIR),
        help="Directory containing *_rv.csv files"
    )
    kw_parser.add_argument(
        "--summary-dir",
        default=str(DEFAULT_SUMMARY_DIR),
        help="Output directory for Markdown tables"
    )
    kw_parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output"
    )

    # ---- redownload L2 with old versions ----
    rd_parser = subparsers.add_parser(
        "redownload-L2",
        help="Move outdated L2 FITS to oldversions/ and re-download fresh versions"
    )
    rd_parser.add_argument(
        "--fits-dir",
        default=str(DEFAULT_FITS_DIR),
        help="Directory containing STAR/ FITS subfolders"
    )
    rd_parser.add_argument(
        "--csv-dir",
        default=str(DEFAULT_CSV_DIR),
        help="Directory containing *_rv.csv files"
    )
    rd_parser.add_argument(
        "--cookies",
        default=str(DEFAULT_COOKIE_FILE),
        help="jump interface cookies.txt file (see README)"
    )
    rd_parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output"
    )

    args = parser.parse_args()

    # ---- Dispatch ----
    if args.command == "auth-check":
        try:
            auth_check(
                cookie_file=args.cookies,
                test_star=args.test_star,
                verbose=not args.quiet
            )
        except Exception as e:
            print(f"✗ {e}")
            raise SystemExit(1)
    elif args.command == "download-rv":
        stars = (
            [s.strip() for s in args.stars.split(",") if s.strip()]
            if args.stars else STAR_LIST
        )

        download_rv_csvs(
            stars=stars,
            output_dir=args.csv_dir,
            cookie_file=args.cookies,
            overwrite=args.overwrite,
            verbose=not args.quiet
        )
    elif args.command == "conv-kima":
        csv_to_rdb(
            input_dir=args.csv_dir,
            output_dir=args.kima_output_dir,
            verbose=not args.quiet
        )
    elif args.command == "download-L2":
        download_from_csv(
            csv_dir=args.csv_dir,
            output_dir=args.fits_dir,
            cookie_file=args.cookies,
            overwrite=args.overwrite,
            verbose=not args.quiet
        )
    elif args.command == "check-KWs":
        extract_fits_keywords(
            input_root=args.fits_dir,
            output_root=args.summary_dir,
            csv_root=args.csv_dir,
            verbose=not args.quiet
        )
    elif args.command == "redownload-L2":
        redownload_outdated_l2(
            fits_root=args.fits_dir,
            csv_root=args.csv_dir,
            cookie_file=args.cookies,
            verbose=not args.quiet
        )


if __name__ == "__main__":
    main()
