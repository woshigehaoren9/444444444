from datetime import datetime, timedelta


class AttendanceService:
    STATUS_ARRIVE = "\u5df2\u5230"
    STATUS_LATE = "\u8fdf\u5230"
    STATUS_ABSENT = "\u7f3a\u52e4"
    STATUS_MAKEUP = "\u8865\u7b7e"
    STATUS_EARLY_LEAVE = "\u65e9\u9000"

    STATUS_ALIAS = {
        "\u5df2\u5230": "\u5df2\u5230",
        "\u8fdf\u5230": "\u8fdf\u5230",
        "\u7f3a\u52e4": "\u7f3a\u52e4",
        "\u8865\u7b7e": "\u8865\u7b7e",
        "\u65e9\u9000": "\u65e9\u9000",
        "\u5b95\u63d2\u57cc": "\u5df2\u5230",
        "\u6769\u719f\u57cc\u5230": "\u8fdf\u5230",
        "\u7f02\u54c4\u5adf": "\u7f3a\u52e4",
        "\u7425\u886f\ue047\ue797": "\u8865\u7b7e",
    }

    def __init__(self, dbcon):
        self.dbcon = dbcon

    @staticmethod
    def _parse_hhmm(text):
        return datetime.strptime(text, "%H:%M").time()

    @staticmethod
    def _format_rate(numerator, denominator):
        if denominator <= 0:
            return 0.0, "0.00%"
        rate = numerator / denominator
        return rate, f"{rate * 100:.2f}%"

    @staticmethod
    def _date_list(start_date, end_date):
        result = []
        cursor = start_date
        while cursor <= end_date:
            result.append(cursor.strftime("%Y-%m-%d"))
            cursor += timedelta(days=1)
        return result

    @classmethod
    def _normalize_status(cls, status):
        text = str(status or "").strip()
        if text in cls.STATUS_ALIAS:
            return cls.STATUS_ALIAS[text]
        return text or cls.STATUS_ABSENT

    @staticmethod
    def _normalize_class_name(class_name):
        text = str(class_name or "").strip()
        return text

    @staticmethod
    def _is_valid_class_name(class_name):
        text = str(class_name or "").strip()
        if not text:
            return False
        return "未分班" not in text

    def _active_rule(self):
        rule = self.dbcon.get_active_rule()
        if not rule:
            raise RuntimeError("\u672a\u627e\u5230\u53ef\u7528\u8003\u52e4\u89c4\u5219")
        return rule

    def _status_for_checkin(self, now_dt, rule):
        start_time = self._parse_hhmm(rule["start_time"])
        end_time = self._parse_hhmm(rule["end_time"])
        start_dt = datetime.combine(now_dt.date(), start_time)
        end_dt = datetime.combine(now_dt.date(), end_time)
        if now_dt < start_dt or now_dt > end_dt:
            return None
        late_deadline = start_dt + timedelta(minutes=int(rule["late_minutes"]))
        if now_dt <= late_deadline:
            return self.STATUS_ARRIVE
        return self.STATUS_LATE

    def _is_absence_time_reached(self, target_date, now_dt, rule):
        deadline = self._parse_hhmm(rule["absence_deadline"])
        deadline_dt = datetime.combine(target_date, deadline)
        if target_date < now_dt.date():
            return True
        return now_dt >= deadline_dt

    def _filter_students(self, sid="", name="", class_name=""):
        students = []
        for stu in self.dbcon.list_students(sid=sid, name=name, class_name=class_name):
            sid_ok = (not sid) or (sid in str(stu.get("student_id", "")))
            name_ok = (not name) or (name in str(stu.get("name", "")))
            class_text = self._normalize_class_name(stu.get("class_name"))
            class_ok = (not class_name) or (class_name == "\u5168\u90e8") or (class_text == class_name)
            if sid_ok and name_ok and class_ok:
                students.append(
                    {
                        "student_id": str(stu.get("student_id", "")),
                        "name": str(stu.get("name", "")),
                        "class_name": class_text,
                    }
                )
        return students

    def ensure_absence_records(self, start_date, end_date):
        rule = self._active_rule()
        students = self.dbcon.get_face_students()
        now_dt = datetime.now()
        cursor = start_date
        while cursor <= end_date:
            if not self._is_absence_time_reached(cursor, now_dt, rule):
                cursor += timedelta(days=1)
                continue
            date_text = cursor.strftime("%Y-%m-%d")
            for stu in students:
                if not self._is_valid_class_name(stu.get("class_name")):
                    # 班级缺失的学生不自动生成缺勤记录，避免污染正式考勤
                    continue
                exists = self.dbcon.get_attendance_record(stu["student_id"], date_text, rule["id"])
                if exists is None:
                    self.dbcon.insert_attendance_record(
                        attendance_date=date_text,
                        student_id=stu["student_id"],
                        name=stu["name"],
                        class_name=self._normalize_class_name(stu.get("class_name")),
                        checkin_time="",
                        attendance_status=self.STATUS_ABSENT,
                        record_source="system",
                        rule_id=rule["id"],
                        task_name=rule["rule_name"],
                        remark="\u7cfb\u7edf\u6309\u622a\u6b62\u65f6\u95f4\u81ea\u52a8\u6807\u8bb0\u7f3a\u52e4",
                        checkout_time="",
                    )
            cursor += timedelta(days=1)

    def process_auto_checkin(self, student_id, student_name):
        rule = self._active_rule()
        now_dt = datetime.now()
        date_text = now_dt.strftime("%Y-%m-%d")

        student = self.dbcon.get_student_by_sid(student_id)
        if not student:
            student = {
                "student_id": str(student_id),
                "name": student_name,
                "class_name": "",
            }

        if not self._is_valid_class_name(student.get("class_name")):
            return {
                "ok": False,
                "code": "class_missing",
                "message": "学生班级未设置，请先在人脸录入/人脸库管理中补全班级信息。",
                "student_id": str(student.get("student_id", student_id)),
                "name": str(student.get("name", student_name)),
                "class_name": "",
            }

        status = self._status_for_checkin(now_dt, rule)
        if status is None:
            return {
                "ok": False,
                "code": "out_of_window",
                "message": "\u5f53\u524d\u4e0d\u5728\u7b7e\u5230\u65f6\u95f4\u6bb5\u5185",
                "student_id": str(student.get("student_id", student_id)),
                "name": str(student.get("name", student_name)),
                "class_name": self._normalize_class_name(student.get("class_name")),
            }

        exists = self.dbcon.get_attendance_record(student["student_id"], date_text, rule["id"])
        now_text = now_dt.strftime("%Y-%m-%d %H:%M:%S")

        if exists:
            exists_status = self._normalize_status(exists.get("attendance_status"))
            if exists_status in (self.STATUS_ARRIVE, self.STATUS_LATE, self.STATUS_MAKEUP):
                self.dbcon.update_attendance_record(
                    exists["id"],
                    checkin_time=exists["checkin_time"] or now_text,
                    remark="\u91cd\u590d\u8bc6\u522b\u5df2\u53bb\u91cd",
                )
                return {
                    "ok": False,
                    "code": "duplicate",
                    "message": "\u8be5\u5b66\u751f\u4eca\u65e5\u5df2\u7b7e\u5230\uff0c\u5df2\u53bb\u91cd",
                    "status": exists_status,
                    "student_id": str(student.get("student_id", student_id)),
                    "name": str(student.get("name", student_name)),
                    "class_name": self._normalize_class_name(student.get("class_name")),
                }
            if exists_status == self.STATUS_ABSENT:
                self.dbcon.update_attendance_record(
                    exists["id"],
                    attendance_status=self.STATUS_MAKEUP,
                    record_source="auto",
                    checkin_time=now_text,
                    remark="\u7f3a\u52e4\u540e\u81ea\u52a8\u8bc6\u522b\u8865\u7b7e",
                )
                return {
                    "ok": True,
                    "code": "makeup_after_absent",
                    "message": "\u5df2\u4ece\u7f3a\u52e4\u66f4\u65b0\u4e3a\u8865\u7b7e",
                    "status": self.STATUS_MAKEUP,
                    "student_id": str(student.get("student_id", student_id)),
                    "name": str(student.get("name", student_name)),
                    "class_name": self._normalize_class_name(student.get("class_name")),
                }

        inserted = self.dbcon.insert_attendance_record(
            attendance_date=date_text,
            student_id=student["student_id"],
            name=student["name"],
            class_name=self._normalize_class_name(student.get("class_name")),
            checkin_time=now_text,
            attendance_status=status,
            record_source="auto",
            rule_id=rule["id"],
            task_name=rule["rule_name"],
            remark="\u4eba\u8138\u8bc6\u522b\u81ea\u52a8\u7b7e\u5230",
            checkout_time="",
        )
        if not inserted:
            # 极短时间并发写入导致唯一键已存在时，按重复签到处理
            latest = self.dbcon.get_attendance_record(student["student_id"], date_text, rule["id"])
            latest_status = self._normalize_status((latest or {}).get("attendance_status"))
            return {
                "ok": False,
                "code": "duplicate",
                "message": "该学生今日已签到，已去重",
                "status": latest_status or status,
                "student_id": str(student.get("student_id", student_id)),
                "name": str(student.get("name", student_name)),
                "class_name": self._normalize_class_name(student.get("class_name")),
            }
        return {
            "ok": True,
            "code": "success",
            "message": "\u7b7e\u5230\u6210\u529f",
            "status": status,
            "student_id": str(student.get("student_id", student_id)),
            "name": str(student.get("name", student_name)),
            "class_name": self._normalize_class_name(student.get("class_name")),
        }

    def manual_makeup(self, student_id, attendance_date, remark):
        rule = self._active_rule()
        student = self.dbcon.get_student_by_sid(student_id)
        if not student:
            raise ValueError("\u5b66\u751f\u4e0d\u5b58\u5728\uff0c\u8bf7\u5148\u5f55\u5165\u4eba\u8138\u6570\u636e")
        if not self._is_valid_class_name(student.get("class_name")):
            raise ValueError("学生班级未设置，无法补签。请先补全班级信息。")

        now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        exists = self.dbcon.get_attendance_record(student["student_id"], attendance_date, rule["id"])
        if exists:
            self.dbcon.update_attendance_record(
                exists["id"],
                attendance_status=self.STATUS_MAKEUP,
                record_source="manual",
                checkin_time=now_text,
                remark=remark or "\u6559\u5e08\u624b\u52a8\u8865\u7b7e",
            )
        else:
            self.dbcon.insert_attendance_record(
                attendance_date=attendance_date,
                student_id=student["student_id"],
                name=student["name"],
                class_name=self._normalize_class_name(student.get("class_name")),
                checkin_time=now_text,
                attendance_status=self.STATUS_MAKEUP,
                record_source="manual",
                rule_id=rule["id"],
                task_name=rule["rule_name"],
                remark=remark or "\u6559\u5e08\u624b\u52a8\u8865\u7b7e",
                checkout_time="",
            )

    def process_checkout(self, student_id, student_name=""):
        rule = self._active_rule()
        now_dt = datetime.now()
        date_text = now_dt.strftime("%Y-%m-%d")
        now_text = now_dt.strftime("%Y-%m-%d %H:%M:%S")

        student = self.dbcon.get_student_by_sid(student_id)
        if not student:
            student = {
                "student_id": str(student_id),
                "name": student_name or "",
                "class_name": "",
            }
        if not self._is_valid_class_name(student.get("class_name")):
            return {
                "ok": False,
                "code": "class_missing",
                "message": "学生班级未设置，无法签退。请先补全班级信息。",
                "student_id": str(student.get("student_id", student_id)),
                "name": str(student.get("name", student_name)),
                "class_name": "",
                "checkout_time": "",
            }

        exists = self.dbcon.get_attendance_record(student["student_id"], date_text, rule["id"])
        if not exists:
            return {
                "ok": False,
                "code": "no_checkin",
                "message": "\u672a\u627e\u5230\u4eca\u65e5\u7b7e\u5230\u8bb0\u5f55\uff0c\u8bf7\u5148\u7b7e\u5230\u518d\u7b7e\u9000\u3002",
                "student_id": str(student.get("student_id", student_id)),
                "name": str(student.get("name", student_name)),
                "class_name": self._normalize_class_name(student.get("class_name")),
                "checkout_time": "",
            }

        exists_status = self._normalize_status(exists.get("attendance_status"))
        if exists_status == self.STATUS_ABSENT or not exists.get("checkin_time"):
            return {
                "ok": False,
                "code": "no_checkin",
                "message": "\u8be5\u5b66\u751f\u4eca\u65e5\u672a\u7b7e\u5230\uff0c\u4e0d\u53ef\u7b7e\u9000\u3002",
                "status": exists_status,
                "student_id": str(student.get("student_id", student_id)),
                "name": str(student.get("name", student_name)),
                "class_name": self._normalize_class_name(student.get("class_name")),
                "checkout_time": "",
            }

        if exists.get("checkout_time"):
            return {
                "ok": False,
                "code": "duplicate_checkout",
                "message": f"\u8be5\u5b66\u751f\u5df2\u7b7e\u9000\uff0c\u7b7e\u9000\u65f6\u95f4\uff1a{exists.get('checkout_time')}",
                "status": exists_status,
                "student_id": str(student.get("student_id", student_id)),
                "name": str(student.get("name", student_name)),
                "class_name": self._normalize_class_name(student.get("class_name")),
                "checkout_time": exists.get("checkout_time"),
            }

        end_dt = datetime.combine(now_dt.date(), self._parse_hhmm(rule["end_time"]))
        if now_dt < end_dt:
            final_status = self.STATUS_EARLY_LEAVE
            code = "early_leave"
            message = "\u7b7e\u9000\u6210\u529f\uff0c\u5df2\u5224\u5b9a\u4e3a\u65e9\u9000\u3002"
            remark = "\u5728\u8bfe\u7a0b\u7ed3\u675f\u65f6\u95f4\u524d\u7b7e\u9000\uff0c\u5224\u5b9a\u65e9\u9000"
        else:
            final_status = exists_status
            code = "success"
            message = "\u7b7e\u9000\u6210\u529f\u3002"
            remark = "\u4eba\u8138\u8bc6\u522b\u7b7e\u9000"

        self.dbcon.update_attendance_checkout(
            exists["id"],
            checkout_time=now_text,
            attendance_status=final_status,
            remark=remark,
        )

        return {
            "ok": True,
            "code": code,
            "message": message,
            "status": final_status,
            "student_id": str(student.get("student_id", student_id)),
            "name": str(student.get("name", student_name)),
            "class_name": self._normalize_class_name(student.get("class_name")),
            "checkout_time": now_text,
        }

    def query_records(self, start_date, end_date, sid="", name="", class_name="", course_keyword=""):
        self.ensure_absence_records(start_date, end_date)
        rows = self.dbcon.list_attendance_records(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            sid=sid,
            name=name,
            class_name=class_name,
            course_keyword=course_keyword,
        )
        for item in rows:
            item["attendance_status"] = self._normalize_status(item.get("attendance_status"))
            item["class_name"] = self._normalize_class_name(item.get("class_name"))
            task_name = str(item.get("task_name") or "").strip()
            rule_name = str(item.get("rule_name") or "").strip()
            course_base_name = task_name or rule_name or "未设置课程"
            rule_missing = bool(item.get("rule_missing", 0))
            rule_deleted = bool(item.get("rule_deleted", 0))

            history_note = ""
            if rule_missing:
                history_note = "历史规则已删除"
                course_name = f"{course_base_name}（历史规则已删除）"
            elif rule_deleted:
                history_note = "规则已归档"
                course_name = f"{course_base_name}（规则已归档）"
            elif task_name and rule_name and task_name != rule_name:
                history_note = f"历史快照，当前规则名：{rule_name}"
                course_name = f"{task_name}（历史快照，当前规则：{rule_name}）"
            else:
                course_name = course_base_name

            item["course_base_name"] = course_base_name
            item["course_name"] = course_name
            item["history_note"] = history_note
        return rows

    def get_statistics(self, start_date, end_date, sid="", name="", class_name="", course_keyword=""):
        self.ensure_absence_records(start_date, end_date)

        date_keys = self._date_list(start_date, end_date)
        date_count = len(date_keys)
        students = self._filter_students(sid=sid, name=name, class_name=class_name)
        records = self.dbcon.list_attendance_records(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            sid=sid,
            name=name,
            class_name=class_name,
            course_keyword=course_keyword,
        )

        precedence = {
            self.STATUS_ABSENT: 1,
            self.STATUS_ARRIVE: 2,
            self.STATUS_LATE: 3,
            self.STATUS_MAKEUP: 4,
            self.STATUS_EARLY_LEAVE: 5,
        }
        status_map = {}
        for item in records:
            key = (str(item.get("student_id", "")), item.get("attendance_date", ""))
            old_status = status_map.get(key)
            new_status = self._normalize_status(item.get("attendance_status"))
            if old_status is None or precedence.get(new_status, 0) >= precedence.get(old_status, 0):
                status_map[key] = new_status

        per_student = {}
        for stu in students:
            stu_id = stu["student_id"]
            stat = {
                "student_id": stu_id,
                "name": stu["name"],
                "class_name": self._normalize_class_name(stu["class_name"]),
                "expected_count": date_count,
                "arrive_count": 0,
                "late_count": 0,
                "absent_count": 0,
                "makeup_count": 0,
                "early_leave_count": 0,
                "present_count": 0,
            }
            for day in date_keys:
                status = status_map.get((stu_id, day), self.STATUS_ABSENT)
                if status == self.STATUS_ARRIVE:
                    stat["arrive_count"] += 1
                    stat["present_count"] += 1
                elif status == self.STATUS_LATE:
                    stat["late_count"] += 1
                    stat["present_count"] += 1
                elif status == self.STATUS_MAKEUP:
                    stat["makeup_count"] += 1
                    stat["present_count"] += 1
                elif status == self.STATUS_EARLY_LEAVE:
                    stat["early_leave_count"] += 1
                    stat["present_count"] += 1
                else:
                    stat["absent_count"] += 1
            rate, rate_text = self._format_rate(stat["absent_count"], stat["expected_count"])
            stat["absence_rate"] = rate
            stat["absence_rate_text"] = rate_text
            per_student[stu_id] = stat

        expected_total = sum(x["expected_count"] for x in per_student.values())
        arrive_total = sum(x["arrive_count"] for x in per_student.values())
        late_total = sum(x["late_count"] for x in per_student.values())
        absent_total = sum(x["absent_count"] for x in per_student.values())
        makeup_total = sum(x["makeup_count"] for x in per_student.values())
        early_leave_total = sum(x["early_leave_count"] for x in per_student.values())
        present_total = sum(x["present_count"] for x in per_student.values())

        present_students = sum(1 for x in per_student.values() if x["present_count"] > 0)
        late_students = sum(1 for x in per_student.values() if x["late_count"] > 0)
        absent_students = sum(1 for x in per_student.values() if x["absent_count"] > 0)
        class_rate, class_rate_text = self._format_rate(absent_total, expected_total)

        if len(students) == 1:
            only = next(iter(per_student.values()))
            student_scope = {
                "scope_desc": f"{only['student_id']} {only['name']}",
                "present_count": only["present_count"],
                "late_count": only["late_count"],
                "absent_count": only["absent_count"],
                "makeup_count": only["makeup_count"],
                "early_leave_count": only["early_leave_count"],
                "absence_rate": only["absence_rate"],
                "absence_rate_text": only["absence_rate_text"],
            }
        else:
            student_rate, student_rate_text = self._format_rate(absent_total, expected_total)
            student_scope = {
                "scope_desc": f"\u5f53\u524d\u7b5b\u9009\u5171 {len(students)} \u540d\u5b66\u751f",
                "present_count": present_total,
                "late_count": late_total,
                "absent_count": absent_total,
                "makeup_count": makeup_total,
                "early_leave_count": early_leave_total,
                "absence_rate": student_rate,
                "absence_rate_text": student_rate_text,
            }

        class_scope_name = class_name if class_name and class_name != "\u5168\u90e8" else "\u5f53\u524d\u7b5b\u9009\u8303\u56f4"
        class_scope = {
            "class_name": class_scope_name,
            "total_students": len(students),
            "present_students": present_students,
            "late_students": late_students,
            "absent_students": absent_students,
            "absence_rate": class_rate,
            "absence_rate_text": class_rate_text,
            "expected_total": expected_total,
            "absent_total": absent_total,
        }

        overview_rate, overview_rate_text = self._format_rate(absent_total, expected_total)
        overview = {
            "date_count": date_count,
            "record_count": len(records),
            "expected_total": expected_total,
            "arrive_total": arrive_total,
            "present_total": present_total,
            "late_total": late_total,
            "absent_total": absent_total,
            "makeup_total": makeup_total,
            "early_leave_total": early_leave_total,
            "absence_rate": overview_rate,
            "absence_rate_text": overview_rate_text,
        }

        return {
            "student": student_scope,
            "class": class_scope,
            "overview": overview,
        }
