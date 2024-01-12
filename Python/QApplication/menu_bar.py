from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QWidget, QScrollArea
from PySide6.QtGui import QAction


def create_help(dict1):
    # 创建“帮助”菜单
    dict1['help_menu'] = dict1['menu_bar'].addMenu("&Help")

    # 创建并添加“帮助内容”动作
    dict1['help_action'] = QAction("&Document", dict1['main_window'])
    dict1['help_action'].triggered.connect(lambda: show_help_dialog(dict1['main_window']))
    dict1['help_menu'].addAction(dict1['help_action'])

    dict1['help_notes'] = QAction("&Release Notes", dict1['main_window'])
    dict1['help_notes'].triggered.connect(lambda: show_notes_dialog(dict1['main_window']))
    dict1['help_menu'].addAction(dict1['help_notes'])


def show_help_dialog(parent):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Help")

    layout = QVBoxLayout()

    # 创建一个滚动区域
    scroll = QScrollArea(dialog)
    content_widget = QWidget()  # 为滚动区域设置内容widget
    content_layout = QVBoxLayout()  # 内容widget的布局

    # 使用富文本标签来显示帮助内容
    help_text = """
    <div style='text-align: left;'>
        <h2>How to Use This Application</h2>
        <p>Here are some basic instructions on how to use the application:</p>
        <ul>
            <li><b>Program:</b> Set this to the type of program you are using, such as Varo, IN, PIT, or OA. Each program requires different values and will process the image accordingly using specific correction algorithms.</li>
            <li><b>Lighting Mode:</b> Depending on the lighting condition, set this to either D50 or Dark. This will influence the choice of correction algorithms.</li>
            <li><b>Sensor Size:</b> Each program has a different sensor size, which is crucial for processing.</li>
            <li><b>Locations:</b> Specify the diagonal coordinates of the output map's location to trim the output without returning the entire map. Remember, indexing starts at zero, so the maximum value is one less than the sensor size.</li>
            <li><b>Range:</b> Determine the distance to expand the output range beyond the specified location.</li>
            <li><b>Output Raw:</b> Decide whether to output raw data by setting this to true or false.</li>
            <li><b>NVM Data Path:</b> Specify the key name as 'nvm_data_path'. Ensure that the NVM data file is not encrypted.</li>
            <li><b>Case Insensitivity:</b> The values for program, mode, and lightingMode are case-insensitive, meaning they do not distinguish between uppercase and lowercase letters.</li>
            <li><b>Path Addition:</b> You can add a 'path' to the config.json so the application automatically searches for raw files in the specified path.</li>
         </ul>
        <p>For more detailed information, please contact: <a href='mailto:Pengcheng.yan@cowellchina.com'>Pengcheng.yan@cowellchina.com</a></p>
    </div>
    """
    label = QLabel(help_text)
    label.setOpenExternalLinks(True)  # 允许打开外部链接
    label.setWordWrap(True)
    label.setOpenExternalLinks(True)  # Allow opening external links
    content_layout.addWidget(label)

    content_widget.setLayout(content_layout)
    scroll.setWidget(content_widget)
    scroll.setWidgetResizable(True)  # Make the scroll area's content widget resizable

    layout.addWidget(scroll)

    # 添加关闭按钮
    close_button = QPushButton("Close")
    close_button.clicked.connect(dialog.close)
    layout.addWidget(close_button)

    dialog.setLayout(layout)
    # 使用 show() 而不是 exec_() 来显示对话框，对话框将以非模态方式打开，这意味着它不会阻塞主事件循环
    dialog.show()


def show_notes_dialog(parent):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Update Log")

    layout = QVBoxLayout(dialog)

    # 创建一个滚动区域
    scroll = QScrollArea(dialog)
    content_widget = QWidget()  # 为滚动区域设置内容widget
    content_layout = QVBoxLayout()  # 内容widget的布局

    # 使用富文本标签来显示更新内容
    note_text = """
    <style>
        body {font-family: Arial, sans-serif;}
        h2 {color: #333;}
        div.update-section {margin-bottom: 20px;}
        div.update-section p {margin: 5px 0;}
        ul {list-style-type: square; padding-left: 20px;}
        li {margin: 3px 0;}
        p.fixes, p.features {font-weight: bold; color: #444;}
        a {color: #065A82; text-decoration: none;}
        a:hover {text-decoration: underline;}
    </style>
    <div style='text-align: left;'>
        <h2>Update Log</h2>
        <div class='update-section'>
            <strong>[2024-01-03]</strong>
            <p class='fixes'>Fixes:</p>
            <ul>
                <li>Fixed the index error of dp_comp_rev3p0 function in Varo project.</li>
            </ul>
        </div>
        <div class='update-section'>
            <strong>[2023-12-30]</strong>
            <p class='fixes'>Fixes:</p>
            <ul>
                <li>Compensate image based on FPC compensation for IN D50.</li>
            </ul>
        </div>
        <div class='update-section'>
            <strong>[2023-12-27]</strong>
            <p class='fixes'>Fixes:</p>
            <ul>
                <li>In Varo D50 mode, the image is compensated based on the average of 4 nearby Gr/Gb values.</li>
                <li>In Varo Dark mode, the image is subjected to row FPN correction and OBP cropping.</li>
            </ul>
        </div>
        <div class='update-section'>
            <strong>[2023-12-26]</strong>
            <p class='fixes'>Fixes:</p>
            <ul>
                <li>The program, mode, and lightingMode in the configuration are no longer case-sensitive.</li>
                <li>Implement the focusGains_OCLHV_1p0_Comp algorithm for image preprocessing in the Varo project.</li>
            </ul>
            <p class='features'>Features:</p>
            <ul>
                <li>Add nvm decoding of Varo, PDX, IN.</li>
                <li>Add the option to output raw data or not.</li>
            </ul>
        </div>
    <p>For any questions or concerns, please contact: <a href='mailto:Pengcheng.yan@cowellchina.com'>Pengcheng.yan@cowellchina.com</a></p>
    """

    label = QLabel(note_text)
    label.setWordWrap(True)
    label.setOpenExternalLinks(True)  # Allow opening external links
    content_layout.addWidget(label)

    content_widget.setLayout(content_layout)
    scroll.setWidget(content_widget)
    scroll.setWidgetResizable(True)  # Make the scroll area's content widget resizable

    layout.addWidget(scroll)

    # Add close button
    close_button = QPushButton("Close")
    close_button.clicked.connect(dialog.close)
    layout.addWidget(close_button)

    dialog.setLayout(layout)
    dialog.setMinimumSize(400, 300)  # Set a minimum size for the dialog
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
