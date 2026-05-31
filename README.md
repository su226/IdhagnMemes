# IdhagnMemes

从 [IdhagnBot](https://github.com/su226/IdhagnBot) 里分离出来的梗图，用于 [meme-generator](https://github.com/MemeCrafters/meme-generator) 加载。 

[--> 表情列表 <--](https://github.com/su226/IdhagnMemes/wiki/%E8%A1%A8%E6%83%85%E5%88%97%E8%A1%A8)

[--> 如何加载表情 <--](https://github.com/MemeCrafters/meme-generator/wiki/%E5%8A%A0%E8%BD%BD%E5%85%B6%E4%BB%96%E8%A1%A8%E6%83%85)

注意：IdhagnMemes 仓库结构特殊，在克隆或下载本仓库 ZIP 后，你会得到如下目录结构。

```
/path_to_clone_or_download_dir
├─/src
│ └─/idhagnmemes
│   ├─/addict
│   ├─/cxk
│   ├─/其他 meme 目录
│   ├─color.py
│   ├─image.py
│   ├─其他工具函数文件.py
│   └─__init__.py
└─README.md
```

你需要向 `meme_dirs` 里加入 `/path_to_clone_or_download_dir/src` 而非 `/path_to_clone_or_download_dir/src/idhagnmemes`。

IdhagnMemes 会将 `/path_to_clone_or_download_dir/src` 加入 [sys.path](https://docs.python.org/3/library/sys.html#sys.path)，这意味着该目录下的其他 Python 文件也可能被加载，可能会导致程序运行不正常甚至加载恶意代码，请尽量保持该目录下只有 `idhagnmemes` 子目录。

## 特别感谢

- [O'RLY? 生成器](https://orly.nanmu.me/) 的原作者 [nanmu42](https://github.com/nanmu42)。
- [One Last Image](https://lab.magiconch.com/one-last-image/)（“卢浮宫”梗图）的原作者 [itorr](https://github.com/itorr/)。
