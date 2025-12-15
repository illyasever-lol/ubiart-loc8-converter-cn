#
**25/12/15增加简中loc8文件适配。loc8Convertersc=转换简中localisation.itf_language_simplifiedchinese.loc8**

# ubiart-loc8-converter
UbiArt 本地化文件转换器，可让您轻松解压缩、压缩和修补 loc8 文件。

## 用途？

`.loc8` 文件用于 UbiArt Framework 游戏中的本地化。此脚本可让您轻松提取或修改这些文件。多年来，我一直使用它来为《舞力全开》（Just Dance）制作模组。

## 支持的游戏

- 所有平台上的《舞力全开》2015 - 2022（可能也支持《舞力全开》2014，但我没有测试过）

- 《雷曼：传奇》（Rayman Legends）

- 《雷曼：起源》（Rayman Origins）

- ……几乎所有其他 UbiArt 游戏

## 使用方法

此脚本不依赖任何外部模块。您只需要 Python 3 或更高版本。

但是，单独使用此脚本时需要传递参数：

```

py loc8Converter.py <mode> <input> <output>

Modes:
-d --decompress     解密 the loc8 file as JSON
-c --compress       将JSON文件转换回 loc8
-p --patch          将json进行对比，将修改文件进行合并

例子:
py loc8Converter.py -d localisation.loc8 localisation.json
```


Step-by-step usage tutorial:
1. Download `loc8Converter.py`
2. Copy it to any desired work directory
3. Run it by opening command prompt or terminal in directory and running `py loc8Converter.py` with parameters listed above

You can also use this script as a module (like I usually do).
