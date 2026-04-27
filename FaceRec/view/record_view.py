# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets


class Ui_RecordViewForm(object):
    def setupUi(self, RecordViewForm):
        RecordViewForm.setObjectName("RecordViewForm")
        RecordViewForm.resize(1180, 760)
        RecordViewForm.setStyleSheet("background-color: rgb(255, 255, 255);")

        self.verticalLayout = QtWidgets.QVBoxLayout(RecordViewForm)
        self.verticalLayout.setContentsMargins(12, 12, 12, 12)
        self.verticalLayout.setSpacing(8)

        self.groupFilter = QtWidgets.QGroupBox("查询筛选")
        self.filterLayout = QtWidgets.QGridLayout(self.groupFilter)
        self.filterLayout.setContentsMargins(10, 12, 10, 10)

        self.lineSid = QtWidgets.QLineEdit()
        self.lineName = QtWidgets.QLineEdit()
        self.comboClass = QtWidgets.QComboBox()
        self.lineCourse = QtWidgets.QLineEdit()
        self.dateStart = QtWidgets.QDateEdit()
        self.dateEnd = QtWidgets.QDateEdit()
        self.dateStart.setCalendarPopup(True)
        self.dateEnd.setCalendarPopup(True)
        self.dateStart.setDisplayFormat("yyyy-MM-dd")
        self.dateEnd.setDisplayFormat("yyyy-MM-dd")
        today = QtCore.QDate.currentDate()
        self.dateStart.setDate(today)
        self.dateEnd.setDate(today)

        self.btnQuery = QtWidgets.QPushButton("查询")
        self.btnReset = QtWidgets.QPushButton("重置")
        self.btnMakeup = QtWidgets.QPushButton("手动补签")

        self.filterLayout.addWidget(QtWidgets.QLabel("学号"), 0, 0)
        self.filterLayout.addWidget(self.lineSid, 0, 1)
        self.filterLayout.addWidget(QtWidgets.QLabel("姓名"), 0, 2)
        self.filterLayout.addWidget(self.lineName, 0, 3)
        self.filterLayout.addWidget(QtWidgets.QLabel("班级"), 0, 4)
        self.filterLayout.addWidget(self.comboClass, 0, 5)
        self.filterLayout.addWidget(QtWidgets.QLabel("课程/考勤任务"), 0, 6)
        self.filterLayout.addWidget(self.lineCourse, 0, 7)

        self.filterLayout.addWidget(QtWidgets.QLabel("开始日期"), 1, 0)
        self.filterLayout.addWidget(self.dateStart, 1, 1)
        self.filterLayout.addWidget(QtWidgets.QLabel("结束日期"), 1, 2)
        self.filterLayout.addWidget(self.dateEnd, 1, 3)
        self.filterLayout.addWidget(self.btnQuery, 1, 5)
        self.filterLayout.addWidget(self.btnReset, 1, 6)
        self.filterLayout.addWidget(self.btnMakeup, 1, 7)

        self.groupStats = QtWidgets.QGroupBox("统计结果")
        self.statsLayout = QtWidgets.QVBoxLayout(self.groupStats)
        self.statsLayout.setContentsMargins(10, 10, 10, 10)
        self.statsLayout.setSpacing(8)
        self.labelStudentStats = QtWidgets.QLabel("学生统计：")
        self.labelClassStats = QtWidgets.QLabel("班级统计：")
        self.labelRangeSummary = QtWidgets.QLabel("汇总信息：")
        self.labelSummary = QtWidgets.QLabel("当前明细：总记录 0，已到 0，迟到 0，缺勤 0，补签 0")
        self.statsLayout.addWidget(self.labelStudentStats)
        self.statsLayout.addWidget(self.labelClassStats)
        self.statsLayout.addWidget(self.labelRangeSummary)
        self.statsLayout.addWidget(self.labelSummary)

        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setColumnCount(9)
        self.tableWidget.setHorizontalHeaderLabels(
            ["日期", "学号", "姓名", "班级", "状态", "签到时间", "来源", "课程/考勤任务", "备注"]
        )
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout.addWidget(self.groupFilter)
        self.verticalLayout.addWidget(self.groupStats)
        self.verticalLayout.addWidget(self.tableWidget, 1)
        self.verticalLayout.setStretch(0, 0)
        self.verticalLayout.setStretch(1, 0)
        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(RecordViewForm)
        QtCore.QMetaObject.connectSlotsByName(RecordViewForm)

    def retranslateUi(self, RecordViewForm):
        _translate = QtCore.QCoreApplication.translate
        RecordViewForm.setWindowTitle(_translate("RecordViewForm", "记录查看"))
