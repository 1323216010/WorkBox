from PySide6.QtWidgets import QTextEdit, QFileDialog
from PySide6.QtGui import QAction


class CustomTextEdit(QTextEdit):
    def contextMenuEvent(self, event):
        # 创建标准菜单
        menu = self.createStandardContextMenu()

        # 添加 "Clear All" 动作
        clear_all_action = QAction("Clear All", self)
        clear_all_action.triggered.connect(self.clear)
        menu.addAction(clear_all_action)

        # 添加 "Save As" 动作
        save_as_action = QAction("Save As...", self)
        save_as_action.triggered.connect(self.saveAs)
        menu.addAction(save_as_action)

        # 展示菜单
        menu.exec_(event.globalPos())

    def saveAs(self):
        # 弹出文件保存对话框
        filename, _ = QFileDialog.getSaveFileName(self, "Save as", "", "Text Files (*.txt);;All Files (*)")
        if filename:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(self.toPlainText())
