import ctypes
import sys
import os
import time
import random
import base64
import io
import threading
from datetime import datetime

import pyautogui
import pygetwindow as gw
import keyboard
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

ctypes.windll.shcore.SetProcessDpiAwareness(2)


def get_base_path():
    return os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)


ICON_DATA = "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"

def get_embedded_icon():
    img = Image.open(io.BytesIO(base64.b64decode(ICON_DATA)))
    return ImageTk.PhotoImage(img)


HWND_TOPMOST = -1
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
RAND_DELAY_MIN = 0.9
RAND_DELAY_MAX = 1.1
SCROLL_STEP = 120


class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]


def get_client_rect(hwnd):
    rect = RECT()
    ctypes.windll.user32.GetClientRect(hwnd, ctypes.byref(rect))
    return rect.right - rect.left, rect.bottom - rect.top


CONFIG = {
    "stabilize_delay": 0.05,           # 拖拽后等待画面稳定的时间(秒)
    "screenshot_delay": 0.01,          # 截图前的等待时间(秒)
    "capture_region_x": 0.626,         # 截图区域水平比例（相对于窗口宽度）
    "capture_region_y": 0.648,         # 截图区域垂直比例（相对于窗口高度）
    "capture_offset_y": 0.03,          # 截图区域垂直偏移（正数向下）
    "drag_margin": 2,                  # 拖拽操作距离窗口边缘的像素距离
    "drag_duration": 0.01,             # 拖拽动作持续时间(秒)
    "base_window_size": (1600, 900),   # 基准窗口尺寸（宽, 高）
    "output_folder": os.path.join(get_base_path(), "screenshots"),  # 截图输出目录
    "output_format": "PNG",            # 输出格式（PNG或JPEG）
}

SCROLL_MODES = {"全名最小字": {"scroll_count": 0}, "全名最大字": {"scroll_count": 5}, "单字最小字": {"scroll_count": 6}}

REGION_CONFIG = {
    "武陵-武陵城": {
        "16:9": {
            "全名最小字": {"grid": (15, 9), "overlap_x": 0.09, "overlap_y": 0.01, "drag": (826, 523)},
            "全名最大字": {"grid": (8, 4), "overlap_x": 0.001, "overlap_y": 0.105, "drag": (1232, 643)},
            "单字最小字": {"grid": (7, 4), "overlap_x": 0.16, "overlap_y": 0.09, "drag": (1072, 676)},
        },
    },
    "武陵-景玉谷": {
        "16:9": {
            "全名最小字": {"grid": (10, 6), "overlap_x": 0.001, "overlap_y": 0.01, "drag": (903, 522)},
            "全名最大字": {"grid": (6, 3), "overlap_x": 0.105, "overlap_y": 0.165, "drag": (1104, 599)},
            "单字最小字": {"grid": (5, 3), "overlap_x": 0.262, "overlap_y": 0.09, "drag": (941, 676)},
        },
    },
    "谷地-枢纽区": {
        "16:9": {
            "全名最小字": {"grid": (13, 8), "overlap_x": 0.06, "overlap_y": 0.01, "drag": (851, 522)},
            "全名最大字": {"grid": (7, 4), "overlap_x": 0.147, "overlap_y": 0.06, "drag": (1052, 676)},
            "单字最小字": {"grid": (7, 4), "overlap_x": 0.271, "overlap_y": 0.171, "drag": (930, 616)},
        },
    },
}

_GUDI_COMMON_CONFIG = {
    "16:9": {
        "全名最小字": {"grid": (9, 5), "overlap_x": 0.001, "overlap_y": 0.008, "drag": (905, 524)},
        "全名最大字": {"grid": (5, 3), "overlap_x": 0.325, "overlap_y": 0.15, "drag": (834, 612)},
        "单字最小字": {"grid": (5, 2), "overlap_x": 0.007, "overlap_y": 0.23, "drag": (1270, 574)},
    },
}

for _region in ["谷地-供能高地", "谷地-谷地通道", "谷地-源石研究园"]:
    REGION_CONFIG[_region] = _GUDI_COMMON_CONFIG

ASPECT_RATIOS = ["16:9", "自定义"]
REGIONS = list(REGION_CONFIG.keys()) + ["自定义"]

DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_SCROLL_MODE = "全名最小字"
GAME_WINDOW_TITLE = "Endfield"


