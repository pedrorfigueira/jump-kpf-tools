from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def plot_rv(csv_dir, plot_dir, verbose=True):

    csv_dir = Path(csv_dir)
    plot_dir = Path(plot_dir)
    plot_dir.mkdir(parents=True, exist_ok=True)

    csv_files = csv_dir.glob("*_rv.csv")
    markers = ["o", "s", "D", "^", "v", ">", "<", "P", "X"]

    for csv_file in csv_files:
        star = csv_file.stem.replace("_rv", "")

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

        required = {"bjd", "mnvel", "errvel", "kpfera"}
        if not required.issubset(df.columns):
            if verbose:
                print(f"Skipping {star}: missing required columns")
            continue

        df = df.dropna(subset=["bjd", "mnvel", "errvel", "kpfera"])
        df["kpfera"] = pd.to_numeric(df["kpfera"], errors="coerce")
        df = df.dropna(subset=["kpfera"])

        if df.empty:
            continue

        # ---- Global statistics ----
        rms = np.sqrt(np.mean((df["mnvel"] - df["mnvel"].mean())**2))
        median_err = np.median(df["errvel"])
        ratio = rms / median_err if median_err > 0 else np.nan

        stats_text = (
            f"RMS = {rms:.2f} m/s\n"
            f"Median σ = {median_err:.2f} m/s\n"
            f"RMS/σ = {ratio:.2f}"
        )

        out_file = plot_dir / f"{star}.pdf"

        with PdfPages(out_file) as pdf:

            # =====================================================
            # PAGE 1 — Absolute RV
            # =====================================================

            fig1, ax1 = plt.subplots()

            for i, (era, group) in enumerate(
                sorted(df.groupby("kpfera"), key=lambda x: x[0])
            ):
                marker = markers[i % len(markers)]
                era_float = float(era)

                ax1.errorbar(
                    group["bjd"],
                    group["mnvel"],
                    yerr=group["errvel"],
                    fmt=marker,
                    linestyle="none",
                    label=f"KPF {era_float:.1f}"
                )

            ax1.set_xlabel("BJD")
            ax1.set_ylabel("RV [m/s]")
            ax1.set_title(star)
            ax1.legend(loc="best")

            # Stats box — let matplotlib place optimally
            ax1.text(
                0.98,
                0.02,
                stats_text,
                transform=ax1.transAxes,
                ha="right",
                va="bottom",
                bbox=dict(boxstyle="round", alpha=0.2)
            )

            fig1.tight_layout()
            pdf.savefig(fig1)
            plt.close(fig1)

            # =====================================================
            # PAGE 2 — Per-era centered RV (outliers removed)
            # =====================================================

            fig2, ax2 = plt.subplots()

            all_clean_residuals = []
            median_err = np.median(df["errvel"])

            for i, (era, group) in enumerate(
                    sorted(df.groupby("kpfera"), key=lambda x: x[0])
            ):
                marker = markers[i % len(markers)]
                era_float = float(era)

                # ---- Center per era ----
                delta_rv = group["mnvel"] - group["mnvel"].mean()

                # ---- Internal scatter per era ----
                sigma_era = np.std(delta_rv, ddof=1)

                if sigma_era > 0:
                    outliers = np.abs(delta_rv) > 4 * sigma_era
                    n_out = np.sum(outliers)
                else:
                    outliers = np.zeros_like(delta_rv, dtype=bool)
                    n_out = 0

                # ---- Cleaned residuals for global internal RMS ----
                clean_residuals = delta_rv[~outliers]
                all_clean_residuals.append(clean_residuals.values)

                # ---- Legend label ----
                if n_out > 0:
                    label = f"KPF {era_float:.1f} ({n_out} 4σ outliers)"
                else:
                    label = f"KPF {era_float:.1f}"

                # ---- Plot ALL points (including outliers visually) ----
                ax2.errorbar(
                    group["bjd"],
                    delta_rv,
                    yerr=group["errvel"],
                    fmt=marker,
                    linestyle="none",
                    label=label
                )

            # ---- Global internal scatter AFTER per-era centering and outlier removal ----
            if all_clean_residuals:
                all_clean_residuals = np.concatenate(all_clean_residuals)
                if len(all_clean_residuals) > 1:
                    rms_centered = np.std(all_clean_residuals, ddof=1)
                else:
                    rms_centered = np.nan
            else:
                rms_centered = np.nan

            ratio_centered = (
                rms_centered / median_err
                if median_err > 0 and not np.isnan(rms_centered)
                else np.nan
            )

            stats_text_centered = (
                f"Internal RMS = {rms_centered:.2f} m/s\n"
                f"Median σ = {median_err:.2f} m/s\n"
                f"RMS/σ = {ratio_centered:.2f}"
            )

            ax2.set_xlabel("BJD")
            ax2.set_ylabel("DeltaRV (within era)")
            ax2.set_title(f"{star} (per-era centered)")
            ax2.legend(loc="best")

            # ---- Stats box (lower right as requested) ----
            ax2.text(
                0.98,
                0.02,
                stats_text_centered,
                transform=ax2.transAxes,
                ha="right",
                va="bottom",
                bbox=dict(boxstyle="round", alpha=0.2)
            )

            fig2.tight_layout()
            pdf.savefig(fig2)
            plt.close(fig2)

        if verbose:
            print(f"✓ Plot written: {out_file}")
