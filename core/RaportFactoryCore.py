import logging
import os
import matplotlib.pyplot
import numpy as np
import datetime as dt
from core.Core import DateManager, Status
from matplotlib.lines import Line2D
from matplotlib.dates import date2num, WEEKLY, MONTHLY, DateFormatter, rrulewrapper, RRuleLocator
import matplotlib.font_manager as font_manager

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle


polish_ascii = {"Ą": "A",
                "Ć": "C",
                "Ę": "E",
                "Ł": "L",
                "Ń": "N",
                "Ó": "O",
                "Ś": "S",
                "Ź": "Z",
                "Ż": "Z",
                "ą": "a",
                "ć": "c",
                "ę": "e",
                "ł": "l",
                "ń": "n",
                "ó": "o",
                "ś": "s",
                "ź": "z",
                "ż": "z"}
status = Status()

class CustomMplSettings:
    def __init__(self):
        self.colors = {"Done": (0.76, 0.76, 0.68, 1),
                       "Ongoing": (0.98, 0.63, 0.25, 1),
                       "Que": (0.33, 0.38, 0.46, 1),
                       "colorDeliverable": (0.31, 0.51, 0.07, 1),
                       "colorDeliverable2": (0, 0.45, 0.74, 1),
                       "colorNonDeliverable": (0.69, 0.84, 0.4, 1),
                       "colorNonDeliverable2": (0.55, 0.75, 0.88, 1),
                       "colorFinishedOnTime": (0, 0.69, 0.31, 1),
                       "colorFinishedNotOnTime": (1, 0, 0, 1),
                       "colorFinishedNotDeliveredYet": (1, 1, 0, 1),
                       "colorOngoing": (1, 0.53, 0.2, 1),
                       "Late": (0.78, 0, 0, 1),
                       "OnTime": (0.18, 0.35, 0.04, 1)
                       }


class TransactionStatisticPlanningPieChart:
    def __init__(self, transaction):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.plt = matplotlib.pyplot
        self.transaction = transaction
        self._show_grid = False
        self.custom_mpl_settings = CustomMplSettings()
        self._internal_calculation()
        self._plot_computing()

    def load_transaction(self, transaction):
        self.transaction = transaction
        self._internal_calculation()
        self._plot_computing()

    def show_on_screen(self):
        self.plt.show()

    def save_image(self, transaction, path=None, image_type="jpeg", dpi=100):
        if path is None:
            full_path = 'chart_pie_pln ' + transaction.name + "." + image_type
        else:
            full_path = path + '\\' + 'chart_pie_pln ' + transaction.name + "." + image_type
        try:
            self.plt.savefig(full_path, bbox_inches='tight', pad_inches=-.4, dpi=dpi)
            self.plt.clf()
            self.plt.cla()
            self.plt.close()
        except Exception:
            self.logger.exception(f'Unable to save figure. Please see details below')

    def _internal_calculation(self):
        stat = self.transaction.statistics
        self.plot_stats = dict()
        if stat['planning_on_time'] + stat['planning_late'] != 0:
            self.plot_stats["OnTime"] = round((stat['planning_on_time'] / (stat['planning_on_time'] + stat['planning_late']) * 100), 2)
            self.plot_stats["Late"] = round((stat['planning_late']/(stat['planning_on_time'] + stat['planning_late']) * 100), 2)
        else:
            self.plot_stats["OnTime"] = 0
            self.plot_stats["Late"] = 0
        self.plot_stats["StatsArray"]= np.array([[stat["planning_on_time"],
                                                  stat["planning_late"]]])

    def _plot_computing(self):
        fig = self.plt.figure(figsize=(7, 7), dpi=200)
        ax = fig.add_subplot(111)

        size = 0.45
        ring_colors = [self.custom_mpl_settings.colors['OnTime'],
                       self.custom_mpl_settings.colors['Late']]

        ax.pie(self.plot_stats['StatsArray'].sum(axis=0), radius=1.1, colors=ring_colors,
               wedgeprops=dict(width=size, edgecolor='w'))

        self.plt.vlines(0, -0.5, 0.5, colors='black')

        if self._show_grid:
            for i in range(-11, 11, 1):
                for j in range(-11, 11, 1):
                    ax.text(i/10, j/10, str(i/10) + ':' + str(j/10), fontsize=4)

        ax.text(-0.25, 0.2, "ON TIME", fontsize=14, va='center', ha='center', color=self.custom_mpl_settings.colors["OnTime"])
        ax.text(0.25, 0.2, "LATE", fontsize=14, va='center', ha='center', color=self.custom_mpl_settings.colors["Late"])
        ax.text(-0.3, 0, str(self.plot_stats['OnTime']) + "%", fontsize=26, va='center', ha='center', color=self.custom_mpl_settings.colors["OnTime"])
        ax.text(0.3, 0, str(self.plot_stats['Late']) + "%", fontsize=26, va='center', ha='center', color=self.custom_mpl_settings.colors["Late"])

        ax.set(aspect="equal")
        fig.tight_layout()