class GameScreenshotTool:
    def __init__(self, log_callback=None):
        self.__dict__.update(CONFIG)
        self.log_callback = log_callback
        self._running_lock = threading.Lock()
        self._is_running = False
        self.screenshots = []
        self.game_window = None
        self.grid_size = None
        self.aspect_ratio = DEFAULT_ASPECT_RATIO
        self.scroll_mode = DEFAULT_SCROLL_MODE
        self.drag_distance = self._get_drag_distance()
        self.custom_overlap_x = 0.01
        self.custom_overlap_y = 0.01

    @property
    def is_running(self):
        with self._running_lock:
            return self._is_running

    @is_running.setter
    def is_running(self, value):
        with self._running_lock:
            self._is_running = value

    def _get_region_config(self, region_name=None):
        if self.aspect_ratio == "自定义":
            return None
        region = region_name or getattr(self, 'current_region', None)
        if region and region in REGION_CONFIG:
            region_data = REGION_CONFIG.get(region)
            aspect_data = region_data.get(self.aspect_ratio, region_data.get(DEFAULT_ASPECT_RATIO))
            if aspect_data and self.scroll_mode in aspect_data:
                return aspect_data[self.scroll_mode]
        return None

    def _get_drag_distance(self, region_name=None):
        config = self._get_region_config(region_name)
        return config.get("drag", (0, 0)) if config else (0, 0)

    def _get_overlap(self, region_name=None):
        if self.aspect_ratio == "自定义":
            return self.custom_overlap_x, self.custom_overlap_y
        config = self._get_region_config(region_name)
        if config:
            return config.get("overlap_x", 0.01), config.get("overlap_y", 0.01)
        return 0.01, 0.01

    def set_aspect_ratio(self, aspect_ratio):
        if aspect_ratio in ASPECT_RATIOS:
            self.aspect_ratio = aspect_ratio
            self.drag_distance = self._get_drag_distance(getattr(self, 'current_region', None))

    def set_scroll_mode(self, scroll_mode):
        if scroll_mode in SCROLL_MODES:
            self.scroll_mode = scroll_mode
            self.drag_distance = self._get_drag_distance(getattr(self, 'current_region', None))

    def get_grid_size(self, region_name):
        if region_name == "自定义" or self.aspect_ratio == "自定义":
            return None
        config = self._get_region_config(region_name)
        return config.get("grid") if config else None

    def log(self, msg):
        if self.log_callback:
            self.log_callback(msg)
        else:
            print(msg)

    def rand_delay(self, base):
        return base * random.uniform(RAND_DELAY_MIN, RAND_DELAY_MAX)

    def find_game_window(self):
        if self.game_window:
            try:
                _ = self.game_window.title
                return self.game_window
            except Exception:
                self.game_window = None
        windows = gw.getWindowsWithTitle(GAME_WINDOW_TITLE)
        if not windows:
            windows = gw.getAllWindows()
        for w in windows:
            if GAME_WINDOW_TITLE.lower() in w.title.lower():
                self.game_window = w
                return self.game_window
        return None

    def setup_window(self):
        if self.game_window:
            self.game_window.activate()
            ctypes.windll.user32.SetWindowPos(
                self.game_window._hWnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOSIZE | SWP_NOMOVE
            )
            time.sleep(1.5)
        return bool(self.game_window)

    def do_scroll(self):
        scroll_count = SCROLL_MODES.get(self.scroll_mode, {}).get("scroll_count", 0)
        if scroll_count <= 0:
            self.log("跳过滚轮滚动")
            return
        
        self.log(f"执行滚轮滚动: 向下滚动 {scroll_count} 次")
        w, h = self.game_window.width, self.game_window.height
        center_x = self.game_window.left + w // 2
        center_y = self.game_window.top + h // 2
        
        pyautogui.moveTo(center_x, center_y, duration=0.1)
        time.sleep(0.1)
        
        for i in range(scroll_count):
            if not self.is_running:
                return
            pyautogui.scroll(-SCROLL_STEP, x=center_x, y=center_y)
            time.sleep(0.15)
        
        time.sleep(0.5)
        
        margin = self.drag_margin
        start_x = self.game_window.left + margin
        start_y = self.game_window.top + margin
        end_x = start_x + 300
        end_y = start_y + 300
        
        self.log("拖拽画面刷新...")
        pyautogui.moveTo(end_x, end_y, duration=0.1)
        pyautogui.mouseDown(button='middle')
        pyautogui.moveTo(start_x, start_y, duration=0.3)
        pyautogui.moveTo(end_x, end_y, duration=0.3)
        pyautogui.mouseUp(button='middle')
        time.sleep(0.05)
        
        self.log("滚轮滚动完成")

    def capture_center_region(self):
        win = self.game_window
        client_w, client_h = get_client_rect(win._hWnd)
        border_x = (win.width - client_w) // 2
        border_y = win.height - client_h - border_x
        client_left = win.left + border_x
        client_top = win.top + border_y
        
        region_size = int(client_w * self.capture_region_x), int(client_h * self.capture_region_y)
        offset_y = int(client_h * self.capture_offset_y)
        region_pos = (
            client_left + (client_w - region_size[0]) // 2,
            client_top + (client_h - region_size[1]) // 2 + offset_y,
        )
        return pyautogui.screenshot(region=(*region_pos, *region_size))

    def move_camera(self, direction):
        if not self.game_window or direction not in ('right', 'left', 'down'):
            return
        win, margin = self.game_window, self.drag_margin
        dx, dy = self.drag_distance
        client_w, client_h = get_client_rect(win._hWnd)
        border_x = (win.width - client_w) // 2
        border_y = win.height - client_h - border_x
        client_left = win.left + border_x
        client_top = win.top + border_y
        base_x = client_left + margin
        base_y_h = client_top + client_h - margin
        base_y_v = client_top + margin
        drag_x = client_left + dx + margin
        drag_y = client_top + dy + margin
        
        if direction == 'right':
            start_x, start_y, end_x, end_y = drag_x, base_y_h, base_x, base_y_h
        elif direction == 'left':
            start_x, start_y, end_x, end_y = base_x, base_y_h, drag_x, base_y_h
        else:
            start_x, start_y, end_x, end_y = base_x, drag_y, base_x, base_y_v
        
        pyautogui.moveTo(start_x, start_y, duration=0.1)
        time.sleep(self.rand_delay(0.05))
        pyautogui.mouseDown(button='middle')
        time.sleep(self.rand_delay(0.1))
        pyautogui.moveTo(end_x, end_y, duration=self.drag_duration)
        time.sleep(self.rand_delay(0.1))
        pyautogui.mouseUp(button='middle')
        time.sleep(self.rand_delay(0.1 + self.stabilize_delay))

    def auto_capture_grid(self):
        self.log("开始自动截图...")
        self.screenshots = []
        if not self.find_game_window() or not self.setup_window():
            self.log("未找到终末地窗口！")
            return False
        
        self.do_scroll()
        if not self.is_running:
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
                self.screenshots.append({
                    'img': self.capture_center_region(),
                    'pos': (row, col)
                })
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
        img_w, img_h = first_img.size
        overlap_x, overlap_y = self._get_overlap(self.current_region)
        overlap_px_x, overlap_px_y = int(img_w * overlap_x), int(img_h * overlap_y)
        step = img_w - overlap_px_x, img_h - overlap_px_y
        total_size = step[0] * self.grid_size[1] + overlap_px_x, step[1] * self.grid_size[0] + overlap_px_y
        result = Image.new('RGB', total_size)
        
        for info in sorted(self.screenshots, key=lambda x: x['pos']):
            pos = info['pos'][1] * step[0], info['pos'][0] * step[1]
            result.paste(info['img'], pos)
        
        self.screenshots.clear()
        
        os.makedirs(self.output_folder, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        mode_suffix = f"_{self.scroll_mode}" if self.scroll_mode != DEFAULT_SCROLL_MODE else ""
        ext = self.output_format.lower()
        output_path = os.path.join(self.output_folder, f"stitched_{timestamp}{mode_suffix}.{ext}")
        if self.output_format == "PNG":
            result.save(output_path, 'PNG')
        else:
            result.save(output_path, 'JPEG', quality=95)
        self.log(f"拼接完成：{output_path}")

    def start_capture(self, region_name, rows=None, cols=None):
        if self.is_running:
            return self.log("已在运行中")
        
        self.current_region = region_name
        if region_name != "自定义":
            self.drag_distance = self._get_drag_distance(region_name)
        
        if region_name == "自定义":
            if rows and cols and rows > 0 and cols > 0:
                self.grid_size = (rows, cols)
            else:
                return self.log("请输入有效的行列数")
        else:
            grid_size = self.get_grid_size(region_name)
            if grid_size:
                self.grid_size = grid_size
            else:
                return self.log("未找到该区域的配置")
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
            except (pyautogui.FailSafeException, pyautogui.ImageNotFoundException) as e:
                self.log(f"操作异常：{e}")
            except OSError as e:
                self.log(f"文件操作错误：{e}")
            except Exception as e:
                self.log(f"未知错误：{type(e).__name__}: {e}")
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
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = self.output_format.lower()
        screenshot_path = os.path.join(self.output_folder, f"manual_{timestamp}.{ext}")
        if self.output_format == "PNG":
            screenshot_img.save(screenshot_path, 'PNG')
        else:
            screenshot_img.save(screenshot_path, 'JPEG', quality=95)
        self.log(f"已保存：{screenshot_path}")


class ScreenshotGUI:
    VERSION = "v2.0.0"
    AUTHOR = "b站@Taumata°"
    WINDOW_TITLE = "终末地截图工具"
    WINDOW_SIZE = "520x470"
    
    def __init__(self):
        self.root = tk.Tk()
        self._setup_dpi_scaling()
        self.root.title(f"{self.WINDOW_TITLE}{self.VERSION} - {self.AUTHOR}")
        self.root.geometry(self.WINDOW_SIZE)
        self.root.resizable(False, False)
        self.icon_photo = get_embedded_icon()
        self.root.iconphoto(True, self.icon_photo)
        self.tool = GameScreenshotTool(log_callback=self.append_log)
        self.setup_ui()
        self.setup_hotkeys()

    def _setup_dpi_scaling(self):
        try:
            hwnd = ctypes.windll.user32.GetDesktopWindow()
            dc = ctypes.windll.user32.GetDC(hwnd)
            dpi = ctypes.windll.gdi32.GetDeviceCaps(dc, 88)
            ctypes.windll.user32.ReleaseDC(hwnd, dc)
            if dpi > 0:
                divisor = 72 + (dpi - 96) * 17 / 24
                scale = dpi / divisor
                self.root.tk.call('tk', 'scaling', scale)
        except Exception:
            pass

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            main_frame, 
            text=f"{self.WINDOW_TITLE}{self.VERSION}", 
            font=("Microsoft YaHei", 14, "bold")
        ).pack(pady=(0, 10))
        
        self._setup_config_frame(main_frame)
        self._setup_region_frame(main_frame)
        self._setup_buttons(main_frame)
        self._setup_log_frame(main_frame)
        self._setup_hint(main_frame)

    def _setup_config_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="配置信息", padding="5")
        frame.pack(fill=tk.X, pady=1)
        
        row1 = ttk.Frame(frame)
        row1.pack(fill=tk.X)
        
        ttk.Label(row1, text="比例:").pack(side=tk.LEFT)
        self.aspect_ratio_var = tk.StringVar(value=self.tool.aspect_ratio)
        self.aspect_ratio_combo = ttk.Combobox(
            row1, textvariable=self.aspect_ratio_var,
            values=ASPECT_RATIOS, state="readonly", width=5
        )
        self.aspect_ratio_combo.pack(side=tk.LEFT, padx=5)
        self.aspect_ratio_combo.bind("<<ComboboxSelected>>", self.on_aspect_ratio_change)
        
        ttk.Label(row1, text="拖拽距离:").pack(side=tk.LEFT, padx=(10, 0))
        self.drag_x_entry = self._create_entry(row1, 5)
        ttk.Label(row1, text="x").pack(side=tk.LEFT)
        self.drag_y_entry = self._create_entry(row1, 5)
        
        ttk.Label(row1, text="重叠率:").pack(side=tk.LEFT, padx=(10, 0))
        self.overlap_x_entry = self._create_entry(row1, 5)
        ttk.Label(row1, text="x").pack(side=tk.LEFT)
        self.overlap_y_entry = self._create_entry(row1, 5)
        ttk.Label(row1, text="%").pack(side=tk.LEFT)
        
        self.update_drag_display()
        self.update_overlap_display()
        
        row2 = ttk.Frame(frame)
        row2.pack(fill=tk.X, pady=(5, 0))
        
        self.scroll_mode_var = tk.StringVar(value=self.tool.scroll_mode)
        center_frame = ttk.Frame(row2)
        center_frame.pack(expand=True)
        self.scroll_mode_radios = []
        for mode in SCROLL_MODES:
            rb = ttk.Radiobutton(
                center_frame, text=mode, value=mode,
                variable=self.scroll_mode_var,
                command=self.on_scroll_mode_change
            )
            rb.pack(side=tk.LEFT, padx=10)
            self.scroll_mode_radios.append(rb)
        
        ttk.Label(center_frame, text="输出格式: ").pack(side=tk.LEFT, padx=(20, 0))
        self.output_format_var = tk.StringVar(value=self.tool.output_format)
        self.output_format_combo = ttk.Combobox(
            center_frame, textvariable=self.output_format_var,
            values=["PNG", "JPEG"], state="readonly", width=5
        )
        self.output_format_combo.pack(side=tk.LEFT)
        self.output_format_combo.bind("<<ComboboxSelected>>", self.on_output_format_change)

    def _setup_region_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="截图区域", padding="5")
        frame.pack(fill=tk.X, pady=1)
        
        ttk.Label(frame, text="区域:").pack(side=tk.LEFT)
        self.region_var = tk.StringVar(value="武陵-武陵城")
        self.region_combo = ttk.Combobox(
            frame, textvariable=self.region_var,
            values=REGIONS, state="readonly", width=12
        )
        self.region_combo.pack(side=tk.LEFT, padx=5)
        self.region_combo.bind("<<ComboboxSelected>>", self.on_region_change)
        
        ttk.Label(frame, text="行:").pack(side=tk.LEFT, padx=(10, 0))
        self.rows_entry = self._create_entry(frame, 4)
        ttk.Label(frame, text="列:").pack(side=tk.LEFT, padx=(5, 0))
        self.cols_entry = self._create_entry(frame, 4)
        
        ttk.Label(frame, text="宽:").pack(side=tk.LEFT, padx=(10, 0))
        self.capture_region_x_entry = self._create_entry(frame, 5)
        ttk.Label(frame, text="高:").pack(side=tk.LEFT, padx=(5, 0))
        self.capture_region_y_entry = self._create_entry(frame, 5)
        ttk.Label(frame, text="%").pack(side=tk.LEFT)
        
        self.update_grid_display()
        self.update_capture_region_display()

    def _setup_buttons(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        
        buttons = [
            ("开始截图 (F1)", self.start_capture),
            ("停止 (F2)", self.stop_capture),
            ("手动截图 (F3)", self.manual_capture),
            ("退出 (F4)", self.exit_app),
        ]
        for text, cmd in buttons:
            ttk.Button(frame, text=text, command=cmd, width=13).pack(side=tk.LEFT, padx=5)

    def _setup_log_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="日志", padding="5")
        frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.log_text = scrolledtext.ScrolledText(frame, height=8, width=50, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _setup_hint(self, parent):
        ttk.Label(
            parent,
            text="进入俯瞰批量选择模式，视野拉到最小并移到左上角使用，截图请勿移动鼠标",
            foreground="gray"
        ).pack(pady=1)

    def _create_entry(self, parent, width):
        entry = ttk.Entry(parent, width=width, state=tk.DISABLED)
        entry.pack(side=tk.LEFT, padx=3)
        return entry

    def _update_entry(self, entry, value, keep_editable=False):
        entry.config(state=tk.NORMAL)
        entry.delete(0, tk.END)
        entry.insert(0, str(value))
        if not keep_editable:
            entry.config(state=tk.DISABLED)

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
            self.update_drag_display()
            self.update_overlap_display()

    def on_scroll_mode_change(self, event=None):
        self.tool.set_scroll_mode(self.scroll_mode_var.get())
        is_custom = self.aspect_ratio_var.get() == "自定义"
        self.update_drag_display(keep_editable=is_custom)
        self.update_overlap_display()
        self.update_grid_display()

    def on_output_format_change(self, event=None):
        self.tool.output_format = self.output_format_var.get()

    def on_aspect_ratio_change(self, event=None):
        aspect_ratio = self.aspect_ratio_var.get()
        is_custom = aspect_ratio == "自定义"
        state = tk.NORMAL if is_custom else tk.DISABLED
        
        for entry in [self.drag_x_entry, self.drag_y_entry, self.overlap_x_entry, self.overlap_y_entry, self.capture_region_x_entry, self.capture_region_y_entry]:
            entry.config(state=state)
        
        scroll_state = tk.DISABLED if is_custom else tk.NORMAL
        for rb in self.scroll_mode_radios:
            rb.config(state=scroll_state)
        
        if is_custom:
            self.tool.aspect_ratio = "自定义"
            self.scroll_mode_var.set(DEFAULT_SCROLL_MODE)
            self.tool.set_scroll_mode(DEFAULT_SCROLL_MODE)
            dx, dy = self.tool.drag_distance or (0, 0)
            overlap_x, overlap_y = self.tool._get_overlap(self.region_var.get())
            self._update_entry(self.drag_x_entry, dx, keep_editable=True)
            self._update_entry(self.drag_y_entry, dy, keep_editable=True)
            self._update_entry(self.overlap_x_entry, f"{overlap_x * 100:.1f}", keep_editable=True)
            self._update_entry(self.overlap_y_entry, f"{overlap_y * 100:.1f}", keep_editable=True)
            self._update_entry(self.capture_region_x_entry, f"{self.tool.capture_region_x * 100:.1f}", keep_editable=True)
            self._update_entry(self.capture_region_y_entry, f"{self.tool.capture_region_y * 100:.1f}", keep_editable=True)
        else:
            self.tool.set_aspect_ratio(aspect_ratio)
            self.update_drag_display()
            self.update_overlap_display()
            self.update_capture_region_display()
            self.update_grid_display()

    def _get_current_region(self):
        return self.region_var.get() if hasattr(self, 'region_var') else REGIONS[0]

    def update_drag_display(self, keep_editable=False):
        drag = self.tool._get_drag_distance(self._get_current_region())
        dx, dy = drag or (0, 0)
        self._update_entry(self.drag_x_entry, dx, keep_editable=keep_editable)
        self._update_entry(self.drag_y_entry, dy, keep_editable=keep_editable)

    def update_overlap_display(self):
        overlap_x, overlap_y = self.tool._get_overlap(self._get_current_region())
        self._update_entry(self.overlap_x_entry, f"{overlap_x * 100:.1f}")
        self._update_entry(self.overlap_y_entry, f"{overlap_y * 100:.1f}")

    def update_capture_region_display(self):
        self._update_entry(self.capture_region_x_entry, f"{self.tool.capture_region_x * 100:.1f}")
        self._update_entry(self.capture_region_y_entry, f"{self.tool.capture_region_y * 100:.1f}")

    def update_grid_display(self):
        grid_size = self.tool.get_grid_size(self._get_current_region())
        if grid_size:
            self._update_entry(self.rows_entry, grid_size[0])
            self._update_entry(self.cols_entry, grid_size[1])

    def append_log(self, msg):
        def _append():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"[{datetime.now():%H:%M:%S}] {msg}\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        self.root.after(0, _append)

    def _validate_custom_params(self):
        try:
            drag_x = int(self.drag_x_entry.get())
            drag_y = int(self.drag_y_entry.get())
            if drag_x <= 0 or drag_y <= 0:
                messagebox.showerror("错误", "拖拽距离必须大于0")
                return False
            self.tool.drag_distance = (drag_x, drag_y)
            
            overlap_x = float(self.overlap_x_entry.get())
            overlap_y = float(self.overlap_y_entry.get())
            if not (0 < overlap_x < 100 and 0 < overlap_y < 100):
                messagebox.showerror("错误", "重叠率必须在0到100之间")
                return False
            self.tool.custom_overlap_x = overlap_x / 100
            self.tool.custom_overlap_y = overlap_y / 100
            
            capture_region_x = float(self.capture_region_x_entry.get())
            capture_region_y = float(self.capture_region_y_entry.get())
            if not (0 < capture_region_x < 100 and 0 < capture_region_y < 100):
                messagebox.showerror("错误", "截图区域比例必须在0到100之间")
                return False
            self.tool.capture_region_x = capture_region_x / 100
            self.tool.capture_region_y = capture_region_y / 100
            return True
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数值")
            return False

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
        
        if self.aspect_ratio_var.get() == "自定义":
            if not self._validate_custom_params():
                return
        
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
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit(0)
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        self.on_region_change()
        
        startup_msgs = [
            "=" * 45,
            "程序已启动",
            f"输出目录: {self.tool.output_folder}",
            "=" * 45,
            "使用说明：",
            "1. 确保分辨率16:9将画面缩到最小并移到左上角",
            "2. 选择截图地区后点击按钮或F1开始",
            "3. 可自定义截图变量及点击F3截取单张画面",
            "=" * 45,
        ]
        for msg in startup_msgs:
            self.append_log(msg)
        
        self.root.mainloop()


if __name__ == "__main__":
    ScreenshotGUI().run()
