from datetime import datetime

from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QHeaderView, QLabel, QInputDialog, QMessageBox, QTableWidgetItem, QWidget

import model.configuration
from model.attendance_service import AttendanceService
from model.connectsqlite import ConnectSqlite
from view.record_view import Ui_RecordViewForm
from view.ui_theme import apply_page_theme, style_button, style_hint_label, style_table


class RecordView(QWidget, Ui_RecordViewForm):
    def __init__(self, parent=None):
        super(RecordView, self).__init__(parent)
        self.setupUi(self)
        self.dbcon = ConnectSqlite(model.configuration.DATABASE_PATH)
        self.attendance_service = AttendanceService(self.dbcon)
        self.current_rows = []
        self.current_stats = {}
        self.current_filters = {}

        self._init_ui()
        self._bind_events()
        self._load_classes()
        self.query(silent_no_result=True)

    def _init_ui(self):
        self.setWindowTitle("记录查看")
        apply_page_theme(self)
        style_table(self.tableWidget)

        self.lineSid.setPlaceholderText("按学号筛选（支持模糊）")
        self.lineName.setPlaceholderText("按姓名筛选（支持模糊）")
        self.lineCourse.setPlaceholderText("按课程/考勤任务筛选（支持模糊）")
        style_button(self.btnQuery, "primary")
        style_button(self.btnReset, "default")
        style_button(self.btnMakeup, "success")

        self.tableWidget.setHorizontalHeaderLabels(
            ["日期", "学号", "姓名", "班级", "状态", "签到时间", "来源", "课程/考勤任务", "备注"]
        )

        style_hint_label(self.labelStudentStats, "info")
        style_hint_label(self.labelClassStats, "info")
        style_hint_label(self.labelRangeSummary, "info")
        style_hint_label(self.labelSummary, "info")
        self.labelStudentStats.setWordWrap(True)
        self.labelClassStats.setWordWrap(True)
        self.labelRangeSummary.setWordWrap(True)
        self.labelSummary.setWordWrap(True)

        self.labelCourseTips = QLabel(self.groupStats)
        self.labelCourseTips.setWordWrap(True)
        self.statsLayout.addWidget(self.labelCourseTips)
        style_hint_label(self.labelCourseTips, "warning")

        self._setup_table()

    def _setup_table(self):
        header = self.tableWidget.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setMinimumHeight(40)
        header.setStretchLastSection(True)

        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 日期
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # 学号
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # 姓名
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # 班级
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # 状态
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # 签到时间
        header.setSectionResizeMode(6, QHeaderView.Fixed)  # 来源
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # 课程/考勤任务
        header.setSectionResizeMode(8, QHeaderView.Stretch)  # 备注

        self.tableWidget.setColumnWidth(0, 120)
        self.tableWidget.setColumnWidth(1, 120)
        self.tableWidget.setColumnWidth(2, 110)
        self.tableWidget.setColumnWidth(3, 130)
        self.tableWidget.setColumnWidth(4, 95)
        self.tableWidget.setColumnWidth(5, 170)
        self.tableWidget.setColumnWidth(6, 95)

        self.tableWidget.verticalHeader().setDefaultSectionSize(36)
        self.tableWidget.setWordWrap(False)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setShowGrid(False)
        self.tableWidget.setSortingEnabled(False)
        self.tableWidget.setFont(QFont("Microsoft YaHei", 9))

    def _bind_events(self):
        self.btnQuery.clicked.connect(lambda: self.query(silent_no_result=False))
        self.btnReset.clicked.connect(self.reset_filters)
        self.btnMakeup.clicked.connect(self.manual_makeup)

    def _load_classes(self):
        self.comboClass.clear()
        self.comboClass.addItem("全部")
        students = self.dbcon.get_face_students()
        classes = sorted({str(x.get("class_name") or "").strip() for x in students})
        for class_name in classes:
            if class_name:
                self.comboClass.addItem(class_name)

    def _filters(self):
        start_date = self.dateStart.date().toPyDate()
        end_date = self.dateEnd.date().toPyDate()
        if start_date > end_date:
            raise ValueError("开始日期不能晚于结束日期。")
        return {
            "start_date": start_date,
            "end_date": end_date,
            "sid": self.lineSid.text().strip(),
            "name": self.lineName.text().strip(),
            "class_name": self.comboClass.currentText().strip(),
            "course_keyword": self.lineCourse.text().strip(),
        }

    def query(self, silent_no_result=False):
        try:
            self.current_filters = self._filters()
            self.current_rows = self.attendance_service.query_records(**self.current_filters)
            self.current_stats = self.attendance_service.get_statistics(**self.current_filters)
            self.render_table()
            self.render_statistics()
            self.render_course_tips()
            if not self.current_rows and not silent_no_result:
                QMessageBox.information(self, "查询结果", "当前筛选条件下暂无考勤记录。")
        except Exception as exc:
            QMessageBox.warning(self, "错误", f"查询失败：{exc}")

    def render_table(self):
        self.tableWidget.setRowCount(0)
        for item in self.current_rows:
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)
            history_note = str(item.get("history_note") or "").strip()
            remark = str(item.get("remark") or "").strip()
            if history_note:
                remark = f"{remark}；{history_note}" if remark else history_note
            values = [
                item.get("attendance_date", ""),
                item.get("student_id", ""),
                item.get("name", ""),
                item.get("class_name", ""),
                item.get("attendance_status", ""),
                item.get("checkin_time", ""),
                item.get("record_source", ""),
                item.get("course_name", "未设置课程"),
                remark,
            ]
            for col, value in enumerate(values):
                text = "" if value is None else str(value)
                cell = QTableWidgetItem(text)
                if col == 8:
                    cell.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    cell.setToolTip(text)
                else:
                    cell.setTextAlignment(Qt.AlignCenter)
                if col == 7 and history_note:
                    cell.setToolTip(history_note)
                self.tableWidget.setItem(row, col, cell)

    def render_statistics(self):
        stats = self.current_stats or {}
        student_stats = stats.get("student", {})
        class_stats = stats.get("class", {})
        overview = stats.get("overview", {})

        self.labelStudentStats.setText(
            "学生统计："
            f"{student_stats.get('scope_desc', '当前筛选学生')}；"
            f"出勤 {student_stats.get('present_count', 0)} 次，"
            f"迟到 {student_stats.get('late_count', 0)} 次，"
            f"缺勤 {student_stats.get('absent_count', 0)} 次，"
            f"补签 {student_stats.get('makeup_count', 0)} 次，"
            f"缺勤率 {student_stats.get('absence_rate_text', '0.00%')}"
        )
        self.labelClassStats.setText(
            "班级统计："
            f"{class_stats.get('class_name', '当前筛选范围')}；"
            f"总人数 {class_stats.get('total_students', 0)}，"
            f"出勤人数 {class_stats.get('present_students', 0)}，"
            f"迟到人数 {class_stats.get('late_students', 0)}，"
            f"缺勤人数 {class_stats.get('absent_students', 0)}，"
            f"缺勤率 {class_stats.get('absence_rate_text', '0.00%')}"
        )
        self.labelRangeSummary.setText(
            "汇总信息："
            f"统计天数 {overview.get('date_count', 0)} 天，"
            f"应到人次 {overview.get('expected_total', 0)}，"
            f"出勤人次 {overview.get('present_total', 0)}，"
            f"迟到人次 {overview.get('late_total', 0)}，"
            f"缺勤人次 {overview.get('absent_total', 0)}，"
            f"补签人次 {overview.get('makeup_total', 0)}"
        )
        self.labelSummary.setText(
            f"当前明细：总记录 {len(self.current_rows)}；"
            f"已到 {overview.get('arrive_total', 0)}；"
            f"迟到 {overview.get('late_total', 0)}；"
            f"缺勤 {overview.get('absent_total', 0)}；"
            f"补签 {overview.get('makeup_total', 0)}"
        )

    def render_course_tips(self):
        filters = self.current_filters or {}
        matched_students = self.dbcon.list_students(
            sid=filters.get("sid", ""),
            name=filters.get("name", ""),
            class_name=filters.get("class_name", ""),
        )

        if len(matched_students) != 1:
            self.labelCourseTips.setText(
                "课程提示：请按学号或姓名筛选单个学生后，查看缺勤课程与早退课程清单。"
            )
            style_hint_label(self.labelCourseTips, "warning")
            return

        absent_courses = set()
        early_courses = set()
        for item in self.current_rows:
            status = str(item.get("attendance_status") or "").strip()
            date_text = str(item.get("attendance_date") or "").strip()
            course_name = str(item.get("course_base_name") or item.get("course_name") or "未设置课程").strip() or "未设置课程"
            pair_text = f"{date_text} {course_name}".strip()
            if status == self.attendance_service.STATUS_ABSENT:
                absent_courses.add(pair_text)
            elif status == self.attendance_service.STATUS_EARLY_LEAVE:
                early_courses.add(pair_text)

        absent_text = "、".join(sorted(absent_courses)) if absent_courses else "无"
        early_text = "、".join(sorted(early_courses)) if early_courses else "无"
        self.labelCourseTips.setText(f"课程提示：缺勤课程清单：{absent_text}\n早退课程清单：{early_text}")
        style_hint_label(self.labelCourseTips, "info")

    def _selected_student_id(self):
        selected = self.tableWidget.selectionModel().selectedRows()
        if not selected:
            return ""
        row = selected[0].row()
        item = self.tableWidget.item(row, 1)
        return (item.text() if item else "").strip()

    def manual_makeup(self):
        default_sid = self._selected_student_id() or self.lineSid.text().strip()
        sid, ok = QInputDialog.getText(self, "手动补签", "请输入学号：", text=default_sid)
        if not ok:
            return
        sid = sid.strip()
        if not sid:
            QMessageBox.warning(self, "提示", "学号不能为空。")
            return

        default_date = QDate.currentDate().toString("yyyy-MM-dd")
        date_text, ok = QInputDialog.getText(self, "手动补签", "请输入补签日期（YYYY-MM-DD）：", text=default_date)
        if not ok:
            return
        date_text = date_text.strip()
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError:
            QMessageBox.warning(self, "提示", "日期格式非法，请使用 YYYY-MM-DD。")
            return

        remark, ok = QInputDialog.getText(self, "手动补签", "请输入补签备注（可选）：", text="教师手动补签")
        if not ok:
            return

        try:
            self.attendance_service.manual_makeup(sid, date_text, remark.strip())
            QMessageBox.information(self, "补签成功", "手动补签已写入数据库。")
            self.query(silent_no_result=True)
        except ValueError as exc:
            QMessageBox.warning(self, "补签失败", str(exc))
        except Exception as exc:
            QMessageBox.warning(self, "补签失败", f"数据库写入失败：{exc}")

    def reset_filters(self):
        self.lineSid.clear()
        self.lineName.clear()
        self.lineCourse.clear()
        self.comboClass.setCurrentIndex(0)
        today = QDate.currentDate()
        self.dateStart.setDate(today)
        self.dateEnd.setDate(today)
        self.query(silent_no_result=True)

    def refresh_data(self):
        self._load_classes()
        self.query(silent_no_result=True)

    def showEvent(self, event):
        super(RecordView, self).showEvent(event)
        self.refresh_data()

    def close_all(self):
        try:
            self.dbcon.close_con()
        except Exception:
            pass
        self.close()
