# jump-kpf-tools
Set of command-line tools to use along [Jump](https://jump.caltech.edu/) to download and manipulate KPF spectrograph data.

Uses web cookies for authentication. Allows command line download of jump rvs and fits files, and quick comparison for KPF pipeline reprocessing.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/pedrorfigueira/jump-kpf-tools/blob/main/LICENSE)


## 📦 Installation

Using Python ≥ 3.10, and preferably a conda virtual environment, clone the repository and move to its local folder

```
git clone https://github.com/pedrorfigueira/jump-kpf-tools.git
cd jump-kpf-tools
```

and run

```
pip install .
```
To install in editable / developer mode use the flag `-e`; this enables live code editing without having to reinstall.

Here is the **updated and internally consistent** `# How to use` section reflecting:

* Moving of outdated FITS now handled by `check-KWs`
* `alltargets_rerun.csv` (not `.txt`)
* `redownload-L2` only performs re-download + renaming
* Addition of `plot-RV`
* Correct logical ordering

---

# How to use

After installation:

```bash
jump-kpf-tools --help
```

The CLI provides workflow-oriented commands for JUMP/KPF data handling.

---

## 1️⃣ Check authentication (recommended first step)

Verify that your exported JUMP cookies are valid:

```bash
jump-kpf-tools auth-check --cookies config/jump_cookies.txt
```

If authentication fails, re-export cookies from your browser.

---

## 2️⃣ Download RV CSV files

Download `*_rv.csv` files for stars defined in `configfile.py`:

```bash
jump-kpf-tools download-rv
```

Override the star list:

```bash
jump-kpf-tools download-rv --stars k2-155,toi-1346
```

Force overwrite:

```bash
jump-kpf-tools download-rv --overwrite
```

---

## 3️⃣ Download L2 FITS files

Download L2 FITS files listed in the `observation_id` column of the CSVs:

```bash
jump-kpf-tools download-L2
```

Force redownload:

```bash
jump-kpf-tools download-L2 --overwrite
```

---

## 4️⃣ Check FITS keywords

Extract header keywords and generate Markdown summaries:

```bash
jump-kpf-tools check-KWs
```

This creates:

```
processed_summary/
  complete/
  diff/
  rerun/
    TARGET_rerun.csv
    alltargets_rerun.csv
```

* `complete/` → full keyword tables
* `diff/` → only varying keywords
* `rerun/` → observations with outdated `DRPHASH`

If outdated files are detected:

* The corresponding L2 FITS files are moved into `STAR/oldversions/`
* `*_rerun.csv` files are generated listing affected observations

If no outdated files are found, no further action is required.

---

## 5️⃣ Re-download outdated L2 FITS

If outdated files were detected and the external DRP pipeline has been rerun, download fresh L2 products:

```bash
jump-kpf-tools redownload-L2
```

This will:

* Download updated L2 FITS for affected observations
* Rename outdated `*_rv.csv` files
* Rename rerun summary files for bookkeeping clarity

After running this command, re-run:

```bash
jump-kpf-tools check-KWs
```

to regenerate keyword summaries and verify consistency.

---

## 6️⃣ Convert RVs for kima

Convert `*_rv.csv` files into kima-compatible `.rdb` files:

```bash
jump-kpf-tools conv-kima
```

Output files are written to the configured kima output directory.
Filenames include floating KPF era identifiers (e.g., `STAR_KPF2p0.rdb`).

---

## 7️⃣ Plot RV time series

Generate PDF plots (two pages per star):

```bash
jump-kpf-tools plot-RV
```

Each PDF contains:

**Page 1** – Absolute RV

* Errorbar plot
* Per-era markers
* RMS, median uncertainty, RMS/σ box

**Page 2** – Per-era centered RV

* Mean-subtracted per era
* 4σ outlier identification (per era)
* Internal scatter computed after outlier removal
* Outlier counts indicated in legend

Plots are saved in the configured plot directory.

---

# Summary of Typical Workflow

```
auth-check
      ↓
download-rv
      ↓
download-L2
      ↓
check-KWs
      ↓
If outdated observations found:
      → (external DRP rerun)
      → redownload-L2
      → check-KWs
      → download-rv
      → plot-RV
Else:
      → plot-RV
      → conv-kima
```

This reflects the full operational logic of the pipeline.

---

If you'd like, I can now produce a compact visual workflow diagram version suitable for the README as well.

---

## 📚 Folder Structure

```
jump-kpf-tools/
├── README.md
├── LICENSE
├── .gitignore
├── pyproject.toml
│
└─── jump_kpf_tools/
    ├── __init__.py
    ├── app.py          
    │
    ├── config/
    │   ├── __init__.py
    │   └── config.py
    │
    └── recipes/
        ├── __init__.py
        ├── rv_processing.py
        ├── downloader.py
        ├── kws_utils.py
        └── extract_kws.py
```

`downloader.py` requires you to log into jump and save the cookies as a text file. For Firefox you can install an extension that **exports your cookies in Netscape `cookies.txt` format**, which is exactly what tools like `curl`, `wget` and the Python downloader expect.

A reliable one is:

### 🔹 **cookies.txt – Export cookies**

This extension lets you save cookies as a `.txt` file in **Netscape/standard format**, suitable for command-line tools. ([addons.mozilla.org][1])

➡ Install from Firefox Add-ons:
👉 [https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/) ([addons.mozilla.org][1])

Once installed, you:

1. Log in to the site in Firefox
2. Click the cookies.txt extension icon
3. Export cookies to a file (e.g., `cookies.txt`)
4. Use that file with your Python downloader or `curl`/`wget`

## 📄 License

This project is distributed under the MIT License.

## 🙌 Acknowledgements

Pedro Figueira acknowledges financial support from the Severo Ochoa grant CEX2021-001131-S funded by MCIN/AEI/10.13039/501100011033. Pedro Figueira is also funded by the European Union (ERC, THIRSTEE, 101164189). Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or the European Research Council. Neither the European Union nor the granting authority can be held responsible for them.

This project depends on several open-source scientific packages. We extend sincere thanks to the support communities for developing and maintaining the scientific Python ecosystem.
