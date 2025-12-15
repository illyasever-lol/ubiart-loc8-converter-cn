#
# https://github.com/wukko/ubiart-loc8-converter
#
# UbiArt localisation file converter by https://github.com/wukko
# Tested on Just Dance 2015 - 2022 games on PC, Wii, Wii U, Nintendo Switch (NX).
# This script should work for Rayman Legends/Origins and other UbiArt games too.
#
# This script requires passing parameters when used standalone. 
#
# Usage:
# py loc8Converter.py <mode> <input> <output>
#
# Modes:
# -d --decompress     Decompresses the loc8 file as JSON
# -c --compress       Compresses the file back to loc8 from JSON
# -p --patch          Patches the output JSON file with values in input JSON file
# 
# Credit to me (https://github.com/wukko) is required when this script is used in other projects.

import json

def decompress(input, output):
    with open(input, "rb") as f:
        j = {}
        f.seek(8)
        i = 0
        amountOfStrings = int.from_bytes(f.read(4), "big")
        while i != amountOfStrings:
            id = int.from_bytes(f.read(4), "big")
            j[id] = f.read(int.from_bytes(f.read(4), "big")).decode("utf-8").replace("\x0A", "\n")
            i += 1

        with open(output, "w", encoding="utf-8") as f2:
            json.dump(j, f2, ensure_ascii=False, indent=4, sort_keys=True)

def compress(input, output):
    with open(input, "r", encoding="utf-8") as f:
        j = json.load(f)
        
    with open(output, "wb") as f:
        # 1. 修复头部 (loc8Converter v0.3 / 第一次修复)
        # 修正第8个字节为 '09'，适用于简体中文文件。
        f.write(bytes.fromhex("0000000100000009"))
        
        # 2. 写入字符串数量
        f.write(len(j).to_bytes(4, "big"))
        
        # 3. 写入字符串数据
        for id, string in j.items():
            f.write(int(id).to_bytes(4, "big"))
            f.write(len(string.replace("\n", "\x0A").encode("utf-8")).to_bytes(4, "big"))
            f.write(string.replace("\n", "\x0A").encode("utf-8"))

        # 4. 修复尾部 (loc8Converter v0.4 / 第二次修复)
        # 移除硬编码的 'FF' 填充，改为动态计算 '00' 填充，以实现 16 字节对齐。
        current_size = f.tell()
        # 计算需要填充的字节数，以达到下一个 16 字节的边界
        padding_size = (16 - (current_size % 16)) % 16
        
        # 写入所需的 0x00 字节
        f.write(b'\x00' * padding_size)

def patch(input, output):
    patchjson = json.load(open(input, 'r', encoding="utf-8"))
    originaljson = json.load(open(output, 'r', encoding="utf-8"))
    for i in patchjson:
        originaljson[i] = patchjson[i]
    with open(output, "w", encoding="utf-8") as f:
        json.dump(originaljson, f, ensure_ascii=False, separators=(',', ':'))

if __name__ == "__main__":
    import sys

    if len(sys.argv) == 4:
        mode = sys.argv[1]
        inputFile = sys.argv[2]
        outputFile = sys.argv[3]

        if mode == "-d" or mode == "--decompress":
            decompress(inputFile, outputFile)

        if mode == "-c" or mode == "--compress":
            compress(inputFile, outputFile)

        if mode == "-p" or mode == "--patch":
            patch(inputFile, outputFile)
    else:
        print('')
        print("This script requires passing parameters when used standalone.")
        print("Usage: py loc8Converter.py <mode> <input> <output>")
        print("Example: py loc8Converter.py -d localization.loc8 localization.json")