class TransactionStatisticStatusPieChart:
    def __init__(self, transaction):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.plt = matplotlib.pyplot
        self.transaction = transaction
        self._show_grid = False
        self.custom_mpl_settings = CustomMplSettings()
        self._internal_calculation()
        self._plot_computing()

    def load_transaction(self, transaction):
        self.transaction = transaction
        self._internal_calculation()
        self._plot_computing()

    def show_on_screen(self):
        self.plt.title(f"{self.transaction.name} - statistics")
        self.plt.show()


    def save_image(self, transaction, path=None, image_type="jpeg", dpi=100):
        if path is None:
            full_path = 'chart_pie_bas ' + transaction.name + "." + image_type
        else:
            full_path = path + '\\' + 'chart_pie_bas ' + transaction.name + "." + image_type
        try:
            self.plt.savefig(full_path, bbox_inches='tight', pad_inches=-.4, dpi=dpi)
            self.plt.clf()
            self.plt.cla()
            self.plt.close()
        except Exception:
            self.logger.exception(f'Unable to save figure. Please see details below')

    def _internal_calculation(self):
        tstat = self.transaction.statistics
        self.plot_stats = {}

        if tstat["tasks_count"] > 0:
            pre_stats = ((tstat["delivered_on_time"] + tstat["finished_on_time"]) / tstat["tasks_count"],
                         (tstat["delivered_late"] + tstat["finished_late"]) / tstat["tasks_count"],
                         tstat["ongoing_on_time"] / tstat["tasks_count"],
                         tstat["ongoing_late"] / tstat["tasks_count"],
                         tstat["planned_on_time"] / tstat["tasks_count"],
                         tstat["planned_late"] / tstat["tasks_count"])
        else:
            pre_stats = (0, 0, 0, 0, 0, 0)

        self.plot_stats['stats array'] = np.array([[pre_stats[0], pre_stats[1]], [pre_stats[2], pre_stats[3]], [pre_stats[4], pre_stats[5]]])

        if tstat['planned_on_time']+tstat['planned_late'] != 0:
            self.plot_stats["que_on_time"] = round(tstat['planned_on_time'] / (tstat['planned_on_time'] + tstat['planned_late']) * 100, 2)
            self.plot_stats["que_late"] = round(tstat['planned_late'] / (tstat['planned_on_time'] + tstat['planned_late']) * 100, 2)
            self.plot_stats["que_total"] = round((tstat['planned_on_time'] + tstat['planned_late']) / tstat['tasks_count'] * 100, 2)
        else:
            self.plot_stats["que_on_time"] = 0
            self.plot_stats["que_late"] = 0
            self.plot_stats["que_total"] = 0

        if tstat['ongoing_on_time']+tstat['ongoing_late'] != 0:
            self.plot_stats["ongoing_on_time"] = round(tstat['ongoing_on_time'] / (tstat['ongoing_on_time'] + tstat['ongoing_late']) * 100, 2)
            self.plot_stats["ongoing_late"] = round(tstat['ongoing_late'] / (tstat['ongoing_on_time'] + tstat['ongoing_late']) * 100, 2)
            self.plot_stats["ongoing_total"] = round((tstat['ongoing_on_time'] + tstat['ongoing_late']) / tstat['tasks_count'] * 100, 2)
        else:
            self.plot_stats["ongoing_on_time"] = 0
            self.plot_stats["ongoing_late"] = 0
            self.plot_stats["ongoing_total"] = 0

        if tstat['delivered_on_time'] + tstat['delivered_late'] + tstat['finished_on_time'] + tstat['finished_late'] != 0:
            self.plot_stats["done_on_time"] = round((tstat['delivered_on_time'] + tstat['finished_on_time']) / (tstat['delivered_on_time'] + tstat['delivered_late'] + tstat['finished_on_time'] + tstat['finished_late']) * 100, 2)
            self.plot_stats["done_late"] = round((tstat['delivered_late'] + tstat['finished_late']) / (tstat['delivered_on_time'] + tstat['delivered_late'] + tstat['finished_on_time'] + tstat['finished_late']) * 100, 2)
            self.plot_stats["done_total"] = round((tstat['finished_on_time'] + tstat['finished_late'] + tstat['delivered_on_time'] + tstat['delivered_late']) / tstat['tasks_count'] * 100, 2)
        else:
            self.plot_stats["done_on_time"] = 0
            self.plot_stats["done_late"] = 0
            self.plot_stats["done_total"] = 0

    def _plot_computing(self):
        fig = self.plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111)

        size = 0.2
        outer_colors = ['green', 'red', 'green', 'red', 'green', 'red']
        inner_colors = [self.custom_mpl_settings.colors['Done'],
                        self.custom_mpl_settings.colors['Ongoing'],
                        self.custom_mpl_settings.colors['Que']]

        ax.pie(self.plot_stats['stats array'].flatten(), radius=1.1, colors=outer_colors,
               wedgeprops=dict(width=size, edgecolor='w'))

        ax.pie(self.plot_stats['stats array'].sum(axis=1), radius=1.1 - size + 0.1, colors=inner_colors,
               wedgeprops=dict(width=size + 0.1, edgecolor='w'))

        if self._show_grid:
            for i in range(-11, 11, 1):
                for j in range(-11, 11, 1):
                    ax.text(i/10, j/10, str(i/10) + ':' + str(j/10), fontsize=4)

        self.plt.hlines(0.2, -0.5, 0.5, colors='black')
        self.plt.hlines(-0.2, -0.5, 0.5, colors='black')

        ax.text(0.0, 0.5, "QUE", fontsize=16, va='center', ha='center', color=self.custom_mpl_settings.colors["Que"])
        ax.text(0.0, 0.45, str(self.plot_stats['que_total']) + "%", fontsize=26, va='top', ha='center', color=self.custom_mpl_settings.colors["Que"])
        ax.text(-0.05, 0.3, str(self.plot_stats['que_on_time']) + "%", fontsize=12, va='top', ha='right', color=self.custom_mpl_settings.colors["OnTime"])
        ax.text(0.05, 0.3, str(self.plot_stats['que_late']) + "%", fontsize=12, va='top', ha='left', color=self.custom_mpl_settings.colors["Late"])

        ax.text(0.0, 0.12, "ONGOING", fontsize=16, va='center', ha='center', color=self.custom_mpl_settings.colors["Ongoing"])
        ax.text(0.0, 0.0, str(self.plot_stats["ongoing_total"]) + "%", fontsize=26, va='center', ha='center', color=self.custom_mpl_settings.colors["Ongoing"])
        ax.text(-0.05, -0.1, str(self.plot_stats['ongoing_on_time']) + "%", fontsize=12, va='top', ha='right', color=self.custom_mpl_settings.colors["OnTime"])
        ax.text(0.05, -0.1, str(self.plot_stats['ongoing_late']) + "%", fontsize=12, va='top', ha='left', color=self.custom_mpl_settings.colors["Late"])

        ax.text(0.0, -0.3, "DONE", fontsize=16, va='bottom', ha='center', color=self.custom_mpl_settings.colors["Done"])
        ax.text(0.0, -0.45, str(self.plot_stats["done_total"]) + "%", fontsize=26, va='bottom', ha='center', color=self.custom_mpl_settings.colors["Done"])
        ax.text(-0.05, -0.5, str(self.plot_stats['done_on_time']) + "%", fontsize=12, va='center', ha='right', color=self.custom_mpl_settings.colors["OnTime"])
        ax.text(0.05, -0.5, str(self.plot_stats['done_late']) + "%", fontsize=12, va='center', ha='left', color=self.custom_mpl_settings.colors["Late"])

        ax.set(aspect="equal")


