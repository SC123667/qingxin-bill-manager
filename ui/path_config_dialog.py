#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import glob
import shutil
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from .style_manager import get_path_config_style, apply_button_style


DATA_FILE_PATTERNS = ("single_*.encrypted", "multi_*.encrypted", "*.encrypted")
PASSWORD_FILE_NAME = "master_password.hash"
CONFIG_FILE_NAME = "path_config.json"


def _normalize_directory(path):
    """Return a stable absolute directory path."""
    return os.path.abspath(os.path.expanduser(path))


def _list_existing_account_files(data_dir):
    """Find encrypted account files in a directory."""
    if not data_dir or not os.path.isdir(data_dir):
        return []

    files = []
    for pattern in DATA_FILE_PATTERNS:
        files.extend(glob.glob(os.path.join(data_dir, pattern)))

    return sorted(set(files))


def _find_password_file(data_dir, selected_dir):
    candidates = [
        os.path.join(data_dir, PASSWORD_FILE_NAME),
        os.path.join(selected_dir, PASSWORD_FILE_NAME),
        os.path.join(os.path.dirname(data_dir), PASSWORD_FILE_NAME),
    ]

    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return _normalize_directory(candidate)

    return ""


def _read_path_config(config_dir):
    config_file = os.path.join(config_dir, CONFIG_FILE_NAME)
    if not os.path.exists(config_file):
        return None

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception:
        return None

    data_path = config.get("data_path")
    backup_path = config.get("backup_path")
    if data_path and not os.path.isabs(data_path):
        data_path = os.path.join(config_dir, data_path)
    if backup_path and not os.path.isabs(backup_path):
        backup_path = os.path.join(config_dir, backup_path)

    return {
        "data_path": _normalize_directory(data_path) if data_path else "",
        "backup_path": _normalize_directory(backup_path) if backup_path else "",
    }


def _guess_backup_path(data_dir, selected_dir, config_backup_path=""):
    candidates = []
    if config_backup_path:
        candidates.append(config_backup_path)

    data_parent = os.path.dirname(data_dir)
    selected_parent = os.path.dirname(selected_dir)
    candidates.extend([
        os.path.join(data_parent, "password_backups"),
        os.path.join(selected_dir, "password_backups"),
        os.path.join(selected_parent, "password_backups"),
        os.path.join(data_parent, "账单管理备份"),
        os.path.join(selected_dir, "账单管理备份"),
    ])

    for candidate in candidates:
        if candidate and os.path.isdir(candidate):
            return _normalize_directory(candidate)

    return _normalize_directory(candidates[0] if candidates else os.path.join(data_parent, "password_backups"))


def detect_existing_data_paths(selected_path):
    """Detect an existing data directory from a folder selected by the user.

    Supports selecting the data directory itself, an old project directory that
    contains accounts_data, or a directory containing path_config.json.
    """
    selected_dir = _normalize_directory(selected_path)
    if not os.path.isdir(selected_dir):
        return None

    configured = _read_path_config(selected_dir)
    if configured and configured["data_path"]:
        data_dir = configured["data_path"]
        password_file = _find_password_file(data_dir, selected_dir)
        account_files = _list_existing_account_files(data_dir)
        if password_file:
            return {
                "data_path": data_dir,
                "backup_path": _guess_backup_path(data_dir, selected_dir, configured["backup_path"]),
                "matched_files": [password_file] + account_files,
                "password_source": password_file,
                "source": "path_config",
            }

    accounts_data_dir = os.path.join(selected_dir, "accounts_data")
    nested_password_file = ""
    nested_account_files = []
    if os.path.isdir(accounts_data_dir):
        nested_password_file = _find_password_file(accounts_data_dir, selected_dir)
        nested_account_files = _list_existing_account_files(accounts_data_dir)

    if nested_password_file:
        return {
            "data_path": _normalize_directory(accounts_data_dir),
            "backup_path": _guess_backup_path(accounts_data_dir, selected_dir),
            "matched_files": [nested_password_file] + nested_account_files,
            "password_source": nested_password_file,
            "source": "accounts_data",
        }

    direct_password_file = _find_password_file(selected_dir, selected_dir)
    direct_account_files = _list_existing_account_files(selected_dir)
    if direct_password_file:
        return {
            "data_path": selected_dir,
            "backup_path": _guess_backup_path(selected_dir, selected_dir),
            "matched_files": [direct_password_file] + direct_account_files,
            "password_source": direct_password_file,
            "source": "direct",
        }

    return None


