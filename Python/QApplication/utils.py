import sys, os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTime
from PySide6.QtGui import QIcon


def elapsed_time(start_time, dict1):
    elapsed_time = QTime.currentTime().msecsTo(start_time) // -1000  # 计算已经过去的时间
    dict1['time_label'].setText(
        f'<img src="{dict1["clock_icon_path"]}" width="16" height="16"> Time: {elapsed_time}s')  # 更新时间标签
    QApplication.processEvents()  # 处理所有挂起的事件，更新界面


def set_res(dict1):
    # 检查应用程序是否被打包
    if getattr(sys, 'frozen', False):
        # 如果应用程序被打包
        application_path = sys._MEIPASS
    else:
        # 如果应用程序未被打包
        application_path = os.path.dirname(os.path.abspath(__file__))

    icon_path = os.path.join(application_path, 'res', 'toolbox.svg')
    dict1['clock_icon_path'] = os.path.join(application_path, 'res', 'clock.svg')
    dict1['start_icon_path'] = os.path.join(application_path, 'res', 'start.svg')
    dict1['help_icon_path'] = os.path.join(application_path, 'res', 'help.svg')

    dict1['main_window'].setWindowIcon(QIcon(icon_path))

    dict1['time_label'].setText(f'<img src="{dict1["clock_icon_path"]}" width="16" height="16"> Time: 0s')
    dict1['button'].setIcon(QIcon(dict1['start_icon_path']))
    dict1['help_action'].setIcon(QIcon(dict1['help_icon_path']))

    # dict1['send_button'].setIcon(QIcon(dict1['send_icon_path']))


def print_welcome_info(dict1, config):
    dict1['console'].append("<span style='color: gray;'>Welcome to the application. Please enter a command or select "
                            "an operation.</span>")

    if config.get('exception'):
        dict1['console'].append(f"Error message: " + f"<span style='color: red;'>{config['exception']}</span>")