class CustomerOTDGeneralBarChart:
    def __init__(self, customer):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.plt = matplotlib.pyplot
        self.custom_mpl_settings = CustomMplSettings()
        self._internal_calculation(customer)
        self._plot_computing(customer)

    def load_customer(self, customer):

        self._plot_computing(customer)

    def show_on_screen(self):
        self.plt.tight_layout()
        self.plt.show()

    def save_image(self, customer, path=None, image_type="jpeg", dpi=100):
        if path is None:
            full_path = 'chart_bar_otd ' + customer.name + "." + image_type
        else:
            full_path = path + '\\' + 'chart_bar_otd ' + customer.name + "." + image_type
        try:
            self.plt.savefig(full_path, bbox_inches='tight', dpi=dpi)
            self.plt.clf()
            self.plt.cla()
            self.plt.close()
        except Exception:
            self.logger.exception(f'Unable to save figure. Please see details below')

    def _internal_calculation(self, customer):
        stats = customer.statistics
        self.info_stats = {"deliverable": list(),
                           "nondeliverable": list()}
        self.otd_deliverable = np.zeros(12)
        self.otd_nondeliverable = np.zeros(12)

        for i in range(0, 12):
            if (stats['tasks_total_d'][i] + stats['transactions_total_d'][i]) != 0:
                self.otd_deliverable[i] = round((stats['tasks_on_time_d'][i] + stats['transactions_on_time_d'][i]) / (stats['tasks_total_d'][i] + stats['transactions_total_d'][i]) * 100, 2)

            if (stats['tasks_total_nd'][i] + stats['transactions_total_nd'][i]) != 0:
                self.otd_nondeliverable[i] = round((stats['tasks_on_time_nd'][i] + stats['transactions_on_time_nd'][i]) / (stats['tasks_total_nd'][i] + stats['transactions_total_nd'][i]) * 100, 2)

            self.info_stats['deliverable'].append(str((stats['tasks_on_time_d'][i] + stats['transactions_on_time_d'][i])) + '\n/\n' + str((stats['tasks_total_d'][i] + stats['transactions_total_d'][i])))
            self.info_stats['nondeliverable'].append(str((stats['tasks_on_time_nd'][i] + stats['transactions_on_time_nd'][i])) + '\n/\n' + str((stats['tasks_total_nd'][i] + stats['transactions_total_nd'][i])))

    def _plot_computing(self, customer):
        fig = self.plt.figure(figsize=(11.69, 8.27))
        ax = fig.add_subplot(111)

        months_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        bar_width = 0.4
        lab_location = np.arange(len(months_labels))

        bars_deliverable = ax.bar(lab_location - bar_width/2, self.otd_deliverable, bar_width, color=self.custom_mpl_settings.colors["colorDeliverable"], edgecolor="gray", label="DELIVERABLE")
        bars_nondeliverable = ax.bar(lab_location + bar_width/2, self.otd_nondeliverable, bar_width, color=self.custom_mpl_settings.colors["colorNonDeliverable"], edgecolor="gray", label="NON DELIVERABLE")

        ax.set_title(f'OTD - {customer.name} - 2019')
        ax.set_xticks(lab_location)
        ax.set_xticklabels(months_labels)
        ax.legend()

        self._autolabel(ax, bars_deliverable, self.info_stats['deliverable'])
        self._autolabel(ax, bars_nondeliverable, self.info_stats['nondeliverable'])

    def _autolabel(self, ax, rects, info):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for i, rect in enumerate(rects):
            height = rect.get_height()
            if height != 0:
                ax.annotate('{}%'.format(int(height)),
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=6)

                ax.annotate('{}'.format(info[i]),
                            xy=(rect.get_x() + rect.get_width() / 2, height-4),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='center', fontsize=7)


