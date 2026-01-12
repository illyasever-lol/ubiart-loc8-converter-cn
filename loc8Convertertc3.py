# -*- coding: utf-8 -*-
import json
import os
import sys

# 严格对照用户提供的语种 HEX 信息
LANG_MAP = {
    "0": ("英语 (English)", 0x00),
    "1": ("法语 (French)", 0x01),
    "2": ("日语 (Japanese)", 0x02),
    "3": ("德语 (German)", 0x03),
    "4": ("西班牙语 (Spanish)", 0x04),
    "6": ("韩语 (Korean)", 0x06),
    "7": ("繁体中文 (Traditional Chinese)", 0x07),
    "8": ("葡萄牙语 (Portuguese)", 0x08),
    "9": ("简体中文 (Simplified Chinese)", 0x09),
    "C": ("荷兰语 (Dutch)", 0x0C),
    "D": ("丹麦语 (Danish)", 0x0D),
    "E": ("挪威语 (Norwegian)", 0x0E),
    "10": ("芬兰语 (Finnish)", 0x10)
}

def print_language_menu():
    print("\n" + "="*60)
    print(f"{'编号':<8} {'语种名称 (Language)':<35} {'HEX 头部 ID'}")
    print("-" * 60)
    # 按十六进制数值排序显示
    sorted_keys = sorted(LANG_MAP.keys(), key=lambda x: int(x, 16))
    for k in sorted_keys:
        name, val = LANG_MAP[k]
        print(f" [{k:<5}] {name:<38} 0x{val:02x}")
    print("="*60)

def load_json(path):
    """加载并解析 JSON 文件"""
    for enc in ['utf-8-sig', 'utf-8', 'gbk']:
        try:
            with open(path, 'rb') as f:
                return json.loads(f.read().decode(enc))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    raise Exception("JSON 格式错误或编码不支持。请确保文件末尾没有多余逗号。")

def decompress(input_file, output_file):
    """解压模式: loc8 -> JSON"""
    try:
        with open(input_file, "rb") as f:
            f.seek(7)
            lang_id = int.from_bytes(f.read(1), "big")
            f.seek(8)
            count = int.from_bytes(f.read(4), "big")
            print(f"[*] 检测到语种 ID: {hex(lang_id)}，文本总数: {count}")
            
            data = {}
            for _ in range(count):
                str_id = int.from_bytes(f.read(4), "big")
                str_len = int.from_bytes(f.read(4), "big")
                content = f.read(str_len).decode("utf-8").replace("\x0a", "\n")
                data[str_id] = content
                
            with open(output_file, "w", encoding="utf-8") as f2:
                json.dump(data, f2, ensure_ascii=False, indent=4, sort_keys=True)
            print(f"[+] 解压完成: {output_file}")
    except Exception as e:
        print(f"[X] 解压失败: {e}")

def compress(input_file, output_file):
    """压缩模式: JSON -> loc8 (使用 0x00 进行 16 字节对齐)"""
    try:
        data = load_json(input_file)
        
        # 转换前提示语种信息
        print_language_menu()
        choice = input("\n请输入语种编号 (例如 7 代表繁体, 9 代表简体, 直接回车默认为 7): ").strip().upper() or "7"
        
        if choice not in LANG_MAP:
            print("[!] 无效编号，请重新运行。")
            return
        
        target_id = LANG_MAP[choice][1]
        print(f"[*] 正在生成: {LANG_MAP[choice][0]} (ID: 0x{target_id:02x})")

        with open(output_file, "wb") as f:
            # 1. 写入 8 字节头部: 00 00 00 01 00 00 00 ID
            f.write(b'\x00\x00\x00\x01\x00\x00\x00' + bytes([target_id]))
            
            # 2. 写入数量 (4字节)
            f.write(len(data).to_bytes(4, "big"))
            
            # 3. 写入每一条字符串
            for sid, text in data.items():
                f.write(int(sid).to_bytes(4, "big"))
                # 换行符转回 0x0A 并计算字节长度
                encoded_text = text.replace("\n", "\x0a").encode("utf-8")
                f.write(len(encoded_text).to_bytes(4, "big"))
                f.write(encoded_text)

            # 4. 关键对齐逻辑 (根据 loc8Convertersc 成功案例修复)
            # 使用 0x00 填充，使文件总大小对齐到 16 字节
            current_pos = f.tell()
            padding_size = (16 - (current_pos % 16)) % 16
            
            if padding_size > 0:
                f.write(b'\x00' * padding_size)
            
        print(f"\n[+] 转换完成！")
        print(f"    - 最终对齐填充: {padding_size} 字节 (使用 0x00)")
        print(f"    - 文件大小: {os.path.getsize(output_file)} 字节")
        
    except Exception as e:
        print(f"\n[X] 转换失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) == 4:
        mode, inp, out = sys.argv[1], sys.argv[2], sys.argv[3]
        if mode == "-d":
            decompress(inp, out)
        elif mode == "-c":
            compress(inp, out)
        else:
            print("[!] 模式错误。使用 -d 解压或 -c 压缩。")
    else:
        print("\nUbiArt loc8 修复版 (0x00 16字节对齐)")
        print("用法: python loc8Converter_Perfect.py <模式> <输入> <输出>")
        print("模式: -d (解压), -c (压缩)")