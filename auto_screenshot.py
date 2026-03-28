import ctypes
import sys
import os
import time
import random
import base64
import io
import threading
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any, Callable

import pyautogui
import pygetwindow as gw
import keyboard
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

ctypes.windll.shcore.SetProcessDpiAwareness(2)

DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_SCROLL_MODE = "全名最小字"
VALIDATION_RANGES = {"overlap": (0, 100), "capture_region": (0, 100), "grid": (1, 100),}

ICON_DATA = "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"

CONFIG = {
    "stabilize_delay": 0.08,            # 稳定画面延迟
    "screenshot_delay": 0.01,           # 截图画面延迟
    "capture_region_x": 0.626,          # 截图区域X坐标
    "capture_region_y": 0.648,          # 截图区域Y坐标
    "capture_offset_y": 0.02,           # 截图区域Y偏移
    "drag_margin": 2,                   # 截图区域拓展
    "drag_duration": 0.01,              # 拖动持续时间
    "base_window_size": (1600, 900),    # 基础窗口大小
    "output_folder": os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__),   # 输出文件夹
    "output_format": "JPG",             # 输出文件格式
}

SCROLL_MODES = {"全名最小字": {"scroll_count": 0}, "全名最大字": {"scroll_count": 5}, "单字最小字": {"scroll_count": 6}}

REGION_CONFIG = {
    "武陵-武陵城": {"16:9": {
        "全名最小字": {"grid": (15, 9), "overlap_x": 0.09, "overlap_y": 0.01, "drag": (826, 523)},
        "全名最大字": {"grid": (8, 4), "overlap_x": 0.001, "overlap_y": 0.105, "drag": (1232, 643)},
        "单字最小字": {"grid": (7, 4), "overlap_x": 0.16, "overlap_y": 0.09, "drag": (1072, 676)},
    }},
    "武陵-景玉谷": {"16:9": {
        "全名最小字": {"grid": (10, 6), "overlap_x": 0.001, "overlap_y": 0.01, "drag": (903, 522)},
        "全名最大字": {"grid": (6, 3), "overlap_x": 0.105, "overlap_y": 0.165, "drag": (1104, 599)},
        "单字最小字": {"grid": (5, 3), "overlap_x": 0.262, "overlap_y": 0.09, "drag": (941, 676)},
    }},
    "谷地-枢纽区": {"16:9": {
        "全名最小字": {"grid": (13, 8), "overlap_x": 0.06, "overlap_y": 0.01, "drag": (851, 522)},
        "全名最大字": {"grid": (7, 4), "overlap_x": 0.147, "overlap_y": 0.06, "drag": (1052, 676)},
        "单字最小字": {"grid": (7, 4), "overlap_x": 0.271, "overlap_y": 0.171, "drag": (930, 616)},
    }},
} # 区域配置信息

_GUDI_COMMON_CONFIG = {"16:9": {
    "全名最小字": {"grid": (9, 5), "overlap_x": 0.001, "overlap_y": 0.008, "drag": (905, 524)},
    "全名最大字": {"grid": (5, 3), "overlap_x": 0.325, "overlap_y": 0.15, "drag": (834, 612)},
    "单字最小字": {"grid": (5, 2), "overlap_x": 0.007, "overlap_y": 0.23, "drag": (1270, 574)},
}}

for _region in ["谷地-供能高地", "谷地-谷地通道", "谷地-源石研究园"]:
    REGION_CONFIG[_region] = _GUDI_COMMON_CONFIG    #补充谷地区域配置

REGION_CONFIG["自定义"] = {"16:9": {
    "全名最小字": {"grid": (2, 2), "overlap_x": 0.001, "overlap_y": 0.001, "drag": (905, 525)},
    "全名最大字": {"grid": (2, 2), "overlap_x": 0.001, "overlap_y": 0.002, "drag": (1235, 716)},
    "单字最小字": {"grid": (2, 2), "overlap_x": 0.001, "overlap_y": 0.040, "drag": (1276, 716)},
}}  # 自定义区域

ASPECT_RATIOS = ["16:9", "自定义"]
REGIONS = list(REGION_CONFIG.keys())


class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]


def get_client_rect(hwnd: int) -> Tuple[int, int]:
    rect = RECT()
    ctypes.windll.user32.GetClientRect(hwnd, ctypes.byref(rect))
    return rect.right - rect.left, rect.bottom - rect.top