class CustomerOTDDetailsBarChart:
    def __init__(self, customer):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.plt = matplotlib.pyplot
        self.custom_mpl_settings = CustomMplSettings()
        self._internal_calculation(customer)
        self._plot_computing(customer)

    def load_customer(self, customer):

        self._plot_computing(customer)

    def show_on_screen(self):
        self.plt.tight_layout()
        self.plt.show()

    def save_image(self, customer, path=None, image_type="jpeg", dpi=100):
        if path is None:
            full_path = 'chart_det_otd ' + customer.name + "." + image_type
        else:
            full_path = path + '\\' + 'chart_det_otd ' + customer.name + "." + image_type
        try:
            self.plt.savefig(full_path, bbox_inches='tight', dpi=dpi)
            self.plt.clf()
            self.plt.cla()
            self.plt.close()
        except Exception:
            self.logger.exception(f'Unable to save figure. Please see details below')

    def _internal_calculation(self, customer):
        stats = customer.statistics
        self.info_stats = {"deliverable_tasks": list(),
                           "nondeliverable_tasks": list(),
                           "deliverable_transactions": list(),
                           "nondeliverable_transactions": list()}

        self.otd_deliverable_tasks = np.zeros(12)
        self.otd_deliverable_transactions = np.zeros(12)
        self.otd_nondeliverable_tasks = np.zeros(12)
        self.otd_nondeliverable_transactions = np.zeros(12)

        for i in range(0, 11):
            if stats['tasks_total_d'][i] != 0:
                self.otd_deliverable_tasks[i] = round(stats['tasks_on_time_d'][i] / stats['tasks_total_d'][i] * 100, 2)

            if stats['transactions_total_d'][i] != 0:
                self.otd_deliverable_transactions[i] = round(stats['transactions_on_time_d'][i] / stats['transactions_total_d'][i] * 100, 2)

            if stats['tasks_total_nd'][i] != 0:
                self.otd_nondeliverable_tasks[i] = round(stats['tasks_on_time_nd'][i] / stats['tasks_total_nd'][i] * 100, 2)

            if stats['transactions_total_nd'][i] != 0:
                self.otd_nondeliverable_transactions[i] = round(stats['transactions_on_time_nd'][i] / stats['transactions_total_nd'][i] * 100, 2)

            self.info_stats['deliverable_tasks'].append(str(stats['tasks_on_time_d'][i]) + '\n/\n' + str(stats['tasks_total_d'][i]))
            self.info_stats['nondeliverable_tasks'].append(str(stats['tasks_on_time_nd'][i]) + '\n/\n' + str(stats['tasks_total_nd'][i]))
            self.info_stats['deliverable_transactions'].append(str(stats['transactions_on_time_d'][i]) + '\n/\n' + str(stats['transactions_total_d'][i]))
            self.info_stats['nondeliverable_transactions'].append(str(stats['transactions_on_time_nd'][i]) + '\n/\n' + str(stats['transactions_total_nd'][i]))

    def _plot_computing(self, customer):
        fig = self.plt.figure(figsize=(11.69, 8.27))
        ax = fig.add_subplot(111)
        custom_color = self.custom_mpl_settings.colors

        months_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        bar_width = 0.2
        lab_location = np.arange(len(months_labels))

        bars_deliverable_tasks = ax.bar(lab_location - bar_width * 2 + 0.1, self.otd_deliverable_tasks, bar_width, color=custom_color['colorDeliverable'], edgecolor="gray", label="TASK d")
        bars_deliverable_transactions = ax.bar(lab_location - bar_width / 2, self.otd_deliverable_transactions, bar_width, color=custom_color['colorDeliverable2'], edgecolor="gray", label="TRANSACTIONS d")
        bars_nondeliverable_tasks = ax.bar(lab_location + bar_width / 2, self.otd_nondeliverable_tasks, bar_width, color=custom_color['colorNonDeliverable'], edgecolor="gray", label="TASK nd")
        bars_nondeliverable_transactions = ax.bar(lab_location + bar_width * 2 -0.1, self.otd_nondeliverable_transactions, bar_width, color=custom_color['colorNonDeliverable2'], edgecolor="gray", label="TRANSACTIONS nd")

        ax.set_title(f'DETAIL OTD - {customer.name} - {dt.datetime.now().year}')
        ax.set_xticks(lab_location)
        ax.set_xticklabels(months_labels)
        ax.legend()

        self._autolabel(ax, bars_deliverable_tasks, self.info_stats['deliverable_tasks'])
        self._autolabel(ax, bars_deliverable_transactions, self.info_stats['deliverable_transactions'])
        self._autolabel(ax, bars_nondeliverable_tasks, self.info_stats['nondeliverable_tasks'])
        self._autolabel(ax, bars_nondeliverable_transactions, self.info_stats['nondeliverable_transactions'])

    def _autolabel(self, ax, rects, info):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for i, rect in enumerate(rects):
            height = rect.get_height()
            if height != 0:
                ax.annotate('{}'.format(int(height)),
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=4)

                ax.annotate('{}'.format(info[i]),
                            xy=(rect.get_x() + rect.get_width() / 2, height-3),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='center', fontsize=4)


