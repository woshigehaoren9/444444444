from view.checkinrecord import *
from view.checkinmodify import *
from PyQt5.QtWidgets import QWidget, QMessageBox, QAbstractItemView, QTableWidgetItem, QLabel, QDialog
from model.connectsqlite import ConnectSqlite
import model.configuration
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class LegacyCheckInRecord(QWidget, Ui_CheckInRecordForm):

    def __init__(self, parent=None):
        super(LegacyCheckInRecord, self).__init__(parent)
        self.setupUi(self)
        self.dbcon = ConnectSqlite(model.configuration.DATABASE_PATH)
        self.checkin_data = []
        self.pushButton_search.clicked.connect(self.search)
        self.pushButton_modify.clicked.connect(self.modify)
        self.pushButton_delete.clicked.connect(self.delete)
        self.make_table()

    def search(self):
        search_str = self.lineEdit_search.text().strip()
        row = 0
        search_result = None
        if search_str != "":
            for i in self.checkin_data:
                if search_str.lower() in str(i[1]).lower():
                    search_result = str(i[1])
                    self.tableWidget.setCurrentIndex(self.tableWidget.model().index(row, 1))
                if search_str.lower() in str(i[0]).lower():
                    search_result = str(i[0])
                    self.tableWidget.setCurrentIndex(self.tableWidget.model().index(row, 0))
                if search_str.lower() in str(i[2]).lower():
                    search_result = str(i[2])
                    self.tableWidget.setCurrentIndex(self.tableWidget.model().index(row, 2))
                row += 1
            if search_result is None:
                QMessageBox.warning(self, "提示", "未找到匹配的信息。", QMessageBox.Yes, QMessageBox.Yes)
        else:
            QMessageBox.warning(self, "提示", "请输入搜索关键词。", QMessageBox.Yes, QMessageBox.Yes)

    def modify(self):
        select = self.tableWidget.selectedItems()
        if len(select) == 0:
            QMessageBox.warning(self, "提示", "请先选择要修改的记录。", QMessageBox.Yes, QMessageBox.Yes)
            return

        row = self.tableWidget.selectedItems()[0].row()
        name = str(self.checkin_data[row][1])
        sid = str(self.checkin_data[row][0])
        checkin_time = str(self.checkin_data[row][2])
        row_id = self.checkin_data[row][-1]
        dialog = CheckInModify([name, sid, checkin_time])
        dialog.exec_()
        modify_list = dialog.getInputs()
        modify_flag = modify_list[1]
        result = self.dbcon.update_checkin_table(modify_list[0], row_id)
        if modify_flag:
            if result == 0:
                self.make_table()
                QMessageBox.information(self, "成功", "修改成功。", QMessageBox.Yes, QMessageBox.Yes)
            else:
                QMessageBox.warning(self, "错误", str(result), QMessageBox.Yes, QMessageBox.Yes)

    def delete(self):
        select = self.tableWidget.selectedItems()
        if len(select) == 0:
            QMessageBox.warning(self, "提示", "请先选择要删除的记录。", QMessageBox.Yes, QMessageBox.Yes)
            return

        row = self.tableWidget.selectedItems()[0].row()
        row_id = self.checkin_data[row][-1]
        result = self.dbcon.delete_checkin_table(row_id)
        if result == 0:
            self.make_table()
            QMessageBox.information(self, "成功", "删除成功。", QMessageBox.Yes, QMessageBox.Yes)
        else:
            QMessageBox.warning(self, "错误", str(result), QMessageBox.Yes, QMessageBox.Yes)

    def make_table(self):
        self.tableWidget.clear()
        self.checkin_data = self.dbcon.return_all_checkin_record()
        data_show = []
        for row in self.checkin_data:
            name = row[1]
            student_id = str(row[0])
            checkin_time = row[2].split(".")[0]
            data_show.append([name, student_id, checkin_time])

        self.RowLength = 0
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setColumnWidth(0, 220)
        self.tableWidget.setColumnWidth(1, 220)
        self.tableWidget.setColumnWidth(2, 300)

        self.tableWidget.setHorizontalHeaderLabels(["姓名", "学号", "签到时间"])
        self.tableWidget.setRowCount(self.RowLength)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.raise_()

        for row_data in data_show:
            self.RowLength += 1
            label = QLabel()
            self.tableWidget.verticalHeader().setDefaultSectionSize(40)
            self.tableWidget.setRowCount(self.RowLength)
            self.tableWidget.setItem(self.RowLength - 1, 0, QTableWidgetItem(row_data[0]))
            self.tableWidget.setItem(self.RowLength - 1, 1, QTableWidgetItem(row_data[1]))
            self.tableWidget.setItem(self.RowLength - 1, 2, QTableWidgetItem(row_data[2]))
            self.tableWidget.item(self.RowLength - 1, 0).setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.tableWidget.item(self.RowLength - 1, 1).setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.tableWidget.item(self.RowLength - 1, 2).setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

    def close_all(self):
        try:
            self.dbcon.close_con()
        except Exception:
            pass
        self.close()


class CheckInModify(QDialog, Ui_Dialog):

    def __init__(self, current_list, parent=None):
        super(CheckInModify, self).__init__(parent)
        self.setupUi(self)
        self.name = current_list[0]
        self.sid = current_list[1]
        self.checkin_time = current_list[2]
        self.lineEdit_sno.setText(self.sid)
        self.lineEdit_name.setText(self.name)
        self.modify_flag = False
        time1 = int(self.checkin_time.split(" ")[1].split(":")[0])
        time2 = int(self.checkin_time.split(" ")[1].split(":")[1])
        time1_format = str("{:0>2d}".format(time1))
        time2_format = str("{:0>2d}".format(time2))
        self.timeEdit_checkin.setTime(QTime.fromString(time1_format + ":" + time2_format))
        self.pushButton_add.clicked.connect(self.modify_return)

    def modify_return(self):
        self.modify_flag = True
        self.close()

    def getInputs(self):
        name = self.lineEdit_name.text()
        sid = self.lineEdit_sno.text()
        checkin_time = self.checkin_time.split(" ")[0] + " " + self.timeEdit_checkin.text()
        return [[name, sid, checkin_time], self.modify_flag]


# 兼容旧入口：统一到新版考勤管理页（attendance_record + attendance_rule + AttendanceService）。
from control.attendanceManage import CheckInRecord  # noqa: E402
