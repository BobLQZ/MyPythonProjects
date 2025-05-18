import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import keyboard
import time
import threading
from random import randint
import win32api
import win32con
import ctypes


def init_rows_and_cols(frame, rows, cols):
    """设置行列的大小"""
    # 自动设置行列的大小
    for row in range(rows):
        frame.grid_rowconfigure(row, weight=1, minsize=30)  # 所有行高度随窗口变化，最小高度 30px

    for col in range(cols):
        frame.grid_columnconfigure(col, weight=1, minsize=20)  # 所有列宽度随窗口变化，最小宽度 40px


def zh_trans_en_key(key):
    """键盘文字中英文转换"""
    key_zh_cn = {'左方向键': 'left', '右方向键': 'right', '上方向键': 'up', '下方向键': 'down', '空格': 'space',
                 '长按': 'hold', '连点': 'spam'}
    try:
        return key_zh_cn[key]
    except:
        value = [k for k, v in key_zh_cn.items() if v == key]
        try:
            return value[0]
        except:
            return key


def zh_trans_en_mou(mou):
    """鼠标文字中英文转换"""
    mou_zh_cn = {'左键 ': 'left', '右键': 'right', '长按': 'hold', '连点': 'spam'}
    value = [k for k, v in mou_zh_cn.items() if v == mou]
    try:
        return value[0]
    except:
        return mou


def show_about():
    """显示关于信息"""
    messagebox.showinfo("关于",
                        "键鼠模拟器 v1.0\n\n"
                        "一个高精度的键盘和鼠标操作模拟工具\n\n"
                        "特性:\n"
                        "• 支持鼠标左右键点击和长按\n"
                        "• 支持键盘按键的连点和长按\n"
                        "• 使用Win32 API实现高精度低延迟\n"
                        "• 可设置精确的时间间隔和随机波动\n\n"
                        "使用说明:\n"
                        "1. 选择需要模拟的操作类型\n"
                        "2. 设置间隔和波动参数\n"
                        "3. 点击开始或使用快捷键启动")