class TransactionGantt:
    def __init__(self, transaction):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.transaction = transaction
        self.plt = matplotlib.pyplot
        self.custom_mpl_settings = CustomMplSettings()
        self._plot_computing()

    def load_transaction(self, transaction):
        self.transaction = transaction
        self._plot_computing()

    def show_on_screen(self):
        self.plt.show()

    def save_image(self, path=None, image_type="jpeg", dpi=100):
        if path is None:
            full_path = 'chart_bar_gnt ' + self.transaction.name + "." + image_type
        else:
            full_path = path + '\\' + 'chart_bar_gnt ' + self.transaction.name + "." + image_type
        try:
            self.plt.savefig(full_path, bbox_inches='tight', dpi=dpi)
            self.plt.clf()
            self.plt.cla()
            self.plt.close()
        except Exception:
            self.logger.exception(f'Unable to save figure. Please see details below')

    def _plot_computing(self):
        ylabels = []
        plannedDates = []
        trueDates = []
        plannedBarColors = []
        trueBarColors = []

        ylabels.append(self.transaction.name + "\n(transaction owner: " + self.transaction.responsible.full_name + ")")

        if self.transaction.true_end is None:
            if self.transaction.true_start is None:
                trueDates.append([date2num(dt.datetime.now()), date2num(dt.datetime.now())])
            else:
                trueDates.append([date2num(self.transaction.true_start), date2num(dt.datetime.now())])
        else:
            trueDates.append([date2num(self.transaction.true_start), date2num(self.transaction.true_end)])
        plannedDates.append([date2num(self.transaction.planned_start), date2num(self.transaction.planned_end)])
        trueBarColors.append("orange")
        if self.transaction.deliverable:
            plannedBarColors.append(self.custom_mpl_settings.colors["colorDeliverable"])
        else:
            plannedBarColors.append(self.custom_mpl_settings.colors["colorNonDeliverable"])

        for task in self.transaction.tasks:
            if task.true_start is not None and task.true_end is not None:
                ylabels.append(task.name + "\n(owner: " + task.responsible.full_name + ")")
                trueDates.append([date2num(task.true_start), date2num(task.true_end)])
                plannedDates.append([date2num(task.planned_start), date2num(task.planned_end)])

                if task.true_end > task.planned_end:
                    trueBarColors.append(self.custom_mpl_settings.colors["colorFinishedNotOnTime"])
                else:
                    trueBarColors.append(self.custom_mpl_settings.colors["colorFinishedOnTime"])

                if task.deliverable:
                    plannedBarColors.append(self.custom_mpl_settings.colors["colorDeliverable"])
                else:
                    plannedBarColors.append(self.custom_mpl_settings.colors["colorNonDeliverable"])

        ilen = len(ylabels)
        pos = np.arange(0, ilen * 0.5 + 0.5, 0.5)
        true_task_dates = {}
        planned_task_dates = {}
        for i, task in enumerate(ylabels):
            planned_task_dates[task] = plannedDates[i]
            true_task_dates[task] = trueDates[i]
        fig = self.plt.figure(figsize=(11, 8))
        # fig = plt.figure()
        ax = fig.add_subplot(111)
        for i in range(len(ylabels)):
            true_start_date, true_end_date = true_task_dates[ylabels[i]]
            planned_start_date, planned_end_date = planned_task_dates[ylabels[i]]
            # ax.text(true_start_date-10, i*0.5-.14, "DATES", fontsize=7)
            ax.barh((i * 0.5) - 0.2, planned_end_date - planned_start_date, left=planned_start_date, height=0.2, align='edge', edgecolor='black', color=plannedBarColors[i])

            ax.barh((i * 0.5) + 0.0, true_end_date - true_start_date, left=true_start_date, height=0.2, align='edge', edgecolor='black', color=trueBarColors[i], alpha=0.5)

        locsy, labelsy = self.plt.yticks(pos, ylabels)
        self.plt.setp(labelsy, fontsize=9, wrap=True)

        ax.set_ylim(ymin=-0.3, ymax=ilen * 0.5 - 0.2)
        ax.grid(color='black', linestyle=':', alpha=0.3)
        ax.xaxis_date()
        rule = rrulewrapper(WEEKLY, interval=1)  # włączyc
        loc = RRuleLocator(rule)  # włączyc
        formatter = DateFormatter("%d-%b '%y")
        # formatter = DateFormatter("%d-%b")


        ax.xaxis.set_major_locator(loc)  # włączyc
        ax.xaxis.set_major_formatter(formatter)
        labelsx = ax.get_xticklabels()
        self.plt.setp(labelsx, rotation=1, fontsize=8)

        font = font_manager.FontProperties(size='small')
        ax.legend(loc=1, prop=font)

        ax.invert_yaxis()
        ax.set_title(self.transaction.name + " - Gantt", fontsize=20)
        fig.autofmt_xdate()
        # fig.tight_layout()


