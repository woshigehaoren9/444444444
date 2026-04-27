from datetime import datetime


class RuleService:
    def __init__(self, dbcon):
        self.dbcon = dbcon

    @staticmethod
    def _validate_time_text(value):
        datetime.strptime(value, "%H:%M")

    def _validate_common(self, rule_name, start_time, end_time, absence_deadline, late_minutes):
        self._validate_time_text(start_time)
        self._validate_time_text(end_time)
        self._validate_time_text(absence_deadline)

        late_minutes = int(late_minutes)
        if late_minutes < 0:
            raise ValueError("迟到阈值不能小于 0。")
        if not str(rule_name or "").strip():
            raise ValueError("规则名称不能为空。")
        return late_minutes

    def list_rules(self):
        return self.dbcon.list_rules() or []

    def get_active_rule(self):
        rule = self.dbcon.get_active_rule()
        if rule:
            return rule
        return {
            "id": 0,
            "rule_name": "默认考勤策略",
            "start_time": "08:00",
            "end_time": "10:00",
            "absence_deadline": "10:00",
            "late_minutes": 10,
            "dedupe_scope": "student+date+rule",
            "is_active": 1,
            "is_deleted": 0,
        }

    def get_rule_by_id(self, rule_id):
        rule = self.dbcon.get_rule_by_id(rule_id)
        if not rule or int(rule.get("is_deleted", 0)) == 1:
            raise ValueError("规则不存在。")
        return rule

    def create_rule(self, rule_name, start_time, end_time, absence_deadline, late_minutes, dedupe_scope):
        late_minutes = self._validate_common(rule_name, start_time, end_time, absence_deadline, late_minutes)
        target_name = rule_name.strip()
        existing_names = {str(x.get("rule_name", "")).strip() for x in self.list_rules()}
        if target_name in existing_names:
            raise ValueError("规则名称已存在，请使用其他名称。")
        return self.dbcon.create_rule(
            rule_name=target_name,
            start_time=start_time,
            end_time=end_time,
            absence_deadline=absence_deadline,
            late_minutes=late_minutes,
            dedupe_scope=dedupe_scope or "student+date+rule",
            is_active=0,
        )

    def update_rule(self, rule_id, rule_name, start_time, end_time, absence_deadline, late_minutes, dedupe_scope):
        late_minutes = self._validate_common(rule_name, start_time, end_time, absence_deadline, late_minutes)
        target_name = rule_name.strip()

        for item in self.list_rules():
            if int(item.get("id", 0)) != int(rule_id) and str(item.get("rule_name", "")).strip() == target_name:
                raise ValueError("规则名称已存在，请使用其他名称。")

        return self.dbcon.update_rule(
            rule_id=rule_id,
            rule_name=target_name,
            start_time=start_time,
            end_time=end_time,
            absence_deadline=absence_deadline,
            late_minutes=late_minutes,
            dedupe_scope=dedupe_scope or "student+date+rule",
        )

    def activate_rule(self, rule_id):
        return self.dbcon.activate_rule(rule_id)

    def delete_rule(self, rule_id):
        return self.dbcon.delete_rule(rule_id)

    def save_rule(self, rule_name, start_time, end_time, absence_deadline, late_minutes, dedupe_scope):
        # 向后兼容旧调用：保存时新增一条并设为激活
        late_minutes = self._validate_common(rule_name, start_time, end_time, absence_deadline, late_minutes)
        return self.dbcon.save_active_rule(
            rule_name.strip(),
            start_time,
            end_time,
            absence_deadline,
            late_minutes,
            dedupe_scope or "student+date+rule",
        )
