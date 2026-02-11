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

# How to use

After installation:

```bash
jump-kpf-tools --help
```

The CLI provides the following workflow-oriented commands.

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

## 3️⃣ Convert RVs for kima

Convert `*_rv.csv` files into kima-compatible `.rdb` files:

```bash
jump-kpf-tools conv-kima
```

Output files are written to the configured kima output directory.

---

## 4️⃣ Download L2 FITS files

Download L2 FITS files listed in the `observation_id` column of the CSVs:

```bash
jump-kpf-tools download-L2
```

Force redownload:

```bash
jump-kpf-tools download-L2 --overwrite
```

---

## 5️⃣ Check FITS keywords

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
    alltargets_rerun.txt
```

* `complete/` → full keyword tables
* `diff/` → only varying keywords
* `rerun/` → observations with outdated DRPHASH

---

## 6️⃣ Re-download outdated L2 FITS

Move outdated FITS into `oldversions/` and download fresh versions:

```bash
jump-kpf-tools redownload-L2
```

This will:

* Move outdated FITS to `STAR/oldversions/`
* Download fresh L2 files
* Rename outdated `*_rv.csv`
* Rename rerun summary files

After running this command, re-run:

```bash
jump-kpf-tools check-KWs
```

to confirm consistency.

---

## Typical Workflow

```bash
jump-kpf-tools auth-check
jump-kpf-tools download-rv
jump-kpf-tools download-L2
jump-kpf-tools check-KWs
jump-kpf-tools redownload-L2
jump-kpf-tools check-KWs
jump-kpf-tools conv-kima
```

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
