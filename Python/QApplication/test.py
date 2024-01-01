import sys
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QTreeWidget,
                               QTreeWidgetItem, QDialog, QVBoxLayout, QPushButton, QMessageBox, QLineEdit)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Configuration")
        self.setGeometry(100, 100, 600, 400)
        self.json_file_path = "config.json"
        self.tree_widget = QTreeWidget()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.tree_widget.setHeaderLabels(["Setting", "Value"])
        self.tree_widget.setColumnWidth(0, 280)
        layout.addWidget(self.tree_widget)

        # Load the config.json file
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                self.json_data = json.load(file)
                self.populate_tree(self.json_data, self.tree_widget.invisibleRootItem())
        except FileNotFoundError:
            QMessageBox.warning(self, "Error", "The config.json file was not found. A new configuration will be created.")
            self.json_data = {}
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Error", "The config.json file is malformed.")
            self.reject()

        self.tree_widget.expandAll()

        # Add a save button
        save_button = QPushButton("Save Changes")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)
        self.setLayout(layout)

    def populate_tree(self, data, parent_item):
        if isinstance(data, dict):
            for key, value in data.items():
                key_item = QTreeWidgetItem(parent_item, [key])
                key_item.setFlags(key_item.flags() & ~Qt.ItemIsEditable)
                self.populate_tree(value, key_item)
        elif isinstance(data, list):
            for i, value in enumerate(data):
                index_item = QTreeWidgetItem(parent_item, [f'Item {i}'])
                index_item.setFlags(index_item.flags() & ~Qt.ItemIsEditable)
                self.populate_tree(value, index_item)
        else:  # for simple types
            value_item = QTreeWidgetItem(parent_item, ["", json.dumps(data)])
            value_item.setFlags(value_item.flags() | Qt.ItemIsEditable)

    def save_settings(self):
        data = self.get_item_data(self.tree_widget.invisibleRootItem())
        try:
            with open(self.json_file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "Success", "The configuration has been saved to config.json.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Failure", f"Could not save the configuration: {e}")


    def get_item_data(self, item):
        data = {}
        for index in range(item.childCount()):
            child = item.child(index)
            key = child.text(0)
            if child.childCount() == 0:  # It's a value
                val = child.parent().text(0)  # Get the key from the parent
                try:
                    data[val] = json.loads(child.text(1))
                except json.JSONDecodeError:
                    data[val] = child.text(1)
            else:
                data[key] = self.get_item_data(child)
        return data


class JSONEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JSON Editor")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()

    def init_ui(self):
        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.open_settings_dialog)
        menu_bar = self.menuBar()
        menu_bar.addAction(settings_action)

    def open_settings_dialog(self):
        dialog = SettingsDialog(self)
        dialog.exec()


# Create and run the application
app = QApplication(sys.argv)
editor = JSONEditor()
editor.show()
sys.exit(app.exec())
