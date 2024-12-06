import tkinter as tk
from tkinter import ttk
import pyautogui
import keyboard
import time
import threading


class SimulatorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("SimulatorApp")
        self.master.geometry("260x440+830+320")  # 设置窗口大小和位置
        self.is_running = False

        self.master.resizable(False, False)  # 禁止水平方向和垂直方向的调整大小

        # 设置窗口的内边距
        self.master.configure(padx=20, pady=10)  # 设置窗口边缘与控件之间的距离

        # 获取组件的行数和列数
        rows = 10  # 根据界面控件来设置行数
        columns = 2  # 界面有两列

        # 自动设置所有列和行的大小
        for col in range(columns):
            master.grid_columnconfigure(col, weight=1, minsize=80)  # 所有列宽度随窗口变化，最小宽度 80px

        for row in range(rows):
            master.grid_rowconfigure(row, weight=1, minsize=27)  # 所有行高度随窗口变化，最小高度 27px

        self.control_key = tk.StringVar(value='F12')  # 默认值为 F12
        self.selected_key = tk.StringVar(value='a')
        self.click_interval = tk.DoubleVar(value=10)
        self.mouse_button = tk.StringVar(value='left')

        tk.Label(master, text="选择操作:").grid(row=0, column=0, columnspan=2, padx=1, pady=1, sticky='nsew')
        self.action_var = tk.StringVar(value='mouse')
        tk.Radiobutton(master, text="鼠标点击", variable=self.action_var, value='mouse', command=self.update_ui).grid(
            row=1, column=0, padx=1, pady=1, sticky='nsew')
        tk.Radiobutton(master, text="键盘按键", variable=self.action_var, value='key', command=self.update_ui).grid(
            row=1, column=1, padx=1, pady=1, sticky='nsew')

        self.Radiobutton_Label = tk.Label(master, text="选择鼠标按钮:")
        self.Radiobutton_l = tk.Radiobutton(master, text="左键", variable=self.mouse_button, value='left')
        self.Radiobutton_r = tk.Radiobutton(master, text="右键", variable=self.mouse_button, value='right')

        self.key_combobox_Label = tk.Label(master, text="选择键盘按键:")
        # 使用Combobox来选择或输入按键
        self.key_options = ['左方向键', '右方向键', '上方向键', '下方向键']  # 方向键选项
        self.key_options.extend([chr(i) for i in range(97, 123)])  # 添加a-z字母按键
        self.key_options.extend([str(i) for i in range(0, 10)])  # 添加数字0-9按键
        self.key_options.extend(['空格', 'enter', 'tab', 'esc'])  # 常用功能键

        self.key_combobox = ttk.Combobox(master, textvariable=self.selected_key, values=self.key_options,
                                         state="normal", width=10)

        tk.Label(master, text="选择功能:").grid(row=4, column=0, columnspan=2, padx=1, pady=1, sticky='nsew')
        self.function_var = tk.StringVar(value='spam')
        tk.Radiobutton(master, text="连点", variable=self.function_var, value='spam').grid(row=5, column=0, padx=1,
                                                                                           pady=1, sticky='nsew')
        tk.Radiobutton(master, text="长按", variable=self.function_var, value='hold').grid(row=5, column=1, padx=1,
                                                                                           pady=1, sticky='nsew')

        tk.Label(master, text="连点间隔(ms):").grid(row=6, column=0, columnspan=2, padx=1, pady=1, sticky='nsew')
        tk.Entry(master, textvariable=self.click_interval, width=13).grid(row=7, column=0, columnspan=2, padx=1, pady=1)

        tk.Label(master, text="控制按键:").grid(row=8, column=0, columnspan=2, padx=1, pady=1, sticky='nsew')
        # 创建一个包含 F1 到 F12 的下拉菜单
        self.control_key_options = [f'F{i}' for i in range(1, 13)]  # 生成 F1 到 F12 的选项
        self.control_key_combobox = ttk.Combobox(master, textvariable=self.control_key, values=self.control_key_options,
                                                 state="readonly", width=10)
        self.control_key_combobox.grid(row=9, column=0, columnspan=2, padx=1, pady=1)

        self.start_button = tk.Button(master, text="开始模拟", command=self.toggle_simulation, width=10)
        self.start_button.grid(row=10, column=0, columnspan=2, padx=1, pady=1)

        # 启动控制按键的检测
        self.check_control_key()

        # 默认显示鼠标按钮设置，隐藏键盘按钮设置
        self.update_ui()

    def update_ui(self):
        # 获取选择的操作类型
        action = self.action_var.get()

        # 如果是鼠标操作，显示鼠标设置，隐藏键盘设置
        if action == 'mouse':
            # 显示鼠标按钮的相关控件
            self.Radiobutton_Label.grid(row=2, column=0, columnspan=2, padx=1, pady=1, sticky='nsew')
            self.Radiobutton_l.grid(row=3, column=0, padx=1, pady=1, sticky='nsew')
            self.Radiobutton_r.grid(row=3, column=1, padx=1, pady=1, sticky='nsew')
            # 隐藏键盘相关控件
            self.key_combobox_Label.grid_forget()
            self.key_combobox.grid_forget()
        elif action == 'key':
            # 显示键盘设置相关控件
            self.key_combobox_Label.grid(row=2, column=0, columnspan=2, padx=1, pady=1, sticky='nsew')
            self.key_combobox.grid(row=3, column=0, columnspan=2, padx=1, pady=3)
            # 隐藏鼠标按钮设置的相关控件
            self.Radiobutton_Label.grid_forget()
            self.Radiobutton_l.grid_forget()
            self.Radiobutton_r.grid_forget()

    def zh_cn_To_en_us(self, key):
        key_zh_cn = {'左方向键':'left', '右方向键':'right', '上方向键':'up', '下方向键':'down', '空格':'space'}
        try:
            return key_zh_cn[key]
        except:
            return key

    def check_control_key(self):
        control_key = self.control_key.get()
        if keyboard.is_pressed(control_key):
            self.toggle_simulation()
            # 等待按键释放，高效地避免按键卡住导致多次触发
            while keyboard.is_pressed(control_key):
                time.sleep(0.01)
        self.master.after(10, self.check_control_key)

    def toggle_simulation(self):
        if not self.is_running:
            self.is_running = True
            self.start_button.config(text="停止模拟")
            threading.Thread(target=self.run_simulation, daemon=True).start()
        else:
            self.is_running = False
            self.start_button.config(text="开始模拟")

    def run_simulation(self):
        control_key = self.control_key.get()
        interval = self.click_interval.get() / 1000.0  # 转换为秒
        while self.is_running:

            # 定期处理事件
            self.master.update_idletasks()
            self.master.update()

            # 如果控制按键被按下，停止模拟
            if keyboard.is_pressed(control_key):
                self.toggle_simulation()
                # 等待按键释放来避免在系统检测到重复输入
                while keyboard.is_pressed(control_key):
                    time.sleep(0.01)
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
                        start_time = time.perf_counter()
                        pyautogui.click(button=button)
                        elapsed_time = time.perf_counter() - start_time
                        time.sleep(max(0, interval - elapsed_time))  # 使用自定义间隔
            elif self.action_var.get() == 'key':
                key = self.zh_cn_To_en_us(self.selected_key.get())
                if self.function_var.get() == 'hold':
                    pyautogui.keyDown(key)
                    while self.is_running:
                        self.master.update()  # 定期更新 GUI
                        return
                    pyautogui.keyUp(key)
                elif self.function_var.get() == 'spam':
                    while self.is_running:
                        start_time = time.perf_counter()
                        pyautogui.press(key)
                        elapsed_time = time.perf_counter() - start_time
                        time.sleep(max(0, interval - elapsed_time))  # 使用自定义间隔
        self.start_button.config(text="开始模拟")


if __name__ == "__main__":
    root = tk.Tk()
    app = SimulatorApp(root)
    root.mainloop()
