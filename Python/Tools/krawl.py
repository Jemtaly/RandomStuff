#!/usr/bin/python3
from urllib.parse import urljoin, unquote, urlparse, parse_qs
import requests, os, bs4, re
import argparse
warn = '\033[31m!!\033[0m'
info = '\033[32m>>\033[0m'
def krawl(url, exclude, include, dir = None):
    if dir is None:
        dir = url.split('/')[-1]
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text, 'html.parser')
    if not os.path.exists(dir):
        os.mkdir(dir)
    href_set = set()
    for div in soup.find_all('div', class_ = 'post__thumbnail') + soup.find_all('li', class_ = 'post__attachment'):
        href_set.add(urljoin(url, div.a.get('href')))
    for href in href_set:
        name = unquote(parse_qs(urlparse(href).query)['f'][0])
        if exclude.fullmatch(name) or not include.fullmatch(name):
            continue
        path = os.path.join(dir, name)
        if os.path.exists(path):
            print('\033[31m>>\033[0m Skipping {} because {} already exists'.format(href, path))
        else:
            print('\033[32m>>\033[0m Downloading {} to {}'.format(href, path))
            part = path + '.part'
            with open(part, 'wb') as f:
                f.write(requests.get(href).content)
            os.rename(part, path)
def index(url):
    dir = url.split('/')[-1]
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text, 'html.parser')
    if not os.path.exists(dir):
        os.mkdir(dir)
    for i, div in enumerate(soup.find_all('div', class_ = 'post__thumbnail')):
        href = urljoin(url, div.a.get('href'))
        oldn = unquote(parse_qs(urlparse(href).query)['f'][0])
        name = '{:02}{}'.format(i, os.path.splitext(oldn)[1])
        oldp = os.path.join(dir, oldn)
        path = os.path.join(dir, name)
        if os.path.exists(path):
            print('\033[31m>>\033[0m Skipping {} because {} already exists'.format(href, path))
        elif os.path.exists(oldp):
            print('\033[32m>>\033[0m Renaming {} to {}'.format(oldp, path))
            os.rename(oldp, path)
        else:
            print('\033[32m>>\033[0m Downloading {} to {}'.format(href, path))
            part = path + '.part'
            with open(part, 'wb') as f:
                f.write(requests.get(href).content)
            os.rename(part, path)
def main():
    parser = argparse.ArgumentParser(description = 'Kemono.party post attachment crawler')
    parser.add_argument('url', type = str, nargs = '*', help = 'URL of the post')
    parser.add_argument('-d', '--dir', type = str, help = 'directory to save the files to')
    parser.add_argument('-e', '--exclude', type = re.compile, default = re.compile('.^'), help = 'exclude files matching this regex')
    parser.add_argument('-i', '--include', type = re.compile, default = re.compile('.*'), help = 'include files matching this regex')
    parser.add_argument('-r', '--rename', action = 'store_true', help = 'rename the files')
    args = parser.parse_args()
    for url in args.url:
        krawl(url, args.exclude, args.include, args.dir) if not args.rename else index(url)
if __name__ == '__main__':
    main()
