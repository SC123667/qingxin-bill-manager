#!/usr/bin/env python3
import sys
import os
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox
from PySide6.QtCore import Qt

# 导入模块化组件
from core import BillManager
from ui import LoginDialog, MainWindow, PathConfigDialog
from ui.style_manager import get_main_style

def show_first_time_path_setup():
    """首次启动时显示路径设置对话框"""
    from PySide6.QtWidgets import QMessageBox
    
    # 显示首次启动提示
    reply = QMessageBox.question(
        None, "账单管理系统", 
        "🎉 欢迎使用账单管理系统！\n\n"
        "这是您首次启动，需要设置数据存储路径。\n"
        "是否现在进行路径配置？\n\n"
        "点击「是」进行配置，点击「否」使用默认路径。",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.Yes
    )
    
    if reply == QMessageBox.Yes:
        path_dialog = PathConfigDialog(None, is_first_time=True)
        if path_dialog.exec() == QDialog.Accepted:
            return True
        else:
            # 用户取消了路径设置，退出程序
            return False
    else:
        # 用户选择使用默认路径，创建默认配置
        import json
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(current_dir, "path_config.json")
        
        default_config = {
            "data_path": os.path.join(current_dir, "accounts_data"),
            "backup_path": os.path.join(current_dir, "password_backups")
        }
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
        except:
            pass
        
        return True

def check_path_config():
    """检查是否需要路径配置"""
    # 检查是否存在路径配置文件
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(current_dir, "path_config.json")
    
    # 检查是否存在任何密码文件（真正的首次启动判断）
    has_any_password_file = False
    
    # 检查默认位置的密码文件
    default_password_file = os.path.join(current_dir, "master_password.hash")
    default_accounts_dir = os.path.join(current_dir, "accounts_data")
    default_accounts_password = os.path.join(default_accounts_dir, "master_password.hash")
    
    if os.path.exists(default_password_file) or os.path.exists(default_accounts_password):
        has_any_password_file = True
    
    # 如果有配置文件，检查配置的路径是否有密码文件
    if os.path.exists(config_file):
        try:
            import json
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            configured_data_dir = config.get("data_path")
            if configured_data_dir:
                configured_password_file = os.path.join(configured_data_dir, "master_password.hash")
                if os.path.exists(configured_password_file):
                    has_any_password_file = True
        except:
            pass
    
    # 如果没有配置文件，或者没有任何密码文件（真正的首次启动），显示路径设置
    if not os.path.exists(config_file) or not has_any_password_file:
        return show_first_time_path_setup()
    
    return True

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("账单管理系统 v5.3")
    
    # 启用高DPI支持
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 应用新的样式主题
    app.setStyleSheet(get_main_style())
    
    # 检查是否需要路径配置
    if not check_path_config():
        sys.exit(0)
    
    # 创建账单管理器
    bill_manager = BillManager()
    
    # 如果是首次设置（没有密码文件），再次确认路径
    if bill_manager.is_first_time_setup():
        QMessageBox.information(
            None, "欢迎使用", 
            "🎉 欢迎使用账单管理系统！\n\n"
            f"📊 数据存储位置: {bill_manager.get_data_directory()}\n"
            f"🔐 备份存储位置: {bill_manager.get_backup_directory()}\n\n"
            "请牢记这些路径，以便日后查找您的数据。"
        )
    
    # 显示登录对话框
    login_dialog = LoginDialog(bill_manager)
    if login_dialog.exec() == QDialog.Accepted:
        bill_manager.load_data()
        
        main_window = MainWindow(bill_manager)
        main_window.show()
        
        sys.exit(app.exec())

if __name__ == "__main__":
    main()
