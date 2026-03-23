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

DEFAULT_CONFIG = {
    "grid_size": [],                      # 网格大小 [行数, 列数]，由用户选择或自定义
    "stabilize_delay": 0.08,              # 拖拽后等待画面稳定的时间(秒)
    "screenshot_delay": 0.08,             # 截图前的等待时间(秒)
    "move_step": 1,                       # 每次移动的步数
    "capture_region_x": 0.62,             # 截图区域宽度占窗口比例
    "capture_region_y": 0.62,             # 截图区域高度占窗口比例
    "overlap_x": 0.005,                   # 水平方向拼接重叠率
    "overlap_y": 0.010,                   # 垂直方向拼接重叠率
    "drag_margin": 40,                    # 拖拽操作距离窗口边缘的像素距离
    "drag_duration": 0.08,                # 拖拽动作持续时间(秒)
    "output_folder": os.path.join(os.path.dirname(__file__), "screenshots"), # 输出目录
    "hotkeys": {"start": "F1", "stop": "F2", "exit": "F4", "manual": "F3"}   # 快捷键配置
}

PRESET_REGIONS = {
    "1": {"name": "武陵-武陵城", "grid_size": [14, 8]},
    "2": {"name": "武陵-景玉谷", "grid_size": [10, 6]},
    "3": {"name": "谷地-枢纽区", "grid_size": [13, 7]},
    "4": {"name": "谷地-谷地通道", "grid_size": [9, 5]},
    "5": {"name": "谷地-供能高地", "grid_size": [9, 5]},
    "6": {"name": "谷地-源石研究园", "grid_size": [9, 5]}
}


