import logging
from os import getlogin, chdir, getcwd
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog

from core.Core import DateManager, Customer, Employee, Transaction, Product, ConnectionDB
from core.RaportFactoryCore import ProductGantt, CustomerOTDGeneralBarChart, CustomerOTDDetailsBarChart, TransactionStatisticStatusPieChart, ReportCreator


class ReportFactory(QMainWindow, DateManager):
    def __init__(self):
        QMainWindow.__init__(self)
        DateManager.__init__(self)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.db = ConnectionDB()
        self.me = Employee(db=self.db)
        self.me.set_login(getlogin())
        self.me.load_data()

        self.rep_gen_customer = Customer(db=self.me.db)
        self.rep_gen_transaction = Transaction(db=self.me.db)
        self.rep_gen_transactions = []
        self.otd_customer = Customer(db=self.me.db)
        self.trans_stats_customer = Customer(db=self.me.db)
        self.trans_stats_transaction = Transaction(db=self.me.db)
        self.trans_stats_transactions = []
        self.gantt_prod_customer = Customer(db=self.me.db)
        self.gantt_prod_product = Product(db=self.me.db)
        self.gantt_prod_products = []

        try:
            self.ui = uic.loadUi(r'src\ui\report_factory_mainwindow.ui', self)
        except Exception:
            self.logger.exception(f'Error while trying to find and load ui file')
            Terminate_Widget(20)

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self._load_otd_customer_combox()
        self._load_trans_stat_customer_combox()
        self._load_rep_gen_customer_combox()
        self._load_gantt_prod_customer_combox()

    def _connect_signals(self):
        self.ui.otd_customer_combox.activated.connect(self._activated_otd_customer_combox)
        self.ui.otd_show_button.clicked.connect(self._activated_otd_show_button)
        self.ui.otd_save_button.clicked.connect(self._activated_otd_save_button)

        self.ui.trans_stats_customer_combox.activated.connect(self._activated_trans_stats_customer_combox)
        self.ui.trans_stats_show_button.clicked.connect(self._activated_trans_stats_show_button)
        self.ui.trans_stats_save_button.clicked.connect(self._activated_trans_stats_save_button)
        self.ui.trans_stats_transaction_listwidget.itemSelectionChanged.connect(self._activated_trans_stats_transaction_listwidget)

        self.ui.rep_gen_customer_combox.activated.connect(self._activated_rep_gen_customer_combox)
        self.ui.rep_gen_save_button.clicked.connect(self._activated_rep_gen_save_button)
        self.ui.rep_gen_transaction_listwidget.itemSelectionChanged.connect(self._activated_rep_gen_transaction_listwidget)

        self.ui.gantt_prod_customer_combox.activated.connect(self._activated_gantt_prod_customer_combox)
        self.ui.gantt_prod_products_listwidget.itemSelectionChanged.connect(self._activated_gantt_prod_products_listwidget)
        self.ui.gantt_prod_show_button.clicked.connect(self._activated_gantt_prod_show_button)
        self.ui.gantt_prod_save_button.clicked.connect(self._activated_gantt_prod_save_button)

    def _load_otd_customer_combox(self):
        try:
            self.otd_customer.load_names()
            self.ui.otd_customer_combox.clear()
            for element in self.otd_customer.names:
                self.ui.otd_customer_combox.addItem(element)
        except Exception:
            self.logger.exception(f'FAILED loading customers to combox.\n')

    def _load_trans_stat_customer_combox(self):
        try:
            self.trans_stats_customer.load_names()
            self.ui.trans_stats_customer_combox.clear()
            for element in self.trans_stats_customer.names:
                self.ui.trans_stats_customer_combox.addItem(element)
        except Exception:
            self.logger.exception(f'FAILED loading customers to combox.\n')

    def _load_trans_stats_transaction_combox(self):
        try:
            self.trans_stats_transaction.customer.id = self.trans_stats_customer.id
            self.trans_stats_transaction.load_names_by_customer(show_active_only=False)
            # self.ui.trans_stats_transaction_combox.clear()
            for element in self.trans_stats_transaction.names:
                self.ui.trans_stats_transaction_combox.addItem(element)
        except Exception:
            self.logger.exception(f'FAILED loading transactions to combox.\n')

    def _load_trans_stats_transaction_listwidget(self):
        try:
            self.trans_stats_transaction.customer.id = self.trans_stats_customer.id
            self.trans_stats_transaction.load_names_by_customer(show_active_only=False)
            self.ui.trans_stats_transaction_listwidget.clear()
            for element in self.trans_stats_transaction.names[1:]:
                self.ui.trans_stats_transaction_listwidget.addItem(element)
        except Exception:
            self.logger.exception(f'FAILED loading transactions to combox.\n')

    def _load_rep_gen_customer_combox(self):
        try:
            self.rep_gen_customer.load_names()
            self.ui.rep_gen_customer_combox.clear()
            for element in self.rep_gen_customer.names:
                self.ui.rep_gen_customer_combox.addItem(element)
        except Exception:
            self.logger.exception(f'FAILED loading customers to combox.\n')

    def _load_rep_gen_transaction_listwidget(self):
        try:
            self.rep_gen_transaction.customer.id = self.rep_gen_customer.id
            self.rep_gen_transaction.load_names_by_customer(show_active_only=False)
            self.ui.rep_gen_transaction_listwidget.clear()
            for element in self.rep_gen_transaction.names[1:]:
                self.ui.rep_gen_transaction_listwidget.addItem(element)
        except Exception:
            self.logger.exception(f'FAILED loading transactions to listwidget.\n')

    def _load_gantt_prod_customer_combox(self):
        try:
            self.gantt_prod_customer.load_names()
            self.ui.gantt_prod_customer_combox.clear()
            for element in self.gantt_prod_customer.names:
                self.ui.gantt_prod_customer_combox.addItem(element)
        except Exception:
            self.logger.exception(f'FAILED loading customers to combox.\n')

    def _load_gantt_prod_products_listwidget(self):
        try:
            self.gantt_prod_product.load_products_for_customer_only(self.gantt_prod_customer.id)
            self.ui.gantt_prod_products_listwidget.clear()
            for element in self.gantt_prod_product.products[1:]:
                self.ui.gantt_prod_products_listwidget.addItem(element)
        except Exception:
            self.logger.exception(f'Exception while trying to load product to listwidget.\n')

    def _activated_otd_customer_combox(self):
        try:
            self.otd_customer.set_id_by_index(self.ui.otd_customer_combox.currentIndex())
        except Exception:
            self.logger.exception(f'Error while trying to activate customer_combox')
            Terminate_Widget(20)

    def _activated_otd_show_button(self):
        if self.otd_customer.id is not None:
            self.otd_customer.calculate_statistics()
            if self.ui.otd_detail_checkbox.isChecked():
                cust_otd_detail_bar_chart = CustomerOTDDetailsBarChart(self.otd_customer)
                cust_otd_detail_bar_chart.show_on_screen()
            else:
                cust_otd_general_bar_chart = CustomerOTDGeneralBarChart(self.otd_customer)
                cust_otd_general_bar_chart.show_on_screen()

    def _activated_otd_save_button(self):
        path = QFileDialog.getExistingDirectory(self, 'Select directory', r'C:\\')
        if path:
            self.otd_customer.calculate_statistics()
            if self.ui.otd_detail_checkbox.isChecked():
                cust_otd_detail_bar_chart = CustomerOTDDetailsBarChart(self.otd_customer)
                cust_otd_detail_bar_chart.save_image(customer=self.otd_customer, path=path, image_type='png')
            else:
                cust_otd_general_bar_chart = CustomerOTDGeneralBarChart(self.otd_customer)
                cust_otd_general_bar_chart.save_image(customer=self.otd_customer, path=path, image_type='png', )


    def _activated_trans_stats_customer_combox(self):
        try:
            self.trans_stats_customer.set_id_by_index(self.ui.trans_stats_customer_combox.currentIndex())
        except Exception:
            self.logger.exception(f'Error while trying to activate customer_combox')
            Terminate_Widget(20)
        else:
            self._load_trans_stats_transaction_combox()
            self._load_trans_stats_transaction_listwidget()

    def _activated_trans_stats_transaction_listwidget(self):
        self.trans_stats_transactions.clear()
        selection = self.ui.trans_stats_transaction_listwidget.selectedItems()
        ids = self.trans_stats_transaction.ids
        for element in selection:
            transaction = Transaction(db=self.me.db)
            transaction.set_id(ids[self.trans_stats_transaction.names.index(element.text())])
            self.trans_stats_transactions.append(transaction)

    def _activated_trans_stats_show_button(self):
        if self.trans_stats_transactions:
            for transaction in self.trans_stats_transactions:
                transaction.load_data_basic()
                transaction.filter_show_released_task = True
                transaction.calculate_statistics()
                trans_general_stats = TransactionStatisticStatusPieChart(transaction=transaction)
                trans_general_stats.show_on_screen()

    def _activated_trans_stats_save_button(self):
        path = QFileDialog.getExistingDirectory(self, 'Select directory', r'C:\\')
        if path:
            if self.trans_stats_transactions:
                for transaction in self.trans_stats_transactions:
                    transaction.filter_show_released_task = True
                    transaction.load_data_basic()
                    transaction.calculate_statistics()
                    trans_general_stats = TransactionStatisticStatusPieChart(transaction=transaction)
                    trans_general_stats.save_image(transaction=transaction, path=path, image_type='png')

    def _activated_rep_gen_transaction_listwidget(self):
        self.rep_gen_transactions.clear()
        selection = self.ui.rep_gen_transaction_listwidget.selectedItems()
        ids = self.rep_gen_transaction.ids
        for element in selection:
            transaction = Transaction(db=self.me.db)
            transaction.set_id(ids[self.rep_gen_transaction.names.index(element.text())])
            self.rep_gen_transactions.append(transaction)

    def _activated_rep_gen_customer_combox(self):
        try:
            self.rep_gen_customer.set_id_by_index(self.ui.rep_gen_customer_combox.currentIndex())
        except Exception:
            self.logger.exception(f'Error while trying to activate customer_combox')
            Terminate_Widget(20)
        else:
            self._load_rep_gen_transaction_listwidget()

    def _activated_rep_gen_save_button(self):
        path = QFileDialog.getExistingDirectory(self, 'Select directory', r'C:\\')
        if path:
            self.ui.statusBar().showMessage("Generating - Please Wait")
            try:
                comment_history = int(self.ui.rep_gen_weeks_history_combox.currentText())
                rep_gen = ReportCreator(self.me, path)
                detail_otd = self.ui.rep_gen_detail_otd_checkbox.isChecked()
                rep_gen.generate_report_for_customer(self.rep_gen_customer, detail_otd=detail_otd, transactions=self.rep_gen_transactions, comment_history=comment_history)
            except Exception :
                self.logger.exception('Report generation - failed')
                self.ui.statusBar().showMessage("Generating - FAILED")
            else:
                self.ui.statusBar().showMessage("Generating - Success")


    def _activated_gantt_prod_customer_combox(self):
        try:
            self.gantt_prod_customer.set_id_by_index(self.ui.gantt_prod_customer_combox.currentIndex())
        except Exception:
            self.logger.exception(f'Exception while trying to activate gantt_prod_customer_combox')
            Terminate_Widget(20)
        else:
            self._load_gantt_prod_products_listwidget()

    def _activated_gantt_prod_products_listwidget(self):
        self.gantt_prod_products.clear()
        selection = self.ui.gantt_prod_products_listwidget.selectedItems()
        ids = self.gantt_prod_product.ids
        for element in selection:
            product = Product(db=self.me.db)
            product.set_id(ids[self.gantt_prod_product.products.index(element.text())])
            self.gantt_prod_products.append(product)

    def _activated_gantt_prod_show_button(self):
        if self.gantt_prod_products:
            for product in self.gantt_prod_products:
                # product.load_data_basic()
                product.load_transactions(filter_show_released=self.ui.gantt_prod_show_released_transactions_checkbox.isChecked())
                gantt_prod_stats = ProductGantt(product=product)
                gantt_prod_stats.show_on_screen()

    def _activated_gantt_prod_save_button(self):
        path = QFileDialog.getExistingDirectory(self, 'Select directory', r'C:\\')
        if path:
            if self.gantt_prod_products:
                for product in self.gantt_prod_products:
                    try:
                        product.load_transactions(filter_show_released=self.ui.gantt_prod_show_released_transactions_checkbox.isChecked())
                        gantt_prod_stats = ProductGantt(product=product)
                        gantt_prod_stats.save_image(path=path, image_type='svg')
                    except Exception as err:
                        print(err)


if __name__ == "__main__":
    chdir(getcwd() + "\..")
    app = QApplication(sys.argv)
    rf = ReportFactory()
    rf.ui.show()
    sys.exit(app.exec_())
