# DeNCM

一个网易云音乐 NCM 格式文件解密工具，支持批量解密。

## 依赖

- Python 3.6+
- pycryptodome

## 使用

```
usage: dencm.py [ncm_path ...]

  ncm_path    NCM 文件路径（如果省略，则查找并解密当前目录下的所有 NCM 文件）
```

解密后的文件会保存在当前目录下专辑名对应的文件夹中，文件以曲名命名。专辑封面将保存在专辑目录下的 `cover.jpg` 中。

示例：

``` bash
$ dencm.py "SEKAI NO OWARI - *.ncm" "End of the World - *.ncm"
# 解密当前目录下所有 SEKAI NO OWARI 和 End of the World 的歌曲

$ dencm.py
# 解密当前目录下所有 NCM 文件
```

## NCM 文件格式及解密原理说明

| 长度 | 内容 | 说明 |
| --- | --- | --- |
| 8 | Magic Number | 文件头，固定为 `CTENFDAM` |
| 2 | Version | 文件版本，略 |
| 4 | Key Length | 密钥信息长度 |
| Key Length | Key | 被加密的密钥信息[^1] |
| 4 | Meta Length | 元数据长度 |
| Meta Length | Meta Info | 被加密的元数据[^2] |
| 4 | Image Length | 图片数据长度 |
| Image Length | Image | 图片数据 |
| - | Music Data | 被加密的音乐数据[^3] |

[^1]: 密钥信息经过 AES-128-ECB 加密及异或处理，解密时先将该部分数据逐字节异或 `0x64`，再使用密钥 `0x687A4852416D736F356B496E62617857` 进行 AES-128-ECB 解密及去填充操作。最后去除解密后的数据开头的 17 字节（内容为 `neteasecloudmusic`）即可得到真正的密钥。

[^2]: 元数据经过 AES-128-ECB 加密，Base64 编码及异或处理，解密时，先将该部分数据逐字节异或 `0x63`，得到字节串，格式为 `163 Key(Don't modify):` + 使用 Base64 编码的密钥，解码后使用密钥 `0x2331346C6A6B5F215C5D2630553C2728` 进行 AES-128-ECB 解密及去填充，得到格式为 `music:` + JSON 格式的元数据，解析后可得到乐曲信息（如歌曲名、歌手名、专辑名、乐曲格式等）。

[^3]: 音乐数据使用某种 RC4 变种算法加密，具体解密流程如下：

    ```python
    n = len(k) # k 为前面解密得到的密钥
    S = bytearray(range(256))
    c = 0
    for i in range(256):
        swap = S[i]
        c = c + swap + k[i % n] & 0xff
        S[i] = S[c]
        S[c] = swap
    # 以上的初始化过程与标准 RC4 算法相同，后续的加解密过程经过简化，密钥流变成了一个循环的字节串，循环长度为 256
    K = bytes(S[S[i] + S[S[i] + i & 0xff] & 0xff] for i in range(256))
    i = 0
    while True:
        chunk = ncm_file.read(0x10000)
        mp3_file.write(bytes(a ^ K[i := i + 1 & 0xff] for a in chunk))
        if len(chunk) < 0x10000:
            break
    ```
