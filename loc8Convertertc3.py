# -*- coding: utf-8 -*-
import json
import os
import sys

def load_json_file(path):
    """尝试以多种编码加载 JSON 文件，并提供详细的错误定位。"""
    content = None
    # 尝试常见的编码格式
    for enc in ['utf-8', 'gbk', 'utf-16', 'big5']:
        try:
            with open(path, 'rb') as f:
                raw = f.read()
                content = raw.decode(enc)
                break
        except UnicodeDecodeError:
            continue
    
    if content is None:
        raise Exception(f"编码错误：无法使用 UTF-8 或 GBK 解析文件 {path}。")

    # 尝试解析 JSON 语法
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        # 针对你之前遇到的文件截断问题，这里会输出具体行号
        raise Exception(f"JSON 语法错误 (行 {e.lineno}, 列 {e.colno}): {e.msg}\n"
                        f"提示：请检查文件末尾是否缺少 '}}' 或多出了逗号。")

def decompress(input_file, output_file):
    """将 loc8 二进制文件解压为 JSON 格式"""
    try:
        with open(input_file, "rb") as f:
            # 读取语言标识位 (偏移量 7)
            f.seek(7)
            lang_id = f.read(1)
            print(f"[*] 检测到语言标识字节: {lang_id.hex()}")
            
            f.seek(8)
            j = {}
            amount_bytes = f.read(4)
            if not amount_bytes: 
                print("[!] 错误：无法读取字符串数量，文件可能已损坏。")
                return
            amount_of_strings = int.from_bytes(amount_bytes, "big")
            print(f"[*] 正在提取 {amount_of_strings} 条文本...")
            
            for i in range(amount_of_strings):
                str_id_bytes = f.read(4)
                if not str_id_bytes: break
                str_id = int.from_bytes(str_id_bytes, "big")
                
                len_bytes = f.read(4)
                if not len_bytes: break
                str_len = int.from_bytes(len_bytes, "big")
                
                raw_data = f.read(str_len)
                try:
                    # 优先使用 UTF-8，失败则尝试 GBK
                    content = raw_data.decode("utf-8").replace("\x0A", "\n")
                except UnicodeDecodeError:
                    content = raw_data.decode("gbk", errors="replace").replace("\x0A", "\n")
                
                j[str_id] = content

            with open(output_file, "w", encoding="utf-8") as f2:
                # 使用 indent=4 使 JSON 易于编辑和阅读
                json.dump(j, f2, ensure_ascii=False, indent=4, sort_keys=True)
            print(f"[+] 解压成功：{output_file}")
    except Exception as e:
        print(f"[X] 解压失败：{e}")

def compress(input_file, output_file):
    """将 JSON 文件压缩回 loc8 二进制格式"""
    if not os.path.exists(input_file):
        print(f"[!] 错误：找不到输入文件 {input_file}")
        return

    try:
        j = load_json_file(input_file)
    except Exception as e:
        print(f"\n[X] 加载 JSON 失败：{e}")
        return

    # 自动识别语言标识：文件名包含 traditional 则设为 01 (繁体)，否则默认为 09 (简体)
    lang_byte = "07" if "traditional" in input_file.lower() or "traditional" in output_file.lower() else "09"

    with open(output_file, "wb") as f:
        # 1. 写入头部 (8字节)
        f.write(bytes.fromhex(f"00000001000007{lang_byte}"))
        
        # 2. 写入字符串总数 (4字节)
        f.write(len(j).to_bytes(4, "big"))
        
        # 3. 写入字符串数据
        for str_id, string in j.items():
            # ID
            f.write(int(str_id).to_bytes(4, "big"))
            # 内容编码并转换换行符
            encoded_str = string.replace("\n", "\x0A").encode("utf-8")
            # 长度
            f.write(len(encoded_str).to_bytes(4, "big"))
            # 文本
            f.write(encoded_str)

        # 4. 数据段 16 字节对齐
        curr_pos = f.tell()
        data_padding = (16 - (curr_pos % 16)) % 16
        f.write(b'\xFF' * data_padding)

        # 5. 写入 128 字节固定 FF 尾部标记 (UbiArt 格式要求)
        f.write(bytes.fromhex("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF" * 8))

        # 6. 最终文件全长 16 字节对齐
        final_pos = f.tell()
        final_padding = (16 - (final_pos % 16)) % 16
        f.write(b'\xFF' * final_padding)
    
    print(f"[+] 压缩完成！")
    print(f"    - 语言标识: {lang_byte}")
    print(f"    - 填充字节: {data_padding + final_padding}")
    print(f"    - 输出文件: {output_file}")

def patch(patch_file, target_json):
    """将补丁 JSON 的内容合并到目标 JSON 中"""
    try:
        patch_data = load_json_file(patch_file)
        target_data = load_json_file(target_json)
        
        # 使用补丁数据更新目标数据
        target_data.update(patch_data)
        
        with open(target_json, "w", encoding="utf-8") as f:
            json.dump(target_data, f, ensure_ascii=False, indent=4, sort_keys=True)
        print(f"[+] 补丁合并成功：{target_json}")
    except Exception as e:
        print(f"[X] 补丁合并失败：{e}")

if __name__ == "__main__":
    if len(sys.argv) == 4:
        mode, inp, out = sys.argv[1], sys.argv[2], sys.argv[3]
        if mode in ["-d", "--decompress"]:
            decompress(inp, out)
        elif mode in ["-c", "--compress"]:
            compress(inp, out)
        elif mode in ["-p", "--patch"]:
            patch(inp, out)
    else:
        print("\nUbiArt loc8 转换工具 (中文增强版)")
        print("="*40)
        print("用法: python loc8Converter.py <模式> <输入文件> <输出文件>")
        print("\n模式说明:")
        print("  -d  解压: 将 loc8 转换为可编辑的 JSON")
        print("  -c  压缩: 将修改后的 JSON 转换回 loc8")
        print("  -p  补丁: 将 patch.json 的内容合并到目标 JSON")
        print("\n示例:")
        print("  python loc8Converter.py -d lang.loc8 lang.json")