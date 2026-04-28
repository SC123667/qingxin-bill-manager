#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from .style_manager import get_path_config_style, apply_button_style

class PathConfigDialog(QDialog):
    def __init__(self, parent=None, is_first_time=False):
        super().__init__(parent)
        self.is_first_time = is_first_time
        self.selected_data_path = ""
        self.selected_backup_path = ""
        self.setup_ui()
        # 应用路径配置对话框样式
        self.setStyleSheet(get_path_config_style())
        
    def setup_ui(self):
        self.setWindowTitle("数据存储路径设置")
        self.setMinimumSize(820, 640)
        self.resize(860, 660)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(34, 30, 34, 30)

        header = QFrame()
        header.setObjectName("dialogHeader")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 18, 20, 18)
        header_layout.setSpacing(8)

        title = QLabel("数据存储路径配置")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("titleLabel")
        header_layout.addWidget(title)
        
        if self.is_first_time:
            info_text = "欢迎首次使用账单管理系统。请选择账单数据与密码备份的保存位置。"
        else:
            info_text = "请选择账单数据与密码备份的保存位置。"
        
        info_label = QLabel(info_text)
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        info_label.setObjectName("dialogLead")
        header_layout.addWidget(info_label)
        layout.addWidget(header)
        
        # 路径配置组
        path_group = QGroupBox("存储路径设置")
        path_group.setMinimumHeight(260)
        path_layout = QGridLayout()
        path_layout.setHorizontalSpacing(12)
        path_layout.setVerticalSpacing(12)
        path_layout.setContentsMargins(18, 26, 18, 18)
        
        # 数据路径设置
        data_label = QLabel("账单数据存储路径")
        data_label.setMinimumWidth(140)
        path_layout.addWidget(data_label, 0, 0)
        
        self.data_path_input = QLineEdit()
        self.data_path_input.setPlaceholderText("选择账单数据存储文件夹...")
        self.data_path_input.setReadOnly(True)
        self.data_path_input.setMinimumHeight(42)
        path_layout.addWidget(self.data_path_input, 0, 1)
        
        data_browse_btn = QPushButton("浏览...")
        data_browse_btn.setMinimumSize(104, 42)
        data_browse_btn.clicked.connect(self.browse_data_path)
        path_layout.addWidget(data_browse_btn, 0, 2)
        
        # 备份路径设置
        backup_label = QLabel("密码备份存储路径")
        backup_label.setMinimumWidth(140)
        path_layout.addWidget(backup_label, 1, 0)
        
        self.backup_path_input = QLineEdit()
        self.backup_path_input.setPlaceholderText("选择密码备份存储文件夹...")
        self.backup_path_input.setReadOnly(True)
        self.backup_path_input.setMinimumHeight(42)
        path_layout.addWidget(self.backup_path_input, 1, 1)
        
        backup_browse_btn = QPushButton("浏览...")
        backup_browse_btn.setMinimumSize(104, 42)
        backup_browse_btn.clicked.connect(self.browse_backup_path)
        path_layout.addWidget(backup_browse_btn, 1, 2)

        path_layout.setColumnStretch(1, 1)
        
        path_group.setLayout(path_layout)
        layout.addWidget(path_group)
        
        # 快速设置按钮
        quick_layout = QHBoxLayout()
        quick_layout.setSpacing(10)
        
        desktop_btn = QPushButton("使用桌面")
        desktop_btn.setMinimumHeight(42)
        desktop_btn.clicked.connect(self.set_desktop_path)
        quick_layout.addWidget(desktop_btn)
        
        documents_btn = QPushButton("使用文档")
        documents_btn.setMinimumHeight(42)
        documents_btn.clicked.connect(self.set_documents_path)
        quick_layout.addWidget(documents_btn)
        
        default_btn = QPushButton("使用默认")
        default_btn.setMinimumHeight(42)
        default_btn.clicked.connect(self.set_default_path)
        quick_layout.addWidget(default_btn)
        
        layout.addLayout(quick_layout)
        
        layout.addStretch()
        
        # 按钮栏
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        if not self.is_first_time:
            cancel_btn = QPushButton("取消")
            cancel_btn.setObjectName("cancelButton")
            cancel_btn.clicked.connect(self.reject)
            button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
        ok_btn = QPushButton("确定")
        ok_btn.setObjectName("primaryButton")
        ok_btn.setMinimumSize(112, 42)
        ok_btn.clicked.connect(self.save_config)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
        # 设置默认路径
        self.set_default_path()
    
    def browse_data_path(self):
        path = QFileDialog.getExistingDirectory(self, "选择账单数据存储文件夹")
        if path:
            self.data_path_input.setText(path)
            self.selected_data_path = path
    
    def browse_backup_path(self):
        path = QFileDialog.getExistingDirectory(self, "选择密码备份存储文件夹")
        if path:
            self.backup_path_input.setText(path)
            self.selected_backup_path = path
    
    def set_desktop_path(self):
        """设置为桌面路径"""
        desktop = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
        data_path = os.path.join(desktop, "账单管理数据")
        backup_path = os.path.join(desktop, "账单管理备份")
        
        self.data_path_input.setText(data_path)
        self.backup_path_input.setText(backup_path)
        self.data_path_input.setCursorPosition(0)
        self.backup_path_input.setCursorPosition(0)
        self.selected_data_path = data_path
        self.selected_backup_path = backup_path
    
    def set_documents_path(self):
        """设置为文档路径"""
        documents = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        data_path = os.path.join(documents, "账单管理数据")
        backup_path = os.path.join(documents, "账单管理备份")
        
        self.data_path_input.setText(data_path)
        self.backup_path_input.setText(backup_path)
        self.data_path_input.setCursorPosition(0)
        self.backup_path_input.setCursorPosition(0)
        self.selected_data_path = data_path
        self.selected_backup_path = backup_path
    
    def set_default_path(self):
        """设置为默认路径（程序目录）"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(current_dir)
        
        data_path = os.path.join(project_dir, "accounts_data")
        backup_path = os.path.join(project_dir, "password_backups")
        
        self.data_path_input.setText(data_path)
        self.backup_path_input.setText(backup_path)
        self.data_path_input.setCursorPosition(0)
        self.backup_path_input.setCursorPosition(0)
        self.selected_data_path = data_path
        self.selected_backup_path = backup_path
    
    def save_config(self):
        """保存配置并接受对话框"""
        data_path = self.data_path_input.text().strip()
        backup_path = self.backup_path_input.text().strip()
        
        if not data_path or not backup_path:
            QMessageBox.warning(self, "警告", "请设置数据存储路径和备份路径！")
            return
        
        # 创建目录（如果不存在）
        try:
            os.makedirs(data_path, exist_ok=True)
            os.makedirs(backup_path, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建目录失败：{e}")
            return
        
        # 保存配置到文件
        config = {
            "data_path": data_path,
            "backup_path": backup_path
        }
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(current_dir)
        config_file = os.path.join(project_dir, "path_config.json")
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败：{e}")
            return
        
        # 显示成功消息
        if self.is_first_time:
            QMessageBox.information(
                self, "设置成功",
                f"✅ 路径设置成功！\n\n"
                f"📊 数据路径：{data_path}\n"
                f"🔐 备份路径：{backup_path}\n\n"
                f"现在请设置您的主密码。"
            )
        
        self.accept()
    
    def get_data_path(self):
        return self.selected_data_path
    
    def get_backup_path(self):
        return self.selected_backup_path
