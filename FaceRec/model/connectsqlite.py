import sys
import os
import sqlite3
import time

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
sys.path.append("..")


class ConnectSqlite:

    def __init__(self, dbName):
        """
        初始化连接--使用完记得关闭连接
        :param dbName: 连接库名字，注意，以'.db'结尾
        """
        self._db_name = dbName
        self._conn = sqlite3.connect(self._db_name, timeout=20)
        self._cur = self._conn.cursor()
        self._time_now = "[" + sqlite3.datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + "]"
        self._setup_sqlite_runtime()
        self._ensure_schema()
        self._ensure_attendance_schema()
        self._migrate_legacy_checkin_records()

    def _reopen_connection(self):
        try:
            if getattr(self, "_cur", None) is not None:
                self._cur.close()
        except Exception:
            pass
        try:
            if getattr(self, "_conn", None) is not None:
                self._conn.close()
        except Exception:
            pass
        self._conn = sqlite3.connect(self._db_name, timeout=20)
        self._cur = self._conn.cursor()

    def _setup_sqlite_runtime(self):
        """配置 SQLite 运行参数，尽量降低并发写锁冲突。"""
        # 说明：
        # 1) 该项目历史环境中部分磁盘/解释器组合对 WAL 支持不稳定，会触发 disk I/O error。
        # 2) 默认走 DELETE + busy_timeout，确保稳定；如需 WAL，可显式设置环境变量开启。
        enable_wal = str(os.environ.get("FACEREC_SQLITE_ENABLE_WAL", "0")).strip().lower() in {"1", "true", "yes"}
        if enable_wal:
            try:
                row = self._cur.execute("PRAGMA journal_mode=WAL;").fetchone()
                if not (row and str(row[0]).lower() == "wal"):
                    raise RuntimeError(f"journal_mode={row}")
            except Exception as e:
                print(self._time_now, "[SQLITE RUNTIME WARN] WAL 不可用，已回退：", e)
                self._reopen_connection()
                try:
                    self._cur.execute("PRAGMA journal_mode=DELETE;")
                except Exception:
                    pass
        else:
            try:
                self._cur.execute("PRAGMA journal_mode=DELETE;")
            except Exception:
                pass
        try:
            self._cur.execute("PRAGMA busy_timeout=20000;")
        except Exception:
            pass
        try:
            self._cur.execute("PRAGMA synchronous=NORMAL;")
        except Exception:
            pass
        try:
            # 统一开启外键，避免孤儿数据继续扩大。
            self._cur.execute("PRAGMA foreign_keys=ON;")
        except Exception:
            pass
        try:
            self._conn.commit()
        except Exception:
            pass

    def _run_write_with_retry(self, fn, retries=4, base_delay=0.08):
        """
        对写操作做轻量重试，缓解短时锁冲突。
        fn: 不带参数的写操作闭包。
        """
        last_exc = None
        for idx in range(max(1, retries)):
            try:
                result = fn()
                self._conn.commit()
                return result
            except sqlite3.OperationalError as exc:
                last_exc = exc
                msg = str(exc).lower()
                try:
                    self._conn.rollback()
                except Exception:
                    pass
                if "locked" not in msg or idx >= retries - 1:
                    raise
                time.sleep(base_delay * (2 ** idx))
            except Exception:
                try:
                    self._conn.rollback()
                except Exception:
                    pass
                raise
        if last_exc:
            raise last_exc

    def _ensure_schema(self):
        """Keep database backward-compatible with newer features."""
        try:
            columns = self._cur.execute("PRAGMA table_info(face_data);").fetchall()
            column_names = [item[1] for item in columns]
            if "class_name" not in column_names:
                # 只补字段，不再自动回填“未分班”，避免持续制造脏数据
                self._cur.execute("ALTER TABLE face_data ADD COLUMN class_name TEXT DEFAULT '';")
            self._conn.commit()
        except Exception as e:
            print(self._time_now, "[SCHEMA MIGRATION ERROR]", e)

    def _ensure_attendance_schema(self):
        try:
            self._cur.execute(
                """
                CREATE TABLE IF NOT EXISTS attendance_rule (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    absence_deadline TEXT NOT NULL,
                    late_minutes INTEGER NOT NULL DEFAULT 10,
                    dedupe_scope TEXT NOT NULL DEFAULT 'student+date+rule',
                    is_active INTEGER NOT NULL DEFAULT 1,
                    is_deleted INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT,
                    updated_at TEXT
                );
                """
            )
            self._cur.execute(
                """
                CREATE TABLE IF NOT EXISTS attendance_record (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    attendance_date TEXT NOT NULL,
                    student_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    class_name TEXT DEFAULT '',
                    checkin_time TEXT,
                    checkout_time TEXT,
                    attendance_status TEXT NOT NULL,
                    record_source TEXT NOT NULL,
                    task_name TEXT,
                    rule_id INTEGER NOT NULL,
                    remark TEXT,
                    created_at TEXT,
                    updated_at TEXT
                );
                """
            )
            self._cur.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_attendance_unique
                ON attendance_record(student_id, attendance_date, rule_id);
                """
            )
            columns = self._cur.execute("PRAGMA table_info(attendance_rule);").fetchall()
            column_names = {item[1] for item in columns}
            if "is_deleted" not in column_names:
                self._cur.execute("ALTER TABLE attendance_rule ADD COLUMN is_deleted INTEGER NOT NULL DEFAULT 0;")
            self._cur.execute("UPDATE attendance_rule SET is_deleted=0 WHERE is_deleted IS NULL;")

            count = self._cur.execute(
                "SELECT COUNT(*) FROM attendance_rule WHERE COALESCE(is_deleted, 0)=0;"
            ).fetchone()[0]
            if count == 0:
                now_text = sqlite3.datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self._cur.execute(
                    """
                    INSERT INTO attendance_rule
                    (rule_name, start_time, end_time, absence_deadline, late_minutes, dedupe_scope, is_active, is_deleted, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, 1, 0, ?, ?);
                    """,
                    ("默认考勤策略", "08:00", "10:00", "10:00", 10, "student+date+rule", now_text, now_text),
                )
            self._conn.commit()
        except Exception as e:
            print(self._time_now, "[ATTENDANCE SCHEMA ERROR]", e)

    def _table_exists(self, table_name):
        row = self._cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
            (table_name,),
        ).fetchone()
        return row is not None

    @staticmethod
    def _normalize_date_text(time_text):
        if not time_text:
            return sqlite3.datetime.datetime.now().strftime('%Y-%m-%d')
        raw = str(time_text).strip()
        for fmt in ("%Y/%m/%d %H:%M", "%Y/%m/%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
            try:
                return sqlite3.datetime.datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
            except Exception:
                pass
        return raw.replace("/", "-").split(" ")[0]

    def _migrate_legacy_checkin_records(self):
        """将旧 re_record 数据迁移到 attendance_record，避免新旧链路分裂。"""
        try:
            if not self._table_exists("re_record"):
                return
            rule = self.get_active_rule()
            if not rule:
                return

            rows = self._cur.execute(
                "SELECT id, student_id, name, checkin_time FROM re_record ORDER BY id ASC;"
            ).fetchall()
            migrated = 0
            for _, student_id, name, checkin_time in rows:
                sid = str(student_id)
                date_text = self._normalize_date_text(checkin_time)
                exists = self.get_attendance_record(sid, date_text, rule["id"])
                if exists:
                    continue
                stu = self.get_student_by_sid(sid)
                class_name = str((stu or {}).get("class_name") or "").strip()
                if not class_name:
                    # 旧数据迁移时没有班级则跳过，不写入脏记录
                    continue
                self.insert_attendance_record(
                    attendance_date=date_text,
                    student_id=sid,
                    name=name or (stu or {}).get("name") or "",
                    class_name=class_name,
                    checkin_time=str(checkin_time or ""),
                    attendance_status="已到",
                    record_source="legacy",
                    rule_id=rule["id"],
                    task_name=rule["rule_name"],
                    remark="旧签到记录迁移",
                    checkout_time="",
                )
                migrated += 1
            if migrated:
                print(self._time_now, f"[LEGACY MIGRATION] re_record -> attendance_record: {migrated}")
        except Exception as e:
            try:
                self._conn.rollback()
            except Exception:
                pass
            print(self._time_now, "[LEGACY MIGRATION ERROR]", e)

    def close_con(self):
        """
        关闭连接对象--主动调用
        :return:
        """
        try:
            if getattr(self, "_cur", None) is not None:
                self._cur.close()
        except Exception:
            pass
        try:
            if getattr(self, "_conn", None) is not None:
                self._conn.close()
        except Exception:
            pass

    def create_tabel(self, sql):
        """
        创建表初始化
        :param sql: 建表语句
        :return: True is ok
        """
        try:
            self._cur.execute(sql)
            self._conn.commit()
            return True
        except Exception as e:
            print(self._time_now, "[CREATE TABLE ERROR]", e)
            return False

    def drop_table(self, table_name):
        """
        删除表
        :param table_name: 表名
        :return:
        """
        try:
            self._cur.execute('DROP TABLE {0}'.format(table_name))
            self._conn.commit()
            return True
        except Exception as e:
            print(self._time_now, "[DROP TABLE ERROR]", e)
            return False

    def fetchall_table(self, sql, limit_flag=True):
        """
        查询所有数据
        :param sql:
        :param limit_flag: 查询条数选择，False 查询一条，True 全部查询
        :return:
        """
        try:
            self._cur.execute(sql)
            if limit_flag is True:
                r = self._cur.fetchall()
                return r if r else []
            elif limit_flag is False:
                r = self._cur.fetchone()
                return r if r is not None else None
        except Exception as e:
            print(self._time_now, "[SELECT TABLE ERROR]", e)
            return [] if limit_flag else None

    def insert_facedata_table(self, insert_list):
        """
        插入/更新表记录
        :param insert_list:
        :return:0 or err
        """
        try:
            # 兼容摄像头录入和图片导入：尽量将人脸图像存为JPG二进制
            # 注意：这里使用惰性导入，避免数据库模块在缺少opencv/numpy环境下无法加载
            if len(insert_list) >= 3 and insert_list[2] is not None:
                try:
                    import numpy as _np
                    import cv2 as _cv2
                    if isinstance(insert_list[2], _np.ndarray):
                        ok, buf = _cv2.imencode(".jpg", insert_list[2])
                        if ok:
                            insert_list[2] = buf.tobytes()
                except Exception:
                    # 编码失败时回退到原始写入，保证主流程可用
                    pass
            sql = "INSERT INTO face_data (id,name,face_data,face_img,change_time,student_id,class_name) values (NULL,?,?,?,?,?,?);"
            print(sql)
            self._cur.execute(sql,insert_list)
            self._conn.commit()
            return 0
        except Exception as e:
            err = self._time_now + "[INSERT/UPDATE TABLE ERROR]"+ str(e)
            print(err)
            return err

    def sid_exists(self, student_id):
        row = self._cur.execute(
            "SELECT 1 FROM face_data WHERE student_id=? LIMIT 1;",
            (str(student_id),),
        ).fetchone()
        return row is not None

    def insert_face_record(self, student_id, name, class_name, face_fingerprint, face_img):
        change_time = sqlite3.datetime.datetime.now()
        face_data = str(face_fingerprint)
        insert_list = [
            str(name),
            face_data,
            face_img,
            change_time,
            str(student_id),
            class_name or "",
        ]
        return self.insert_facedata_table(insert_list)

    def insert_checkin_table(self, insert_list):
        """
        插入/更新表记录
        :param insert_list:
        :return:0 or err
        """
        try:
            # 兼容旧接口：优先写入新版 attendance_record。
            sid = str(insert_list[0])
            name = str(insert_list[1])
            checkin_time = str(insert_list[2]) if len(insert_list) > 2 else ""
            rule = self.get_active_rule()
            if not rule:
                return self._time_now + "[INSERT/UPDATE TABLE ERROR]未找到有效考勤规则"
            attendance_date = self._normalize_date_text(checkin_time)
            exists = self.get_attendance_record(sid, attendance_date, rule["id"])
            if exists:
                return 0
            stu = self.get_student_by_sid(sid)
            class_name = str((stu or {}).get("class_name") or "").strip()
            if not class_name:
                return self._time_now + "[INSERT/UPDATE TABLE ERROR]学生班级为空，已拒绝写入考勤记录"
            self.insert_attendance_record(
                attendance_date=attendance_date,
                student_id=sid,
                name=name or (stu or {}).get("name") or "",
                class_name=class_name,
                checkin_time=checkin_time,
                attendance_status="已到",
                record_source="legacy",
                rule_id=rule["id"],
                task_name=rule["rule_name"],
                remark="旧接口写入",
                checkout_time="",
            )
            return 0
        except Exception as e:
            err = self._time_now + "[INSERT/UPDATE TABLE ERROR]" + str(e)
            print(err)
            return err

    def return_all_face(self):
        sql = """SELECT * FROM face_data;"""

        face_data = self.fetchall_table(sql)
        if not isinstance(face_data, list):
            return []
        face_list = []
        for i in face_data:
            face_list.append(i)
        return face_list

    def return_all_checkin_record(self):
        # 兼容旧页面格式：[student_id, name, checkin_time, id]
        rows = self.list_attendance_records()
        check_list = []
        for item in rows:
            check_list.append(
                [
                    str(item.get("student_id", "")),
                    str(item.get("name", "")),
                    str(item.get("checkin_time", "")),
                    item.get("id"),
                ]
            )
        return check_list

    def return_all_sid(self):
        sql = """SELECT student_id FROM face_data;"""

        student_id = self.fetchall_table(sql)
        if not isinstance(student_id, list):
            return []
        id_list = []
        for i in student_id:
            id_list.append(str(i[0]))
        return id_list

    def return_face_photo(self):
        sql = """SELECT face_img FROM face_data;"""

        face_img = self.fetchall_table(sql)
        if not isinstance(face_img, list):
            return []
        face_list = []
        for i in face_img:
            face_list.append(i[0])
        return face_list

    def insert_table_many(self, sql, value):
        """
        插入多条记录
        :param sql:
        :param value: list:[(),()]
        :return:
        """
        try:
            self._cur.executemany(sql, value)
            self._conn.commit()
            return True
        except Exception as e:
            print(self._time_now, "[INSERT MANY TABLE ERROR]", e)
        return False

    # 载入已录入信息的函数
    def load_registered_data(self):

        sql = """SELECT student_id,name,face_data FROM face_data;"""

        info = self.fetchall_table(sql)
        if not isinstance(info, list):
            return []
        student_info_all = []
        for i in info:
            try:
                face_data = list(map(float, str(i[2]).split('\n')))
                if len(face_data) != 128:
                    continue
                student_info = {'sid': i[0], 'name': i[1], 'feature': face_data}
                student_info_all.append(student_info)
            except Exception:
                continue
        return student_info_all

    def insert_update_table(self, sql):
        """
        插入/更新表记录
        :param sql:
        :return:
        """
        try:
            self._cur.execute(sql)
            self._conn.commit()
            return 0
        except Exception as e:
            err = self._time_now + "[INSERT/UPDATE TABLE ERROR]" + str(e)
            print(err)
            return err

    def update_face_table(self,modify_list):
        print(modify_list)
        if len(modify_list) >= 4:
            sql_update = "UPDATE face_data SET student_id='{0}',name='{1}',class_name='{2}' WHERE id={3}".format(
                modify_list[0], modify_list[1], modify_list[2], modify_list[3]
            )
        else:
            sql_update = "UPDATE face_data SET student_id='{0}',name='{1}' WHERE id={2}".format(
                modify_list[0], modify_list[1], modify_list[2]
            )
        print(sql_update)
        return self.insert_update_table(sql_update)

    def _status_priority(self, status_text):
        text = str(status_text or "").strip()
        return {"早退": 5, "补签": 4, "迟到": 3, "已到": 2, "缺勤": 1}.get(text, 0)

    def _source_priority(self, source_text):
        text = str(source_text or "").strip().lower()
        if text == "manual":
            return 3
        if text in {"auto", "system"}:
            return 2
        return 1

    @staticmethod
    def _earlier_time(time_a, time_b):
        a = str(time_a or "").strip()
        b = str(time_b or "").strip()
        if not a:
            return b
        if not b:
            return a
        return a if a <= b else b

    @staticmethod
    def _later_time(time_a, time_b):
        a = str(time_a or "").strip()
        b = str(time_b or "").strip()
        if not a:
            return b
        if not b:
            return a
        return a if a >= b else b

    @staticmethod
    def _merge_remark(remark_a, remark_b):
        raw_parts = []
        for item in (remark_a, remark_b):
            text = str(item or "").strip()
            if text:
                raw_parts.extend(text.replace("；", ";").replace("\n", ";").split(";"))
        seen = set()
        merged = []
        for item in raw_parts:
            token = item.strip()
            if not token or token in seen:
                continue
            seen.add(token)
            merged.append(token)
        return "；".join(merged)

    def _find_sid_conflicts(self, old_sid, new_sid):
        return self._cur.execute(
            """
            SELECT
                a.id, a.attendance_date, a.rule_id, a.attendance_status, a.checkin_time, a.checkout_time, a.record_source, a.remark,
                b.id, b.attendance_status, b.checkin_time, b.checkout_time, b.record_source, b.remark
            FROM attendance_record a
            INNER JOIN attendance_record b
                ON a.student_id = ?
               AND b.student_id = ?
               AND a.attendance_date = b.attendance_date
               AND a.rule_id = b.rule_id
            ORDER BY a.attendance_date DESC, a.rule_id ASC;
            """,
            (old_sid, new_sid),
        ).fetchall()

    def merge_student_history_sid(self, old_sid, new_sid, prefer_profile=True):
        """
        将 old_sid 历史考勤并入 new_sid，并自动合并同日同规则冲突记录。
        """
        old_sid = str(old_sid).strip()
        new_sid = str(new_sid).strip()
        if not old_sid:
            raise ValueError("原学号不能为空。")
        if not new_sid:
            raise ValueError("新学号不能为空。")
        if old_sid == new_sid:
            return {"old_sid": old_sid, "new_sid": new_sid, "merged_conflicts": 0, "moved_rows": 0}

        old_profile = self.get_student_by_sid(old_sid)
        new_profile = self.get_student_by_sid(new_sid)
        if not old_profile and not new_profile:
            raise ValueError("原学号与目标学号均不存在，无法并档。")

        conflict_rows = self._find_sid_conflicts(old_sid, new_sid)
        now_text = sqlite3.datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if prefer_profile and new_profile:
            canonical_name = str(new_profile.get("name") or "").strip()
            canonical_class = str(new_profile.get("class_name") or "").strip()
        elif old_profile:
            canonical_name = str(old_profile.get("name") or "").strip()
            canonical_class = str(old_profile.get("class_name") or "").strip()
        elif new_profile:
            canonical_name = str(new_profile.get("name") or "").strip()
            canonical_class = str(new_profile.get("class_name") or "").strip()
        else:
            canonical_name = ""
            canonical_class = ""

        def _write():
            for row in conflict_rows:
                old_id, _, _, old_status, old_in, old_out, old_src, old_remark, new_id, new_status, new_in, new_out, new_src, new_remark = row
                keep_old = self._status_priority(old_status) >= self._status_priority(new_status)

                keep_id = old_id if keep_old else new_id
                drop_id = new_id if keep_old else old_id
                merged_status = old_status if keep_old else new_status
                merged_checkin = self._earlier_time(old_in, new_in)
                merged_checkout = self._later_time(old_out, new_out)
                merged_source = old_src if self._source_priority(old_src) >= self._source_priority(new_src) else new_src
                merged_remark = self._merge_remark(old_remark, new_remark)

                self._cur.execute(
                    """
                    UPDATE attendance_record
                    SET attendance_status=?, checkin_time=?, checkout_time=?, record_source=?, remark=?, updated_at=?
                    WHERE id=?;
                    """,
                    (
                        str(merged_status or "").strip(),
                        merged_checkin,
                        merged_checkout,
                        str(merged_source or "").strip(),
                        merged_remark,
                        now_text,
                        int(keep_id),
                    ),
                )
                self._cur.execute("DELETE FROM attendance_record WHERE id=?;", (int(drop_id),))

            self._cur.execute(
                """
                UPDATE attendance_record
                SET student_id=?, updated_at=?
                WHERE student_id=?;
                """,
                (new_sid, now_text, old_sid),
            )

            if canonical_name or canonical_class:
                self._cur.execute(
                    """
                    UPDATE attendance_record
                    SET name=CASE WHEN ?<>'' THEN ? ELSE name END,
                        class_name=CASE WHEN ?<>'' THEN ? ELSE class_name END,
                        updated_at=?
                    WHERE student_id=?;
                    """,
                    (canonical_name, canonical_name, canonical_class, canonical_class, now_text, new_sid),
                )

            # 兼容旧签到表：同步学号与姓名
            if self._table_exists("re_record"):
                if canonical_name:
                    self._cur.execute(
                        """
                        UPDATE re_record
                        SET student_id=?, name=?
                        WHERE student_id=?;
                        """,
                        (new_sid, canonical_name, old_sid),
                    )
                    self._cur.execute(
                        "UPDATE re_record SET name=? WHERE student_id=?;",
                        (canonical_name, new_sid),
                    )
                else:
                    self._cur.execute(
                        "UPDATE re_record SET student_id=? WHERE student_id=?;",
                        (new_sid, old_sid),
                    )

            if old_profile and new_profile:
                if not prefer_profile:
                    self._cur.execute(
                        """
                        UPDATE face_data
                        SET name=?, class_name=?, change_time=?
                        WHERE student_id=?;
                        """,
                        (canonical_name, canonical_class, now_text, new_sid),
                    )
                self._cur.execute("DELETE FROM face_data WHERE student_id=?;", (old_sid,))
            elif old_profile and not new_profile:
                self._cur.execute(
                    """
                    UPDATE face_data
                    SET student_id=?, name=?, class_name=?, change_time=?
                    WHERE student_id=?;
                    """,
                    (new_sid, canonical_name or old_profile.get("name", ""), canonical_class or old_profile.get("class_name", ""), now_text, old_sid),
                )

        moved_before = self._cur.execute(
            "SELECT COUNT(*) FROM attendance_record WHERE student_id=?;",
            (old_sid,),
        ).fetchone()[0]

        self._run_write_with_retry(_write)
        return {
            "old_sid": old_sid,
            "new_sid": new_sid,
            "merged_conflicts": len(conflict_rows),
            "moved_rows": int(moved_before),
            "canonical_name": canonical_name,
            "canonical_class_name": canonical_class,
        }

    def update_student_profile_and_sync(self, old_student_id, new_student_id, new_name, new_class_name, allow_merge_conflict=False):
        """
        同步更新学生主档与历史考勤快照。
        """
        old_sid = str(old_student_id).strip()
        new_sid = str(new_student_id).strip()
        new_name = str(new_name).strip()
        new_class_name = str(new_class_name or "").strip()

        if not old_sid:
            raise ValueError("原学号不能为空。")
        if not new_sid:
            raise ValueError("新学号不能为空。")
        if not new_name:
            raise ValueError("姓名不能为空。")
        if not new_class_name:
            raise ValueError("班级不能为空。")

        old_profile = self.get_student_by_sid(old_sid)
        new_profile = self.get_student_by_sid(new_sid)
        old_profile_exists = old_profile is not None

        old_att_count = self._cur.execute(
            "SELECT COUNT(*) FROM attendance_record WHERE student_id=?;",
            (old_sid,),
        ).fetchone()[0]
        old_re_count = 0
        if self._table_exists("re_record"):
            old_re_count = self._cur.execute(
                "SELECT COUNT(*) FROM re_record WHERE student_id=?;",
                (old_sid,),
            ).fetchone()[0]

        if not old_profile_exists and int(old_att_count) <= 0 and int(old_re_count) <= 0:
            raise ValueError("未找到对应学生记录。")
        if not old_profile_exists and new_profile is None:
            raise ValueError("旧学号仅存在历史数据，且目标学号主档不存在，无法同步。")

        if old_profile_exists:
            sid_conflict = self._cur.execute(
                "SELECT id FROM face_data WHERE student_id=? AND student_id<>? LIMIT 1;",
                (new_sid, old_sid),
            ).fetchone()
            if sid_conflict:
                raise ValueError("新学号已存在，请使用其他学号。")

        conflict_rows = []
        if new_sid != old_sid:
            conflict_rows = self._find_sid_conflicts(old_sid, new_sid)
            if conflict_rows and not allow_merge_conflict:
                first = conflict_rows[0]
                raise ValueError(
                    f"[历史考勤冲突] 目标学号在历史考勤中已存在同日期同规则记录，例如 日期 {first[1]} / 规则ID {first[2]}。"
                )

        merged_count = 0
        if conflict_rows and allow_merge_conflict:
            merge_result = self.merge_student_history_sid(old_sid, new_sid, prefer_profile=True)
            merged_count = int((merge_result or {}).get("merged_conflicts", 0))

        now_text = sqlite3.datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        def _write():
            self._cur.execute(
                """
                UPDATE face_data
                SET student_id=?, name=?, class_name=?, change_time=?
                WHERE student_id=?;
                """,
                (new_sid, new_name, new_class_name, now_text, new_sid),
            )
            self._cur.execute(
                """
                UPDATE attendance_record
                SET name=?, class_name=?, updated_at=?
                WHERE student_id=?;
                """,
                (new_name, new_class_name, now_text, new_sid),
            )

        if not (conflict_rows and allow_merge_conflict):
            def _write_direct():
                if old_profile_exists:
                    self._cur.execute(
                        """
                        UPDATE face_data
                        SET student_id=?, name=?, class_name=?, change_time=?
                        WHERE student_id=?;
                        """,
                        (new_sid, new_name, new_class_name, now_text, old_sid),
                    )
                else:
                    self._cur.execute(
                        """
                        UPDATE face_data
                        SET name=?, class_name=?, change_time=?
                        WHERE student_id=?;
                        """,
                        (new_name, new_class_name, now_text, new_sid),
                    )
                self._cur.execute(
                    """
                    UPDATE attendance_record
                    SET student_id=?, name=?, class_name=?, updated_at=?
                    WHERE student_id=?;
                    """,
                    (new_sid, new_name, new_class_name, now_text, old_sid),
                )
                if self._table_exists("re_record"):
                    self._cur.execute(
                        """
                        UPDATE re_record
                        SET student_id=?, name=?
                        WHERE student_id=?;
                        """,
                        (new_sid, new_name, old_sid),
                    )
            self._run_write_with_retry(_write_direct)
        else:
            self._run_write_with_retry(_write)

        return {
            "old_student_id": old_sid,
            "new_student_id": new_sid,
            "name": new_name,
            "class_name": new_class_name,
            "merged_conflicts": merged_count,
        }

    def sync_student_profile_everywhere(self, old_sid, new_sid, new_name, new_class_name, auto_merge_conflict=True):
        """
        主档驱动全链路同步：
        - face_data
        - attendance_record
        - re_record(若存在)
        """
        old_sid = str(old_sid).strip()
        new_sid = str(new_sid).strip()
        new_name = str(new_name).strip()
        new_class_name = str(new_class_name or "").strip()

        before_old_att = self._cur.execute(
            "SELECT COUNT(*) FROM attendance_record WHERE student_id=?;",
            (old_sid,),
        ).fetchone()[0]
        before_new_att = self._cur.execute(
            "SELECT COUNT(*) FROM attendance_record WHERE student_id=?;",
            (new_sid,),
        ).fetchone()[0]

        before_old_re = 0
        before_new_re = 0
        if self._table_exists("re_record"):
            before_old_re = self._cur.execute(
                "SELECT COUNT(*) FROM re_record WHERE student_id=?;",
                (old_sid,),
            ).fetchone()[0]
            before_new_re = self._cur.execute(
                "SELECT COUNT(*) FROM re_record WHERE student_id=?;",
                (new_sid,),
            ).fetchone()[0]

        result = self.update_student_profile_and_sync(
            old_student_id=old_sid,
            new_student_id=new_sid,
            new_name=new_name,
            new_class_name=new_class_name,
            allow_merge_conflict=bool(auto_merge_conflict),
        ) or {}

        now_text = sqlite3.datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        def _write():
            if self._table_exists("re_record"):
                self._cur.execute(
                    """
                    UPDATE re_record
                    SET student_id=?, name=?
                    WHERE student_id=?;
                    """,
                    (new_sid, new_name, old_sid),
                )
                self._cur.execute(
                    "UPDATE re_record SET name=? WHERE student_id=?;",
                    (new_name, new_sid),
                )
            self._cur.execute(
                """
                UPDATE attendance_record
                SET name=?, class_name=?, updated_at=?
                WHERE student_id=?;
                """,
                (new_name, new_class_name, now_text, new_sid),
            )

        self._run_write_with_retry(_write)

        after_old_att = self._cur.execute(
            "SELECT COUNT(*) FROM attendance_record WHERE student_id=?;",
            (old_sid,),
        ).fetchone()[0]
        after_new_att = self._cur.execute(
            "SELECT COUNT(*) FROM attendance_record WHERE student_id=?;",
            (new_sid,),
        ).fetchone()[0]

        after_old_re = 0
        after_new_re = 0
        if self._table_exists("re_record"):
            after_old_re = self._cur.execute(
                "SELECT COUNT(*) FROM re_record WHERE student_id=?;",
                (old_sid,),
            ).fetchone()[0]
            after_new_re = self._cur.execute(
                "SELECT COUNT(*) FROM re_record WHERE student_id=?;",
                (new_sid,),
            ).fetchone()[0]

        return {
            "old_student_id": old_sid,
            "new_student_id": new_sid,
            "name": new_name,
            "class_name": new_class_name,
            "merged_conflicts": int(result.get("merged_conflicts", 0)),
            "before_attendance_old": int(before_old_att),
            "before_attendance_new": int(before_new_att),
            "after_attendance_old": int(after_old_att),
            "after_attendance_new": int(after_new_att),
            "before_re_record_old": int(before_old_re),
            "before_re_record_new": int(before_new_re),
            "after_re_record_old": int(after_old_re),
            "after_re_record_new": int(after_new_re),
            "updated_total_rows": int(before_old_att + before_old_re),
        }

    def update_checkin_table(self, modify_list,id):
        print(modify_list)
        try:
            row = self._cur.execute(
                "SELECT id FROM attendance_record WHERE id=? LIMIT 1;",
                (int(id),),
            ).fetchone()
            if row:
                self._cur.execute(
                    """
                    UPDATE attendance_record
                    SET name=?, student_id=?, checkin_time=?, updated_at=?
                    WHERE id=?;
                    """,
                    (
                        str(modify_list[0]),
                        str(modify_list[1]),
                        str(modify_list[2]),
                        sqlite3.datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        int(id),
                    ),
                )
                self._conn.commit()
                return 0
        except Exception as e:
            err = self._time_now + "[INSERT/UPDATE TABLE ERROR]" + str(e)
            print(err)
            return err

        sql_update = "UPDATE re_record SET name='{0}',student_id='{1}',checkin_time='{2}' WHERE id={3}".format(modify_list[0], modify_list[1], modify_list[2], id)
        print(sql_update)
        return self.insert_update_table(sql_update)

    def delete_table(self, sql):
        """
        删除表记录
        :param sql:
        :return: True or False
        """
        try:
            if 'DELETE' in sql.upper():
                self._cur.execute(sql)
                self._conn.commit()
                return 0
            else:
                err = self._time_now + "[EXECUTE SQL IS NOT DELETE]"
                return err
        except Exception as e:
            err = self._time_now + "[DELETE TABLE ERROR]" + str(e)
            return err

    def delete_face_table(self,id):
        sql = "DELETE FROM face_data WHERE id='{0}';".format(id)
        return self.delete_table(sql)

    def delete_student_keep_attendance(self, student_id):
        """
        只删除 face_data 学生主档，保留 attendance_record 历史流水。
        """
        sid = str(student_id).strip()
        if not sid:
            raise ValueError("学号不能为空。")

        exists = self._cur.execute(
            "SELECT id FROM face_data WHERE student_id=? LIMIT 1;",
            (sid,),
        ).fetchone()
        if not exists:
            raise ValueError("学生不存在或已删除。")

        def _write():
            self._cur.execute("DELETE FROM face_data WHERE student_id=?;", (sid,))

        self._run_write_with_retry(_write)
        return {"student_id": sid}

    def delete_checkin_table(self,id):
        try:
            self._cur.execute("DELETE FROM attendance_record WHERE id=?;", (int(id),))
            self._conn.commit()
            if self._cur.rowcount > 0:
                return 0
        except Exception:
            pass
        sql = "DELETE FROM re_record WHERE id='{0}';".format(id)
        print(sql)
        return self.delete_table(sql)

    def get_face_students(self):
        sql = "SELECT id, student_id, name, class_name, change_time FROM face_data;"
        rows = self.fetchall_table(sql)
        if not isinstance(rows, list):
            return []
        students = []
        for item in rows:
            students.append(
                {
                    "id": item[0],
                    "student_id": str(item[1]),
                    "name": str(item[2]),
                    "class_name": str(item[3] or ""),
                    "change_time": item[4],
                }
            )
        return students

    def list_students(self, sid="", name="", class_name=""):
        sql = """
            SELECT id, student_id, name, class_name, change_time
            FROM face_data
            WHERE 1=1
        """
        params = []
        if sid:
            sql += " AND student_id LIKE ?"
            params.append(f"%{sid}%")
        if name:
            sql += " AND name LIKE ?"
            params.append(f"%{name}%")
        if class_name and class_name != "全部":
            sql += " AND class_name = ?"
            params.append(class_name)
        sql += " ORDER BY student_id ASC;"

        rows = self._cur.execute(sql, tuple(params)).fetchall()
        students = []
        for item in rows:
            students.append(
                {
                    "id": item[0],
                    "student_id": str(item[1]),
                    "name": str(item[2]),
                    "class_name": str(item[3] or ""),
                    "change_time": item[4],
                }
            )
        return students

    def get_checkin_records(self):
        rows = self.list_attendance_records()
        records = []
        for item in rows:
            records.append(
                {
                    "id": item.get("id"),
                    "student_id": str(item.get("student_id", "")),
                    "name": str(item.get("name", "")),
                    "checkin_time": str(item.get("checkin_time", "")),
                }
            )
        return records

    def get_student_by_sid(self, sid):
        row = self._cur.execute(
            "SELECT id, student_id, name, class_name FROM face_data WHERE student_id=? LIMIT 1;",
            (str(sid),),
        ).fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "student_id": str(row[1]),
            "name": row[2],
            "class_name": row[3] or "",
        }

    @staticmethod
    def _rule_row_to_dict(row):
        if not row:
            return None
        return {
            "id": row[0],
            "rule_name": row[1],
            "start_time": row[2],
            "end_time": row[3],
            "absence_deadline": row[4],
            "late_minutes": int(row[5]),
            "dedupe_scope": row[6],
            "is_active": int(row[7]),
            "is_deleted": int(row[8]) if len(row) > 8 else 0,
        }

    def list_rules(self):
        rows = self._cur.execute(
            """
            SELECT id, rule_name, start_time, end_time, absence_deadline, late_minutes, dedupe_scope, is_active, COALESCE(is_deleted, 0)
            FROM attendance_rule
            WHERE COALESCE(is_deleted, 0)=0
            ORDER BY id ASC;
            """
        ).fetchall()
        return [self._rule_row_to_dict(x) for x in rows]

    def get_rule_by_id(self, rule_id):
        row = self._cur.execute(
            """
            SELECT id, rule_name, start_time, end_time, absence_deadline, late_minutes, dedupe_scope, is_active, COALESCE(is_deleted, 0)
            FROM attendance_rule
            WHERE id=?
            LIMIT 1;
            """,
            (int(rule_id),),
        ).fetchone()
        return self._rule_row_to_dict(row)

    def get_active_rule(self):
        row = self._cur.execute(
            """
            SELECT id, rule_name, start_time, end_time, absence_deadline, late_minutes, dedupe_scope, is_active, COALESCE(is_deleted, 0)
            FROM attendance_rule
            WHERE is_active=1 AND COALESCE(is_deleted, 0)=0
            ORDER BY id DESC
            LIMIT 1;
            """
        ).fetchone()
        return self._rule_row_to_dict(row)

    def create_rule(self, rule_name, start_time, end_time, absence_deadline, late_minutes, dedupe_scope, is_active=0):
        now_text = sqlite3.datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        def _write():
            if int(is_active) == 1:
                self._cur.execute(
                    "UPDATE attendance_rule SET is_active=0, updated_at=? WHERE is_active=1 AND COALESCE(is_deleted, 0)=0;",
                    (now_text,),
                )
            self._cur.execute(
                """
                INSERT INTO attendance_rule
                (rule_name, start_time, end_time, absence_deadline, late_minutes, dedupe_scope, is_active, is_deleted, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?);
                """,
                (
                    rule_name,
                    start_time,
                    end_time,
                    absence_deadline,
                    int(late_minutes),
                    dedupe_scope,
                    int(is_active),
                    now_text,
                    now_text,
                ),
            )
        self._run_write_with_retry(_write)
        return self.get_rule_by_id(self._cur.lastrowid)

    def update_rule(self, rule_id, rule_name, start_time, end_time, absence_deadline, late_minutes, dedupe_scope):
        now_text = sqlite3.datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        def _write():
            self._cur.execute(
                """
                UPDATE attendance_rule
                SET rule_name=?, start_time=?, end_time=?, absence_deadline=?, late_minutes=?, dedupe_scope=?, updated_at=?
                WHERE id=? AND COALESCE(is_deleted, 0)=0;
                """,
                (
                    rule_name,
                    start_time,
                    end_time,
                    absence_deadline,
                    int(late_minutes),
                    dedupe_scope,
                    now_text,
                    int(rule_id),
                ),
            )
        self._run_write_with_retry(_write)
        return self.get_rule_by_id(rule_id)

    def activate_rule(self, rule_id):
        rule_id = int(rule_id)
        target = self.get_rule_by_id(rule_id)
        if not target or int(target.get("is_deleted", 0)) == 1:
            raise ValueError("规则不存在或已删除。")

        current_active = self.get_active_rule()
        if current_active and int(current_active.get("id", 0)) == rule_id:
            return current_active

        now_text = sqlite3.datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        def _write():
            self._cur.execute(
                "UPDATE attendance_rule SET is_active=0, updated_at=? WHERE is_active=1 AND COALESCE(is_deleted, 0)=0;",
                (now_text,),
            )
            self._cur.execute(
                "UPDATE attendance_rule SET is_active=1, updated_at=? WHERE id=? AND COALESCE(is_deleted, 0)=0;",
                (now_text, rule_id),
            )
            if self._cur.rowcount <= 0:
                raise ValueError("规则不存在或已删除。")

        self._run_write_with_retry(_write)
        return self.get_rule_by_id(rule_id)

    def delete_rule(self, rule_id):
        rule_id = int(rule_id)
        total = self._cur.execute(
            "SELECT COUNT(*) FROM attendance_rule WHERE COALESCE(is_deleted, 0)=0;"
        ).fetchone()[0]
        if total <= 1:
            raise ValueError("至少保留一条规则，不能全部删除。")

        row = self.get_rule_by_id(rule_id)
        if not row:
            raise ValueError("规则不存在。")
        if int(row.get("is_deleted", 0)) == 1:
            raise ValueError("该规则已删除。")

        now_text = sqlite3.datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        referenced_records = self.count_rule_references(rule_id)
        was_active = int(row.get("is_active", 0)) == 1

        def _write():
            self._cur.execute(
                "UPDATE attendance_rule SET is_deleted=1, is_active=0, updated_at=? WHERE id=?;",
                (now_text, rule_id),
            )

        self._run_write_with_retry(_write)

        if was_active:
            # 删除的是当前激活规则时，自动激活最新一条未删除规则
            newest = self._cur.execute(
                "SELECT id FROM attendance_rule WHERE COALESCE(is_deleted, 0)=0 ORDER BY id DESC LIMIT 1;"
            ).fetchone()
            if newest:
                self.activate_rule(newest[0])
        return {
            "rule_id": rule_id,
            "referenced_records": int(referenced_records),
            "was_active": was_active,
            "soft_deleted": True,
        }

    def save_active_rule(self, rule_name, start_time, end_time, absence_deadline, late_minutes, dedupe_scope):
        # 向后兼容旧接口：保存时新增一条并设为激活
        return self.create_rule(
            rule_name=rule_name,
            start_time=start_time,
            end_time=end_time,
            absence_deadline=absence_deadline,
            late_minutes=late_minutes,
            dedupe_scope=dedupe_scope,
            is_active=1,
        )

    def count_rule_references(self, rule_id):
        row = self._cur.execute(
            "SELECT COUNT(*) FROM attendance_record WHERE rule_id=?;",
            (int(rule_id),),
        ).fetchone()
        return int((row or [0])[0])

    def count_orphan_rule_records(self):
        row = self._cur.execute(
            """
            SELECT COUNT(*)
            FROM attendance_record ar
            LEFT JOIN attendance_rule r ON ar.rule_id=r.id
            WHERE ar.rule_id IS NOT NULL AND r.id IS NULL;
            """
        ).fetchone()
        return int((row or [0])[0])

    def get_attendance_record(self, student_id, attendance_date, rule_id):
        row = self._cur.execute(
            """
            SELECT id, attendance_date, student_id, name, class_name, checkin_time, checkout_time,
                   attendance_status, record_source, task_name, rule_id, remark, created_at, updated_at
            FROM attendance_record
            WHERE student_id=? AND attendance_date=? AND rule_id=?
            LIMIT 1;
            """,
            (str(student_id), attendance_date, int(rule_id)),
        ).fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "attendance_date": row[1],
            "student_id": str(row[2]),
            "name": row[3],
            "class_name": row[4] or "",
            "checkin_time": row[5] or "",
            "checkout_time": row[6] or "",
            "attendance_status": row[7],
            "record_source": row[8],
            "task_name": row[9] or "",
            "rule_id": row[10],
            "remark": row[11] or "",
            "created_at": row[12],
            "updated_at": row[13],
        }

    def insert_attendance_record(
        self,
        attendance_date,
        student_id,
        name,
        class_name,
        checkin_time,
        attendance_status,
        record_source,
        rule_id,
        task_name="",
        remark="",
        checkout_time="",
    ):
        now_text = sqlite3.datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        def _write():
            self._cur.execute(
                """
                INSERT INTO attendance_record
                (attendance_date, student_id, name, class_name, checkin_time, checkout_time, attendance_status,
                 record_source, task_name, rule_id, remark, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    attendance_date,
                    str(student_id),
                    name,
                    class_name or "",
                    checkin_time,
                    checkout_time,
                    attendance_status,
                    record_source,
                    task_name,
                    int(rule_id),
                    remark,
                    now_text,
                    now_text,
                ),
            )
            return self._cur.rowcount > 0

        try:
            return bool(self._run_write_with_retry(_write))
        except sqlite3.IntegrityError:
            # 并发/重复识别导致唯一键冲突时，按“已存在记录”处理，不抛异常中断主流程
            return False

    def update_attendance_record(
        self,
        record_id,
        attendance_status=None,
        record_source=None,
        checkin_time=None,
        checkout_time=None,
        remark=None,
    ):
        current = self._cur.execute(
            """
            SELECT attendance_status, record_source, checkin_time, checkout_time, remark
            FROM attendance_record WHERE id=?;
            """,
            (int(record_id),),
        ).fetchone()
        if not current:
            return
        now_text = sqlite3.datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        def _write():
            self._cur.execute(
                """
                UPDATE attendance_record
                SET attendance_status=?, record_source=?, checkin_time=?, checkout_time=?, remark=?, updated_at=?
                WHERE id=?;
                """,
                (
                    attendance_status if attendance_status is not None else current[0],
                    record_source if record_source is not None else current[1],
                    checkin_time if checkin_time is not None else current[2],
                    checkout_time if checkout_time is not None else current[3],
                    remark if remark is not None else current[4],
                    now_text,
                    int(record_id),
                ),
            )

        self._run_write_with_retry(_write)

    def update_attendance_checkout(self, record_id, checkout_time, attendance_status=None, remark=None):
        self.update_attendance_record(
            record_id=record_id,
            attendance_status=attendance_status,
            checkout_time=checkout_time,
            remark=remark,
        )

    def list_attendance_records(self, start_date="", end_date="", sid="", name="", class_name="", course_keyword=""):
        sql = """
            SELECT
                ar.id,
                ar.attendance_date,
                ar.student_id,
                ar.name,
                ar.class_name,
                ar.checkin_time,
                ar.checkout_time,
                ar.attendance_status,
                ar.record_source,
                ar.task_name,
                ar.rule_id,
                ar.remark,
                COALESCE(r.rule_name, '') AS rule_name,
                CASE WHEN r.id IS NULL THEN 1 ELSE 0 END AS rule_missing,
                COALESCE(r.is_deleted, 0) AS rule_deleted
            FROM attendance_record ar
            LEFT JOIN attendance_rule r ON ar.rule_id = r.id
            WHERE 1=1
        """
        params = []
        if start_date:
            sql += " AND ar.attendance_date >= ?"
            params.append(start_date)
        if end_date:
            sql += " AND ar.attendance_date <= ?"
            params.append(end_date)
        if sid:
            sql += " AND ar.student_id LIKE ?"
            params.append(f"%{sid}%")
        if name:
            sql += " AND ar.name LIKE ?"
            params.append(f"%{name}%")
        if class_name and class_name != "全部":
            sql += " AND ar.class_name = ?"
            params.append(class_name)
        if course_keyword:
            sql += " AND COALESCE(NULLIF(TRIM(ar.task_name), ''), NULLIF(TRIM(r.rule_name), ''), '未设置课程') LIKE ?"
            params.append(f"%{course_keyword}%")
        sql += " ORDER BY ar.attendance_date DESC, ar.student_id ASC;"
        rows = self._cur.execute(sql, tuple(params)).fetchall()
        result = []
        for row in rows:
            result.append(
                {
                    "id": row[0],
                    "attendance_date": row[1],
                    "student_id": str(row[2]),
                    "name": row[3],
                    "class_name": row[4] or "",
                    "checkin_time": row[5] or "",
                    "checkout_time": row[6] or "",
                    "attendance_status": row[7],
                    "record_source": row[8],
                    "task_name": row[9] or "",
                    "rule_id": row[10],
                    "remark": row[11] or "",
                    "rule_name": row[12] or "",
                    "rule_missing": int(row[13] or 0),
                    "rule_deleted": int(row[14] or 0),
                }
            )
        return result
