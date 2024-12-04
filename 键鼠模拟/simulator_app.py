import tkinter as tk
import pyautogui
import keyboard
import time
import threading


class SimulatorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("SimulatorApp")
        self.master.geometry("300x400+790+300")  # 设置窗口大小和位置
        self.is_running = False

        self.control_key = tk.StringVar(value='F12')
        self.selected_key = tk.StringVar(value='a')
        self.click_interval = tk.DoubleVar(value=10)
        self.mouse_button = tk.StringVar(value='left')

        tk.Label(master, text="选择操作:").pack()
        self.action_var = tk.StringVar(value='mouse')
        tk.Radiobutton(master, text="鼠标点击", variable=self.action_var, value='mouse').pack()
        tk.Radiobutton(master, text="键盘按键", variable=self.action_var, value='key').pack()

        tk.Label(master, text="控制按键:").pack()
        tk.Entry(master, textvariable=self.control_key).pack()

        tk.Label(master, text="选择鼠标按钮:").pack()
        tk.Radiobutton(master, text="左键", variable=self.mouse_button, value='left').pack()
        tk.Radiobutton(master, text="右键", variable=self.mouse_button, value='right').pack()

        tk.Label(master, text="选择功能:").pack()
        self.function_var = tk.StringVar(value='spam')
        tk.Radiobutton(master, text="连点", variable=self.function_var, value='spam').pack()
        tk.Radiobutton(master, text="长按", variable=self.function_var, value='hold').pack()

        tk.Label(master, text="选择键盘按键:").pack()
        tk.Entry(master, textvariable=self.selected_key).pack()

        tk.Label(master, text="连点间隔(ms):").pack()
        tk.Entry(master, textvariable=self.click_interval).pack()

        self.start_button = tk.Button(master, text="开始模拟", command=self.toggle_simulation)
        self.start_button.pack()

        # 启动控制按键的检测
        self.check_control_key()

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
                key = self.selected_key.get()
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
