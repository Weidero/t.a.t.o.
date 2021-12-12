import logging

from PyQt5.QtWidgets import QMainWindow, QTreeWidgetItem, QMessageBox, QAction, QFileDialog
from PyQt5.QtGui import QColor, QIcon, QPixmap
from PyQt5.QtCore import Qt
from PyQt5 import uic

from core.Core import Transaction, Task, Check, Rework, Status, DateManager, Loader
from core.Widgets import Task_Info_Widget, Transaction_info_widget, BlankActionWidger, BlankInfoWidger, CommentsWidget, TaskEditorWidget, TaskStackWidget, TaskActionWidget, TaskCheckWidget, TaskReworkWidget, TransactionActionWidget, TransactionEditorModule
from core.ReportFactory import ReportFactory
from core.TaskImporter import TaskImporter
from core.EmployeeEditor import EmployeeEditorModule
import webbrowser
from threading import Thread

status = Status()


class MainGui(QMainWindow, DateManager):

    def __init__(self, user):
        QMainWindow.__init__(self)
        DateManager.__init__(self)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.me = user
        self.loader = Loader(user=self.me)
        self.task = Task(db=user.db)
        self.check = Check(db=user.db)
        self.rework = Rework(db=user.db)
        self.transaction = Transaction(db=user.db)

        self.customer_selected = None

        self.ui = uic.loadUi(r'src\ui\main.ui')
        self.ui.setWindowIcon(QIcon('src\img\ico\start.ico'))
        self.ui.setWindowTitle('Task And Time Organizer')
        self.ee = EmployeeEditorModule()

        self.panel = self.ui.panel_treewidget
        self.filter_show_closed_task = False
        self.filter_show_closed_transactions = False
        self.filter_show_closed_check = False
        self.filter_task_responsible_only = False

        self._setup_me()
        self._connect_signals()

        self.ui.action_stackwidget.setCurrentWidget(self.blank_action)
        self.ui.info_and_edit_stackwidget.setCurrentWidget(self.blank_info)

        self.loader.transactions_where_user_has_actions()

        self._display_transactions_where_user_has_action()

    def _setup_me(self):
        if self.me.access_id < 4:
            self.ui.export_to_excel_act.setEnabled(False)
        if self.me.access_id < 8:
            self.ui.employee_editor_act.setEnabled(False)
        self.chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'


        self._load_customers_to_menu()

        #COLOR SETTINGS
        self.transaction_bg_color = QColor(0, 0, 0)
        self.task_bg_color = QColor(148, 148, 139)
        self.check_bg_color = QColor(191, 191, 191)
        self.rework_bg_color = QColor(217, 217, 217)

        #SETTING QTREEWIDGET COLUMN SIZE
        self.ui.panel_treewidget.setColumnWidth(0, 355)
        self.ui.panel_treewidget.setColumnWidth(1, 120)
        self.ui.panel_treewidget.setColumnWidth(2, 90)
        self.ui.panel_treewidget.setColumnWidth(3, 120)

        self.task_editor = TaskEditorWidget(task=self.task, user=self.me)
        self.ui.info_and_edit_stackwidget.addWidget(self.task_editor)

        self.transaction_editor = TransactionEditorModule(user=self.me)
        self.ui.info_and_edit_stackwidget.addWidget(self.transaction_editor)

        self.task_info = Task_Info_Widget(self.task)
        self.ui.info_and_edit_stackwidget.addWidget(self.task_info)

        self.transaction_info = Transaction_info_widget(self.transaction)
        self.ui.info_and_edit_stackwidget.addWidget(self.transaction_info)

        self.task_stack = TaskStackWidget(task=self.task, user=self.me)
        self.ui.stack_stackwidget.addWidget(self.task_stack)
        self.ui.stack_stackwidget.setCurrentWidget(self.task_stack)

        self.task_action = TaskActionWidget(task=self.task, user=self.me)
        self.ui.action_stackwidget.addWidget(self.task_action)

        self.transaction_action = TransactionActionWidget(transaction=self.transaction,
                                                          user=self.me)
        self.ui.action_stackwidget.addWidget(self.transaction_action)

        self.task_check = TaskCheckWidget(task=self.task, check=self.check, user=self.me)
        self.ui.action_stackwidget.addWidget(self.task_check)

        self.task_rework = TaskReworkWidget(task=self.task, rework=self.rework, user=self.me)
        self.ui.action_stackwidget.addWidget(self.task_rework)

        self.blank_action = BlankActionWidger()
        self.ui.action_stackwidget.addWidget(self.blank_action)

        self.blank_info = BlankInfoWidger()
        self.ui.info_and_edit_stackwidget.addWidget(self.blank_info)

        self.comments = CommentsWidget(transaction=self.transaction, task=self.task, user=self.me)
        self.ui.comments_stackwidget.addWidget(self.comments)

    def _reload(self):
        self.ui.info_and_edit_stackwidget.setCurrentWidget(self.blank_info)
        self.ui.action_stackwidget.setCurrentWidget(self.blank_action)
        self.task.set_id(None)
        self.transaction.set_id(None)
        self.rework.set_id(None)
        self.check.set_id(None)
        self.ui.panel_treewidget.clear()
        self._display_transactions()

    def _refresh(self):
        self.show_last()
        self._reload()

    def _refresh_controller(self, state):
        if state:
            self._refresh()
        else:
            pass

    def _connect_signals(self):
        self.task.signal_id_changed.connect(self._show_task_info)
        self.task.signal_message.connect(self._message_receiver)
        self.transaction.signal_message.connect(self._message_receiver)
        self.transaction.signal_deleted.connect(self._refresh_controller)
        self.ui.panel_treewidget.currentItemChanged.connect(self._single_click_selection_manager)
        # self.ui.panel_treewidget.itemExpanded.connect(self._load_extended_data_to_panel)
        self.ui.panel_treewidget.itemDoubleClicked.connect(self._double_click_selection_manager)

        self.ui.refresh_act.triggered.connect(self._refresh)
        self.ui.new_transaction_act.triggered.connect(self._new_transaction_act)
        self.ui.edit_transaction_act.triggered.connect(self._edit_transaction_act)
        self.ui.new_task_act.triggered.connect(self._new_task_act)
        self.ui.edit_task_act.triggered.connect(self._edit_task_act)
        self.ui.show_closed_task_act.triggered.connect(self._filter_show_released_tasks)
        self.ui.show_closed_transaction_act.triggered.connect(self._filter_show_released_transactions)
        self.ui.show_closed_check_act.triggered.connect(self._filter_show_released_checks)
        self.ui.show_task_responsible_user_act.triggered.connect(self._display_transactions_where_user_has_action)
        self.ui.show_transaction_responsible_user_act.triggered.connect(self._display_transactions_where_user_is_responsible_for)
        self.ui.report_factory_act.triggered.connect(self._report_factory_act)
        self.ui.task_importer_act.triggered.connect(self._task_importer_act)
        self.ui.export_to_excel_act.triggered.connect(self._export_to_excel_act)
        self.ui.employee_editor_act.triggered.connect(self._employee_editor_act)

        self.ui.knowledge_database_act_2.triggered.connect(self._open_knowledge_database_in_chrome)
        self.ui.autotime_act.triggered.connect(self._open_autotime_in_chrome)

        self.me.db.signal_exporting_status.connect(self._message_receiver)

        self.transaction_editor.signal_editing.connect(self._lock_gui)
        self.task_editor.signal_refresh_panel.connect(self._refresh_controller)
        self.task_editor.signal_widget_active.connect(self._lock_gui)

    def _lock_gui(self, status):
        if status is True:
            self.ui.panel_treewidget.setEnabled(False)
            self.ui.stack_stackwidget.setEnabled(False)
            self.ui.action_stackwidget.setEnabled(False)
            self.ui.menubar.setEnabled(False)

        else:
            self.ui.panel_treewidget.setEnabled(True)
            self.ui.stack_stackwidget.setEnabled(True)
            self.ui.action_stackwidget.setEnabled(True)
            self.ui.menubar.setEnabled(True)

    def _message_receiver(self, msg):
        self.ui.statusBar().showMessage(str(msg))

    def _display_transactions_where_user_has_action(self):
        self.filter_task_responsible_only = True
        self.show_last = self.loader.transactions_where_user_has_actions
        self.ui.show_closed_transaction_act.setChecked(False)
        self.ui.menuTransaction_2.setEnabled(False)
        self.ui.menuCheck.setEnabled(True)
        self._refresh()

    def _display_transactions_where_user_is_responsible_for(self):
        self.filter_task_responsible_only = False
        self.show_last = self.loader.transactions_where_user_is_responsible
        self.ui.menuTransaction_2.setEnabled(True)
        self.ui.menuCheck.setEnabled(False)
        self.ui.show_closed_check_act.setChecked(False)
        self._refresh()

    def _display_transactions_for_selected_customer(self):
        self.filter_task_responsible_only = False
        self.ui.show_closed_check_act.setChecked(False)
        self.ui.menuCheck.setEnabled(False)
        self.ui.menuTransaction_2.setEnabled(True)
        self._refresh()

    def _show_task_info(self):
        if self.task.id is not None:
            self.ui.info_and_edit_stackwidget.setCurrentWidget(self.task_info)
        else:
            self.ui.info_and_edit_stackwidget.setCurrentWidget(self.blank_info)

    def _filter_show_released_tasks(self, state):
        self.loader.filter_show_released_task = state
        self._refresh()

    def _filter_show_released_checks(self, state):
        self.loader.filter_show_released_checks = state
        self._refresh()

    def _filter_show_released_transactions(self, state):
        self.loader.filter_show_released_transactions = state
        self._refresh()

    def _edit_task_act(self):
        if self.task.id is not None:
            if self.task.released == 1:
                QMessageBox.information(self, 'Information',
                                        'Editing task with status Finished(for non deliverable) or Delivered(for deliverable) is prohibited')
                return

            if self.task.creator.login == self.me.login or self.me.access_id >= 8 or self.transaction.responsible.login == self.me.login or (self.task.editable == 1 and self.task.responsible.login == self.me.login):
                self.task_editor.edit_task(self.task)
                self.task_editor.show()
                self.ui.info_and_edit_stackwidget.setCurrentWidget(self.task_editor)
            else:
                QMessageBox.information(self, 'Editing prohibited', "You can't edit this task")
        else:
            QMessageBox.information(self, 'Information',
                                    'Please select task you want to edit first')

    def _new_task_act(self):
        self.task_editor.show()
        self.task_editor.create_task()
        self.ui.info_and_edit_stackwidget.setCurrentWidget(self.task_editor)
        self.ui.action_stackwidget.setCurrentWidget(self.blank_action)

    def _edit_transaction_act(self):
        if self.transaction.id is not None:
            if self.transaction.responsible.login == self.me.login or self.me.login in self.transaction.admins:
                self.transaction_editor.show()
                self.transaction_editor.edit_transaction(self.transaction)
                self.ui.info_and_edit_stackwidget.setCurrentWidget(self.transaction_editor)
                self.transaction_editor.show()
            else:
                QMessageBox.information(self, 'Editing prohibited',
                                        'Only transaction responsible person can edit transaction!\nResponsible for this transaction is {}'.format(
                                            self.transaction.responsible.full_name))

    def _new_transaction_act(self):
        if self.me.access_id > 1:
            self.ui.info_and_edit_stackwidget.setCurrentWidget(self.transaction_editor)
            self.transaction_editor.create_transaction()
        else:
            QMessageBox.information(self, 'Information',
                                    'Your access level is not sufficient to create transaction')

    def _report_factory_act(self):
        try:
            rf = ReportFactory()
            rf.ui.show()
        except Exception:
            self.logger.exception("Error during starting Raport Factory")

    def _task_importer_act(self):
        try:
            ti = TaskImporter()
            ti.ui.show()
        except Exception:
            self.logger.exception("Error during starting Tato Importer")

    def _export_to_excel_act(self):
        path = QFileDialog.getOpenFileName(self, 'Select file where data will be saved', 'C:\\', 'Excel file(*.xlsx)')
        if path:
            self.me.db.export_data_to_excel(path[0])

    def _open_knowledge_database_in_chrome(self):
        url = r"G:\DR\common\08. Knowledge\index.html"
        webbrowser.get(self.chrome_path).open(url)

    def _open_autotime_in_chrome(self):
        thread = Thread(target=self._open_webbrowser_with_at)
        thread.start()

    def _open_webbrowser_with_at(self):
        url = r"http://gush1ax1.utcapp.com:8080/autotime/login?action=view"
        webbrowser.get(self.chrome_path).open(url)

    def _employee_editor_act(self):
        self.ee.show()

    def _single_click_selection_manager(self, item):
        if item is not None:
            if item.text(101) == "transaction":
                self.task.set_id(None)
                self.transaction.set_id(int(item.text(100)))
                self.transaction.load_data_childs()
                self.ui.info_and_edit_stackwidget.setCurrentWidget(self.transaction_info)
                if self.transaction.responsible.login == self.me.login or self.me.login in self.transaction.admins:
                    self.ui.action_stackwidget.setCurrentWidget(self.transaction_action)
                else:
                    self.ui.action_stackwidget.setCurrentWidget(self.blank_action)

            if item.text(101) == "task":
                self.task.set_id(int(item.text(100)))
                self.transaction.set_id(self.task.transaction_id)  # TODO: zastanowic sie czy trzeba tutaj resetowac Transakcje ?
                self.transaction.load_data_basic()
                self.comments._reload_task()
                self.ui.info_and_edit_stackwidget.setCurrentWidget(self.task_info)
                self.ui.comments_stackwidget.setCurrentWidget(self.comments)
                if self.task.responsible.login == self.me.login:
                    self.ui.action_stackwidget.setCurrentWidget(self.task_action)
                else:
                    self.ui.action_stackwidget.setCurrentWidget(self.blank_action)

            if item.text(101) == "check":
                self.task.set_id(int(item.parent().text(100)))
                self.check.set_id(int(item.text(100))) #TODO zalatic to
                # for check in self.task.checks:
                #     if check.id == int(item.text(100)):
                #         self.check = check
                #         self.check.signal_id_changed.emit(self.check.id)
                # self.check.load_data()
                self.ui.info_and_edit_stackwidget.setCurrentWidget(self.task_info)
                if self.check.responsible.login == self.me.login:
                    self.task_check._reload()
                    self.ui.action_stackwidget.setCurrentWidget(self.task_check)
                else:
                    self.ui.action_stackwidget.setCurrentWidget(self.blank_action)

            if item.text(101) == "rework":
                self.rework.set_id(int(item.text(100)))
                self.task.set_id(self.rework.task_id)
                self.ui.info_and_edit_stackwidget.setCurrentWidget(self.task_info)
                if self.rework.responsible.login == self.me.login:
                    self.ui.action_stackwidget.setCurrentWidget(self.task_rework)
                else:
                    self.ui.action_stackwidget.setCurrentWidget(self.blank_action)
        else:
            self.ui.action_stackwidget.setCurrentWidget(self.blank_action)
            self.ui.info_and_edit_stackwidget.setCurrentWidget(self.blank_info)

    def _double_click_selection_manager(self, item):
        if item is not None:
            if item.text(101) == "transaction":
                self._edit_transaction_act()

            if item.text(101) == "task":
                self._edit_task_act()

    def _display_transactions(self):
        deliverable = QIcon(r'src/img/ico/deliverable2.ico')
        for transaction in self.loader.transactions:
            transaction_item = QTreeWidgetItem(self.panel)
            transaction_item.setText(0, transaction.name)
            transaction_item.setText(1, status.name(transaction.status))
            transaction_item.setTextAlignment(2, Qt.AlignRight)
            if transaction.deliverable == 1:
                transaction_item.setText(2, str(transaction.planned_delivery))
                transaction_item.setIcon(2, deliverable)
            else:
                transaction_item.setText(2, str(transaction.planned_end))
            transaction_item.setText(3, str(transaction.responsible.full_name))
            transaction_item.setText(100, str(transaction.id))
            transaction_item.setText(101, "transaction")

            transaction_item.setBackground(0, self.transaction_bg_color)
            transaction_item.setBackground(1, self.transaction_bg_color)
            transaction_item.setBackground(2, self.transaction_bg_color)
            transaction_item.setBackground(3, self.transaction_bg_color)
            transaction_item.setForeground(0, QColor(255, 255, 255))
            transaction_item.setForeground(1, QColor(255, 255, 255))
            transaction_item.setForeground(2, QColor(255, 255, 255))
            transaction_item.setForeground(3, QColor(255, 255, 255))


            for task in transaction.tasks:
                task_item = QTreeWidgetItem(transaction_item)
                task_item.setText(0, task.name)
                task_item.setText(1, status.name(task.status))
                task_item.setTextAlignment(2, Qt.AlignRight)
                if task.deliverable == 1:
                    task_item.setText(2, str(task.planned_delivery))
                    task_item.setIcon(2, deliverable)
                else:
                    task_item.setText(2, str(task.planned_end))
                task_item.setText(3, task.responsible.full_name)
                task_item.setText(100, str(task.id))
                task_item.setText(101, "task")

                task_item.setBackground(0, self.task_bg_color)
                task_item.setBackground(1, self.task_bg_color)
                task_item.setBackground(2, self.task_bg_color)
                task_item.setBackground(3, self.task_bg_color)

                for counter, check in enumerate(task.checks, 1):
                    check_item = QTreeWidgetItem(task_item)
                    check_item.setText(0, "[" + str(counter) + "] check")
                    check_item.setText(1, status.name(check.status))
                    check_item.setText(2, str(check.planned_end))
                    check_item.setTextAlignment(2, Qt.AlignRight)
                    check_item.setText(3, check.responsible.full_name)
                    check_item.setText(100, str(check.id))
                    check_item.setText(101, "check")

                    check_item.setBackground(0, self.check_bg_color)
                    check_item.setBackground(1, self.check_bg_color)
                    check_item.setBackground(2, self.check_bg_color)
                    check_item.setBackground(3, self.check_bg_color)

                for counter, rework in enumerate(task.reworks, 1):
                    rework_item = QTreeWidgetItem(task_item)
                    rework_item.setText(0, "[" + str(counter) + "] rework")
                    rework_item.setText(1, status.name(rework.status))
                    rework_item.setTextAlignment(2, Qt.AlignRight)
                    rework_item.setText(2, str(rework.planned_end))
                    rework_item.setText(3, rework.responsible.full_name)
                    rework_item.setText(100, str(rework.id))
                    rework_item.setText(101, "rework")

                    rework_item.setBackground(0, self.rework_bg_color)
                    rework_item.setBackground(1, self.rework_bg_color)
                    rework_item.setBackground(2, self.rework_bg_color)
                    rework_item.setBackground(3, self.rework_bg_color)

    def _load_customers_to_menu(self):

        customers_list = self.ui.menuShow.addMenu('Customers')
        c_1 = QAction('ABU', self)
        c_2 = QAction('HS Marston', self)
        c_3 = QAction('Rockford-EPS', self)
        c_4 = QAction('Rome', self)
        c_8 = QAction('West Des Moines', self)
        c_9 = QAction('Winsdsor Locks-AMS Pack', self)
        c_10 = QAction('Winsdsor Locks-Pneumatic Valves', self)
        c_11 = QAction('Winsdsor Locks-FHEM', self)
        c_12 = QAction('Winsdsor Locks-HX', self)
        c_13 = QAction('Winsdsor Locks-SES', self)
        c_14 = QAction('Rockford-ECS', self)

        customers_list.addAction(c_1)
        customers_list.addAction(c_2)
        customers_list.addAction(c_3)
        customers_list.addAction(c_4)
        customers_list.addAction(c_8)
        customers_list.addAction(c_9)
        customers_list.addAction(c_10)
        customers_list.addAction(c_11)
        customers_list.addAction(c_12)
        customers_list.addAction(c_13)
        customers_list.addAction(c_14)

        c_1.triggered.connect(self._c_1)
        c_2.triggered.connect(self._c_2)
        c_3.triggered.connect(self._c_3)
        c_4.triggered.connect(self._c_4)
        c_8.triggered.connect(self._c_8)
        c_9.triggered.connect(self._c_9)
        c_10.triggered.connect(self._c_10)
        c_11.triggered.connect(self._c_11)
        c_12.triggered.connect(self._c_12)
        c_13.triggered.connect(self._c_13)
        c_14.triggered.connect(self._c_14)

    def _c_1(self):
        self.loader.customer_id = 1
        self.show_last = self.loader.transaction_for_customer
        self._display_transactions_for_selected_customer()

    def _c_2(self):
        self.loader.customer_id = 2
        self.show_last = self.loader.transaction_for_customer
        self._display_transactions_for_selected_customer()

    def _c_3(self):
        self.loader.customer_id = 3
        self.show_last = self.loader.transaction_for_customer
        self._display_transactions_for_selected_customer()

    def _c_4(self):
        self.loader.customer_id = 4
        self.show_last = self.loader.transaction_for_customer
        self._display_transactions_for_selected_customer()

    def _c_8(self):
        self.loader.customer_id = 8
        self.show_last = self.loader.transaction_for_customer
        self._display_transactions_for_selected_customer()

    def _c_9(self):
        self.loader.customer_id = 9
        self.show_last = self.loader.transaction_for_customer
        self._display_transactions_for_selected_customer()

    def _c_10(self):
        self.loader.customer_id = 10
        self.show_last = self.loader.transaction_for_customer
        self._display_transactions_for_selected_customer()

    def _c_11(self):
        self.loader.customer_id = 11
        self.show_last = self.loader.transaction_for_customer
        self._display_transactions_for_selected_customer()

    def _c_12(self):
        self.loader.customer_id = 12
        self.show_last = self.loader.transaction_for_customer
        self._display_transactions_for_selected_customer()

    def _c_13(self):
        self.loader.customer_id = 13
        self.show_last = self.loader.transaction_for_customer
        self._display_transactions_for_selected_customer()

    def _c_14(self):
        self.loader.customer_id = 14
        self.show_last = self.loader.transaction_for_customer
        self._display_transactions_for_selected_customer()








