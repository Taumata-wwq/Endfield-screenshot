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


HWND_TOPMOST = -1
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SET_WINDOW_POS_FLAGS = SWP_NOSIZE | SWP_NOMOVE
RAND_DELAY_MIN = 0.9
RAND_DELAY_MAX = 1.1


CONFIG = {
    "stabilize_delay": 0.05,           # 拖拽后等待画面稳定的时间(秒)
    "screenshot_delay": 0.01,          # 截图前的等待时间(秒)
    "capture_region": 0.62,            # 截图区域比例（相对于窗口宽高）
    "capture_offset_y": 0.02,          # 截图区域垂直偏移（正数向下）
    "drag_margin": 40,                 # 拖拽操作距离窗口边缘的像素距离
    "drag_duration": 0.01,             # 拖拽动作持续时间(秒)
    "output_folder": os.path.join(get_base_path(), "screenshots"),  # 截图输出目录
}

SCROLL_MODES = {"全名最小字": {"scroll_count": 0}, "全名最大字": {"scroll_count": 5}, "单字最小字": {"scroll_count": 6}}

REGION_CONFIG = {
    "武陵-武陵城": {
        "16:9": {
            "全名最小字": {"grid": (15, 9), "overlap_x": 0.09, "overlap_y": 0.01, "drag": (825, 520)},
            "全名最大字": {"grid": (8, 4), "overlap_x": 0.001, "overlap_y": 0.105, "drag": (1230, 640)},
            "单字最小字": {"grid": (7, 4), "overlap_x": 0.16, "overlap_y": 0.09, "drag": (1070, 675)},
        },
    },
    "武陵-景玉谷": {
        "16:9": {
            "全名最小字": {"grid": (10, 6), "overlap_x": 0.001, "overlap_y": 0.01, "drag": (900, 520)},
            "全名最大字": {"grid": (6, 3), "overlap_x": 0.105, "overlap_y": 0.165, "drag": (1100, 600)},
            "单字最小字": {"grid": (5, 3), "overlap_x": 0.262, "overlap_y": 0.09, "drag": (940, 675)},
        },
    },
    "谷地-枢纽区": {
        "16:9": {
            "全名最小字": {"grid": (13, 8), "overlap_x": 0.06, "overlap_y": 0.01, "drag": (850, 520)},
            "全名最大字": {"grid": (7, 4), "overlap_x": 0.147, "overlap_y": 0.06, "drag": (1050, 675)},
            "单字最小字": {"grid": (7, 4), "overlap_x": 0.271, "overlap_y": 0.171, "drag": (930, 615)},
        },
    },
    "谷地-供能高地": {
        "16:9": {
            "全名最小字": {"grid": (9, 5), "overlap_x": 0.001, "overlap_y": 0.008, "drag": (900, 520)},
            "全名最大字": {"grid": (5, 3), "overlap_x": 0.325, "overlap_y": 0.15, "drag": (830, 610)},
            "单字最小字": {"grid": (5, 2), "overlap_x": 0.03, "overlap_y": 0.23, "drag": (1239, 575)},
        },
    },
    "谷地-谷地通道": {
        "16:9": {
            "全名最小字": {"grid": (9, 5), "overlap_x": 0.001, "overlap_y": 0.008, "drag": (900, 520)},
            "全名最大字": {"grid": (5, 3), "overlap_x": 0.325, "overlap_y": 0.15, "drag": (830, 610)},
            "单字最小字": {"grid": (5, 2), "overlap_x": 0.03, "overlap_y": 0.23, "drag": (1239, 575)},
        },
    },
    "谷地-源石研究园": {
        "16:9": {
            "全名最小字": {"grid": (9, 5), "overlap_x": 0.001, "overlap_y": 0.008, "drag": (900, 520)},
            "全名最大字": {"grid": (5, 3), "overlap_x": 0.325, "overlap_y": 0.15, "drag": (830, 610)},
            "单字最小字": {"grid": (5, 2), "overlap_x": 0.03, "overlap_y": 0.23, "drag": (1239, 575)},
        },
    },
}

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
        if region_name == "自定义":
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
                self.game_window._hWnd, HWND_TOPMOST, 0, 0, 0, 0, SET_WINDOW_POS_FLAGS
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
            pyautogui.scroll(-120, x=center_x, y=center_y)
            time.sleep(0.15)
        
        time.sleep(0.5)
        
        margin = self.drag_margin
        start_x = self.game_window.left + margin
        start_y = self.game_window.top + margin
        end_x = start_x + 300
        end_y = start_y + 300
        
        self.log("拖拽画面刷新...")
        pyautogui.moveTo(end_x, end_y, duration=0.1)
        time.sleep(0.01)
        pyautogui.mouseDown(button='middle')
        time.sleep(0.01)
        pyautogui.moveTo(start_x, start_y, duration=0.3)
        time.sleep(0.01)
        pyautogui.moveTo(end_x, end_y, duration=0.3)
        time.sleep(0.01)
        pyautogui.mouseUp(button='middle')
        time.sleep(0.05)
        
        self.log("滚轮滚动完成")

    def capture_center_region(self):
        w, h = self.game_window.width, self.game_window.height
        region_size = int(w * self.capture_region), int(h * self.capture_region)
        offset_y = int(h * self.capture_offset_y)
        region_pos = (
            self.game_window.left + (w - region_size[0]) // 2,
            self.game_window.top + (h - region_size[1]) // 2 + offset_y,
        )
        return pyautogui.screenshot(region=(*region_pos, *region_size))

    def move_camera(self, direction):
        if not self.game_window or direction not in ('right', 'left', 'down'):
            return
        win, margin = self.game_window, self.drag_margin
        dx, dy = self.drag_distance
        base_x, base_y = win.left + margin, win.top + margin
        drag_x, drag_y = win.left + dx + margin, win.top + dy + margin
        
        if direction == 'right':
            start_x, start_y, end_x, end_y = drag_x, base_y, base_x, base_y
        elif direction == 'left':
            start_x, start_y, end_x, end_y = base_x, base_y, drag_x, base_y
        else:
            start_x, start_y, end_x, end_y = base_x, drag_y, base_x, base_y
        
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
        output_path = os.path.join(self.output_folder, f"stitched_{timestamp}{mode_suffix}.jpg")
        result.save(output_path, 'JPEG', quality=95)
        self.log(f"拼接完成：{output_path}")

    def start_capture(self, region_name, rows=None, cols=None):
        if self.is_running:
            return self.log("已在运行中")
        
        self.current_region = region_name
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
        screenshot_path = os.path.join(self.output_folder, f"manual_{timestamp}.jpg")
        screenshot_img.save(screenshot_path, 'JPEG', quality=95)
        self.log(f"已保存：{screenshot_path}")


