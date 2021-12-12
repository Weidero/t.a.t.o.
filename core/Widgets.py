#THIS DOCUMENT DOES NOT CONTAIN ANY TECHNICAL DATA

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QLabel, QRadioButton, QSizePolicy, QSpacerItem, QComboBox, QScrollArea, QVBoxLayout,QSlider, QGridLayout, QHBoxLayout,QRadioButton, QListWidget, QGroupBox, QPushButton, QTextEdit, QDateEdit, QLineEdit, QFileDialog, QInputDialog, QMessageBox, QCheckBox, QLCDNumber, QTextBrowser
from PyQt5.QtCore import pyqtProperty, Qt, pyqtSignal, QDateTime, QTimer, QDate
from PyQt5.QtGui import QFont, QColor, QPen, QPainter
import os
import subprocess
import logging
import copy
import time, sys
from pathlib import Path
from core.Core import Status, DateManager, Comment, Customer, Transaction, Discipline, Activity, Employee, Task, \
    Product, Transaction_type, Check, Rework, EmailSender
from datetime import timedelta, date, datetime

# information
"""
 /$$$$$$$$   /$$$$$$   /$$$$$$$$   /$$$$$$ 
|__  $$__/  /$$__  $$ |__  $$__/  /$$__  $$
   | $$    | $$  \ $$    | $$    | $$  \ $$
   | $$    | $$$$$$$$    | $$    | $$  | $$
   | $$    | $$__  $$    | $$    | $$  | $$
   | $$    | $$  | $$    | $$    | $$  | $$
   | $$ /$$| $$  | $$ /$$| $$ /$$|  $$$$$$/
   |__/|__/|__/  |__/|__/|__/|__/ \______/ 

Module:         Widgets
Version         1.0 alpha 1
Release date:   21.02.2019

This module is integral part of application T.A.T.O 
It CAN'T be used whitout colaboration with other T.A.T.O core.
"""

status = Status()

class Terminate_Widget(QDialog):
    def __init__(self, exit_code=666, parent=None):
        self.logger = logging.getLogger(__name__ + '.' + self.__class__.__name__)
        QDialog.__init__(self, parent=parent)
        self.ui = uic.loadUi(r'src\ui\terminated.ui', self)
        self.exit_code = exit_code
        self._setup_ui()
        self._connect_signals()
        self.ui.show()

    def _setup_ui(self):
        pass

    def _connect_signals(self):
        self.ui.ok_button.pressed.connect(self._activated_ok_button)

    def _activated_ok_button(self):
        sys.exit(self.exit_code)


