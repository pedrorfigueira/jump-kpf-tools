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
