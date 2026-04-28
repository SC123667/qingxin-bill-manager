#!/usr/bin/env python3
"""统一 UI 样式管理器。"""

COLORS = {
    "window": "#f5f8f7",
    "surface": "#ffffff",
    "surface_soft": "#eef6f4",
    "surface_alt": "#f8fbfa",
    "sidebar": "#14312d",
    "sidebar_soft": "#1d4741",
    "sidebar_text": "#f4fbf9",
    "sidebar_muted": "#a9c9c3",
    "hover": "#e6f2ef",
    "selected": "#d7ece8",
    "text": "#17312d",
    "muted": "#64748b",
    "subtle": "#8a9a96",
    "disabled": "#a8b3af",
    "border": "#d9e6e2",
    "border_strong": "#b8d5ce",
    "primary": "#0f766e",
    "primary_hover": "#0d9488",
    "primary_pressed": "#115e59",
    "primary_soft": "#dff5f1",
    "info": "#2563eb",
    "info_soft": "#dbeafe",
    "success": "#15803d",
    "success_soft": "#dcfce7",
    "warning": "#b45309",
    "warning_soft": "#fef3c7",
    "danger": "#dc2626",
    "danger_hover": "#b91c1c",
    "danger_soft": "#fee2e2",
    "focus": "#14b8a6",
}