class GameScreenshotTool:
    def __init__(self):
        self.config = DEFAULT_CONFIG.copy()
        for k, v in self.config.items():
            setattr(self, k, v)
        self.is_running = False
        self.screenshots = []
        self.game_window = None

    def rand_delay(self, base, jitter=0.1):
        return base + random.uniform(-jitter, jitter) * base

    def request_admin(self):
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("请求管理员权限...")
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            return False
        return True

    def find_game_window(self):
        if self.game_window:
            return self.game_window
        for window in gw.getWindowsWithTitle('Endfield') or gw.getAllWindows():
            if 'endfield' in window.title.lower():
                self.game_window = window
                return window
        return None

    def setup_window(self):
        if not self.game_window:
            return False
        self.game_window.activate()
        ctypes.windll.user32.SetWindowPos(self.game_window._hWnd, -1, 0, 0, 0, 0, 0x0002 | 0x0001)
        time.sleep(1.5)
        return True

    def capture_center_region(self, window):
        if not window:
            return None
        rw, rh = int(window.width * self.capture_region_x), int(window.height * self.capture_region_y)
        rx, ry = window.left + (window.width - rw) // 2, window.top + (window.height - rh) // 2
        return pyautogui.screenshot(region=(rx, ry, rw, rh)), (rx, ry, rw, rh)

    def move_camera(self, direction, step_count=1):
        if not self.game_window or direction not in ['down', 'left', 'right']:
            return
        
        w = self.game_window
        m = self.drag_margin
        f = 0.7
        offsets = {
            'right': ((w.left + int(w.width * f) + m, w.top + m), (w.left + m, w.top + m)),
            'left': ((w.left + m, w.top + m), (w.left + int(w.width * f) + m, w.top + m)),
            'down': ((w.left + m, w.top + int(w.height * f) + m), (w.left + m, w.top + m))
        }
        
        start, end = offsets[direction]
        for _ in range(step_count):
            pyautogui.moveTo(*start, duration=0.1)
            time.sleep(self.rand_delay(0.05))
            pyautogui.mouseDown(button='middle')
            time.sleep(self.rand_delay(0.1))
            pyautogui.moveTo(*end, duration=self.drag_duration)
            time.sleep(self.rand_delay(0.1))
            pyautogui.mouseUp(button='middle')
            time.sleep(self.rand_delay(0.1))
        time.sleep(self.rand_delay(self.stabilize_delay))

    def auto_capture_grid(self):
        print("=" * 50)
        print("开始自动截图...")
        self.screenshots = []
        
        if not self.find_game_window():
            print("=" * 50)
            print("未找到终末地窗口！")
            return False
        
        if not self.setup_window():
            return False
        
        for row in range(self.grid_size[0]):
            cols = range(self.grid_size[1]) if row % 2 == 0 else range(self.grid_size[1] - 1, -1, -1)
            for idx, col in enumerate(cols):
                if not self.is_running:
                    return False
                print(f"正在拍摄位置 ({row}, {col})...")
                time.sleep(self.rand_delay(self.screenshot_delay))
                img, region = self.capture_center_region(self.game_window)
                if img:
                    self.screenshots.append({'image': img, 'position': (row, col), 'region': region})
                if idx < len(cols) - 1:
                    self.move_camera('right' if row % 2 == 0 else 'left', self.move_step)
            if row < self.grid_size[0] - 1:
                self.move_camera('down', self.move_step)
        
        print(f"完成 {len(self.screenshots)} 张截图")
        return True

    def stitch_images(self, output_path=None):
        if not self.screenshots:
            print("=" * 50)
            print("没有截图可拼接")
            return None
        
        img = self.screenshots[0]['image']
        w, h = img.size
        ox, oy = int(w * self.overlap_x), int(h * self.overlap_y)
        sx, sy = w - ox, h - oy
        
        total_w, total_h = sx * self.grid_size[1] + ox, sy * self.grid_size[0] + oy
        result = Image.new('RGB', (total_w, total_h), (0, 0, 0))
        
        for info in sorted(self.screenshots, key=lambda x: x['position']):
            result.paste(info['image'], (info['position'][1] * sx, info['position'][0] * sy))
        
        if output_path is None:
            output_path = os.path.join(self.output_folder, f"stitched_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        result.save(output_path, 'JPEG', quality=95)
        print("=" * 50)
        print(f"拼接完成，已保存到：{output_path}")
        return result

    def select_region(self):
        print("=" * 50)
        print("请选择截图区域：")
        for key, value in PRESET_REGIONS.items():
            print(f"  {key}. {value['name']} ({value['grid_size'][0]} x {value['grid_size'][1]})")
        print(f"  0. 自定义网格大小")
        
        while self.is_running:
            try:
                choice = input("请输入选项：").strip()
                if choice in PRESET_REGIONS:
                    region = PRESET_REGIONS[choice]
                    self.grid_size = region["grid_size"]
                    print("=" * 50)
                    print(f"已选择：{region['name']}，网格大小：{region['grid_size'][0]} x {region['grid_size'][1]}")
                    return True
                elif choice == "0":
                    rows = input("请输入行数：").strip()
                    cols = input("请输入列数：").strip()
                    if not rows.isdigit() or not cols.isdigit():
                        print("输入无效，请输入数字")
                        continue
                    rows, cols = int(rows), int(cols)
                    if rows <= 0 or cols <= 0:
                        print("行数和列数必须大于 0，请重新选择")
                        continue
                    self.grid_size = [rows, cols]
                    print("=" * 50)
                    print(f"已选择：自定义模式，网格大小：{rows} x {cols}")
                    return True
                else:
                    print("=" * 50)
                    print("输入无效，请重新输入")
            except Exception as e:
                print(f"输入错误：{e}")
                return False
        return False

    def start_auto_capture(self):
        if self.is_running:
            print("=" * 50)
            print("已在运行中")
            return
        
        threading.Thread(target=self._capture_with_setup, daemon=True).start()
    
    def _capture_with_setup(self):
        self.is_running = True
        if not self.select_region():
            self.is_running = False
            return
        
        if not self.find_game_window():
            print("=" * 50)
            print("未找到终末地窗口，请先打开游戏")
            self.is_running = False
            return
        
        print("=" * 50)
        print(f"找到终末地窗口：{self.game_window.title}")
        try:
            if self.auto_capture_grid():
                print("=" * 50)
                print("开始拼接图片...")
                self.stitch_images()
                print("=" * 50)
                print("拼接完成，可按 F1 F3 截图 或 ESC 退出")
            else:
                print("=" * 50)
                print("截图中断")
        except Exception as e:
            print("=" * 50)
            print(f"截图过程出错：{e}")
        finally:
            self.is_running = False



    def stop(self):
        if not self.is_running:
            print("=" * 50)
            print("当前未在运行")
            return
        self.is_running = False
        print("=" * 50)
        print("已停止截图")

    def manual_screenshot(self):
        if self.is_running:
            print("=" * 50)
            print("自动截图进行中，无法手动截图")
            return
        
        if not self.find_game_window():
            print("=" * 50)
            print("未找到终末地窗口")
            return
        
        self.game_window.activate()
        time.sleep(0.5)
        img, region = self.capture_center_region(self.game_window)
        if img:
            os.makedirs(self.output_folder, exist_ok=True)
            filename = f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            filepath = os.path.join(self.output_folder, filename)
            img.save(filepath, 'JPEG', quality=95)
            print("=" * 50)
            print(f"已保存截图：{filepath}")

    def setup_hotkeys(self):
        print("=" * 50)
        print("全局快捷键:")
        print(f"  {self.hotkeys['start']}: 开始自动截图")
        print(f"  {self.hotkeys['stop']}: 停止截图")
        print(f"  {self.hotkeys['manual']}: 手动截图一次")
        print(f"  {self.hotkeys['exit']}: 退出程序")
        
        keyboard.add_hotkey(self.hotkeys['start'], lambda: threading.Thread(target=self.start_auto_capture, daemon=True).start())
        keyboard.add_hotkey(self.hotkeys['stop'], self.stop)
        keyboard.add_hotkey(self.hotkeys['manual'], self.manual_screenshot)
        keyboard.add_hotkey(self.hotkeys['exit'], self._exit_program)
        keyboard.wait()
    
    def _exit_program(self):
        os._exit(0)


def main():
    print("=" * 50)
    print("终末地工业模式俯瞰模式截图拼接工具")
    print("=" * 50)
    
    tool = GameScreenshotTool()
    
    if not tool.request_admin():
        sys.exit(0)
    
    print(f"当前配置：")
    print(f"  截图区域：{tool.capture_region_x * 100:.1f}% x {tool.capture_region_y * 100:.1f}%")
    print(f"  拼接重叠率：{tool.overlap_x * 100:.1f}% x {tool.overlap_y * 100:.1f}%")
    print(f"  输出目录：{tool.output_folder}")
    print("=" * 50)
    print("提示：")
    print("1. 打开终末地设置为[1280*720窗口]并进入俯瞰状态的批量选择模式")
    print("2. 若截取全图则确保放到最大(滚轮上滚后最小视野状态)并将画面移动到最左上角")
    print(f"3. 按 {tool.hotkeys['start']} 并选择截图地区或自定义区域后开始自动截图拼接")
    print(f"4. 按 {tool.hotkeys['stop']} 停止截图")
    print(f"5. 按 {tool.hotkeys['manual']} 手动截图一次")
    print(f"6. 按 {tool.hotkeys['exit']} 退出程序")
    
    tool.setup_hotkeys()


if __name__ == "__main__":
    main()
