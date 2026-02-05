#!/usr/bin/env python3

import argparse

from jump_kpf_tools.recipes.rv_processing import csv_to_rdb
from jump_kpf_tools.recipes.downloader import download_rv_csvs, download_from_csv
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

    # ---- RV CSV downloader command ----
    rvdl_parser = subparsers.add_parser(
        "download_rv",
        help="Download *_rv.csv files for configured stars"
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
        default=None,
        help="cookies.txt file (if RV endpoint requires auth)"
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
        "conv_kima",
        help="Convert *_rv.csv files into kima-compatible .rdb files"
    )
    rv_parser.add_argument(
        "--csv-dir",
        default=str(DEFAULT_CSV_DIR),
        help="Directory with *_rv.csv files"
    )
    rv_parser.add_argument(
        "--kima-output-dir",
        default=str(DEFAULT_KIMA_OUTPUT_DIR),
        help="Output directory for .rdb files"
    )
    rv_parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output"
    )

    # ---- FITS downloader command ----
    dl_parser = subparsers.add_parser(
        "download_L2",
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
        help="cookies.txt file exported from browser"
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
        "check_KWs",
        help="Extract and check FITS header keywords; create/move Md tables and .csv"
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
        "--repeatdownload",
        action="store_true",
        help="Move outdated FITS to oldversions/, redownload; rename old _rv.csv files"
    )
    kw_parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output"
    )

    args = parser.parse_args()

    # ---- Dispatch ----
    if args.command == "download-rv":
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
            repeatdownload=args.repeatdownload,
            verbose=not args.quiet
        )


if __name__ == "__main__":
    main()
