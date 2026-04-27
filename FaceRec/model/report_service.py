import csv
from datetime import datetime


class ReportService:
    def __init__(self, attendance_service):
        self.attendance_service = attendance_service

    @staticmethod
    def default_filename(ext):
        ts = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        return f"attendance_report_{ts}.{ext}"

    @staticmethod
    def csv_headers():
        return [
            "\u5b66\u53f7",
            "\u59d3\u540d",
            "\u73ed\u7ea7",
            "\u65e5\u671f",
            "\u7b7e\u5230\u65f6\u95f4",
            "\u7b7e\u5230\u72b6\u6001",
            "\u8bb0\u5f55\u6765\u6e90",
            "\u8bfe\u7a0b/\u8003\u52e4\u4efb\u52a1",
            "\u5907\u6ce8",
        ]

    @staticmethod
    def _normalize_row(item):
        course_name = str(item.get("course_name") or "").strip()
        if not course_name:
            task_name = str(item.get("task_name") or "").strip()
            rule_name = str(item.get("rule_name") or "").strip()
            course_name = task_name or rule_name or "\u672a\u8bbe\u7f6e\u8bfe\u7a0b"

        history_note = str(item.get("history_note") or "").strip()
        remark = str(item.get("remark", ""))
        if history_note:
            remark = f"{remark}\uff1b{history_note}" if remark else history_note

        return {
            "student_id": str(item.get("student_id", "")),
            "name": str(item.get("name", "")),
            "class_name": str(item.get("class_name") or ""),
            "attendance_date": str(item.get("attendance_date", "")),
            "checkin_time": str(item.get("checkin_time", "")),
            "attendance_status": str(item.get("attendance_status", "")),
            "record_source": str(item.get("record_source", "")),
            "course_name": course_name,
            "remark": remark,
        }

    def build_export_payload(self, filters):
        rows = self.attendance_service.query_records(**filters)
        stats = self.attendance_service.get_statistics(**filters)
        detail_rows = [self._normalize_row(x) for x in rows]
        return detail_rows, stats

    def export_csv(self, path, detail_rows):
        with open(path, "w", newline="", encoding="utf-8-sig") as file_handle:
            writer = csv.writer(file_handle)
            writer.writerow(self.csv_headers())
            for item in detail_rows:
                writer.writerow(
                    [
                        item["student_id"],
                        item["name"],
                        item["class_name"],
                        item["attendance_date"],
                        item["checkin_time"],
                        item["attendance_status"],
                        item["record_source"],
                        item["course_name"],
                        item["remark"],
                    ]
                )

    def export_excel(self, path, detail_rows, stats):
        try:
            from openpyxl import Workbook
        except ImportError as exc:
            raise RuntimeError("\u7f3a\u5c11 openpyxl \u4f9d\u8d56\u3002") from exc

        student_stats = stats.get("student", {})
        class_stats = stats.get("class", {})
        overview = stats.get("overview", {})

        workbook = Workbook()

        detail_sheet = workbook.active
        detail_sheet.title = "\u8003\u52e4\u660e\u7ec6"
        detail_sheet.append(self.csv_headers())
        for item in detail_rows:
            detail_sheet.append(
                [
                    item["student_id"],
                    item["name"],
                    item["class_name"],
                    item["attendance_date"],
                    item["checkin_time"],
                    item["attendance_status"],
                    item["record_source"],
                    item["course_name"],
                    item["remark"],
                ]
            )

        summary_sheet = workbook.create_sheet("\u7edf\u8ba1\u6c47\u603b")
        summary_sheet.append(["\u7ef4\u5ea6", "\u6307\u6807", "\u503c"])
        summary_sheet.append(["\u5b66\u751f", "\u8303\u56f4", student_stats.get("scope_desc", "")])
        summary_sheet.append(["\u5b66\u751f", "\u51fa\u52e4\u6b21\u6570", student_stats.get("present_count", 0)])
        summary_sheet.append(["\u5b66\u751f", "\u8fdf\u5230\u6b21\u6570", student_stats.get("late_count", 0)])
        summary_sheet.append(["\u5b66\u751f", "\u7f3a\u52e4\u6b21\u6570", student_stats.get("absent_count", 0)])
        summary_sheet.append(["\u5b66\u751f", "\u8865\u7b7e\u6b21\u6570", student_stats.get("makeup_count", 0)])
        summary_sheet.append(["\u5b66\u751f", "\u7f3a\u52e4\u7387", student_stats.get("absence_rate_text", "0.00%")])

        summary_sheet.append(["\u73ed\u7ea7", "\u73ed\u7ea7", class_stats.get("class_name", "\u5f53\u524d\u7b5b\u9009\u8303\u56f4")])
        summary_sheet.append(["\u73ed\u7ea7", "\u603b\u4eba\u6570", class_stats.get("total_students", 0)])
        summary_sheet.append(["\u73ed\u7ea7", "\u51fa\u52e4\u4eba\u6570", class_stats.get("present_students", 0)])
        summary_sheet.append(["\u73ed\u7ea7", "\u8fdf\u5230\u4eba\u6570", class_stats.get("late_students", 0)])
        summary_sheet.append(["\u73ed\u7ea7", "\u7f3a\u52e4\u4eba\u6570", class_stats.get("absent_students", 0)])
        summary_sheet.append(["\u73ed\u7ea7", "\u7f3a\u52e4\u7387", class_stats.get("absence_rate_text", "0.00%")])

        summary_sheet.append(["\u6c47\u603b", "\u7edf\u8ba1\u5929\u6570", overview.get("date_count", 0)])
        summary_sheet.append(["\u6c47\u603b", "\u5e94\u5230\u4eba\u6b21", overview.get("expected_total", 0)])
        summary_sheet.append(["\u6c47\u603b", "\u51fa\u52e4\u4eba\u6b21", overview.get("present_total", 0)])
        summary_sheet.append(["\u6c47\u603b", "\u8fdf\u5230\u4eba\u6b21", overview.get("late_total", 0)])
        summary_sheet.append(["\u6c47\u603b", "\u7f3a\u52e4\u4eba\u6b21", overview.get("absent_total", 0)])
        summary_sheet.append(["\u6c47\u603b", "\u8865\u7b7e\u4eba\u6b21", overview.get("makeup_total", 0)])

        workbook.save(path)
