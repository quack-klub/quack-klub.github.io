#! /usr/bin/env python3

from ast import TypeAlias
import os
import sys
from pathlib import Path
import re
from typing import NewType
from bs4 import BeautifulSoup
from requests import get, Response

FILE_BASE_PATH: Path = Path("./templates")
FONT_OUTPUT_PATH: Path = Path("./static/fonts/MaterialSymbols/Symbols-Outlined.woff2")
SYMBOL_EXTRAS: set[str] = {"open_in_new"}
CSS_REGEX: re.Pattern[str] = re.compile(r"""src: url\((.+)\) format\(['"](.+)['"]\)""")

CollectException = NewType("CollectException", str)


def get_files(*, base: Path = FILE_BASE_PATH) -> list[Path]:
    return [
        Path(cur, f) for cur, _, fs in os.walk(base) for f in fs if f.endswith(".html")
    ]


def find_symbols(paths: list[Path], /) -> set[str]:
    symbols: set[str] = set()

    for p in paths:
        with open(p, "r") as f:
            soup = BeautifulSoup(f.read(), features="html.parser")

        symbols.update(map(lambda r: r.text, soup.find_all(class_="symbol")))

    return symbols


def fetch_font(
    symbols: set[str], /, *, out: Path = FONT_OUTPUT_PATH
) -> None | CollectException:
    symbols_sorted = sorted(list(symbols))

    fetch_url: str = f"https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined&icon_names={','.join(symbols_sorted)}&display=block"
    response: Response = get(
        fetch_url,
        headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "User-Agent": "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116",
        },
    )

    match: re.Match[str] | None = re.search(CSS_REGEX, response.text)
    if match == None:
        return CollectException("No match found in the CSS")

    url: str = match.group(1)

    if (format := match.group(2)) != out.suffix[1::]:
        return CollectException(f"Font is format {format}, expected {out.suffix[1::]}")

    font_file: Response = get(url)
    with open(out, "wb") as f:
        f.write(font_file.content)

    return None


def main() -> None:
    symbols: set[str] = find_symbols(get_files())
    symbols |= SYMBOL_EXTRAS

    if err := fetch_font(symbols):
        sys.stderr.write(err)
        sys.stderr.write(os.linesep)
        sys.stderr.flush()
        sys.exit(1)


if __name__ == "__main__":
    main()
