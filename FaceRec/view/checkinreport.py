# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CheckInRecordForm(object):
    def setupUi(self, CheckInRecordForm):
        CheckInRecordForm.setObjectName("CheckInRecordForm")
        CheckInRecordForm.resize(800, 600)
        CheckInRecordForm.setStyleSheet("background-color: rgb(255, 255, 255);")

        self.verticalLayout = QtWidgets.QVBoxLayout(CheckInRecordForm)
        self.verticalLayout.setContentsMargins(16, 12, 16, 12)
        self.verticalLayout.setSpacing(10)

        self.groupBox_filter = QtWidgets.QGroupBox(CheckInRecordForm)
        self.groupBox_filter.setTitle("筛选条件")
        self.groupBox_filter.setStyleSheet(
            "QGroupBox {border: 2px solid rgb(69, 90, 100); border-radius:4px; margin-top:6px;}"
            "QGroupBox:title {color:rgb(69, 90, 100); subcontrol-origin: margin; left: 10px;}"
        )
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_filter)
        self.gridLayout.setContentsMargins(12, 16, 12, 10)
        self.gridLayout.setHorizontalSpacing(12)
        self.gridLayout.setVerticalSpacing(8)

        self.label_sid = QtWidgets.QLabel("学号")
        self.label_name = QtWidgets.QLabel("姓名")
        self.label_class = QtWidgets.QLabel("班级")
        self.label_start = QtWidgets.QLabel("开始日期")
        self.label_end = QtWidgets.QLabel("结束日期")

        self.lineEdit_sid = QtWidgets.QLineEdit()
        self.lineEdit_name = QtWidgets.QLineEdit()
        self.comboBox_class = QtWidgets.QComboBox()
        self.comboBox_class.setEditable(False)

        self.dateEdit_start = QtWidgets.QDateEdit()
        self.dateEdit_start.setCalendarPopup(True)
        self.dateEdit_start.setDisplayFormat("yyyy-MM-dd")
        self.dateEdit_end = QtWidgets.QDateEdit()
        self.dateEdit_end.setCalendarPopup(True)
        self.dateEdit_end.setDisplayFormat("yyyy-MM-dd")

        today = QtCore.QDate.currentDate()
        self.dateEdit_start.setDate(today)
        self.dateEdit_end.setDate(today)

        self.pushButton_query = QtWidgets.QPushButton("查询")
        self.pushButton_reset = QtWidgets.QPushButton("重置")
        self.pushButton_export_csv = QtWidgets.QPushButton("导出 CSV")
        self.pushButton_export_excel = QtWidgets.QPushButton("导出 Excel")

        for button in [
            self.pushButton_query,
            self.pushButton_reset,
            self.pushButton_export_csv,
            self.pushButton_export_excel,
        ]:
            button.setStyleSheet(
                "QPushButton {color: rgb(255, 255, 255); border-width: 1px; border-radius: 6px;"
                "border-style: solid; padding: 4px; background-color: rgb(69, 90, 100);}"
                "QPushButton:hover {background-color: rgb(94, 120, 132);}"
                "QPushButton:pressed {background-color: rgb(129, 156, 169);}"
            )

        self.gridLayout.addWidget(self.label_sid, 0, 0)
        self.gridLayout.addWidget(self.lineEdit_sid, 0, 1)
        self.gridLayout.addWidget(self.label_name, 0, 2)
        self.gridLayout.addWidget(self.lineEdit_name, 0, 3)
        self.gridLayout.addWidget(self.label_class, 0, 4)
        self.gridLayout.addWidget(self.comboBox_class, 0, 5)
        self.gridLayout.addWidget(self.label_start, 1, 0)
        self.gridLayout.addWidget(self.dateEdit_start, 1, 1)
        self.gridLayout.addWidget(self.label_end, 1, 2)
        self.gridLayout.addWidget(self.dateEdit_end, 1, 3)
        self.gridLayout.addWidget(self.pushButton_query, 1, 4)
        self.gridLayout.addWidget(self.pushButton_reset, 1, 5)
        self.gridLayout.addWidget(self.pushButton_export_csv, 2, 4)
        self.gridLayout.addWidget(self.pushButton_export_excel, 2, 5)

        self.groupBox_stat = QtWidgets.QGroupBox(CheckInRecordForm)
        self.groupBox_stat.setTitle("统计摘要")
        self.groupBox_stat.setStyleSheet(
            "QGroupBox {border: 2px solid rgb(69, 90, 100); border-radius:4px; margin-top:6px;}"
            "QGroupBox:title {color:rgb(69, 90, 100); subcontrol-origin: margin; left: 10px;}"
        )
        self.statLayout = QtWidgets.QHBoxLayout(self.groupBox_stat)
        self.statLayout.setContentsMargins(12, 10, 12, 10)

        self.label_summary = QtWidgets.QLabel("总学生数: 0  统计天数: 0  应到: 0  实到: 0  缺勤: 0  缺勤率: 0%")
        self.label_summary.setStyleSheet("font-weight: bold; color: rgb(69, 90, 100);")
        self.statLayout.addWidget(self.label_summary)

        self.tableWidget = QtWidgets.QTableWidget(CheckInRecordForm)
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(["学号", "姓名", "班级", "日期", "签到时间", "状态"])
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.setAlternatingRowColors(True)

        self.verticalLayout.addWidget(self.groupBox_filter)
        self.verticalLayout.addWidget(self.groupBox_stat)
        self.verticalLayout.addWidget(self.tableWidget, 1)

        self.retranslateUi(CheckInRecordForm)
        QtCore.QMetaObject.connectSlotsByName(CheckInRecordForm)

    def retranslateUi(self, CheckInRecordForm):
        _translate = QtCore.QCoreApplication.translate
        CheckInRecordForm.setWindowTitle(_translate("CheckInRecordForm", "考勤记录与报表"))
