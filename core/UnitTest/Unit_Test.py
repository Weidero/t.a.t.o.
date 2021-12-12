import unittest
from unittest.mock import MagicMock

import os
import sys
import sqlite3
import datetime

from core.Core import Check, Rework, Task, Transaction, Status

status = Status()

class SignalReceiver:
    def __init__(self):
        self.received = None
        self.counter = 0

    def receiver(self, signal):
        self.received = signal
        self.counter += 1


class ConnectionDB:
    def __init__(self):
        self.db_path = os.getcwd() + '\\ut_database.db'
        if self.db_avaliable():
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
        else:
            sys.exit(4)

    def execute(self, cmd, param):
        if self.db_avaliable():
            self.cursor.execute(cmd, param)
        else:
            sys.exit(4) #TODO: RETRY functionality

    def commit(self):
        if self.db_avaliable():
            self.connection.commit()
        else:
            sys.exit(4) #TODO: RETRY functionality

    def fetchall(self):
        if self.db_avaliable():
            return self.cursor.fetchall()
        else:
            sys.exit(4)  # TODO: RETRY functionality

    def fetchone(self):
        if self.db_avaliable():
            return self.cursor.fetchone()
        else:
            sys.exit(4)  # TODO: RETRY functionality

    def db_avaliable(self):
        if os.path.isfile(self.db_path):
            return True
        else:
            return False

    def __del__(self):
        try:
            self.connection.close()
        except AttributeError:
            pass


 class Test_Task_Class(unittest.TestCase):
     db = ConnectionDB()

     def test_task_obj_created(self):
         task = Task(db=self.db)

      def test_task_obj_can_register_new_tupple_in_sqlite_database(self):
          name = "Test Name"
          transaction_id = 1
          activity_id = 1
          discipline_id = 1
          responsible_login = "horbald"
          planned_start = datetime.date(2019, 1, 1)
          planned_end = datetime.date(2019, 1, 1)
     
          created = SignalReceiver()
     
          task = Task(db=self.db)
          task.signal_created.connect(created.receiver)
     
          task.set_name(name)
          task.transaction.set_id(transaction_id)
          task.activity.set_id(activity_id)
          task.discipline.set_id(discipline_id)
          task.responsible.set_login(responsible_login)
          task.set_planned_start(planned_start)
          task.set_planned_end(planned_end)
          task.register_data()
          id_to_remove = self.db.cursor.lastrowid
          self.assertTrue(created.received)
     
          task2 = Task(db=self.db)
          task2.set_id(id_to_remove)
          self.assertEqual(task2.name, task.name)
          self.assertEqual(task2.lock, task.lock)
          self.assertEqual(task2.locking, task.locking)
     
     
          self.db.cursor.execute('DELETE FROM tasks WHERE id={}'.format(id_to_remove))
          self.db.commit()

    def test_task_obj_emit_signal_id_changed_when_id_changed(self):
          id = SignalReceiver()
          task = Task(db=self.db)
          task.signal_id_changed.connect(id.receiver)
          task.set_id(3)
          self.assertEqual(task.id, id.received)

     def test_task_obj_has_status_READY_TO_POP(self):
         task = Task(db=self.db)
         task.responsible.set_login("stack_task_wdm")
         self.assertEqual(task.status, code.Core.code["READY TO POP"])

     def test_task_obj_has_status_ASSIGNED(self):
         task = Task(db=self.db)
         task.responsible.set_login("horbald")
         self.assertEqual(task.status, code.Core.code["ASSIGNED"])

     def test_task_obj_has_status_SHEDULED(self):
         task = Task(db=self.db)
         task.responsible.set_login("horbald")
         task.set_planned_start(datetime.date(2019, 1, 1))
         task.set_planned_end(datetime.date(2019, 1, 1))
         self.assertEqual(task.status, code.Core.code["SCHEDULED"])

     def test_task_obj_has_status_ONGOING(self):
         task = Task(db=self.db)
         task.responsible.set_login("horbald")
         task.set_planned_start(datetime.date(2019, 1, 1))
         task.set_planned_end(datetime.date(2100, 1, 1))
         task.set_true_start(datetime.date(2019, 1, 1))
         self.assertEqual(task.status, code.Core.code["ONGOING"])

     def test_task_obj_has_status_LATE(self):
         task = Task(db=self.db)
         task.responsible.set_login("horbald")
         task.set_planned_start(datetime.date(2019, 1, 1))
         task.set_planned_end(datetime.date(2019, 1, 1))
         task.set_true_start(datetime.date(2019, 1, 1))
         self.assertEqual(task.status, code.Core.code["LATE"])

     def test_task_obj_has_status_READY_TO_CHECK(self):
         task = Task(db=self.db)
         task.responsible.set_login("horbald")
         task.set_checker_required(1)
         task.set_planned_start(datetime.date(2019, 1, 1))
         task.set_planned_end(datetime.date(2019, 1, 1))
         task.set_true_start(datetime.date(2019, 1, 1))
         task.set_true_end(datetime.date(2019, 1, 1))
         self.assertEqual(task.status, code.Core.code["READY TO CHECK"])

     def test_task_obj_has_status_IN_CHECK(self):
         task = Task(db=self.db)
         task.responsible.set_login("horbald")
         task.set_checker_required(1)
         task.set_planned_start(datetime.date(2019, 1, 1))
         task.set_planned_end(datetime.date(2019, 1, 1))
         task.set_true_start(datetime.date(2019, 1, 1))
         task.set_true_end(datetime.date(2019, 1, 1))
         task.check.responsible.set_login("mikulam")
         self.assertEqual(task.status, code.Core.code["IN CHECK"])

      def test_task_obj_has_status_IN_CHECKING_STACK(self):
          task = Task(db=self.db)
          task.responsible.set_login("horbald")
          task.set_checker_required(1)
          task.set_planned_start(datetime.date(2019, 1, 1))
          task.set_planned_end(datetime.date(2019, 1, 1))
          task.set_true_start(datetime.date(2019, 1, 1))
          task.set_true_end(datetime.date(2019, 1, 1))
          task.check.responsible.set_login("stack_check")
          self.assertEqual(task.status, status.core["IN CHECKING STACK"])
     
      def test_task_obj_has_status_CHECKER_ASSIGNED(self):
          task = Task(db=self.db)
          task.responsible.set_login("horbald")
          task.set_checker_required(1)
          task.set_planned_start(datetime.date(2019, 1, 1))
          task.set_planned_end(datetime.date(2019, 1, 1))
          task.set_true_start(datetime.date(2019, 1, 1))
          task.set_true_end(datetime.date(2019, 1, 1))
          task.check.responsible.set_login("mikulam")
          self.assertEqual(task.status, status.core["CHECKER ASSIGNED"])
     
      def test_task_obj_has_status_CHECKING_SCHEDULED(self):
          task = Task(db=self.db)
          task.responsible.set_login("horbald")
          task.set_checker_required(1)
          task.set_planned_start(datetime.date(2019, 1, 1))
          task.set_planned_end(datetime.date(2019, 1, 1))
          task.set_true_start(datetime.date(2019, 1, 1))
          task.set_true_end(datetime.date(2019, 1, 1))
          task.check.responsible.set_login("mikulam")
          task.check.set_planned_start(datetime.date(2019, 1, 1))
          task.check.set_planned_end(datetime.date(2019, 1, 1))
          self.assertEqual(task.status, status.core["CHECKING SCHEDULED"])
     
      def test_task_obj_has_status_CHECK_ONGING(self):
          task = Task(db=self.db)
          task.responsible.set_login("horbald")
          task.set_checker_required(1)
          task.set_planned_start(datetime.date(2019, 1, 1))
          task.set_planned_end(datetime.date(2019, 1, 1))
          task.set_true_start(datetime.date(2019, 1, 1))
          task.set_true_end(datetime.date(2019, 1, 1))
          task.check.responsible.set_login("mikulam")
          task.check.set_planned_start(datetime.date(2019, 1, 1))
          task.check.set_planned_end(datetime.date(2019, 12, 31))
          task.check.set_true_start(datetime.date(2019, 1, 1))
          self.assertEqual(task.status, status.core["CHECK - ONGOING"])
     
      def test_task_obj_has_status_CHECK_LATE(self):
          task = Task(db=self.db)
          task.responsible.set_login("horbald")
          task.set_checker_required(1)
          task.set_planned_start(datetime.date(2019, 1, 1))
          task.set_planned_end(datetime.date(2019, 1, 1))
          task.set_true_start(datetime.date(2019, 1, 1))
          task.set_true_end(datetime.date(2019, 1, 1))
          task.check.responsible.set_login("mikulam")
          task.check.set_planned_start(datetime.date(2019, 1, 1))
          task.check.set_planned_end(datetime.date(2019, 1, 1))
          task.check.set_true_start(datetime.date(2019, 1, 1))
          self.assertEqual(task.status, status.core["CHECK - LATE"])

     def test_task_obj_has_status_REWORK_NEEDED(self):
         task = Task(db=self.db)
         task.responsible.set_login("horbald")
         task.set_checker_required(1)
         task.set_planned_start(datetime.date(2019, 1, 1))
         task.set_planned_end(datetime.date(2019, 1, 1))
         task.set_true_start(datetime.date(2019, 1, 1))
         task.set_true_end(datetime.date(2019, 1, 1))
         task.check.responsible.set_login("mikulam")
         task.check.set_planned_start(datetime.date(2019, 1, 1))
         task.check.set_planned_end(datetime.date(2019, 1, 1))
         task.check.set_true_start(datetime.date(2019, 1, 1))
         task.check.set_rework(1)
         task.check.set_released(1)
         self.assertEqual(task.status, code.Core.code["REWORK NEEDED"])

      def test_task_obj_has_status_DELIVERED(self):
          task = Task(db=self.db)
          task.set_true_delivery(datetime.date(2019, 1, 1))
          self.assertEqual(task.status, status.core["DELIVERED"])
     
      def test_task_obj_has_status_READY_FOR_DELIVERY(self):
          task = Task(db=self.db)
          task.set_checker_required(0)
          task.set_deliverable(1)
          task.set_true_end(datetime.date(2019, 1, 1))
          self.assertEqual(task.status, status.core["READY FOR DELIVERY"])

      def test_check_obj_has_status_FINISHED(self):
          task = Task(db=self.db)
          task.responsible.set_login("horbald")
          task.set_planned_start(datetime.date(2019, 1, 1))
          task.set_planned_end(datetime.date(2019, 1, 1))
          task.set_true_start(datetime.date(2019, 1, 1))
          task.set_true_end(datetime.date(2019, 1 ,1 ))
          self.assertEqual(task.status, status.core["FINISHED"])
     
      def test_check_obj_has_status_RETURNED(self):
          task = Task(db=self.db)
          task.responsible.set_login("horbald")
          task.set_planned_start(datetime.date(2019, 1, 1))
          task.set_planned_end(datetime.date(2019, 1, 1))
          task.set_true_start(datetime.date(2019, 1, 1))
          task.set_true_end(datetime.date(2019, 1, 1))
          task.set_rework(1)
          task.set_released(1)
          self.assertEqual(task.status, status.core["RETURNED"])
     
      def test_check_obj_has_status_RELEASED(self):
          task = Task(db=self.db)
          task.responsible.set_login("horbald")
          task.set_planned_start(datetime.date(2019, 1, 1))
          task.set_planned_end(datetime.date(2019, 1, 1))
          task.set_true_start(datetime.date(2019, 1, 1))
          task.set_true_end(datetime.date(2019, 1, 1))
          task.set_rework(0)
          task.set_released(1)
          self.assertEqual(task.status, status.core["RELEASED"])

     def test_task_obj_has_status_IN_REWORK(self):
         task = Task(db=self.db)
         task.responsible.set_login("horbald")
         task.set_checker_required(1)
         task.set_planned_start(datetime.date(2019, 1, 1))
         task.set_planned_end(datetime.date(2019, 1, 1))
         task.set_true_start(datetime.date(2019, 1, 1))
         task.set_true_end(datetime.date(2019, 1, 1))
         task.check.responsible.set_login("mikulam")
         task.rework.set_planned_start(datetime.date(2019, 1, 1))
         task.rework.set_planned_end(datetime.date(2019, 1, 1))
         self.assertEqual(task.status, code.Core.code["IN REWORK"])

     def test_task_obj_has_status_FINISHED(self):
         task = Task(db=self.db)
         task.responsible.set_login("horbald")
         task.set_checker_required(0)
         task.set_deliverable(0)
         task.set_planned_start(datetime.date(2019, 1, 1))
         task.set_planned_end(datetime.date(2019, 1, 1))
         task.set_true_start(datetime.date(2019, 1, 1))
         task.set_true_end(datetime.date(2019, 1, 1))
         self.assertEqual(task.status, code.Core.code["FINISHED"])

     def test_task_obj_has_status_READY_FOR_DELIVERY_no_checking_required(self):
         task = Task(db=self.db)
         task.responsible.set_login("horbald")
         task.set_checker_required(0)
         task.set_deliverable(1)
         task.set_planned_start(datetime.date(2019, 1, 1))
         task.set_planned_end(datetime.date(2019, 1, 1))
         task.set_true_start(datetime.date(2019, 1, 1))
         task.set_true_end(datetime.date(2019, 1, 1))
         self.assertEqual(task.status, code.Core.code["READY TO DELIVERY"])

     def test_task_obj_has_status_READY_FOR_DELIVERY_rework_required(self):
         task = Task(db=self.db)
         task.responsible.set_login("horbald")
         task.set_checker_required(1)
         task.set_deliverable(1)
         task.set_planned_start(datetime.date(2019, 1, 1))
         task.set_planned_end(datetime.date(2019, 1, 1))
         task.set_true_start(datetime.date(2019, 1, 1))
         task.set_true_end(datetime.date(2019, 1, 1))
         task.check._set_status(code.Core.code["RELEASED"])
         self.assertEqual(task.status, code.Core.code["READY TO DELIVERY"])

     def test_task_obj_has_status_DELIVERED_no_checking_required(self):
         task = Task(db=self.db)
         task.responsible.set_login("horbald")
         task.set_checker_required(0)
         task.set_deliverable(1)
         task.set_planned_start(datetime.date(2019, 1, 1))
         task.set_planned_end(datetime.date(2019, 1, 1))
         task.set_true_start(datetime.date(2019, 1, 1))
         task.set_true_end(datetime.date(2019, 1, 1))
         task.set_true_delivery(datetime.date(2019, 1, 1))
         self.assertEqual(task.status, code.Core.code["DELIVERED"])


