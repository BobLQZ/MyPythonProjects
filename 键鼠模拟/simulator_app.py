import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import keyboard
import time
import threading
from random import randint


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

        self.default_geometry = {
            "original": "620x440",  # 原始页面大小
            "compact": "230x440",  # 精简页面大小
        }

        # 最大行数与列数
        self.max_rows = 0
        self.max_cols = 0

        # 设置窗口的内边距
        self.master.configure(padx=10, pady=10)  # 设置窗口边缘与控件之间的距离

        self.default_active = 'mouse'
        self.default_mouse = 'left'
        self.default_keyboard = 'a'
        self.default_function = 'spam'
        self.default_click = '100'
        self.default_click_swings = '50'
        self.default_control = 'F12'  # 默认值为 F12

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
        self.key_options.extend(['左方向键', '右方向键', '上方向键', '下方向键'])  # 方向键选项
        self.key_options.extend(['空格', 'enter', 'tab', 'esc'])  # 常用功能键
        # 控制按键选项
        self.control_key_options = [f'F{i}' for i in range(1, 13)]  # 生成 F1 到 F12 的选项

        # 创建两个页面的 Frame
        self.original_frame = tk.Frame(self.master)  # 原始页面
        self.compact_frame = tk.Frame(self.master)  # 精简页面

        # 初始化页面内容
        self.init_original_page()

        # 初始显示原始页面
        self.original_frame.pack(fill=tk.BOTH, expand=True)
        self.master.geometry(self.default_geometry["original"])  # 设置初始大小

    def init_rows_and_cols(self, rows, cols):
        self.max_rows = rows
        self.max_cols = cols
        # 获取组件的行数和列数
        # 原始页面
        # rows = 11  # 根据界面控件来设置行数
        # cols = 7  # 界面有7列
        # 精简页面
        # rows = 11  # 根据界面控件来设置行数
        # cols = 4  # 界面有7列

        # 自动设置所有列和行的大小
        for col in range(4):
            self.original_frame.grid_columnconfigure(col, weight=1, minsize=20)  # 所有列宽度随窗口变化，最小宽度 40px

        if cols > 4:
            for col in range(4, cols):
                self.original_frame.grid_columnconfigure(col, weight=5, minsize=0)  # 所有列宽度随窗口变化，最小宽度 80px

        for row in range(rows):
            self.original_frame.grid_rowconfigure(row, weight=1, minsize=27)  # 所有行高度随窗口变化，最小高度 27px

    def reset_grid_configuration(self):
        # for row in range(self.max_rows):
        #     self.original_frame.grid_rowconfigure(row, weight=0, minsize=0)
        for col in range(self.max_cols):
            self.original_frame.grid_columnconfigure(col, weight=0, minsize=0)


    def init_original_page(self):
        """原始页面初始化"""
        self.init_rows_and_cols(11,7)

        tk.Label(self.original_frame, text="选择操作:").grid(row=0, column=1, columnspan=2, padx=1, pady=1)
        tk.Radiobutton(self.original_frame, text="鼠标点击", variable=self.action_var, value='mouse', command=self.update_ui).grid(
            row=1, column=0, columnspan=2, padx=1, pady=1)
        tk.Radiobutton(self.original_frame, text="键盘按键", variable=self.action_var, value='key', command=self.update_ui).grid(
            row=1, column=2, columnspan=2, padx=1, pady=1)

        self.Radiobutton_Label = tk.Label(self.original_frame, text="选择鼠标按钮:")
        self.Radiobutton_l = tk.Radiobutton(self.original_frame, text="左键", variable=self.mouse_button, value='left')
        self.Radiobutton_r = tk.Radiobutton(self.original_frame, text="右键", variable=self.mouse_button, value='right')

        self.key_combobox_Label = tk.Label(self.original_frame, text="选择键盘按键:")
        # 使用Combobox来选择或输入按键
        self.key_combobox = ttk.Combobox(self.original_frame, textvariable=self.selected_key, values=self.key_options, width=8)

        tk.Label(self.original_frame, text="选择功能:").grid(row=4, column=1, columnspan=2, padx=1, pady=1)
        tk.Radiobutton(self.original_frame, text="连点", variable=self.function_var, value='spam').grid(row=5, column=0, columnspan=2, padx=1, pady=1)
        tk.Radiobutton(self.original_frame, text="长按", variable=self.function_var, value='hold').grid(row=5, column=2, columnspan=2, padx=1, pady=1)

        tk.Label(self.original_frame, text="连点间隔(ms):").grid(row=6, column=0, columnspan=2, padx=1, pady=1)
        self.click_interval_entry = tk.Entry(self.original_frame, textvariable=self.click_interval, width=11)
        self.click_interval_entry.grid(row=7, column=0, columnspan=2, padx=1, pady=1)

        tk.Label(self.original_frame, text="间隔波动(ms):").grid(row=6, column=2, columnspan=2, padx=1, pady=1)
        self.click_interval_swings_entry = tk.Entry(self.original_frame, textvariable=self.click_interval_swings, width=11)
        self.click_interval_swings_entry.grid(row=7, column=2, columnspan=2, padx=1, pady=1)

        tk.Label(self.original_frame, text="控制按键:").grid(row=8, column=1, columnspan=2, padx=1, pady=1)
        # 创建一个包含 F1 到 F12 的下拉菜单
        self.control_key_combobox = ttk.Combobox(self.original_frame, textvariable=self.control_key, values=self.control_key_options, state="readonly", width=8)
        self.control_key_combobox.grid(row=9, column=1, columnspan=2, padx=1, pady=1)

        self.start_button = tk.Button(self.original_frame, text="开始模拟", command=self.toggle_simulation, width=10)
        self.start_button.grid(row=10, column=0, columnspan=2, padx=1, pady=1)

        # 页面切换
        tk.Button(self.original_frame, text="精简页面", font=("Times New Roman", 8), command=self.toggle_page, width=7).grid(row=10, column=2, columnspan=2, padx=1, pady=1)

        # 添加状态显示文本框
        self.status_label = tk.Label(self.original_frame, text="模拟记录:")
        self.status_label.grid(row=0, column=4, columnspan=3, padx=9, pady=1, sticky='w')

        self.status_text = tk.Text(self.original_frame, height=6, width=30, wrap=tk.WORD, state=tk.DISABLED)
        self.status_text.grid(row=1, column=4, columnspan=3, rowspan=10, padx=9, pady=1, sticky='nsew')
        self.update_status(f"<{time.strftime('%H:%M:%S')}>软件已就绪", color="")  # 初始状态

        # 启动控制按键的检测
        self.check_control_key()

        # 默认显示鼠标按钮设置，隐藏键盘按钮设置
        self.update_ui()

    def toggle_page(self):
        """切换页面"""
        # 获取当前窗口位置
        x = self.master.winfo_x()
        y = self.master.winfo_y()

        if self.is_compact:
            # 切换到原始页面
            self.master.geometry(f"{self.default_geometry['original']}+{x}+{y}")
            self.reset_grid_configuration()
            self.init_rows_and_cols(11,7)
            self.status_label.grid(row=0, column=4, columnspan=3, padx=9, pady=1, sticky='w')
            self.status_text.grid(row=1, column=4, columnspan=3, rowspan=10, padx=9, pady=1, sticky='nsew')
        else:
            # 切换到精简页面
            self.status_label.grid_forget()
            self.status_text.grid_forget()
            self.master.geometry(f"{self.default_geometry['compact']}+{x}+{y}")
            self.reset_grid_configuration()
            self.init_rows_and_cols(11,4)

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
            self.click_interval_entry.grid(row=7, column=0, columnspan=2, padx=1, pady=1)
        elif not click_interval_value.isdigit():
            self.click_interval.set(value="")
            self.click_interval_entry.grid(row=7, column=0, columnspan=2, padx=1, pady=1)
            messagebox.showwarning("输入错误!", "连点间隔只接受数字。")
            return True

        if not click_interval_swings_value:
            entry = False
            self.click_interval_swings.set(value=self.default_click_swings)
            self.click_interval_swings_entry.grid(row=7, column=2, columnspan=2, padx=1, pady=1)
        elif not click_interval_swings_value.isdigit():
            self.click_interval.set(value="")
            self.click_interval_swings_entry.grid(row=7, column=2, columnspan=2, padx=1, pady=1)
            messagebox.showwarning("输入错误!", "波动间隔只接受数字。")
            return True

        if action_value == "key" and not selected_key_value:  # 如果为空或空白字符，弹出警告框
            messagebox.showwarning("输入错误!", "请选择模拟按键。")
            return True

        if int(click_interval_value) <= int(click_interval_swings_value) and entry:
            messagebox.showwarning("输入值错误!", "连点间隔小于或等于间隔波动时不起作用，所填间隔波动应小于连点间隔。")
            return True
        return False

    def update_ui(self):
        """鼠标键盘模拟选项切换"""
        # 获取选择的操作类型
        action = self.action_var.get()

        # 如果是鼠标操作，显示鼠标设置，隐藏键盘设置
        if action == 'mouse':
            # 显示鼠标按钮的相关控件
            self.Radiobutton_Label.grid(row=2, column=1, columnspan=2, padx=1, pady=1)
            self.Radiobutton_l.grid(row=3, column=0, columnspan=2, padx=1, pady=1)
            self.Radiobutton_r.grid(row=3, column=2, columnspan=2, padx=1, pady=1)
            # 隐藏键盘相关控件
            self.key_combobox_Label.grid_forget()
            self.key_combobox.grid_forget()
        elif action == 'key':
            # 显示键盘设置相关控件
            self.key_combobox_Label.grid(row=2, column=1, columnspan=2, padx=1, pady=1)
            self.key_combobox.grid(row=3, column=1, columnspan=2, padx=1, pady=3)
            # 隐藏鼠标按钮设置的相关控件
            self.Radiobutton_Label.grid_forget()
            self.Radiobutton_l.grid_forget()
            self.Radiobutton_r.grid_forget()

    def update_status(self, message, color="black"):
        """模拟记录添加"""
        # 向文本框中添加信息并自动滚动
        self.status_text.config(state=tk.NORMAL)  # 允许编辑
        self.status_text.insert(tk.END, message + "\n")
        line_index = str(int(self.status_text.index(tk.END).split('.')[0]) - 2)  # 获取当前插入文本的行号, 起始行号为 3 暂时不知道为什么
        tag_name = f"text_{line_index}"  # 为新插入的文本创建一个唯一标签
        self.status_text.tag_add(tag_name, f"{line_index}.0", f"{line_index}.end")  # 为新插入的文本设置标签
        self.status_text.tag_config(tag_name, foreground=color)  # 新文本按需着色
        self.status_text.config(state=tk.DISABLED)  # 禁止编辑
        self.status_text.yview(tk.END)  # 自动滚动到底部

    def zh_cn_To_en_us_key(self, key):
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

    def zh_cn_To_en_us_mou(self, mou):
        """鼠标文字中英文转换"""
        mou_zh_cn = {'左键 ': 'left', '右键': 'right', '长按': 'hold', '连点': 'spam'}
        value = [k for k, v in mou_zh_cn.items() if v == mou]
        try:
            return value[0]
        except:
            return mou

    def check_control_key(self):
        """模拟启动检测"""
        control_key = self.control_key.get()
        if keyboard.is_pressed(control_key):
            self.toggle_simulation()
            # 等待按键释放，高效地避免按键卡住导致多次触发
            while keyboard.is_pressed(control_key):
                time.sleep(0.01)
        self.master.after(100, self.check_control_key)

    def toggle_simulation(self):
        """控制模拟的开始并模拟记录"""
        if not self.is_running:
            if self.check_block():
                return
            self.is_running = True
            self.start_button.config(text="停止模拟")
            if self.action_var.get() == 'mouse':
                self.update_status(
                    f"<{time.strftime('%H:%M:%S')}>模拟开始, 模拟: {self.zh_cn_To_en_us_mou(self.function_var.get())} - {self.zh_cn_To_en_us_mou(self.mouse_button.get())}",
                    color="#41ae3c")
            elif self.action_var.get() == 'key':
                self.update_status(
                    f"<{time.strftime('%H:%M:%S')}>模拟开始, 模拟: {self.zh_cn_To_en_us_key(self.function_var.get())} - {self.selected_key.get()}",
                    color="#41ae3c")
            threading.Thread(target=self.run_simulation, daemon=True).start()
        else:
            self.is_running = False
            self.start_button.config(text="开始模拟")

    def run_simulation(self):
        """模拟操作的核心逻辑"""
        control_key = self.control_key.get()
        interval = float(self.click_interval.get()).__abs__()
        interval_swings = int(self.click_interval_swings.get()).__abs__()

        click_count = 0
        start_time = time.time()

        while self.is_running:
            # 定期处理事件
            self.master.update_idletasks()
            self.master.update()
            interval_round = (interval + randint(-interval_swings, interval_swings)) / 1000.0

            # 如果控制按键被按下，停止模拟
            if keyboard.is_pressed(control_key):
                self.toggle_simulation()
                # 等待按键释放来避免在系统检测到重复输入
                while keyboard.is_pressed(control_key):
                    time.sleep(0.1)
                break

            if self.action_var.get() == 'mouse':
                if self.function_var.get() == 'hold':
                    button = self.mouse_button.get()
                    pyautogui.mouseDown(button=button)
                    while self.is_running:
                        self.master.update()  # 定期更新 GUI
                    pyautogui.mouseUp(button=button)
                elif self.function_var.get() == 'spam':
                    button = self.mouse_button.get()
                    while self.is_running:
                        start_time_spam = time.perf_counter()
                        pyautogui.click(button=button)
                        click_count += 1
                        elapsed_time = time.perf_counter() - start_time_spam
                        time.sleep(max(0, interval_round - elapsed_time))  # 使用自定义间隔
            elif self.action_var.get() == 'key':
                key = self.zh_cn_To_en_us_key(self.selected_key.get())
                if self.function_var.get() == 'hold':
                    pyautogui.keyDown(key)
                    while self.is_running:
                        self.master.update()  # 定期更新 GUI
                    pyautogui.keyUp(key)
                elif self.function_var.get() == 'spam':
                    while self.is_running:
                        start_time_spam = time.perf_counter()
                        pyautogui.press(key)
                        click_count += 1
                        elapsed_time = time.perf_counter() - start_time_spam
                        time.sleep(max(0, interval_round - elapsed_time))  # 使用自定义间隔

        # 模拟结束时显示时间和点击次数
        end_time = time.time()
        elapsed_time = end_time - start_time
        if self.function_var.get() == 'hold':
            self.update_status(
                f"<{time.strftime('%H:%M:%S')}>模拟结束, 时长: {elapsed_time:.3f}秒", color="")
        elif self.function_var.get() == 'spam':
            self.update_status(
                f"<{time.strftime('%H:%M:%S')}>模拟结束, 时长: {elapsed_time:.3f}秒, 点击次数: {click_count}, 平均间隔: {elapsed_time / click_count:.3f}", color="")
        self.start_button.config(text="开始模拟")


if __name__ == "__main__":
    root = tk.Tk()
    app = SimulatorApp(root)
    root.mainloop()
