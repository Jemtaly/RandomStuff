#!/usr/bin/env python3

import argparse
import os
import re
import time
from urllib.parse import parse_qs, unquote, urljoin, urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

import bs4
import requests
from tqdm import tqdm


def download(url: str, path: str, chunk_size: int = 1024, retry: int = 3) -> bool:
    for attempt in range(retry):
        try:
            resp = requests.get(url, stream=True)
            total = int(resp.headers.get("content-length", 0))
            with open(path, "wb") as file, tqdm(total=total) as bar:
                for data in resp.iter_content(chunk_size=chunk_size):
                    bar.update(file.write(data))
            return True
        except Exception as e:
            print(f"{WARN} Download failed (attempt {attempt + 1}/{retry}): {e}")
    return False


WARN = "\033[31m!!\033[0m"
INFO = "\033[32m>>\033[0m"


def get_rendered_html(url: str) -> str:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--enable-unsafe-swiftshader")
    service = Service()
    with webdriver.Chrome(service=service, options=options) as driver:
        driver.get(url)
        time.sleep(5.0)
        return driver.page_source


def crawl_by_name(url: str, *, exclude: re.Pattern, include: re.Pattern, dir: str | None = None, retry: int = 3) -> list[tuple[str, str]]:
    if dir is None:
        dir = url.split("/")[-1]
    html = get_rendered_html(url)
    soup = bs4.BeautifulSoup(html, "html.parser")
    if not os.path.exists(dir):
        os.mkdir(dir)
    href_set = set()
    for div in soup.find_all("div", class_="post__thumbnail"):
        href_set.add(urljoin(url, div.a.get("href")))
    for div in soup.find_all("li", class_="post__attachment"):
        href_set.add(urljoin(url, div.a.get("href")))
    failed = []
    for href in href_set:
        name = unquote(parse_qs(urlparse(href).query)["f"][0])
        if exclude.fullmatch(name) or not include.fullmatch(name):
            continue
        path = os.path.join(dir, name)
        if os.path.exists(path):
            print(f"{WARN} Skipping {href} because {path} already exists")
        else:
            print(f"{INFO} Downloading {href} to {path}")
            part = path + ".part"
            if download(href, part, retry=retry):
                os.rename(part, path)
            else:
                failed.append((path, href))
    return failed


def crawl_by_index(url: str, *, retry: int = 3) -> list[tuple[str, str]]:
    dir = url.split("/")[-1]
    html = get_rendered_html(url)
    soup = bs4.BeautifulSoup(html, "html.parser")
    if not os.path.exists(dir):
        os.mkdir(dir)
    failed = []
    for i, div in enumerate(soup.find_all("div", class_="post__thumbnail")):
        href = urljoin(url, div.a.get("href"))
        oldn = unquote(parse_qs(urlparse(href).query)["f"][0])
        extn = os.path.splitext(oldn)[1]
        name = f"{i:02}{extn}"
        oldp = os.path.join(dir, oldn)
        path = os.path.join(dir, name)
        if os.path.exists(oldp):
            print(f"{INFO} Renaming {href} to {path}")
            os.rename(oldp, path)
        elif os.path.exists(path):
            print(f"{WARN} Skipping {href} because {path} already exists")
        else:
            print(f"{INFO} Downloading {href} to {path}")
            part = path + ".part"
            if download(href, part, retry=retry):
                os.rename(part, path)
            else:
                failed.append((path, href))
    return failed


def main():
    parser = argparse.ArgumentParser(description="Kemono.party post attachment crawler")
    parser.add_argument("url", type=str, nargs="*", help="URL of the post")
    parser.add_argument("-d", "--dir", type=str, help="directory to save the files to")
    parser.add_argument("-e", "--exclude", type=re.compile, default=re.compile(".^"), help="exclude files matching this regex")
    parser.add_argument("-i", "--include", type=re.compile, default=re.compile(".*"), help="include files matching this regex")
    parser.add_argument("-n", "--num", action="store_true", help="rename the files")
    parser.add_argument("-r", "--retry", type=int, default=3, help="number of retries for downloading files")
    args = parser.parse_args()
    faileds = []
    for url in args.url:
        if args.num:
            failed = crawl_by_index(url, retry=args.retry)
            if failed:
                faileds.append((url, failed))
        else:
            failed = crawl_by_name(url, exclude=args.exclude, include=args.include, dir=args.dir, retry=args.retry)
            if failed:
                faileds.append((url, failed))
    if not faileds:
        print(f"{INFO} All downloads completed successfully")
    else:
        print(f"{WARN} Some downloads failed:")
        for url, failed in faileds:
            print(f"  From {url}:")
            for path, href in failed:
                print(f"    {href} -> {path}")

if __name__ == "__main__":
    main()
