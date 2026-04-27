from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem, QWidget

import model.configuration
from model.connectsqlite import ConnectSqlite
from model.report_service import ReportService
from view.checkinreport import Ui_CheckInRecordForm


class CheckInRecord(QWidget, Ui_CheckInRecordForm):
    def __init__(self, parent=None):
        super(CheckInRecord, self).__init__(parent)
        self.setupUi(self)

        self.dbcon = ConnectSqlite(model.configuration.DATABASE_PATH)
        self.report_service = ReportService(self.dbcon)
        self.current_rows = []
        self.current_student_stats = []
        self.current_class_stats = []
        self.current_overview = {}

        self.pushButton_query.clicked.connect(self.query)
        self.pushButton_reset.clicked.connect(self.reset_filters)
        self.pushButton_export_csv.clicked.connect(self.export_csv)
        self.pushButton_export_excel.clicked.connect(self.export_excel)

        self._load_class_filters()
        self.query()

    def _load_class_filters(self):
        self.comboBox_class.clear()
        self.comboBox_class.addItem("全部")
        for item in self.report_service.get_classes():
            self.comboBox_class.addItem(item)

    def _get_filters(self):
        return {
            "sid": self.lineEdit_sid.text().strip(),
            "name": self.lineEdit_name.text().strip(),
            "class_name": self.comboBox_class.currentText().strip(),
            "start_date": self.dateEdit_start.date().toPyDate(),
            "end_date": self.dateEdit_end.date().toPyDate(),
        }

    def query(self):
        try:
            result = self.report_service.query_attendance(**self._get_filters())
        except ValueError as exc:
            QMessageBox.warning(self, "错误", str(exc), QMessageBox.Yes, QMessageBox.Yes)
            return
        except Exception as exc:
            QMessageBox.warning(self, "错误", f"查询失败: {exc}", QMessageBox.Yes, QMessageBox.Yes)
            return

        self.current_rows = result["rows"]
        self.current_student_stats = result["student_stats"]
        self.current_class_stats = result["class_stats"]
        self.current_overview = result["overview"]

        self._render_table()
        self._render_summary()

        if not self.current_rows:
            QMessageBox.information(self, "提示", "当前筛选条件下没有数据。", QMessageBox.Yes, QMessageBox.Yes)

    def _render_table(self):
        self.tableWidget.setRowCount(0)
        for item in self.current_rows:
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)
            values = [
                item["student_id"],
                item["name"],
                item["class_name"],
                item["date"],
                item["checkin_time"],
                item["status"],
            ]
            for col, value in enumerate(values):
                cell = QTableWidgetItem(str(value))
                cell.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.tableWidget.setItem(row, col, cell)

    def _render_summary(self):
        summary = self.current_overview or {
            "student_count": 0,
            "date_count": 0,
            "should_count": 0,
            "present_count": 0,
            "absent_count": 0,
            "absent_rate": 0.0,
        }
        text = (
            f"总学生数: {summary['student_count']}  "
            f"统计天数: {summary['date_count']}  "
            f"应到: {summary['should_count']}  "
            f"实到: {summary['present_count']}  "
            f"缺勤: {summary['absent_count']}  "
            f"缺勤率: {summary['absent_rate']}%"
        )
        self.label_summary.setText(text)

    def reset_filters(self):
        self.lineEdit_sid.clear()
        self.lineEdit_name.clear()
        self.comboBox_class.setCurrentIndex(0)
        today = datetime.now().date()
        self.dateEdit_start.setDate(today)
        self.dateEdit_end.setDate(today)
        self.query()

    def export_csv(self):
        if not self.current_rows:
            QMessageBox.warning(self, "错误", "没有可导出的明细数据。", QMessageBox.Yes, QMessageBox.Yes)
            return
        default_name = f"attendance_report_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv"
        path, _ = QFileDialog.getSaveFileName(self, "导出 CSV 报表", default_name, "CSV Files (*.csv)")
        if not path:
            return
        try:
            self.report_service.export_csv(path, self.current_rows)
            QMessageBox.information(self, "成功", f"CSV 导出成功:\n{path}", QMessageBox.Yes, QMessageBox.Yes)
        except Exception as exc:
            QMessageBox.warning(self, "错误", f"CSV 导出失败: {exc}", QMessageBox.Yes, QMessageBox.Yes)

    def export_excel(self):
        if not self.current_rows:
            QMessageBox.warning(self, "错误", "没有可导出的明细数据。", QMessageBox.Yes, QMessageBox.Yes)
            return
        default_name = f"attendance_report_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.xlsx"
        path, _ = QFileDialog.getSaveFileName(self, "导出 Excel 报表", default_name, "Excel Files (*.xlsx)")
        if not path:
            return
        try:
            self.report_service.export_excel(
                path,
                self.current_rows,
                self.current_student_stats,
                self.current_class_stats,
                self.current_overview,
            )
            QMessageBox.information(self, "成功", f"Excel 导出成功:\n{path}", QMessageBox.Yes, QMessageBox.Yes)
        except Exception as exc:
            QMessageBox.warning(self, "错误", f"Excel 导出失败: {exc}", QMessageBox.Yes, QMessageBox.Yes)

    def close_all(self):
        try:
            self.dbcon.close_con()
        except Exception:
            pass
        self.close()
