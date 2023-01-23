# -*- coding: utf-8 -*-
import os
import sys
import traceback
import subprocess
from datetime import datetime, timedelta

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QDialog

from db import get_all_data, get_one_row, get_columns, add_new_row, change_data_in_cell, custom_selection
from config_loader import engineers, machines, statuses, operation_types, path

"""Константы гланого окна"""
width = 1920 - 320
height = 1080 - 280
title = 'BTZ'

"""Константы таблицы главного окна"""
row_height = 30
visible_rows = 20

horizontal_header_height = 60
horizontal_header_width = 130

table_width = width - 10
table_height = row_height * visible_rows + horizontal_header_height + 2
scrollbar_width = 16

"""Константы кнопок главного окна"""
b_x = 10
b_y = table_height + 25
b_size_x = 150
b_size_y = 50


class InfoDialog(QDialog):
    """класс для вывода диалогового окна с предупреждениями"""
    btn_font = QtGui.QFont()
    btn_font.setPointSize(8)
    btn_font.setBold(True)
    btn_font.setWeight(50)

    def __init__(self, dlg_window=None, message=None):
        super().__init__()
        self.setWindowTitle('Предупреждение')
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.WindowTitleHint |
            QtCore.Qt.CustomizeWindowHint
        )

        self.dlg_window = dlg_window
        self.message = message
        self.textBrowser = QtWidgets.QTextBrowser(self)
        self.textBrowser.setEnabled(True)
        self.textBrowser.setGeometry(QtCore.QRect(5, 5, 215, 125))
        self.textBrowser.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.textBrowser.setFrameShadow(QtWidgets.QFrame.Plain)
        self.textBrowser.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textBrowser.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textBrowser.setAutoFormatting(QtWidgets.QTextEdit.AutoBulletList)
        self.textBrowser.setText(self.message)

        self.resize(225, 170)

        self.btn_ok = QtWidgets.QPushButton('Ok', self)
        self.btn_ok.setGeometry(QtCore.QRect(75, 135, 75, 23))
        self.btn_ok.setFont(self.btn_font)
        self.btn_ok.clicked.connect(self.btn_ok_func)

    def btn_ok_func(self):
        self.close()
        if self.dlg_window:
            self.dlg_window.setEnabled(True)

    def showEvent(self, event):
        event.accept()
        if self.dlg_window:
            self.dlg_window.setEnabled(False)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.request_dict = None

        self.selected_program_number = 'A0001'
        self.program_column_index = 3
        self.selected_row_index = 0
        self.detail_code_index = 1
        self.setup_window()
        self.setup_table()
        self.setup_dialog_windows()
        self.setup_buttons()
        self.update_data_in_table()

    def setup_window(self):
        """Настройки главного окна"""

        self.setWindowTitle(title)
        self.setMinimumSize(width, height)
        self.setMaximumSize(width, height)
        self.center()

    def setup_table(self):
        """Настройки таблицы"""

        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(65)

        headers = get_columns()
        s = len(max(headers, key=len))
        headers = [i.center(s, ' ') for i in headers]
        columns = len(headers)

        self.table = QtWidgets.QTableWidget(self)
        self.table.setGeometry(5, 5, table_width, table_height)
        self.table.setColumnCount(columns)
        self.table.setFrameShape(QtWidgets.QFrame.Box)
        self.table.setFrameShadow(QtWidgets.QFrame.Plain)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setLineWidth(1)
        self.table.setMidLineWidth(1)
        self.table.setAlternatingRowColors(True)

        self.table.verticalHeader().setDefaultSectionSize(row_height)
        self.table.verticalHeader().setVisible(False)

        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setMaximumSectionSize(table_width // 10)
        self.table.horizontalHeader().setFont(font)
        self.table.horizontalHeader().setMinimumHeight(horizontal_header_height)
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.table.itemSelectionChanged.connect(self.on_selection)

    def on_selection(self):
        """Настройки выделения"""
        self.selected_row_index = self.table.currentRow()
        self.selected_program_number = self.table.model().index(self.selected_row_index,
                                                                self.program_column_index).data()
        self.selected_detail_code = self.table.model().index(self.selected_row_index,
                                                             self.detail_code_index).data()

        if self.selected_program_number is None:
            self.btn_change.setEnabled(False)
        else:
            self.btn_change.setEnabled(True)

    def setup_buttons(self):
        """Настройки кнопок"""

        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(50)

        self.btn_add = QtWidgets.QPushButton('Добавить\nзапись', self)
        self.btn_add.setFont(font)
        self.btn_add.resize(b_size_x, b_size_y)
        self.btn_add.move(b_x, b_y)
        self.btn_add.clicked.connect(self.add_dlg.show)

        self.btn_change = QtWidgets.QPushButton('Изменить\nзапись', self)
        self.btn_change.setFont(font)
        self.btn_change.resize(b_size_x, b_size_y)
        self.btn_change.move(b_x * 2 + b_size_x, b_y)
        self.btn_change.clicked.connect(self.change_dlg.show)

        self.btn_select = QtWidgets.QPushButton('Выборка', self)
        self.btn_select.setFont(font)
        self.btn_select.resize(b_size_x, b_size_y)
        self.btn_select.move(b_x * 3 + b_size_x * 2, b_y)
        self.btn_select.clicked.connect(self.select_dlg.show)

        self.btn_open_dir = QtWidgets.QPushButton('Открыть\nпапку', self)
        self.btn_open_dir.setFont(font)
        self.btn_open_dir.resize(b_size_x, b_size_y)
        self.btn_open_dir.move(b_x * 4 + b_size_x * 3, b_y)
        self.btn_open_dir.clicked.connect(self.open_dir)

        self.btn_update = QtWidgets.QPushButton('Обновить', self)
        self.btn_update.setFont(font)
        self.btn_update.resize(b_size_x, b_size_y)
        self.btn_update.move(b_x * 5 + b_size_x * 4, b_y)
        self.btn_update.clicked.connect(self.btn_update_func)

    def btn_update_func(self):
        """функция кнопки обновления таблицы"""
        self.request_dict = None
        self.update_data_in_table(self.request_dict)

    def open_dir(self):
        """функция кнопки открытия директории"""
        dirs = os.listdir(path)
        if self.selected_detail_code in dirs:
            subprocess.Popen(fr'explorer {path}\{self.selected_detail_code}')
        else:
            os.mkdir(f'{path}\\{self.selected_detail_code}')
            subprocess.Popen(fr'explorer {path}\{self.selected_detail_code}')

    def setup_dialog_windows(self):
        """Загрузка диалоговых окон"""

        self.add_dlg = AddDialog(self)
        self.change_dlg = ChangeDialog(self)
        self.select_dlg = SelectDialog(self)

    def make_disabled(self):
        """Главное окно недоступно"""

        self.setEnabled(False)

    def make_enabled(self):
        """Главное окно доступно"""

        self.setEnabled(True)

    def update_data_in_table(self, request_dict=None):
        """Обновить данные в таблице"""

        self.table.clearContents()

        if not request_dict:
            data = get_all_data()
        else:
            self.request_dict = request_dict
            data = custom_selection(request_dict)

        self.rows = len(data)

        if self.rows < 25:
            self.table.setRowCount(visible_rows)
        else:
            self.table.setRowCount(self.rows)

        for i, row in enumerate(data):
            j = 0
            for key, value in row.items():
                if key == 'id':
                    continue
                if not value:
                    value = ''
                else:
                    if isinstance(value, datetime):
                        value = value.strftime("%d.%m.%Y")

                self.table.setItem(i, j, QTableWidgetItem(value))
                self.table.item(i, j).setTextAlignment(QtCore.Qt.AlignLeft)
                self.table.item(i, j).setTextAlignment(QtCore.Qt.AlignBottom)
                j += 1

        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.selectRow(self.selected_row_index)

    def center(self):
        """Центрировать окно"""

        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        self.add_dlg.close()
        self.change_dlg.close()
        self.select_dlg.close()
        event.accept()


class Dialog(QDialog):
    """Класс родителя диалоговых окон"""
    btn_font = QtGui.QFont()
    btn_font.setPointSize(8)
    btn_font.setBold(True)
    btn_font.setWeight(50)

    brush = QtGui.QBrush(QtGui.QColor(255, 0, 0, 200))
    brush.setStyle(QtCore.Qt.SolidPattern)

    def __init__(self, main_window):
        super().__init__()

        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.WindowTitleHint |
            QtCore.Qt.CustomizeWindowHint
        )

        self.vertical_headers = get_columns()

        self.name_index = 0
        self.detail_code_index = 1
        self.op_number_index = 2
        self.program_number_index = 3
        self.machine_index = 4
        self.operation_type_index = 5
        self.status_index = 6
        self.machine_time_index = 7
        self.creating_day_index = 8
        self.calculation_date_index = 9
        self.ok_date_index = 10
        self.introduction_date_index = 11
        self.dop_inf_index = 12

        self.main_window = main_window
        self.table = QtWidgets.QTableWidget(self)

    def setup_standard_dialog_table(self, vertical_headers):
        """загрузка таблицы"""

        self.t_rows = len(vertical_headers)
        self.t_height = self.t_rows * row_height + 2
        self.t_width = 400
        self.t_columns = 1

        self.table.setRowCount(len(vertical_headers))
        self.table.setColumnCount(self.t_columns)
        self.table.horizontalHeader().setVisible(False)
        self.table.setVerticalHeaderLabels(vertical_headers)
        self.table.setGeometry(5, 5, self.t_width, self.t_height)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setMaximumSectionSize(row_height)
        self.table.verticalHeader().setMinimumSectionSize(row_height)
        self.setFixedSize(self.t_width + 10, self.t_height + 100)
        self.center()

    def setup_standard_dialog_btn_layout(self):
        """Загрузка стандартного поля для кнопок"""

        self.horizontalLayoutWidget = QtWidgets.QWidget(self)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, self.t_height, self.t_width + 10, 100))

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout.setContentsMargins(25, 25, 25, 25)
        self.horizontalLayout.setSpacing(20)

    def setup_standard_dialog_buttons(self):
        """Загрузка стандартных функций кнопок"""

        self.btn_clear = QtWidgets.QPushButton('Очистить', self.horizontalLayoutWidget)
        self.btn_clear.setFont(self.btn_font)
        self.btn_clear.clicked.connect(self.btn_clear_func)
        self.horizontalLayout.addWidget(self.btn_clear)

        self.btn_cancel = QtWidgets.QPushButton('Отмена', self.horizontalLayoutWidget)
        self.btn_cancel.setFont(self.btn_font)
        self.btn_cancel.clicked.connect(self.close)
        self.horizontalLayout.addWidget(self.btn_cancel)

    def setup_standard_dialog_combo_boxes(self):
        """Загрузка комбобоксов для определенных полей"""

        self.cmb_engineers = QtWidgets.QComboBox()
        self.cmb_engineers.addItem(None)
        for name in engineers:
            self.cmb_engineers.addItem(name)

        self.cmb_machines = QtWidgets.QComboBox()
        self.cmb_machines.addItem(None)
        for machine in machines:
            self.cmb_machines.addItem(machine)

        self.cmb_operation_types = QtWidgets.QComboBox()
        self.cmb_operation_types.addItem(None)
        for op_type in operation_types:
            self.cmb_operation_types.addItem(op_type)

        self.cmb_statuses = QtWidgets.QComboBox()
        self.cmb_statuses.addItem(None)
        for status in statuses:
            self.cmb_statuses.addItem(status)

        last_14_days = [(datetime.now() - timedelta(days=i)).strftime("%d.%m.%Y") for i in range(14)]

        self.cmb_calculation_date = QtWidgets.QComboBox()
        self.cmb_calculation_date.addItem(None)
        self.cmb_calculation_date.addItems(last_14_days)

        self.cmb_ok_date = QtWidgets.QComboBox()
        self.cmb_ok_date.addItem(None)
        self.cmb_ok_date.addItems(last_14_days)

        self.cmb_introduction_date = QtWidgets.QComboBox()
        self.cmb_introduction_date.addItem(None)
        self.cmb_introduction_date.addItems(last_14_days)

        self.cmb_engineers.currentIndexChanged.connect(self.update_table_model)
        self.cmb_machines.currentIndexChanged.connect(self.update_table_model)
        self.cmb_operation_types.currentIndexChanged.connect(self.update_table_model)
        self.cmb_statuses.currentIndexChanged.connect(self.update_table_model)
        self.cmb_calculation_date.currentIndexChanged.connect(self.update_table_model)
        self.cmb_ok_date.currentIndexChanged.connect(self.update_table_model)
        self.cmb_introduction_date.currentIndexChanged.connect(self.update_table_model)

        if self.name_index is not None:
            self.table.setCellWidget(self.name_index, 0, self.cmb_engineers)
        if self.machine_index is not None:
            self.table.setCellWidget(self.machine_index, 0, self.cmb_machines)
        if self.operation_type_index is not None:
            self.table.setCellWidget(self.operation_type_index, 0, self.cmb_operation_types)
        if self.status_index is not None:
            self.table.setCellWidget(self.status_index, 0, self.cmb_statuses)
        if self.calculation_date_index is not None:
            self.table.setCellWidget(self.calculation_date_index, 0, self.cmb_calculation_date)
        if self.ok_date_index is not None:
            self.table.setCellWidget(self.ok_date_index, 0, self.cmb_ok_date)
        if self.introduction_date_index is not None:
            self.table.setCellWidget(self.introduction_date_index, 0, self.cmb_introduction_date)

    def get_data_from_table(self):
        """Получение данных из таблицы для проверки и последующего запроса"""

        request_data = []
        for i in range(self.t_rows):
            try:
                elem = self.table.model().index(i, 0).data()
            except:
                elem = None
            request_data.append(elem)
        result = dict(zip(self.vertical_headers, request_data))
        return result

    def update_table_model(self):
        """Расположение комбобоксов"""

        if self.name_index is not None:
            self.table.setItem(self.name_index, 0, QTableWidgetItem(self.cmb_engineers.currentText()))
        if self.machine_index is not None:
            self.table.setItem(self.machine_index, 0, QTableWidgetItem(self.cmb_machines.currentText()))
        if self.operation_type_index is not None:
            self.table.setItem(self.operation_type_index, 0, QTableWidgetItem(self.cmb_operation_types.currentText()))
        if self.status_index is not None:
            self.table.setItem(self.status_index, 0, QTableWidgetItem(self.cmb_statuses.currentText()))
        if self.calculation_date_index is not None:
            self.table.setItem(self.calculation_date_index, 0,
                               QTableWidgetItem(self.cmb_calculation_date.currentText()))
        if self.ok_date_index is not None:
            self.table.setItem(self.ok_date_index, 0, QTableWidgetItem(self.cmb_ok_date.currentText()))
        if self.introduction_date_index is not None:
            self.table.setItem(self.introduction_date_index, 0,
                               QTableWidgetItem(self.cmb_introduction_date.currentText()))

    def btn_clear_func(self):
        """Функция кнопки очистки полей"""
        self.table.clearContents()
        self.setup_standard_dialog_combo_boxes()

    def showEvent(self, event):
        self.main_window.make_disabled()
        event.accept()

    def closeEvent(self, event):
        self.main_window.make_enabled()
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        if event.key() == 16777220 or event.key() == 16777221:
            self.btn_ok.click()

    def center(self):
        """Центрирование диалогового окна"""

        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class AddDialog(Dialog):
    """Окно добавления записи"""

    def __init__(self, main_window):
        super().__init__(main_window)
        self.setWindowTitle('Добавить запись')
        self.vertical_headers = [
            self.vertical_headers[self.name_index],
            self.vertical_headers[self.detail_code_index],
            self.vertical_headers[self.machine_index],
            self.vertical_headers[self.operation_type_index],
            self.vertical_headers[self.op_number_index],
            self.vertical_headers[self.dop_inf_index],
        ]

        self.name_index = None
        self.detail_code_index = None
        self.op_number_index = None
        self.program_number_index = None
        self.machine_index = None
        self.operation_type_index = None
        self.status_index = None
        self.machine_time_index = None
        self.creating_day_index = None
        self.calculation_date_index = None
        self.ok_date_index = None
        self.introduction_date_index = None
        self.dop_inf_index = None

        self.name_index = 0
        self.detail_code_index = 1
        self.machine_index = 2
        self.operation_type_index = 3
        self.op_number_index = 4
        self.dop_inf_index = 5

        self.inf1 = InfoDialog(self, 'Полe "Номер операции" должно быть числом')
        self.inf2 = InfoDialog(self, 'Поля помеченные красным должны быть заполнены')

        self.setup_add_widgets()

    def setup_add_widgets(self):
        """Загрузка виджетов для окна добавления записи"""

        self.setup_standard_dialog_table(self.vertical_headers)
        self.setup_standard_dialog_btn_layout()
        self.setup_standard_dialog_buttons()
        self.setup_standard_dialog_combo_boxes()

    def setup_standard_dialog_table(self, vertical_headers):
        super().setup_standard_dialog_table(vertical_headers)
        self.table.verticalHeaderItem(0).setBackground(self.brush)
        self.table.verticalHeaderItem(1).setBackground(self.brush)
        self.table.verticalHeaderItem(2).setBackground(self.brush)
        self.table.verticalHeaderItem(3).setBackground(self.brush)

    def setup_standard_dialog_buttons(self):
        self.btn_ok = QtWidgets.QPushButton('Добавить', self.horizontalLayoutWidget)
        self.btn_ok.setFont(self.btn_font)
        self.btn_ok.clicked.connect(self.btn_add_func)
        self.horizontalLayout.addWidget(self.btn_ok)
        super().setup_standard_dialog_buttons()

    def btn_add_func(self):
        """Функция кнопки добавления записи"""

        self.request_dict = self.get_data_from_table()

        main_data = [self.request_dict[column_name] for column_name in self.vertical_headers[:4]]

        cond1 = all(i for i in main_data)
        cond2 = (op_number := self.request_dict[self.vertical_headers[self.op_number_index]]) is None \
                or op_number.isdigit() \
                or op_number == ''

        if cond1 and main_data[1].strip():
            if cond2:
                add_new_row(self.request_dict)
                self.close()
                self.main_window.update_data_in_table()
                self.main_window.table.selectRow(self.main_window.table.rowCount() - 1)
            else:
                self.inf1.show()
        else:
            self.inf2.show()


