#!/usr/bin/python3 -i
import os
def pwd():
    return os.getcwd()
def mkdir(dirname):
    os.mkdir(dirname)
def cd(dirname = '.'):
    os.chdir(dirname)
def ls(dirname = '.', recursive = False, dirs = True, files = True):
    result = []
    for item in os.listdir(dirname):
        item = os.path.join(dirname, item)
        if os.path.isdir(item):
            if recursive:
                result.extend(ls(item, recursive, dirs, files))
            if dirs:
                result.append(item)
        else:
            if files:
                result.append(item)
    return result
def mkfile(filename, content = b'', append = False):
    mode = 'a' if append else 'w'
    if isinstance(content, bytes):
        mode += 'b'
    with open(filename, mode) as f:
        f.write(content)
def cat(filename, binary = True):
    mode = 'r'
    if binary:
        mode += 'b'
    with open(filename, mode) as f:
        return f.read()
def mv(src, dest):
    os.rename(src, dest)
def cp(src, dest):
    if os.path.isdir(src):
        mkdir(dest)
        for item in os.listdir(src):
            cp(os.path.join(src, item), os.path.join(dest, item))
    else:
        with open(src, 'rb') as i, open(dest, 'wb') as o:
            o.write(i.read())
def rm(path):
    if os.path.isdir(path):
        for item in os.listdir(path):
            rm(os.path.join(path, item))
        os.rmdir(path)
    else:
        os.remove(path)
