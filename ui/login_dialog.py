#!/usr/bin/env python3
import os
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from .style_manager import get_login_dialog_style

class LoginDialog(QDialog):
    def __init__(self, bill_manager):
        super().__init__()
        self.bill_manager = bill_manager
        self.password = None
        self.setup_ui()
        # 应用登录对话框样式
        self.setStyleSheet(get_login_dialog_style())
        
    def setup_ui(self):
        self.setWindowTitle("登录")
        self.setMinimumSize(440, 300)
        self.resize(460, 310)
        
        layout = QVBoxLayout()
        layout.setSpacing(14)
        layout.setContentsMargins(44, 34, 44, 30)
        
        title = QLabel("清账")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("titleLabel")
        title.setMinimumHeight(52)
        layout.addWidget(title)
        
        layout.addSpacing(4)
        
        is_first_time = not os.path.exists(self.bill_manager.password_file)
        
        if is_first_time:
            prompt = QLabel("设置密码")
        else:
            prompt = QLabel("密码")
        
        prompt.setAlignment(Qt.AlignCenter)
        prompt.setObjectName("subtitleLabel")
        prompt.setMinimumHeight(28)
        layout.addWidget(prompt)
        
        layout.addSpacing(6)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("密码")
        self.password_input.setMinimumHeight(44)
        layout.addWidget(self.password_input)
        
        layout.addSpacing(8)
        
        button_text = "设置" if is_first_time else "登录"
        self.login_button = QPushButton(button_text)
        self.login_button.setObjectName("primaryButton")
        self.login_button.setMinimumHeight(48)
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)
        
        layout.addSpacing(8)
        
        layout.addStretch(1)
        
        self.password_input.returnPressed.connect(self.handle_login)
        
        self.setLayout(layout)
        self.password_input.setFocus()
    
    def handle_login(self):
        password = self.password_input.text()
        
        if not password:
            QMessageBox.warning(self, "错误", "密码为空。")
            return
        
        if not os.path.exists(self.bill_manager.password_file):
            if self.bill_manager.setup_password(password):
                self.password = password
                QMessageBox.information(self, "成功", "密码已设置。")
                self.accept()
            else:
                QMessageBox.critical(self, "错误", "设置失败。")
        else:
            if self.bill_manager.verify_password(password):
                self.password = password
                self.accept()
            else:
                QMessageBox.critical(self, "错误", "密码错误。")
                self.password_input.clear()