class ChangeDialog(Dialog):
    """Окно изменения записи"""

    def __init__(self, main_window):
        super().__init__(main_window)
        self.setWindowTitle('Изменить запись')
        self.inf = InfoDialog(self, 'Поля "Номер операции" и "Машинное время" должны быть числами')
        self.setup_change_widgets()
        self.flag = True

    def setup_change_widgets(self):
        """Загрузка виджетов для окна изменения записи"""

        self.setup_standard_dialog_table(self.vertical_headers)
        self.setup_standard_dialog_btn_layout()
        self.setup_standard_dialog_buttons()
        self.setup_standard_dialog_combo_boxes()

    def setup_standard_dialog_buttons(self):
        self.btn_ok = QtWidgets.QPushButton('Изменить', self.horizontalLayoutWidget)
        self.btn_ok.setFont(self.btn_font)
        self.btn_ok.clicked.connect(self.btn_change_func)
        self.horizontalLayout.addWidget(self.btn_ok)
        super().setup_standard_dialog_buttons()
        self.btn_clear.deleteLater()

    def update_standard_combo_boxes(self):
        name = self.table.model().index(self.name_index, 0).data()
        machine = self.table.model().index(self.machine_index, 0).data()
        op_type = self.table.model().index(self.operation_type_index, 0).data()
        status = self.table.model().index(self.status_index, 0).data()
        calc_date = self.table.model().index(self.calculation_date_index, 0).data()
        ok_date = self.table.model().index(self.ok_date_index, 0).data()
        intr_date = self.table.model().index(self.introduction_date_index, 0).data()
        self.cmb_engineers.setCurrentText(name)
        self.cmb_machines.setCurrentText(machine)
        self.cmb_statuses.setCurrentText(status)
        self.cmb_operation_types.setCurrentText(op_type)
        self.cmb_calculation_date.setCurrentText(calc_date)
        self.cmb_ok_date.setCurrentText(ok_date)
        self.cmb_introduction_date.setCurrentText(intr_date)
        if self.flag:
            self.cmb_engineers.removeItem(0)
            self.cmb_machines.removeItem(0)
            self.cmb_statuses.removeItem(0)
            self.cmb_operation_types.removeItem(0)
            self.flag = False

    def insert_data_into_table(self):
        """Подгрузка данных из выбранной строки в таблицу окна"""

        if self.main_window.selected_program_number is not None:
            p_num = self.main_window.selected_program_number
            data_for_insert = get_one_row(p_num)

            i = 0
            for key, value in data_for_insert.items():
                if key == 'id':
                    continue
                if isinstance(value, datetime):
                    value = value.strftime("%d.%m.%Y")

                self.table.setItem(i, 0, QTableWidgetItem(value))
                self.table.item(i, 0).setTextAlignment(QtCore.Qt.AlignLeft)
                self.table.item(i, 0).setTextAlignment(QtCore.Qt.AlignBottom)
                if i == self.program_number_index or i == self.creating_day_index:
                    self.table.item(i, 0).setFlags(QtCore.Qt.ItemIsEditable)
                i += 1

    def btn_change_func(self):
        """Функция кнопки изменения записи"""

        self.request_dict = self.get_data_from_table()
        cond1 = (x := self.request_dict[self.vertical_headers[self.op_number_index]].strip()).isdigit() or x == ''
        cond2 = (y := self.request_dict[self.vertical_headers[self.machine_time_index]].strip()).isdigit() or y == ''

        if cond1 and cond2:
            self.change_one_row_in_database(self.request_dict)
            self.close()
            self.main_window.update_data_in_table(self.main_window.request_dict)
        else:
            self.inf.show()

    def change_one_row_in_database(self, data_dict):
        """Изменение записи"""

        p_num = self.main_window.selected_program_number
        for k, v in data_dict.items():
            if not v or k == self.vertical_headers[self.creating_day_index]:
                continue
            if k in (self.vertical_headers[self.calculation_date_index], self.vertical_headers[self.ok_date_index],
                     self.vertical_headers[self.introduction_date_index]):
                v = datetime.strptime(v, "%d.%m.%Y")

            change_data_in_cell(k, v, p_num)

    def showEvent(self, event):
        super().showEvent(event)
        self.insert_data_into_table()
        self.update_standard_combo_boxes()


