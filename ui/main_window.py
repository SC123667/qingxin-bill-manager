#!/usr/bin/env python3
from datetime import datetime
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from core.export_manager import ExportManager
from .style_manager import apply_button_style

class MainWindow(QMainWindow):
    def __init__(self, bill_manager):
        super().__init__()
        self.bill_manager = bill_manager
        self.export_manager = ExportManager(bill_manager)
        self.adding_bill = False  # 防止重复添加的标志
        self.recent_bills_limit = 20
        self.show_all_recent_bills = False
        # 初始化账本列表
        self.bill_manager.load_accounts_list()
        self.setup_ui()
        self.load_data()
        self.update_window_title()
        
        # 初始化多人模式界面状态
        self.update_mode_button_text()
        self.update_person_toolbar_visibility()
        self.update_add_bill_person_visibility()
        self.update_export_person_visibility()
        
    def setup_ui(self):
        self.setWindowTitle("账单管理系统")
        self.setGeometry(80, 80, 1360, 860)
        self.setMinimumSize(1180, 760)
        
        self.create_menu_bar()
        self.create_status_bar()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        shell_layout = QHBoxLayout(central_widget)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        sidebar = self._create_sidebar()
        shell_layout.addWidget(sidebar)

        workspace = QFrame()
        workspace.setObjectName("workspace")
        workspace_layout = QVBoxLayout(workspace)
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        workspace_layout.setSpacing(0)

        workspace_layout.addWidget(self._create_context_bar())

        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("contentStack")
        self.content_stack.addWidget(self.create_overview_tab())
        self.content_stack.addWidget(self.create_add_bill_tab())
        self.content_stack.addWidget(self.create_search_tab())
        self.content_stack.addWidget(self.create_transfer_tab())
        self.content_stack.addWidget(self.create_export_tab())
        self.content_stack.addWidget(self.create_account_management_tab())
        workspace_layout.addWidget(self.content_stack, 1)

        shell_layout.addWidget(workspace, 1)
        self._switch_page(0)

    def _create_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sideBar")
        sidebar.setFixedWidth(224)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 22, 18, 18)
        layout.setSpacing(10)

        brand = QLabel("清新账本")
        brand.setObjectName("brandLabel")
        layout.addWidget(brand)

        subtitle = QLabel("本地优先的专业记账")
        subtitle.setObjectName("brandSubLabel")
        layout.addWidget(subtitle)
        layout.addSpacing(18)

        self.nav_buttons = []
        nav_items = [
            ("总览", "预算、支出与分类统计"),
            ("记一笔", "快速录入新的账单"),
            ("账单流水", "搜索与管理历史记录"),
            ("转账平账", "多人账本结算"),
            ("导出报表", "Excel 与图表导出"),
            ("账本设置", "账本与数据设置"),
        ]
        for index, (title, desc) in enumerate(nav_items):
            button = self._create_nav_button(title, desc, index)
            self.nav_buttons.append(button)
            layout.addWidget(button)

        layout.addStretch(1)

        refresh_btn = QPushButton("刷新数据")
        refresh_btn.setObjectName("sideUtilityButton")
        refresh_btn.clicked.connect(self.load_data)
        layout.addWidget(refresh_btn)

        path_btn = QPushButton("数据路径")
        path_btn.setObjectName("sideUtilityButton")
        path_btn.clicked.connect(self.show_path_config_dialog)
        layout.addWidget(path_btn)

        return sidebar

    def _create_nav_button(self, title, desc, index):
        button = QPushButton(f"{title}\n{desc}")
        button.setObjectName("navButton")
        button.setCheckable(True)
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(lambda checked=False, page=index: self._switch_page(page))
        return button

    def _switch_page(self, index):
        if hasattr(self, "content_stack"):
            self.content_stack.setCurrentIndex(index)
        for i, button in enumerate(getattr(self, "nav_buttons", [])):
            button.setChecked(i == index)

    def _create_context_bar(self):
        bar = QFrame()
        bar.setObjectName("contextBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(24, 14, 24, 14)
        layout.setSpacing(12)

        account_label = self._make_toolbar_label("当前账本")
        layout.addWidget(account_label)

        self.account_combo = QComboBox()
        self.account_combo.addItems(self.bill_manager.accounts_list)
        self.account_combo.setCurrentText(self.bill_manager.current_account)
        self.account_combo.setMinimumWidth(190)
        self.account_combo.setMaximumWidth(260)
        self.account_combo.activated.connect(self.on_account_combo_activated)
        layout.addWidget(self.account_combo)

        new_account_btn = QPushButton("新建")
        apply_button_style(new_account_btn, "info")
        new_account_btn.clicked.connect(self.show_new_account_dialog)
        layout.addWidget(new_account_btn)

        rename_account_btn = QPushButton("重命名")
        apply_button_style(rename_account_btn, "warning")
        rename_account_btn.clicked.connect(self.rename_current_account)
        layout.addWidget(rename_account_btn)

        delete_account_btn = QPushButton("删除")
        apply_button_style(delete_account_btn, "danger")
        delete_account_btn.clicked.connect(self.delete_current_account)
        layout.addWidget(delete_account_btn)

        layout.addSpacing(12)

        self.mode_toggle_btn = QPushButton()
        apply_button_style(self.mode_toggle_btn, "tool")
        self.mode_toggle_btn.clicked.connect(self.toggle_person_mode)
        layout.addWidget(self.mode_toggle_btn)

        self.person_label = self._make_toolbar_label("当前人员")
        layout.addWidget(self.person_label)

        self.person_combo = QComboBox()
        self.person_combo.setMinimumWidth(130)
        self.person_combo.setMaximumWidth(190)
        self.person_combo.activated.connect(self.on_person_combo_activated)
        layout.addWidget(self.person_combo)

        self.add_person_btn = QPushButton("添加人员")
        apply_button_style(self.add_person_btn, "success")
        self.add_person_btn.clicked.connect(self.add_person)
        layout.addWidget(self.add_person_btn)

        self.remove_person_btn = QPushButton("删除人员")
        apply_button_style(self.remove_person_btn, "danger")
        self.remove_person_btn.clicked.connect(self.remove_person)
        layout.addWidget(self.remove_person_btn)

        layout.addStretch(1)

        quick_add_btn = QPushButton("记一笔")
        apply_button_style(quick_add_btn, "primary")
        quick_add_btn.clicked.connect(lambda: self._switch_page(1))
        layout.addWidget(quick_add_btn)

        return bar

    def _create_page(self, title, subtitle):
        scroll = QScrollArea()
        scroll.setObjectName("pageScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        page = QWidget()
        page.setObjectName("page")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(26, 24, 26, 26)
        layout.setSpacing(18)

        title_label = QLabel(title)
        title_label.setObjectName("pageTitle")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("pageSubtitle")
        subtitle_label.setWordWrap(True)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)

        scroll.setWidget(page)
        return scroll, layout

    def _make_section(self, title, subtitle=None):
        section = QFrame()
        section.setObjectName("sectionCard")
        layout = QVBoxLayout(section)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignTop)

        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        layout.addWidget(title_label)

        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setObjectName("sectionSubtitle")
            subtitle_label.setWordWrap(True)
            layout.addWidget(subtitle_label)

        return section, layout

    def _make_action_row(self):
        row = QHBoxLayout()
        row.setSpacing(10)
        row.addStretch(1)
        return row

    def _make_toolbar_label(self, text):
        label = QLabel(text)
        label.setObjectName("toolbarLabel")
        return label

    def _make_note_label(self, text):
        label = QLabel(text)
        label.setObjectName("noteLabel")
        label.setWordWrap(True)
        return label

    def _make_metric_card(self, title, value="¥0.00", object_name="metricValue"):
        card = QFrame()
        card.setObjectName("metricCard")
        card.setMinimumHeight(88)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setObjectName("metricTitle")
        value_label = QLabel(value)
        value_label.setObjectName(object_name)

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()
        return card, value_label

    def _configure_table(self, table):
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(38)
        table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)

    def _begin_table_update(self, table):
        table.setUpdatesEnabled(False)

    def _end_table_update(self, table):
        table.resizeRowsToContents()
        table.setUpdatesEnabled(True)
        table.viewport().update()
    
    def create_account_toolbar(self):
        """创建账本管理工具栏"""
        account_toolbar = self.addToolBar('账本管理')
        account_toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        account_toolbar.setMovable(False)
        
        # 添加一些间距
        spacer_left = QWidget()
        spacer_left.setFixedWidth(10)
        account_toolbar.addWidget(spacer_left)
        
        # 账本选择部分
        account_label = self._make_toolbar_label('当前账本')
        account_toolbar.addWidget(account_label)
        
        # 账本下拉框
        self.account_combo = QComboBox()
        self.account_combo.addItems(self.bill_manager.accounts_list)
        self.account_combo.setCurrentText(self.bill_manager.current_account)
        self.account_combo.setMinimumWidth(180)
        # 修复切换响应问题：使用activated信号而不是currentTextChanged
        self.account_combo.activated.connect(self.on_account_combo_activated)
        account_toolbar.addWidget(self.account_combo)
        
        # 添加间距
        spacer_mid = QWidget()
        spacer_mid.setFixedWidth(20)
        account_toolbar.addWidget(spacer_mid)
        
        # 新建账本按钮
        new_account_btn = QPushButton('新建账本')
        apply_button_style(new_account_btn, 'info')
        new_account_btn.clicked.connect(self.show_new_account_dialog)
        account_toolbar.addWidget(new_account_btn)
        
        # 删除账本按钮
        delete_account_btn = QPushButton('删除账本')
        apply_button_style(delete_account_btn, 'danger')
        delete_account_btn.clicked.connect(self.delete_current_account)
        account_toolbar.addWidget(delete_account_btn)
        
        # 重命名账本按钮
        rename_account_btn = QPushButton('重命名')
        apply_button_style(rename_account_btn, 'warning')
        rename_account_btn.clicked.connect(self.rename_current_account)
        account_toolbar.addWidget(rename_account_btn)
        
        # 添加弹性空间，让按钮靠左
        spacer_right = QWidget()
        spacer_right.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        account_toolbar.addWidget(spacer_right)
    
    def create_person_toolbar(self):
        """创建多人模式工具栏"""
        self.person_toolbar = self.addToolBar('人员管理')
        self.person_toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.person_toolbar.setMovable(False)
        
        # 添加一些间距
        spacer_left = QWidget()
        spacer_left.setFixedWidth(10)
        self.person_toolbar.addWidget(spacer_left)
        
        # 模式切换按钮
        self.mode_toggle_btn = QPushButton()
        self.update_mode_button_text()
        self.mode_toggle_btn.setMinimumHeight(35)
        apply_button_style(self.mode_toggle_btn, 'warning')
        self.mode_toggle_btn.clicked.connect(self.toggle_person_mode)
        self.person_toolbar.addWidget(self.mode_toggle_btn)
        
        # 添加间距
        spacer_mid1 = QWidget()
        spacer_mid1.setFixedWidth(15)
        self.person_toolbar.addWidget(spacer_mid1)
        
        # 人员选择部分（只在多人模式显示）
        self.person_label = self._make_toolbar_label('当前人员')
        self.person_label_action = self.person_toolbar.addWidget(self.person_label)
        
        # 人员下拉框
        self.person_combo = QComboBox()
        self.person_combo.setMinimumWidth(120)
        self.person_combo.setMinimumHeight(35)
        self.person_combo.activated.connect(self.on_person_combo_activated)
        self.person_combo_action = self.person_toolbar.addWidget(self.person_combo)
        
        # 添加间距
        spacer_mid2 = QWidget()
        spacer_mid2.setFixedWidth(15)
        self.person_toolbar.addWidget(spacer_mid2)
        
        # 人员管理按钮
        self.add_person_btn = QPushButton('添加人员')
        self.add_person_btn.setMinimumHeight(35)
        apply_button_style(self.add_person_btn, 'success')
        self.add_person_btn.clicked.connect(self.add_person)
        self.add_person_action = self.person_toolbar.addWidget(self.add_person_btn)
        
        self.remove_person_btn = QPushButton('删除人员')
        self.remove_person_btn.setMinimumHeight(35)
        apply_button_style(self.remove_person_btn, 'danger')
        self.remove_person_btn.clicked.connect(self.remove_person)
        self.remove_person_action = self.person_toolbar.addWidget(self.remove_person_btn)
        
        # 添加弹性空间，让按钮靠左
        spacer_right = QWidget()
        spacer_right.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.person_toolbar.addWidget(spacer_right)
        
        # 初始化工具栏显示状态
        self.update_person_toolbar_visibility()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu('文件')
        
        refresh_action = QAction('刷新数据', self)
        refresh_action.triggered.connect(self.load_data)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 账本菜单
        account_menu = menubar.addMenu('账本')
        
        new_account_action = QAction('新建账本', self)
        new_account_action.triggered.connect(self.show_new_account_dialog)
        account_menu.addAction(new_account_action)
        
        delete_account_action = QAction('删除当前账本', self)
        delete_account_action.triggered.connect(self.delete_current_account)
        account_menu.addAction(delete_account_action)
        
        rename_account_action = QAction('重命名当前账本', self)
        rename_account_action.triggered.connect(self.rename_current_account)
        account_menu.addAction(rename_account_action)
        
        # 设置菜单
        settings_menu = menubar.addMenu('设置')
        
        path_config_action = QAction('数据存储路径设置', self)
        path_config_action.triggered.connect(self.show_path_config_dialog)
        settings_menu.addAction(path_config_action)
    
    def create_status_bar(self):
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪")
    
    def create_overview_tab(self):
        widget, layout = self._create_page("财务总览", "集中查看预算、支出余额和分类占比，快速判断当前账本的资金状态。")
        
        budget_group, budget_layout_outer = self._make_section("预算控制", "设置全局预算后，系统会自动计算当前支出和剩余额度。")
        budget_layout = QHBoxLayout()
        budget_layout.setSpacing(12)
        
        budget_layout.addWidget(QLabel("总预算:"))
        self.budget_input = QDoubleSpinBox()
        self.budget_input.setRange(0, 999999999)
        self.budget_input.setSuffix(" 元")
        self.budget_input.setMinimumWidth(180)
        self.budget_input.setMaximumWidth(260)
        budget_layout.addWidget(self.budget_input)
        
        set_budget_btn = QPushButton("设置预算")
        apply_button_style(set_budget_btn, 'primary')
        set_budget_btn.clicked.connect(self.set_budget)
        budget_layout.addWidget(set_budget_btn)
        
        budget_layout.addStretch()
        budget_layout_outer.addLayout(budget_layout)
        layout.addWidget(budget_group)
        
        balance_layout = QGridLayout()
        balance_layout.setHorizontalSpacing(14)
        balance_layout.setVerticalSpacing(14)
        total_budget_card, self.total_budget_label = self._make_metric_card("全局预算")
        total_spent_card, self.total_spent_label = self._make_metric_card("总支出")
        balance_card, self.balance_label = self._make_metric_card("预算余额", object_name="metricPositive")
        balance_layout.addWidget(total_budget_card, 0, 0)
        balance_layout.addWidget(total_spent_card, 0, 1)
        balance_layout.addWidget(balance_card, 0, 2)
        balance_layout.setColumnStretch(0, 1)
        balance_layout.setColumnStretch(1, 1)
        balance_layout.setColumnStretch(2, 1)
        layout.addLayout(balance_layout)
        
        overview_group, overview_layout = self._make_section("分类支出统计", "双击备注列可以维护分类备注，用于导出总账或日后复盘。")
        self.overview_table = QTableWidget()
        self._configure_table(self.overview_table)
        self.overview_table.setMinimumHeight(390)
        self.overview_table.setColumnCount(4)
        self.overview_table.setHorizontalHeaderLabels(["分类", "总金额", "百分比", "备注"])
        
        # 设置列宽比例
        header = self.overview_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.resizeSection(0, 140)  # 分类列（增加宽度以显示长分类名）
        header.resizeSection(1, 100)  # 总金额列
        header.resizeSection(2, 80)   # 百分比列
        
        # 允许双击编辑备注
        self.overview_table.itemDoubleClicked.connect(self.edit_category_note)
        
        overview_layout.addWidget(self.overview_table)
        
        note_hint = self._make_note_label("提示：双击备注列可编辑分类备注")
        overview_layout.addWidget(note_hint)
        
        layout.addWidget(overview_group, 1)
        
        return widget
    
    def create_add_bill_tab(self):
        widget, layout = self._create_page("记一笔", "高频录入区保持紧凑，右侧同步展示最近记录，适合连续记账。")

        content_layout = QHBoxLayout()
        content_layout.setSpacing(18)

        form_group, form_outer_layout = self._make_section("新增账单")
        form_group.setMinimumWidth(380)
        form_group.setMaximumWidth(460)
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # 分类选择和管理
        category_layout = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(250)  # 设置最小宽度以显示长分类名
        self.category_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        categories_without_budget = [cat for cat in self.bill_manager.categories if cat != "总预算"]
        self.category_combo.addItems(categories_without_budget)
        category_layout.addWidget(self.category_combo)
        
        add_category_btn = QPushButton("添加分类")
        add_category_btn.setMaximumWidth(80)
        apply_button_style(add_category_btn, 'info')
        add_category_btn.clicked.connect(self.add_custom_category)
        category_layout.addWidget(add_category_btn)
        
        remove_category_btn = QPushButton("删除分类")
        remove_category_btn.setMaximumWidth(80)
        apply_button_style(remove_category_btn, 'danger')
        remove_category_btn.clicked.connect(self.remove_custom_category)
        category_layout.addWidget(remove_category_btn)
        
        form_layout.addRow("分类:", category_layout)
        
        # 人员选择（只在多人模式显示）
        self.person_select_layout = QHBoxLayout()
        self.add_bill_person_combo = QComboBox()
        self.add_bill_person_combo.setMinimumWidth(200)
        self.add_bill_person_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.person_select_layout.addWidget(self.add_bill_person_combo)
        
        # 创建人员选择的容器widget，方便控制显示/隐藏
        self.person_select_widget = QWidget()
        self.person_select_widget.setLayout(self.person_select_layout)
        form_layout.addRow("人员:", self.person_select_widget)
        
        # 使用QLineEdit替代QDoubleSpinBox以支持自由输入小数点
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        # 设置验证器，只允许输入数字和小数点
        amount_validator = QDoubleValidator(0.00, 999999999.99, 2)
        amount_validator.setNotation(QDoubleValidator.StandardNotation)
        self.amount_input.setValidator(amount_validator)
        
        # 创建带单位的输入组件
        amount_widget = QWidget()
        amount_layout = QHBoxLayout(amount_widget)
        amount_layout.setContentsMargins(0, 0, 0, 0)
        amount_layout.addWidget(self.amount_input)
        amount_layout.addWidget(QLabel("元"))
        form_layout.addRow("金额:", amount_widget)
        
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("备注信息（可选）")
        form_layout.addRow("描述:", self.description_input)
        
        add_btn = QPushButton("添加账单")
        add_btn.setMinimumHeight(44)
        apply_button_style(add_btn, 'primary')
        add_btn.clicked.connect(self.add_bill)
        form_layout.addRow("", add_btn)
        form_outer_layout.addWidget(form_widget)
        
        # 添加键盘支持
        self.description_input.returnPressed.connect(self.add_bill)
        
        # 设置Tab顺序，方便键盘操作
        self.setTabOrder(self.category_combo, self.amount_input)
        self.setTabOrder(self.amount_input, self.description_input)
        self.setTabOrder(self.description_input, add_btn)
        
        content_layout.addWidget(form_group, 0, Qt.AlignTop)
        
        recent_group, recent_layout = self._make_section("最近账单", "默认展示最近 20 条记录，可切换查看全部历史记录。")
        self.recent_table = QTableWidget()
        self._configure_table(self.recent_table)
        self.recent_table.setMinimumHeight(520)
        self.recent_table.setColumnCount(5)
        self.recent_table.setHorizontalHeaderLabels(["选择", "分类", "金额", "描述", "日期"])
        self.recent_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        header = self.recent_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.resizeSection(0, 60)    # 选择列
        header.resizeSection(1, 120)   # 分类列（增加宽度）
        header.resizeSection(2, 100)   # 金额列
        header.resizeSection(4, 150)   # 日期列
        
        recent_layout.addWidget(self.recent_table)
        
        # 添加删除按钮到最近账单区域
        recent_delete_layout = QHBoxLayout()
        
        delete_recent_btn = QPushButton("删除选中")
        apply_button_style(delete_recent_btn, 'danger')
        delete_recent_btn.clicked.connect(self.delete_selected_recent_bills)
        recent_delete_layout.addWidget(delete_recent_btn)
        
        select_all_recent_btn = QPushButton("全选")
        apply_button_style(select_all_recent_btn, 'small')
        select_all_recent_btn.clicked.connect(self.select_all_recent_bills)
        recent_delete_layout.addWidget(select_all_recent_btn)
        
        clear_recent_selection_btn = QPushButton("清除选择")
        apply_button_style(clear_recent_selection_btn, 'small')
        clear_recent_selection_btn.clicked.connect(self.clear_recent_selection)
        recent_delete_layout.addWidget(clear_recent_selection_btn)

        self.toggle_recent_scope_btn = QPushButton("显示全部")
        apply_button_style(self.toggle_recent_scope_btn, 'info')
        self.toggle_recent_scope_btn.clicked.connect(self.toggle_recent_bills_scope)
        recent_delete_layout.addWidget(self.toggle_recent_scope_btn)
        
        recent_delete_layout.addStretch()
        recent_layout.addLayout(recent_delete_layout)

        self.recent_scope_label = QLabel("当前显示最近 20 条")
        self.recent_scope_label.setObjectName("noteLabel")
        recent_layout.addWidget(self.recent_scope_label)
        
        content_layout.addWidget(recent_group, 1)
        layout.addLayout(content_layout, 1)
        
        return widget
    
    def create_search_tab(self):
        widget, layout = self._create_page("账单流水", "按关键词检索历史账单，并在同一个工作区完成选择、清除和删除。")
        
        search_group, search_outer_layout = self._make_section("流水检索")
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        search_layout.addWidget(QLabel("关键词:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入分类、描述、金额或日期关键词...")
        search_layout.addWidget(self.search_input, 1)
        
        search_btn = QPushButton("搜索")
        apply_button_style(search_btn, 'primary')
        search_btn.clicked.connect(self.search_bills)
        search_layout.addWidget(search_btn)
        search_outer_layout.addLayout(search_layout)
        
        layout.addWidget(search_group)
        
        results_group, results_layout = self._make_section("检索结果", "结果表格保留原有删除逻辑，勾选左侧复选框后执行批量操作。")
        self.search_table = QTableWidget()
        self._configure_table(self.search_table)
        self.search_table.setMinimumHeight(520)
        self.search_table.setColumnCount(5)
        self.search_table.setHorizontalHeaderLabels(["选择", "分类", "金额", "描述", "日期"])
        self.search_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        header = self.search_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.resizeSection(0, 60)    # 选择列
        header.resizeSection(1, 120)   # 分类列（增加宽度）
        header.resizeSection(2, 100)   # 金额列
        header.resizeSection(4, 150)   # 日期列
        
        results_layout.addWidget(self.search_table)
        
        # 添加删除按钮
        delete_buttons_layout = QHBoxLayout()
        
        delete_selected_btn = QPushButton("删除选中")
        apply_button_style(delete_selected_btn, 'danger')
        delete_selected_btn.clicked.connect(self.delete_selected_search_results)
        delete_buttons_layout.addWidget(delete_selected_btn)
        
        select_all_btn = QPushButton("全选")
        apply_button_style(select_all_btn, 'small')
        select_all_btn.clicked.connect(self.select_all_search_results)
        delete_buttons_layout.addWidget(select_all_btn)
        
        clear_selection_btn = QPushButton("清除选择")
        apply_button_style(clear_selection_btn, 'small')
        clear_selection_btn.clicked.connect(self.clear_search_selection)
        delete_buttons_layout.addWidget(clear_selection_btn)
        
        delete_buttons_layout.addStretch()
        results_layout.addLayout(delete_buttons_layout)
        
        layout.addWidget(results_group)
        
        self.search_input.returnPressed.connect(self.search_bills)
        
        return widget
    
    def create_transfer_tab(self):
        """创建转账平账标签页"""
        widget, layout = self._create_page("转账平账", "多人账本下设置主账单人员，记录转账并查看每个人的结算状态。")

        top_layout = QHBoxLayout()
        top_layout.setSpacing(18)
        
        master_group, master_layout = self._make_section("主账单设置")
        master_group.setMinimumWidth(360)
        
        # 当前主账单显示
        current_master_layout = QHBoxLayout()
        current_master_layout.addWidget(QLabel("当前主账单:"))
        self.current_master_label = QLabel("未设置")
        self.current_master_label.setObjectName("accentLabel")
        current_master_layout.addWidget(self.current_master_label)
        current_master_layout.addStretch()
        master_layout.addLayout(current_master_layout)
        
        # 设置主账单
        set_master_layout = QHBoxLayout()
        set_master_layout.addWidget(QLabel("设置主账单:"))
        self.master_person_combo = QComboBox()
        self.master_person_combo.setMinimumWidth(150)
        set_master_layout.addWidget(self.master_person_combo)
        
        set_master_btn = QPushButton("设置为主账单")
        apply_button_style(set_master_btn, 'success')
        set_master_btn.clicked.connect(self.set_master_person)
        set_master_layout.addWidget(set_master_btn)
        set_master_layout.addStretch()
        master_layout.addLayout(set_master_layout)
        
        top_layout.addWidget(master_group)
        
        transfer_group, transfer_layout = self._make_section("转账录入")
        
        # 转账表单
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.from_person_combo = QComboBox()
        self.from_person_combo.setMinimumWidth(150)
        form_layout.addRow("转账方:", self.from_person_combo)
        
        self.to_person_combo = QComboBox()
        self.to_person_combo.setMinimumWidth(150)
        form_layout.addRow("接收方:", self.to_person_combo)
        
        # 使用QLineEdit替代QDoubleSpinBox以支持自由输入小数点
        self.transfer_amount_input = QLineEdit()
        self.transfer_amount_input.setPlaceholderText("0.00")
        # 设置验证器
        transfer_validator = QDoubleValidator(0.00, 999999999.99, 2)
        transfer_validator.setNotation(QDoubleValidator.StandardNotation)
        self.transfer_amount_input.setValidator(transfer_validator)
        
        # 创建带单位的输入组件
        transfer_amount_widget = QWidget()
        transfer_amount_layout = QHBoxLayout(transfer_amount_widget)
        transfer_amount_layout.setContentsMargins(0, 0, 0, 0)
        transfer_amount_layout.addWidget(self.transfer_amount_input)
        transfer_amount_layout.addWidget(QLabel("元"))
        form_layout.addRow("转账金额:", transfer_amount_widget)
        
        self.transfer_description_input = QLineEdit()
        self.transfer_description_input.setPlaceholderText("转账说明（可选）")
        form_layout.addRow("转账说明:", self.transfer_description_input)
        
        transfer_layout.addLayout(form_layout)
        
        # 转账按钮
        transfer_buttons_layout = QHBoxLayout()
        
        manual_transfer_btn = QPushButton("手动转账")
        apply_button_style(manual_transfer_btn, 'primary')
        manual_transfer_btn.clicked.connect(self.manual_transfer)
        transfer_buttons_layout.addWidget(manual_transfer_btn)
        
        quick_balance_btn = QPushButton("快速平账")
        apply_button_style(quick_balance_btn, 'warning')
        quick_balance_btn.clicked.connect(self.quick_balance)
        transfer_buttons_layout.addWidget(quick_balance_btn)
        
        transfer_buttons_layout.addStretch()
        transfer_layout.addLayout(transfer_buttons_layout)
        
        top_layout.addWidget(transfer_group, 1)
        layout.addLayout(top_layout)
        
        tables_layout = QHBoxLayout()
        tables_layout.setSpacing(18)

        balance_group, balance_layout = self._make_section("人员余额状况")
        self.balance_table = QTableWidget()
        self._configure_table(self.balance_table)
        self.balance_table.setMinimumHeight(360)
        self.balance_table.setColumnCount(4)
        self.balance_table.setHorizontalHeaderLabels(["人员", "支出总额", "收入总额", "账单余额"])
        
        header = self.balance_table.horizontalHeader()
        header.setStretchLastSection(False)
        for col in range(4):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        header.resizeSection(0, 100)
        header.resizeSection(1, 120)
        header.resizeSection(2, 120)
        header.resizeSection(3, 120)
        
        balance_layout.addWidget(self.balance_table)
        tables_layout.addWidget(balance_group, 1)
        
        history_group, history_layout = self._make_section("转账记录")
        self.transfer_history_table = QTableWidget()
        self._configure_table(self.transfer_history_table)
        self.transfer_history_table.setMinimumHeight(360)
        self.transfer_history_table.setColumnCount(5)
        self.transfer_history_table.setHorizontalHeaderLabels(["人员", "金额", "说明", "日期", "类型"])
        
        header = self.transfer_history_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.resizeSection(0, 100)
        header.resizeSection(1, 100)
        header.resizeSection(3, 150)
        header.resizeSection(4, 80)
        
        history_layout.addWidget(self.transfer_history_table)
        tables_layout.addWidget(history_group, 1)
        layout.addLayout(tables_layout, 1)
        
        return widget
    
    def create_export_tab(self):
        widget, layout = self._create_page("导出报表", "按当前账本数据生成 Excel 明细或 PNG 图表，适合归档与分享。")
        
        settings_group, settings_layout = self._make_section("报表设置")
        
        # 时间导出选项
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("时间选项:"))
        self.include_time_checkbox = QCheckBox("包含时间信息")
        self.include_time_checkbox.setChecked(True)  # 默认包含时间
        time_layout.addWidget(self.include_time_checkbox)
        time_layout.addStretch()
        settings_layout.addLayout(time_layout)
        
        # 导出模式选项
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("导出模式:"))
        self.export_mode_group = QButtonGroup()
        self.detail_mode_radio = QRadioButton("明细模式")
        self.summary_mode_radio = QRadioButton("总账模式")
        self.detail_mode_radio.setChecked(True)  # 默认明细模式
        
        self.export_mode_group.addButton(self.detail_mode_radio)
        self.export_mode_group.addButton(self.summary_mode_radio)
        
        mode_layout.addWidget(self.detail_mode_radio)
        mode_layout.addWidget(self.summary_mode_radio)
        mode_layout.addStretch()
        settings_layout.addLayout(mode_layout)
        
        # 添加说明文本
        help_text = self._make_note_label("明细模式：导出所有账单的详细信息\n总账模式：仅导出各分类的汇总金额和备注")
        settings_layout.addWidget(help_text)
        
        layout.addWidget(settings_group)
        
        self.person_export_group, person_export_layout = self._make_section("人员导出设置")
        
        # 人员选择选项
        person_layout = QHBoxLayout()
        person_layout.addWidget(QLabel("导出人员:"))
        
        self.export_person_group = QButtonGroup()
        self.current_person_radio = QRadioButton("当前人员")
        self.all_persons_radio = QRadioButton("所有人员")
        self.specific_person_radio = QRadioButton("指定人员:")
        self.current_person_radio.setChecked(True)  # 默认当前人员
        
        self.export_person_group.addButton(self.current_person_radio)
        self.export_person_group.addButton(self.all_persons_radio)
        self.export_person_group.addButton(self.specific_person_radio)
        
        person_layout.addWidget(self.current_person_radio)
        person_layout.addWidget(self.all_persons_radio)
        person_layout.addWidget(self.specific_person_radio)
        
        # 指定人员选择下拉框
        self.export_person_combo = QComboBox()
        self.export_person_combo.setMinimumWidth(150)
        self.export_person_combo.setEnabled(False)  # 默认禁用
        person_layout.addWidget(self.export_person_combo)
        
        person_layout.addStretch()
        person_export_layout.addLayout(person_layout)
        
        # 连接指定人员单选按钮信号
        self.specific_person_radio.toggled.connect(
            lambda checked: self.export_person_combo.setEnabled(checked)
        )
        
        # 添加人员导出说明
        person_help_text = self._make_note_label("当前人员：导出当前选中人员的数据\n所有人员：导出所有人员的数据（多人模式）\n指定人员：导出选择的特定人员数据")
        person_export_layout.addWidget(person_help_text)
        
        layout.addWidget(self.person_export_group)
        
        # 初始化人员导出组的显示状态
        self.update_export_person_visibility()
        
        export_group, export_layout = self._make_section("生成文件")
        
        export_cards = QHBoxLayout()
        export_cards.setSpacing(14)

        excel_card = QFrame()
        excel_card.setObjectName("miniPanel")
        excel_layout = QVBoxLayout(excel_card)
        excel_layout.setContentsMargins(16, 14, 16, 16)
        excel_layout.setSpacing(10)
        excel_title = QLabel("Excel 明细/总账")
        excel_title.setObjectName("miniPanelTitle")
        excel_layout.addWidget(excel_title)
        excel_layout.addWidget(self._make_note_label("适合继续统计、筛选或打印归档。"))
        excel_btn = QPushButton("导出为 Excel")
        apply_button_style(excel_btn, 'primary')
        excel_btn.clicked.connect(self.export_excel)
        excel_layout.addWidget(excel_btn)
        excel_layout.addStretch(1)
        export_cards.addWidget(excel_card)

        png_card = QFrame()
        png_card.setObjectName("miniPanel")
        png_layout = QVBoxLayout(png_card)
        png_layout.setContentsMargins(16, 14, 16, 16)
        png_layout.setSpacing(10)
        png_title = QLabel("PNG 支出图表")
        png_title.setObjectName("miniPanelTitle")
        png_layout.addWidget(png_title)
        png_layout.addWidget(self._make_note_label("适合快速查看分类分布或发送给他人。"))
        png_btn = QPushButton("导出为 PNG 图表")
        apply_button_style(png_btn, 'info')
        png_btn.clicked.connect(self.export_png)
        png_layout.addWidget(png_btn)
        png_layout.addStretch(1)
        export_cards.addWidget(png_card)
        export_layout.addLayout(export_cards)
        
        layout.addWidget(export_group)
        layout.addStretch()
        
        return widget
    
    def create_account_management_tab(self):
        """创建账本管理标签页"""
        widget, layout = self._create_page("账本设置", "管理多个账本的创建、切换、重命名和删除，当前账本会同步显示在顶部状态栏。")
        
        current_group, current_layout = self._make_section("当前账本")
        
        self.current_account_label = QLabel(f"当前账本: {self.bill_manager.current_account}")
        self.current_account_label.setObjectName("accentLabel")
        current_layout.addWidget(self.current_account_label)
        
        layout.addWidget(current_group)
        
        list_group, list_layout = self._make_section("所有账本", "双击非当前账本可直接切换。删除操作会再次确认。")
        
        self.accounts_table = QTableWidget()
        self._configure_table(self.accounts_table)
        self.accounts_table.setMinimumHeight(430)
        self.accounts_table.setColumnCount(3)
        self.accounts_table.setHorizontalHeaderLabels(["账本名称", "状态", "操作"])
        self.accounts_table.cellDoubleClicked.connect(self.on_account_table_double_click)
        
        header = self.accounts_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.resizeSection(1, 120)
        
        list_layout.addWidget(self.accounts_table)
        layout.addWidget(list_group, 1)
        
        button_group, button_group_layout = self._make_section("账本操作")
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        new_account_btn = QPushButton("新建账本")
        apply_button_style(new_account_btn, 'info')
        new_account_btn.clicked.connect(self.show_new_account_dialog)
        button_layout.addWidget(new_account_btn)
        
        delete_account_btn = QPushButton("删除选中账本")
        apply_button_style(delete_account_btn, 'danger')
        delete_account_btn.clicked.connect(self.delete_selected_account)
        button_layout.addWidget(delete_account_btn)
        
        rename_account_btn = QPushButton("重命名选中账本")
        apply_button_style(rename_account_btn, 'warning')
        rename_account_btn.clicked.connect(self.rename_selected_account)
        button_layout.addWidget(rename_account_btn)
        
        button_layout.addStretch()
        button_group_layout.addLayout(button_layout)
        layout.addWidget(button_group)
        
        return widget
    
    def set_budget(self):
        budget = self.budget_input.value()
        
        # 使用全局预算设置
        if self.bill_manager.set_total_budget(budget):
            self.load_data()
            self.status_bar.showMessage(f"全局预算已设置为 ¥{budget:.2f}")
        else:
            self.status_bar.showMessage("预算设置失败，请输入有效数值")
    
    def add_bill(self):
        # 防止重复触发
        if self.adding_bill:
            return
            
        category = self.category_combo.currentText()
        amount_text = self.amount_input.text().strip()
        description = self.description_input.text().strip()
        
        # 验证金额输入
        try:
            amount = float(amount_text) if amount_text else 0
        except ValueError:
            amount = 0
            
        if amount <= 0:
            self.status_bar.showMessage("请输入大于0的金额")
            self.amount_input.setFocus()
            self.amount_input.selectAll()
            return
        
        # 设置添加标志
        self.adding_bill = True
        
        try:
            # 获取目标人员
            target_person = None
            if self.bill_manager.is_multi_person_mode_enabled() and self.person_select_widget.isVisible():
                target_person = self.add_bill_person_combo.currentText()
            
            if self.bill_manager.add_bill(category, amount, description, target_person):
                # 成功添加，清除输入并更新界面
                self.amount_input.clear()
                self.description_input.clear()
                self.load_data()
                
                # 在多人模式下显示人员信息
                if self.bill_manager.is_multi_person_mode_enabled() and target_person:
                    self.status_bar.showMessage(f"✅ 已为 {target_person} 添加 {category}: ¥{amount:.2f}")
                else:
                    self.status_bar.showMessage(f"✅ 已添加 {category}: ¥{amount:.2f}")
                
                # 聚焦到金额输入框，方便继续添加
                self.amount_input.setFocus()
            else:
                self.status_bar.showMessage("❌ 账单添加失败，请重试")
                
        except Exception as e:
            self.status_bar.showMessage(f"❌ 添加失败: {str(e)}")
            
        finally:
            # 重置添加标志
            self.adding_bill = False
    
    def search_bills(self):
        keyword = self.search_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "提示", "请输入搜索关键词!")
            return
        
        self._perform_search(keyword)
    
    def _perform_search(self, keyword):
        """执行搜索（内部方法，不检查关键词）"""
        results = self.bill_manager.search_bills(keyword)
        
        self._begin_table_update(self.search_table)
        try:
            self.search_table.setRowCount(len(results))
            for i, result in enumerate(results):
                checkbox = QCheckBox()
                self.search_table.setCellWidget(i, 0, checkbox)
                
                self.search_table.setItem(i, 1, QTableWidgetItem(result["category"]))
                self.search_table.setItem(i, 2, QTableWidgetItem(f"¥{result['amount']:.2f}"))
                self.search_table.setItem(i, 3, QTableWidgetItem(result["description"]))
                self.search_table.setItem(i, 4, QTableWidgetItem(result["date"]))
        finally:
            self._end_table_update(self.search_table)
        
        self.status_bar.showMessage(f"找到 {len(results)} 条记录")
    
    def select_all_search_results(self):
        """全选搜索结果"""
        for i in range(self.search_table.rowCount()):
            checkbox = self.search_table.cellWidget(i, 0)
            if checkbox:
                checkbox.setChecked(True)
    
    def clear_search_selection(self):
        """清除搜索结果选择"""
        for i in range(self.search_table.rowCount()):
            checkbox = self.search_table.cellWidget(i, 0)
            if checkbox:
                checkbox.setChecked(False)
    
    def delete_selected_search_results(self):
        """删除选中的搜索结果"""
        selected_bills = []
        
        for i in range(self.search_table.rowCount()):
            checkbox = self.search_table.cellWidget(i, 0)
            if checkbox and checkbox.isChecked():
                category = self.search_table.item(i, 1).text()
                amount_text = self.search_table.item(i, 2).text()
                amount = float(amount_text.replace('¥', '').replace(',', ''))
                description = self.search_table.item(i, 3).text()
                date = self.search_table.item(i, 4).text()
                
                # 根据模式获取账单列表
                if self.bill_manager.is_multi_person_mode_enabled():
                    # 多人模式
                    current_person = self.bill_manager.get_current_person()
                    if current_person in self.bill_manager.bills:
                        bills = self.bill_manager.bills[current_person].get(category, [])
                    else:
                        bills = []
                else:
                    # 单人模式 - 数据结构是 {"默认": {category: [bills]}}
                    if "默认" in self.bill_manager.bills:
                        bills = self.bill_manager.bills["默认"].get(category, [])
                    else:
                        bills = []
                
                # 在账单列表中找到匹配的账单索引
                for j, bill in enumerate(bills):
                    if (bill["amount"] == amount and 
                        bill.get("description", "") == description and 
                        bill.get("date", "") == date):
                        selected_bills.append((category, j))
                        break
        
        if not selected_bills:
            QMessageBox.warning(self, "提示", "请先选择要删除的账单！\n\n请勾选账单左侧的复选框。")
            return
        
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除选中的 {len(selected_bills)} 条账单吗?\n\n此操作不可撤销!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            deleted_bills = self.bill_manager.delete_bills_batch(selected_bills)
            if deleted_bills:
                self.load_data()  # 刷新数据
                # 如果当前有搜索关键词，重新执行搜索
                keyword = self.search_input.text().strip()
                if keyword:
                    self._perform_search(keyword)
                QMessageBox.information(self, "成功", f"已删除 {len(deleted_bills)} 条账单!")
                self.status_bar.showMessage(f"✅ 已删除 {len(deleted_bills)} 条账单")
            else:
                QMessageBox.critical(self, "错误", "删除失败!")
    
    def select_all_recent_bills(self):
        """全选最近账单"""
        for i in range(self.recent_table.rowCount()):
            checkbox = self.recent_table.cellWidget(i, 0)
            if checkbox:
                checkbox.setChecked(True)
    
    def clear_recent_selection(self):
        """清除最近账单选择"""
        for i in range(self.recent_table.rowCount()):
            checkbox = self.recent_table.cellWidget(i, 0)
            if checkbox:
                checkbox.setChecked(False)

    def toggle_recent_bills_scope(self):
        """切换最近账单显示范围。"""
        self.show_all_recent_bills = not self.show_all_recent_bills
        self.update_recent_bills_table()
    
    def delete_selected_recent_bills(self):
        """删除选中的最近账单"""
        selected_bills = []
        
        for i in range(self.recent_table.rowCount()):
            checkbox = self.recent_table.cellWidget(i, 0)
            if checkbox and checkbox.isChecked():
                category = self.recent_table.item(i, 1).text()
                amount_text = self.recent_table.item(i, 2).text()
                amount = float(amount_text.replace('¥', '').replace(',', ''))
                description = self.recent_table.item(i, 3).text()
                date = self.recent_table.item(i, 4).text()
                source_index = self.recent_table.item(i, 1).data(Qt.UserRole)
                if isinstance(source_index, int):
                    selected_bills.append((category, source_index))
                    continue
                
                # 根据模式获取账单列表
                if self.bill_manager.is_multi_person_mode_enabled():
                    # 多人模式
                    current_person = self.bill_manager.get_current_person()
                    if current_person in self.bill_manager.bills:
                        bills = self.bill_manager.bills[current_person].get(category, [])
                    else:
                        bills = []
                else:
                    # 单人模式 - 数据结构是 {"默认": {category: [bills]}}
                    if "默认" in self.bill_manager.bills:
                        bills = self.bill_manager.bills["默认"].get(category, [])
                    else:
                        bills = []
                
                # 在账单列表中找到匹配的账单索引
                for j, bill in enumerate(bills):
                    if (bill["amount"] == amount and 
                        bill.get("description", "") == description and 
                        bill.get("date", "") == date):
                        selected_bills.append((category, j))
                        break
        
        if not selected_bills:
            QMessageBox.warning(self, "提示", "请先选择要删除的账单！\n\n请勾选账单左侧的复选框。")
            return
        
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除选中的 {len(selected_bills)} 条账单吗?\n\n此操作不可撤销!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            deleted_bills = self.bill_manager.delete_bills_batch(selected_bills)
            if deleted_bills:
                self.load_data()  # 刷新数据
                QMessageBox.information(self, "成功", f"已删除 {len(deleted_bills)} 条账单!")
                self.status_bar.showMessage(f"✅ 已删除 {len(deleted_bills)} 条账单")
            else:
                QMessageBox.critical(self, "错误", "删除失败!")
    
    def edit_category_note(self, item):
        """编辑分类备注"""
        row = item.row()
        col = item.column()
        
        # 只允许编辑备注列（第3列）
        if col != 3:
            return
        
        # 获取分类名称
        category_item = self.overview_table.item(row, 0)
        if not category_item:
            return
            
        category = category_item.text()
        if category == "总预算" or category == "全局预算":
            return
        
        # 获取当前备注
        current_note = self.bill_manager.get_category_note(category)
        
        # 显示编辑对话框
        note, ok = QInputDialog.getText(
            self, f"编辑 {category} 备注", 
            "请输入备注:", 
            QLineEdit.Normal, current_note)
        
        if ok:
            # 保存备注
            if self.bill_manager.set_category_note(category, note):
                # 更新表格显示
                self.overview_table.setItem(row, 3, QTableWidgetItem(note))
                self.status_bar.showMessage(f"✅ 已更新 {category} 的备注")
            else:
                QMessageBox.critical(self, "错误", "备注保存失败!")
    
    def update_window_title(self):
        """更新窗口标题显示当前账本和人员"""
        title = f"账单管理系统 - {self.bill_manager.current_account}"
        if self.bill_manager.is_multi_person_mode_enabled():
            current_person = self.bill_manager.get_current_person()
            title += f" - {current_person}"
        self.setWindowTitle(title)
    
    def on_account_combo_activated(self, index):
        """处理账本下拉框选择事件 - 修复多次点击问题"""
        account_name = self.account_combo.itemText(index)
        if account_name and account_name != self.bill_manager.current_account:
            # 临时断开信号连接，避免循环触发
            self.account_combo.activated.disconnect()
            self.switch_account(account_name)
            # 重新连接信号
            self.account_combo.activated.connect(self.on_account_combo_activated)
    
    def switch_account(self, account_name):
        """切换账本"""
        if account_name == self.bill_manager.current_account:
            return
            
        if self.bill_manager.switch_account(account_name):
            # 更新界面数据
            self.load_data()
            self.update_window_title()
            
            # 更新下拉框选中项（不触发信号）
            self.account_combo.blockSignals(True)
            self.account_combo.setCurrentText(account_name)
            self.account_combo.blockSignals(False)
            
            # 更新其他界面元素
            if hasattr(self, 'current_account_label'):
                self.current_account_label.setText(f"当前账本: {account_name}")
            if hasattr(self, 'accounts_table'):
                self.update_accounts_table()
                
            self.status_bar.showMessage(f"✅ 已切换到账本: {account_name}")
        else:
            QMessageBox.critical(self, "错误", "切换账本失败!")
            # 恢复下拉框到之前的选择
            self.account_combo.blockSignals(True)
            self.account_combo.setCurrentText(self.bill_manager.current_account)
            self.account_combo.blockSignals(False)
    
    def show_new_account_dialog(self):
        """显示新建账本对话框"""
        account_name, ok = QInputDialog.getText(
            self, "新建账本", "请输入账本名称:", 
            QLineEdit.Normal, "")
        
        if ok and account_name:
            account_name = account_name.strip()
            if not account_name:
                QMessageBox.warning(self, "错误", "账本名称不能为空!")
                return
                
            if account_name in self.bill_manager.accounts_list:
                QMessageBox.warning(self, "错误", "账本已存在!")
                return
                
            if self.bill_manager.create_new_account(account_name):
                # 更新界面
                self.account_combo.addItem(account_name)
                if hasattr(self, 'accounts_table'):
                    self.update_accounts_table()
                QMessageBox.information(self, "成功", f"账本 '{account_name}' 创建成功!")
                self.status_bar.showMessage(f"账本 '{account_name}' 创建成功")
            else:
                QMessageBox.critical(self, "错误", "创建账本失败!")
    
    def delete_current_account(self):
        """删除当前账本"""
        current = self.bill_manager.current_account
        
        # 检查是否只剩一个账本
        if len(self.bill_manager.accounts_list) <= 1:
            QMessageBox.warning(self, "提示", "至少需要保留一个账本!")
            return
            
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除账本 '{current}' 吗?\n\n此操作不可撤销，所有数据将被永久删除!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success, message = self.bill_manager.delete_account(current)
            if success:
                # 更新界面
                index = self.account_combo.findText(current)
                if index >= 0:
                    self.account_combo.removeItem(index)
                    
                # 更新下拉框选中项
                self.account_combo.setCurrentText(self.bill_manager.current_account)
                    
                self.load_data()
                self.update_window_title()
                if hasattr(self, 'current_account_label'):
                    self.current_account_label.setText(f"当前账本: {self.bill_manager.current_account}")
                if hasattr(self, 'accounts_table'):
                    self.update_accounts_table()
                QMessageBox.information(self, "成功", message)
                self.status_bar.showMessage(f"账本 '{current}' 已删除")
            else:
                QMessageBox.critical(self, "错误", message)
    
    def delete_selected_account(self):
        """删除选中的账本"""
        current_row = self.accounts_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "提示", "请选择要删除的账本!")
            return
            
        account_name = self.accounts_table.item(current_row, 0).text()
        
        # 检查是否只剩一个账本
        if len(self.bill_manager.accounts_list) <= 1:
            QMessageBox.warning(self, "提示", "至少需要保留一个账本!")
            return
            
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除账本 '{account_name}' 吗?\n\n此操作不可撤销，所有数据将被永久删除!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success, message = self.bill_manager.delete_account(account_name)
            if success:
                # 更新界面
                index = self.account_combo.findText(account_name)
                if index >= 0:
                    self.account_combo.removeItem(index)
                    
                # 更新下拉框选中项
                self.account_combo.setCurrentText(self.bill_manager.current_account)
                    
                if account_name == self.bill_manager.current_account:
                    self.load_data()
                    self.update_window_title()
                    if hasattr(self, 'current_account_label'):
                        self.current_account_label.setText(f"当前账本: {self.bill_manager.current_account}")
                    
                self.update_accounts_table()
                QMessageBox.information(self, "成功", message)
                self.status_bar.showMessage(f"账本 '{account_name}' 已删除")
            else:
                QMessageBox.critical(self, "错误", message)
    
    def rename_selected_account(self):
        """重命名选中的账本"""
        current_row = self.accounts_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "提示", "请选择要重命名的账本!")
            return
            
        old_name = self.accounts_table.item(current_row, 0).text()
        
        # 弹出输入对话框
        new_name, ok = QInputDialog.getText(
            self, "重命名账本", 
            f"请输入账本 '{old_name}' 的新名称:",
            text=old_name)
        
        if ok and new_name:
            success, message = self.bill_manager.rename_account(old_name, new_name)
            if success:
                # 更新界面
                index = self.account_combo.findText(old_name)
                if index >= 0:
                    self.account_combo.setItemText(index, new_name)
                    
                # 如果重命名的是当前账本，更新下拉框选中项
                if old_name == self.bill_manager.current_account:
                    self.account_combo.setCurrentText(new_name)
                    self.update_window_title()
                    if hasattr(self, 'current_account_label'):
                        self.current_account_label.setText(f"当前账本: {new_name}")
                    
                self.update_accounts_table()
                QMessageBox.information(self, "成功", message)
                self.status_bar.showMessage(f"账本已重命名为 '{new_name}'")
            else:
                QMessageBox.critical(self, "错误", message)
    
    def rename_current_account(self):
        """重命名当前账本"""
        old_name = self.bill_manager.current_account
        
        # 弹出输入对话框
        new_name, ok = QInputDialog.getText(
            self, "重命名账本", 
            f"请输入账本 '{old_name}' 的新名称:",
            text=old_name)
        
        if ok and new_name:
            success, message = self.bill_manager.rename_account(old_name, new_name)
            if success:
                # 更新界面
                index = self.account_combo.findText(old_name)
                if index >= 0:
                    self.account_combo.setItemText(index, new_name)
                    self.account_combo.setCurrentText(new_name)
                    
                self.update_window_title()
                if hasattr(self, 'current_account_label'):
                    self.current_account_label.setText(f"当前账本: {new_name}")
                if hasattr(self, 'accounts_table'):
                    self.update_accounts_table()
                    
                QMessageBox.information(self, "成功", message)
                self.status_bar.showMessage(f"账本已重命名为 '{new_name}'")
            else:
                QMessageBox.critical(self, "错误", message)
    
    def update_accounts_table(self):
        """更新账本列表表格"""
        accounts = self.bill_manager.accounts_list
        self._begin_table_update(self.accounts_table)
        try:
            self.accounts_table.setRowCount(len(accounts))
            
            for i, account in enumerate(accounts):
                self.accounts_table.setItem(i, 0, QTableWidgetItem(account))
                
                status = "当前" if account == self.bill_manager.current_account else "空闲"
                status_item = QTableWidgetItem(status)
                if account == self.bill_manager.current_account:
                    status_item.setBackground(QColor("#dcfce7"))
                self.accounts_table.setItem(i, 1, status_item)
                
                action_text = "当前使用" if account == self.bill_manager.current_account else "双击切换"
                self.accounts_table.setItem(i, 2, QTableWidgetItem(action_text))
        finally:
            self._end_table_update(self.accounts_table)
        
        # 双击事件已在create_account_management_tab中连接，避免重复连接
    
    def on_account_table_double_click(self, row, column):
        """处理账本表格双击事件"""
        account_name = self.accounts_table.item(row, 0).text()
        if account_name != self.bill_manager.current_account:
            self.switch_account(account_name)

    def update_overview_table(self):
        """兼容分类管理后的刷新入口。"""
        self.load_data()
    
    def export_excel(self):
        # 获取导出设置
        include_time = self.include_time_checkbox.isChecked()
        detail_mode = self.detail_mode_radio.isChecked()
        
        # 获取人员导出设置
        export_all_persons = False
        target_person = None
        
        if self.bill_manager.is_multi_person_mode_enabled():
            if self.all_persons_radio.isChecked():
                export_all_persons = True
            elif self.specific_person_radio.isChecked():
                target_person = self.export_person_combo.currentText()
            # current_person_radio为默认，不需要特殊处理
        
        # 生成文件名
        mode_suffix = "明细" if detail_mode else "总账"
        person_suffix = ""
        if export_all_persons:
            person_suffix = "_所有人员"
        elif target_person:
            person_suffix = f"_{target_person}"
        elif self.bill_manager.is_multi_person_mode_enabled():
            person_suffix = f"_{self.bill_manager.get_current_person()}"
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "导出Excel文件", f"账单{mode_suffix}{person_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Excel files (*.xlsx)"
        )
        
        if filename:
            if self.export_manager.export_to_excel(filename, include_time, detail_mode, target_person, export_all_persons):
                QMessageBox.information(self, "成功", f"Excel文件已导出到:\n{filename}")
                self.status_bar.showMessage(f"Excel导出完成 - {mode_suffix}模式{person_suffix}")
            else:
                QMessageBox.critical(self, "错误", "Excel导出失败!")
    
    def export_png(self):
        # 获取导出设置
        include_time = self.include_time_checkbox.isChecked()
        detail_mode = self.detail_mode_radio.isChecked()
        
        mode_suffix = "明细" if detail_mode else "总账"
        filename, _ = QFileDialog.getSaveFileName(
            self, "导出PNG图表", f"账单图表{mode_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            "PNG files (*.png)"
        )
        
        if filename:
            if self.export_manager.export_to_png(filename, include_time, detail_mode):
                QMessageBox.information(self, "成功", f"PNG图表已导出到:\n{filename}")
                self.status_bar.showMessage(f"PNG导出完成 - {mode_suffix}模式")
            else:
                QMessageBox.critical(self, "错误", "PNG导出失败，可能没有支出数据!")
    
    def load_data(self):
        # 确保当前模式至少有一个账本
        self.bill_manager._ensure_account_exists()
        
        # 加载数据
        self.bill_manager.load_data()
        if hasattr(self, 'accounts_table'):
            self.update_accounts_table()  # 更新账本表格
        
        # 获取全局预算
        total_budget = self.bill_manager.get_total_budget()
        self.budget_input.setValue(total_budget)
        
        # 计算所有人员的总支出
        total_spent = self.bill_manager.get_total_spent()
        
        # 更新余额显示
        balance = self.bill_manager.get_remaining_budget()
        self.total_budget_label.setText(f"¥{total_budget:.2f}")
        self.total_spent_label.setText(f"¥{total_spent:.2f}")
        
        # 根据余额设置颜色
        if balance >= 0:
            self.balance_label.setObjectName("metricPositive")
            self.balance_label.setText(f"¥{balance:.2f}")
        else:
            self.balance_label.setObjectName("metricNegative")
            self.balance_label.setText(f"超支 ¥{abs(balance):.2f}")
        self.balance_label.style().unpolish(self.balance_label)
        self.balance_label.style().polish(self.balance_label)
        
        categories_to_show = ["全局预算"] + [cat for cat in self.bill_manager.categories if cat != "总预算"]
        current_person_spent = total_spent
        if self.bill_manager.is_multi_person_mode_enabled():
            current_person_spent = sum(
                self.bill_manager.get_category_total(cat)
                for cat in self.bill_manager.categories
                if cat != "总预算"
            )

        self._begin_table_update(self.overview_table)
        try:
            self.overview_table.setRowCount(len(categories_to_show))
            
            for i, category in enumerate(categories_to_show):
                if category == "全局预算":
                    total = self.bill_manager.get_total_budget()
                    percentage = "N/A"
                    note = "所有人员共享的预算"
                    
                    cat_item = QTableWidgetItem(category)
                    cat_item.setFlags(cat_item.flags() & ~Qt.ItemIsEditable)
                    self.overview_table.setItem(i, 0, cat_item)
                    
                    amount_item = QTableWidgetItem(f"¥{total:.2f}")
                    amount_item.setFlags(amount_item.flags() & ~Qt.ItemIsEditable)
                    self.overview_table.setItem(i, 1, amount_item)
                    
                    perc_item = QTableWidgetItem(percentage)
                    perc_item.setFlags(perc_item.flags() & ~Qt.ItemIsEditable)
                    self.overview_table.setItem(i, 2, perc_item)
                    
                    note_item = QTableWidgetItem(note)
                    note_item.setFlags(note_item.flags() & ~Qt.ItemIsEditable)
                    self.overview_table.setItem(i, 3, note_item)
                else:
                    total = self.bill_manager.get_category_total(category)
                    percentage = f"{(total/current_person_spent*100):.1f}%" if current_person_spent > 0 else "0%"
                    note = self.bill_manager.get_category_note(category)
                    
                    self.overview_table.setItem(i, 0, QTableWidgetItem(category))
                    self.overview_table.setItem(i, 1, QTableWidgetItem(f"¥{total:.2f}"))
                    self.overview_table.setItem(i, 2, QTableWidgetItem(percentage))
                    
                    note_item = QTableWidgetItem(note)
                    note_item.setFlags(note_item.flags() | Qt.ItemIsEditable)
                    self.overview_table.setItem(i, 3, note_item)
        finally:
            self._end_table_update(self.overview_table)
        
        self.update_recent_bills_table()

    def collect_recent_bills(self):
        """收集当前人员或默认人员的所有账单，按时间倒序返回。"""
        all_bills = []
        if self.bill_manager.is_multi_person_mode_enabled():
            current_person = self.bill_manager.get_current_person()
            if current_person in self.bill_manager.bills:
                person_bills = self.bill_manager.bills[current_person]
                for category, bills in person_bills.items():
                    if category != "总预算" and isinstance(bills, list):
                        for source_index, bill in enumerate(bills):
                            if not isinstance(bill, dict):
                                continue
                            all_bills.append({
                                "category": category,
                                "amount": bill.get("amount", 0),
                                "description": bill.get("description", ""),
                                "date": bill.get("date", ""),
                                "source_index": source_index,
                            })
        else:
            if "默认" in self.bill_manager.bills:
                person_bills = self.bill_manager.bills["默认"]
                for category, bills in person_bills.items():
                    if category != "总预算" and isinstance(bills, list):
                        for source_index, bill in enumerate(bills):
                            if isinstance(bill, dict):
                                all_bills.append({
                                    "category": category,
                                    "amount": bill.get("amount", 0),
                                    "description": bill.get("description", ""),
                                    "date": bill.get("date", ""),
                                    "source_index": source_index,
                                })
        
        all_bills.sort(key=lambda x: x["date"], reverse=True)
        return all_bills

    def update_recent_bills_table(self):
        """刷新最近账单表格，支持最近记录和全部记录两种视图。"""
        all_bills = self.collect_recent_bills()
        visible_bills = all_bills if self.show_all_recent_bills else all_bills[:self.recent_bills_limit]
        
        self._begin_table_update(self.recent_table)
        try:
            self.recent_table.setRowCount(len(visible_bills))
            for i, bill in enumerate(visible_bills):
                checkbox = QCheckBox()
                self.recent_table.setCellWidget(i, 0, checkbox)
                
                category_item = QTableWidgetItem(bill["category"])
                category_item.setData(Qt.UserRole, bill["source_index"])
                self.recent_table.setItem(i, 1, category_item)
                self.recent_table.setItem(i, 2, QTableWidgetItem(f"¥{bill['amount']:.2f}"))
                self.recent_table.setItem(i, 3, QTableWidgetItem(bill["description"]))
                self.recent_table.setItem(i, 4, QTableWidgetItem(bill["date"]))
        finally:
            self._end_table_update(self.recent_table)

        if hasattr(self, "toggle_recent_scope_btn"):
            self.toggle_recent_scope_btn.setText("显示最近20条" if self.show_all_recent_bills else "显示全部")
        if hasattr(self, "recent_scope_label"):
            if self.show_all_recent_bills:
                self.recent_scope_label.setText(f"当前显示全部 {len(all_bills)} 条记录")
            else:
                visible_count = min(len(all_bills), self.recent_bills_limit)
                self.recent_scope_label.setText(f"当前显示最近 {visible_count} 条，共 {len(all_bills)} 条记录")
    
    def add_custom_category(self):
        """添加自定义分类"""
        text, ok = QInputDialog.getText(self, "添加自定义分类", "请输入分类名称:")
        
        if ok and text:
            success, message = self.bill_manager.add_custom_category(text)
            if success:
                QMessageBox.information(self, "成功", message)
                self.refresh_categories()
                self.update_overview_table()
            else:
                QMessageBox.warning(self, "错误", message)
    
    def remove_custom_category(self):
        """删除自定义分类"""
        current_category = self.category_combo.currentText()
        if not current_category:
            QMessageBox.warning(self, "错误", "请先选择要删除的分类")
            return
        
        if not self.bill_manager.is_custom_category(current_category):
            QMessageBox.warning(self, "错误", "只能删除自定义分类")
            return
        
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除分类 '{current_category}' 吗？\n删除后该分类下的所有账单将无法恢复。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.bill_manager.remove_custom_category(current_category)
            if success:
                QMessageBox.information(self, "成功", message)
                self.refresh_categories()
                self.update_overview_table()
            else:
                QMessageBox.warning(self, "错误", message)
    
    def refresh_categories(self):
        """刷新分类下拉框"""
        current_text = self.category_combo.currentText()
        self.category_combo.clear()
        categories_without_budget = [cat for cat in self.bill_manager.categories if cat != "总预算"]
        self.category_combo.addItems(categories_without_budget)
        
        # 尝试保持之前的选择
        if current_text in categories_without_budget:
            self.category_combo.setCurrentText(current_text)
    
    # ============= 多人模式管理方法 =============
    
    def update_mode_button_text(self):
        """更新模式按钮文本"""
        if self.bill_manager.is_multi_person_mode_enabled():
            self.mode_toggle_btn.setText("切换到单人模式")
        else:
            self.mode_toggle_btn.setText("切换到多人模式")
    
    def update_person_toolbar_visibility(self):
        """更新人员工具栏的显示状态"""
        is_multi = self.bill_manager.is_multi_person_mode_enabled()
        
        # 确保人员工具栏本身是可见的
        if hasattr(self, 'person_toolbar'):
            self.person_toolbar.setVisible(True)  # 工具栏本身始终可见
        
        # 人员选择相关控件只在多人模式下显示
        self.person_label.setVisible(is_multi)
        self.person_combo.setVisible(is_multi)
        self.add_person_btn.setVisible(is_multi)
        self.remove_person_btn.setVisible(is_multi)
        for action_name in (
            'person_label_action',
            'person_combo_action',
            'add_person_action',
            'remove_person_action',
        ):
            if hasattr(self, action_name):
                getattr(self, action_name).setVisible(is_multi)
        
        # 强制刷新工具栏布局
        if hasattr(self, 'person_toolbar'):
            self.person_toolbar.update()
            self.person_toolbar.repaint()
        
        # 强制刷新主窗口
        self.update()
        self.repaint()
        
        # 更新人员下拉框
        if is_multi:
            self.refresh_person_combo()
    
    def refresh_person_combo(self):
        """刷新人员下拉框"""
        current_person = self.person_combo.currentText()
        self.person_combo.clear()
        self.person_combo.addItems(self.bill_manager.get_persons_list())
        
        # 设置当前选中的人员
        current_person = self.bill_manager.get_current_person()
        if current_person in self.bill_manager.get_persons_list():
            self.person_combo.setCurrentText(current_person)
    
    def toggle_person_mode(self):
        """切换单人/多人模式（带加载动画）"""
        if self.bill_manager.is_multi_person_mode_enabled():
            # 切换到单人模式
            reply = QMessageBox.question(
                self, "确认切换", 
                "确定要切换到单人模式吗？\\n切换后将只显示默认人员的账单。",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self._switch_mode_with_animation("single")
        else:
            # 切换到多人模式
            reply = QMessageBox.question(
                self, "确认切换", 
                "确定要切换到多人模式吗？\\n切换后可以管理多个人员的账单。",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self._switch_mode_with_animation("multi")
    
    def on_person_combo_activated(self):
        """处理人员切换"""
        person_name = self.person_combo.currentText()
        if person_name and person_name != self.bill_manager.get_current_person():
            self.bill_manager.switch_current_person(person_name)
            self.refresh_all_data()
            self.update_window_title()
    
    def add_person(self):
        """添加新人员"""
        text, ok = QInputDialog.getText(self, "添加人员", "请输入人员名称:")
        
        if ok and text:
            success, message = self.bill_manager.add_person(text)
            if success:
                QMessageBox.information(self, "成功", message)
                self.refresh_person_combo()
                self.refresh_all_data()
            else:
                QMessageBox.warning(self, "错误", message)
    
    def remove_person(self):
        """删除人员"""
        current_person = self.person_combo.currentText()
        if not current_person:
            QMessageBox.warning(self, "错误", "请先选择要删除的人员")
            return
        
        if current_person == "默认":
            QMessageBox.warning(self, "错误", "不能删除默认人员")
            return
        
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除人员 '{current_person}' 吗？\\n删除后该人员的所有账单将无法恢复。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.bill_manager.remove_person(current_person)
            if success:
                QMessageBox.information(self, "成功", message)
                self.refresh_person_combo()
                self.refresh_all_data()
            else:
                QMessageBox.warning(self, "错误", message)
    
    def refresh_all_data(self):
        """刷新所有数据显示"""
        self.load_data()
        # 不调用search_bills()，避免在模式切换时弹出搜索提示
        self.update_add_bill_person_visibility()
        self.update_export_person_visibility()
        self.update_transfer_tab_data()
    
    def update_export_person_visibility(self):
        """更新导出页面的人员选择显示状态"""
        is_multi = self.bill_manager.is_multi_person_mode_enabled()
        self.person_export_group.setVisible(is_multi)
        
        # 强制刷新导出页面的人员组件
        self.person_export_group.update()
        self.person_export_group.repaint()
        
        if is_multi:
            # 更新人员下拉框
            current_person = self.export_person_combo.currentText()
            self.export_person_combo.clear()
            self.export_person_combo.addItems(self.bill_manager.get_persons_list())
            
            # 设置当前人员为默认选择
            current_person = self.bill_manager.get_current_person()
            if current_person in self.bill_manager.get_persons_list():
                self.export_person_combo.setCurrentText(current_person)
    
    def update_add_bill_person_visibility(self):
        """更新添加账单页面的人员选择显示状态"""
        is_multi = self.bill_manager.is_multi_person_mode_enabled()
        self.person_select_widget.setVisible(is_multi)
        
        # 强制刷新添加账单页面的人员组件
        self.person_select_widget.update()
        self.person_select_widget.repaint()
        
        if is_multi:
            # 更新人员下拉框
            current_person = self.add_bill_person_combo.currentText()
            self.add_bill_person_combo.clear()
            self.add_bill_person_combo.addItems(self.bill_manager.get_persons_list())
            
            # 设置当前人员为默认选择
            current_person = self.bill_manager.get_current_person()
            if current_person in self.bill_manager.get_persons_list():
                self.add_bill_person_combo.setCurrentText(current_person)
    
    def _switch_mode_with_animation(self, target_mode):
        """带加载动画的模式切换"""
        # 创建加载对话框
        loading_dialog = self._create_loading_dialog(target_mode)
        loading_dialog.show()
        
        # 使用QTimer延迟执行切换，让加载对话框有时间显示
        QTimer.singleShot(100, lambda: self._perform_mode_switch(target_mode, loading_dialog))
    
    def _create_loading_dialog(self, target_mode):
        """创建加载动画对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("模式切换中...")
        dialog.setFixedSize(400, 150)
        dialog.setWindowFlag(Qt.WindowCloseButtonHint, False)  # 禁用关闭按钮
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        
        # 添加图标和文字
        icon_label = QLabel()
        if target_mode == "multi":
            icon_label.setText("👥")
            text = "正在切换到多人模式..."
        else:
            icon_label.setText("👤")
            text = "正在切换到单人模式..."
        
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setObjectName("metricValue")
        
        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignCenter)
        
        # 添加进度条动画
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 0)  # 设置为无限进度条
        
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        layout.addWidget(progress_bar)
        layout.addStretch()
        
        return dialog
    
    def _perform_mode_switch(self, target_mode, loading_dialog):
        """执行实际的模式切换"""
        try:
            # 执行模式切换
            if target_mode == "multi":
                self.bill_manager.switch_to_multi_person_mode()
                success_msg = "已成功切换到多人模式！\\n现在可以管理多个人员的账单。"
            else:
                self.bill_manager.switch_to_single_person_mode()
                success_msg = "已成功切换到单人模式！\\n现在只显示默认人员的账单。"
            
            # 更新UI界面
            self._update_all_ui_for_mode_switch()
            
            # 延迟关闭加载对话框并显示成功消息
            QTimer.singleShot(800, lambda: self._finish_mode_switch(loading_dialog, success_msg))
            
        except Exception as e:
            loading_dialog.close()
            QMessageBox.critical(self, "切换失败", f"模式切换时发生错误：{str(e)}")
    
    def _update_all_ui_for_mode_switch(self):
        """更新所有与模式相关的UI元素"""
        # 更新按钮文字
        self.update_mode_button_text()
        
        # 重新加载当前模式的账本列表
        self.bill_manager.load_accounts_list()
        
        # 更新账本下拉框
        self.account_combo.clear()
        self.account_combo.addItems(self.bill_manager.accounts_list)
        self.account_combo.setCurrentText(self.bill_manager.current_account)
        
        # 更新人员工具栏可见性
        self.update_person_toolbar_visibility()
        
        # 更新添加账单页面的人员选择
        self.update_add_bill_person_visibility()
        
        # 更新导出页面的人员选择
        self.update_export_person_visibility()
        
        # 更新账本管理表格（如果存在）
        if hasattr(self, 'accounts_table'):
            self.update_accounts_table()
        
        # 刷新所有数据显示
        self.refresh_all_data()
        
        # 更新窗口标题
        self.update_window_title()
    
    def _finish_mode_switch(self, loading_dialog, success_msg):
        """完成模式切换，关闭加载对话框并显示成功消息"""
        loading_dialog.close()
        
        # 处理所有待处理的Qt事件，确保UI更新完成
        QApplication.processEvents()
        
        # 再次强制刷新所有UI元素
        self._update_all_ui_for_mode_switch()
        
        # 创建成功提示对话框
        success_dialog = QMessageBox(self)
        success_dialog.setWindowTitle("切换成功")
        success_dialog.setText(success_msg)
        success_dialog.setIcon(QMessageBox.Information)
        
        # 设置图标
        if self.bill_manager.is_multi_person_mode_enabled():
            success_dialog.setIconPixmap(QPixmap())  # 可以添加自定义图标
        
        success_dialog.setStandardButtons(QMessageBox.Ok)
        success_dialog.exec()
    
    # ============= 转账平账功能方法 =============
    
    def update_transfer_tab_data(self):
        """更新转账平账标签页数据"""
        if not hasattr(self, 'master_person_combo'):
            return  # 转账标签页还未创建
        
        # 更新主账单信息
        master_person = self.bill_manager.get_master_person()
        if master_person:
            self.current_master_label.setText(master_person)
            self.current_master_label.setObjectName("accentLabel")
        else:
            self.current_master_label.setText("未设置")
            self.current_master_label.setObjectName("metricNegative")
        self.current_master_label.style().unpolish(self.current_master_label)
        self.current_master_label.style().polish(self.current_master_label)
        
        # 更新人员下拉框
        persons = self.bill_manager.get_persons_list()
        
        # 更新主账单设置下拉框
        self.master_person_combo.clear()
        self.master_person_combo.addItems(persons)
        if master_person and master_person in persons:
            self.master_person_combo.setCurrentText(master_person)
        
        # 更新转账下拉框
        self.from_person_combo.clear()
        self.from_person_combo.addItems(persons)
        self.to_person_combo.clear()
        self.to_person_combo.addItems(persons)
        
        # 更新人员余额表格
        self.update_balance_table()
        
        # 更新转账记录表格
        self.update_transfer_history_table()
    
    def update_balance_table(self):
        """更新人员余额表格"""
        if not hasattr(self, 'balance_table'):
            return
        
        persons = self.bill_manager.get_persons_list()
        self._begin_table_update(self.balance_table)
        try:
            self.balance_table.setRowCount(len(persons))
            
            for i, person in enumerate(persons):
                name_item = QTableWidgetItem(person)
                if self.bill_manager.is_master_person(person):
                    name_item.setBackground(QColor("#dcfce7"))
                    name_item.setText(f"{person} (主)")
                self.balance_table.setItem(i, 0, name_item)
                
                total_expense = 0
                total_income = 0
                
                if person in self.bill_manager.bills:
                    for category, bills in self.bill_manager.bills[person].items():
                        if category != "总预算":
                            for bill in bills:
                                amount = bill["amount"]
                                if amount > 0:
                                    total_expense += amount
                                else:
                                    total_income += abs(amount)
                
                balance = total_expense - total_income
                
                self.balance_table.setItem(i, 1, QTableWidgetItem(f"¥{total_expense:.2f}"))
                self.balance_table.setItem(i, 2, QTableWidgetItem(f"¥{total_income:.2f}"))
                
                balance_item = QTableWidgetItem(f"¥{balance:.2f}")
                if balance > 0:
                    balance_item.setBackground(QColor("#fee2e2"))
                elif balance < 0:
                    balance_item.setBackground(QColor("#dcfce7"))
                self.balance_table.setItem(i, 3, balance_item)
        finally:
            self._end_table_update(self.balance_table)
    
    def update_transfer_history_table(self):
        """更新转账记录表格"""
        if not hasattr(self, 'transfer_history_table'):
            return
        
        transfer_summary = self.bill_manager.get_transfer_summary()
        
        # 计算总行数
        total_rows = 0
        for person_transfers in transfer_summary.values():
            total_rows += len(person_transfers)
        
        self._begin_table_update(self.transfer_history_table)
        try:
            self.transfer_history_table.setRowCount(total_rows)
            
            row = 0
            for person, transfers in transfer_summary.items():
                for transfer in transfers:
                    self.transfer_history_table.setItem(row, 0, QTableWidgetItem(person))
                    
                    amount = transfer["amount"]
                    amount_item = QTableWidgetItem(f"¥{abs(amount):.2f}")
                    if amount > 0:
                        amount_item.setBackground(QColor("#fee2e2"))
                    else:
                        amount_item.setBackground(QColor("#dcfce7"))
                    self.transfer_history_table.setItem(row, 1, amount_item)
                    
                    self.transfer_history_table.setItem(row, 2, QTableWidgetItem(transfer["description"]))
                    self.transfer_history_table.setItem(row, 3, QTableWidgetItem(transfer["date"]))
                    
                    transfer_type = "转出" if amount > 0 else "收入"
                    self.transfer_history_table.setItem(row, 4, QTableWidgetItem(transfer_type))
                    
                    row += 1
        finally:
            self._end_table_update(self.transfer_history_table)
    
    def set_master_person(self):
        """设置主账单人员"""
        if not self.bill_manager.is_multi_person_mode_enabled():
            QMessageBox.warning(self, "提示", "请先切换到多人模式!")
            return
        
        person_name = self.master_person_combo.currentText()
        if not person_name:
            QMessageBox.warning(self, "提示", "请选择要设置的主账单人员!")
            return
        
        success, message = self.bill_manager.set_master_person(person_name)
        if success:
            QMessageBox.information(self, "成功", message)
            self.update_transfer_tab_data()
            self.status_bar.showMessage(f"✅ {message}")
        else:
            QMessageBox.warning(self, "错误", message)
    
    def manual_transfer(self):
        """手动转账"""
        if not self.bill_manager.is_multi_person_mode_enabled():
            QMessageBox.warning(self, "提示", "请先切换到多人模式!")
            return
        
        from_person = self.from_person_combo.currentText()
        to_person = self.to_person_combo.currentText()
        amount_text = self.transfer_amount_input.text().strip()
        description = self.transfer_description_input.text().strip()
        
        # 验证金额输入
        try:
            amount = float(amount_text) if amount_text else 0
        except ValueError:
            amount = 0
        
        if not from_person or not to_person:
            QMessageBox.warning(self, "提示", "请选择转账方和接收方!")
            return
        
        if from_person == to_person:
            QMessageBox.warning(self, "提示", "转账方和接收方不能是同一人!")
            return
        
        if amount <= 0:
            QMessageBox.warning(self, "提示", "转账金额必须大于0!")
            return
        
        if not description:
            description = "转账平账"
        
        success, message = self.bill_manager.add_transfer_bill(from_person, to_person, amount, description)
        if success:
            QMessageBox.information(self, "成功", message)
            self.transfer_amount_input.clear()
            self.transfer_description_input.clear()
            self.update_transfer_tab_data()
            self.load_data()  # 刷新总览数据
            self.status_bar.showMessage(f"✅ {message}")
        else:
            QMessageBox.warning(self, "错误", message)
    
    def quick_balance(self):
        """快速平账"""
        if not self.bill_manager.is_multi_person_mode_enabled():
            QMessageBox.warning(self, "提示", "请先切换到多人模式!")
            return
        
        target_person = self.to_person_combo.currentText()
        if not target_person:
            QMessageBox.warning(self, "提示", "请选择要平账的人员!")
            return
        
        master_person = self.bill_manager.get_master_person()
        if not master_person:
            QMessageBox.warning(self, "提示", "请先设置主账单人员!")
            return
        
        # 计算目标人员的实际支出
        actual_expense = 0
        if target_person in self.bill_manager.bills:
            for category, bills in self.bill_manager.bills[target_person].items():
                if category != "总预算" and category != "转账平账":
                    actual_expense += sum(bill["amount"] for bill in bills)
        
        if actual_expense <= 0:
            QMessageBox.information(self, "提示", f"{target_person} 没有需要平账的支出")
            return
        
        reply = QMessageBox.question(
            self, "确认平账", 
            f"确定要为 {target_person} 平账吗？\n\n"
            f"实际支出: ¥{actual_expense:.2f}\n"
            f"平账方式: {master_person} → {target_person}\n\n"
            f"平账后 {target_person} 的账单余额将变为0",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success, message = self.bill_manager.quick_balance_account(target_person)
            if success:
                QMessageBox.information(self, "平账成功", message)
                self.update_transfer_tab_data()
                self.load_data()  # 刷新总览数据
                self.status_bar.showMessage(f"✅ {message}")
            else:
                QMessageBox.warning(self, "平账失败", message)
    
    def show_path_config_dialog(self):
        """显示数据路径设置对话框"""
        from ui.path_config_dialog import PathConfigDialog
        
        path_dialog = PathConfigDialog(self, is_first_time=False)
        if path_dialog.exec() == QDialog.Accepted:
            # 路径配置已更改，提示用户重启程序
            QMessageBox.information(
                self, "设置成功", 
                "✅ 数据路径设置已保存！\n\n"
                "⚠️ 路径更改将在下次启动程序时生效。\n"
                "如需立即生效，请重启账单管理系统。\n\n"
                f"📊 新数据路径: {path_dialog.get_data_path()}\n"
                f"🔐 新备份路径: {path_dialog.get_backup_path()}"
            )
