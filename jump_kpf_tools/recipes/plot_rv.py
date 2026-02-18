from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D

from collections import defaultdict

from jump_kpf_tools.config.configfile import MIN_RV_ERA_GENPLOT


def plot_rv_individual(csv_dir, plot_dir, verbose=True):

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

                # -----------------------------
                # Step 1: initial centering
                # -----------------------------
                delta_rv_initial = group["mnvel"] - group["mnvel"].mean()

                sigma_era = np.std(delta_rv_initial, ddof=1)

                if sigma_era > 0:
                    outliers = np.abs(delta_rv_initial) > 4 * sigma_era
                else:
                    outliers = np.zeros(len(group), dtype=bool)

                n_out = np.sum(outliers)

                # -----------------------------
                # Step 2: remove outliers
                # -----------------------------
                clean_group = group.loc[~outliers].copy()

                if len(clean_group) == 0:
                    continue

                # -----------------------------
                # Step 3: recompute mean WITHOUT outliers
                # -----------------------------
                clean_mean = clean_group["mnvel"].mean()
                clean_delta_rv = clean_group["mnvel"] - clean_mean

                # store for global RMS
                all_clean_residuals.append(clean_delta_rv.values)

                # -----------------------------
                # Legend label
                # -----------------------------
                if n_out > 0:
                    label = f"KPF {era_float:.1f} ({n_out} 4σ outliers)"
                else:
                    label = f"KPF {era_float:.1f}"

                # -----------------------------
                # Plot ONLY clean points
                # -----------------------------
                ax2.errorbar(
                    clean_group["bjd"],
                    clean_delta_rv,
                    yerr=clean_group["errvel"],
                    fmt=marker,
                    linestyle="none",
                    label=label
                )

            # -----------------------------
            # Global internal RMS
            # -----------------------------
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

            # Lower right stats box
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


def plot_rv_global(csv_dir, plot_dir, verbose=True):

    csv_dir = Path(csv_dir)
    plot_dir = Path(plot_dir)
    plot_dir.mkdir(parents=True, exist_ok=True)

    csv_files = list(csv_dir.glob("*_rv.csv"))
    if not csv_files:
        return

    markers = ["o", "s", "D", "^", "v", ">", "<", "P", "X"]

    # distinct colors per star
    cmap = plt.get_cmap("tab10")

    era_residuals = defaultdict(list)
    total_residuals = []
    included_stars = {}

    fig, ax = plt.subplots()

    for star_idx, csv_file in enumerate(csv_files):

        star = csv_file.stem.replace("_rv", "")
        color = cmap(star_idx % 10)

        try:
            df = pd.read_csv(
                csv_file,
                comment="#",
                skip_blank_lines=True
            )
        except Exception:
            continue

        required = {"bjd", "mnvel", "errvel", "kpfera"}
        if not required.issubset(df.columns):
            continue

        df = df.dropna(subset=["bjd", "mnvel", "errvel", "kpfera"])
        df["kpfera"] = pd.to_numeric(df["kpfera"], errors="coerce")
        df = df.dropna(subset=["kpfera"])

        for era_idx, (era, group) in enumerate(
                sorted(df.groupby("kpfera"), key=lambda x: x[0])
        ):


            # ---- Outlier rejection (same logic as page 2) ----
            delta_initial = group["mnvel"] - group["mnvel"].mean()
            sigma_era = np.std(delta_initial, ddof=1)

            if sigma_era > 0:
                mask = np.abs(delta_initial) <= 4 * sigma_era
            else:
                mask = np.ones(len(group), dtype=bool)

            clean_group = group.loc[mask]

            if len(group) < MIN_RV_ERA_GENPLOT:
                continue

            clean_mean = clean_group["mnvel"].mean()
            residuals = clean_group["mnvel"] - clean_mean

            # store stats
            era_residuals[era].extend(residuals.values)
            total_residuals.extend(residuals.values)

            marker = markers[era_idx % len(markers)]

            ax.errorbar(
                clean_group["bjd"],
                residuals,
                yerr=clean_group["errvel"],
                fmt=marker,
                linestyle="none",
                color=color,
                label=f"{star} – KPF {float(era):.1f}"
            )

            included_stars[star] = color

    if not total_residuals:
        if verbose:
            print("No data passed filtering criteria.")
        return

    # -----------------------------
    # Label
    # -----------------------------

    unique_eras = sorted(era_residuals.keys())

    era_handles = []
    for i, era in enumerate(unique_eras):
        marker = markers[i % len(markers)]

        handle = Line2D(
            [0], [0],
            marker=marker,
            linestyle="none",
            markerfacecolor="none",
            markeredgecolor="grey",
            markeredgewidth=1.2,
            markersize=8,
            label=f"KPF {float(era):.1f}"
        )
        era_handles.append(handle)

    star_handles = []

    for star, color in included_stars.items():
        handle = Line2D(
            [0], [0],
            marker="o",
            linestyle="none",
            markerfacecolor=color,
            markeredgecolor=color,
            markersize=8,
            label=star
        )
        star_handles.append(handle)

    # Era legend (first row)
    legend1 = ax.legend(
        handles=era_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        ncol=len(era_handles),
        frameon=False
    )

    # Star legend (second row)
    legend2 = ax.legend(
        handles=star_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.22),
        ncol=min(len(star_handles), 5),
        frameon=False
    )

    ax.add_artist(legend1)

    # -----------------------------
    # Compute statistics
    # -----------------------------

    stats_lines = []

    for era in sorted(era_residuals.keys()):
        vals = np.array(era_residuals[era])
        if len(vals) > 1:
            scatter = np.std(vals, ddof=1)
            stats_lines.append(f"KPF {float(era):.1f}: {scatter:.2f} m/s")

    total_scatter = np.std(np.array(total_residuals), ddof=1)

    stats_text = "\n".join(stats_lines)
    stats_text += f"\nTotal: {total_scatter:.2f} m/s"

    # -----------------------------
    # Plot formatting
    # -----------------------------

    ax.set_xlabel("BJD")
    ax.set_ylabel("DeltaRV (within era)")
    ax.set_title("Global RV comparison")

    ax.text(
        0.98,
        0.02,
        stats_text,
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        bbox=dict(boxstyle="round", alpha=0.2)
    )

    fig.subplots_adjust(bottom=0.30)
    fig.tight_layout()

    out_file = plot_dir / "global_RV.pdf"
    fig.savefig(out_file)
    plt.close(fig)

    if verbose:
        print(f"✓ Global plot written: {out_file}")


def plot_rv(csv_dir, plot_dir, verbose=True):
    """
    High-level plotting entry point:
    - Generates per-star RV plots
    - Generates combined global RV plot
    """

    plot_rv_individual(csv_dir, plot_dir, verbose=verbose)
    plot_rv_global(csv_dir, plot_dir, verbose=verbose)