def get_embedded_icon() -> ImageTk.PhotoImage:
    img = Image.open(io.BytesIO(base64.b64decode(ICON_DATA)))
    return ImageTk.PhotoImage(img)


def rand_delay(base: float) -> float:
    return base * random.uniform(0.9, 1.1)


def validate_number(value: str, name: str, range_key: str) -> Tuple[bool, Any, str]:
    try:
        num = float(value)
        min_val, max_val = VALIDATION_RANGES[range_key]
        if not (min_val < num < max_val):
            return False, None, f"{name}必须在{min_val}到{max_val}之间"
        return True, num, ""
    except ValueError:
        return False, None, "请输入有效的数值"


def save_image(img: Image.Image, path: str, fmt: str) -> None:
    if fmt == "PNG":
        img.save(path, 'PNG')
    else:
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        img.save(path, 'JPEG', quality=95)


class GameScreenshotTool:
    def __init__(self, log_callback: Optional[Callable] = None):
        self.__dict__.update(CONFIG)
        self.output_folder = os.path.join(CONFIG["output_folder"], "screenshots")
        self.log_callback = log_callback
        self._running_lock = threading.Lock()
        self._is_running = False
        self.screenshots: List[Dict] = []
        self.game_window = None
        self.grid_size: Optional[Tuple[int, int]] = None
        self.aspect_ratio = DEFAULT_ASPECT_RATIO
        self.scroll_mode = DEFAULT_SCROLL_MODE
        self.current_region = REGIONS[0]
        self.drag_distance = self._get_drag_distance()
        self.custom_overlap_x = 0.01    # 自定义区域默认重叠x轴
        self.custom_overlap_y = 0.01    # 自定义区域默认重叠y轴

    @property
    def is_running(self) -> bool:
        with self._running_lock:
            return self._is_running

    @is_running.setter
    def is_running(self, value: bool) -> None:
        with self._running_lock:
            self._is_running = value

    def log(self, msg: str) -> None:
        if self.log_callback:
            self.log_callback(msg)
        else:
            print(msg)

    def _get_region_config(self, region_name: Optional[str] = None) -> Optional[Dict]:
        region = region_name or self.current_region
        if region and region in REGION_CONFIG:
            region_data = REGION_CONFIG.get(region)
            aspect_ratio = DEFAULT_ASPECT_RATIO if self.aspect_ratio == "自定义" else self.aspect_ratio
            aspect_data = region_data.get(aspect_ratio, region_data.get(DEFAULT_ASPECT_RATIO))
            if aspect_data and self.scroll_mode in aspect_data:
                return aspect_data[self.scroll_mode]
        return None

    def _get_drag_distance(self, region_name: Optional[str] = None) -> Tuple[int, int]:
        config = self._get_region_config(region_name)
        return config.get("drag", (0, 0)) if config else (0, 0)

    def _get_overlap(self, region_name: Optional[str] = None) -> Tuple[float, float]:
        if self.aspect_ratio == "自定义":
            return self.custom_overlap_x, self.custom_overlap_y
        config = self._get_region_config(region_name)
        if config:
            return config.get("overlap_x", 0.01), config.get("overlap_y", 0.01)
        return 0.01, 0.01

    def set_aspect_ratio(self, aspect_ratio: str) -> None:
        if aspect_ratio in ASPECT_RATIOS:
            self.aspect_ratio = aspect_ratio
            self.drag_distance = self._get_drag_distance(self.current_region)

    def set_scroll_mode(self, scroll_mode: str) -> None:
        if scroll_mode in SCROLL_MODES:
            self.scroll_mode = scroll_mode
            self.drag_distance = self._get_drag_distance(self.current_region)

    def get_grid_size(self, region_name: str) -> Optional[Tuple[int, int]]:
        if self.aspect_ratio == "自定义":
            return None
        config = self._get_region_config(region_name)
        return config.get("grid") if config else None

    def find_game_window(self):
        if self.game_window:
            try:
                _ = self.game_window.title
                return self.game_window
            except Exception:
                self.game_window = None
        windows = gw.getWindowsWithTitle("Endfield")    # 仅查找Endfield窗口
        if not windows:
            windows = gw.getAllWindows()
        for w in windows:
            if "Endfield".lower() in w.title.lower():
                self.game_window = w
                return self.game_window
        return None

    def _get_window_client_rect(self) -> Tuple[int, int, int, int]:
        win = self.game_window
        client_w, client_h = get_client_rect(win._hWnd)
        border_x = (win.width - client_w) // 2
        border_y = win.height - client_h - border_x
        return win.left + border_x, win.top + border_y, client_w, client_h

    def setup_window(self) -> bool:
        if self.game_window:
            self.game_window.activate()
            ctypes.windll.user32.SetWindowPos(
                self.game_window._hWnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002
            )
            time.sleep(1.5)
        return bool(self.game_window)

    def do_scroll(self) -> None:
        scroll_count = SCROLL_MODES.get(self.scroll_mode, {}).get("scroll_count", 0)
        if scroll_count <= 0:
            self.log("跳过滚轮滚动")
            return
        self.log(f"执行滚轮滚动: 向下滚动 {scroll_count} 次")
        client_left, client_top, client_w, client_h = self._get_window_client_rect()
        center_x = client_left + client_w // 2
        center_y = client_top + client_h // 2
        pyautogui.moveTo(center_x, center_y, duration=0.1)
        time.sleep(0.1)
        for _ in range(scroll_count):
            if not self.is_running:
                return
            pyautogui.scroll(-120, x=center_x, y=center_y)
            time.sleep(0.15)
        time.sleep(0.5)
        margin = self.drag_margin
        start_x = self.game_window.left + margin
        start_y = self.game_window.top + margin
        end_x, end_y = start_x + 300, start_y + 300
        self.log("拖拽画面刷新...")
        pyautogui.moveTo(end_x, end_y, duration=0.05)
        pyautogui.mouseDown(button='middle')
        pyautogui.moveTo(start_x, start_y, duration=0.05)
        pyautogui.moveTo(end_x, end_y, duration=0.05)
        pyautogui.mouseUp(button='middle')
        time.sleep(0.05)
        self.log("滚轮滚动完成")

    def capture_center_region(self) -> Image.Image:
        client_left, client_top, client_w, client_h = self._get_window_client_rect()
        region_size = int(client_w * self.capture_region_x), int(client_h * self.capture_region_y)
        offset_y = int(client_h * self.capture_offset_y)
        region_pos = (
            client_left + (client_w - region_size[0]) // 2,
            client_top + (client_h - region_size[1]) // 2 + offset_y,
        )
        return pyautogui.screenshot(region=(*region_pos, *region_size))

    def move_camera(self, direction: str) -> None:
        if not self.game_window or direction not in ('right', 'left', 'down'):
            return
        margin = self.drag_margin
        dx, dy = self.drag_distance
        client_left, client_top, client_w, client_h = self._get_window_client_rect()
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
        pyautogui.moveTo(start_x, start_y, duration=0.05)
        pyautogui.mouseDown(button='middle')
        pyautogui.moveTo(end_x, end_y, duration=self.drag_duration)
        pyautogui.mouseUp(button='middle')
        time.sleep(rand_delay(0.1 + self.stabilize_delay))

    def auto_capture_grid(self) -> bool:
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
                time.sleep(rand_delay(self.screenshot_delay))
                self.screenshots.append({'img': self.capture_center_region(), 'pos': (row, col)})
                if idx < cols - 1:
                    self.move_camera('right' if is_even_row else 'left')
            if row < rows - 1:
                self.move_camera('down')
        self.log(f"完成 {len(self.screenshots)} 张截图")
        return True

    def stitch_images(self) -> None:
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
        for info in self.screenshots:
            pos = info['pos'][1] * step[0], info['pos'][0] * step[1]
            result.paste(info['img'], pos)
        self.screenshots.clear()
        os.makedirs(self.output_folder, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        mode_suffix = f"_{self.scroll_mode}" if self.scroll_mode != DEFAULT_SCROLL_MODE else ""
        ext = "jpg" if self.output_format == "JPG" else self.output_format.lower()
        output_path = os.path.join(self.output_folder, f"stitched_{timestamp}{mode_suffix}.{ext}")
        save_image(result, output_path, self.output_format)
        self.log(f"拼接完成：{output_path}")

    def start_capture(self, region_name: str, rows: Optional[int] = None, cols: Optional[int] = None) -> None:
        if self.is_running:
            return self.log("已在运行中")
        self.current_region = region_name
        if self.aspect_ratio != "自定义":
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

    def _capture_thread(self) -> None:
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

    def stop(self) -> None:
        if self.is_running:
            self.is_running = False
            self.log("已停止截图")

    def manual_screenshot(self) -> None:
        if self.is_running:
            return self.log("自动截图进行中，无法手动截图")
        if not self.find_game_window():
            return self.log("未找到终末地窗口")
        self.game_window.activate()
        time.sleep(0.5)
        screenshot_img = self.capture_center_region()
        os.makedirs(self.output_folder, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = "jpg" if self.output_format == "JPG" else self.output_format.lower()
        screenshot_path = os.path.join(self.output_folder, f"manual_{timestamp}.{ext}")
        save_image(screenshot_img, screenshot_path, self.output_format)
        self.log(f"已保存：{screenshot_path}")


class ScreenshotGUI:
    VERSION = "v2.3.0"
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
        self._setup_ui()
        self._setup_hotkeys()

    def _setup_dpi_scaling(self) -> None:
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

    def _setup_ui(self) -> None:
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(main_frame, text=f"{self.WINDOW_TITLE}{self.VERSION}", font=("Microsoft YaHei", 14, "bold")).pack(pady=(0, 10))
        self._setup_config_frame(main_frame)
        self._setup_region_frame(main_frame)
        self._setup_buttons(main_frame)
        self._setup_log_frame(main_frame)
        self._setup_hint(main_frame)

    def _create_entry(self, parent: ttk.Frame, width: int, state: str = tk.DISABLED) -> ttk.Entry:
        entry = ttk.Entry(parent, width=width, state=state)
        entry.pack(side=tk.LEFT, padx=3)
        return entry

    def _update_entry(self, entry: ttk.Entry, value: Any, keep_editable: bool = False) -> None:
        entry.config(state=tk.NORMAL)
        entry.delete(0, tk.END)
        entry.insert(0, str(value))
        if not keep_editable:
            entry.config(state=tk.DISABLED)

    def _setup_config_frame(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="配置信息", padding="5")
        frame.pack(fill=tk.X, pady=1)
        row1 = ttk.Frame(frame)
        row1.pack(fill=tk.X)
        ttk.Label(row1, text="比例:").pack(side=tk.LEFT)
        self.aspect_ratio_var = tk.StringVar(value=self.tool.aspect_ratio)
        self.aspect_ratio_combo = ttk.Combobox(row1, textvariable=self.aspect_ratio_var, values=ASPECT_RATIOS, state="readonly", width=5)
        self.aspect_ratio_combo.pack(side=tk.LEFT, padx=5)
        self.aspect_ratio_combo.bind("<<ComboboxSelected>>", self._on_aspect_ratio_change)
        ttk.Label(row1, text="拖拽距离:").pack(side=tk.LEFT, padx=(10, 0))
        self.drag_x_entry = self._create_entry(row1, 5)
        ttk.Label(row1, text="x").pack(side=tk.LEFT)
        self.drag_y_entry = self._create_entry(row1, 5)
        ttk.Label(row1, text="重叠率:").pack(side=tk.LEFT, padx=(10, 0))
        self.overlap_x_entry = self._create_entry(row1, 5)
        ttk.Label(row1, text="x").pack(side=tk.LEFT)
        self.overlap_y_entry = self._create_entry(row1, 5)
        ttk.Label(row1, text="%").pack(side=tk.LEFT)
        self._update_drag_display()
        self._update_overlap_display()
        row2 = ttk.Frame(frame)
        row2.pack(fill=tk.X, pady=(5, 0))
        self.scroll_mode_var = tk.StringVar(value=self.tool.scroll_mode)
        center_frame = ttk.Frame(row2)
        center_frame.pack(expand=True)
        self.scroll_mode_radios = []
        for mode in SCROLL_MODES:
            rb = ttk.Radiobutton(center_frame, text=mode, value=mode, variable=self.scroll_mode_var, command=self._on_scroll_mode_change)
            rb.pack(side=tk.LEFT, padx=10)
            self.scroll_mode_radios.append(rb)
        ttk.Label(center_frame, text="输出格式: ").pack(side=tk.LEFT, padx=(20, 0))
        self.output_format_var = tk.StringVar(value=self.tool.output_format)
        self.output_format_combo = ttk.Combobox(center_frame, textvariable=self.output_format_var, values=["JPG", "PNG"], state="readonly", width=5)
        self.output_format_combo.pack(side=tk.LEFT)
        self.output_format_combo.bind("<<ComboboxSelected>>", self._on_output_format_change)

    def _setup_region_frame(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="截图区域", padding="5")
        frame.pack(fill=tk.X, pady=1)
        ttk.Label(frame, text="区域:").pack(side=tk.LEFT)
        self.region_var = tk.StringVar(value=REGIONS[0])
        self.region_combo = ttk.Combobox(frame, textvariable=self.region_var, values=REGIONS, state="readonly", width=12)
        self.region_combo.pack(side=tk.LEFT, padx=5)
        self.region_combo.bind("<<ComboboxSelected>>", self._on_region_change)
        ttk.Label(frame, text="行:").pack(side=tk.LEFT, padx=(10, 0))
        self.rows_entry = self._create_entry(frame, 4)
        ttk.Label(frame, text="列:").pack(side=tk.LEFT, padx=(5, 0))
        self.cols_entry = self._create_entry(frame, 4)
        ttk.Label(frame, text="宽:").pack(side=tk.LEFT, padx=(10, 0))
        self.capture_region_x_entry = self._create_entry(frame, 5)
        ttk.Label(frame, text="高:").pack(side=tk.LEFT, padx=(5, 0))
        self.capture_region_y_entry = self._create_entry(frame, 5)
        ttk.Label(frame, text="%").pack(side=tk.LEFT)
        self._update_grid_display()
        self._update_capture_region_display()

    def _setup_buttons(self, parent: ttk.Frame) -> None:
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        buttons = [("开始截图 (F1)", self._start_capture), ("停止 (F2)", self._stop_capture), ("手动截图 (F3)", self._manual_capture), ("退出 (F4)", self._exit_app)]
        for text, cmd in buttons:
            ttk.Button(frame, text=text, command=cmd, width=13).pack(side=tk.LEFT, padx=5)

    def _setup_log_frame(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="日志", padding="5")
        frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.log_text = scrolledtext.ScrolledText(frame, height=8, width=50, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _setup_hint(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="进入俯瞰批量选择模式，视野拉到最小并移到左上角使用，截图请勿移动鼠标", foreground="gray").pack(pady=1)

    def _get_current_region(self) -> str:
        return self.region_var.get() if hasattr(self, 'region_var') else REGIONS[0]

    def _update_drag_display(self, keep_editable: bool = False) -> None:
        drag = self.tool._get_drag_distance(self._get_current_region())
        dx, dy = drag or (0, 0)
        is_custom_aspect = hasattr(self, 'aspect_ratio_var') and self.aspect_ratio_var.get() == "自定义"
        final_keep_editable = keep_editable or is_custom_aspect
        self._update_entry(self.drag_x_entry, dx, final_keep_editable)
        self._update_entry(self.drag_y_entry, dy, final_keep_editable)

    def _update_overlap_display(self) -> None:
        overlap_x, overlap_y = self.tool._get_overlap(self._get_current_region())
        is_custom_aspect = hasattr(self, 'aspect_ratio_var') and self.aspect_ratio_var.get() == "自定义"
        self._update_entry(self.overlap_x_entry, f"{overlap_x * 100:.1f}", keep_editable=is_custom_aspect)
        self._update_entry(self.overlap_y_entry, f"{overlap_y * 100:.1f}", keep_editable=is_custom_aspect)

    def _update_capture_region_display(self) -> None:
        is_custom_aspect = hasattr(self, 'aspect_ratio_var') and self.aspect_ratio_var.get() == "自定义"
        self._update_entry(self.capture_region_x_entry, f"{self.tool.capture_region_x * 100:.1f}", keep_editable=is_custom_aspect)
        self._update_entry(self.capture_region_y_entry, f"{self.tool.capture_region_y * 100:.1f}", keep_editable=is_custom_aspect)

    def _update_grid_display(self) -> None:
        grid_size = self.tool.get_grid_size(self._get_current_region())
        if grid_size:
            is_custom_region = hasattr(self, 'region_var') and self.region_var.get() == "自定义"
            self._update_entry(self.rows_entry, grid_size[0], keep_editable=is_custom_region)
            self._update_entry(self.cols_entry, grid_size[1], keep_editable=is_custom_region)

    def _on_region_change(self, event=None) -> None:
        is_custom = self.region_var.get() == "自定义"
        state = tk.NORMAL if is_custom else tk.DISABLED
        self.rows_entry.config(state=state)
        self.cols_entry.config(state=state)
        self._update_grid_display()
        self._update_drag_display()
        self._update_overlap_display()

    def _on_scroll_mode_change(self, event=None) -> None:
        self.tool.set_scroll_mode(self.scroll_mode_var.get())
        self._update_drag_display()
        self._update_overlap_display()
        self._update_grid_display()

    def _on_output_format_change(self, event=None) -> None:
        self.tool.output_format = self.output_format_var.get()

    def _on_aspect_ratio_change(self, event=None) -> None:
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
            self._update_drag_display()
            self._update_overlap_display()
            self._update_capture_region_display()
            self._update_grid_display()

    def _validate_custom_params(self) -> bool:
        try:
            drag_x = int(self.drag_x_entry.get())
            drag_y = int(self.drag_y_entry.get())
            if drag_x <= 0 or drag_y <= 0:
                messagebox.showerror("错误", "拖拽距离必须大于0")
                return False
            self.tool.drag_distance = (drag_x, drag_y)
            valid, overlap_x, err = validate_number(self.overlap_x_entry.get(), "重叠率X", "overlap")
            if not valid:
                messagebox.showerror("错误", err)
                return False
            valid, overlap_y, err = validate_number(self.overlap_y_entry.get(), "重叠率Y", "overlap")
            if not valid:
                messagebox.showerror("错误", err)
                return False
            self.tool.custom_overlap_x = overlap_x / 100
            self.tool.custom_overlap_y = overlap_y / 100
            valid, capture_x, err = validate_number(self.capture_region_x_entry.get(), "截图区域宽度", "capture_region")
            if not valid:
                messagebox.showerror("错误", err)
                return False
            valid, capture_y, err = validate_number(self.capture_region_y_entry.get(), "截图区域高度", "capture_region")
            if not valid:
                messagebox.showerror("错误", err)
                return False
            self.tool.capture_region_x = capture_x / 100
            self.tool.capture_region_y = capture_y / 100
            return True
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数值")
            return False

    def _start_capture(self) -> None:
        region = self.region_var.get()
        custom_rows = custom_cols = None
        if region == "自定义":
            try:
                custom_rows = int(self.rows_entry.get())
                custom_cols = int(self.cols_entry.get())
                if custom_rows <= 0 or custom_cols <= 0:
                    return messagebox.showerror("错误", "行列数必须大于0")
                if custom_rows > 100 or custom_cols > 100:
                    return messagebox.showerror("错误", f"行列数最大为100")
            except ValueError:
                return messagebox.showerror("错误", "请输入有效的数字")
            if not self._validate_custom_params():
                return
        if self.aspect_ratio_var.get() == "自定义" and not self._validate_custom_params():
            return
        self.tool.start_capture(region, custom_rows, custom_cols)

    def _stop_capture(self) -> None:
        self.tool.stop()

    def _manual_capture(self) -> None:
        self.tool.manual_screenshot()

    def _exit_app(self) -> None:
        self.tool.is_running = False
        self.root.quit()

    def append_log(self, msg: str) -> None:
        def _append():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"[{datetime.now():%H:%M:%S}] {msg}\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        self.root.after(0, _append)

    def _setup_hotkeys(self) -> None:
        hotkeys = {"F1": self._start_capture, "F2": self._stop_capture, "F3": self._manual_capture, "F4": self._exit_app}
        for key, action in hotkeys.items():
            keyboard.add_hotkey(key, lambda a=action: self.root.after(0, a))

    def run(self) -> None:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit(0)
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        self._on_region_change()
        startup_msgs = ["=" * 45, "程序已启动", f"输出目录: {self.tool.output_folder}", "=" * 45, "使用说明：", "1. 确保分辨率16:9将画面缩到最小并移到左上角", "2. 选择截图地区后点击按钮或F1开始", "3. 可自定义截图变量及点击F3截取单张画面", "=" * 45]
        for msg in startup_msgs:
            self.append_log(msg)
        self.root.mainloop()


if __name__ == "__main__":
    ScreenshotGUI().run()
