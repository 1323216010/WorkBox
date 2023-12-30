import sys
from PySide6.QtWidgets import QApplication, QPushButton, QMainWindow, QVBoxLayout, QWidget, QProgressBar, QTextEdit, QLineEdit
from PySide6.QtCore import Qt
from component import creat_help, creat_about
from work import on_button_clicked

def main():
    app = QApplication(sys.argv)

    main_window = QMainWindow()
    main_window.setWindowTitle('PySide6')

    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)

    # 创建按钮、进度条和控制台文本区域
    button = QPushButton('Start Operation')

    progress_bar = QProgressBar()
    progress_bar.setAlignment(Qt.AlignCenter)

    console = QTextEdit()
    console.setReadOnly(True)  # 设置为只读，仅用于显示信息

    input_line = QLineEdit()  # 创建输入栏
    input_line.setPlaceholderText("Please enter the path to log...")  # 设置提示文字

    # 使用lambda函数传递progress_bar和console
    button.clicked.connect(lambda: on_button_clicked(progress_bar, console, input_line.text()))

    layout = QVBoxLayout(central_widget)
    layout.addWidget(input_line)  # 将输入栏添加到布局中
    layout.addWidget(button)
    layout.addWidget(progress_bar)
    layout.addWidget(console)  # 将控制台添加到布局中

    central_widget.setLayout(layout)

    # 创建菜单栏
    menu_bar = main_window.menuBar()
    creat_help(main_window, menu_bar)
    creat_about(main_window, menu_bar)

    main_window.resize(500, 400)
    main_window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()