class ProductGantt:
    def __init__(self, product):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.product = product
        self.plt = matplotlib.pyplot
        self.custom_mpl_settings = CustomMplSettings()
        self._plot_computing2()

    def load_product(self, product):
        self.product = product
        self._plot_computing2()

    def show_on_screen(self):
        self.plt.show()

    def save_image(self, path=None, image_type="jpeg", dpi=100):
        if path is None:
            full_path = 'chart_bar_gnt_prod ' + self.product.product + "." + image_type
        else:
            full_path = path + '\\' + 'chart_bar_gnt_prod ' + self.product.product + "." + image_type
        try:
            self.plt.savefig(full_path, bbox_inches='tight', dpi=dpi)
            self.plt.clf()
            self.plt.cla()
            self.plt.close()
        except Exception:
            self.logger.exception(f'Unable to save figure. Please see details below')

    def _plot_computing(self):
        today = dt.date.today()
        ylabels = []
        plannedDates = []
        trueDates = []
        plannedBarColors = []
        trueBarColors = []

        for transaction in self.product.transactions:
            ylabels.append(transaction.name + "\n(owner: " + transaction.responsible.full_name + ")")

            plannedDates.append([date2num(transaction.planned_start), date2num(transaction.planned_end)])
            if transaction.deliverable:
                plannedBarColors.append(self.custom_mpl_settings.colors["colorDeliverable"])
            else:
                plannedBarColors.append(self.custom_mpl_settings.colors["colorNonDeliverable"])

            if transaction.true_start is None:
                trueDates.append([date2num(today), date2num(today)])
                trueBarColors.append((0, 0, 0, 0))
            else:
                if transaction.deliverable:
                    if transaction.true_delivery is None:
                        trueDates.append([date2num(transaction.true_start), date2num(today)])
                        if today > transaction.planned_delivery:
                            trueBarColors.append(self.custom_mpl_settings.colors["Late"])
                        else:
                            trueBarColors.append(self.custom_mpl_settings.colors["Ongoing"])
                    else:
                        trueDates.append([date2num(transaction.true_start), date2num(transaction.true_delivery)])
                        if transaction.true_delivery > transaction.planned_delivery:
                            trueBarColors.append(self.custom_mpl_settings.colors["Late"])
                        else:
                            trueBarColors.append(self.custom_mpl_settings.colors["colorFinishedOnTime"])
                else:
                    if transaction.true_end is None:
                        trueDates.append([date2num(transaction.true_start), date2num(today)])
                        if today > transaction.planned_end:
                            trueBarColors.append(self.custom_mpl_settings.colors["Late"])
                        else:
                            trueBarColors.append(self.custom_mpl_settings.colors["Ongoing"])
                    else:
                        trueDates.append([date2num(transaction.true_start), date2num(transaction.true_end)])
                        if transaction.true_end > transaction.planned_end:
                            trueBarColors.append(self.custom_mpl_settings.colors["Late"])
                        else:
                            trueBarColors.append(self.custom_mpl_settings.colors["colorFinishedOnTime"])



        ilen = len(ylabels)
        pos = np.arange(0, ilen * 0.5 + 0.5, 0.5)
        true_transactions_dates = {}
        planned_transactions_dates = {}
        for i, transaction in enumerate(ylabels):
            planned_transactions_dates[transaction] = plannedDates[i]
            true_transactions_dates[transaction] = trueDates[i]
        fig = self.plt.figure(figsize=(19, ilen/1.5))
        # fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.axvline(x=date2num(today), color='r', alpha=0.5)
        for i in range(len(ylabels)):
            true_start_date, true_end_date = true_transactions_dates[ylabels[i]]
            planned_start_date, planned_end_date = planned_transactions_dates[ylabels[i]]
            # ax.text(true_start_date-10, i*0.5-.14, "DATES", fontsize=7)
            ax.barh((i * 0.5) - 0.2, planned_end_date - planned_start_date, left=planned_start_date, height=0.2, align='edge', edgecolor='black', color=plannedBarColors[i])
            ax.barh((i * 0.5) + 0.0, true_end_date - true_start_date, left=true_start_date, height=0.2, align='edge', edgecolor='black', color=trueBarColors[i], alpha=0.5)

        locsy, labelsy = self.plt.yticks(pos, ylabels)
        self.plt.setp(labelsy, fontsize=9, wrap=True)

        ax.set_ylim(ymin=-0.3, ymax=ilen * 0.5 - 0.2)
        ax.grid(color='black', linestyle=':', alpha=0.3)
        ax.xaxis_date()
        rule = rrulewrapper(WEEKLY, interval=1)  # włączyc
        loc = RRuleLocator(rule)  # włączyc
        formatter = DateFormatter("%d-%b '%y")
        # formatter = DateFormatter("%d-%b")


        ax.xaxis.set_major_locator(loc)  # włączyc
        ax.xaxis.set_major_formatter(formatter)
        labelsx = ax.get_xticklabels()
        self.plt.setp(labelsx, rotation=1, fontsize=8)

        font = font_manager.FontProperties(size='small')
        ax.legend(loc=1, prop=font)

        ax.invert_yaxis()
        ax.set_title(self.product.product + " - Gantt", fontsize=20)
        fig.autofmt_xdate()
        # fig.tight_layout()

    def _plot_computing2(self):
        today = dt.date.today()
        to_plot = dict()
        to_plot[1] = 1

        for transaction in self.product.transactions:
            to_plot[transaction.id] = dict()
            to_plot[transaction.id]['name'] = str(transaction.name) + "\n(owner: " + str(transaction.responsible.full_name) + ")"
            to_plot[transaction.id]['planned_start'] = transaction.planned_start
            to_plot[transaction.id]['planned_end'] = transaction.planned_end
            if transaction.deliverable:
                to_plot[transaction.id]["planned_color"] = self.custom_mpl_settings.colors["colorDeliverable"]
            else:
                to_plot[transaction.id]["planned_color"] = self.custom_mpl_settings.colors["colorNonDeliverable"]
            if transaction.true_start is None:
                to_plot[transaction.id]['true_start'] = today
                to_plot[transaction.id]['true_end'] = today
                to_plot[transaction.id]['true_color'] = (0, 0, 0, 0)
            else:
                if transaction.deliverable:
                    if transaction.true_delivery is None:
                        to_plot[transaction.id]['true_start'] = transaction.true_start
                        to_plot[transaction.id]['true_end'] = today
                        if today > transaction.planned_delivery:
                            to_plot[transaction.id]['true_color'] = self.custom_mpl_settings.colors["Late"]
                        else:
                            to_plot[transaction.id]['true_color'] = self.custom_mpl_settings.colors["Ongoing"]
                    else:
                        to_plot[transaction.id]['true_start'] = transaction.true_start
                        to_plot[transaction.id]['true_end'] = transaction.true_delivery
                        if transaction.true_delivery > transaction.planned_delivery:
                            to_plot[transaction.id]['true_color'] = self.custom_mpl_settings.colors["Late"]
                        else:
                            to_plot[transaction.id]['true_color'] = self.custom_mpl_settings.colors["colorFinishedOnTime"]
                else:
                    if transaction.true_end is None:
                        to_plot[transaction.id]['true_start'] = transaction.true_start
                        to_plot[transaction.id]['true_end'] = today
                        if today > transaction.planned_end:
                            to_plot[transaction.id]['true_color'] = self.custom_mpl_settings.colors["Late"]
                        else:
                            to_plot[transaction.id]['true_color'] = self.custom_mpl_settings.colors["Ongoing"]
                    else:
                        to_plot[transaction.id]['true_start'] = transaction.true_start
                        to_plot[transaction.id]['true_end'] = transaction.true_end
                        if transaction.true_end > transaction.planned_end:
                            to_plot[transaction.id]['true_color'] = self.custom_mpl_settings.colors["Late"]
                        else:
                            to_plot[transaction.id]['true_color'] = self.custom_mpl_settings.colors["colorFinishedOnTime"]


    def controler(self, all_to_plot):
        batches = {}

        for i, transaction in enumerate(all_to_plot):
            trans_set = {}
            trans_set



    def _no_name(self, to_plot):
        today = dt.date.today()
        ilen = len(to_plot)
        pos = np.arange(0, ilen * 0.5 + 0.5, 0.5)
        ylabels = []
        fig = self.plt.figure(figsize=(19, ilen / 1.5))
        ax = fig.add_subplot(111)
        ax.axvline(x=date2num(today), color='r', alpha=0.5)
        i = 0
        for key, value in to_plot.items():
            # ax.text(true_start_date-10, i*0.5-.14, "DATES", fontsize=7)
            ax.barh((i * 0.5) - 0.2, date2num(value["planned_end"]) - date2num(value["planned_start"]), left=date2num(value["planned_start"]), height=0.2, align='edge',
                    edgecolor='black', color=value['planned_color'])
            ax.barh((i * 0.5) + 0.0, date2num(value['true_end']) - date2num(value["true_start"]), left=date2num(value["true_start"]), height=0.2, align='edge', edgecolor='black',
                    color=value['true_color'], alpha=0.5)
            ylabels.append(value["name"])
            i += 1

        locsy, labelsy = self.plt.yticks(pos, ylabels)
        self.plt.setp(labelsy, fontsize=9, wrap=True)

        ax.set_ylim(ymin=-0.3, ymax=ilen * 0.5 - 0.2)
        ax.grid(color='black', linestyle=':', alpha=0.3)
        ax.xaxis_date()
        rule = rrulewrapper(WEEKLY, interval=1)  # włączyc
        loc = RRuleLocator(rule)  # włączyc
        formatter = DateFormatter("%d-%b '%y")
        # formatter = DateFormatter("%d-%b")


        ax.xaxis.set_major_locator(loc)  # włączyc
        ax.xaxis.set_major_formatter(formatter)
        labelsx = ax.get_xticklabels()
        self.plt.setp(labelsx, rotation=1, fontsize=8)

        font = font_manager.FontProperties(size='small')
        ax.legend(loc=1, prop=font)

        ax.invert_yaxis()
        ax.set_title(self.product.product + " - Gantt", fontsize=20)
        fig.autofmt_xdate()
        # fig.tight_layout()