def get_main_style():
    """获取主窗口样式表。"""
    return f"""
    QWidget {{
        background-color: {COLORS["window"]};
        color: {COLORS["text"]};
        font-family: "PingFang SC", "Microsoft YaHei UI", "Segoe UI", Arial;
        font-size: 14px;
        selection-background-color: {COLORS["primary"]};
        selection-color: #ffffff;
    }}

    QMainWindow::separator {{
        background-color: {COLORS["border"]};
        width: 1px;
        height: 1px;
    }}

    QLabel {{
        color: {COLORS["text"]};
        background: transparent;
    }}

    QFrame#sideBar {{
        background-color: {COLORS["sidebar"]};
        border: none;
    }}

    QLabel#brandLabel {{
        color: {COLORS["sidebar_text"]};
        font-size: 24px;
        font-weight: 900;
        padding: 2px 4px 0 4px;
    }}

    QLabel#brandSubLabel {{
        color: {COLORS["sidebar_muted"]};
        font-size: 12px;
        font-weight: 600;
        padding: 0 4px;
    }}

    QPushButton#navButton {{
        background-color: transparent;
        color: {COLORS["sidebar_text"]};
        border: 1px solid transparent;
        border-radius: 8px;
        padding: 11px 12px;
        text-align: left;
        min-height: 54px;
        font-size: 13px;
        font-weight: 700;
    }}

    QPushButton#navButton:hover {{
        background-color: {COLORS["sidebar_soft"]};
        border-color: rgba(255, 255, 255, 0.08);
    }}

    QPushButton#navButton:checked {{
        background-color: {COLORS["primary"]};
        color: #ffffff;
        border-color: {COLORS["primary_hover"]};
    }}

    QPushButton#sideUtilityButton {{
        background-color: rgba(255, 255, 255, 0.07);
        color: {COLORS["sidebar_text"]};
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        min-height: 34px;
        min-width: 0;
        padding: 8px 10px;
        font-size: 13px;
        font-weight: 700;
    }}

    QPushButton#sideUtilityButton:hover {{
        background-color: {COLORS["sidebar_soft"]};
    }}

    QFrame#workspace {{
        background-color: {COLORS["window"]};
        border: none;
    }}

    QFrame#contextBar {{
        background-color: {COLORS["surface"]};
        border: none;
        border-bottom: 1px solid {COLORS["border"]};
    }}

    QStackedWidget#contentStack {{
        background-color: {COLORS["window"]};
        border: none;
    }}

    QScrollArea#pageScroll {{
        background-color: {COLORS["window"]};
        border: none;
    }}

    QScrollArea#pageScroll > QWidget > QWidget {{
        background-color: {COLORS["window"]};
    }}

    QWidget#page {{
        background-color: {COLORS["window"]};
    }}

    QLabel#pageTitle {{
        color: {COLORS["text"]};
        font-size: 28px;
        font-weight: 900;
        padding: 0;
    }}

    QLabel#pageSubtitle {{
        color: {COLORS["muted"]};
        font-size: 13px;
        font-weight: 500;
        padding: 0 0 2px 1px;
    }}

    QFrame#sectionCard {{
        background-color: {COLORS["surface"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
    }}

    QLabel#sectionTitle {{
        color: {COLORS["text"]};
        font-size: 16px;
        font-weight: 850;
        padding: 0;
    }}

    QLabel#sectionSubtitle {{
        color: {COLORS["muted"]};
        font-size: 12px;
        font-weight: 500;
        padding: 0;
    }}

    QFrame#miniPanel {{
        background-color: {COLORS["surface_alt"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
    }}

    QLabel#miniPanelTitle {{
        color: {COLORS["text"]};
        font-size: 15px;
        font-weight: 800;
    }}

    QLabel#toolbarLabel {{
        color: {COLORS["muted"]};
        font-size: 13px;
        font-weight: 600;
        padding: 0 6px;
    }}

    QLabel#noteLabel {{
        color: {COLORS["muted"]};
        font-size: 12px;
        padding: 6px 2px;
    }}

    QLabel#accentLabel {{
        color: {COLORS["primary"]};
        font-size: 15px;
        font-weight: 700;
    }}

    QFrame#metricCard {{
        background-color: {COLORS["surface"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
    }}

    QLabel#metricTitle {{
        color: {COLORS["muted"]};
        font-size: 12px;
        font-weight: 600;
    }}

    QLabel#metricValue {{
        color: {COLORS["text"]};
        font-size: 21px;
        font-weight: 800;
    }}

    QLabel#metricPositive {{
        color: {COLORS["success"]};
        font-size: 21px;
        font-weight: 800;
    }}

    QLabel#metricNegative {{
        color: {COLORS["danger"]};
        font-size: 21px;
        font-weight: 800;
    }}

    QPushButton {{
        background-color: {COLORS["surface"]};
        color: {COLORS["text"]};
        border: 1px solid {COLORS["border_strong"]};
        border-radius: 7px;
        padding: 8px 16px;
        font-size: 14px;
        font-weight: 600;
        min-height: 34px;
        min-width: 84px;
    }}

    QPushButton:hover {{
        background-color: {COLORS["hover"]};
        border-color: {COLORS["primary_hover"]};
    }}

    QPushButton:pressed {{
        background-color: {COLORS["selected"]};
        border-color: {COLORS["primary_pressed"]};
    }}

    QPushButton:disabled {{
        background-color: {COLORS["surface_alt"]};
        color: {COLORS["disabled"]};
        border-color: {COLORS["border"]};
    }}

    QPushButton#primaryButton,
    QPushButton[variant="primary"] {{
        background-color: {COLORS["primary"]};
        color: #ffffff;
        border-color: {COLORS["primary"]};
    }}

    QPushButton#primaryButton:hover,
    QPushButton[variant="primary"]:hover {{
        background-color: {COLORS["primary_hover"]};
        border-color: {COLORS["primary_hover"]};
    }}

    QPushButton#primaryButton:pressed,
    QPushButton[variant="primary"]:pressed {{
        background-color: {COLORS["primary_pressed"]};
        border-color: {COLORS["primary_pressed"]};
    }}

    QPushButton[variant="danger"] {{
        background-color: {COLORS["danger_soft"]};
        color: {COLORS["danger"]};
        border-color: #fecaca;
    }}

    QPushButton[variant="danger"]:hover {{
        background-color: {COLORS["danger"]};
        color: #ffffff;
        border-color: {COLORS["danger"]};
    }}

    QPushButton[variant="success"] {{
        background-color: {COLORS["success_soft"]};
        color: {COLORS["success"]};
        border-color: #bbf7d0;
    }}

    QPushButton[variant="success"]:hover {{
        background-color: {COLORS["success"]};
        color: #ffffff;
        border-color: {COLORS["success"]};
    }}

    QPushButton[variant="warning"] {{
        background-color: {COLORS["warning_soft"]};
        color: {COLORS["warning"]};
        border-color: #fde68a;
    }}

    QPushButton[variant="warning"]:hover {{
        background-color: {COLORS["warning"]};
        color: #ffffff;
        border-color: {COLORS["warning"]};
    }}

    QPushButton[variant="info"] {{
        background-color: {COLORS["info_soft"]};
        color: {COLORS["info"]};
        border-color: #bfdbfe;
    }}

    QPushButton[variant="info"]:hover {{
        background-color: {COLORS["info"]};
        color: #ffffff;
        border-color: {COLORS["info"]};
    }}

    QPushButton#smallButton {{
        min-height: 30px;
        min-width: 74px;
        padding: 6px 10px;
        font-size: 13px;
    }}

    QPushButton#toolButton {{
        min-height: 32px;
        min-width: 82px;
        padding: 7px 12px;
        font-size: 13px;
    }}

    QPushButton#iconButton {{
        min-height: 34px;
        min-width: 34px;
        max-width: 34px;
        padding: 7px;
    }}

    QLineEdit,
    QTextEdit,
    QPlainTextEdit,
    QDoubleSpinBox,
    QSpinBox {{
        background-color: {COLORS["surface"]};
        color: {COLORS["text"]};
        border: 1px solid {COLORS["border_strong"]};
        border-radius: 7px;
        padding: 8px 10px;
        min-height: 34px;
    }}

    QLineEdit:focus,
    QTextEdit:focus,
    QPlainTextEdit:focus,
    QDoubleSpinBox:focus,
    QSpinBox:focus {{
        border: 2px solid {COLORS["focus"]};
        padding: 7px 9px;
        background-color: #ffffff;
    }}

    QLineEdit:disabled,
    QTextEdit:disabled,
    QPlainTextEdit:disabled,
    QDoubleSpinBox:disabled,
    QSpinBox:disabled {{
        color: {COLORS["disabled"]};
        background-color: {COLORS["surface_alt"]};
    }}

    QComboBox {{
        background-color: {COLORS["surface"]};
        color: {COLORS["text"]};
        border: 1px solid {COLORS["border_strong"]};
        border-radius: 7px;
        padding: 8px 34px 8px 10px;
        min-height: 34px;
    }}

    QComboBox:hover {{
        border-color: {COLORS["primary_hover"]};
    }}

    QComboBox:focus {{
        border: 2px solid {COLORS["focus"]};
        padding: 7px 33px 7px 9px;
    }}

    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 28px;
        border: none;
        border-left: 1px solid {COLORS["border"]};
        border-top-right-radius: 7px;
        border-bottom-right-radius: 7px;
        background-color: {COLORS["surface_soft"]};
    }}

    QComboBox::down-arrow {{
        image: none;
        width: 0;
        height: 0;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid {COLORS["muted"]};
        margin-right: 8px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {COLORS["surface"]};
        color: {COLORS["text"]};
        border: 1px solid {COLORS["border_strong"]};
        selection-background-color: {COLORS["primary_soft"]};
        selection-color: {COLORS["text"]};
        padding: 4px;
        outline: none;
    }}

    QTableWidget {{
        background-color: {COLORS["surface"]};
        alternate-background-color: {COLORS["surface_alt"]};
        color: {COLORS["text"]};
        gridline-color: {COLORS["border"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        selection-background-color: {COLORS["primary_soft"]};
        selection-color: {COLORS["text"]};
        outline: none;
        font-size: 13px;
    }}

    QTableWidget::item {{
        padding: 7px 8px;
        border: none;
    }}

    QTableWidget::item:selected {{
        background-color: {COLORS["primary_soft"]};
        color: {COLORS["text"]};
    }}

    QTableWidget::item:hover {{
        background-color: {COLORS["hover"]};
    }}

    QHeaderView::section {{
        background-color: {COLORS["surface_soft"]};
        color: {COLORS["muted"]};
        padding: 10px 8px;
        border: none;
        border-right: 1px solid {COLORS["border"]};
        border-bottom: 1px solid {COLORS["border"]};
        font-weight: 700;
        font-size: 13px;
    }}

    QTabWidget::pane {{
        background-color: {COLORS["surface"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        top: -1px;
    }}

    QTabBar::tab {{
        background-color: transparent;
        color: {COLORS["muted"]};
        padding: 11px 18px;
        margin-right: 4px;
        border: 1px solid transparent;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        font-size: 14px;
        font-weight: 700;
    }}

    QTabBar::tab:selected {{
        background-color: {COLORS["surface"]};
        color: {COLORS["primary"]};
        border-color: {COLORS["border"]};
        border-bottom-color: {COLORS["surface"]};
    }}

    QTabBar::tab:hover {{
        color: {COLORS["primary"]};
        background-color: {COLORS["hover"]};
    }}

    QGroupBox {{
        background-color: {COLORS["surface"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        margin-top: 14px;
        padding: 18px 14px 14px 14px;
        font-size: 14px;
        font-weight: 600;
    }}

    QGroupBox::title {{
        color: {COLORS["primary"]};
        subcontrol-origin: margin;
        left: 14px;
        padding: 0 8px;
        background-color: {COLORS["window"]};
        font-size: 14px;
        font-weight: 800;
    }}

    QToolBar {{
        background-color: {COLORS["surface"]};
        border: none;
        border-bottom: 1px solid {COLORS["border"]};
        padding: 8px 12px;
        spacing: 8px;
    }}

    QToolBar QWidget {{
        background: transparent;
    }}

    QToolBar::separator {{
        background-color: {COLORS["border"]};
        width: 1px;
        margin: 6px 8px;
    }}

    QToolBar QPushButton {{
        min-height: 32px;
        min-width: 78px;
        padding: 7px 12px;
        margin: 0 2px;
    }}

    QToolButton {{
        background-color: transparent;
        color: {COLORS["text"]};
        border: 1px solid transparent;
        border-radius: 7px;
        padding: 7px 10px;
        min-height: 32px;
    }}

    QToolButton:hover {{
        background-color: {COLORS["hover"]};
        border-color: {COLORS["border_strong"]};
    }}

    QMenuBar {{
        background-color: {COLORS["surface"]};
        color: {COLORS["text"]};
        border-bottom: 1px solid {COLORS["border"]};
        padding: 4px 8px;
    }}

    QMenuBar::item {{
        background-color: transparent;
        padding: 7px 12px;
        margin: 0 2px;
        border-radius: 7px;
    }}

    QMenuBar::item:selected {{
        background-color: {COLORS["hover"]};
        color: {COLORS["primary"]};
    }}

    QMenu {{
        background-color: {COLORS["surface"]};
        color: {COLORS["text"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        padding: 6px;
    }}

    QMenu::item {{
        padding: 8px 28px;
        border-radius: 6px;
    }}

    QMenu::item:selected {{
        background-color: {COLORS["primary_soft"]};
        color: {COLORS["primary"]};
    }}

    QStatusBar {{
        background-color: {COLORS["surface"]};
        color: {COLORS["muted"]};
        border-top: 1px solid {COLORS["border"]};
        font-size: 13px;
        padding: 2px 8px;
    }}

    QCheckBox,
    QRadioButton {{
        color: {COLORS["text"]};
        spacing: 8px;
        font-size: 14px;
        background: transparent;
    }}

    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 1px solid {COLORS["border_strong"]};
        border-radius: 5px;
        background-color: {COLORS["surface"]};
    }}

    QCheckBox::indicator:checked {{
        background-color: {COLORS["primary"]};
        border-color: {COLORS["primary"]};
    }}

    QRadioButton::indicator {{
        width: 18px;
        height: 18px;
        border: 1px solid {COLORS["border_strong"]};
        border-radius: 9px;
        background-color: {COLORS["surface"]};
    }}

    QRadioButton::indicator:checked {{
        background-color: {COLORS["primary"]};
        border: 4px solid {COLORS["surface"]};
    }}

    QProgressBar {{
        background-color: {COLORS["surface_soft"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 7px;
        text-align: center;
        color: {COLORS["muted"]};
        height: 18px;
    }}

    QProgressBar::chunk {{
        background-color: {COLORS["primary"]};
        border-radius: 6px;
    }}

    QScrollBar:vertical {{
        background-color: transparent;
        width: 12px;
        margin: 2px;
    }}

    QScrollBar::handle:vertical {{
        background-color: {COLORS["border_strong"]};
        border-radius: 6px;
        min-height: 34px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS["primary_hover"]};
    }}

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0;
        border: none;
        background: none;
    }}

    QMessageBox,
    QDialog {{
        background-color: {COLORS["window"]};
        color: {COLORS["text"]};
    }}

    QMessageBox QPushButton {{
        min-width: 84px;
    }}
    """