class Linker_short_widget(QWidget):
    def __init__(self, task, parent=None):
        QWidget.__init__(self, parent=parent)
        self.task = task
        self.db = self.task.db
        self.links_list = []

        self._initUI()
        self._connect_signals()

    def _connect_signals(self):
        self.task.signal_id_changed.connect(self._reload)
        # self.new_directory_button.clicked.connect(self._reload)
        # self.new_file_button.clicked.connect(self._reload)
        self.new_file_button.pressed.connect(self._link_file_button_pressed)
        self.new_directory_button.pressed.connect(self._link_directory_button_pressed)
        self.all_links_list.itemSelectionChanged.connect(self._all_list_link_changed)
        self.all_links_list.itemActivated.connect(self._open_link)


    def _initUI(self):
        groupbox = QGroupBox("Linker")
        # groupbox.setMaximumHeight(200)
        sublayout = QGridLayout()

        self.new_directory_button = QPushButton("Folder")
        self.new_file_button = QPushButton("File")
        self.all_links_list = QListWidget()

        sublayout.addWidget(self.new_directory_button, 0, 0)
        sublayout.addWidget(self.new_file_button, 0, 1)
        sublayout.addWidget(self.all_links_list, 1, 0, 1, 2)

        groupbox.setLayout(sublayout)

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(groupbox)


        self.setLayout(layout)


    def _reload(self):
        self.all_links_list.clear()
        self.links_list.clear()

        cmd = '''SELECT
                id,
                link_name
                FROM
                task_links
                WHERE
                task_id = ?'''
        param = [self.task.id, ]

        try:
            self.db.cursor.execute(cmd, param)
            sql_ret = self.db.cursor.fetchall()
            for link in sql_ret:
                self.links_list.append(link[0])
                self.all_links_list.addItem(link[1])
        except Employee as err:
            pass

    def _link_file_button_pressed(self):

        link_name, ok = QInputDialog.getText(self, 'Input Link Name for File',
                                        'Enter link name:')

        if ok:
            link_path = QFileDialog.getOpenFileName(self, "Select File")
            user_login = os.getlogin()
            if link_path[0]:
                sql_query = '''INSERT INTO task_links VALUES(NULL,{task_id},"{link_name}","{linked_by}","{link_type}", "{link_path}")'''.format(
                    task_id=self.task.id,
                    link_name=link_name,
                    linked_by=user_login,
                    link_type="file",
                    link_path=link_path[0]
                )
                self.db.cursor.execute(sql_query)
                self.db.connection.commit()
                self._reload()

    def _all_list_link_changed(self):
        self.selected_link_id = self.links_list[self.all_links_list.currentRow()]

    def _open_link(self):
        for link in self.db.cursor.execute('SELECT id, link_type, link_path FROM task_links WHERE id={}'.format(self.selected_link_id)):
            if link[1]=='file':
                if os.path.isfile(link[2]):
                    try:
                        os.startfile(link[2])
                        # subprocess.Popen('explorer /select, "{file_path}"'.format(file_path=link[2]))
                    except Exception as err:
                        print(err)
                else:
                    button_reply = QMessageBox.question(self, 'Link error', 'The file is not exist or connection broken. \nDelete link?',QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if button_reply == QMessageBox.Yes:
                        self.db.cursor.execute('DELETE FROM task_links WHERE id={link_id}'.format(link_id=self.selected_link_id))
                        self.db.connection.commit()
                        self._reload()
                    else:
                        pass

            elif link[1]=='dir':
                if os.path.isdir(link[2]):
                    try:
                        subprocess.Popen(r'explorer "{dir_path}"'.format(dir_path=Path(link[2])))
                        # subprocess.Popen('explorer /select,  "{dir_path}"'.format(dir_path=link[2]))
                    except Exception as err:
                        print(err)
                else:
                    button_reply = QMessageBox.question(self, 'Link error', 'The directory is not exist or connection broken. \nDelete link?',QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if button_reply == QMessageBox.Yes:
                        self.db.cursor.execute('DELETE FROM task_links WHERE id={link_id}'.format(link_id=self.selected_link_id))
                        self.db.connection.commit()
                        self._reload()
                    else:
                        pass

    def _link_directory_button_pressed(self):
        link_name, ok = QInputDialog.getText(self, 'Input Link Name for Directory', 'Enter link name:')

        if ok:
            link_path = QFileDialog.getExistingDirectory(self, "Select Directory")
            user_login = os.getlogin()
            if link_path:
                try:
                    sql_query = '''INSERT INTO 
                                        task_links 
                                    VALUES(NULL,{task_id},"{link_name}","{linked_by}","{link_type}", "{link_path}")'''.format(
                        task_id=self.task.id,
                        link_name=link_name,
                        linked_by=user_login,
                        link_type="dir",
                        link_path=link_path
                    )
                    self.db.cursor.execute(sql_query)
                    self.db.connection.commit()
                    self._reload()
                except Exception as err:
                    print (err)


class Transaction_info_widget(QWidget):
    def __init__(self, transaction, parent=None):
        QWidget.__init__(self, parent=parent)
        self.transaction = transaction

        self._initUI()
        self._connect_signals()

    def _connect_signals(self):
        self.transaction.signal_id_changed.connect(self._reload)

    def _initUI(self):
        self.setMinimumSize(280, 430)
        # self.setMaximumSize(320, 430)
        groupbox = QGroupBox("Transaction info")

        sublayout = QGridLayout()

        self.transaction_info_text_browser = QTextBrowser()
        self.transaction_info_text_browser.setAcceptRichText(True)
        self.transaction_info_text_browser.setOpenExternalLinks(True)
        self.transaction_info_text_browser.setReadOnly(True)

        sublayout.addWidget(self.transaction_info_text_browser, 0, 0)

        groupbox.setLayout(sublayout)

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(groupbox)

        self.setLayout(layout)

    def _reload(self):
        self.transaction_info_text_browser.clear()
        if not self.transaction.loaded_basic:
            self.transaction.load_data_basic()

        html_label_style = '" margin-top:2px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"'
        html_text_style = '" margin-top:0px; margin-bottom:0px; margin-left:10px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"'

        html_header = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
                                <html><head><meta name="qrichtext" content="1" /><style type="text/css">
                                p, li { white-space: pre-wrap; }
                                </style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">'''
        html_footer = '</body></html>'

        html_body = '<p style={style}>{label}:</p>'.format(style=html_label_style, label="Customer")
        html_body += '<p style={style}><span style=" font-size:10pt; font-weight:600;">{text}</span></p>'.format(
            style=html_text_style, text=self.transaction.customer.name)
        html_body += '<p style={style}>{label}:</p>'.format(style=html_label_style, label="Product")
        html_body += '<p style={style}><span style=" font-size:10pt; font-weight:600;">{text}</span></p>'.format(
            style=html_text_style, text=self.transaction.product.product)
        html_body += '<p style={style}>{label}:</p>'.format(style=html_label_style, label="Type")
        html_body += '<p style={style}><span style=" font-size:10pt; font-weight:600;">{text}</span></p>'.format(
            style=html_text_style, text=self.transaction.transaction_type.type)
        html_body += '<p style={style}>{label}:</p>'.format(style=html_label_style, label="Transaction name")
        html_body += '<p style={style}><span style=" font-size:10pt; font-weight:600;">{text}</span></p>'.format(
            style=html_text_style, text=self.transaction.name)
        html_body += '<p style={style}>{label}:</p>'.format(style=html_label_style, label="Transaction responsible")
        html_body += '<p style={style}><span style=" font-size:10pt; font-weight:600;">{text}</span></p>'.format(
            style=html_text_style, text=self.transaction.responsible.full_name)
        html_body += '<p style={style}>{label}:</p>'.format(style=html_label_style, label="Transaction Charge Code")
        html_body += '<p style={style}><span style=" font-size:10pt; font-weight:600;">{text}</span></p>'.format(
            style=html_text_style, text=self.transaction.charge_code)
        html_body += '<p style={style}>{label}:</p>'.format(style=html_label_style, label="Planned start\t\tStarted")
        html_body += '<p style={style}><span style=" font-size:10pt; font-weight:600;">{text}</span></p>'.format(
            style=html_text_style, text=str(self.transaction.planned_start) + "\t\t" + str(self.transaction.true_start))
        html_body += '<p style={style}>{label}:</p>'.format(style=html_label_style, label="Planned end\t\tEnded")
        html_body += '<p style={style}><span style=" font-size:10pt; font-weight:600;">{text}</span></p>'.format(
            style=html_text_style, text=str(self.transaction.planned_end) +"\t\t" + str(self.transaction.true_end))

        if self.transaction.admins:
            html_body += '<p style={style}>{label}:</p>'.format(style=html_label_style, label="Transaction administrators")
            for admin_login in self.transaction.admins:
                admin = Employee()
                admin.set_login(admin_login)
                html_body += '<p style={style}><span style=" font-size:10pt; font-weight:600;">{text}</span></p>'.format(
                    style=html_text_style, text=admin.full_name)

        if self.transaction.deliverable:
            html_body += '<p style={style}>{label}:</p>'.format(style=html_label_style, label="Planned delivery\t\tDelivered")
            html_body += '<p style={style}><span style=" font-size:10pt; font-weight:600;">{text}</span></p>'.format(
                style=html_text_style, text=str(self.transaction.planned_delivery) + "\t\t" + str(self.transaction.true_delivery))

        self.transaction_info_text_browser.append(html_header + html_body + html_footer)


class Task_Info_Widget(QWidget):
    def __init__(self, task, parent=None):
        QWidget.__init__(self, parent=parent)

        self.task = task

        self._initUI()
        self._connect_signals()

    def _connect_signals(self):
        self.task.signal_id_changed.connect(self._reload)

    def _initUI(self):
        self.setMinimumSize(280, 430)
        # self.setMaximumSize(320, 430)

        groupbox = QGroupBox("Task info")
        sublayout = QGridLayout()

        self.task_info_textbrowser = QTextBrowser()
        self.task_info_textbrowser.setAcceptRichText(True)
        self.task_info_textbrowser.setOpenExternalLinks(True)
        self.task_info_textbrowser.setReadOnly(True)

        sublayout.addWidget(self.task_info_textbrowser, 0, 0)

        groupbox.setLayout(sublayout)

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(groupbox)

        self.setLayout(layout)

    def _reload(self):
        self.task_info_textbrowser.clear()
        if not self.task.loaded_basic:
            self.task.load_data_basic()

        html_label_style = '" margin-top:2px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"'
        html_text_style = '" margin-top:0px; margin-bottom:0px; margin-left:10px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"'

        html_header = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
                        <html><head><meta name="qrichtext" content="1" /><style type="text/css">
                        p, li { white-space: pre-wrap; }
                        </style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">'''
        html_footer = '</body></html>'

        html_body = '<p style={style}>{label}:</p>'.format(style=html_label_style, label="Task responsible")
        html_body += '<p style={style}><span style=" font-size:10pt; font-weight:600;">{text}</span></p>'.format(style=html_text_style, text=self.task.responsible.full_name)
        html_body += '<p style={style}>{label}:</p>'.format(style=html_label_style, label="Task creator")
        html_body += '<p style={style}><span style=" font-size:10pt; font-weight:600;">{text}</span></p>'.format(style=html_text_style, text=self.task.creator.full_name)
        html_body += '<p style={style}>{label}:</p>'.format(style=html_label_style, label="Discipline")
        html_body += '<p style={style}><span style=" font-size:10pt; font-weight:600;">{text}</span></p>'.format(style=html_text_style, text=self.task.discipline.name)
        html_body += '<p style={style}>{label}:</p>'.format(style=html_label_style, label="Activity")
        html_body += '<p style={style}><span style=" font-size:10pt; font-weight:600;">{text}</span></p>'.format(style=html_text_style, text=self.task.activity.type)
        html_body += '<p style={style}>{label}:</p>'.format(style=html_label_style, label="Checker required")
        if self.task.checker_required:
            checker_text = "Yes"
        else:
            checker_text = "No"
        html_body += '<p style={style}><span style=" font-size:10pt; font-weight:600;">{text}</span></p>'.format(
            style=html_text_style, text=checker_text)
        html_body += '<p style={style}>{label}:</p>'.format(style=html_label_style, label="Planned start\t\tStarted")
        html_body += '<p style={style}><span style=" font-size:10pt; font-weight:600;">{text}</span></p>'.format(style=html_text_style, text=str(self.task.planned_start) + "\t\t" + str(self.task.true_start))
        html_body += '<p style={style}>{label}:</p>'.format(style=html_label_style, label="Planned end\t\tEnded")
        html_body += '<p style={style}><span style=" font-size:10pt; font-weight:600;">{text}</span></p>'.format(style=html_text_style, text=str(self.task.planned_end) + "\t\t" + str(self.task.true_end))

        if self.task.deliverable:
            html_body += '<p style={style}>{label}:</p>'.format(style=html_label_style, label="Plenned delivery\t\tDelivered")
            html_body += '<p style={style}><span style=" font-size:10pt; font-weight:600;">{text}</span></p>'.format(style=html_text_style, text=str(self.task.planned_delivery)+ "\t\t" + str(self.task.true_delivery))

        self.task_info_textbrowser.append(html_header + html_body + html_footer)


class Daily_Workload_Printer_Widget(QWidget):
    def __init__(self, date_to_print=None, workload=0):
        super().__init__()
        self.initUI()
        self.value = workload
        self._date = date_to_print

    def initUI(self):
        self.setMinimumSize(40, 70)
        # self.setMaximumWidth(40)
        # self.setMaximumSize(40, 300)

    def setValue(self, value):
        self.value = value

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        max_value = 200
        over_value = 250

        size = self.size()
        width = size.width()
        height = size.height()

        post_height = int(((height / over_value) * self.value))
        post_100 = int(((height / over_value) * 100))
        post_max_height = int(((height / over_value) * max_value))

        white = QColor(255, 255, 255)
        black = QColor(0, 0, 0)
        green = QColor(0, 255, 0)
        red = QColor(255, 0, 0)
        gray = QColor(200, 200, 200)

        font = QFont('Serif', 8, QFont.Light)
        pen_outlayer = QPen(black, 1, Qt.SolidLine)

        qp.setFont(font)

        qp.setPen(white)
        if self.value <= 100:
            qp.setBrush(green)
        else:
            qp.setBrush(red)

        if self._date.strftime("%a") != "Sat" and self._date.strftime("%a") != "Sun":
            qp.drawRect(0, height - 28, width, -post_height)
            qp.setPen(pen_outlayer)
            qp.setBrush(Qt.NoBrush)
            qp.drawRect(0, height - 28, width - 1, -post_height + 1)

            qp.drawText(width / 2 - 14, height - 2, self._date.strftime("%d-%b"))  # DONE
            font.setBold(True)
            qp.setFont(font)
            if self.value < 100:
                qp.drawText(width/2 - 12, height - 15, str(int(self.value)) + '%')
            else:
                qp.drawText(width /2 - 14, height - 15, str(int(self.value)) + '%')
        else:
            qp.setBrush(gray)
            qp.setBrush(Qt.Dense6Pattern)
            qp.drawRect(0, height - 28, width, -post_100)
            qp.setPen(pen_outlayer)
            qp.setBrush(Qt.NoBrush)
            qp.drawRect(0, height - 28, width - 1, -post_100 + 1)
            qp.drawText(width / 2 - 12, height - 2, self._date.strftime("%d-%b"))
            font.setBold(True)
            qp.setFont(font)
            qp.setPen(red)
            qp.drawText(width / 2 - 12, height - 15, self._date.strftime("%a"))


class Workload_Widget(QWidget, DateManager):

    def __init__(self, employee, parent=None, start_date=None, end_date=None):
        QWidget.__init__(self, parent=parent)
        DateManager.__init__(self)
        self.start_date = start_date
        self.end_date = end_date
        self.employee = employee
        self._initUI()
        self._make_signals()

    def _make_signals(self):
        self.employee.signal_login_changed.connect(self._reload)

    def set_start_date(self, date_str):
        self.start_date = date_str
        self._reload()

    def set_end_date(self, date_str):
        self.end_date = date_str
        self._reload()

    def _reload(self):
        self.clearLayout()
        if self.start_date and self.end_date and self.employee.login:
            self.employee.load_workload()
            for single_date in self.daterange(self.start_date, self.end_date):
                wl = 0
                if single_date in self.employee.workload:
                    wl = self.employee.workload[single_date]

                dw = Daily_Workload_Printer_Widget(single_date, wl)
                self.layout.addWidget(dw)

    def _initUI(self):

        #   Container Widget
        widget = QWidget()
        #   Layout of Container Widget
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(self.layout)

        #   Scroll Area Properties
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(90)
        scroll.setWidget(widget)

        #   Scroll Area Layer add
        scroll_layout = QVBoxLayout(self)
        scroll_layout.addWidget(scroll)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(scroll_layout)

        self._reload()

    def clearLayout(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()


class TimelinePrinter(QWidget, DateManager):

    def __init__(self, item, widget_start_date=None, widget_end_date=None, show_date=False):
        QWidget.__init__(self)
        DateManager.__init__(self)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.item = item
        self.ready_to_plot = False
        self.show_date = show_date
        # self.set_boundary()
        self.initUI()

    def initUI(self):
        self.setMinimumSize(400, 50)
        self.setMaximumHeight(50)

    def set_boundary(self):

        if self.item.planned_start and self.item.planned_end:
            # self.widget_start_date = self.item.planned_start
            # self.widget_end_date = self.item.planned_end
            self.ready_to_plot = True

            if not self.item.true_end:
                self.item.true_end = datetime.now().date()

            if not self.item.true_delivery:
                self.item.true_delivery = datetime.now().date()

            if self.item.deliverable and self.item.true_delivery is None:
                self.item.true_delivery = datetime.now().date()

            # if self.item.true_start:
            #     if self.item.planned_start > self.item.true_start:
            #         self.widget_start_date = self.item.true_start


            # if self.item.deliverable:
            #     if self.item.planned_delivery >= self.item.true_delivery:
            #         self.widget_end_date = self.item.planned_delivery
            #     else:
            #         self.widget_end_date = self.item.true_delivery
            # else:
            #     if self.item.planned_end < self.item.true_end:
            #         self.widget_end_date = self.item.true_end

    def set_widget_start_date(self, date_str):
        self.widget_start_date = self.convert_to_date_class(date_str)
        self.update_widget()

    def set_widget_end_date(self, date_str):
        self.widget_end_date = self.convert_to_date_class(date_str)
        self.update_widget()

    def update_widget(self):
        self.set_boundary()
        self.repaint()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        if self.ready_to_plot:
            self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        size = self.size()
        width = size.width()
        height = size.height()
        title_height = 10
        rect_height = 20

        widget_days = int((self.widget_end_date - self.widget_start_date).days)
        day_width = int((width / widget_days))

        black = QColor(0, 0, 0)
        red = QColor(255, 0, 0)
        green_light = QColor(181, 230, 29)
        blue_light = QColor(153, 217, 234)
        purple_light = QColor(187, 104, 187)

        font = QFont('Serif', 7, QFont.Light)
        qp.setFont(font)

        label_planned_start = self.item.planned_start.strftime('%x')
        x_point_planned_start = int((self.item.planned_start - self.widget_start_date).days) * day_width
        y_point_planned_start = title_height + rect_height


        if self.item.deliverable:
            qp.setBrush(purple_light)

            rect_width_planned_start = int((self.item.planned_delivery - self.item.planned_start).days) * day_width
            if self.item.true_start:
                true_duration = int((self.item.true_delivery - self.item.true_start).days) * day_width
            lateness = int((self.item.true_delivery - self.item.planned_delivery).days) * day_width

            label_planned_end = self.item.planned_delivery.strftime('%x')
            label_true_end = self.item.true_delivery.strftime('%x')
        else:
            qp.setBrush(blue_light)

            rect_width_planned_start = int((self.item.planned_end - self.item.planned_start).days) * day_width
            if self.item.true_start:
                true_duration = int((self.item.true_end - self.item.true_start).days) * day_width
            lateness = int((self.item.true_end - self.item.planned_end).days) * day_width

            label_planned_end = self.item.planned_end.strftime('%x')
            label_true_end = self.item.true_end.strftime('%x')

        #planned rectangle
        qp.drawRect(x_point_planned_start, y_point_planned_start, rect_width_planned_start-1, -rect_height)

        # true_rectangle
        if self.item.true_start:
            x_point_true_start = int((self.item.true_start - self.widget_start_date).days) * day_width
            y_point_true_start = title_height + 2*rect_height
            label_true_start = self.item.true_start.strftime('%x')
            qp.setBrush(green_light)
            if self.item.planned_end >= self.item.true_end:
                qp.drawRect(x_point_true_start, height-1, true_duration-1, -rect_height+1)
            else:
                if self.item.true_start >= self.item.planned_end:
                    qp.setBrush(red)
                    qp.drawRect(x_point_true_start, height - 1, true_duration - 1, -height / 2 + 1)
                else:
                    qp.drawRect(x_point_true_start, y_point_true_start-1, true_duration-1, -rect_height)
                    qp.setBrush(red)
                    qp.setPen(red)
                    qp.drawRect(x_point_planned_start + rect_width_planned_start, y_point_true_start-2, lateness-2, -rect_height)
        else:
            qp.drawText(x_point_planned_start, height-1, "NOT STARTED YET")

        if self.show_date:
            text_offset = 2
            qp.setPen(black)
            #planned start
            qp.drawText(x_point_planned_start + text_offset, font.pointSize() + text_offset+title_height, label_planned_start)

            #planned end
            if rect_width_planned_start > 38:
                qp.drawText(x_point_planned_start + rect_width_planned_start - 38, - font.pointSize() + text_offset+3 + title_height + rect_height, label_planned_end)
            else:
                qp.drawText(x_point_planned_start + text_offset, - font.pointSize() + text_offset+3 + title_height + rect_height, label_planned_end)

            if self.item.true_start:
                #true start
                qp.drawText(x_point_true_start + text_offset, font.pointSize() + text_offset+title_height+rect_height, label_true_start)

                #true_end
                if true_duration > 38:
                    qp.drawText(x_point_true_start + true_duration - 38, height - text_offset, label_true_end)
                else:
                    qp.drawText(x_point_true_start + text_offset, height - text_offset, label_true_end)

        font = QFont('Serif', 8, QFont.Bold)
        qp.setFont(font)
        qp.drawText(x_point_planned_start, 8, self.item.name)


class BlankActionWidger(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.logger = logging.getLogger(self.__class__.__name__)
        try:
            self.ui = uic.loadUi(r'src\ui\blank_action_widget.ui', self)
        except Exception:
            self.logger.exception(f'Error while trying to find and load ui file')
            Terminate_Widget(20)


class BlankInfoWidger(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.logger = logging.getLogger(self.__class__.__name__)
        try:
            self.ui = uic.loadUi(r'src\ui\blank_info_widget.ui', self)
        except Exception:
            self.logger.exception(f'Error while trying to find and load ui file')
            Terminate_Widget(20)


class TaskEditorWidget(QWidget, DateManager):
    signal_widget_active = pyqtSignal(bool)
    signal_refresh_panel = pyqtSignal(bool)

    def __init__(self, task, user):
        QWidget.__init__(self)
        DateManager.__init__(self)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.me = user
        self.task = Task(db=self.me.db)
        self.reference_task = None

        self.customer = Customer(db=self.me.db)
        self.transaction = Transaction(db=self.me.db)
        self.discipline = Discipline(db=self.me.db)
        self.activity = Activity(db=self.me.db)
        self.responsible = Employee(db=self.me.db)

        self.userDateChange = True

        try:
            self.ui = uic.loadUi(r'src\ui\task_editor_widget.ui', self)
        except Exception:
            self.logger.exception(f'Error while trying to find and load ui file')
            Terminate_Widget(20)

        self._setup_ui()
        self._connect_signals()

    def _connect_signals(self):
        self.ui.customer_combox.activated.connect(self._activated_customer_combox)
        self.ui.transaction_combox.activated.connect(self._activated_transaction_combox)
        self.ui.discipline_combox.activated.connect(self._activated_discipline_combox)
        self.ui.activity_type_combox.activated.connect(self._activated_activity_type_combox)
        self.ui.deliverable_yes_radiobutton.clicked.connect(self._activated_deliverable_yes_checkbox)
        self.ui.deliverable_no_radiobutton.clicked.connect(self._activated_deliverable_no_checkbox)
        self.ui.task_name_lineedit.textEdited.connect(self._activated_task_name_lineedit)
        self.ui.responsible_combox.activated.connect(self._activated_responsible_combox)
        self.ui.planned_hours_spinbox.valueChanged.connect(self._activated_planned_hours_spinbox)
        self.ui.avability_spinbox.valueChanged.connect(self._activated_availability_spinbox)
        self.ui.planned_start_dateedit.userDateChanged.connect(self._activated_planned_start_date)
        self.ui.planned_end_dateedit.userDateChanged.connect(self._activated_planned_end_date)
        self.ui.planned_delivery_dateedit.userDateChanged.connect(self._activated_planned_delivery_date)
        self.ui.checking_yes_radiobutton.clicked.connect(self._activated_checking_yes_checkbox)
        self.ui.checking_no_radiobutton.clicked.connect(self._activated_checking_no_checkbox)

        self.ui.cancel_button.clicked.connect(self._activated_cancel_button)
        self.ui.register_button.clicked.connect(self._activated_register_button)
        self.ui.save_button.clicked.connect(self._activated_save_button)
        self.ui.delete_button.clicked.connect(self._activated_delete_button)

    def _setup_ui(self):
        pass

    def _default_ui(self):
        # Cleaning ui
        self.ui.customer_combox.clear()
        self.ui.transaction_combox.clear()
        self.ui.discipline_combox.clear()
        self.ui.activity_type_combox.clear()
        self.ui.group_deliverable.setExclusive(False)
        self.ui.deliverable_no_radiobutton.setChecked(False)
        self.ui.deliverable_yes_radiobutton.setChecked(False)
        self.ui.group_deliverable.setExclusive(True)

        self.ui.group_checking.setExclusive(False)
        self.ui.checking_no_radiobutton.setChecked(False)
        self.ui.checking_yes_radiobutton.setChecked(False)
        self.ui.group_checking.setExclusive(True)
        self.ui.task_name_lineedit.clear()
        self.ui.responsible_combox.clear()

        # Reseting dateedit limits
        self.ui.planned_start_dateedit.clearMinimumDate()
        self.ui.planned_start_dateedit.clearMaximumDate()
        self.ui.planned_end_dateedit.clearMinimumDate()
        self.ui.planned_end_dateedit.clearMaximumDate()
        self.ui.planned_delivery_dateedit.clearMinimumDate()
        self.ui.planned_delivery_dateedit.clearMaximumDate()

        # Hidding buttons
        self.ui.register_button.setVisible(False)
        self.ui.register_button.setEnabled(False)
        self.ui.save_button.setVisible(False)
        self.ui.cancel_button.setVisible(True)
        self.ui.delete_button.setVisible(False)
        self.ui.delete_button.setEnabled(False)
        self.ui.planned_delivery_frame.setVisible(False)

        # Unlockin frames
        self.ui.customer_frame.setEnabled(True)
        self.ui.transaction_frame.setEnabled(True)
        self.ui.deliverable_frame.setEnabled(True)
        self.ui.responsible_frame.setEnabled(True)
        self.ui.workload_frame.setEnabled(True)
        self.ui.checker_frame.setEnabled(True)
        self.ui.planned_date_frame.setEnabled(True)
        self.ui.planned_start_frame.setEnabled(True)
        self.ui.planned_end_frame.setEnabled(True)
        self.ui.planned_delivery_frame.setEnabled(True)

    def create_task(self):
        self.signal_widget_active.emit(True)
        self.task.reset()
        self._default_ui()
        self.ui.planned_start_dateedit.setDate(QDate.currentDate())
        self.ui.planned_end_dateedit.setDate(QDate.currentDate())
        self.ui.planned_delivery_dateedit.setDate(QDate.currentDate())
        self.ui.planned_hours_spinbox.setValue(0)
        self.ui.register_button.setVisible(True)
        self._load_customers_to_combox()
        self._load_responsibles_to_combox()
        self.ui.responsible_combox.setCurrentIndex(
            self.responsible.logins.copy().index(self.me.login))
        self.task.responsible.set_login(self.me.login)
        self.task.creator.set_login(self.me.login)
        self.task.set_planned_start(QDate.currentDate().toPyDate())
        self.task.set_planned_end(QDate.currentDate().toPyDate())

    def edit_task(self, task):
        self.signal_widget_active.emit(True)
        self._default_ui()
        self.task = task
        self.reference_task = copy.copy(task)
        self.task.set_lock()
        self.transaction.set_id(self.task.transaction_id)
        self.transaction.load_data_basic()
        self.customer = self.transaction.customer
        self.activity = self.task.activity
        self.discipline = self.task.discipline
        self.reponsible = self.task.responsible

        # Loading selected customer to combox
        self._load_customers_to_combox()
        self.ui.customer_combox.setCurrentIndex(
            self.customer.ids.copy().index(self.transaction.customer.id))

        # Loading selected transaction to combox
        self._load_transactions_to_combox(show_active_only=False)
        self.ui.transaction_combox.setCurrentIndex(
            self.transaction.ids.copy().index(self.transaction.id))
        self._set_dateedit_limits()

        # Loading selected discipline
        self._load_disciplines_to_combox()
        self.ui.discipline_combox.setCurrentIndex(
            self.discipline.ids.copy().index(self.task.discipline.id))

        # Loading selected activity type
        self._load_activity_types_to_combox()
        self.ui.activity_type_combox.setCurrentIndex(
            self.activity.ids.copy().index(self.task.activity.id))

        # Loading deliverable
        if self.task.deliverable == 1:
            self.ui.deliverable_yes_radiobutton.setChecked(True)
            self.ui.planned_delivery_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.task.planned_delivery))
            self.ui.planned_delivery_frame.setVisible(True)
        else:
            self.ui.deliverable_no_radiobutton.setChecked(True)
            # self.ui.planned_delivery_dateedit.setDate(QDate.currentDate().toPyDate())

        # Loading task name
        self.ui.task_name_lineedit.setText(self.task.name)

        # Loading responsible
        self._load_responsibles_to_combox()
        self.ui.responsible_combox.setCurrentIndex(
            self.responsible.logins.copy().index(self.task.responsible.login))

        # Loading planned hours
        self.ui.planned_hours_spinbox.setValue(self.task.hours_planned)

        # Loading checker required
        if self.task.checker_required == 1:
            self.ui.checking_yes_radiobutton.setChecked(True)
        else:
            self.ui.checking_no_radiobutton.setChecked(True)

        # Loading planned_start and planned_end
        self.ui.planned_start_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.task.planned_start))
        self.ui.planned_end_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.task.planned_end))

        self._access_controller()

    def _access_controller(self):
        # DISSABLING FRAMES
        self.ui.customer_frame.setEnabled(False)
        self.ui.transaction_frame.setEnabled(False)
        if self.transaction.deliverable == 1:
            self.ui.deliverable_frame.setEnabled(False)

        if self.me.access_id >= 4 and self.transaction.responsible.login == self.me.login or self.me.login in self.transaction.admins:
            self.ui.customer_frame.setEnabled(True)
            self.ui.transaction_frame.setEnabled(True)
            self.ui.deliverable_frame.setEnabled(True)


        self.ui.responsible_frame.setEnabled(False)
        if self.transaction.responsible.login == self.me.login or self.me.login in self.transaction.admins:
            self.ui.responsible_frame.setEnabled(True)

        self.ui.workload_frame.setEnabled(False)
        if self.transaction.responsible.login == self.me.login or self.me.login in self.transaction.admins:
            self.ui.workload_frame.setEnabled(True)

        self.ui.checker_frame.setEnabled(False)
        if self.transaction.responsible.login == self.me.login or self.me.login in self.transaction.admins:
            self.ui.checker_frame.setEnabled(True)
            # if self.task.status < status.code["READY TO CHECK"]:
            #     self.ui.checker_frame.setEnabled(True)

        self.ui.planned_start_frame.setEnabled(False)
        if self.task.status < status.code["ONGOING"]:
            self.ui.planned_start_frame.setEnabled(True)

        self.ui.planned_end_frame.setEnabled(False)
        self.ui.workload_frame.setEnabled(False)
        if self.task.status < status.code["READY TO CHECK"]:
            self.ui.planned_end_frame.setEnabled(True)
            self.ui.workload_frame.setEnabled(True)

        # if self.task.status > status.code["ONGOING"]:
        #     self.ui.planned_date_frame.setEnabled(False)
        #     if self.me.access_id >= 8:
        #         self.ui.planned_date_frame.setEnabled(True)
        #     if self.transaction.responsible.login == self.me.login:
        #         if self.task.responsible.login != self.me.login:
        #             self.ui.planned_date_frame.setEnabled(True)

        self.ui.register_button.setVisible(False)
        self.ui.save_button.setVisible(True)
        self.ui.delete_button.setVisible(True)

        self._delete_button_controller()

    def _load_customers_to_combox(self):
        try:
            self.customer.load_names()
            self.ui.customer_combox.clear()
            for element in self.customer.names:
                self.ui.customer_combox.addItem(element)
        except Exception:
            self.logger.exception(f'ERROR')
            Terminate_Widget(20)

    def _load_transactions_to_combox(self, show_active_only=True):
        try:
            self.transaction.customer.id = self.customer.id
            self.transaction.load_names_by_customer(show_active_only=show_active_only)
            self.ui.transaction_combox.clear()
            for element in self.transaction.names:
                self.ui.transaction_combox.addItem(element)
        except Exception:
            self.logger.exception(f'ERROR')
            Terminate_Widget(20)

    def _load_disciplines_to_combox(self):
        try:
            self.discipline.customer.id = self.customer.id
            self.discipline.load_names()
            self.ui.discipline_combox.clear()
            for element in self.discipline.names:
                self.ui.discipline_combox.addItem(element)
        except Exception:
            self.logger.exception(f'ERROR')
            Terminate_Widget(20)

    def _load_activity_types_to_combox(self):
        try:
            self.ui.activity_type_combox.clear()
            self.activity.customer.id = self.transaction.customer.id
            self.activity.product.id = self.transaction.product.id
            self.activity.transaction_type.id = self.transaction.transaction_type.id
            self.activity.discipline.id = self.discipline.id
            self.activity.load_types()
            self.ui.activity_type_combox.clear()
            for element in self.activity.types:
                self.ui.activity_type_combox.addItem(element)
        except Exception:
            self.logger.exception(f'ERROR')

    def _load_responsibles_to_combox(self):
        try:
            self.responsible.load_full_names()
            self.ui.responsible_combox.clear()
            for element in self.responsible.full_names:
                self.ui.responsible_combox.addItem(element)
        except Exception:
            self.logger.exception(f'ERROR')

    def _activated_customer_combox(self):
        try:
            self.customer.id = self.customer.ids[self.ui.customer_combox.currentIndex()]
            self._load_transactions_to_combox()
            self._load_disciplines_to_combox()
        except Exception:
            self.logger.exception(f'ERROR')
            Terminate_Widget(20)

    def _activated_transaction_combox(self):
        try:
            self.transaction.id = self.transaction.ids[self.ui.transaction_combox.currentIndex()]
            self.transaction.loaded_basic = False
            self.transaction.load_data_basic()
            self.task.set_transaction_id(self.transaction.id)
            self._load_activity_types_to_combox()
            self.ui.activity_type_combox.setCurrentIndex(0)
            self.task.activity.id = None
            self.ui.discipline_combox.setCurrentIndex(0)
            self.task.discipline.id = None
            self._set_dateedit_limits()

            if self.transaction.deliverable == 1:
                self.ui.deliverable_frame.setEnabled(False)
                self.ui.deliverable_no_radiobutton.setChecked(True)
                self._activated_deliverable_no_checkbox()
                self.ui.planned_start_dateedit.setMaximumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_delivery))
                self.ui.planned_end_dateedit.setMaximumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_delivery))
                self.ui.planned_delivery_dateedit.setMaximumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_delivery))

            else:
                self.ui.deliverable_frame.setEnabled(True)
                self.task.deliverable = None
                self.task.set_planned_delivery(None)
                self.ui.group_deliverable.setExclusive(False)
                self.ui.deliverable_no_radiobutton.setChecked(False)
                self.ui.deliverable_yes_radiobutton.setChecked(False)
                self.ui.group_deliverable.setExclusive(True)
                self.ui.planned_start_dateedit.setMaximumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_end))
                self.ui.planned_end_dateedit.setMaximumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_end))
                self.ui.planned_delivery_dateedit.setMaximumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_end))


        except Exception:
            self.logger.exception(f'ERROR')
            Terminate_Widget(20)

    def _activated_discipline_combox(self):
        try:
            self.discipline.id = self.discipline.ids[self.ui.discipline_combox.currentIndex()]
            self.task.discipline.id = self.discipline.id
            self._load_activity_types_to_combox()
            self.task.activity.id = None
            self._register_and_save_buttons_controller()
        except Exception:
            self.logger.exception(f'Error while trying to activate discipline_combox')
            Terminate_Widget(20)

    def _activated_activity_type_combox(self):
        try:
            self.activity.id = self.activity.ids[self.ui.activity_type_combox.currentIndex()]
            self.task.activity.id = self.activity.id
            self._register_and_save_buttons_controller()
        except Exception:
            self.logger.exception(f'Error while trying to activate activity_type_combox')
            Terminate_Widget(20)

    def _activated_deliverable_yes_checkbox(self):
        try:
            self.ui.planned_delivery_frame.setVisible(True)
            self.task.set_deliverable(1)
            self.ui.planned_delivery_dateedit.setDate(QDate.currentDate().toPyDate()) #TODO: check
            delivery = self.ui.planned_delivery_dateedit.date()
            self.task.set_planned_delivery(self.convert_QDate_to_pyDate(delivery))
            self._data_verification()
            self._register_and_save_buttons_controller()
        except Exception:
            self.logger.exception(f'Error while trying to activate deliverable_yes_checkbox')
            Terminate_Widget(20)

    def _activated_deliverable_no_checkbox(self):
        try:
            self.ui.planned_delivery_frame.setVisible(False)
            self.task.set_deliverable(0)
            self.task.set_planned_delivery(None)
            self._register_and_save_buttons_controller()
        except Exception:
            self.logger.exception(f'Error while trying to activate deliverable_no_checkbox')
            Terminate_Widget(20)

    def _activated_checking_yes_checkbox(self):
        try:
            self.task.set_checker_required(1)
            self._register_and_save_buttons_controller()
        except Exception:
            self.logger.exception(f'ERROR')
            Terminate_Widget(20)

    def _activated_checking_no_checkbox(self):
        try:
            self.task.set_checker_required(0)
            self._register_and_save_buttons_controller()
        except Exception:
            self.logger.exception(f'ERROR')
            Terminate_Widget(20)

    def _activated_task_name_lineedit(self, name):
        forbidden_characters = ['/', '\\', '|', '*', '?', '<', '>', '"']
        try:
            if name != "":
                for character in name:
                    if character in forbidden_characters:
                        self.ui.task_name_lineedit.setText(name.replace(f'{character}', ''))
                    else:
                        self.task.set_name(name)
            else:
                self.task.set_name(None)
            self._register_and_save_buttons_controller()
        except Exception:
            self.logger.exception(f'ERROR')
            Terminate_Widget(20)

    def _activated_responsible_combox(self):
        try:
            self.responsible.set_login(self.responsible.logins[self.ui.responsible_combox.currentIndex()])
            self.task.set_responsible_login(self.responsible.login)
            if self.task.responsible.login == None or self.task.responsible.login == self.me.login or self.task.responsible.login[:5] == "STACK":
                self.ui.email_combox.setChecked(False)
            else:
                self.ui.email_combox.setChecked(True)

            self._register_and_save_buttons_controller()
        except Exception:
            self.logger.exception(f'ERROR')
            Terminate_Widget(20)

    def _activated_planned_hours_spinbox(self, hours):
        try:
            self.task.set_hours_planned(hours)
            self._update_avaiability()
            self._register_and_save_buttons_controller()
        except Exception:
                self.logger.exception(f'ERROR')
                Terminate_Widget(20)

    def _activated_availability_spinbox(self, availability):
        try:
            self._update_planned_hours(availability)
        except Exception:
            self.logger.exception(f'ERROR')
            Terminate_Widget(20)

    def _activated_planned_start_date(self, date):
        if self.userDateChange:
            try:
                self.task.set_planned_start(date.toPyDate())
                self._data_verification()
                self._update_avaiability()
                self._register_and_save_buttons_controller()
            except Exception:
                self.logger.exception(f'ERROR')
                Terminate_Widget(20)

    def _activated_planned_end_date(self, date):
        if self.userDateChange:
            try:
                self.task.set_planned_end(date.toPyDate())
                self._data_verification()
                self._update_avaiability()
                self._register_and_save_buttons_controller()
            except Exception:
                    self.logger.exception(f'ERROR')
                    Terminate_Widget(20)

    def _activated_planned_delivery_date(self, date):
        if self.userDateChange:
            try:
                self.task.set_planned_delivery(date.toPyDate())
                self._data_verification()
                self._register_and_save_buttons_controller()
            except Exception:
                self.logger.exception(f'ERROR')
                Terminate_Widget(20)

    def _activated_register_button(self):
        try:
            self.task.register_data()
        except Exception:
            self.logger.exception(f'Error')
            Terminate_Widget(20)
        else:
            if self.ui.email_combox.isChecked():
                sender = EmailSender()
                sender.new_task_notification(self.task)
                sender.show_mail()
                info = QMessageBox.information(self,
                                               'Information',
                                               'E-mail to task responsible person has been prepared. You only need to send it')

            self.ui.hide()
            self.signal_widget_active.emit(False)
            self.signal_refresh_panel.emit(True)

    def _activated_save_button(self):
        try:
            self.task.set_unlock()
            self.task.update_data()
        except Exception:
            self.logger.exception(f'Error while trying to save date in database')
            Terminate_Widget(20)
        else:
            comment = Comment(db=self.task.db)
            comment.set_source("SYSTEM")
            comment.set_task_id(self.task.id)
            comment.set_publisher_login(self.me.login)
            description = f"Task edited by: {comment.publisher.full_name}"
            any_change = False

            if self.task.discipline.id != self.reference_task.discipline.id:
                self.task.discipline.load_data()
                description += f"\ndiscipline -> was {self.reference_task.discipline.name} is {self.task.discipline.name}"
                any_change = True

            if self.task.activity.id != self.reference_task.activity.id:
                self.task.activity.load_data()
                description += f"\nactivity -> was {self.reference_task.activity.type} is {self.task.activity.type}"
                any_change = True

            if self.task.name != self.reference_task.name:
                description += f"\nname -> was {self.reference_task.name} is {self.task.name}"
                any_change = True

            if self.task.planned_start != self.reference_task.planned_start:
                description += f"\nplanned start -> was {self.reference_task.planned_start} is {self.task.planned_start}"
                any_change = True

            if self.task.planned_end != self.reference_task.planned_end:
                description += f"\nplanned end -> was {self.reference_task.planned_end} is {self.task.planned_end}"
                any_change = True

            if self.task.deliverable != self.reference_task.deliverable:
                human = lambda x: "Yes" if x == 1 else "No"
                description += f"\ndeliverable -> was {human(self.reference_task.deliverable)} is {human(self.task.deliverable)}"
                any_change = True

            if self.task.planned_delivery != self.reference_task.planned_delivery:
                description += f"\nplanned delivery -> was {self.reference_task.planned_delivery} is {self.task.planned_delivery}"
                any_change = True

            if self.task.responsible.login != self.reference_task.responsible.login:
                self.task.responsible.load_data()
                description += f"\nresponsible -> was {self.reference_task.responsible.full_name} is {self.task.responsible.full_name}"
                any_change = True

            if self.task.hours_planned != self.reference_task.hours_planned:
                description += f"\nhours planned -> was {self.reference_task.hours_planned} is {self.task.hours_planned}"
                any_change = True

            if self.task.checker_required != self.reference_task.checker_required:
                human = lambda x: "Yes" if x == 1 else "No"
                description += f"\nchecking req. -> was {human(self.reference_task.checker_required)} is {human(self.task.checker_required)}"
                any_change = True
            else:
                oko = 1 #TODO:nie wiem dlaczego ale brak jakiekolwiek operacji po tym ifie wywala błąd.

            if any_change:
                comment.set_description(description)
                comment.register_data()

            self.ui.hide()
            self.signal_widget_active.emit(False)
            self.signal_refresh_panel.emit(True)

    def _activated_delete_button(self):
        buttonReply = QMessageBox.question(self,
                                           'Delete task',
                                           "Are you going to delete task:\n\n{}\n\nPlease confirm".format(self.task.name),
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            try:
                self.task.delete_data()
            except Exception:
                self.logger.exception(f"Error while trying deleting task from database")
            else:
                self.ui.hide()
                self.signal_widget_active.emit(False)
                self.signal_refresh_panel.emit(True)

    def _activated_cancel_button(self):
        try:
            self.task.set_unlock()
        except Exception:
            self.logger.exception(f'Error')
            Terminate_Widget(20)
        else:
            self.ui.hide()
            self.signal_widget_active.emit(False)

    def _set_dateedit_limits(self):
        self.userDateChange = False
        self.ui.planned_start_dateedit.setMinimumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_start))
        self.ui.planned_end_dateedit.setMinimumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_start))
        if self.task.planned_delivery is not None:
            self.ui.planned_delivery_dateedit.setMinimumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_start))

        if self.transaction.deliverable == 1:
            self.ui.planned_start_dateedit.setMaximumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_delivery))
            self.ui.planned_end_dateedit.setMaximumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_delivery))
            self.ui.planned_delivery_dateedit.setMaximumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_delivery))
        else:
            self.ui.planned_start_dateedit.setMaximumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_end))
            self.ui.planned_end_dateedit.setMaximumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_end))
            self.ui.planned_delivery_dateedit.setMaximumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_end))
        self.userDateChange = True

    def _data_verification(self):
        # self.ui.planned_start_label.setStyleSheet('color: black')
        # self.ui.planned_end_label.setStyleSheet('color: black')
        # self.ui.planned_delivery_label.setStyleSheet('color: black')

        if self.task.planned_start is not None and self.task.planned_end is not None:
            if self.task.planned_end < self.task.planned_start:
                # self.ui.planned_end_label.setStyleSheet('color: red')
                pass

        if self.task.planned_end is not None and self.task.planned_delivery is not None:
                if self.task.planned_delivery < self.task.planned_end:
                    # self.ui.planned_delivery_label.setStyleSheet('color: red')
                    pass

    def _register_and_save_buttons_controller(self):
        if self.task.ready_to_save():
            self.ui.register_button.setEnabled(True)
            self.ui.save_button.setEnabled(True)
        else:
            self.ui.register_button.setEnabled(False)
            self.ui.save_button.setEnabled(False)

    def _delete_button_controller(self):
        if self.task.status < status.code["ONGOING"]:
            self.ui.delete_button.setEnabled(True)
        else:
            self.ui.delete_button.setEnabled(False)

    def _update_avaiability(self):
        if self.task.planned_start is not None and self.task.planned_end is not None:
            if self.task.planned_start <= self.task.planned_end:
                daydiff = self.task.planned_end.weekday() - self.task.planned_start.weekday()
                working_task_days = int(
                    ((self.task.planned_end - self.task.planned_start).days - daydiff) / 7 * 5 + min(daydiff, 5) - (
                    max(self.task.planned_end.weekday() - 4, 0) % 5)) + 1
                if working_task_days != 0:
                    self.ui.avability_spinbox.setValue((self.task.hours_planned / 8 / working_task_days) * 100)
            else:
                self.ui.avability_spinbox.setValue(0)
        else:
            self.ui.avability_spinbox.setValue(0)

    def _update_planned_hours(self, avability):
        if self.task.planned_start is not None and self.task.planned_end is not None:
            if self.task.planned_start <= self.task.planned_end:
                daydiff = self.task.planned_end.weekday() - self.task.planned_start.weekday()
                working_task_days = int(
                    ((self.task.planned_end - self.task.planned_start).days - daydiff) / 7 * 5 + min(daydiff, 5) - (
                        max(self.task.planned_end.weekday() - 4, 0) % 5)) + 1
                self.ui.planned_hours_spinbox.setValue((8 * avability / 100) * working_task_days)
            else:
                self.ui.planned_hours_spinbox.setValue(0)
        else:
            self.ui.planned_hours_spinbox.setValue(0)


