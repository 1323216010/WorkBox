from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit
from menu_bar import create_help, create_about
from PySide6.QtGui import QFont

def create_input(dict1):
    dict1['input_line'] = QLineEdit()  # 创建输入栏
    dict1['input_line'].setPlaceholderText("Enter commands here and press enter to start")  # 设置提示文字
    # 设置输入框的字体和大小
    font = QFont()
    font.setPointSize(10)  # 设置字体大小
    dict1['input_line'].setFont(font)

    # 设置输入框的最小尺寸
    dict1['input_line'].setMinimumSize(QSize(0, 30))  # 设置最小高度

    # dict1['send_button'] = QPushButton()

    # 创建布局并添加输入框和发送按钮
    dict1['input_send_layout'] = QHBoxLayout()

    dict1['input_send_layout'].addWidget(dict1['input_line'])
    # dict1['input_send_layout'].addWidget(dict1['send_button'])


def create_menu_bar(dict1):
    # 创建菜单栏
    dict1['menu_bar'] = dict1['main_window'].menuBar()
    create_help(dict1)
    create_about(dict1)

def create_button(dict1):
    # 创建按钮和进度条
    dict1['button'] = QPushButton('Start')
    dict1['button'].setObjectName("buttonLabel")

    # progress_bar = QProgressBar()
    # progress_bar.setAlignment(Qt.AlignCenter)

    # 创建一个垂直布局来包含按钮和进度条
    dict1['button_layout'] = QVBoxLayout()
    dict1['button_layout'].addWidget(dict1['button'])
    # button_progress_layout.addWidget(progress_bar)


def create_time(dict1):
    # 创建一个标签来显示任务消耗时间
    dict1['time_label'] = QLabel('Time: 0s')
    dict1['time_label'].setAlignment(Qt.AlignCenter)
    dict1['time_label'].setObjectName("timeLabel")

    # 创建一个水平布局来包含按钮/进度条布局和时间标签
    dict1['operation_layout'] = QHBoxLayout()
    dict1['operation_layout'].addLayout(dict1['button_layout'])
    dict1['operation_layout'].addWidget(dict1['time_label'])


def set_component(dict1):
    central_widget = QWidget()
    dict1['main_window'].setCentralWidget(central_widget)
    # 创建一个垂直布局来包含所有控件
    layout = QVBoxLayout()
    layout.addLayout(dict1['input_send_layout'])  # 将输入栏添加到布局中
    layout.addLayout(dict1['operation_layout'])  # 添加操作布局
    layout.addWidget(dict1['console'])  # 将控制台添加到布局中

    # 设置中心部件的布局为垂直布局
    central_widget.setLayout(layout)