from pathlib import Path
import pandas as pd


def csv_to_rdb(input_dir, output_dir, verbose=True):

    input_dir = Path(input_dir)
    if not input_dir.exists():
        raise FileNotFoundError(f"CSV input directory does not exist: {input_dir}")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_files = input_dir.glob("*_rv.csv")

    for csv_file in csv_files:
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

        required_cols = {"bjd", "mnvel", "errvel", "kpfera"}
        if not required_cols.issubset(df.columns):
            if verbose:
                print(f"Skipping {csv_file}: missing required columns")
            continue

        star_name = csv_file.stem.replace("_rv", "")

        # Ensure kpfera numeric
        df["kpfera"] = pd.to_numeric(df["kpfera"], errors="coerce")
        df = df.dropna(subset=["kpfera"])

        for kpfera_value, group in df.groupby("kpfera"):

            # Format era as 1 decimal float
            era_float = float(kpfera_value)
            era_str = f"{era_float:.1f}".replace(".", "p")

            # Transform data
            rjd = group["bjd"] - 2400000.0
            vrad = group["mnvel"] - group["mnvel"].mean()
            svrad = group["errvel"]

            out_df = pd.DataFrame({
                "rjd": rjd,
                "vrad": vrad,
                "svrad": svrad
            })

            out_file = output_dir / f"{star_name}_KPF{era_str}.rdb"

            with open(out_file, "w") as f:
                f.write("rjd\tvrad\tsvrad\n")
                f.write("---\t----\t-----\n")
                out_df.to_csv(
                    f,
                    sep="\t",
                    index=False,
                    header=False,
                    float_format="%.8f"
                )

            if verbose:
                print(f"Written: {out_file}")

