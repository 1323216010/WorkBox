import time
from PySide6.QtCore import QTime, QThread, Signal
from PySide6.QtCore import QMetaObject, Q_ARG, Qt
from utils import elapsed_time


class WorkerThread(QThread):
    update_signal = Signal(str)
    task_completed = False  # 任务完成标志

    def __init__(self, content, config, *args, **kwargs):
        super(WorkerThread, self).__init__(*args, **kwargs)
        self.content = content
        self.config = config

    def new_print(self, message, color='normal'):
        if color == 'normal':
            formatted_message = f"{message}"
        elif color == 'red':
            formatted_message = f"Error message: " + f"<span style='color: red;'>{message}</span>"
        else:
            formatted_message = f"<span style='color: {color};'>{message}</span>"
        self.update_signal.emit(formatted_message)

    def task(self):
        max_steps = 100
        for step in range(max_steps):
            time.sleep(0.19)  # 模拟耗时操作
            self.update_signal.emit(f"步骤 {step + 1} 完成")

    def run(self):
        try:
            self.new_print(self.content, '#44546A')
            self.task()
            self.task_completed = True  # 更新任务完成标志
            self.new_print('')
            self.new_print('The task is completed', 'green')
        except Exception as e:
            self.task_completed = True
            self.new_print(e, 'red')


def on_button_clicked(dict1, config):
    # 禁用按钮
    dict1['button'].setEnabled(False)
    dict1['input_line'].setEnabled(False)
    content = dict1['input_line'].text()
    # 清空输入框
    dict1['input_line'].clear()

    # 创建并启动新线程
    worker_thread = WorkerThread(content, config)
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
