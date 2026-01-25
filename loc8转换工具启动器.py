import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

class Loc8ToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LOC8 增强转换工具 v2.4")
        
        # 窗口尺寸与居中
        self.window_width = 420
        self.window_height = 280
        self.center_window()
        self.root.resizable(False, False)

        # 界面布局
        tk.Label(root, text="UbiArt LOC8 转换器", font=("微软雅黑", 14, "bold")).pack(pady=15)
        
        btn_style = {"width": 30, "height": 2, "font": ("微软雅黑", 10), "cursor": "hand2"}

        self.btn_to_json = tk.Button(
            root, text="1. 解包：LOC8 ➡️ JSON", 
            bg="#e1f5fe", command=self.handle_decompress, **btn_style
        )
        self.btn_to_json.pack(pady=10)

        self.btn_to_loc8 = tk.Button(
            root, text="2. 封包：JSON ➡️ LOC8", 
            bg="#fff9c4", command=self.handle_compress, **btn_style
        )
        self.btn_to_loc8.pack(pady=10)
        
        self.status_label = tk.Label(root, text="状态: 等待操作", fg="#666")
        self.status_label.pack(side="bottom", pady=10)

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (self.window_width // 2)
        y = (screen_height // 2) - (self.window_height // 2)
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

    def run_logic(self, mode, input_file, output_file):
        # 1. 获取脚本绝对路径
        script_name = "loc8Convertertc3.py"
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
        
        if not os.path.exists(script_path):
            messagebox.showerror("文件缺失", f"找不到脚本:\n{script_path}")
            return

        # 2. 确定 Python 命令
        python_exe = "py" if os.system("py --version >nul 2>nul") == 0 else "python"
        
        # 3. 彻底解决窗口不停止的问题：
        # 使用 & pause 而不是 || pause。
        # & 表示前面的命令执行完（无论成功失败）都执行后面的 pause。
        # 同时最外层用双引号包裹整个命令链，防止路径中的空格截断命令。
        inner_cmd = f'{python_exe} "{script_path}" {mode} "{input_file}" "{output_file}"'
        final_cmd = f'cmd /c "{inner_cmd} & echo. & echo ================================ & echo 提示：操作已结束，请检查上方信息 & pause"'

        try:
            # 启动新的控制台窗口
            subprocess.Popen(
                final_cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            self.status_label.config(text="状态: 转换窗口运行中...", fg="blue")
        except Exception as e:
            messagebox.showerror("致命错误", f"无法启动命令行窗口:\n{str(e)}")

    def handle_decompress(self):
        file_path = filedialog.askopenfilename(title="选择 LOC8", filetypes=[("LOC8 files", "*.loc8")])
        if file_path:
            output_path = os.path.splitext(file_path)[0] + ".json"
            self.run_logic("-d", file_path, output_path)

    def handle_compress(self):
        file_path = filedialog.askopenfilename(title="选择 JSON", filetypes=[("JSON files", "*.json")])
        if file_path:
            output_path = os.path.splitext(file_path)[0] + ".loc8"
            self.run_logic("-c", file_path, output_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = Loc8ToolGUI(root)
    root.mainloop()