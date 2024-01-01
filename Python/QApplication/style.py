def apply_stylesheet(app):
    app.setStyleSheet("""
* {
    font-family: 'Segoe UI', sans-serif;
    font-size: 10pt;
    color: #333;
}

QMainWindow {
    background-color: #f2f2f2;
}

QPushButton#buttonLabel {
    font-size: 12pt; /* 字体大小与timeLabel一致 */
    font-weight: bold; /* 如果需要，可以加粗以匹配其他UI元素 */
    color: white;
    border: none;
    padding: 12px 24px;
    background-color: #495057; /* 使用timeLabel的暗灰色背景 */
    border-radius: 4px;
    cursor: pointer;
}

QPushButton#buttonLabel:hover {
    background-color: #5a6268; /* 可以保持这个颜色不变 */
}

QPushButton#buttonLabel:pressed {
    background-color: #545b62; /* 可以保持这个颜色不变 */
}

QPushButton#buttonLabel:disabled {
    background-color: #a9a9a9;
    color: #ccc;
}

QLabel#timeLabel {
    font-size: 12pt;
    font-weight: bold;
    color: #FFFFFF;
    background-color: #6c757d; /* 使用buttonLabel的更柔和的灰色 */
    padding: 12px 24px;
    border-radius: 4px;
    margin: 0;
    display: inline-block;
    vertical-align: middle;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

QTextEdit {
    border: 1px solid #c5c5c5;
    border-radius: 4px;
    background-color: #fff;
    padding: 2px;
}

QLineEdit {
    border: 2px solid #6c757d; /* 可以保持这个颜色不变 */
    border-radius: 5px;
    padding: 7px 10px;
    margin-bottom: 10px;
}

QLineEdit:focus {
    border: 2px solid #5a6268; /* 可以保持这个颜色不变 */
}

    """)