class PathConfigDialog(QDialog):
    def __init__(self, parent=None, is_first_time=False):
        super().__init__(parent)
        self.is_first_time = is_first_time
        self.selected_data_path = ""
        self.selected_backup_path = ""
        self.uses_existing_data = False
        self.existing_password_source = ""
        self.setup_ui()
        # 应用路径配置对话框样式
        self.setStyleSheet(get_path_config_style())
        
    def setup_ui(self):
        self.setWindowTitle("数据存储路径设置")
        self.setMinimumSize(860, 700)
        self.resize(900, 730)
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
            info_text = "欢迎首次使用账单管理系统。您可以创建新的数据目录，也可以读取电脑上已有的账单数据。"
        else:
            info_text = "请选择账单数据与密码备份的保存位置，也可以切换到已有数据目录。"
        
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

        import_group = QFrame()
        import_group.setObjectName("importPanel")
        import_layout = QHBoxLayout(import_group)
        import_layout.setContentsMargins(18, 14, 18, 14)
        import_layout.setSpacing(12)

        import_text_layout = QVBoxLayout()
        import_text_layout.setSpacing(4)

        import_title = QLabel("读取已有数据")
        import_title.setObjectName("importTitle")
        import_text_layout.addWidget(import_title)

        self.import_status_label = QLabel("可选择旧版程序目录、accounts_data 数据目录，或包含 path_config.json 的目录。")
        self.import_status_label.setObjectName("importHint")
        self.import_status_label.setWordWrap(True)
        import_text_layout.addWidget(self.import_status_label)

        import_layout.addLayout(import_text_layout, 1)

        import_existing_btn = QPushButton("读取已有数据目录")
        import_existing_btn.setObjectName("importButton")
        import_existing_btn.setMinimumSize(156, 42)
        import_existing_btn.clicked.connect(self.browse_existing_data_path)
        import_layout.addWidget(import_existing_btn)

        layout.addWidget(import_group)
        
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
            detected = detect_existing_data_paths(path)
            if detected:
                self.selected_data_path = detected["data_path"]
                self.selected_backup_path = detected["backup_path"]
                self.data_path_input.setText(self.selected_data_path)
                self.backup_path_input.setText(self.selected_backup_path)
                self.uses_existing_data = True
                self.existing_password_source = detected["password_source"]
            else:
                self.data_path_input.setText(path)
                self.selected_data_path = path
                self.uses_existing_data = False
                self.existing_password_source = ""
            self.data_path_input.setCursorPosition(0)
            self.backup_path_input.setCursorPosition(0)
            self.update_import_status()
    
    def browse_backup_path(self):
        path = QFileDialog.getExistingDirectory(self, "选择密码备份存储文件夹")
        if path:
            self.backup_path_input.setText(path)
            self.selected_backup_path = path
            self.uses_existing_data = self.path_has_existing_data(self.selected_data_path)
            self.update_import_status()

    def browse_existing_data_path(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "选择已有账单数据目录",
            QStandardPaths.writableLocation(QStandardPaths.HomeLocation)
        )
        if not path:
            return

        detected = detect_existing_data_paths(path)
        if not detected:
            QMessageBox.warning(
                self,
                "未识别到已有数据",
                "没有在所选目录中找到清账数据。\n\n"
                "请尝试选择以下任一目录：\n"
                "• 包含 master_password.hash 的数据目录\n"
                "• 旧程序目录（其中有 master_password.hash 与 accounts_data）\n"
                "• 包含 path_config.json 的旧程序目录"
            )
            return

        data_path = detected["data_path"]
        backup_path = detected["backup_path"]
        matched_count = len(detected["matched_files"])

        self.data_path_input.setText(data_path)
        self.backup_path_input.setText(backup_path)
        self.data_path_input.setCursorPosition(0)
        self.backup_path_input.setCursorPosition(0)
        self.selected_data_path = data_path
        self.selected_backup_path = backup_path
        self.uses_existing_data = True
        self.existing_password_source = detected["password_source"]

        self.import_status_label.setText(
            f"已识别到 {matched_count} 个已有数据文件。保存后将使用原主密码登录并读取该目录。"
        )

    def path_has_existing_data(self, data_path):
        detected = detect_existing_data_paths(data_path)
        self.existing_password_source = detected["password_source"] if detected else ""
        return bool(detected)

    def update_import_status(self):
        if self.uses_existing_data:
            self.import_status_label.setText("已选择已有数据目录。保存后将使用原主密码登录并读取该目录。")
        else:
            self.import_status_label.setText("可选择旧版程序目录、accounts_data 数据目录，或包含 path_config.json 的目录。")
    
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
        self.uses_existing_data = False
        self.existing_password_source = ""
        self.update_import_status()
    
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
        self.uses_existing_data = False
        self.existing_password_source = ""
        self.update_import_status()
    
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
        self.uses_existing_data = self.path_has_existing_data(data_path)
        self.update_import_status()
    
    def save_config(self):
        """保存配置并接受对话框"""
        data_path = self.data_path_input.text().strip()
        backup_path = self.backup_path_input.text().strip()
        
        if not data_path or not backup_path:
            QMessageBox.warning(self, "警告", "请设置数据存储路径和备份路径！")
            return

        self.uses_existing_data = self.path_has_existing_data(data_path)
        
        # 创建目录（如果不存在）
        try:
            os.makedirs(data_path, exist_ok=True)
            os.makedirs(backup_path, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建目录失败：{e}")
            return

        password_target = os.path.join(data_path, PASSWORD_FILE_NAME)
        if self.uses_existing_data and self.existing_password_source and self.existing_password_source != password_target:
            try:
                shutil.copy2(self.existing_password_source, password_target)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"迁移主密码文件失败：{e}")
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
            next_step = "现在请输入已有数据的原主密码。" if self.uses_existing_data else "现在请设置您的主密码。"
            QMessageBox.information(
                self, "设置成功",
                f"✅ 路径设置成功！\n\n"
                f"📊 数据路径：{data_path}\n"
                f"🔐 备份路径：{backup_path}\n\n"
                f"{next_step}"
            )
        
        self.accept()
    
    def get_data_path(self):
        return self.selected_data_path
    
    def get_backup_path(self):
        return self.selected_backup_path
