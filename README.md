# dl_gh

Download GitHub releases via the API.

## Minimum Requirements

* [Python 3.11+](https://www.python.org/downloads/)

## Development Requirements

* [devbox](https://www.jetify.com/devbox/docs/quickstart/)

## Installation

```bash
git clone https://github.com/pythoninthegrass/dl_gh.git
cd dl_gh
python -m pip install -r requirements.txt
ln -s $(pwd)/dl_gh.py ~/.local/bin/dl-gh
```

## Usage

```bash
dl-gh -u <owner> -r <repo> -t <extension type>
```

## Example

```bash
dl-gh -u MusicDin -r kubitect -t tar.gz
```

## Development

```bash
pytest
```