class ReportCreator(DateManager):
    def __init__(self, employee, path):
        self.logger = logging.getLogger(self.__class__.__name__)
        DateManager.__init__(self)
        self.path = path
        self.canvas = canvas.Canvas(f"{self.path}//TATO - Report {dt.datetime.now().strftime('%d%m%Y%H%M%S')}.pdf", bottomup=1, verbosity=1)
        self.height, self.width = A4
        self.me = employee
        self.canvas.setAuthor(self.me.full_name)
        self.canvas.setTitle("T.A.T.O Report")
        self.cleaning_list = []

    def load_transaction(self, transaction):
        self.transaction = transaction

    def _plot_charts(self, transaction):
        trans_stat = TransactionStatisticStatusPieChart(transaction)
        trans_stat.save_image(path=self.path, transaction=transaction, image_type='png', dpi=300)

        trans_stat_planned = TransactionStatisticPlanningPieChart(transaction)
        trans_stat_planned.save_image(path=self.path,transaction=transaction, image_type='png', dpi=300)

        # trans_gantt = TransactionGantt(transaction)
        # trans_gantt.save_image(path=r'D:\Testy\Tato report', image_type='svg')

    def _coord(self, x, y, unit=mm):
        x, y = x * unit, self.height - y * unit
        return x, y

    def generate_report_for_customer(self, customer, detail_otd=True, transactions=None, comment_history=2):
        self._prepare_first_page()
        self.comment_history = comment_history
        # customer.load_transactions()
        customer.calculate_statistics()
        cust_otd_general = CustomerOTDGeneralBarChart(customer)
        cust_otd_general.save_image(customer, path=self.path, image_type='png', dpi=300)
        self._prepare_customer_otd(customer)

        # customer.load_products()
        # for product in customer.products:
        #     product.load_transactions(filter_show_released=False)
        #     gantt_product = ProductGantt(product)
        #     gantt_product.save_image(path=self.path, image_type='png', dpi=300)
        #     self._prepare_gantt_for_customer(product)

        if detail_otd:
            cust_otd_detail = CustomerOTDDetailsBarChart(customer)
            cust_otd_detail.save_image(customer, path=self.path, image_type='png', dpi=300)
            self._prepare_customer_otd_detail(customer)

        if transactions is not None:
            customer.transactions = transactions

        for transaction in customer.transactions:
            self.transaction = transaction
            self.transaction.load_data_basic()
            self.transaction.filter_show_released_task = True
            self.transaction._load_all_tasks_for_transaction()
            self.transaction.calculate_statistics()
            self._plot_charts(transaction)
            self._prepare_pie_statistics(transaction)
            # self._prepare_gantt()

        self.canvas.save()
        self._clean()

    def generate_report_for_transaction(self, transaction):
        # self.transaction = transaction
        transaction.load_data_basic()
        transaction.filter_show_released_task = True
        transaction._load_all_tasks_for_transaction()
        transaction.calculate_statistics()
        self._prepare_first_page()
        self._plot_charts(transaction)
        self._prepare_pie_statistics(transaction)
        self._prepare_gantt(transaction)
        self.canvas.save()
        self._clean()

    def _prepare_first_page(self,):
        self.canvas.setPageSize(landscape(A4))
        self.canvas.setFont('Times-Roman', 40)
        self.canvas.drawCentredString(*self._coord(297/2, 23, mm), "T.A.T.O. REPORT")
        self.canvas.line(*self._coord(15, 35, mm), *self._coord(297-15, 35, mm))
        self.canvas.setFont('Times-Roman', 12)
        self.canvas.drawString(*self._coord(20, 45, mm), "PREPARED BY:")
        self.canvas.drawString(*self._coord(20, 51, mm), "E-MAIL:")
        self.canvas.drawString(*self._coord(20, 57, mm), "DATE:")

        self.canvas.drawString(*self._coord(55, 45, mm), f"{self.me.full_name}")
        self.canvas.drawString(*self._coord(55, 51, mm), f"{self.me.e_mail}")
        self.canvas.drawString(*self._coord(55, 57, mm), f"{dt.datetime.now().strftime('%d %b %Y, %H:%M')}")

        self.canvas.line(*self._coord(15, 200, mm), *self._coord(297 - 15, 200, mm))
        self.canvas.setFont('Times-Roman', 10)
        self.canvas.drawCentredString(*self._coord(297/2, 205, mm), "THIS DOCUMENT WAS PREPARED AUTOMATICALY BY T.A.T.O. APPLICATION")

        story = []
        toc = TableOfContents()
        PS = ParagraphStyle
        toc.levelStyles = [PS(fontName='Times-Bold', fontSize=14, name='TOCHeading1',
                              leftIndent=20, firstLineIndent=-20, spaceBefore=5, leading=16),
                           PS(fontSize=12, name='TOCHeading2',
                              leftIndent=40, firstLineIndent=-20, spaceBefore=0, leading=12),
                           PS(fontSize=10, name='TOCHeading3',
                              leftIndent=60, firstLineIndent=-20, spaceBefore=0, leading=12),
                           PS(fontSize=10, name='TOCHeading4',
                              leftIndent=100, firstLineIndent=-20, spaceBefore=0, leading=12),
        ]
        story.append(toc)

    def _prepare_pie_statistics(self, transaction):
        self.canvas.showPage()

        # self.canvas.setPageSize(landscape(A4))

        #LINES
        self.canvas.line(*self._coord(120, 15, mm), *self._coord(120, 200, mm))
        self.canvas.line(*self._coord(10, 15, mm), *self._coord(297 - 10, 15, mm))
        self.canvas.line(*self._coord(10, 20, mm), *self._coord(297-10, 20, mm))

        #TEXT LAYOUT
        self.canvas.setFont('Times-Roman', 16)
        self.canvas.drawCentredString(*self._coord(297/2, 10, mm), f"{transaction.name}")
        self.canvas.setFont('Times-Roman', 12)
        self.canvas.drawCentredString(*self._coord(208, 19, mm), "COMMENTS")
        self.canvas.drawCentredString(*self._coord(60, 19, mm), "STATISTICS")

        self.canvas.drawCentredString(*self._coord(60, 118, mm), "PLANNING")
        self.canvas.drawCentredString(*self._coord(60, 26, mm), "STATUS")

        #PIE CHARTS
        self.canvas.drawImage(f"{self.path}/chart_pie_bas {transaction.name}.png", *self._coord(20, 28, mm), 80*mm, -80*mm)
        self.canvas.drawImage(f"{self.path}/chart_pie_pln {transaction.name}.png", *self._coord(20, 120, mm), 80*mm, -80*mm)

        self.cleaning_list.append(f"{self.path}/chart_pie_bas {transaction.name}.png")
        self.cleaning_list.append(f"{self.path}/chart_pie_pln {transaction.name}.png")

        #COMMENTS
        today = dt.date.today()
        weekday = today.weekday()
        start_date_range = today - dt.timedelta(days=weekday, weeks=self.comment_history)
        # end_date_range = start_date_range + dt.timedelta(5)
        end_date_range = today

        transaction._load_comments()
        styleSheet = getSampleStyleSheet()
        style = styleSheet['BodyText']
        self.anchorY = 25
        self.canvas.setFont('Times-Roman', 7)
        self.canvas.setFillColorRGB(0.4, 0.4, 0.4)
        transaction.comments.reverse()
        for comment in transaction.comments:
            if self.convert_to_date_class(comment.publishing_date) >= start_date_range and self.convert_to_date_class(comment.publishing_date) <= end_date_range:
                P = Paragraph(f'{comment.description}', style)
                w, h = P.wrap(155*mm, 12)
                P.drawOn(self.canvas, *self._coord(130, self.anchorY + h / mm, mm))

                publisher_name = comment.publisher.full_name
                for w in publisher_name:
                    if w in polish_ascii:
                        publisher_name = publisher_name.replace(w, polish_ascii[w])
                self.canvas.drawString(*self._coord(128, self.anchorY, mm), f'{publisher_name}  {comment.publishing_date}')
                self.anchorY += h / mm + 2 *mm

    def _clean(self):
        for element in self.cleaning_list:
            try:
                os.remove(element)
            except Exception:
                self.logger.exception("Error while trying to remove file")
            else:
                print("File removed: ", element)

        self.cleaning_list.clear()

    def _prepare_gantt(self, transaction):
        self.canvas.showPage()
        self.canvas.drawImage(f"{self.path}/chart_bar_gnt {transaction.name}.png", *self._coord(0, 0, mm), 297 * mm, -210 * mm)
        self.cleaning_list.append(f"{self.path}/chart_bar_gnt {transaction.name}.png")

    def _prepare_gantt_for_customer(self, product):
        self.canvas.showPage()
        self.canvas.drawImage(f'{self.path}/chart_bar_gnt_prod {product.product}.png', *self._coord(0, 0, mm), 297 * mm, -210 * mm)
        self.cleaning_list.append(f'{self.path}/chart_bar_gnt_prod {product.product}.png')

    def _prepare_customer_otd(self, customer):
        self.canvas.showPage()
        self.canvas.drawImage(f"{self.path}/chart_bar_otd {customer.name}.png", *self._coord(0, 0, mm), 297 * mm, -210 * mm)
        self.cleaning_list.append(f"{self.path}/chart_bar_otd {customer.name}.png")

    def _prepare_customer_otd_detail(self, customer):
        self.canvas.showPage()
        self.canvas.drawImage(f"{self.path}/chart_det_otd {customer.name}.png", *self._coord(0, 0, mm), 297 * mm, -210 * mm)
        self.cleaning_list.append(f"{self.path}/chart_det_otd {customer.name}.png")