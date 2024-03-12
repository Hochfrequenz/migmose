![migmose-logo](migmose-logo.jpeg)

# MIG_mose

![Unittests status badge](https://github.com/Hochfrequenz/migmose/workflows/Unittests/badge.svg)
![Coverage status badge](https://github.com/Hochfrequenz/migmose/workflows/Coverage/badge.svg)
![Linting status badge](https://github.com/Hochfrequenz/migmose/workflows/Linting/badge.svg)
![Black status badge](https://github.com/Hochfrequenz/migmose/workflows/Formatting/badge.svg)

MIG_mose generates machine-readable files from MIG documents.
MIG_mose is the sister of [kohlrahbi](https://github.com/Hochfrequenz/kohlrahbi).

## Installation
MIGmose is a Python based tool.
Therefore you have to make sure, that Python is running on your machine.

We recommend to use virtual environments to keep your system clean.

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
See our [Python Template Repository](https://github.com/Hochfrequenz/python_template_repository#how-to-use-this-repository-on-your-machine) for detailed explanations.

## Contribute

You are very welcome to contribute to this template repository by opening a pull request against the main branch.

## Related Tools and Context

This repository is part of the [Hochfrequenz Libraries and Tools for a truly digitized market communication](https://github.com/Hochfrequenz/digital_market_communication/).
