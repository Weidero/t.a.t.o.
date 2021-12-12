#THIS DOCUMENT DOES NOT CONTAIN ANY TECHNICAL DATA

import sys
import os
import logging
import time
import datetime
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon, QPixmap
from core.Core import Employee, Transaction
from core.GUI import MainGui
import core.CSSTemplates

"""
 /$$$$$$$$   /$$$$$$   /$$$$$$$$   /$$$$$$ 
|__  $$__/  /$$__  $$ |__  $$__/  /$$__  $$
   | $$    | $$  \ $$    | $$    | $$  \ $$
   | $$    | $$$$$$$$    | $$    | $$  | $$
   | $$    | $$__  $$    | $$    | $$  | $$
   | $$    | $$  | $$    | $$    | $$  | $$
   | $$ /$$| $$  | $$ /$$| $$ /$$|  $$$$$$/
   |__/|__/|__/  |__/|__/|__/|__/ \______/ 
                                                                                 
Module:         Main
Version         1.0 alpha 1
Release date:   18.01.2019
Author:         Dariusz Horbal (dariusz.horbal@collins.com)

This module is integral part of application T.A.T.O 
It CAN'T be used whitout colaboration with other T.A.T.O core.
"""

class Starter:
    try:
        my_login = os.getlogin()
        if os.path.isdir(os.getcwd() + '\\log\\' + my_login) is False:
            new_user = True
            os.mkdir(os.getcwd() + '\\log\\' + my_login)
        else:
            new_user = False
        logging.basicConfig(level=logging.INFO,
                            filename='log\\' + my_login + '\\' + my_login + '.log',
                            filemode="w",
                            format='%(levelname)-8s %(name)-30s  %(message)-s  ',
                            datefmt='%d-%b-%y %H:%M:%S')
        logger = logging.getLogger(__name__)
    except Exception as err:
        print(f'Error occured. Please contact Dariusz Horbal: {str(err)}')

    def __init__(self,):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.ui = uic.loadUi(r'src\ui\starter.ui')
        self.force_refresh = QApplication.processEvents
        self.me = Employee()
        self.me.set_login(os.getlogin())
        # self.speed_test()
        self.main_path = os.getcwd()
        self.no_error_status = True
        self._connect_signals()
        self._setup_ui()

        self.ui.show()
        self.main_gui = MainGui(user=self.me)

        self.ui.setWindowIcon(QIcon('src/img/ico/start.ico'))
        self.ui.setWindowTitle('Task And Time Organizer')
        self.ui.login_button.setVisible(False)
        self.ui.login_button.setVisible(False)
        self._all_animations()

    def _setup_ui(self):
        self.ui.access_denied.setVisible(False)
        self.ui.access_granded.setVisible(False)
        self.ui.welcome.setVisible(False)
        self.ui.user_name.setVisible(False)

        self.ui.cmd_starting.setVisible(False)
        self.ui.cmd_starting_ok.setVisible(False)
        self.ui.cmd_starting_failed.setVisible(False)

        self.ui.cmd_connecting.setVisible(False)
        self.ui.cmd_connecting_ok.setVisible(False)
        self.ui.cmd_connecting_failed.setVisible(False)

        self.ui.cmd_configuring.setVisible(False)
        self.ui.cmd_configuring_ok.setVisible(False)
        self.ui.cmd_configuring_failed.setVisible(False)

        self.ui.cmd_user_settings.setVisible(False)
        self.ui.cmd_user_settings_ok.setVisible(False)
        self.ui.cmd_user_settings_new_user.setVisible(False)

        self.ui.cmd_checking_access.setVisible(False)
        self.ui.cmd_checking_access_ok.setVisible(False)
        self.ui.cmd_checking_access_failed.setVisible(False)

        self.ui.cmd_loading.setVisible(False)
        self.ui.arka.setVisible(False)


        self.total_steps = 26
        self.current_step = 0
        self.ui.progress_bar.setValue(0)

    def _connect_signals(self):
        self.ui.login_button.clicked.connect(self._all_animations)

    def _update_progress_bar(self):
        self.current_step += 1
        self.ui.progress_bar.setValue((self.current_step / self.total_steps) * 100)

    def _all_animations(self):
        self.ui.login_button.setEnabled(False)
        self._cmd_starting_animation()
        self._cmd_connecting_animation()
        self._cmd_configuring_animation()
        self._cmd_user_settings_animation()
        self._cmd_checking_access_animation()
        self._welcome_animation()
        if self.no_error_status:
            self._loading()

    def _loading(self):
        self.ui.cmd_loading.setVisible(True)
        for i in range(0, 4):
            self.ui.cmd_loading.setText(self.ui.cmd_loading.text() + '.')

            time.sleep(.5)
            self.force_refresh()
        self._update_progress_bar()
        self.ui.close()
        self.main_gui.setWindowOpacity(0)
        self.main_gui.ui.show()
        # self.tmm.setWindowOpacity(0)
        # self.tmm.show()
        for i in range(0, 101):
            # self.tmm.setWindowOpacity(i/100)
            self.main_gui.setWindowOpacity(i/100)
            time.sleep(.01)

    def _cmd_starting_animation(self):
        self.ui.cmd_starting.setVisible(True)
        for i in range(0, 5):
            self.ui.cmd_starting.setText(self.ui.cmd_starting.text() + ".")
            time.sleep(.1)
            self._update_progress_bar()
            self.force_refresh()

        self.ui.cmd_starting_ok.setVisible(True)

    def _cmd_connecting_animation(self):
        self.ui.cmd_connecting.setVisible(True)
        for i in range(0, 6):
            self.ui.cmd_connecting.setText(self.ui.cmd_connecting.text() + ".")
            self._update_progress_bar()
            time.sleep(.1)
            self.force_refresh()

        if os.path.isfile(self.main_path + '\\db\\database.db'):
            self.ui.cmd_connecting_ok.setVisible(True)
            self.logger.info(f'connection OK')
        else:
            self.ui.cmd_connecting_failed.setVisible(True)
            self.logger.info(f'connection OK')
            self.no_error_status = False

    def _cmd_configuring_animation(self):
        self.ui.cmd_configuring.setVisible(True)
        for i in range(0, 8):
            self.ui.cmd_configuring.setText(self.ui.cmd_configuring.text() + ".")
            self._update_progress_bar()
            time.sleep(.1)
            self.force_refresh()

        if os.path.isfile(self.main_path + '\\config\\TATO.config'):
            self.ui.cmd_configuring_ok.setVisible(True)
            self.logger.info(f'main configuration OK')
        else:
            self.logger.info(f'main configuration FAILED')
            self.ui.cmd_configuring_failed.setVisible(True)
            self.no_error_status = False

    def _cmd_user_settings_animation(self):
        self.ui.cmd_user_settings.setVisible(True)
        for i in range(0, 3):
            self.ui.cmd_user_settings.setText(self.ui.cmd_user_settings.text() + ".")
            self._update_progress_bar()
            time.sleep(.1)
            self.force_refresh()
            self.new_user = False #TODO Musi!! zostac naprawione
        if self.new_user is True:
            self.ui.cmd_user_settings_new_user.setVisible(True)
        else:
            self.ui.cmd_user_settings_ok.setVisible(True)

    def _cmd_checking_access_animation(self):
        self.ui.cmd_checking_access.setVisible(True)
        for i in range(0, 3):
            self.ui.cmd_checking_access.setText(self.ui.cmd_checking_access.text() + ".")
            self._update_progress_bar()
            time.sleep(.1)
            self.force_refresh()

        if self.me.has_account():
            self.ui.cmd_checking_access_ok.setVisible(True)
            self.logger.info(f'user access OK')
        else:
            self.logger.info(f'user access FAILED')
            self.ui.cmd_checking_access_failed.setVisible(True)
            self.no_error_status = False
        self.force_refresh()

    def _welcome_animation(self):
        if self.me.has_account():
            time.sleep(1)
            access_info = f'ACCESS GRANTED'
            # if self.kara_status:
            #     access_info = f'ARKA PONAD ŚLĄSK'
            self.ui.access_granded.setText('<html><head/><body><p><span style=" color:#00aa00;"></span></p></body></html>')
            self.ui.access_granded.setVisible(True)
            word = ""
            for letter in access_info:
                word += letter
                self.ui.access_granded.setText(f'<html><head/><body><p><span style=" font-size:14pt; color:#00aa00;">{word}</span></p></body></html>')
                time.sleep(.07)
                self.force_refresh()
            self.force_refresh()
            self.ui.welcome.setVisible(True)
            time.sleep(1)
            self.force_refresh()
            # self.me.load_data()
            name = f'<html><head/><body><p><span style=" font-size:20pt;">{self.me.full_name}</span></p></body></html>'
            self.ui.user_name.setText(name)
            self.ui.user_name.setVisible(True)
        else:
            access_info = f'ACCESS DENIED'
            self.ui.access_denied.setText(' ')
            self.ui.access_denied.setVisible(True)
            word = ""
            for letter in access_info:
                word += letter
                self.ui.access_denied.setText(f'<html><head/><body><p><span style=" font-size:12pt; color:#aa0000;">{word}</span></p></body></html>')
                time.sleep(.07)
                self.force_refresh()

            contact = f'T.A.T.O. did not recognize your login: {self.me.login}.\n Please contact your supervisor !'
            self.ui.welcome.setText(' ')
            self.ui.welcome.setVisible(True)
            for letter in contact:
                self.ui.welcome.setText(self.ui.welcome.text() + letter)
                time.sleep(.04)
                self.force_refresh()

    def speed_test(self):

        self.me.db.cursor.execute("SELECT id FROM transactions WHERE customer_id = 4")
        transaction_list = self.me.db.fetchall()

        start = time.time()
        transaction = Transaction(db=self.me.db)
        for id in transaction_list:
            transaction.set_id(id[0])
            transaction.filter_show_released_task=True
            transaction.load_data_basic()
            transaction.load_data_childs()
        end = time.time()
        print('elapsed:', end-start)

        stat_employee = Employee(db=self.me.db)


if __name__ == '__main__':

    my_login = os.getlogin()
    if os.path.isdir(os.getcwd() + '\\log\\' + my_login) is False:
        os.mkdir(os.getcwd() + '\\log\\' + my_login)
    logging.basicConfig(level=logging.INFO,
                        filename='log\\' + my_login + '\\' + my_login + '.log',
                        filemode="w",
                        format='%(levelname)-8s %(name)-30s  %(message)-s  ',
                        datefmt='%d-%b-%y %H:%M:%S')
    logger = logging.getLogger(__name__)

    # logging.SUCCESS = 25  # between WARNING and INFO
    # logging.addLevelName(logging.SUCCESS, 'SUCCESS')
    # setattr(logger, 'success', lambda message, *args: logger._log(logging.SUCCESS, message, args))
    app = QApplication(sys.argv)
    app.setStyleSheet(core.CSSTemplates.my_style)
    starter = Starter()
    sys.exit(app.exec_())