class TaskStackWidget(QWidget):
    widget_version = 1.0
    release_date = 'Not released officially'

    def __init__(self, task, user):
        QWidget.__init__(self)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.task = task
        self.me = user
        self.task_clicked = False

        try:
            self.ui = uic.loadUi(r'src\ui\task_stack_widget.ui', self)
        except Exception:
            self.logger.exception(f'Error while trying to find and load ui file')
            Terminate_Widget(20)

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self._load_stack_name_to_combox()

    def _reload(self):
        if self.task_clicked:
            self.ui.assign_to_me_button.setEnabled(True)
        else:
            self.ui.assign_to_me_button.setEnabled(False)
            self.ui.task_stack_listwidget.clearSelection()

    def _connect_signals(self):
        self.task.signal_id_changed.connect(self._reload)
        self.ui.task_stack_listwidget.itemClicked.connect(self._activated_task_stack_listwidget)
        self.ui.stack_name_combox.activated.connect(self._activated_stack_name_combox)
        self.ui.assign_to_me_button.clicked.connect(self._activated_assign_to_me)

    def _load_stack_name_to_combox(self):
        try:
            self.me.load_stack_tasks()
            self.ui.stack_name_combox.clear()
            for element in self.me.stack_tasks:
                self.ui.stack_name_combox.addItem(element)
        except Exception:
            self.logger.exception(f'FAILED loading customers to combox.\n')

    def _activated_stack_name_combox(self):
        self.task_stack_listwidget.clear()
        self.task.set_id(None)
        try:
            self.task.load_task_names_by_responsible_login(self.me.stack_logins[self.ui.stack_name_combox.currentIndex()])
        except Exception:
            self.logger.exception(f'Error while trying to load stock task into list')
        else:
            for element in self.task.names:
                self.task_stack_listwidget.addItem(element)

    def _activated_task_stack_listwidget(self):
        self.task_clicked = True
        self.task.set_id_by_index(self.task_stack_listwidget.currentRow())
        self.task_clicked = False

    def _activated_assign_to_me(self):
        self.task.reassign_to_user(user=self.me)
        self._activated_stack_name_combox()


