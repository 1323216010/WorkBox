import time
from PySide6.QtWidgets import QMessageBox

def on_button_clicked(progress_bar, console, text):
    console.append(text)
    max_steps = 10
    for step in range(max_steps):
        # 模拟耗时操作
        time.sleep(0.5)  # 模拟操作，暂停0.5秒
        progress_bar.setValue((step + 1) * 10)  # 更新进度条
        console.append(f"步骤 {step + 1} 完成")  # 向控制台输出信息
    # QMessageBox.information(None, "Message", "Operation complete！")