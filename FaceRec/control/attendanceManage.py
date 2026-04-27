from PyQt5.QtCore import QDate, QTime
from PyQt5.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QWidget,
)

import model.configuration
from model.attendance_service import AttendanceService
from model.connectsqlite import ConnectSqlite
from model.report_service import ReportService
from model.rule_service import RuleService
from view.attendance_manage import Ui_AttendanceManageForm
from view.ui_theme import apply_page_theme, style_button, style_hint_label


class CheckInRecord(QWidget, Ui_AttendanceManageForm):
    def __init__(self, parent=None):
        super(CheckInRecord, self).__init__(parent)
        self.setupUi(self)
        self.dbcon = ConnectSqlite(model.configuration.DATABASE_PATH)
        self.rule_service = RuleService(self.dbcon)
        self.attendance_service = AttendanceService(self.dbcon)
        self.report_service = ReportService(self.attendance_service)

        self.current_rule_id = None
        self._rule_map = {}
        self._is_switching_rule = False

        self._init_ui()
        self._bind_events()
        self._load_classes()
        self._load_rule_list()
        self.query_preview(silent_no_result=True)

    def _init_ui(self):
        self.setWindowTitle("考勤管理")
        apply_page_theme(self)

        self.groupRule.setTitle("考勤规则管理")
        self.groupFilter.setTitle("筛选与导出")
        self.groupStats.setTitle("导出预览")
        self.tableWidget.hide()

        self.lineRuleName.setPlaceholderText("请输入规则名称")
        self.comboDedupe.clear()
        self.comboDedupe.addItems(["student+date+rule"])
        self.lineSid.setPlaceholderText("按学号筛选（支持模糊）")
        self.lineName.setPlaceholderText("按姓名筛选（支持模糊）")
        self.lineCourse.setPlaceholderText("按课程/考勤任务筛选（支持模糊）")
        self.btnMakeup.hide()

        style_button(self.btnSaveRule, "primary")
        style_button(self.btnQuery, "primary")
        style_button(self.btnReset, "default")
        style_button(self.btnExportCsv, "success")
        style_button(self.btnExportExcel, "success")

        style_hint_label(self.labelStudentStats, "info")
        style_hint_label(self.labelClassStats, "info")
        style_hint_label(self.labelRangeSummary, "info")
        style_hint_label(self.labelSummary, "info")
        self.labelStudentStats.setWordWrap(True)
        self.labelClassStats.setWordWrap(True)
        self.labelRangeSummary.setWordWrap(True)
        self.labelSummary.setWordWrap(True)

        self.comboRule = QComboBox(self.groupRule)
        self.btnNewRule = QPushButton("新增规则", self.groupRule)
        self.btnDeleteRule = QPushButton("删除规则", self.groupRule)
        self.btnActivateRule = QPushButton("设为生效规则", self.groupRule)
        self.labelRuleHint = QLabel(
            "提示：选择规则只会加载详情，点击“设为生效规则”后才会生效。",
            self.groupRule,
        )

        style_button(self.btnNewRule, "success")
        style_button(self.btnDeleteRule, "danger")
        style_button(self.btnActivateRule, "warning")
        style_hint_label(self.labelRuleHint, "info")

        layout = self.groupRule.layout()
        if isinstance(layout, QGridLayout):
            layout.addWidget(QLabel("规则选择"), 2, 0)
            layout.addWidget(self.comboRule, 2, 1, 1, 2)
            layout.addWidget(self.btnNewRule, 2, 3)
            layout.addWidget(self.btnDeleteRule, 2, 4)
            layout.addWidget(self.btnActivateRule, 2, 5)
            layout.addWidget(self.labelRuleHint, 3, 0, 1, 7)

    def _bind_events(self):
        self.btnSaveRule.clicked.connect(self.save_rule)
        self.btnNewRule.clicked.connect(self.new_rule)
        self.btnDeleteRule.clicked.connect(self.delete_rule)
        self.btnActivateRule.clicked.connect(self.activate_selected_rule)
        self.comboRule.currentIndexChanged.connect(self.on_rule_selected)
        self.btnQuery.clicked.connect(lambda: self.query_preview(silent_no_result=False))
        self.btnReset.clicked.connect(self.reset_filters)
        self.btnExportCsv.clicked.connect(self.export_csv)
        self.btnExportExcel.clicked.connect(self.export_excel)

    def _load_classes(self):
        self.comboClass.clear()
        self.comboClass.addItem("全部")
        students = self.dbcon.get_face_students()
        classes = sorted({str(x.get("class_name") or "").strip() for x in students})
        for class_name in classes:
            if class_name:
                self.comboClass.addItem(class_name)

    def _load_rule_list(self, prefer_rule_id=None):
        rules = self.rule_service.list_rules()
        if not rules:
            active = self.rule_service.get_active_rule()
            rules = [active] if active else []

        self._rule_map = {int(item.get("id")): item for item in rules if item.get("id") is not None}

        self.comboRule.blockSignals(True)
        self.comboRule.clear()
        active_rule_id = None
        for item in rules:
            rid = item.get("id")
            self.comboRule.addItem(str(item.get("rule_name", "未命名规则")), rid)
            if int(item.get("is_active", 0)) == 1:
                active_rule_id = rid

        target_rule_id = prefer_rule_id if prefer_rule_id is not None else active_rule_id
        if target_rule_id is not None:
            idx = self.comboRule.findData(target_rule_id)
            self.comboRule.setCurrentIndex(max(0, idx))
        elif self.comboRule.count() > 0:
            self.comboRule.setCurrentIndex(0)
        self.comboRule.blockSignals(False)
        self.on_rule_selected(self.comboRule.currentIndex())

    def on_rule_selected(self, _index=None):
        rule_id = self.comboRule.currentData()
        self.current_rule_id = rule_id
        self._load_rule_to_form(rule_id)
        self._refresh_rule_hint()

    def _refresh_rule_hint(self):
        if self.current_rule_id is None:
            self.labelRuleHint.setText("提示：当前无可用规则，请先新增规则。")
            style_hint_label(self.labelRuleHint, "warning")
            return
        item = self._rule_map.get(int(self.current_rule_id), {})
        if int(item.get("is_active", 0)) == 1:
            self.labelRuleHint.setText("提示：当前选择规则已经是生效规则。")
            style_hint_label(self.labelRuleHint, "success")
        else:
            self.labelRuleHint.setText("提示：当前选择规则尚未生效，点击“设为生效规则”后生效。")
            style_hint_label(self.labelRuleHint, "info")

    def _load_rule_to_form(self, rule_id):
        if rule_id is None:
            return
        rule = self.rule_service.get_rule_by_id(rule_id)
        self.lineRuleName.setText(str(rule.get("rule_name", "")))
        self.timeStart.setTime(QTime.fromString(str(rule.get("start_time", "08:00")), "HH:mm"))
        self.timeEnd.setTime(QTime.fromString(str(rule.get("end_time", "10:00")), "HH:mm"))
        self.timeDeadline.setTime(QTime.fromString(str(rule.get("absence_deadline", "10:00")), "HH:mm"))
        self.spinLate.setValue(int(rule.get("late_minutes", 10)))
        dedupe_scope = str(rule.get("dedupe_scope") or "student+date+rule")
        idx = self.comboDedupe.findText(dedupe_scope)
        if idx < 0:
            self.comboDedupe.addItem(dedupe_scope)
            idx = self.comboDedupe.findText(dedupe_scope)
        self.comboDedupe.setCurrentIndex(max(0, idx))

    def _current_filters(self):
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

    def activate_selected_rule(self):
        if self._is_switching_rule:
            return
        rule_id = self.comboRule.currentData()
        if rule_id is None:
            QMessageBox.warning(self, "提示", "请先选择规则。")
            return

        current = self.rule_service.get_active_rule()
        if current and int(current.get("id", 0)) == int(rule_id):
            QMessageBox.information(self, "提示", "该规则已是当前生效规则。")
            self._refresh_rule_hint()
            return

        self._is_switching_rule = True
        self.btnActivateRule.setEnabled(False)
        try:
            activated = self.rule_service.activate_rule(rule_id)
            self._load_rule_list(prefer_rule_id=activated.get("id"))
            QMessageBox.information(self, "成功", f"已切换生效规则：{activated.get('rule_name', '')}")
        except Exception as exc:
            QMessageBox.warning(self, "错误", f"切换规则失败：{exc}")
        finally:
            self._is_switching_rule = False
            self.btnActivateRule.setEnabled(True)

    def switch_rule(self, _index=None):
        self.activate_selected_rule()

    def new_rule(self):
        name, ok = QInputDialog.getText(self, "新增规则", "请输入新规则名称：")
        if not ok:
            return
        rule_name = name.strip()
        if not rule_name:
            QMessageBox.warning(self, "提示", "规则名称不能为空。")
            return
        try:
            created = self.rule_service.create_rule(
                rule_name=rule_name,
                start_time=self.timeStart.time().toString("HH:mm"),
                end_time=self.timeEnd.time().toString("HH:mm"),
                absence_deadline=self.timeDeadline.time().toString("HH:mm"),
                late_minutes=int(self.spinLate.value()),
                dedupe_scope=self.comboDedupe.currentText(),
            )
            self._load_rule_list(prefer_rule_id=created.get("id"))
            QMessageBox.information(self, "成功", "新规则创建成功，请按需点击“设为生效规则”。")
        except Exception as exc:
            QMessageBox.warning(self, "错误", f"创建规则失败：{exc}")

    def save_rule(self):
        if self.current_rule_id is None:
            QMessageBox.warning(self, "提示", "请先选择规则。")
            return
        try:
            self.rule_service.update_rule(
                rule_id=self.current_rule_id,
                rule_name=self.lineRuleName.text().strip(),
                start_time=self.timeStart.time().toString("HH:mm"),
                end_time=self.timeEnd.time().toString("HH:mm"),
                absence_deadline=self.timeDeadline.time().toString("HH:mm"),
                late_minutes=int(self.spinLate.value()),
                dedupe_scope=self.comboDedupe.currentText(),
            )
            self._load_rule_list(prefer_rule_id=self.current_rule_id)
            QMessageBox.information(self, "成功", "规则保存成功。")
        except Exception as exc:
            QMessageBox.warning(self, "错误", f"保存规则失败：{exc}")

    def delete_rule(self):
        rule_id = self.comboRule.currentData()
        rule_name = self.comboRule.currentText()
        if rule_id is None:
            QMessageBox.warning(self, "提示", "请先选择规则。")
            return
        confirm = QMessageBox.question(
            self,
            "确认删除",
            f"确定删除规则“{rule_name}”吗？\n该操作会归档规则，不会删除历史考勤记录。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        try:
            result = self.rule_service.delete_rule(rule_id) or {}
            self._load_rule_list()
            referenced = int(result.get("referenced_records", 0))
            if referenced > 0:
                QMessageBox.information(
                    self,
                    "已归档",
                    f"规则已归档，保留了 {referenced} 条历史考勤记录的关联展示。",
                )
            else:
                QMessageBox.information(self, "成功", "规则删除成功（已归档）。")
        except Exception as exc:
            QMessageBox.warning(self, "错误", f"删除规则失败：{exc}")

    def query_preview(self, silent_no_result=False):
        try:
            filters = self._current_filters()
            rows = self.attendance_service.query_records(**filters)
            stats = self.attendance_service.get_statistics(**filters)
            self._render_preview(rows, stats)
            if not rows and not silent_no_result:
                QMessageBox.information(self, "查询结果", "当前筛选条件下暂无考勤数据。")
        except Exception as exc:
            QMessageBox.warning(self, "错误", f"查询失败：{exc}")

    def _render_preview(self, rows, stats):
        student_stats = stats.get("student", {})
        class_stats = stats.get("class", {})
        overview = stats.get("overview", {})

        self.labelStudentStats.setText(
            "学生统计："
            f"范围 {student_stats.get('scope_desc', '当前筛选学生')}；"
            f"出勤 {student_stats.get('present_count', 0)} 次，"
            f"迟到 {student_stats.get('late_count', 0)} 次，"
            f"缺勤 {student_stats.get('absent_count', 0)} 次，"
            f"补签 {student_stats.get('makeup_count', 0)} 次，"
            f"缺勤率 {student_stats.get('absence_rate_text', '0.00%')}"
        )
        self.labelClassStats.setText(
            "班级统计："
            f"范围 {class_stats.get('class_name', '当前筛选范围')}；"
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
        self.labelSummary.setText(f"当前筛选记录总数：{len(rows)}")

    def reset_filters(self):
        self.lineSid.clear()
        self.lineName.clear()
        self.lineCourse.clear()
        self.comboClass.setCurrentIndex(0)
        today = QDate.currentDate()
        self.dateStart.setDate(today)
        self.dateEnd.setDate(today)
        self.query_preview(silent_no_result=True)

    def refresh_data(self):
        self._load_classes()
        self.query_preview(silent_no_result=True)

    def showEvent(self, event):
        super(CheckInRecord, self).showEvent(event)
        self.refresh_data()

    def export_csv(self):
        self._export_report("csv")

    def export_excel(self):
        self._export_report("xlsx")

    def _export_report(self, ext):
        try:
            filters = self._current_filters()
            detail_rows, stats = self.report_service.build_export_payload(filters)
            if not detail_rows:
                QMessageBox.information(self, "提示", "当前筛选条件下无数据可导出。")
                return

            if ext == "csv":
                title = "导出 CSV 报表"
                file_filter = "CSV 文件 (*.csv)"
            else:
                title = "导出 Excel 报表"
                file_filter = "Excel 文件 (*.xlsx)"
            default_name = self.report_service.default_filename(ext)
            path, _ = QFileDialog.getSaveFileName(self, title, default_name, file_filter)
            if not path:
                return

            if ext == "csv":
                self.report_service.export_csv(path, detail_rows)
            else:
                self.report_service.export_excel(path, detail_rows, stats)

            QMessageBox.information(self, "导出成功", f"报表已导出：\n{path}")
        except Exception as exc:
            QMessageBox.warning(self, "导出失败", f"导出报表失败：{exc}")

    def close_all(self):
        try:
            self.dbcon.close_con()
        except Exception:
            pass
        self.close()