class TaskActionWidget(QWidget, DateManager):
    signal_saved_changes = pyqtSignal(bool)

    def __init__(self, task, user):
        QWidget.__init__(self)
        DateManager.__init__(self)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.task = task
        self.me = user
        self.userDateChange = True
        self.reassignChange = False

        try:
            self.ui = uic.loadUi(r'src\ui\task_action_widget.ui', self)
        except Exception:
            self.logger.exception(f'Error while trying to find and load ui file')
            Terminate_Widget(20)

        self._setup_ui()
        self._connect_signals()
        self._reload()

    def _setup_ui(self):
        self.ui.true_start_dateedit.setVisible(False)
        self.ui.true_end_dateedit.setVisible(False)
        self.ui.true_delivery_dateedit.setVisible(False)

    def _connect_signals(self):
        self.task.signal_id_changed.connect(self._reload)
        self.task.signal_updated.connect(self._reload)

        self.ui.true_start_checkbox.clicked.connect(self._activated_true_start_checkbox)
        self.ui.true_end_checkbox.clicked.connect(self._activated_true_end_checkbox)
        self.ui.true_delivery_checkbox.clicked.connect(self._activated_true_delivery_checkbox)

        self.ui.true_start_dateedit.dateChanged.connect(self._activated_true_start_dateedit)
        self.ui.true_end_dateedit.dateChanged.connect(self._activated_true_end_dateedit)
        self.ui.true_delivery_dateedit.dateChanged.connect(self._activated_true_delivery_dateedit)

        self.ui.checker_selection_combox.activated.connect(self._activated_checker_combox)

        self.ui.save_button.clicked.connect(self._activated_save_button)
        self.ui.assign_button.clicked.connect(self._activated_assign_button)
        self.ui.reassign_button.clicked.connect(self._activated_reassign_button)
        self.ui.close_button.clicked.connect(self._activated_close_button)

        # SIGNALS FOR CONTROLL SAVE BUTTON
        self.task.signal_planned_start_changed.connect(self._show_save_button)
        self.task.signal_planned_end_changed.connect(self._show_save_button)
        self.task.signal_hours_planned_changed.connect(self._show_save_button)
        self.task.signal_true_start_changed.connect(self._show_save_button)
        self.task.signal_true_end_changed.connect(self._show_save_button)
        self.task.signal_true_delivery_changed.connect(self._show_close_button)
        # self.task.signal_true_end_changed.connect(self._show_close_button)

    def _show_save_button(self):
        if self.task.deliverable == 0 and self.task.checker_required == 0 and self.task.true_end is not None:
            self.ui.close_button.setVisible(True)
            self.ui.save_button.setVisible(False)
            return
        self.ui.save_button.setVisible(True)

    def _show_assign_button(self):
        if self.task.check.id is not None:
            self.ui.assign_button.setVisible(True)
        else:
            self.ui.save_button.setVisible(True)

    def _show_close_button(self):
        self.ui.close_button.setVisible(False)
        self.ui.save_button.setVisible(False)
        if self.task.deliverable == 1:
            if self.task.true_delivery is not None:
                self.ui.close_button.setVisible(True)
            else:
                self.ui.save_button.setVisible(True)
        else:
            if self.task.true_end is not None:
                self.ui.close_button.setVisible(True)
            else:
                self.ui.save_button.setVisible(True)

    def _reload(self):
        self.ui.reassign_button.setVisible(False)
        if self.task.id is not None:
            # self.task.load_data_basic()
            if self.task.responsible.login is not None:
                if self.task.responsible.login[:5] == "STACK":
                    return

            self.ui.save_button.setVisible(False)
            self.ui.assign_button.setVisible(False)
            self.ui.close_button.setVisible(False)

            self.ui.true_start_frame.setVisible(False)
            self.ui.true_end_frame.setVisible(False)
            self.ui.true_delivery_frame.setVisible(False)
            self.ui.checker_frame.setVisible(False)

            self.ui.true_start_checkbox.setChecked(False)
            self.ui.true_end_checkbox.setChecked(False)
            self.ui.true_delivery_checkbox.setChecked(False)

            self.ui.true_start_checkbox.setVisible(False)
            self.ui.true_end_checkbox.setVisible(False)
            self.ui.true_delivery_checkbox.setVisible(False)

            self.ui.checker_frame.setEnabled(True)
            self.ui.true_date_frame.setEnabled(True)
            self.ui.true_start_frame.setEnabled(True)
            self.ui.true_end_frame.setEnabled(True)

            if self.task.status == status.code["ASSIGNED"]:
                pass

            if self.task.status == status.code["SCHEDULED"]:
                self.ui.true_start_frame.setVisible(True)
                self.ui.true_start_checkbox.setVisible(True)
                self.ui.true_start_dateedit.setVisible(False)

            if self.task.status == int(status.code["ONGOING"]) or self.task.status == int(status.code["LATE"]):
                #BLOKOWANIE
                self.ui.true_start_frame.setVisible(True)
                self.ui.true_start_frame.setEnabled(False)
                self.ui.true_start_checkbox.setVisible(True)
                self.ui.true_start_checkbox.setChecked(True)
                self.ui.true_start_dateedit.setVisible(True)
                self.ui.true_start_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.task.true_start))

                self.ui.true_end_frame.setVisible(True)
                self.ui.true_end_checkbox.setVisible(True)
                self.ui.true_end_dateedit.setVisible(False)

            if self.task.status == status.code["READY TO CHECK"]:
                # BLOKOWANIE
                self.ui.true_start_frame.setVisible(True)
                self.ui.true_start_frame.setEnabled(False)
                self.ui.true_start_checkbox.setVisible(True)
                self.ui.true_start_checkbox.setChecked(True)
                self.ui.true_start_dateedit.setVisible(True)
                self.ui.true_start_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.task.true_start))

                self.ui.true_end_frame.setVisible(True)
                self.ui.true_end_frame.setEnabled(False)
                self.ui.true_end_checkbox.setVisible(True)
                self.ui.true_end_checkbox.setChecked(True)
                self.ui.true_end_dateedit.setVisible(True)
                self.ui.true_end_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.task.true_end))

                self.ui.checker_frame.setVisible(True)
                self.ui.checker_frame.setVisible(True)
                self._load_checkers_to_combox()

            if self.task.status == status.code["IN CHECK"]:
                # BLOKOWANIE
                self.ui.true_start_frame.setVisible(True)
                self.ui.true_start_frame.setEnabled(False)
                self.ui.true_start_checkbox.setVisible(True)
                self.ui.true_start_checkbox.setChecked(True)
                self.ui.true_start_dateedit.setVisible(True)
                self.ui.true_start_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.task.true_start))

                self.ui.true_end_frame.setVisible(True)
                self.ui.true_end_frame.setEnabled(False)
                self.ui.true_end_checkbox.setVisible(True)
                self.ui.true_end_checkbox.setChecked(True)
                self.ui.true_end_dateedit.setVisible(True)
                self.ui.true_end_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.task.true_end))

                self.ui.reassign_button.setVisible(True)
                self.ui.reassign_button.setEnabled(False)
                if self.task.check.status == status.code["ASSIGNED"]:
                    self.ui.reassign_button.setEnabled(True)

            if self.task.status == status.code["REWORK NEEDED"]:
                # BLOKOWANIE
                self.ui.true_start_frame.setVisible(True)
                self.ui.true_start_frame.setEnabled(False)
                self.ui.true_start_checkbox.setVisible(True)
                self.ui.true_start_checkbox.setChecked(True)
                self.ui.true_start_dateedit.setVisible(True)
                self.ui.true_start_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.task.true_start))

                self.ui.true_end_frame.setVisible(True)
                self.ui.true_end_frame.setEnabled(False)
                self.ui.true_end_checkbox.setVisible(True)
                self.ui.true_end_checkbox.setChecked(True)
                self.ui.true_end_dateedit.setVisible(True)
                self.ui.true_end_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.task.true_end))

            if self.task.status == status.code["IN REWORK"]:
                # BLOKOWANIE
                self.ui.true_start_frame.setVisible(True)
                self.ui.true_start_frame.setEnabled(False)
                self.ui.true_start_checkbox.setVisible(True)
                self.ui.true_start_checkbox.setChecked(True)
                self.ui.true_start_dateedit.setVisible(True)
                self.ui.true_start_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.task.true_start))

                self.ui.true_end_frame.setVisible(True)
                self.ui.true_end_frame.setEnabled(False)
                self.ui.true_end_checkbox.setVisible(True)
                self.ui.true_end_checkbox.setChecked(True)
                self.ui.true_end_dateedit.setVisible(True)
                self.ui.true_end_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.task.true_end))

            if self.task.status == status.code["FINISHED"]:
                self.ui.true_start_frame.setVisible(True)
                self.ui.true_start_frame.setEnabled(False)
                self.ui.true_start_checkbox.setVisible(True)
                self.ui.true_start_checkbox.setChecked(True)
                self.ui.true_start_dateedit.setVisible(True)
                self.ui.true_start_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.task.true_start))

                self.ui.true_end_frame.setVisible(True)
                self.ui.true_end_frame.setEnabled(False)
                self.ui.true_end_checkbox.setVisible(True)
                self.ui.true_end_checkbox.setChecked(True)
                self.ui.true_end_dateedit.setVisible(True)
                self.ui.true_end_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.task.true_end))

            if self.task.status == status.code["READY TO DELIVERY"]:
                # BLOKOWANIE
                self.ui.true_start_frame.setVisible(True)
                self.ui.true_start_frame.setEnabled(False)
                self.ui.true_start_checkbox.setVisible(True)
                self.ui.true_start_checkbox.setChecked(True)
                self.ui.true_start_dateedit.setVisible(True)
                self.ui.true_start_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.task.true_start))

                self.ui.true_end_frame.setVisible(True)
                self.ui.true_end_frame.setEnabled(False)
                self.ui.true_end_checkbox.setVisible(True)
                self.ui.true_end_checkbox.setChecked(True)
                self.ui.true_end_dateedit.setVisible(True)
                self.ui.true_end_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.task.true_end))

                self.ui.true_delivery_frame.setVisible(True)
                self.ui.true_delivery_frame.setEnabled(True)
                self.ui.true_delivery_checkbox.setVisible(True)
                self.ui.true_delivery_checkbox.setEnabled(True)
                self.ui.true_delivery_dateedit.setVisible(False)


            if self.task.status == status.code["DELIVERED"]:
                # BLOKOWANIE
                self.ui.true_start_frame.setVisible(True)
                self.ui.true_start_frame.setEnabled(False)
                self.ui.true_start_checkbox.setVisible(True)
                self.ui.true_start_checkbox.setChecked(True)
                self.ui.true_start_dateedit.setVisible(True)
                self.ui.true_start_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.task.true_start))

                self.ui.true_end_frame.setVisible(True)
                self.ui.true_end_frame.setEnabled(False)
                self.ui.true_end_checkbox.setVisible(True)
                self.ui.true_end_checkbox.setChecked(True)
                self.ui.true_end_dateedit.setVisible(True)
                self.ui.true_end_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.task.true_end))

                self.ui.true_delivery_frame.setVisible(True)
                self.ui.true_delivery_frame.setEnabled(False)
                self.ui.true_delivery_checkbox.setVisible(True)
                self.ui.true_delivery_checkbox.setChecked(True)
                self.ui.true_delivery_dateedit.setVisible(True)
                self.ui.true_delivery_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.task.true_delivery))

    def _load_checkers_to_combox(self):
        try:
            self.me.load_full_names(stack=False)
            self.ui.checker_selection_combox.clear()
            for element in self.me.full_names:
                self.ui.checker_selection_combox.addItem(element)
        except Exception:
            self.logger.exception(f'FAILED load checkers to combox.\n')

    def _activated_true_start_checkbox(self, state):
        if state is True:
            self.ui.true_start_dateedit.setDate(QDate.currentDate())
            self._activated_true_start_dateedit(QDate.currentDate())
            self.ui.true_start_dateedit.setVisible(True)
        else:
            self.ui.true_end_checkbox.setChecked(False)
            self._activated_true_end_checkbox(False)
            self.ui.true_start_dateedit.setVisible(False)
            self.task.set_true_start(None)
        self.ui.save_button.setVisible(True)

    def _activated_true_end_checkbox(self, state):
        self.userDateChange = False
        self.ui.true_end_dateedit.setMinimumDate(self.convert_pyDateTime_to_QDate(self.task.true_start))
        self.userDateChange = True
        if state is True:
            self.ui.true_end_dateedit.setDate(QDate.currentDate())
            self._activated_true_end_dateedit(QDate.currentDate())
            self.ui.true_end_dateedit.setVisible(True)
        else:
            self.ui.true_delivery_checkbox.setChecked(False)
            self._activated_true_delivery_checkbox(False)
            self.ui.true_end_dateedit.setVisible(False)
            self.task.set_true_end(None)

    def _activated_true_delivery_checkbox(self, state):
        self.userDateChange = False
        self.ui.true_delivery_dateedit.setMinimumDate(self.convert_pyDateTime_to_QDate(self.task.true_end))
        self.userDateChange = True
        if state is True:
            self.ui.true_delivery_dateedit.setDate(QDate.currentDate())
            self._activated_true_delivery_dateedit(QDate.currentDate())
            self.ui.true_delivery_dateedit.setVisible(True)
        else:
            self.ui.true_delivery_dateedit.setVisible(False)
            self.task.set_true_delivery(None)

    def _activated_true_start_dateedit(self, date):
        if self.userDateChange:
            self.task.set_true_start(date.toPyDate())

    def _activated_true_end_dateedit(self, date):
        if self.userDateChange:
            self.task.set_true_end(date.toPyDate())

    def _activated_true_delivery_dateedit(self, date):
        if self.userDateChange:
            self.task.set_true_delivery(date.toPyDate())

    def _activated_checker_combox(self):
        self.check = Check(db=self.me.db)
        self.check.creator.set_login(self.me.login)
        # self.task.transaction.customer.set_id_by_index(self.ui.customer_combox.currentIndex())
        self.check.responsible.load_full_names(stack=False)
        self.check.responsible.set_login_by_index(self.ui.checker_selection_combox.currentIndex())
        self.check.set_task_id(self.task.id)
        self.ui.assign_button.setVisible(True)

    def _activated_save_button(self):
        self.task.update_data()
        self.ui.save_button.setVisible(False)

    def _activated_assign_button(self):
        if self.reassignChange:
            self.check.id = self.task.check.id
            self.check.update_data()
        else:
            self.check.register_data()
        self.ui.assign_button.setVisible(False)
        self.ui.checker_frame.setEnabled(False)
        self.reassignChange = False

    def _activated_reassign_button(self):
        self.reassignChange = True
        self.ui.checker_frame.setVisible(True)
        self._load_checkers_to_combox()
        self.ui.checker_selection_combox.setCurrentIndex(
            self.me.logins.copy().index(self.task.check.responsible.login))
        self.ui.reassign_button.setVisible(False)

    def _activated_close_button(self):
        self.task.set_released(1)
        self.task.update_data()
        self.ui.close_button.setVisible(False)


