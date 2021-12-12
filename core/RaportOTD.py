import logging
from os import getlogin
import sys
import datetime
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget, QHBoxLayout,QWidget, QVBoxLayout,QScrollArea, QGridLayout, QSpacerItem,QSizePolicy, QLabel, QComboBox, QGroupBox
from matplotlib.ticker import FuncFormatter
from core.Core import Employee, Date_picker_widget, DateManager, Customer, Product, Transaction, Task
from core.Widgets import Workload_Widget, Terminate_Widget, Linker_short_widget

from core.RaportFactoryCore import TransactionStatisticStatusPieChart

import matplotlib.dates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import WEEKLY, MONTHLY, DateFormatter, rrulewrapper, RRuleLocator
import matplotlib.font_manager as font_manager
from core.Core import Employee, Transaction
import datetime as dt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

class ReportOTD(QMainWindow,  DateManager):
    def __init__(self):
        QMainWindow.__init__(self)
        DateManager.__init__(self)
        self.logger = logging.getLogger(self.__class__.__name__)

        # self.addToolBar(NavigationToolbar(self.MplWidget.canvas, self))

        self.me = Employee()
        self.me.set_login(getlogin())
        self.me.load_data()

        self.customer = Customer(db=self.me.db)
        self.product = Product(db=self.me.db)
        self.transaction = Transaction(db=self.me.db)

        self.dtp = None  #DATA TO PRINT
        self.dtp_stats = None
        self.current_year = datetime.datetime.now().year
        self.chart_title = "OTD " + str(self.current_year)

        try:
            self.ui = uic.loadUi(r'src\ui\raport_otd.ui', self)
        except Exception:
            # print (err)
            self.logger.exception(f'Error while trying to find and load ui file')
            Terminate_Widget(20)

        self._print()
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self._load_customers_to_combox()
        try:
            self.addToolBar(NavigationToolbar(self.MplWidget.canvas, self))
        except Exception as err:
            print(err)

    def _connect_signals(self):
        self.ui.otd_customer_combox.activated.connect(self._activated_customer_combox)

    def _load_customers_to_combox(self):
        try:
            self.customer.load_names()
            self.ui.otd_customer_combox.clear()
            for element in self.customer.names:
                self.ui.otd_customer_combox.addItem(element)
        except Exception:
            self.logger.exception(f'FAILED loading customers to combox.\n')

    def _load_transactions_to_combox(self):
        try:
            self.transaction.customer.id = self.customer.id
            self.transaction.load_names_by_customer()
            self.ui.transaction_combox.clear()
            for element in self.transaction.names:
                self.ui.transaction_combox.addItem(element)
        except Exception:
            self.logger.exception(f'FAILED loading transactions to combox.\n')

    def _activated_customer_combox(self):
        try:
            self.customer.set_id_by_index(self.ui.otd_customer_combox.currentIndex())
            self.customer._calculate_otd_by_delivery_date()

            self.dtp = self.customer.stats.get_otd_by_delivery_date()
            self.dtp_stats = self.customer.stats.get_otd_stats_by_delivery_date()
            self.chart_title = "OTD " + str(self.current_year) + " (" + str(self.customer.name) + ")"
            self._print()

            self._load_transactions_to_combox()
        except Exception:
            self.logger.exception(f'Error while trying to activate customer_combox')
            Terminate_Widget(20)

    def _activated_product_combox(self):
        pass


    def _chart_settings(self):

        self.MplWidget.canvas.axes.set_ylim(0, 1)
        self.MplWidget.canvas.axes.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
        self.MplWidget.canvas.axes.set_xticks(range(12))
        self.MplWidget.canvas.axes.set_xticklabels(
            ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

        self.MplWidget.canvas.axes.set_title(self.chart_title, fontsize=18)
        self.MplWidget.canvas.axes.set_xlabel('Month', fontsize=16)
        self.MplWidget.canvas.axes.set_ylabel('On Time Delivery', fontsize=16)


class Gantt_for_Transaction(QWidget):

    def __init__(self):
        QWidget.__init__()

    def no_name(self):
        customColors = {"colorDeliverable": (0.44, 0.19, 0.63, 0.3),
                        "colorNonDeliverable": (0, 0.44, 0.75, 0.3),
                        "colorFinishedOnTime": (0, 0.69, 0.31, 1),
                        "colorFinishedNotOnTime": (1, 0, 0, 1),
                        "colorFinishedNotDeliveredYet": (1, 1, 0, 1),
                        "colorOngoing": (1, 0.53, 0.2, 1)}

        tt = Transaction()
        tt.set_id(109)
        tt.load_data_basic()
        tt.filter_show_released_task = True
        tt._load_all_tasks_for_transaction()

        ylabels = []
        plannedDates = []
        trueDates = []
        plannedBarColors = []
        trueBarColors = []

        ylabels.append(tt.name + "(transaction owner: " + tt.responsible.full_name + ")")
        if tt.true_end is None:
            trueDates.append([matplotlib.dates.date2num(tt.true_start), matplotlib.dates.date2num(dt.datetime.now())])
        else:
            trueDates.append([matplotlib.dates.date2num(tt.true_start), matplotlib.dates.date2num(tt.true_end)])
        plannedDates.append([matplotlib.dates.date2num(tt.planned_start), matplotlib.dates.date2num(tt.planned_end)])
        trueBarColors.append("orange")
        if tt.deliverable:
            plannedBarColors.append(customColors["colorDeliverable"])
        else:
            plannedBarColors.append(customColors["colorNonDeliverable"])

        for task in tt.tasks:
            if task.true_start is not None and task.true_end is not None:
                ylabels.append(task.name + "(owner: " + task.responsible.full_name + ")")
                trueDates.append([matplotlib.dates.date2num(task.true_start), matplotlib.dates.date2num(task.true_end)])
                plannedDates.append([matplotlib.dates.date2num(task.planned_start), matplotlib.dates.date2num(task.planned_end)])

                if task.true_end > task.planned_end:
                    trueBarColors.append(customColors["colorFinishedNotOnTime"])
                else:
                    trueBarColors.append(customColors["colorFinishedOnTime"])

                if task.deliverable:
                    plannedBarColors.append(customColors["colorDeliverable"])
                else:
                    plannedBarColors.append(customColors["colorNonDeliverable"])

        ilen = len(ylabels)
        pos = np.arange(0, ilen, 1)
        true_task_dates = {}
        planned_task_dates = {}
        for i, task in enumerate(ylabels):
            planned_task_dates[task] = plannedDates[i]
            true_task_dates[task] = trueDates[i]
        # fig = plt.figure(figsize=(17, ilen))
        # fig = plt.figure()
        # ax = fig.add_subplot(111)
        for i in range(len(ylabels)):
            true_start_date, true_end_date = true_task_dates[ylabels[i]]
            planned_start_date, planned_end_date = planned_task_dates[ylabels[i]]
            self.MplWidget.canvas.axes.text(planned_start_date, i - .23, ylabels[i], fontsize=9)
            self.MplWidget.canvas.axes.barh((i) - 0.2, planned_end_date - planned_start_date, left=planned_start_date, height=0.2, align='edge', edgecolor='black',
                                            color=plannedBarColors[i])

            self.MplWidget.canvas.axes.barh((i) + 0.0, true_end_date - true_start_date, left=true_start_date, height=0.2, align='edge', edgecolor='black', color=trueBarColors[i],
                                            alpha=0.5)

        try:
            # pass
            labelsy = self.MplWidget.canvas.axes.set_yticklabels(ylabels)
            for i, single in enumerate(labelsy):
                single.set_y(pos[i])
                single.set_x(1)
                single.set_text("OKO")

                # locsy, labelsy = self.MplWidget.canvas.axes.set_yticks(pos, ylabels)

        except Exception as err:
            print(err)
        labelsy = self.MplWidget.canvas.axes.get_yticklabels()
        plt.setp(labelsy, fontsize=12, wrap=True)

        # self.MplWidget.canvas.axes.set_ylim(ymin=-0.3, ymax=ilen - 0.2)
        # self.MplWidget.canvas.axes.grid(color='black', linestyle=':', alpha=0.3)
        self.MplWidget.canvas.axes.xaxis_date()
        rule = rrulewrapper(WEEKLY, interval=1)  # włączyc
        loc = RRuleLocator(rule)  # włączyc
        formatter = DateFormatter("%d-%b '%y")
        # formatter = DateFormatter("%d-%b")


        self.MplWidget.canvas.axes.xaxis.set_major_locator(loc)  # włączyc
        self.MplWidget.canvas.axes.xaxis.set_major_formatter(formatter)
        labelsx = self.MplWidget.canvas.axes.get_xticklabels()
        plt.setp(labelsx, rotation=90, fontsize=8)

        font = font_manager.FontProperties(size='small')
        self.MplWidget.canvas.axes.legend(loc=1, prop=font)

        self.MplWidget.canvas.axes.invert_yaxis()
        self.MplWidget.canvas.axes.set_title(tt.name + " - Gantt", fontsize=20)
        # fig.autofmt_xdate()
        self.MplWidget.canvas.axes.get_yaxis().set_visible(False)
        self.MplWidget.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    raport_otd = ReportOTD()
    raport_otd.ui.show()
    sys.exit(app.exec_())
