from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QAction

def creat_help(main_window, menu_bar):
    # 创建“帮助”菜单
    help_menu = menu_bar.addMenu("&Help")

    # 创建并添加“帮助内容”动作
    help_action = QAction("&Help Content", main_window)
    help_action.triggered.connect(lambda: QMessageBox.information(main_window, "Help", "Help content goes here..."))
    help_menu.addAction(help_action)

def creat_about(main_window, menu_bar):
    # 直接在菜单栏上添加“关于”动作
    about_action = QAction("&About This App", main_window)
    about_action.triggered.connect(
        lambda: QMessageBox.information(main_window, "About", "PySide6 Application\nVersion 20231230a"))
    menu_bar.addAction(about_action)  # 直接添加到菜单栏