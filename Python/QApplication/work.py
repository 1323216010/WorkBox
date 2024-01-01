import time
from PySide6.QtCore import QTime, QThread, Signal
from PySide6.QtCore import QMetaObject, Q_ARG, Qt
from utils import elapsed_time


class WorkerThread(QThread):
    update_signal = Signal(str)
    task_completed = False  # 任务完成标志

    def task(self):
        max_steps = 100
        for step in range(max_steps):
            time.sleep(0.19)  # 模拟耗时操作
            self.update_signal.emit(f"步骤 {step + 1} 完成")

    def run(self):
        try:
            self.task()
            self.task_completed = True  # 更新任务完成标志
            self.update_signal.emit(f"<span style='color: green;'>The task is completed</span>")
        except Exception as e:
            self.task_completed = True
            self.update_signal.emit(f"Error message: " + f"<span style='color: red;'>{e}</span>")


def on_button_clicked(dict1):
    # 禁用按钮
    dict1['button'].setEnabled(False)
    dict1['input_line'].setEnabled(False)

    # 在控制台以特定格式输出用户输入
    dict1['console'].append(f"<span style=\"color: #44546A;\">{dict1['input_line'].text()}</span>")
    # 清空输入框
    dict1['input_line'].clear()

    # 创建并启动新线程
    worker_thread = WorkerThread()
    worker_thread.update_signal.connect(dict1['console'].append)
    worker_thread.start()

    start_time = QTime.currentTime()  # 记录开始时间
    # worker_thread.quit()

    while not worker_thread.task_completed:  # 检查任务是否完成
        time.sleep(0.1)
        elapsed_time(start_time, dict1)

    # worker_thread.wait()
    # 更新UI元素需要在主线程中完成
    QMetaObject.invokeMethod(dict1['button'], "setEnabled", Qt.QueuedConnection, Q_ARG(bool, True))
    QMetaObject.invokeMethod(dict1['input_line'], "setEnabled", Qt.QueuedConnection, Q_ARG(bool, True))