class SelectDialog(Dialog):
    """Окно выборки"""

    def __init__(self, main_window):
        super().__init__(main_window)
        self.setWindowTitle('Выборка')
        self.inf = InfoDialog(self, 'Хотя бы одно поле должно быть заполнено')
        self.vertical_headers = self.vertical_headers[0:7]
        self.setup_select_widgets()

    def setup_select_widgets(self):
        """Загрузка виджетов для окна выборки"""

        self.setup_standard_dialog_table(self.vertical_headers)
        self.setup_standard_dialog_btn_layout()
        self.setup_standard_dialog_buttons()
        self.setup_standard_dialog_combo_boxes()

    def setup_standard_dialog_buttons(self):
        self.btn_ok = QtWidgets.QPushButton('Выборка', self.horizontalLayoutWidget)
        self.btn_ok.setFont(self.btn_font)
        self.btn_ok.clicked.connect(self.btn_ok_func)
        self.horizontalLayout.addWidget(self.btn_ok)
        super().setup_standard_dialog_buttons()

    def btn_ok_func(self):
        """Функция кнопки выборки"""

        self.request_dict = {k: v for k, v in self.get_data_from_table().items() if bool(v)}
        if self.request_dict:
            self.main_window.update_data_in_table(self.request_dict)
            self.close()
        else:
            self.inf.show()


def log_uncaught_exceptions(ex_cls, ex, tb):
    """Функция для отлова ошибок и вывода текста ошибок в окне"""

    text = f'{ex_cls.__name__}: {ex}:\n' + ''.join(traceback.format_tb(tb))
    QtWidgets.QMessageBox.critical(None, 'Error', text)
    sys.exit()


sys.excepthook = log_uncaught_exceptions

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