def get_login_dialog_style():
    """获取登录对话框专用样式。"""
    return get_main_style() + f"""
    QDialog {{
        background-color: {COLORS["window"]};
    }}

    QLabel#titleLabel {{
        color: {COLORS["primary"]};
        font-size: 24px;
        font-weight: 800;
        padding: 4px 8px;
    }}

    QLabel#subtitleLabel {{
        color: {COLORS["muted"]};
        font-size: 14px;
        padding: 4px;
    }}

    QPushButton#cancelButton {{
        background-color: {COLORS["surface"]};
        color: {COLORS["muted"]};
        border-color: {COLORS["border_strong"]};
    }}
    """


def get_path_config_style():
    """获取路径配置对话框样式。"""
    return get_main_style() + f"""
    QFrame#dialogHeader {{
        background-color: {COLORS["surface"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
    }}

    QLabel#titleLabel {{
        color: {COLORS["primary"]};
        font-size: 24px;
        font-weight: 800;
        padding: 4px;
    }}

    QLabel#dialogLead {{
        color: {COLORS["muted"]};
        font-size: 14px;
        font-weight: 500;
    }}
    """


def apply_button_style(button, style_type="default"):
    """为单个按钮设置语义样式。"""
    if style_type in {"primary", "small", "tool", "icon"}:
        object_names = {
            "primary": "primaryButton",
            "small": "smallButton",
            "tool": "toolButton",
            "icon": "iconButton",
        }
        button.setObjectName(object_names[style_type])
    elif style_type in {"danger", "success", "warning", "info"}:
        button.setProperty("variant", style_type)

    button.style().unpolish(button)
    button.style().polish(button)
