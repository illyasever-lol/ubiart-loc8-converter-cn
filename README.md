**26/1/25**

**增加启动器，只要下载loc8Convertertc3.py及loc8转换工具启动器.py到同一目录下，运行loc8转换工具启动器.py即可**

1、启动器启动界面，可选择loc8转换为json或json转换为loc8

![启动界面](https://github.com/illyasever-lol/ubiart-loc8-converter-cn/blob/main/images/%E5%B7%A5%E5%85%B7%E7%AE%B1%E7%95%8C%E9%9D%A2.jpg)

2、增加json文件判定，如果有错误的位置会进行提示，便于修复

![错误提示](https://github.com/illyasever-lol/ubiart-loc8-converter-cn/blob/main/images/%E9%94%99%E8%AF%AF%E6%8F%90%E7%A4%BA.jpg)

3、增加多语种支持，可支持全部13语种互相转换，转换结束前选择对应语种即可

![语种选项截图](https://github.com/user-attachments/assets/d21add74-50c2-47c9-9cd7-cadae4c959d3)#


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
