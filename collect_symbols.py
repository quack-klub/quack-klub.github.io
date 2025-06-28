import os
from pathlib import Path
import re
from typing_extensions import Any
from bs4 import BeautifulSoup
from requests import get, Response

FILE_BASE_PATH: str = "./templates"
FONT_OUTPUT_PATH: str = "./static/fonts/MaterialSymbols/Symbols-Outlined.woff2"
SYMBOL_EXTRAS: list[str] = ["open_in_new"]


def get_files(base: str | Path = FILE_BASE_PATH) -> list[Path]:
    paths: list[Path] = []

    for cur, sub, fs in os.walk(base):
        for f in fs:
            if f.endswith(".html"):
                paths.append(Path(cur, f))

    return paths


def find_symbols(paths: list[Path]) -> set[str]:
    symbols: set[str] = set()

    for p in paths:
        with open(p, "r") as f:
            soup = BeautifulSoup(f.read(), features="html.parser")

        for res in soup.find_all(class_="symbol"):
            symbols.add(res.text)

    return symbols


def fetch_font(symbols: set[str], out: str | Path = FONT_OUTPUT_PATH) -> bool:
    symbols_sorted = sorted(list(symbols))

    fetch_url: str = f"https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined&icon_names={','.join(symbols_sorted)}&display=block"
    response: Response = get(
        fetch_url,
        headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "User-Agent": "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116",
        },
    )

    match: re.Match[str] | None = re.search(
        r"""src: url\((.+)\) format\(['"](.*)['"]\)""", response.text
    )
    if match == None:
        return False

    url: str = match.group(1)
    format: str = match.group(2)

    if format != "woff2":
        raise Exception("Font is not woff2")

    font_file: Response = get(url)
    with open(out, "wb") as f:
        f.write(font_file.content)

    return True


def main() -> None:
    symbols: set[str] = find_symbols(get_files())
    symbols.update(SYMBOL_EXTRAS)

    fetch_font(symbols)


if __name__ == "__main__":
    main()
