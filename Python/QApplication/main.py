import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from component import create_button, create_time, create_menu_bar, create_input, set_component
from CustomTextEdit import CustomTextEdit
from style import apply_stylesheet
from work import on_button_clicked
from utils import set_res, print_welcome_info
from config import read_or_create_config

def main(dict1, config):
    app = QApplication(sys.argv)
    apply_stylesheet(app)

    dict1['main_window'] = QMainWindow()
    dict1['main_window'].setWindowTitle('PySide6')

    # 创建按钮和进度条
    create_button(dict1)

    # 创建一个标签来显示任务消耗时间
    create_time(dict1)

    # 创建控制台文本区域
    dict1['console'] = CustomTextEdit()
    dict1['console'].setReadOnly(True)  # 设置为只读，仅用于显示信息

    create_input(dict1)

    # 使用lambda函数传递progress_bar和console
    dict1['button'].clicked.connect(lambda: on_button_clicked(dict1))
    # 将输入栏的returnPressed信号也连接到相同的槽函数
    dict1['input_line'].returnPressed.connect(lambda: on_button_clicked(dict1))

    set_component(dict1)

    create_menu_bar(dict1)

    set_res(dict1)

    dict1['main_window'] .resize(config['width'], config['height'])
    dict1['main_window'] .show()
    print_welcome_info(dict1)

    sys.exit(app.exec())

if __name__ == '__main__':
    dict1 = {}
    config = read_or_create_config('config.json')
    main(dict1, config)