class SimulatorApp:
    def __init__(self, master):
        """页面初始化"""
        self.master = master
        self.master.title("SimulatorApp")
        self.master.iconbitmap('D:/Python/Project/MyPythonProjects/键鼠模拟/ico/logo.ico')
        self.master.geometry("620x440+650+320")  # 设置窗口大小和位置
        self.is_running = False
        self.is_compact = False  # 是否处于精简页面的标志
        self.master.resizable(False, False)  # 禁止水平方向和垂直方向的调整大小
        self.master.configure(padx=10, pady=10)  # 设置窗口边缘与控件之间的距离，窗口的内边距
        self.last_toggle_time = float(-1)  # 上次切换的时间

        self.default_geometry = {
            "original": "620x440",  # 原始页面大小
            "compact": "235x440",  # 精简页面大小
        }
        # 默认值
        self.default_active = 'mouse'
        self.default_mouse = 'left'
        self.default_keyboard = 'a'
        self.default_function = 'spam'
        self.default_click = '100'
        self.default_click_swings = '50'
        self.default_control = 'F12'  # 默认值为 F12

        # 控件变量
        self.action_var = tk.StringVar(value=self.default_active)
        self.mouse_button = tk.StringVar(value=self.default_mouse)
        self.selected_key = tk.StringVar(value=self.default_keyboard)
        self.function_var = tk.StringVar(value=self.default_function)
        self.click_interval = tk.StringVar(value=self.default_click)
        self.click_interval_swings = tk.StringVar(value=self.default_click_swings)
        self.control_key = tk.StringVar(value=self.default_control)

        # 键盘模拟键
        self.key_options = [chr(i) for i in range(97, 123)]  # 添加a-z字母按键
        self.key_options.extend([str(i) for i in range(0, 10)])  # 添加数字0-9按键
        self.key_options.extend(['空格', 'enter', 'tab', 'esc'])  # 常用功能键

        # 控制按键选项
        self.control_key_options = [f'F{i}' for i in range(1, 13)]  # 生成 F1 到 F12 的选项

        # 部分按键的中文初始化
        self.Radiobutton_Label = None
        self.Radiobutton_l = None
        self.Radiobutton_r = None
        self.key_combobox_Label = None
        self.key_combobox = None
        self.click_interval_entry = None
        self.click_interval_swings_entry = None
        self.start_button = None
        self.about_button = None
        self.logging_text = None

        # 创建两个 Frame
        self.control_frame = ttk.LabelFrame(self.master, text="操作设置", padding="10")  # 操作设置框
        self.logging_frame = ttk.LabelFrame(self.master, text="运行状态", padding="10")  # 日志输出框

        # 初始显示原始页面
        self.control_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.logging_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        self.master.geometry(self.default_geometry["original"])  # 设置初始大小

        # 初始化页面内容
        self.init_control_frame()
        self.init_logging_frame()

        # 默认显示鼠标按钮设置，隐藏键盘按钮设置
        self.update_ui()

        # 启动控制按键的检测
        self.check_control_key()

        # 切换按钮
        self.switch_btn = ttk.Button(self.master, text="精简页面", command=self.toggle_page)
        self.switch_btn.place(x=115, y=0)

    def init_control_frame(self):
        """控制操作设置区初始化"""
        init_rows_and_cols(self.control_frame, 11, 4)

        ttk.Label(self.control_frame, text="选择操作:").grid(row=0, column=0, columnspan=2, padx=1, pady=1)
        ttk.Radiobutton(self.control_frame, text="鼠标模拟", variable=self.action_var, value='mouse',
                        command=self.update_ui).grid(
            row=1, column=0, columnspan=2, padx=1, pady=1)
        ttk.Radiobutton(self.control_frame, text="键盘模拟", variable=self.action_var, value='key',
                        command=self.update_ui).grid(
            row=1, column=2, columnspan=2, padx=1, pady=1)

        self.Radiobutton_Label = ttk.Label(self.control_frame, text="选择鼠标按键:")
        self.Radiobutton_l = ttk.Radiobutton(self.control_frame, text="左键", variable=self.mouse_button, value='left')
        self.Radiobutton_r = ttk.Radiobutton(self.control_frame, text="右键", variable=self.mouse_button, value='right')

        self.key_combobox_Label = ttk.Label(self.control_frame, text="选择键盘按键:")
        # 使用Combobox来选择或输入按键
        self.key_combobox = ttk.Combobox(self.control_frame, textvariable=self.selected_key, values=self.key_options,
                                         width=8)

        ttk.Label(self.control_frame, text="选择功能:").grid(row=4, column=0, columnspan=2, padx=1, pady=1)
        ttk.Radiobutton(self.control_frame, text="连点", variable=self.function_var, value='spam').grid(row=5, column=0,
                                                                                                        columnspan=2,
                                                                                                        padx=1, pady=1)
        ttk.Radiobutton(self.control_frame, text="长按", variable=self.function_var, value='hold').grid(row=5, column=2,
                                                                                                        columnspan=2,
                                                                                                        padx=1, pady=1)

        ttk.Label(self.control_frame, text="连点间隔(ms):").grid(row=6, column=0, columnspan=2, padx=1, pady=1)
        self.click_interval_entry = ttk.Entry(self.control_frame, textvariable=self.click_interval, width=11)
        self.click_interval_entry.grid(row=7, column=0, columnspan=2, padx=1, pady=1)

        ttk.Label(self.control_frame, text="波动间隔(ms):").grid(row=6, column=2, columnspan=2, padx=1, pady=1)
        self.click_interval_swings_entry = ttk.Entry(self.control_frame, textvariable=self.click_interval_swings,
                                                     width=11)
        self.click_interval_swings_entry.grid(row=7, column=2, columnspan=2, padx=1, pady=1)

        ttk.Label(self.control_frame, text="控制按键:").grid(row=8, column=1, columnspan=2, padx=1, pady=1)
        # 创建一个包含 F1 到 F12 的下拉菜单
        ttk.Combobox(self.control_frame, textvariable=self.control_key, values=self.control_key_options,
                     state="readonly", width=8).grid(row=9, column=1, columnspan=2, padx=1, pady=1)

        self.start_button = ttk.Button(self.control_frame, text="开始模拟", command=self.toggle_simulation, width=11)
        self.start_button.grid(row=10, column=0, columnspan=2, padx=1, pady=1)

        self.about_button = ttk.Button(self.control_frame, text="关于", command=show_about, width=6)
        self.about_button.grid(row=10, column=2, columnspan=2, padx=1, pady=1)

    def update_ui(self):
        """鼠标键盘模拟选项切换"""
        # 获取选择的操作类型
        action = self.action_var.get()

        # 如果是鼠标操作，显示鼠标设置，隐藏键盘设置
        if action == 'mouse':
            # 显示鼠标按钮的相关控件
            self.Radiobutton_Label.grid(row=2, column=0, columnspan=2, padx=1, pady=1)
            self.Radiobutton_l.grid(row=3, column=0, columnspan=2, padx=1, pady=1)
            self.Radiobutton_r.grid(row=3, column=2, columnspan=2, padx=1, pady=1)
            # 隐藏键盘相关控件
            self.key_combobox_Label.grid_forget()
            self.key_combobox.grid_forget()
        elif action == 'key':
            # 显示键盘设置相关控件
            self.key_combobox_Label.grid(row=2, column=0, columnspan=2, padx=1, pady=1)
            self.key_combobox.grid(row=3, column=0, columnspan=2, padx=1, pady=3)
            # 隐藏鼠标按钮设置的相关控件
            self.Radiobutton_Label.grid_forget()
            self.Radiobutton_l.grid_forget()
            self.Radiobutton_r.grid_forget()

    def init_logging_frame(self):
        """状态显示文本框初始化"""
        self.logging_text = tk.Text(self.logging_frame, height=6, width=46, wrap="word", state="disabled")
        scrollbar = ttk.Scrollbar(self.logging_frame, orient="vertical", command=self.logging_text.yview)
        self.logging_text.configure(yscrollcommand=scrollbar.set)

        self.logging_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 添加初始状态信息
        self.update_status(f"[{time.strftime('%H:%M:%S')}] 软件已就绪", color="#1677b3")  # 初始状态

    def toggle_page(self):
        """切换页面"""
        if self.is_compact:
            # 切换到原始页面
            self.master.geometry(f"{self.default_geometry['original']}")
            self.logging_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
            self.switch_btn.configure(text="精简页面")
        else:
            # 切换到精简页面
            self.master.geometry(f"{self.default_geometry['compact']}")
            self.logging_frame.pack_forget()
            self.switch_btn.configure(text="原始页面")

        self.is_compact = not self.is_compact

    def check_block(self):
        """完整性检测"""
        action_value = self.action_var.get().strip()  # 去除两端空白字符
        selected_key_value = self.selected_key.get().strip()
        click_interval_value = self.click_interval.get().strip()
        click_interval_swings_value = self.click_interval_swings.get().strip()
        entry = True
        if not click_interval_value:  # 若 连点间隔 为空，则设置为默认值
            entry = False
            self.click_interval.set(value=self.default_click)
            click_interval_value = self.default_click
            self.click_interval_entry.grid(row=7, column=0, columnspan=2, padx=1, pady=1)
        elif not click_interval_value.isdigit():
            self.click_interval.set(value="")
            self.click_interval_entry.grid(row=7, column=0, columnspan=2, padx=1, pady=1)
            messagebox.showwarning("输入错误!", "连点间隔只接受数字且为大于0的整数。")
            return True

        if not click_interval_swings_value:
            entry = False
            self.click_interval_swings.set(value=str(int(click_interval_value) // 2))
            click_interval_swings_value = str(int(click_interval_value) // 2)
            self.click_interval_swings_entry.grid(row=7, column=2, columnspan=2, padx=1, pady=1)
        elif not click_interval_swings_value.isdigit():
            self.click_interval.set(value="")
            self.click_interval_swings_entry.grid(row=7, column=2, columnspan=2, padx=1, pady=1)
            messagebox.showwarning("输入错误!", "波动间隔只接受数字且为大于0的整数。")
            return True

        if action_value == "key" and not selected_key_value:  # 如果为空或空白字符，弹出警告框
            messagebox.showwarning("输入错误!", "请选择模拟按键。")
            return True

        if int(click_interval_value) <= int(click_interval_swings_value) and entry:
            messagebox.showwarning("输入值错误!", "连点间隔小于或等于间隔波动时不起作用，所填间隔波动应小于连点间隔。")
            return True
        return False

    def update_status(self, message, color="black"):
        """模拟记录添加"""
        # 向文本框中添加信息并自动滚动
        self.logging_text.config(state="normal")  # 允许编辑
        self.logging_text.insert(tk.END, message + "\n")
        line_index = str(int(self.logging_text.index(tk.END).split('.')[0]) - 2)  # 获取当前插入文本的行号, 起始行号为 3 暂时不知道为什么
        tag_name = f"text_{line_index}"  # 为新插入的文本创建一个唯一标签
        self.logging_text.tag_add(tag_name, f"{line_index}.0", f"{line_index}.end")  # 为新插入的文本设置标签
        self.logging_text.tag_config(tag_name, foreground=color)  # 新文本按需着色
        self.logging_text.config(state="disabled")  # 禁止编辑
        self.logging_text.yview(tk.END)  # 自动滚动到底部

    def check_control_key(self):
        """模拟启动检测 - 带防抖功能"""
        control_key = self.control_key.get()

        # 如果按键刚被按下且不处于冷却期
        if keyboard.is_pressed(control_key):
            self.toggle_simulation()

            # 等待按键释放，避免重复触发
            while keyboard.is_pressed(control_key):
                time.sleep(0.01)

        self.master.after(100, self.check_control_key)

    def toggle_simulation(self):
        """控制模拟的开始/停止并记录状态"""
        current_time = time.perf_counter()

        # 添加防抖动锁，避免短时间内重复触发
        if hasattr(self, 'last_toggle_time') and current_time - self.last_toggle_time < 0.05:
            return  # 如果距离上次触发不到50ms，则忽略此次操作

        self.last_toggle_time = current_time  # 记录本次触发时间

        if not self.is_running:
            if self.check_block():
                return
            self.is_running = True
            self.start_button.config(text="停止模拟")
            if self.action_var.get() == 'mouse':
                self.update_status(
                    f"[{time.strftime('%H:%M:%S')}] 模拟开始, 模拟: {zh_trans_en_key(self.function_var.get())} - {self.mouse_button.get()}",
                    color="#41ae3c")
            elif self.action_var.get() == 'key':
                self.update_status(
                    f"[{time.strftime('%H:%M:%S')}] 模拟开始, 模拟: {zh_trans_en_key(self.function_var.get())} - {self.selected_key.get()}",
                    color="#41ae3c")
            threading.Thread(target=self.run_simulation, daemon=True).start()
        else:
            self.is_running = False
            self.start_button.config(text="开始模拟")

    def run_simulation(self):
        """模拟操作的核心逻辑 - 使用Win32API"""
        interval = float(self.click_interval.get()).__abs__() / 1000.0  # 转为秒
        interval_swings = int(self.click_interval_swings.get()).__abs__() / 1000.0  # 转为秒

        click_count = 0
        start_time = time.perf_counter()  # 使用高精度计时器
        next_click_time = start_time  # 下次点击时间
        last_gui_update = start_time  # 上次GUI更新时间

        # 鼠标事件映射
        mouse_event_map = {
            "left": {"down": win32con.MOUSEEVENTF_LEFTDOWN, "up": win32con.MOUSEEVENTF_LEFTUP},
            "right": {"down": win32con.MOUSEEVENTF_RIGHTDOWN, "up": win32con.MOUSEEVENTF_RIGHTUP}
        }

        # 键盘VK码映射
        vk_codes = {
            'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45, 'f': 0x46, 'g': 0x47, 'h': 0x48,
            'i': 0x49, 'j': 0x4A, 'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E, 'o': 0x4F, 'p': 0x50,
            'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54, 'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58,
            'y': 0x59, 'z': 0x5A, '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34, '5': 0x35,
            '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39, 'space': 0x20, 'enter': 0x0D, 'f1': 0x70,
            'f2': 0x71, 'f3': 0x72, 'f4': 0x73, 'f5': 0x74, 'f6': 0x75, 'f7': 0x76, 'f8': 0x77,
            'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B, 'esc': 0x1B, 'tab': 0x09
        }

        # 创建SendInput结构体 (用于键盘操作)
        PUL = ctypes.POINTER(ctypes.c_ulong)

        class KeyBdInput(ctypes.Structure):
            _fields_ = [("wVk", ctypes.c_ushort),
                        ("wScan", ctypes.c_ushort),
                        ("dwFlags", ctypes.c_ulong),
                        ("time", ctypes.c_ulong),
                        ("dwExtraInfo", PUL)]

        class HardwareInput(ctypes.Structure):
            _fields_ = [("uMsg", ctypes.c_ulong),
                        ("wParamL", ctypes.c_short),
                        ("wParamH", ctypes.c_ushort)]

        class MouseInput(ctypes.Structure):
            _fields_ = [("dx", ctypes.c_long),
                        ("dy", ctypes.c_long),
                        ("mouseData", ctypes.c_ulong),
                        ("dwFlags", ctypes.c_ulong),
                        ("time", ctypes.c_ulong),
                        ("dwExtraInfo", PUL)]

        class Input_I(ctypes.Union):
            _fields_ = [("ki", KeyBdInput),
                        ("mi", MouseInput),
                        ("hi", HardwareInput)]

        class Input(ctypes.Structure):
            _fields_ = [("type", ctypes.c_ulong),
                        ("ii", Input_I)]

        # 确保至少执行一次点击操作
        force_first_click = True

        while self.is_running:
            current_time = time.perf_counter()

            # 降低GUI更新频率，减少开销
            if current_time - last_gui_update >= 0.05:  # 每50ms更新一次GUI
                self.master.update_idletasks()
                self.master.update()
                last_gui_update = current_time

            if self.action_var.get() == 'mouse':
                button = self.mouse_button.get()
                if self.function_var.get() == 'hold':
                    # 使用win32api实现鼠标长按
                    win32api.mouse_event(mouse_event_map[button]["down"], 0, 0, 0, 0)
                    while self.is_running:
                        if time.perf_counter() - last_gui_update >= 0.05:
                            self.master.update()
                            last_gui_update = time.perf_counter()

                        time.sleep(0.01)
                    win32api.mouse_event(mouse_event_map[button]["up"], 0, 0, 0, 0)
                    break
                elif self.function_var.get() == 'spam':
                    if current_time >= next_click_time or force_first_click:
                        # 使用win32api实现鼠标点击
                        win32api.mouse_event(mouse_event_map[button]["down"], 0, 0, 0, 0)
                        win32api.mouse_event(mouse_event_map[button]["up"], 0, 0, 0, 0)
                        click_count += 1
                        force_first_click = False  # 已完成首次点击

                        # 计算下一次点击时间 (更精确的随机间隔)
                        random_interval = interval
                        if interval_swings > 0:
                            random_interval += randint(-int(interval_swings * 1000),
                                                       int(interval_swings * 1000)) / 1000.0
                        next_click_time = current_time + max(0.001, random_interval)  # 至少1ms间隔

            elif self.action_var.get() == 'key':
                key = self.selected_key.get().lower()

                # 尝试获取虚拟键码
                vk_code = None
                if key in vk_codes:
                    vk_code = vk_codes[key]

                if vk_code is not None:
                    # 使用SendInput API处理键盘
                    extra = ctypes.c_ulong(0)
                    ii_ = Input_I()

                    if self.function_var.get() == 'hold':
                        # 按下键
                        ii_.ki = KeyBdInput(vk_code, 0, 0, 0, ctypes.pointer(extra))
                        x = Input(ctypes.c_ulong(1), ii_)
                        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

                        while self.is_running:
                            if time.perf_counter() - last_gui_update >= 0.05:
                                self.master.update()
                                last_gui_update = time.perf_counter()
                            time.sleep(0.001)

                        # 释放键
                        ii_.ki = KeyBdInput(vk_code, 0, 0x0002, 0, ctypes.pointer(extra))
                        x = Input(ctypes.c_ulong(1), ii_)
                        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
                        break

                    elif self.function_var.get() == 'spam':
                        if current_time >= next_click_time:
                            # 按下键
                            ii_.ki = KeyBdInput(vk_code, 0, 0, 0, ctypes.pointer(extra))
                            x = Input(ctypes.c_ulong(1), ii_)
                            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

                            # 释放键
                            ii_.ki = KeyBdInput(vk_code, 0, 0x0002, 0, ctypes.pointer(extra))
                            x = Input(ctypes.c_ulong(1), ii_)
                            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

                            click_count += 1

                            # 计算下一次点击时间
                            random_interval = interval
                            if interval_swings > 0:
                                random_interval += randint(-int(interval_swings * 1000),
                                                           int(interval_swings * 1000)) / 1000.0
                            next_click_time = current_time + max(0.001, random_interval)
                else:
                    # 对于不在映射表中的键，回退到PyAutoGUI
                    if self.function_var.get() == 'hold':
                        pyautogui.keyDown(key)
                        while self.is_running:
                            if time.perf_counter() - last_gui_update >= 0.05:
                                self.master.update()
                                last_gui_update = time.perf_counter()
                            time.sleep(0.001)
                        pyautogui.keyUp(key)
                        break
                    elif self.function_var.get() == 'spam' and current_time >= next_click_time:
                        pyautogui.press(key)
                        click_count += 1
                        random_interval = interval
                        if interval_swings > 0:
                            random_interval += randint(-int(interval_swings * 1000),
                                                       int(interval_swings * 1000)) / 1000.0
                        next_click_time = current_time + max(0.001, random_interval)

            # 使用更小的睡眠时间提高响应性
            time.sleep(0.0001)

        # 结束处理
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time

        if self.function_var.get() == 'hold':
            self.update_status(f"[{time.strftime('%H:%M:%S')}] 模拟结束, 时长: {elapsed_time:.3f}秒", color="")
        elif self.function_var.get() == 'spam':
            if click_count > 0:
                avg_interval = elapsed_time / click_count
            else:
                avg_interval = 0
            self.update_status(
                f"[{time.strftime('%H:%M:%S')}] 模拟结束, 时长: {elapsed_time:.3f}秒, 点击次数: {click_count}, 平均间隔: {avg_interval:.3f}秒",
                color="")


if __name__ == "__main__":
    root = tk.Tk()
    app = SimulatorApp(root)
    root.mainloop()