class TaskCheckWidget(QWidget, DateManager):

    def __init__(self, task, check, user):
        QWidget.__init__(self)
        DateManager.__init__(self)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.task = task
        self.check = check
        self.me = user

        try:
            self.ui = uic.loadUi(r'src\ui\task_check_widget.ui', self)
        except Exception:
            self.logger.exception(f'Error while trying to find and load ui file')
            Terminate_Widget(20)

        self._setup_ui()
        self._connect_signals()
        self._reload()

    def _setup_ui(self):
        pass

    def _connect_signals(self):
        self.check.signal_updated.connect(self._reload)
        self.check.signal_id_changed.connect(self._reload)

        self.ui.planned_start_checkbox.clicked.connect(self._activated_planned_start_checkbox)
        self.ui.planned_end_checkbox.clicked.connect(self._activated_planned_end_checkbox)

        self.ui.planned_start_dateedit.dateChanged.connect(self._activated_planned_start_dateedit)
        self.ui.planned_end_dateedit.dateChanged.connect(self._activated_planned_end_dateedit)

        self.ui.planned_hours_spinbox.valueChanged.connect(self._activated_planned_hours_spinbox)
        self.ui.utilized_hours_spinbox.valueChanged.connect(self._activated_utilized_hours_spinbox)

        self.ui.true_start_checkbox.clicked.connect(self._activated_true_start_checkbox)
        self.ui.true_start_dateedit.dateChanged.connect(self._activated_true_start_dateedit)

        self.ui.true_end_checkbox.clicked.connect(self._activated_true_end_checkbox)
        self.ui.true_end_dateedit.dateChanged.connect(self._activated_true_end_dateedit)

        self.ui.rework_yes_checkbox.clicked.connect(self._activated_rework_yes_checkbox)
        self.ui.rework_no_checkbox.clicked.connect(self._activated_rework_no_checkbox)

        self.ui.save_button.clicked.connect(self._activated_save_button)
        self.ui.release_button.clicked.connect(self._activated_release_button)

        #SIGNALS FOR CONTROLL SAVE BUTTON
        self.check.signal_planned_start_changed.connect(self._show_save_button)
        self.check.signal_planned_end_changed.connect(self._show_save_button)
        self.check.signal_hours_planned_changed.connect(self._show_save_button)
        self.check.signal_true_start_changed.connect(self._show_save_button)
        self.check.signal_true_end_changed.connect(self._show_save_button)
        self.check.signal_rework_changed.connect(self._show_release_button)

    def _show_save_button(self):
        self.ui.save_button.setVisible(True)

    def _show_release_button(self):
        self.ui.release_button.setVisible(True)

    def _reload(self):
        self.ui.planned_dates_group_box.setEnabled(True)
        self.ui.planned_start_frame.setVisible(False)
        self.ui.planned_end_frame.setVisible(False)
        self.ui.planned_hours_frame.setVisible(False)

        self.ui.true_date_frame.setEnabled(True)
        self.ui.true_start_frame.setVisible(False)
        self.ui.true_end_frame.setVisible(False)
        self.ui.utilized_hours_frame.setVisible(False)

        self.ui.rework_groupbutton.setExclusive(False)
        self.ui.rework_no_checkbox.setChecked(False)
        self.ui.rework_yes_checkbox.setChecked(False)
        self.ui.rework_groupbutton.setExclusive(True)

        self.ui.rework_selection_frame.setEnabled(True)
        self.ui.rework_selection_frame.setVisible(False)
        self.ui.save_button.setVisible(False)
        self.ui.release_button.setVisible(False)

        if self.check.status >= status.code["ASSIGNED"]:
            self.ui.planned_start_frame.setVisible(True)
            self.ui.planned_end_frame.setVisible(True)
            self.ui.planned_hours_spinbox.setValue(self.check.hours_planned)

            if self.check.planned_start is not None:
                self.ui.planned_start_checkbox.setChecked(True)
                self.ui.planned_start_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.check.planned_start))
                self.ui.planned_start_dateedit.setVisible(True)
            else:
                self.ui.planned_start_checkbox.setChecked(False)
                self.ui.planned_start_dateedit.setVisible(False)

            if self.check.planned_end is not None:
                self.ui.planned_end_checkbox.setChecked(True)
                self.ui.planned_end_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.check.planned_end))
                self.ui.planned_end_dateedit.setVisible(True)
            else:
                self.ui.planned_end_checkbox.setChecked(False)
                self.ui.planned_end_dateedit.setVisible(False)

            if self.check.planned_start is not None and self.check.planned_end is not None:
                self.ui.planned_hours_frame.setVisible(True)

        if self.check.status >= status.code["SCHEDULED"]:
            self.ui.planned_dates_group_box.setEnabled(False)
            self.ui.true_start_frame.setVisible(True)

            if self.check.true_start is not None:
                self.ui.true_start_checkbox.setChecked(True)
                self.ui.true_start_dateedit.setVisible(True)
                self.ui.true_start_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.check.true_start))
            else:
                self.ui.true_start_checkbox.setChecked(False)
                self.ui.true_start_dateedit.setVisible(False)

        if self.check.status >= status.code["ONGOING"]:
            self.ui.true_end_frame.setVisible(True)

            if self.check.true_end is not None:
                self.ui.true_end_checkbox.setChecked(True)
                self.ui.true_end_dateedit.setVisible(True)
                self.ui.true_end_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.check.true_end))
            else:
                self.ui.true_end_checkbox.setChecked(False)
                self.ui.true_end_dateedit.setVisible(False)

        if self.check.status >= status.code["FINISHED"]:
            self.ui.true_date_frame.setEnabled(False)
            self.ui.utilized_hours_frame.setVisible(True)
            self.rework_selection_frame.setVisible(True)

        if self.check.status == status.code["RETURNED"]:
            self.ui.rework_selection_frame.setEnabled(False)
            self.ui.rework_yes_checkbox.setChecked(True)

        if self.check.status == status.code["RELEASED"]:
            self.ui.rework_selection_frame.setEnabled(False)
            self.ui.rework_no_checkbox.setChecked(True)

    def _activated_planned_start_checkbox(self, state):
        if state is True:
            self.ui.planned_start_dateedit.setDate(QDate.currentDate())
            self._activated_planned_start_dateedit(QDate.currentDate())
            self.ui.planned_start_dateedit.setVisible(True)
        else:
            self.ui.planned_end_checkbox.setChecked(False)
            self._activated_planned_end_checkbox(False)
            self.ui.planned_start_dateedit.setVisible(False)
            self.check.set_planned_start(None)

    def _activated_planned_end_checkbox(self, state):
        if state is True:
            self.ui.planned_end_dateedit.setDate(QDate.currentDate())
            self._activated_planned_end_dateedit(QDate.currentDate())
            self.ui.planned_end_dateedit.setVisible(True)
            self.ui.planned_hours_frame.setVisible(True)
        else:
            self.ui.planned_end_checkbox.setChecked(False)
            self.ui.planned_end_dateedit.setVisible(False)
            self.check.set_planned_end(None)
            self.ui.planned_hours_frame.setVisible(False)

    def _activated_true_start_checkbox(self, state):
        if state is True:
            self.ui.true_start_dateedit.setDate(QDate.currentDate())
            self._activated_true_start_dateedit(QDate.currentDate())
            self.ui.true_start_dateedit.setVisible(True)
            self.ui.true_end_checkbox.setVisible(True)
        else:
            self.ui.true_end_checkbox.setChecked(False)
            self._activated_true_end_checkbox(False)
            self.ui.true_start_dateedit.setVisible(False)
            self.check.set_true_start(None)
            self.ui.true_end_checkbox.setVisible(False)

    def _activated_true_end_checkbox(self, state):
        if state is True:
            self.ui.true_end_dateedit.setDate(QDate.currentDate())
            self._activated_true_end_dateedit(QDate.currentDate())
            self.ui.true_end_dateedit.setVisible(True)
            self.ui.utilized_hours_frame.setVisible(True)
        else:
            self.ui.true_end_checkbox.setChecked(False)
            self.ui.true_end_dateedit.setVisible(False)
            self.check.set_true_end(None)
            self.ui.utilized_hours_frame.setVisible(False)

    def _activated_planned_start_dateedit(self, date):
        self.check.set_planned_start(date.toPyDate())

    def _activated_planned_end_dateedit(self, date):
        self.check.set_planned_end(date.toPyDate())

    def _activated_planned_hours_spinbox(self, hours):
        self.check.set_hours_planned(hours)

    def _activated_utilized_hours_spinbox(self, hours):
        self.check.set_hours_utilized(hours)

    def _activated_true_start_dateedit(self, date):
        self.check.set_true_start(date.toPyDate())

    def _activated_true_end_dateedit(self, date):
        self.check.set_true_end(date.toPyDate())

    def _activated_rework_yes_checkbox(self, state):
        if state:
            self.check.set_rework(1)

    def _activated_rework_no_checkbox(self, state):
        if state:
            self.check.set_rework(0)

    def _activated_save_button(self):
        self.check.update_data()
        self.ui.save_button.setVisible(False)

    def _activated_release_button(self):
        if self.check.rework == 1:
            rework = Rework(db=self.me.db)
            rework.set_task_id(self.check.task_id)
            rework.creator.set_login(self.me.login)
            rework.responsible.set_login(self.task.responsible.login)
            rework.register_data()

        if self.check.rework == 0 and self.task.deliverable == 0:
            self.task.set_released(1)
            self.task.update_data()

        self.check.set_released(1)
        self.check.update_data()
        self.ui.release_button.setVisible(False)


class TaskReworkWidget(QWidget, DateManager):
    widget_version = 1.0
    release_date = 'Not released officially'

    def __init__(self, task, rework, user):
        QWidget.__init__(self)
        DateManager.__init__(self)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.task = task
        self.rework = rework
        self.me = user

        try:
            self.ui = uic.loadUi(r'src\ui\task_rework_widget.ui', self)
        except Exception:
            self.logger.exception(f'Error while trying to find and load ui file')
            Terminate_Widget(20)

        self._setup_ui()
        self._connect_signals()
        self._reload()

    def _setup_ui(self):
        pass

    def _connect_signals(self):
        self.rework.signal_updated.connect(self._reload)
        self.rework.signal_id_changed.connect(self._reload)

        self.rework.signal_true_start_changed.connect(self._reload)

        self.ui.planned_start_checkbox.clicked.connect(self._activated_planned_start_checkbox)
        self.ui.planned_end_checkbox.clicked.connect(self._activated_planned_end_checkbox)

        self.ui.planned_start_dateedit.dateChanged.connect(self._activated_planned_start_dateedit)
        self.ui.planned_end_dateedit.dateChanged.connect(self._activated_planned_end_dateedit)

        self.ui.planned_hours_spinbox.valueChanged.connect(self._activated_planned_hours_spinbox)

        self.ui.true_start_checkbox.clicked.connect(self._activated_true_start_checkbox)
        self.ui.true_end_checkbox.clicked.connect(self._activated_true_end_checkbox)

        self.ui.true_start_checkbox.clicked.connect(self._activated_true_start_checkbox)
        self.ui.true_start_dateedit.dateChanged.connect(self._activated_true_start_dateedit)

        self.ui.save_button.clicked.connect(self._activated_save_button)
        self.ui.release_button.clicked.connect(self._activated_release_button)

        #SIGNALS FOR CONTROLL SAVE BUTTON
        self.rework.signal_planned_start_changed.connect(self._show_save_button)
        self.rework.signal_planned_end_changed.connect(self._show_save_button)
        self.rework.signal_hours_planned_changed.connect(self._show_save_button)
        self.rework.signal_true_start_changed.connect(self._show_save_button)
        self.rework.signal_true_end_changed.connect(self._show_release_button)

    def _show_save_button(self):
        self.ui.save_button.setVisible(True)

    def _show_release_button(self):
        self.ui.save_button.setVisible(False)
        self.ui.release_button.setVisible(True)

    def _reload(self):
        self.ui.planned_dates_group_box.setEnabled(True)
        self.ui.planned_start_frame.setVisible(False)
        self.ui.planned_end_frame.setVisible(False)
        self.ui.planned_hours_frame.setVisible(False)

        self.ui.true_date_frame.setEnabled(True)
        self.ui.true_start_frame.setVisible(False)
        self.ui.true_end_frame.setVisible(False)
        self.ui.utilized_hours_frame.setVisible(False)

        self.ui.save_button.setVisible(False)
        self.ui.release_button.setVisible(False)

        if self.rework.status >= status.code["ASSIGNED"]:
            self.ui.planned_start_frame.setVisible(True)
            self.ui.planned_end_frame.setVisible(True)

            if self.rework.planned_start is not None:
                self.ui.planned_start_checkbox.setChecked(True)
                self.ui.planned_start_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.rework.planned_start))
                self.ui.planned_start_dateedit.setVisible(True)
            else:
                self.ui.planned_start_checkbox.setChecked(False)
                self.ui.planned_start_dateedit.setVisible(False)

            if self.rework.planned_end is not None:
                self.ui.planned_end_checkbox.setChecked(True)
                self.ui.planned_end_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.rework.planned_end))
                self.ui.planned_end_dateedit.setVisible(True)
            else:
                self.ui.planned_end_checkbox.setChecked(False)
                self.ui.planned_end_dateedit.setVisible(False)

            if self.rework.planned_start is not None and self.rework.planned_end is not None:
                self.ui.planned_hours_frame.setVisible(True)

        if self.rework.status >= status.code["SCHEDULED"]:
            self.ui.planned_dates_group_box.setEnabled(False)
            self.ui.true_start_frame.setVisible(True)

            if self.rework.true_start is not None:
                self.ui.true_start_checkbox.setChecked(True)
                self.ui.true_start_dateedit.setVisible(True)
                self.ui.true_start_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.rework.true_start))
            else:
                self.ui.true_start_checkbox.setChecked(False)
                self.ui.true_start_dateedit.setVisible(False)

        if self.rework.status >= status.code["ONGOING"]:
            self.ui.true_end_frame.setVisible(True)

            if self.rework.true_end is not None:
                self.ui.true_end_checkbox.setChecked(True)
                self.ui.true_end_dateedit.setVisible(True)
                self.ui.true_end_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.rework.true_end))
            else:
                self.ui.true_end_checkbox.setChecked(False)
                self.ui.true_end_dateedit.setVisible(False)

        if self.rework.status >= status.code["FINISHED"]:
            self.ui.true_date_frame.setEnabled(False)
            self.ui.utilized_hours_frame.setVisible(True)


        if self.rework.status == status.code["RELEASED"]:
            pass

    def _activated_planned_start_checkbox(self, state):
        if state is True:
            self.ui.planned_start_dateedit.setDate(QDate.currentDate())
            self._activated_planned_start_dateedit(QDate.currentDate())
            self.ui.planned_start_dateedit.setVisible(True)
        else:
            self.ui.planned_end_checkbox.setChecked(False)
            self._activated_planned_end_checkbox(False)
            self.ui.planned_start_dateedit.setVisible(False)
            self.rework.set_planned_start(None)

    def _activated_planned_end_checkbox(self, state):
        if state is True:
            self.ui.planned_end_dateedit.setDate(QDate.currentDate())
            self._activated_planned_end_dateedit(QDate.currentDate())
            self.ui.planned_end_dateedit.setVisible(True)
            self.ui.planned_hours_frame.setVisible(True)
        else:
            self.ui.planned_end_checkbox.setChecked(False)
            self.ui.planned_end_dateedit.setVisible(False)
            self.rework.set_planned_end(None)
            self.ui.planned_hours_frame.setVisible(False)

    def _activated_true_start_checkbox(self, state):
        if state is True:
            self.ui.true_start_dateedit.setDate(QDate.currentDate())
            self._activated_true_start_dateedit(QDate.currentDate())
            self.ui.true_start_dateedit.setVisible(True)
            self.ui.true_end_checkbox.setVisible(True)
        else:
            self.ui.true_end_checkbox.setChecked(False)
            self._activated_true_end_checkbox(False)
            self.ui.true_start_dateedit.setVisible(False)
            self.rework.set_true_start(None)
            self.ui.true_end_checkbox.setVisible(False)

    def _activated_true_end_checkbox(self, state):
        if state is True:
            self.ui.true_end_dateedit.setDate(QDate.currentDate())
            self._activated_true_end_dateedit(QDate.currentDate())
            self.ui.true_end_dateedit.setVisible(True)
            self.ui.utilized_hours_frame.setVisible(True)
        else:
            self.ui.true_end_checkbox.setChecked(False)
            self.ui.true_end_dateedit.setVisible(False)
            self.rework.set_true_end(None)
            self.ui.utilized_hours_frame.setVisible(False)

    def _activated_planned_start_dateedit(self, date):
        self.rework.set_planned_start(date.toPyDate())

    def _activated_planned_end_dateedit(self, date):
        self.rework.set_planned_end(date.toPyDate())

    def _activated_planned_hours_spinbox(self, hours):
        self.rework.set_hours_planned(hours)

    def _activated_true_start_dateedit(self, date):
        self.rework.set_true_start(date.toPyDate())

    def _activated_true_end_dateedit(self, date):
        self.rework.set_true_end(date.toPyDate())

    def _activated_rework_yes_checkbox(self, state):
        if state:
            self.rework.set_rework(1)

    def _activated_rework_no_checkbox(self, state):
        if state:
            self.rework.set_rework(0)

    def _activated_save_button(self):
        self.rework.update_data()
        self.ui.save_button.setVisible(False)

    def _activated_release_button(self):
        check = Check(db=self.me.db)
        check.set_task_id(self.rework.task_id)
        check.creator.set_login(self.me.login)

        first_checker_login = self.task.checks[0].responsible.login
        check.responsible.set_login(first_checker_login)
        check.register_data()

        self.rework.set_released(1)
        self.rework.update_data()
        self.ui.release_button.setVisible(False)


