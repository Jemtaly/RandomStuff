#!/usr/bin/env python3

import argparse
import re

import bs4
import requests
from tqdm import tqdm


def download(url: str, path: str, chunk_size: int = 1024):
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get("content-length", 0))
    with open(path, "wb") as file, tqdm(total=total) as bar:
        for data in resp.iter_content(chunk_size=chunk_size):
            bar.update(file.write(data))


def download_sg(url: str, fmt: str):
    response = requests.get(url)
    response.raise_for_status()
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    src = re.search(r'm4a: "(.*?)"', response.text).group(1)
    title = soup.select_one(".jp-title").text
    author = soup.select_one('div[style="margin:10px 0"] a').text
    title = re.sub(r'[\\/:*?"<>|]', "_", title)
    author = re.sub(r'[\\/:*?"<>|]', "_", author)
    base = fmt.format(author=author, title=title)
    if len(base) > 200:
        base = base[:200] + "..."
    path = base + ".m4a"
    download(src, path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", nargs="*", help="URL of the soundgasm page")
    parser.add_argument("-f", "--fmt", help="format of the file name (without extension)", default="{author} - {title}")
    args = parser.parse_args()
    for url in args.url:
        download_sg(url, args.fmt)


if __name__ == "__main__":
    main()
