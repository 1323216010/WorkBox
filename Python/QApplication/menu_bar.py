from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QAction

def create_help(dict1):
    # 创建“帮助”菜单
    dict1['help_menu'] = dict1['menu_bar'].addMenu("&Help")

    # 创建并添加“帮助内容”动作
    dict1['help_action'] = QAction("&Doc", dict1['main_window'])
    dict1['help_action'].triggered.connect(lambda: show_help_dialog(dict1['main_window']))
    dict1['help_menu'].addAction(dict1['help_action'])

def show_help_dialog(parent):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Help")

    layout = QVBoxLayout()

    # 使用富文本标签来显示帮助内容
    help_text = """
    <div style='text-align: left;'>
        <h2>How to Use This Application</h2>
        <p>Here are some basic instructions on how to use the application:</p>
        <ul>
            <li>Feature 1: Description...</li>
            <li>Feature 2: Description...</li>
            <li>Feature 3: Description...</li>
        </ul>
        <p>For more detailed information, please contact: <a href='mailto:Pengcheng.yan@cowellchina.com'>Pengcheng.yan@cowellchina.com</a></p>
    </div>
    """
    label = QLabel(help_text)
    label.setOpenExternalLinks(True)  # 允许打开外部链接
    layout.addWidget(label)

    # 添加关闭按钮
    close_button = QPushButton("Close")
    close_button.clicked.connect(dialog.close)
    layout.addWidget(close_button)

    dialog.setLayout(layout)
    # 使用 show() 而不是 exec_() 来显示对话框，对话框将以非模态方式打开，这意味着它不会阻塞主事件循环
    dialog.show()

def create_about(dict1):
    # 直接在菜单栏上添加“关于”动作
    about_action = QAction("&About This App", dict1['main_window'])
    about_action.triggered.connect(lambda: show_about_dialog(dict1['main_window']))
    dict1['menu_bar'].addAction(about_action)  # 直接添加到菜单栏

def show_about_dialog(parent):
    dialog = QDialog(parent)
    dialog.setWindowTitle("About")

    layout = QVBoxLayout()

    # 添加富文本标签，使用HTML和CSS进行排版
    about_text = """
    <div style='text-align: center;'>
        <h2>PySide6 Application</h2>
        <p>Version 20231230a</p>
        <p>For any questions or concerns, please contact:<br>
        <a href='mailto:Pengcheng.yan@cowellchina.com'>Pengcheng.yan@cowellchina.com</a></p>
    </div>
    """
    label = QLabel(about_text)
    label.setOpenExternalLinks(True)  # 允许打开外部链接
    layout.addWidget(label)

    # 添加关闭按钮
    close_button = QPushButton("Close")
    close_button.clicked.connect(dialog.close)
    layout.addWidget(close_button)

    dialog.setLayout(layout)
    dialog.show()