class TaskImportWidget(QWidget, DateManager):
    signal_customer_pass = pyqtSignal(dict)
    signal_message = pyqtSignal(str)

    def __init__(self, w_id, user):
        QWidget.__init__(self)
        DateManager.__init__(self)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.me = user
        self.w_id = w_id
        self.task = Task(db=self.me.db)
        self.parameters = {"widget_id": self.w_id}

        self.customer = Customer(db=self.me.db)
        self.transaction = Transaction(db=self.me.db)
        self.discipline = Discipline(db=self.me.db)
        self.activity = Activity(db=self.me.db)
        self.responsible = Employee(db=self.me.db)

        try:
            self.ui = uic.loadUi(r'src\ui\task_import_widget.ui', self)
        except Exception:
            self.logger.exception(f'Error while trying to find and load ui file')
            Terminate_Widget(20)

        self._connect_signals()
        self._setup_ui()

    def _setup_ui(self):
        self._load_customers_to_combox()
        self._load_responsibles_to_combox()
        self.ui.widget_id.setText(str(self.w_id))
        self.ui.planned_start_dateedit.setDate(QDate.currentDate())
        self.ui.planned_end_dateedit.setDate(QDate.currentDate())
        self.ui.planned_delivery_dateedit.setDate(QDate.currentDate())
        self.ui.planned_delivery_dateedit.setEnabled(False)

    def _connect_signals(self):
        self.task.signal_message.connect(self.signal_emiter)
        self.ui.customer_combox.activated.connect(self._activated_customer_combox)
        self.ui.transaction_combox.activated.connect(self._activated_transaction_combox)
        self.ui.discipline_combox.activated.connect(self._activated_discipline_combox)
        self.ui.activity_type_combox.activated.connect(self._activated_activity_type_combox)
        self.ui.task_name_lineedit.textEdited.connect(self._activated_task_name_lineedit)
        self.ui.deliverable_yes_radiobutton.clicked.connect(self._activated_deliverable_yes_checkbox)
        self.ui.deliverable_no_radiobutton.clicked.connect(self._activated_deliverable_no_checkbox)
        self.ui.responsible_combox.activated.connect(self._activated_responsible_combox)
        self.ui.checking_yes_radiobutton.clicked.connect(self._activated_checking_yes_checkbox)
        self.ui.checking_no_radiobutton.clicked.connect(self._activated_checking_no_checkbox)
        self.ui.planned_start_dateedit.userDateChanged.connect(self._activated_planned_start_date)
        self.ui.planned_end_dateedit.userDateChanged.connect(self._activated_planned_end_date)
        self.ui.planned_delivery_dateedit.userDateChanged.connect(self._activated_planned_delivery_date)
        self.ui.planned_hours_spinbox.valueChanged.connect(self._activated_planned_hours_spinbox)

    def load_parameters(self, parameters):
        try:
            if "customer" in parameters.keys():
                findex = self.ui.customer_combox.findText(parameters["customer"])
                if findex > 0:
                    self.ui.customer_combox.setCurrentIndex(findex)
                else:
                    self.ui.customer_combox.setCurrentIndex(0)
                self._activated_customer_combox(signal=False)
            if "transaction" in parameters.keys():
                findex = self.ui.transaction_combox.findText(parameters["transaction"])
                if findex > 0:
                    self.ui.transaction_combox.setCurrentIndex(findex)
                else:
                    self.ui.transaction_combox.setCurrentIndex(0)
                self._activated_transaction_combox(signal=False)
            if "discipline" in parameters.keys():
                findex = self.ui.discipline_combox.findText(parameters["discipline"])
                if findex > 0:
                    self.ui.discipline_combox.setCurrentIndex(findex)
                else:
                    self.ui.discipline_combox.setCurrentIndex(0)
                self._activated_discipline_combox(signal=False)
            if "activity_type" in parameters.keys():
                findex = self.ui.activity_type_combox.findText(parameters["activity_type"])
                if findex > 0:
                    self.ui.activity_type_combox.setCurrentIndex(findex)
                else:
                    self.ui.activity_type_combox.setCurrentIndex(findex)
                self._activated_activity_type_combox(signal=False)

            if "task_name" in parameters.keys():
                self.ui.task_name_lineedit.setText(parameters["task_name"])
                self._activated_task_name_lineedit(parameters["task_name"])

            if "responsible_name" in parameters.keys():
                findex = self.ui.responsible_combox.findText(parameters["responsible_name"])
                if findex > 0:
                    self.ui.responsible_combox.setCurrentIndex(findex)
                else:
                    self.ui.responsible_combox.setCurrentIndex(0)
                self._activated_responsible_combox(signal=False)
            if "deliverable" in parameters.keys():
                if parameters['deliverable'] is True:
                    self.ui.deliverable_yes_radiobutton.setChecked(True)
                    self._activated_deliverable_yes_checkbox(signal=False)
                else:
                    self.ui.deliverable_no_radiobutton.setChecked(True)
                    self._activated_deliverable_no_checkbox(signal=False)
            if "planned_start" in parameters.keys():
                try:
                    date = self.convert_to_date_class(parameters['planned_start'])
                    self.ui.planned_start_dateedit.setDate(date)
                except Exception:
                    pass
            if "planned_end" in parameters.keys():
                try:
                    date = self.convert_to_date_class(parameters['planned_end'])
                    self.ui.planned_end_dateedit.setDate(date)
                except Exception:
                    pass
            if "planned_delivery" in parameters.keys():
                if self.task.deliverable:
                    try:
                        date = self.convert_to_date_class(parameters['planned_delivery'])
                        self.ui.planned_delivery_dateedit.setDate(date)
                    except Exception:
                        pass

            if "planned_hours" in parameters.keys():
                self.ui.planned_hours_spinbox.setValue(parameters['planned_hours'])
            if "checking_required" in parameters.keys():
                if parameters['checking_required'] is True:
                    self.ui.checking_yes_radiobutton.setChecked(True)
                    self._activated_checking_yes_checkbox(signal=False)
                else:
                    self.ui.checking_no_radiobutton.setChecked(True)
                    self._activated_checking_no_checkbox(signal=False)
        except Exception as err:
            print(err)

    def _load_customers_to_combox(self):
        try:
            self.customer.load_names()
            self.ui.customer_combox.clear()
            for element in self.customer.names:
                self.ui.customer_combox.addItem(element)
        except Exception:
            self.logger.exception(f'ERROR')
            Terminate_Widget(20)

    def _load_transactions_to_combox(self, show_active_only=True):
        try:
            self.transaction.customer.id = self.customer.id
            self.transaction.load_names_by_customer(show_active_only=show_active_only)
            self.ui.transaction_combox.clear()
            for element in self.transaction.names:
                self.ui.transaction_combox.addItem(element)
        except Exception:
            self.logger.exception(f'ERROR')
            Terminate_Widget(20)

    def _load_disciplines_to_combox(self):
        try:
            self.discipline.customer.id = self.customer.id
            self.discipline.load_names()
            self.ui.discipline_combox.clear()
            for element in self.discipline.names:
                self.ui.discipline_combox.addItem(element)
        except Exception:
            self.logger.exception(f'ERROR')
            Terminate_Widget(20)

    def _load_activity_types_to_combox(self):
        try:
            self.ui.activity_type_combox.clear()
            self.activity.customer.id = self.transaction.customer.id
            self.activity.product.id = self.transaction.product.id
            self.activity.transaction_type.id = self.transaction.transaction_type.id
            self.activity.discipline.id = self.discipline.id
            self.activity.load_types()
            self.ui.activity_type_combox.clear()
            for element in self.activity.types:
                self.ui.activity_type_combox.addItem(element)
        except Exception:
            self.logger.exception(f'ERROR')

    def _load_responsibles_to_combox(self):
        try:
            self.responsible.load_full_names()
            self.ui.responsible_combox.clear()
            for element in self.responsible.full_names:
                self.ui.responsible_combox.addItem(element)
        except Exception:
            self.logger.exception(f'ERROR')

    def _activated_customer_combox(self, index=None, signal=True):
        try:
            self.customer.id = self.customer.ids[self.ui.customer_combox.currentIndex()]
            self._load_transactions_to_combox()
            self._load_disciplines_to_combox()
            self._activated_transaction_combox(signal=False)
            self._register_controller()
        except Exception:
            self.logger.exception(f'ERROR')
            Terminate_Widget(20)
        else:
            if signal:
                parameters = {"widget_id": self.w_id,
                              "customer": self.ui.customer_combox.currentText()}
                self.signal_customer_pass.emit(parameters)

    def _activated_transaction_combox(self, index=None, signal=True):
        try:
            self.transaction.id = self.transaction.ids[self.ui.transaction_combox.currentIndex()]
            self.transaction.loaded_basic = False
            self.transaction.load_data_basic()
            self.task.set_transaction_id(self.transaction.id)
            self._load_activity_types_to_combox()
            self.ui.activity_type_combox.setCurrentIndex(0)
            self.task.activity.id = None
            self.ui.discipline_combox.setCurrentIndex(0)
            self.task.discipline.id = None
            self._set_dateedit_limits()
            self._register_controller()

            if self.transaction.deliverable == 1:
                self.ui.deliverable_frame.setEnabled(False)
                self.ui.deliverable_no_radiobutton.setChecked(True)
                self._activated_deliverable_no_checkbox()
                self.ui.planned_start_dateedit.setMaximumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_delivery))
                self.ui.planned_end_dateedit.setMaximumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_delivery))
                self.ui.planned_delivery_dateedit.setMaximumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_delivery))

            else:
                self.ui.deliverable_frame.setEnabled(True)
                self.task.deliverable = None
                self.task.set_planned_delivery(None)
                self.ui.group_deliverable.setExclusive(False)
                self.ui.deliverable_no_radiobutton.setChecked(False)
                self.ui.deliverable_yes_radiobutton.setChecked(False)
                self.ui.group_deliverable.setExclusive(True)
                self.ui.planned_start_dateedit.setMaximumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_end))
                self.ui.planned_end_dateedit.setMaximumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_end))
                self.ui.planned_delivery_dateedit.setMaximumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_end))

            if signal:
                parameters = {"widget_id": self.w_id,
                              "customer": self.ui.customer_combox.currentText(),
                              "transaction": self.ui.transaction_combox.currentText()}
                self.signal_customer_pass.emit(parameters)

        except Exception:
            self.logger.exception(f'ERROR')
            Terminate_Widget(20)

    def _activated_discipline_combox(self, index=None, signal=True):
        try:
            self.discipline.id = self.discipline.ids[self.ui.discipline_combox.currentIndex()]
            self.task.discipline.id = self.discipline.id
            self._load_activity_types_to_combox()
            self.task.activity.id = None
            self._register_controller()
        except Exception:
            self.logger.exception(f'Error while trying to activate discipline_combox')
            Terminate_Widget(20)
        else:
            if signal:
                parameters = {"widget_id": self.w_id,
                              "customer": self.ui.customer_combox.currentText(),
                              "transaction": self.ui.transaction_combox.currentText(),
                              "discipline": self.ui.discipline_combox.currentText()}
                self.signal_customer_pass.emit(parameters)

    def _activated_activity_type_combox(self, index=None, signal=True):
        try:
            self.activity.id = self.activity.ids[self.ui.activity_type_combox.currentIndex()]
            self.task.activity.id = self.activity.id
            self._register_controller()
        except Exception:
            self.logger.exception(f'Error while trying to activate activity_type_combox')
            Terminate_Widget(20)
        if signal:
            parameters = {"widget_id": self.w_id,
                          "customer": self.ui.customer_combox.currentText(),
                          "transaction": self.ui.transaction_combox.currentText(),
                          "discipline": self.ui.discipline_combox.currentText(),
                          "activity_type": self.ui.activity_type_combox.currentText()}
            self.signal_customer_pass.emit(parameters)

    def _activated_task_name_lineedit(self, name):
        forbidden_characters = ['/', '\\', '|', '*', '?', '<', '>', '"']
        try:
            if name != "":
                for character in name:
                    if character in forbidden_characters:
                        self.ui.task_name_lineedit.setText(name.replace(f'{character}', ''))
                    else:
                        self.task.set_name(name)
            else:
                self.task.set_name(None)
            self._register_controller()
        except Exception:
            self.logger.exception(f'ERROR')
            Terminate_Widget(20)

    def _activated_deliverable_yes_checkbox(self, state=None, signal=True):
        try:
            # self.ui.planned_delivery_frame.setVisible(True)
            self.ui.planned_delivery_dateedit.setEnabled(True)
            # self.ui.planned_delivery_dateedit.setStyleSheet('color: rgb(0, 0, 0)')
            self.task.set_deliverable(1)
            self.ui.planned_delivery_dateedit.setDate(QDate.currentDate().toPyDate()) #TODO: check
            delivery = self.ui.planned_delivery_dateedit.date()
            self.task.set_planned_delivery(self.convert_QDate_to_pyDate(delivery))
            self._data_verification()
            self._register_controller()
            if signal:
                parameters = {"widget_id": self.w_id,
                              "deliverable": True}
                self.signal_customer_pass.emit(parameters)
        except Exception:
            self.logger.exception(f'Error while trying to activate deliverable_yes_checkbox')
            Terminate_Widget(20)

    def _activated_deliverable_no_checkbox(self, state=None, signal = True):
        try:
            # self.ui.planned_delivery_frame.setVisible(False)
            self.ui.planned_delivery_dateedit.setEnabled(False)
            # self.ui.planned_delivery_dateedit.setStyleSheet('color: rgb(240, 240, 240)')
            self.task.set_deliverable(0)
            self.task.set_planned_delivery(None)
            self._register_controller()
            if signal:
                parameters = {"widget_id": self.w_id,
                              "deliverable": False}
                self.signal_customer_pass.emit(parameters)
        except Exception:
            self.logger.exception(f'Error while trying to activate deliverable_no_checkbox')
            Terminate_Widget(20)

    def _activated_responsible_combox(self, index=None, signal=True):
        try:
            self.responsible.set_login(self.responsible.logins[self.ui.responsible_combox.currentIndex()])
            self.task.responsible = self.responsible
            self._register_controller()
        except Exception:
            self.logger.exception(f'ERROR')
            Terminate_Widget(20)
        if signal:
            parameters = {"widget_id": self.w_id,
                          "responsible_name": self.ui.responsible_combox.currentText()}
            self.signal_customer_pass.emit(parameters)

    def _activated_checking_yes_checkbox(self, state=None, signal=True):
        try:
            self.task.set_checker_required(1)
            self._register_controller()
        except Exception:
            self.logger.exception(f'ERROR')
            Terminate_Widget(20)
        if signal:
            parameters = {"widget_id": self.w_id,
                          "checking_required": True}
            self.signal_customer_pass.emit(parameters)

    def _activated_checking_no_checkbox(self, state=None, signal=True):
        try:
            self.task.set_checker_required(0)
            self._register_controller()
        except Exception:
            self.logger.exception(f'ERROR')
            Terminate_Widget(20)
        if state:
            parameters = {"widget_id": self.w_id,
                          "checking_required": False}
            self.signal_customer_pass.emit(parameters)

    def _activated_planned_start_date(self, date, signal=True):
        try:
            self.task.set_planned_start(date.toPyDate())
            self._data_verification()
            self._register_controller()
        except Exception:
            self.logger.exception(f'ERROR')
            Terminate_Widget(20)
        if signal:
            parameters = {"widget_id": self.w_id,
                          "planned_start": date.toPyDate()}
            self.signal_customer_pass.emit(parameters)

    def _activated_planned_end_date(self, date, signal=True):
        try:
            self.task.set_planned_end(date.toPyDate())
            self._data_verification()
            self._register_controller()
        except Exception:
                self.logger.exception(f'ERROR')
                Terminate_Widget(20)
        if signal:
            parameters = {"widget_id": self.w_id,
                          "planned_end": date.toPyDate()}
            self.signal_customer_pass.emit(parameters)

    def _activated_planned_delivery_date(self, date, signal=True):
        try:
            self.task.set_planned_delivery(date.toPyDate())
            self._data_verification()
            self._register_controller()
        except Exception:
            self.logger.exception(f'ERROR')
            Terminate_Widget(20)
        else:
            if signal:
                parameters = {"widget_id": self.w_id,
                              "planned_delivery": date.toPyDate()}
                self.signal_customer_pass.emit(parameters)

    def _activated_planned_hours_spinbox(self, hours, signal=True):
        try:
            self.task.set_hours_planned(hours)
            self._register_controller()
        except Exception:
                self.logger.exception(f'ERROR')
                Terminate_Widget(20)
        else:
            if signal:
                parameters = {"widget_id": self.w_id,
                              "planned_hours": hours}
                self.signal_customer_pass.emit(parameters)

    def _update_planned_hours(self, avability):
        if self.task.planned_start is not None and self.task.planned_end is not None:
            if self.task.planned_start <= self.task.planned_end:
                daydiff = self.task.planned_end.weekday() - self.task.planned_start.weekday()
                working_task_days = int(
                    ((self.task.planned_end - self.task.planned_start).days - daydiff) / 7 * 5 + min(daydiff, 5) - (
                        max(self.task.planned_end.weekday() - 4, 0) % 5)) + 1
                self.ui.planned_hours_spinbox.setValue((8 * avability / 100) * working_task_days)
            else:
                self.ui.planned_hours_spinbox.setValue(0)
        else:
            self.ui.planned_hours_spinbox.setValue(0)

    def _set_dateedit_limits(self):
        self.ui.planned_start_dateedit.setMinimumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_start))
        self.ui.planned_end_dateedit.setMinimumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_start))
        if self.task.planned_delivery is not None:
            self.ui.planned_delivery_dateedit.setMinimumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_start))

        if self.transaction.deliverable == 1:
            self.ui.planned_start_dateedit.setMaximumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_delivery))
            self.ui.planned_end_dateedit.setMaximumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_delivery))
            self.ui.planned_delivery_dateedit.setMaximumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_delivery))
        else:
            self.ui.planned_start_dateedit.setMaximumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_end))
            self.ui.planned_end_dateedit.setMaximumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_end))
            self.ui.planned_delivery_dateedit.setMaximumDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_end))

    def _data_verification(self):
        # self.ui.planned_start_dateedit.setStyleSheet('background-color: rgb(255, 255, 255)')
        # self.ui.planned_start_dateedit.setStyleSheet('color: rgb(0,0,0)')
        # self.ui.planned_end_dateedit.setStyleSheet('background-color: rgb(255, 255, 255)')
        # self.ui.planned_end_dateedit.setStyleSheet('color: rgb(0,0,0)')
        # if self.task.deliverable:
        #     self.ui.planned_delivery_dateedit.setStyleSheet('background-color: rgb(255, 255, 255)')
        #     self.ui.planned_delivery_dateedit.setStyleSheet('color: rgb(0,0,0)')
        # else:
        #     self.ui.planned_delivery_dateedit.setStyleSheet('color: rgb(240, 240, 240)')
        #
        #
        # if self.task.planned_start is not None and self.task.planned_end is not None:
        #     if self.task.planned_end < self.task.planned_start:
        #         self.ui.planned_end_dateedit.setStyleSheet('background-color: rgb(255, 0, 0)')
        #
        # if self.task.planned_end is not None and self.task.planned_delivery is not None:
        #         if self.task.planned_delivery < self.task.planned_end:
        #             self.ui.planned_delivery_dateedit.setStyleSheet('background-color: rgb(255, 0, 0)')
        pass

    def signal_emiter(self, msg):
        self.signal_message.emit(str(self.w_id) + ": " + msg)

    def _register_task(self):
        try:
            self.task.register_data()
        except Exception:
            self.logger.exception(f'Error')
            Terminate_Widget(20)
        else:
            pass

    def _register_controller(self):
        if self.task.ready_to_save():
            self.ui.widget_id.setEnabled(True)
            # self.ui.widget_id.setStyleSheet('background-color: rgb(0, 255, 0)')
        else:
            # self.ui.widget_id.setStyleSheet('background-color: rgb(255, 0, 0)')
            self.ui.widget_id.setEnabled(False)
            self.ui.widget_id.setChecked(False)


