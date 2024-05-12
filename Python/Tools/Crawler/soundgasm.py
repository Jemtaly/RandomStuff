#!/usr/bin/python3
import argparse
import requests
import bs4
import re
def download(url, fmt):
    response = requests.get(url)
    response.raise_for_status()
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    src = re.search(r'm4a: "(.*?)"', response.text).group(1)
    title = soup.select_one('.jp-title').text
    author = soup.select_one('div[style="margin:10px 0"] a').text
    title = re.sub(r'[\\/:*?"<>|]', '_', title)
    author = re.sub(r'[\\/:*?"<>|]', '_', author)
    base = fmt.format(author = author, title = title)
    if len(base) > 200:
        base = base[:200] + '...'
    path = base + '.m4a'
    with open(path, 'wb') as file:
        file.write(requests.get(src).content)
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', nargs = '*', help = 'URL of the soundgasm page')
    parser.add_argument('-f', '--fmt', help = 'format of the file name (without extension)', default = '{author} - {title}')
    args = parser.parse_args()
    for url in args.url:
        download(url, args.fmt)
if __name__ == '__main__':
    main()
