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
    "5": ("意大利语 (Italian)", 0x05),
    "6": ("韩语 (Korean)", 0x06),
    "7": ("繁体中文 (Traditional Chinese)", 0x07),
    "8": ("葡萄牙语 (Portuguese)", 0x08),
    "9": ("简体中文 (Simplified Chinese)", 0x09),
    "B": ("俄语 (Russian)", 0x0B),
    "C": ("荷兰语 (Dutch)", 0x0C),
    "D": ("丹麦语 (Danish)", 0x0D),
    "E": ("挪威语 (Norwegian)", 0x0E),
    "F": ("瑞典语 (Swedish)", 0x0F),
    "10": ("芬兰语 (Finnish)", 0x10)
}

def print_language_menu():
    print("\n" + "="*60)
    print(f"{'编号':<8} {'语种名称 (Language)':<35} {'HEX 头部 ID'}")
    print("-" * 60)
    sorted_keys = sorted(LANG_MAP.keys(), key=lambda x: int(x, 16))
    for k in sorted_keys:
        name, val = LANG_MAP[k]
        print(f" [{k:<5}] {name:<38} 0x{val:02x}")
    print("="*60)

def load_json_with_validation(path):
    """
    带有深度校验功能的 JSON 加载器
    能识别语法错误并提示具体位置
    """
    raw_data = None
    # 尝试读取文件
    for enc in ['utf-8-sig', 'utf-8', 'gbk']:
        try:
            with open(path, 'rb') as f:
                raw_data = f.read().decode(enc)
                break
        except UnicodeDecodeError:
            continue
    
    if raw_data is None:
        print(f"[X] 错误: 无法读取文件 {path}，请检查文件是否被占用或编码格式不正确。")
        return None

    try:
        return json.loads(raw_data)
    except json.JSONDecodeError as e:
        print("\n" + "!"*20 + " JSON 校验失败 " + "!"*20)
        print(f"致命错误: 发现非法的 JSON 语法")
        print(f"具体位置: 第 {e.lineno} 行，第 {e.colno} 列")
        print(f"错误原因: {e.msg}")
        
        # 显示错误附近的文本段落
        lines = raw_data.splitlines()
        start = max(0, e.lineno - 3)
        end = min(len(lines), e.lineno + 2)
        
        print("\n错误上下文定位:")
        for i in range(start, end):
            prefix = ">>> " if i == e.lineno - 1 else "    "
            print(f"{prefix}{i+1}: {lines[i]}")
        
        print("\n可能的原因分析:")
        if "Expecting property name enclosed in double quotes" in e.msg:
            print(" -> 提示: 可能是这一行之前的最后一段内容后面多了一个逗号 [ , ]。")
        elif "Expecting ',' delimiter" in e.msg:
            print(" -> 提示: 可能是这一行缺少了逗号或者引号没有闭合。")
        elif "Expecting value" in e.msg:
            print(" -> 提示: 可能是文件末尾不完整，缺少了闭合的大括号 [ } ]。")
        
        print("!"*55 + "\n")
        return None

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
    """压缩模式: JSON -> loc8 (带语法校验)"""
    # 1. 执行校验加载
    data = load_json_with_validation(input_file)
    if data is None:
        print("[X] 由于 JSON 存在语法错误，转换已终止。请修复后重试。")
        return

    try:
        # 2. 语种选择提示
        print_language_menu()
        choice = input("\n请输入语种编号 (例如 7 代表繁体, 直接回车默认为 7): ").strip().upper() or "7"
        
        if choice not in LANG_MAP:
            print("[!] 无效编号。")
            return
        
        target_id = LANG_MAP[choice][1]
        print(f"[*] 正在转换: {LANG_MAP[choice][0]} (ID: 0x{target_id:02x})")

        with open(output_file, "wb") as f:
            # 写入头部
            f.write(b'\x00\x00\x00\x01\x00\x00\x00' + bytes([target_id]))
            f.write(len(data).to_bytes(4, "big"))
            
            # 写入文本
            for sid, text in data.items():
                f.write(int(sid).to_bytes(4, "big"))
                encoded_text = text.replace("\n", "\x0a").encode("utf-8")
                f.write(len(encoded_text).to_bytes(4, "big"))
                f.write(encoded_text)

            # 3. 尾部 16 字节对齐修复 (基于成功版本逻辑)
            current_pos = f.tell()
            padding_size = (16 - (current_pos % 16)) % 16
            if padding_size > 0:
                f.write(b'\x00' * padding_size)
            
        print(f"\n[+] 转换完成！")
        print(f"    - 对齐填充: {padding_size} 字节 (使用 0x00)")
        print(f"    - 最终大小: {os.path.getsize(output_file)} 字节")
        
    except Exception as e:
        print(f"\n[X] 写入过程中发生未知错误: {e}")

if __name__ == "__main__":
    if len(sys.argv) == 4:
        mode, inp, out = sys.argv[1], sys.argv[2], sys.argv[3]
        if mode == "-d": decompress(inp, out)
        elif mode == "-c": compress(inp, out)
        else: print("[!] 模式错误。")
    else:
        print("\nUbiArt loc8 转换器 (增强校验版)")
        print("用法: python 脚本名.py -c <输入json> <输出loc8>")
