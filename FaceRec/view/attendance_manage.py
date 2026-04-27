from PyQt5 import QtCore, QtWidgets


class Ui_AttendanceManageForm(object):
    def setupUi(self, AttendanceManageForm):
        AttendanceManageForm.setObjectName("AttendanceManageForm")
        AttendanceManageForm.resize(1040, 720)
        AttendanceManageForm.setStyleSheet("background-color: rgb(255, 255, 255);")

        self.verticalLayout = QtWidgets.QVBoxLayout(AttendanceManageForm)
        self.verticalLayout.setContentsMargins(12, 12, 12, 12)
        self.verticalLayout.setSpacing(8)

        self.groupRule = QtWidgets.QGroupBox("考勤规则")
        self.ruleLayout = QtWidgets.QGridLayout(self.groupRule)
        self.ruleLayout.setContentsMargins(10, 12, 10, 10)

        self.lineRuleName = QtWidgets.QLineEdit()
        self.timeStart = QtWidgets.QTimeEdit()
        self.timeEnd = QtWidgets.QTimeEdit()
        self.timeDeadline = QtWidgets.QTimeEdit()
        self.spinLate = QtWidgets.QSpinBox()
        self.spinLate.setRange(0, 180)
        self.spinLate.setValue(10)
        self.comboDedupe = QtWidgets.QComboBox()
        self.comboDedupe.addItems(["student+date+rule"])
        self.btnSaveRule = QtWidgets.QPushButton("保存规则")

        for widget in [self.timeStart, self.timeEnd, self.timeDeadline]:
            widget.setDisplayFormat("HH:mm")

        self.ruleLayout.addWidget(QtWidgets.QLabel("规则名"), 0, 0)
        self.ruleLayout.addWidget(self.lineRuleName, 0, 1)
        self.ruleLayout.addWidget(QtWidgets.QLabel("开始时间"), 0, 2)
        self.ruleLayout.addWidget(self.timeStart, 0, 3)
        self.ruleLayout.addWidget(QtWidgets.QLabel("结束时间"), 0, 4)
        self.ruleLayout.addWidget(self.timeEnd, 0, 5)
        self.ruleLayout.addWidget(QtWidgets.QLabel("缺勤判定时间"), 1, 0)
        self.ruleLayout.addWidget(self.timeDeadline, 1, 1)
        self.ruleLayout.addWidget(QtWidgets.QLabel("迟到阈值(分钟)"), 1, 2)
        self.ruleLayout.addWidget(self.spinLate, 1, 3)
        self.ruleLayout.addWidget(QtWidgets.QLabel("去重范围"), 1, 4)
        self.ruleLayout.addWidget(self.comboDedupe, 1, 5)
        self.ruleLayout.addWidget(self.btnSaveRule, 0, 6, 2, 1)

        self.groupFilter = QtWidgets.QGroupBox("查询与操作")
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
        self.btnExportCsv = QtWidgets.QPushButton("导出CSV")
        self.btnExportExcel = QtWidgets.QPushButton("导出Excel")

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
        self.filterLayout.addWidget(self.btnQuery, 1, 4)
        self.filterLayout.addWidget(self.btnReset, 1, 5)
        self.filterLayout.addWidget(self.btnMakeup, 1, 6)
        self.filterLayout.addWidget(self.btnExportCsv, 1, 7)
        self.filterLayout.addWidget(self.btnExportExcel, 1, 8)

        self.groupStats = QtWidgets.QGroupBox("统计结果")
        self.statsLayout = QtWidgets.QVBoxLayout(self.groupStats)
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
            ["日期", "学号", "姓名", "班级", "状态", "签到时间", "来源", "规则", "备注"]
        )
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout.addWidget(self.groupRule)
        self.verticalLayout.addWidget(self.groupFilter)
        self.verticalLayout.addWidget(self.groupStats)
        self.verticalLayout.addWidget(self.tableWidget, 1)

        self.retranslateUi(AttendanceManageForm)
        QtCore.QMetaObject.connectSlotsByName(AttendanceManageForm)

    def retranslateUi(self, AttendanceManageForm):
        _translate = QtCore.QCoreApplication.translate
        AttendanceManageForm.setWindowTitle(_translate("AttendanceManageForm", "考勤数据管理"))