class ScreenshotGUI:
    VERSION = "v1.0.0"
    WINDOW_TITLE = "终末地截图工具"
    WINDOW_SIZE = "520x470"
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{self.WINDOW_TITLE}{self.VERSION}")
        self.root.geometry(self.WINDOW_SIZE)
        self.root.resizable(False, False)
        self.tool = GameScreenshotTool(log_callback=self.append_log)
        self.setup_ui()
        self.setup_hotkeys()

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

    def _setup_region_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="截图区域", padding="5")
        frame.pack(fill=tk.X, pady=1)
        
        ttk.Label(frame, text="区域:").pack(side=tk.LEFT)
        self.region_var = tk.StringVar(value="武陵-武陵城")
        self.region_combo = ttk.Combobox(
            frame, textvariable=self.region_var,
            values=REGIONS, state="readonly", width=20
        )
        self.region_combo.pack(side=tk.LEFT, padx=5)
        self.region_combo.bind("<<ComboboxSelected>>", self.on_region_change)
        
        ttk.Label(frame, text="行:").pack(side=tk.LEFT, padx=(10, 0))
        self.rows_entry = self._create_entry(frame, 4)
        ttk.Label(frame, text="列:").pack(side=tk.LEFT, padx=(5, 0))
        self.cols_entry = self._create_entry(frame, 4)
        
        ttk.Label(frame, text="大小:").pack(side=tk.LEFT, padx=(10, 0))
        self.capture_region_entry = self._create_entry(frame, 5)
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
            text="打开游戏进入俯瞰批量选择模式使用，截图时请勿移动鼠标",
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

    def on_aspect_ratio_change(self, event=None):
        aspect_ratio = self.aspect_ratio_var.get()
        is_custom = aspect_ratio == "自定义"
        state = tk.NORMAL if is_custom else tk.DISABLED
        
        for entry in [self.drag_x_entry, self.drag_y_entry, self.overlap_x_entry, self.overlap_y_entry, self.capture_region_entry]:
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
            self._update_entry(self.capture_region_entry, f"{self.tool.capture_region * 100:.1f}", keep_editable=True)
        else:
            self.tool.set_aspect_ratio(aspect_ratio)
            self.update_drag_display()
            self.update_overlap_display()
            self.update_capture_region_display()
            self.update_grid_display()

    def update_drag_display(self, keep_editable=False):
        region = self.region_var.get() if hasattr(self, 'region_var') else REGIONS[0]
        drag = self.tool._get_drag_distance(region)
        dx, dy = drag or (0, 0)
        self._update_entry(self.drag_x_entry, dx, keep_editable=keep_editable)
        self._update_entry(self.drag_y_entry, dy, keep_editable=keep_editable)

    def update_overlap_display(self):
        region = self.region_var.get() if hasattr(self, 'region_var') else REGIONS[0]
        overlap_x, overlap_y = self.tool._get_overlap(region)
        self._update_entry(self.overlap_x_entry, f"{overlap_x * 100:.1f}")
        self._update_entry(self.overlap_y_entry, f"{overlap_y * 100:.1f}")

    def update_capture_region_display(self):
        self._update_entry(self.capture_region_entry, f"{self.tool.capture_region * 100:.1f}")

    def update_grid_display(self):
        if not hasattr(self, 'region_var'):
            return
        grid_size = self.tool.get_grid_size(self.region_var.get())
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
            
            capture_region = float(self.capture_region_entry.get())
            if not (0 < capture_region < 100):
                messagebox.showerror("错误", "截图区域比例必须在0到100之间")
                return False
            self.tool.capture_region = capture_region / 100
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
