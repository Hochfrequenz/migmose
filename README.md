![migmose-logo](migmose-logo.jpeg)

# MIG_mose

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python Versions (officially) supported](https://img.shields.io/pypi/pyversions/migmose.svg)
![Pypi status badge](https://img.shields.io/pypi/v/migmose)
![Unittests status badge](https://github.com/Hochfrequenz/migmose/workflows/Unittests/badge.svg)
![Coverage status badge](https://github.com/Hochfrequenz/migmose/workflows/Coverage/badge.svg)
![Linting status badge](https://github.com/Hochfrequenz/migmose/workflows/Linting/badge.svg)
![Black status badge](https://github.com/Hochfrequenz/migmose/workflows/Formatting/badge.svg)

MIG_mose generates machine-readable files from MIG `.docx` documents ([edi-energy](https://www.edi-energy.de/index.php?id=38)).
MIG_mose is the sister of [kohlrahbi](https://github.com/Hochfrequenz/kohlrahbi).

If you're looking for a tool to process the **official** BDEW XMLs for MIGs (available since 2024), checkout [fundamend](https://github.com/Hochfrequenz/xml-fundamend-python).

## Tech-Stack
- MIG_mose is a Python(3.11,3.12) project.
- .docx files a processed by the [python-docx](https://python-docx.readthedocs.io/en/latest/) library.
- EdiFact formats are used as in [efoli](https://github.com/Hochfrequenz/efoli)).
- syrupy for unittest snapshots

## Installation
MIG_mose is a Python-based tool.
Therefore, you have to make sure, that Python is running on your machine.

We recommend using virtual environments to keep your system clean.

Create a new virtual environment with
```bash
python -m venv .venv
```

The activation of the virtual environment depends on your used OS.

**Windows**
```
.venv\Scripts\activate
```
**MacOS/Linux**
```
source .venv/bin/activate
```
Finally, install the package with

```bash
pip install migmose
```

## Features And How To Use Them

At this point, MIG_mose works as a command-line interface tool (CLI).
There are several flags available to provide a user-friendly way to interact with MIG_mose.
Below the available options are listed:

- **Input Directory (`-eemp`, `--edi-energy-mirror-path`):**
    - Description: This option allows the user to specify the path to a edi-energy-mirror-like repository which contains .docx files for the MIGs (Message Implementation Guides) in subdirectories structured by the format version.
    - Example: `--edi-energy-mirror-path /path/to/edi_energy_mirror`

- **Message Format (`-mf`, `--message-format`):**
    - Description: This option defines the set of message formats to be parsed. Users can specify multiple message formats by providing multiple values. The formats are EdiFact formats (cf. [efoli.EdifactFormat](https://github.com/Hochfrequenz/efoli/blob/src/efoli/edifact_format.py)). If no format is specified, all formats are parsed.
    - Example: `--message_format "UTILMD" --message_format "ORDCHG"`

- **Output Directory (`-o`, `--output-dir`):**
    - Description: This option allows the user to specify the path to the directory which should contain the output files generated by the tool. If the directory does not exist, it will be created automatically.
    - Example: `--output_dir /path/to/output_directory`
- **Output File Type (`-ft`, `--file-type`):**
    - Description: Defines the output format. Choose between (Default is `csv`):
      - `csv` for flat Nachrichtenstruktur tables
      - `nested_json` for json files of the nested Nachrichtenstruktur tables
      - `reduced_nested_json` for a reduced nested Nachrichtenstruktur
      - `sgh_json` for segmentgrouphierarchy files (cf. [MAUS sgh](https://github.com/Hochfrequenz/edifact-templates/tree/b024e3671deae9aec7e8ea29e74fa48257f6ccfe/segment_group_hierarchies))
      - `tree` for .tree files (cf. [MAUS tree](https://github.com/Hochfrequenz/mig_ahb_utility_stack/blob/5cce94069ead5aa63d4b9ac7f5e0fcec0bf608ea/src/maus/reader/tree_to_sgh.py))
    - Example: `--file-type "csv"
- **Format Version (`-fv`, `--format-version`):**
    - Description: Defines the format version.
    - Example: `--format-version "FV2310"

### Usage Example

To use the CLI logic provided by this tool, follow the command syntax below:

```bash
migmose -eemp /path/to/edi_energy_mirror -o /path/to/output_directory -mf "UTILMD" -mf "ORDCHG" -ft "csv" -fv "FV2310"
```

## Development

### Setup

To set up the development environment, you have to install the dev dependencies.

```bash
tox -e dev
```

### Run all tests and linters

To run the tests, you can use tox.

```bash
tox
```
To update the test snapshots run
```bash
tox -e update_snapshots
```
See our [Python Template Repository](https://github.com/Hochfrequenz/python_template_repository#how-to-use-this-repository-on-your-machine) for detailed explanations.

## Contribute

You are very welcome to contribute to this template repository by opening a pull request against the main branch.

## Related Tools and Context

This repository is part of the [Hochfrequenz Libraries and Tools for a truly digitized market communication](https://github.com/Hochfrequenz/digital_market_communication/).