class Test_Transaction_Class(unittest.TestCase):
    db = ConnectionDB()
    dummy_date_1_1_2019 = datetime.date(2019, 1, 1)
    dummy_date_31_12_2019 = datetime.date(2019, 12, 31)

    def test_signal_is_emitted_when_planned_start_date_is_changed(self):
        sr = SignalReceiver()
        transaction = Transaction(db=self.db)
        transaction.signal_planned_start_changed.connect(sr.receiver)
        transaction.set_planned_start(self.dummy_date_1_1_2019)
        self.assertEqual(sr.received, self.dummy_date_1_1_2019) #check if signal is emited when date chantged

        transaction.set_planned_start(self.dummy_date_31_12_2019)
        self.assertEqual(sr.counter, 2)

    def test__reset_method_will_reset_all_attributes_to_default_values(self):
        transaction = Transaction(db=self.db)
        transaction.set_id(1)
        transaction.set_name("Test Transaction")
        # transaction.customer = Customer(db=db)
        # transaction.product = Product(db=db)
        # transaction.transaction_type = Transaction_type(db=db)
        # transaction.responsible = Employee(db=db)
        transaction.set_deliverable(0)
        transaction.set_planned_start(self.dummy_date_1_1_2019)
        transaction.set_planned_end (self.dummy_date_1_1_2019)
        transaction.set_planned_delivery (self.dummy_date_1_1_2019)
        transaction.set_true_start(self.dummy_date_1_1_2019)
        transaction.set_true_end(self.dummy_date_1_1_2019)
        transaction.set_true_delivery(self.dummy_date_1_1_2019)
        transaction.set_charge_code("12345")
        # transaction.escape_counter = 0
        transaction.reset()

        self.assertIsNone(transaction.id)
        self.assertIsNone(transaction.name)
        self.assertIsNone(transaction.deliverable)
        self.assertIsNone(transaction.planned_start)
        self.assertIsNone(transaction.planned_end)
        self.assertIsNone(transaction.planned_delivery)
        self.assertIsNone(transaction.true_start)
        self.assertIsNone(transaction.true_end)
        self.assertIsNone(transaction.true_delivery)
        self.assertIsNone(transaction.charge_code)

    def test_transaction_obj_has_status_SCHEDULED(self):
        transaction = Transaction(db=self.db)
        transaction.responsible.set_login("HORBALD")
        transaction.set_planned_start(datetime.date(2019, 1, 1))
        transaction.set_planned_end(datetime.date(2019, 1, 1))
        self.assertEqual(transaction.status, status.code["SCHEDULED"])

    def test_transaction_obj_has_status_ONGOING(self):
        transaction = Transaction(db=self.db)
        transaction.responsible.set_login("HORBALD")
        transaction.set_planned_start(datetime.date(2019, 1, 1))
        transaction.set_planned_end(datetime.date(2100, 1, 1))
        transaction.set_true_start(datetime.date(2019, 1, 1))
        self.assertEqual(transaction.status, status.code["ONGOING"])

    def test_transaction_obj_has_status_LATE(self):
        transaction = Transaction(db=self.db)
        transaction.responsible.set_login("HORBALD")
        transaction.set_planned_start(datetime.date(2019, 1, 1))
        transaction.set_planned_end(datetime.date(2019, 1, 1))
        transaction.set_true_start(datetime.date(2019, 1, 1))
        self.assertEqual(transaction.status, status.code["LATE"])

    def test_transaction_obj_has_status_FINISHED(self):
        transaction = Transaction(db=self.db)
        transaction.responsible.set_login("HORBALD")
        transaction.set_deliverable(0)
        transaction.set_planned_start(datetime.date(2019, 1, 1))
        transaction.set_planned_end(datetime.date(2019, 1, 1))
        transaction.set_true_start(datetime.date(2019, 1, 1))
        transaction.set_true_end(datetime.date(2019, 1, 1))
        transaction.set_released(1)
        self.assertEqual(transaction.status, status.code["FINISHED"])

    def test_obj_has_status_WAITING_FOR_TASKS(self):
        transaction = Transaction(db=self.db)
        transaction.responsible.set_login("HORBALD")
        transaction.set_deliverable(1)
        transaction.set_planned_start(datetime.date(2019, 1, 1))
        transaction.set_planned_end(datetime.date(2019, 1, 1))
        transaction.set_true_start(datetime.date(2019, 1, 1))
        transaction.set_true_end(datetime.date(2019, 1, 1))
        task1 = Task(db=self.db)
        task1.status = status.code["IN REWORK"]
        task2 = Task(db=self.db)
        task2.status = status.code["RELEASED"]
        transaction.tasks.append(task1)
        transaction._update_status()
        self.assertEqual(transaction.status, status.code["NOT READY TO DELIVERY"])

    def test_transaction_obj_has_status_READY_TO_DELIVERY(self):
        transaction = Transaction(db=self.db)
        transaction.responsible.set_login("HORBALD")
        transaction.set_deliverable(1)
        transaction.set_planned_start(datetime.date(2019, 1, 1))
        transaction.set_planned_end(datetime.date(2019, 1, 1))
        transaction.set_true_start(datetime.date(2019, 1, 1))
        transaction.set_true_end(datetime.date(2019, 1, 1))
        task1 = Task(db=self.db)
        task1.status = status.code["RELEASED"]
        task2 = Task(db=self.db)
        task2.status = status.code["RELEASED"]
        transaction.tasks.append(task1)
        transaction._update_status()
        self.assertEqual(transaction.status, status.code["READY TO DELIVERY"])

    def test_transaction_obj_has_status_DELIVERED(self):
        transaction = Transaction(db=self.db)
        transaction.responsible.set_login("HORBALD")
        transaction.set_deliverable(1)
        transaction.set_planned_start(datetime.date(2019, 1, 1))
        transaction.set_planned_end(datetime.date(2019, 1, 1))
        transaction.set_true_start(datetime.date(2019, 1, 1))
        transaction.set_true_end(datetime.date(2019, 1, 1))
        transaction.set_true_delivery(datetime.date(2019, 1, 1,))
        transaction.set_released(1)
        self.assertEqual(transaction.status, status.code["DELIVERED"])


 class Test_Check_Class(unittest.TestCase):
     db = ConnectionDB()

     def test_check_obj_created(self):
         check = Check(db=self.db)

     def test_check_obj_has_status_READY_TO_POP(self):
         check = Check(db=self.db)
         check.responsible.set_login("stack_check_wdm")
         self.assertEqual(check.status, code.Core.code["READY TO POP"])

     def test_check_obj_has_status_ASSIGNED(self):
         check = Check(db=self.db)
         check.responsible.set_login("horbald")
         self.assertEqual(check.status, code.Core.code["ASSIGNED"])

     def test_check_obj_has_status_SCHEDULED(self):
         check = Check(db=self.db)
         check.responsible.set_login("horbald")
         check.set_planned_start(datetime.date(2019, 1, 1))
         check.set_planned_end(datetime.date(2019, 1, 1))
         self.assertEqual(check.status, code.Core.code["SCHEDULED"])

     def test_check_obj_has_status_ONGOING(self):
         check = Check(db=self.db)
         check.responsible.set_login("horbald")
         check.set_planned_start(datetime.date(2019, 1, 1))
         check.set_planned_end(datetime.date(2100, 1, 1))
         check.set_true_start(datetime.date(2019, 1, 1))
         self.assertEqual(check.status, code.Core.code["ONGOING"])

     def test_check_obj_has_status_LATE(self):
         check = Check(db=self.db)
         check.responsible.set_login("horbald")
         check.set_planned_start(datetime.date(2019, 1, 1))
         check.set_planned_end(datetime.date(2019, 1, 1))
         check.set_true_start(datetime.date(2019, 1, 1))
         self.assertEqual(check.status, code.Core.code["LATE"])

     def test_check_obj_has_status_FINISHED(self):
         check = Check(db=self.db)
         check.responsible.set_login("horbald")
         check.set_planned_start(datetime.date(2019, 1, 1))
         check.set_planned_end(datetime.date(2019, 1, 1))
         check.set_true_start(datetime.date(2019, 1, 1))
         check.set_true_end(datetime.date(2019, 1,1))
         self.assertEqual(check.status, code.Core.code["FINISHED"])

     def test_check_obj_has_status_RETURNED(self):
         check = Check(db=self.db)
         check.responsible.set_login("horbald")
         check.set_planned_start(datetime.date(2019, 1, 1))
         check.set_planned_end(datetime.date(2019, 1, 1))
         check.set_true_start(datetime.date(2019, 1, 1))
         check.set_true_end(datetime.date(2019, 1, 1))
         check.set_rework(1)
         check.set_released(1)
         self.assertEqual(check.status, code.Core.code["RETURNED"])

     def test_check_obj_has_status_RELEASED(self):
         check = Check(db=self.db)
         check.responsible.set_login("horbald")
         check.set_planned_start(datetime.date(2019, 1, 1))
         check.set_planned_end(datetime.date(2019, 1, 1))
         check.set_true_start(datetime.date(2019, 1, 1))
         check.set_true_end(datetime.date(2019, 1, 1))
         check.set_rework(0)
         check.set_released(1)
         self.assertEqual(check.status, code.Core.code["RELEASED"])


 class Test_Rework_Class(unittest.TestCase):
     db = ConnectionDB()

     def test_rework_obj_created(self):
         rework = Rework(db=self.db)

      def test_rework_obj_has_status_READY_TO_POP(self):
          rework = Rework(db=self.db)
          rework.responsible.set_login("stack_check_wdm")
          self.assertEqual(rework.status, status.core["READY TO POP"])

     def test_rework_obj_has_status_ASSIGNED(self):
         rework = Rework(db=self.db)
         rework.responsible.set_login("horbald")
         self.assertEqual(rework.status, code.Core.code["ASSIGNED"])

     def test_rework_obj_has_status_SCHEDULED(self):
         rework = Rework(db=self.db)
         rework.responsible.set_login("horbald")
         rework.set_planned_start(datetime.date(2019, 1, 1))
         rework.set_planned_end(datetime.date(2019, 1, 1))
         self.assertEqual(rework.status, code.Core.code["SCHEDULED"])

     def test_rework_obj_has_status_ONGOING(self):
         rework = Rework(db=self.db)
         rework.responsible.set_login("horbald")
         rework.set_planned_start(datetime.date(2019, 1, 1))
         rework.set_planned_end(datetime.date(2100, 1, 1))
         rework.set_true_start(datetime.date(2019, 1, 1))
         self.assertEqual(rework.status, code.Core.code["ONGOING"])

     def test_rework_obj_has_status_LATE(self):
         rework = Rework(db=self.db)
         rework.responsible.set_login("horbald")
         rework.set_planned_start(datetime.date(2019, 1, 1))
         rework.set_planned_end(datetime.date(2019, 1, 1))
         rework.set_true_start(datetime.date(2019, 1, 1))
         self.assertEqual(rework.status, code.Core.code["LATE"])

     def test_rework_obj_has_status_FINISHED(self):
         rework = Rework(db=self.db)
         rework.responsible.set_login("horbald")
         rework.set_planned_start(datetime.date(2019, 1, 1))
         rework.set_planned_end(datetime.date(2019, 1, 1))
         rework.set_true_start(datetime.date(2019, 1, 1))
         rework.set_true_end(datetime.date(2019, 1 ,1 ))
         self.assertEqual(rework.status, code.Core.code["FINISHED"])

     def test_rework_obj_has_status_RELEASED(self):
         rework = Rework(db=self.db)
         rework.responsible.set_login("horbald")
         rework.set_planned_start(datetime.date(2019, 1, 1))
         rework.set_planned_end(datetime.date(2019, 1, 1))
         rework.set_true_start(datetime.date(2019, 1, 1))
         rework.set_true_end(datetime.date(2019, 1, 1))
         rework.set_released(1)
         self.assertEqual(rework.status, code.Core.code["RELEASED"])
