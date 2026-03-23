import ctypes
import sys
import os
import time
import random
import pyautogui
import pygetwindow as gw
from PIL import Image
import keyboard
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

def get_base_path():
    return os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)

def hide_console():
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

CONFIG = {
    "stabilize_delay": 0.08,           # 拖拽后等待画面稳定的时间(秒)
    "screenshot_delay": 0.08,          # 截图前的等待时间(秒)
    "capture_region": (0.62, 0.62),    # 截图区域比例（相对于窗口宽高）
    "overlap": (0.005, 0.010),         # 图片拼接重叠率（宽，高）
    "drag_margin": 40,                 # 拖拽操作距离窗口边缘的像素距离
    "drag_duration": 0.08,             # 拖拽动作持续时间(秒)
    "output_folder": os.path.join(get_base_path(), "screenshots"),  # 截图输出目录
}

PRESET_REGIONS = {
    "武陵-武陵城": (14, 8), "武陵-景玉谷": (10, 6), "谷地-枢纽区": (13, 7),
    "谷地-谷地通道": (9, 5), "谷地-供能高地": (9, 5), "谷地-源石研究园": (9, 5),
    "自定义": None
}                                      # 网格大小(行数, 列数)，由用户选择或自定义

class GameScreenshotTool:
    def __init__(self, log_callback=None):
        self.__dict__.update(CONFIG)
        self.log_callback = log_callback
        self.is_running = False
        self.screenshots = []
        self.game_window = None
        self.grid_size = []

    def log(self, msg):
        if self.log_callback:
            self.log_callback(msg)
        else:
            print(msg)

    def rand_delay(self, base):
        return base * random.uniform(0.9, 1.1)

    def find_game_window(self):
        if self.game_window:
            return self.game_window
        windows = gw.getWindowsWithTitle('Endfield')
        if not windows:
            windows = gw.getAllWindows()
        for w in windows:
            if 'endfield' in w.title.lower():
                self.game_window = w
                return self.game_window
        return None

    def setup_window(self):
        if self.game_window:
            self.game_window.activate()
            ctypes.windll.user32.SetWindowPos(self.game_window._hWnd, -1, 0, 0, 0, 0, 0x0003)
            time.sleep(1.5)
        return bool(self.game_window)

    def capture_center_region(self):
        window_width, window_height = self.game_window.width, self.game_window.height
        region_width = int(window_width * self.capture_region[0])
        region_height = int(window_height * self.capture_region[1])
        region_x = self.game_window.left + (window_width - region_width) // 2
        region_y = self.game_window.top + (window_height - region_height) // 2
        return pyautogui.screenshot(region=(region_x, region_y, region_width, region_height))

    def move_camera(self, direction):
        if not self.game_window:
            return
        window, margin, factor = self.game_window, self.drag_margin, 0.7
        moves = {
            'right': (window.left + int(window.width * factor) + margin, window.top + margin, 
                      window.left + margin, window.top + margin),
            'left': (window.left + margin, window.top + margin, 
                     window.left + int(window.width * factor) + margin, window.top + margin),
            'down': (window.left + margin, window.top + int(window.height * factor) + margin, 
                     window.left + margin, window.top + margin)
        }
        if direction not in moves:
            return
        start_x, start_y, end_x, end_y = moves[direction]
        pyautogui.moveTo(start_x, start_y, duration=0.1)
        time.sleep(self.rand_delay(0.05))
        pyautogui.mouseDown(button='middle')
        time.sleep(self.rand_delay(0.1))
        pyautogui.moveTo(end_x, end_y, duration=self.drag_duration)
        time.sleep(self.rand_delay(0.1))
        pyautogui.mouseUp(button='middle')
        time.sleep(self.rand_delay(0.1))
        time.sleep(self.rand_delay(self.stabilize_delay))

    def auto_capture_grid(self):
        self.log("开始自动截图...")
        self.screenshots = []
        if not self.find_game_window() or not self.setup_window():
            self.log("未找到终末地窗口！")
            return False
        
        rows, cols = self.grid_size
        total = rows * cols
        for row in range(rows):
            is_even_row = row % 2 == 0
            col_range = range(cols) if is_even_row else range(cols - 1, -1, -1)
            for idx, col in enumerate(col_range):
                if not self.is_running:
                    return False
                self.log(f"正在拍摄 ({row * cols + idx + 1}/{total}) 位置 ({row}, {col})...")
                time.sleep(self.rand_delay(self.screenshot_delay))
                self.screenshots.append({'img': self.capture_center_region(), 'pos': (row, col)})
                if idx < cols - 1:
                    self.move_camera('right' if is_even_row else 'left')
            if row < rows - 1:
                self.move_camera('down')
        self.log(f"完成 {len(self.screenshots)} 张截图")
        return True

    def stitch_images(self):
        if not self.screenshots:
            self.log("没有截图可拼接")
            return
        
        first_img = self.screenshots[0]['img']
        img_width, img_height = first_img.size
        overlap_x = int(img_width * self.overlap[0])
        overlap_y = int(img_height * self.overlap[1])
        step_x = img_width - overlap_x
        step_y = img_height - overlap_y
        total_width = step_x * self.grid_size[1] + overlap_x
        total_height = step_y * self.grid_size[0] + overlap_y
        result = Image.new('RGB', (total_width, total_height))
        
        for info in sorted(self.screenshots, key=lambda x: x['pos']):
            pos_x = info['pos'][1] * step_x
            pos_y = info['pos'][0] * step_y
            result.paste(info['img'], (pos_x, pos_y))
        
        os.makedirs(self.output_folder, exist_ok=True)
        output_path = os.path.join(self.output_folder, f"stitched_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        result.save(output_path, 'JPEG', quality=95)
        self.log(f"拼接完成：{output_path}")

    def start_capture(self, region_name, rows=None, cols=None):
        if self.is_running:
            return self.log("已在运行中")
        if region_name == "自定义":
            if rows and cols and rows > 0 and cols > 0:
                self.grid_size = [rows, cols]
            else:
                return self.log("请输入有效的行列数")
        else:
            self.grid_size = list(PRESET_REGIONS[region_name])
        threading.Thread(target=self._capture_thread, daemon=True).start()

    def _capture_thread(self):
        self.is_running = True
        if not self.find_game_window():
            self.log("未找到终末地窗口，请先打开游戏")
        else:
            self.log(f"找到窗口：{self.game_window.title}")
            try:
                if self.auto_capture_grid():
                    self.log("开始拼接图片...")
                    self.stitch_images()
                    self.log("完成！")
                else:
                    self.log("截图中断")
            except Exception as e:
                self.log(f"出错：{e}")
        self.is_running = False

    def stop(self):
        if self.is_running:
            self.is_running = False
            self.log("已停止截图")

    def manual_screenshot(self):
        if self.is_running:
            return self.log("自动截图进行中，无法手动截图")
        if not self.find_game_window():
            return self.log("未找到终末地窗口")
        self.game_window.activate()
        time.sleep(0.5)
        screenshot_img = self.capture_center_region()
        os.makedirs(self.output_folder, exist_ok=True)
        screenshot_path = os.path.join(self.output_folder, f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        screenshot_img.save(screenshot_path, 'JPEG', quality=95)
        self.log(f"已保存：{screenshot_path}")


class ScreenshotGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("终末地截图工具v0.2.0")
        self.root.geometry("520x460")
        self.root.resizable(False, False)
        self.tool = GameScreenshotTool(log_callback=self.append_log)
        self.setup_ui()
        self.setup_hotkeys()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="终末地截图工具v0.2.0", font=("Microsoft YaHei", 14, "bold")).pack(pady=(0, 10))
        
        region_frame = ttk.LabelFrame(main_frame, text="截图区域", padding="5")
        region_frame.pack(fill=tk.X, pady=1)
        
        ttk.Label(region_frame, text="选择区域：").pack(side=tk.LEFT)
        self.region_var = tk.StringVar(value="武陵-武陵城")
        self.region_combo = ttk.Combobox(region_frame, textvariable=self.region_var, 
                                          values=list(PRESET_REGIONS.keys()), state="readonly", width=32)
        self.region_combo.pack(side=tk.LEFT, padx=5)
        self.region_combo.bind("<<ComboboxSelected>>", self.on_region_change)
        
        ttk.Label(region_frame, text="行:").pack(side=tk.LEFT, padx=(10, 0))
        self.rows_entry = ttk.Entry(region_frame, width=4, state=tk.DISABLED)
        self.rows_entry.pack(side=tk.LEFT)
        ttk.Label(region_frame, text="列:").pack(side=tk.LEFT, padx=(5, 0))
        self.cols_entry = ttk.Entry(region_frame, width=4, state=tk.DISABLED)
        self.cols_entry.pack(side=tk.LEFT)
        self.update_grid_display()
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        btns = [("开始截图 (F1)", self.start_capture), ("停止 (F2)", self.stop_capture),
                ("手动截图 (F3)", self.manual_capture), ("退出 (F4)", self.exit_app)]
        for text, cmd in btns:
            ttk.Button(btn_frame, text=text, command=cmd, width=13).pack(side=tk.LEFT, padx=5)
        
        config_frame = ttk.LabelFrame(main_frame, text="配置信息", padding="2")
        config_frame.pack(fill=tk.X, pady=1)
        ttk.Label(config_frame, text=f"截图区域: {self.tool.capture_region[0]*100:.0f}% x {self.tool.capture_region[1]*100:.0f}%  |  "
                                     f"重叠率: {self.tool.overlap[0]*100:.1f}% x {self.tool.overlap[1]*100:.1f}%").pack(padx=0)
        ttk.Label(config_frame, text=f"输出目录: {self.tool.output_folder}").pack(padx=0)
        
        log_frame = ttk.LabelFrame(main_frame, text="日志", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=50, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="提示: 请将游戏设为1280x720窗口，进入俯瞰批量选择模式使用", 
                  foreground="gray").pack(pady=1)

    def on_region_change(self, event=None):
        is_custom = self.region_var.get() == "自定义"
        state = tk.NORMAL if is_custom else tk.DISABLED
        self.rows_entry.config(state=state)
        self.cols_entry.config(state=state)
        if is_custom:
            self.rows_entry.delete(0, tk.END)
            self.cols_entry.delete(0, tk.END)
        else:
            self.update_grid_display()

    def update_grid_display(self):
        region = self.region_var.get()
        if region in PRESET_REGIONS and PRESET_REGIONS[region]:
            grid_rows, grid_cols = PRESET_REGIONS[region]
            for entry, value in [(self.rows_entry, grid_rows), (self.cols_entry, grid_cols)]:
                entry.config(state=tk.NORMAL)
                entry.delete(0, tk.END)
                entry.insert(0, str(value))
                entry.config(state=tk.DISABLED)

    def append_log(self, msg):
        def _append():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"[{datetime.now():%H:%M:%S}] {msg}\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        self.root.after(0, _append)

    def start_capture(self):
        region = self.region_var.get()
        custom_rows = custom_cols = None
        if region == "自定义":
            try:
                custom_rows = int(self.rows_entry.get())
                custom_cols = int(self.cols_entry.get())
                if custom_rows <= 0 or custom_cols <= 0:
                    return messagebox.showerror("错误", "行列数必须大于0")
                if custom_rows > 99 or custom_cols > 99:
                    return messagebox.showerror("错误", "行列数最大为99")
            except ValueError:
                return messagebox.showerror("错误", "请输入有效的数字")
        self.tool.start_capture(region, custom_rows, custom_cols)

    def stop_capture(self):
        self.tool.stop()

    def manual_capture(self):
        self.tool.manual_screenshot()

    def exit_app(self):
        self.tool.is_running = False
        self.root.quit()

    def setup_hotkeys(self):
        hotkeys = {
            "F1": self.start_capture,
            "F2": self.stop_capture,
            "F3": self.manual_capture,
            "F4": self.exit_app,
        }
        for key, action in hotkeys.items():
            keyboard.add_hotkey(key, lambda a=action: self.root.after(0, a))

    def run(self):
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit(0)
        hide_console()
        self.on_region_change()
        for msg in ["=" * 45, "程序已启动", "=" * 45, "使用说明：",
                    "1. 若使用预设，将画面缩到最小并移到左上角，选择截图地区后点击按钮或F1开始",
                    "2. 自定义则输入行数和列数后点击按钮或F1开始", "3. 可点击F3截取单张画面",
                    "=" * 45]:
            self.append_log(msg)
        self.root.mainloop()


if __name__ == "__main__":
    ScreenshotGUI().run()