class TransactionActionWidget(QWidget, DateManager):
    def __init__(self, transaction, user):
        QWidget.__init__(self)
        DateManager.__init__(self)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.transaction = transaction
        self.me = user

        try:
            self.ui = uic.loadUi(r'src\ui\transaction_action_widget.ui', self)
        except Exception:
            self.logger.exception(f'Error while trying to find and load ui file')
            Terminate_Widget(20)

        self._setup_ui()
        self._connect_signals()
        self._reload()

    def _setup_ui(self):
        self.ui.true_start_dateedit.setVisible(False)
        self.ui.true_end_dateedit.setVisible(False)
        self.ui.true_delivery_dateedit.setVisible(False)

    def _connect_signals(self):
        self.transaction.signal_id_changed.connect(self._reload)
        self.transaction.signal_updated.connect(self._reload)

        self.ui.true_start_checkbox.clicked.connect(self._activated_true_start_checkbox)
        self.ui.true_end_checkbox.clicked.connect(self._activated_true_end_checkbox)
        self.ui.true_delivery_checkbox.clicked.connect(self._activated_true_delivery_checkbox)

        self.ui.true_start_dateedit.dateChanged.connect(self._activated_true_start_dateedit)
        self.ui.true_end_dateedit.dateChanged.connect(self._activated_true_end_dateedit)
        self.ui.true_delivery_dateedit.dateChanged.connect(self._activated_true_delivery_dateedit)

        # self.ui.checker_selection_combox.activated.connect(self._activated_checker_combox)

        self.ui.save_button.clicked.connect(self._activated_save_button)
        self.ui.delivered_button.clicked.connect(self._activated_delivered_button)
        # self.ui.assign_button.clicked.connect(self._activated_assign_button)

        # SIGNALS FOR CONTROLL SAVE BUTTON
        # self.transaction.signal_planned_start_changed.connect(self._show_save_button)
        # self.transaction.signal_planned_end_changed.connect(self._show_save_button)
        self.transaction.signal_true_start_changed.connect(self._show_save_button)
        self.transaction.signal_true_end_changed.connect(self._show_save_button)
        self.transaction.signal_true_delivery_changed.connect(self._show_delivered_button)

    def _show_save_button(self):
        self.ui.save_button.setVisible(True)

    def _show_delivered_button(self):
        self.ui.delivered_button.setVisible(False)
        if self.transaction.true_delivery is not None:
            self.ui.delivered_button.setVisible(True)

    def _reload(self):
        self.ui.save_button.setVisible(False)
        self.ui.delivered_button.setVisible(False)

        self.ui.true_start_frame.setVisible(False)
        self.ui.true_end_frame.setVisible(False)
        self.ui.true_delivery_frame.setVisible(False)

        self.ui.true_start_checkbox.setChecked(False)
        self.ui.true_end_checkbox.setChecked(False)
        self.ui.true_delivery_checkbox.setChecked(False)

        self.ui.true_start_checkbox.setVisible(False)
        self.ui.true_end_checkbox.setVisible(False)
        self.ui.true_delivery_checkbox.setVisible(False)

        self.ui.true_date_frame.setEnabled(True)
        self.ui.true_start_frame.setEnabled(True)
        self.ui.true_end_frame.setEnabled(True)

        if self.transaction.status == status.code["SCHEDULED"]:
            self.ui.true_start_frame.setVisible(True)
            self.ui.true_start_checkbox.setVisible(True)
            self.ui.true_start_dateedit.setVisible(False)

        if self.transaction.status == status.code["ONGOING"] or self.transaction.status == status.code["LATE"]:
            #BLOKOWANIE

            self.ui.true_start_frame.setVisible(True)
            self.ui.true_start_frame.setEnabled(False)
            self.ui.true_start_checkbox.setVisible(True)
            self.ui.true_start_checkbox.setChecked(True)
            self.ui.true_start_dateedit.setVisible(True)
            self.ui.true_start_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.transaction.true_start))

            self.ui.true_end_frame.setVisible(True)
            self.ui.true_end_checkbox.setVisible(True)
            self.ui.true_end_dateedit.setVisible(False)

        if self.transaction.status == status.code["FINISHED"]:
            self.ui.true_start_frame.setVisible(True)
            self.ui.true_start_frame.setEnabled(False)
            self.ui.true_start_checkbox.setVisible(True)
            self.ui.true_start_checkbox.setChecked(True)
            self.ui.true_start_dateedit.setVisible(True)
            self.ui.true_start_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.transaction.true_start))

            self.ui.true_end_frame.setVisible(True)
            self.ui.true_end_frame.setEnabled(False)
            self.ui.true_end_checkbox.setVisible(True)
            self.ui.true_end_checkbox.setChecked(True)
            self.ui.true_end_dateedit.setVisible(True)
            self.ui.true_end_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.transaction.true_end))

            if self.transaction.deliverable:
                self.ui.true_delivery_frame.setVisible(True)
                self.ui.true_delivery_frame.setEnabled(True)
                self.ui.true_delivery_checkbox.setVisible(True)
                self.ui.true_delivery_checkbox.setEnabled(True)
                self.ui.true_delivery_dateedit.setVisible(False)


        if self.transaction.status == status.code["DELIVERED"]:
            # BLOKOWANIE
            self.ui.true_start_frame.setVisible(True)
            self.ui.true_start_frame.setEnabled(False)
            self.ui.true_start_checkbox.setVisible(True)
            self.ui.true_start_checkbox.setChecked(True)
            self.ui.true_start_dateedit.setVisible(True)
            self.ui.true_start_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.transaction.true_start))

            self.ui.true_end_frame.setVisible(True)
            self.ui.true_end_frame.setEnabled(False)
            self.ui.true_end_checkbox.setVisible(True)
            self.ui.true_end_checkbox.setChecked(True)
            self.ui.true_end_dateedit.setVisible(True)
            self.ui.true_end_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.transaction.true_end))

            self.ui.true_delivery_frame.setVisible(True)
            self.ui.true_delivery_frame.setEnabled(False)
            self.ui.true_delivery_checkbox.setVisible(True)
            self.ui.true_delivery_checkbox.setChecked(True)
            self.ui.true_delivery_dateedit.setVisible(True)
            self.ui.true_delivery_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.transaction.true_delivery))

    def _activated_true_start_checkbox(self, state):
        if state is True:
            self.ui.true_start_dateedit.setDate(QDate.currentDate())
            self._activated_true_start_dateedit(QDate.currentDate())
            self.ui.true_start_dateedit.setVisible(True)
        else:
            self.ui.true_end_checkbox.setChecked(False)
            self._activated_true_end_checkbox(False)
            self.ui.true_start_dateedit.setVisible(False)
            self.transaction.set_true_start(None)
        self.ui.save_button.setVisible(True)

    def _activated_true_end_checkbox(self, state):
        if state is True:
            self.ui.true_end_dateedit.setMinimumDate(self.convert_pyDateTime_to_QDate(self.transaction.true_start))
            self.ui.true_end_dateedit.setDate(QDate.currentDate())
            self._activated_true_end_dateedit(QDate.currentDate())
            self.ui.true_end_dateedit.setVisible(True)
        else:
            self.ui.true_end_dateedit.clearMinimumDate()
            self.ui.true_delivery_checkbox.setChecked(False)
            self._activated_true_delivery_checkbox(False)
            self.ui.true_end_dateedit.setVisible(False)
            self.transaction.set_true_end(None)

    def _activated_true_delivery_checkbox(self, state):
        if state is True:
            self.ui.true_delivery_dateedit.setMinimumDate(self.convert_pyDateTime_to_QDate(self.transaction.true_end))
            self.ui.true_delivery_dateedit.setDate(QDate.currentDate())
            self._activated_true_delivery_dateedit(QDate.currentDate())
            self.ui.true_delivery_dateedit.setVisible(True)
        else:
            self.ui.true_delivery_dateedit.clearMinimumDate()
            self.ui.true_delivery_dateedit.setVisible(False)
            self.transaction.set_true_delivery(None)
        self._show_delivered_button()

    def _activated_true_start_dateedit(self, date):
        self.transaction.set_true_start(date.toPyDate())

    def _activated_true_end_dateedit(self, date):
        self.transaction.set_true_end(date.toPyDate())

    def _activated_true_delivery_dateedit(self, date):
        self.transaction.set_true_delivery(date.toPyDate())

    def _activated_save_button(self):
        self.transaction.update_data()
        self.ui.save_button.setVisible(False)

    def _activated_delivered_button(self):
        buttonReply = QMessageBox.question(self, 'Transaction and Task - Delivery', 'Transaction and all belongs tasks will change status to Delivered with date {}.\n\nContinue ?'.format(self.transaction.true_delivery),
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            ready = True
            not_ready_tasks = []
            for task in self.transaction.tasks:
                if task.status < status.code["FINISHED"]:
                    ready = False
                    not_ready_tasks.append(task.name)
            if ready:
                self.transaction.set_released(1)
                self.transaction.update_data()
                self.ui.delivered_button.setVisible(False)
            else:
                all_names = ""
                for name in not_ready_tasks:
                    all_names += name
                QMessageBox.information(self, 'Delivery not possible', 'Unable to delivery.\nThis transaction has still ongoing tasks:\n\n {}'.format(all_names))
                self.ui.true_delivery_checkbox.setEnabled(False)


class TransactionEditorModule(QWidget, DateManager):
    signal_editing = pyqtSignal(bool)

    def __init__(self, user):
        QWidget.__init__(self)
        DateManager.__init__(self)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.me = user
        self.transaction = Transaction(db=self.me.db)

        self.customer = Customer(db=self.me.db)
        self.product = Product(db=self.me.db)
        self.transaction_type = Transaction_type(db=self.me.db)
        self.responsible = Employee(db=self.me.db)
        self.admin = Employee(db=self.me.db)

        try:
            self.ui = uic.loadUi(r'src\ui\transaction_editor_widget.ui', self)
        except Exception:
                    self.logger.exception(f'Error while trying to find and load ui file')
                    Terminate_Widget(20)
        self._setup_ui()
        self._connect_signals()

    def _connect_signals(self):
        self.ui.customer_combox.activated.connect(self._activated_customer_combox)
        self.ui.product_combox.activated.connect(self._activated_products_combox)
        self.ui.type_combox.activated.connect(self._activated_types_combox)
        self.ui.transaction_name_lineedit.textEdited.connect(self._activated_transaction_name_lineedit)
        self.ui.responsible_combox.activated.connect(self._activated_responsible_combox)
        self.ui.admin_combox.activated.connect(self._activated_admin_combox)
        self.ui.charge_code_lineedit.textEdited.connect(self._activated_transaction_charge_code_lineedit)
        self.ui.deliverable_yes_radiobutton.clicked.connect(self._activated_deliverable_yes_radiobutton)
        self.ui.deliverable_no_radiobutton.clicked.connect(self._activated_deliverable_no_radiobutton)
        self.ui.planned_start_dateedit.userDateChanged.connect(self._activated_planned_start_date)
        self.ui.planned_end_dateedit.userDateChanged.connect(self._activated_planned_end_date)
        self.ui.planned_delivery_dateedit.userDateChanged.connect(self._activated_planned_delivery_date)

        self.ui.add_admin_button.clicked.connect(self._activated_add_admin_button)
        self.ui.remove_admin_button.clicked.connect(self._activated_remove_admin_button)
        self.ui.save_button.clicked.connect(self._activated_save_button)
        self.ui.register_button.clicked.connect(self._activated_register_button)
        self.ui.delete_button.clicked.connect(self._activated_delete_button)
        self.ui.cancel_button.clicked.connect(self._activated_cancel_button)

    def _setup_ui(self):
        self._ui_default()

    def _ui_default(self):
        #Cleaning ui
        self.ui.customer_combox.clear()
        self.ui.product_combox.clear()
        self.ui.type_combox.clear()
        self.ui.transaction_name_lineedit.clear()
        self.ui.responsible_combox.clear()
        self.ui.charge_code_lineedit.clear()
        self.ui.deliverable_no_radiobutton.setAutoExclusive(False)
        self.ui.deliverable_yes_radiobutton.setAutoExclusive(False)
        self.ui.deliverable_no_radiobutton.setChecked(False)
        self.ui.deliverable_yes_radiobutton.setChecked(False)
        self.ui.deliverable_no_radiobutton.setAutoExclusive(True)
        self.ui.deliverable_yes_radiobutton.setAutoExclusive(True)

        #Hidding buttons
        self.ui.register_button.setVisible(False)
        self.ui.register_button.setEnabled(False)
        self.ui.save_button.setVisible(False)
        self.ui.cancel_button.setVisible(True)
        self.ui.delete_button.setVisible(False)
        self.ui.delete_button.setEnabled(False)
        self.ui.planned_delivery_frame.setVisible(False)

        #Unlockin frames
        self.ui.planned_delivery_frame.setEnabled(True)
        self.ui.customer_frame_2.setEnabled(True)
        self.ui.product_frame.setEnabled(True)
        self.ui.type_frame.setEnabled(True)
        self.ui.transaction_name_frame.setEnabled(True)
        self.ui.responsible_frame.setEnabled(True)
        self.ui.charge_code_frame.setEnabled(True)
        self.ui.deliverable_frame.setEnabled(True)
        self.ui.planned_date_frame.setEnabled(True)
        self.ui.planned_start_frame.setEnabled(True)
        self.ui.planned_end_frame.setEnabled(True)

    def create_transaction(self):
        self.transaction.reset()
        self._ui_default()
        self.ui.planned_start_dateedit.setDate(QDate.currentDate())
        self.ui.planned_end_dateedit.setDate(QDate.currentDate())
        self.ui.planned_delivery_dateedit.setDate(QDate.currentDate())
        self.ui.register_button.setVisible(True)
        self._load_customers_to_combox()
        self._load_types_to_combox()
        self._load_responsible_to_combox()
        self.ui.responsible_combox.setCurrentIndex(
            self.responsible.logins.copy().index(self.me.login))
        self.transaction.responsible.set_login(self.me.login)
        self._load_admin_to_combox()

        self.transaction.set_planned_start(self.ui.planned_start_dateedit.date().toPyDate())
        self.transaction.set_planned_end(self.ui.planned_end_dateedit.date().toPyDate())
        self._refresh_admins_plaintextedit()

    def edit_transaction(self, transaction):
        self.signal_editing.emit(True)
        self._ui_default()
        self.ui.save_button.setVisible(True)
        self.ui.delete_button.setVisible(True)
        self.transaction = transaction
        self.customer = self.transaction.customer
        self.product = self.transaction.product
        self.transaction_type = self.transaction.transaction_type
        self.responsible = self.transaction.responsible

        self._load_customers_to_combox()
        self.ui.customer_combox.setCurrentIndex(
            self.customer.ids.copy().index(self.transaction.customer.id))

        self._load_products_to_combox()
        self.ui.product_combox.setCurrentIndex(
            self.product.ids.copy().index(self.transaction.product.id))

        self._load_types_to_combox()
        self.ui.type_combox.setCurrentIndex(
            self.transaction_type.ids.copy().index(self.transaction.transaction_type.id))

        self.ui.transaction_name_lineedit.setText(self.transaction.name)

        self._load_responsible_to_combox()
        self.ui.responsible_combox.setCurrentIndex(
            self.responsible.logins.copy().index(self.transaction.responsible.login))

        self.ui.charge_code_lineedit.setText(self.transaction.charge_code)

        if self.transaction.deliverable:
            self.ui.deliverable_yes_radiobutton.setChecked(True)
            self.ui.planned_delivery_frame.setVisible(True)
        else:
            self.ui.deliverable_no_radiobutton.setChecked(True)

        self.ui.planned_start_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_start))
        self.ui.planned_end_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_end))
        self.ui.planned_delivery_dateedit.setDate(self.convert_pyDateTime_to_QDate(self.transaction.planned_delivery))

        self._load_admin_to_combox()
        self._refresh_admins_plaintextedit()


        if len(self.transaction.tasks) > 0:
            task_dates = [d.planned_end for d in self.transaction.tasks]
            task_dates.sort(reverse=True)
            self.ui.planned_end_dateedit.setMinimumDate(self.convert_pyDateTime_to_QDate(task_dates[0]))
            if self.transaction.planned_delivery is not None:
                self.ui.planned_delivery_dateedit.setMinimumDate(self.convert_pyDateTime_to_QDate(task_dates[0]))

        self._delete_button_controller()
        self._register_and_save_buttons_controller()

        #Access level
        if self.transaction.has_childs():
            self.ui.deliverable_frame.setEnabled(False)
        if self.transaction.released == 1:
            self.ui.customer_frame_2.setEnabled(False)
            self.ui.product_frame.setEnabled(False)
            self.ui.type_frame.setEnabled(False)
            self.ui.transaction_name_frame.setEnabled(False)
            self.ui.responsible_frame.setEnabled(False)
            self.ui.charge_code_frame.setEnabled(False)
            self.ui.deliverable_frame.setEnabled(False)
            self.ui.planned_date_frame.setEnabled(False)
            self.ui.delete_button.setEnabled(False)
            self.ui.save_button.setEnabled(False)

        if self.transaction.status >= status.code["ONGOING"]:
            self.ui.planned_start_frame.setEnabled(False)
        if self.transaction.status >= status.code["FINISHED"]:
            self.ui.planned_end_frame.setEnabled(False)
        if self.transaction.status == status.code["DELIVERED"]:
            self.ui.planned_delivery_frame.setEnabled(False)

    def _load_customers_to_combox(self):
        self.customer.load_names()
        self.ui.customer_combox.clear()
        for element in self.customer.names:
            self.ui.customer_combox.addItem(element)

    def _load_products_to_combox(self):
        self.product.load_products_for_customer_only(self.customer.id)
        self.ui.product_combox.clear()
        for element in self.product.products:
            self.ui.product_combox.addItem(element)

    def _load_types_to_combox(self):
        self.transaction_type.load_types()
        self.ui.type_combox.clear()
        for element in self.transaction_type.types:
            self.ui.type_combox.addItem(element)

    def _load_responsible_to_combox(self):
        self.ui.responsible_combox.clear()
        self.responsible.load_full_names()
        for element in self.responsible.full_names:
            self.ui.responsible_combox.addItem(element)

    def _load_admin_to_combox(self):
        self.ui.admin_combox.clear()
        self.admin.load_full_names()
        for element in self.admin.full_names:
            self.ui.admin_combox.addItem(element)

    def _activated_customer_combox(self):
        self.customer.set_id_by_index(self.ui.customer_combox.currentIndex())
        self.transaction.customer.set_id(self.customer.id)
        self._load_products_to_combox()
        self._register_and_save_buttons_controller()

    def _activated_products_combox(self):
        self.product.set_id_by_index(self.ui.product_combox.currentIndex())
        self.transaction.product.set_id(self.product.id)
        self._register_and_save_buttons_controller()

    def _activated_types_combox(self):
        self.transaction_type.set_id_by_index(self.ui.type_combox.currentIndex())
        self.transaction.transaction_type.set_id(self.transaction_type.id)
        self._register_and_save_buttons_controller()

    def _activated_transaction_name_lineedit(self, name):
        forbidden_characters = ['/', '\\', '|', '*', '?', '<', '>', '"']
        for character in name:
            if character in forbidden_characters:
                self.ui.transaction_name_lineedit.setText(name.replace(f'{character}', ''))
            else:
                self.transaction.set_name(name.rstrip())
                self._register_and_save_buttons_controller()

    def _activated_responsible_combox(self, index):
        self.responsible.set_login_by_index(index)
        self.transaction.responsible.set_login(self.responsible.login)
        self._register_and_save_buttons_controller()

    def _activated_admin_combox(self, index):
        self.admin.set_login_by_index(index)

    def _activated_transaction_charge_code_lineedit(self, charge_code):
        self.transaction.set_charge_code(charge_code.strip())

    def _activated_deliverable_yes_radiobutton(self):
        self.transaction.set_deliverable(1)
        self.ui.planned_delivery_frame.setVisible(True)
        self.ui.planned_delivery_dateedit.setDate(QDate.currentDate())
        self.transaction.set_planned_delivery(self.ui.planned_delivery_dateedit.date().toPyDate())
        self._register_and_save_buttons_controller()

    def _activated_deliverable_no_radiobutton(self):
        self.transaction.set_deliverable(0)
        self.transaction.set_planned_delivery(None)
        self.ui.planned_delivery_frame.setVisible(False)
        self._register_and_save_buttons_controller()

    def _activated_planned_start_date(self, date):
        self.transaction.set_planned_start(date.toPyDate())
        self._register_and_save_buttons_controller()
        self._data_verification()

    def _activated_planned_end_date(self, date):
        self.transaction.set_planned_end(date.toPyDate())
        self._register_and_save_buttons_controller()
        self._data_verification()

    def _activated_planned_delivery_date(self, date):
        self.transaction.set_planned_delivery(date.toPyDate())
        self._register_and_save_buttons_controller()
        self._data_verification()

    def _activated_add_admin_button(self):
        if self.admin.login:
            self.transaction.add_admin(self.admin)
            self._refresh_admins_plaintextedit()
            self.ui.admin_combox.setCurrentIndex(0)

    def _activated_remove_admin_button(self):
        if self.admin.login:
            self.transaction.remove_admin(self.admin)
            self._refresh_admins_plaintextedit()

    def _activated_register_button(self):
        try:
            self.transaction.register_data()
        except Exception:
            self.logger.exception(f'Error while trying to find and load ui file')
            Terminate_Widget(20)
        else:
            self.signal_editing.emit(False)
            self.ui.hide()

    def _activated_save_button(self):
        try:
            self.transaction.update_data()
        except Exception:
            self.logger.exception(f'Error while trying to find and load ui file')
            Terminate_Widget(20)
        else:
            self.signal_editing.emit(False)
            self.ui.hide()

    def _activated_delete_button(self):
        if not self.transaction.has_childs():
            buttonReply = QMessageBox.question(self,
                                               'Delete transaction',
                                               "Are you going to delete transaction: {}\nPlease confirm".format(self.transaction.name),
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                self.transaction.delete_data()
                self.transaction.set_id(None)
                self.signal_editing.emit(False)
        else:
            self.transaction.signal_message.emit("Can't delete this transaction due to tasks dependency")
            self._delete_button_controller()

    def _activated_cancel_button(self):
        self.transaction.set_id(None)
        self.hide()
        self.signal_editing.emit(False)

    def _refresh_admins_plaintextedit(self):
        self.current_admins_plaintextedit.clear()
        curr_admins = ""
        for admin_login in self.transaction.admins:
            self.admin.set_login(admin_login)
            curr_admins += self.admin.full_name + '\n'
        self.current_admins_plaintextedit.setPlainText(curr_admins)

    def _register_and_save_buttons_controller(self):
        if self.transaction.ready_to_save():
            self.ui.register_button.setEnabled(True)
            self.ui.save_button.setEnabled(True)
        else:
            self.ui.register_button.setEnabled(False)
            self.ui.save_button.setEnabled(False)

    def _delete_button_controller(self):
        if not self.transaction.has_childs():
            self.ui.delete_button.setEnabled(True)
        else:
            self.ui.delete_button.setEnabled(False)

    def _data_verification(self):
        if self.transaction.planned_end is not None and self.transaction.planned_start is not None:
            if self.transaction.planned_end < self.transaction.planned_start:
                self.ui.planned_end_label.setStyleSheet('color: red')
            else:
                self.ui.planned_end_label.setStyleSheet('color: black')

        if self.transaction.planned_delivery is not None and self.transaction.planned_end is not None:
            if self.transaction.planned_delivery < self.transaction.planned_end:
                self.ui.planned_delivery_label.setStyleSheet('color: red')
            else:
                self.ui.planned_delivery_label.setStyleSheet('color: black')


class CommentsWidget(QWidget, DateManager):
    def __init__(self, transaction, task, user):
        QWidget.__init__(self)
        DateManager.__init__(self)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.transaction = transaction
        self.task = task
        self.me = user
        self.comments = None

        try:
            self.ui = uic.loadUi(r'src\ui\comments_widget.ui', self)
        except Exception:
            self.logger.exception(f'Error while trying to find and load ui file')
            Terminate_Widget(20)

        self._connect_signals()
        self._setup_me()


    def _setup_me(self):
        try:
            self.ui.filter_system_checkbox.setChecked(True)
            self.ui.filter_user_checkbox.setChecked(True)
        except Exception as err:
            print(err)

    def _connect_signals(self):
        self.transaction.signal_id_changed.connect(self._reload_transaction)
        self.task.signal_id_changed.connect(self._reload_task)
        self.ui.filter_system_checkbox.toggled.connect(self._activated_filter_system_checkbox)
        self.ui.filter_user_checkbox.toggled.connect(self._activated_filter_user_checkbox)
        self.ui.add_comment_button.clicked.connect(self._activated_add_comment_button)

    def _reload_task(self):
        self.ui.comments_display_groupbox.setTitle("TASK COMMENTS")
        self.task._load_comments()
        self.comments = self.task.comments
        self._reload()

    def _reload_transaction(self):
        self.ui.comments_display_groupbox.setTitle("TRANSACTION COMMENTS")
        self.transaction._load_comments()
        self.comments = self.transaction.comments
        self._reload()

    def _reload(self):
        self.ui.comments_display_textbrowser.clear()
        if self.comments is not None:
            html_text_header = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
                                <html><head><meta name="qrichtext" content="1" /><style type="text/css">
                                p, li { white-space: pre-wrap; }
                                </style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8pt; font-weight:400; font-style:normal;">'''
            html_text_body = ''''''
            html_text_blank_line = '''<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">         </p></body></html>'''


            for comment in self.comments:

                if comment.source == "USER" and self.filter_user is True:
                    for single_line in comment.description.split('\n'):
                        html_text_body += r'''<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:11pt;  color:#d08b00">{comment_body}</span></p>'''.format(
                            comment_body=single_line)

                    html_text_signature = '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt; text-decoration: underline; color:#7e7e7e">{author}</span></a><span style=" font-size:8pt; color:#767676;">  {comment_date}</span></p>'.format(
                        author=comment.publisher.full_name,  comment_date=comment.publishing_date)

                    self.comments_display_textbrowser.append(
                    html_text_header + html_text_body + html_text_signature + html_text_blank_line)

                if comment.source == "SYSTEM" and self.filter_system is True:
                    for single_line in comment.description.split('\n'):
                        html_text_body += r'''<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;   color:#b53d3d">{comment_body}</span></p>'''.format(
                            comment_body=single_line)

                    html_text_signature = '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt; text-decoration: underline; color:#7e7e7e">{author}</span></a><span style=" font-size:8pt; color:#767676;">  {comment_date}</span></p>'.format(
                        author="T.A.T.O.", comment_date=comment.publishing_date)
                    self.comments_display_textbrowser.append(
                        html_text_header + html_text_body + html_text_signature + html_text_blank_line)

                html_text_body = ''''''

    def _activated_filter_system_checkbox(self, state):
        if state is True:
            self.filter_system = True
            self._reload()
        else:
            self.filter_system = False
            self._reload()

    def _activated_filter_user_checkbox(self, state):
        if state is True:
            self.filter_user = True
            self._reload()
        else:
            self.filter_user = False
            self._reload()

    def _activated_add_comment_button(self):
        description = self.ui.new_comment_textedit.toPlainText()
        if description:
            try:
                new_comment = Comment(db=self.me.db)
                new_comment.set_source("USER")
                new_comment.set_transaction_id(self.transaction.id)
                new_comment.set_task_id(self.task.id)
                new_comment.set_description(description)
                new_comment.set_publisher_login(self.me.login)
            except Exception:
                self.logger.exception(f'Error while trying to save new comment')
                Terminate_Widget(20)
            else:
                new_comment.register_data()
                self.ui.new_comment_textedit.clear()
                self.comments.append(new_comment)
                self._reload()























