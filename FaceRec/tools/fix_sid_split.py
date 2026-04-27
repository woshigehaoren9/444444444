#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from model.connectsqlite import ConnectSqlite  # noqa: E402
import model.configuration as configuration  # noqa: E402


def backup_database(db_path: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.parent / f"database_backup_before_sid_merge_{ts}.db"
    shutil.copy2(db_path, backup_path)
    return backup_path


def audit_counts(conn: sqlite3.Connection, old_sid: str, new_sid: str):
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM attendance_record WHERE student_id=?;",
        (old_sid,),
    )
    old_count = int(cur.fetchone()[0])
    cur.execute(
        "SELECT COUNT(*) FROM attendance_record WHERE student_id=?;",
        (new_sid,),
    )
    new_count = int(cur.fetchone()[0])
    cur.execute(
        """
        SELECT COUNT(*)
        FROM (
            SELECT a.attendance_date, a.rule_id
            FROM attendance_record a
            JOIN attendance_record b
              ON a.student_id=?
             AND b.student_id=?
             AND a.attendance_date=b.attendance_date
             AND a.rule_id=b.rule_id
            GROUP BY a.attendance_date, a.rule_id
        ) t;
        """,
        (old_sid, new_sid),
    )
    conflict_key_count = int(cur.fetchone()[0])
    cur.execute(
        """
        SELECT a.attendance_date, a.rule_id
        FROM attendance_record a
        JOIN attendance_record b
          ON a.student_id=?
         AND b.student_id=?
         AND a.attendance_date=b.attendance_date
         AND a.rule_id=b.rule_id
        GROUP BY a.attendance_date, a.rule_id
        ORDER BY a.attendance_date DESC, a.rule_id ASC
        LIMIT 20;
        """,
        (old_sid, new_sid),
    )
    conflict_top = cur.fetchall()
    return {
        "old_count": old_count,
        "new_count": new_count,
        "conflict_key_count": conflict_key_count,
        "conflict_top20": conflict_top,
    }


def print_report(stage: str, report: dict):
    print(f"\n[{stage}]")
    print(f"原学号记录数: {report['old_count']}")
    print(f"新学号记录数: {report['new_count']}")
    print(f"冲突键数量(同日期+同规则): {report['conflict_key_count']}")
    print("冲突键前20条:")
    if report["conflict_top20"]:
        for item in report["conflict_top20"]:
            print(f"  - 日期: {item[0]}, 规则ID: {item[1]}")
    else:
        print("  - 无")


def main():
    parser = argparse.ArgumentParser(description="学号分叉并档修复工具")
    parser.add_argument("--old-sid", required=True, help="原学号")
    parser.add_argument("--new-sid", required=True, help="目标学号")
    parser.add_argument("--dry-run", action="store_true", help="只预览不写库")
    args = parser.parse_args()

    old_sid = str(args.old_sid).strip()
    new_sid = str(args.new_sid).strip()
    if not old_sid or not new_sid:
        print("失败：--old-sid 与 --new-sid 不能为空。")
        sys.exit(2)

    db_path = Path(configuration.DATABASE_PATH).resolve()
    if not db_path.exists():
        print(f"失败：数据库不存在：{db_path}")
        sys.exit(2)

    backup_path = backup_database(db_path)
    print(f"已备份数据库：{backup_path}")

    conn = sqlite3.connect(str(db_path))
    before = audit_counts(conn, old_sid, new_sid)
    print_report("并档前", before)
    conn.close()

    if args.dry_run:
        print("\n[执行结果]")
        print("dry-run 模式：未执行写库。")
        print("是否成功: 是（仅预览）")
        return

    dbcon = None
    try:
        dbcon = ConnectSqlite(str(db_path))
        result = dbcon.merge_student_history_sid(old_sid, new_sid, prefer_profile=True)
        print("\n[执行结果]")
        print("并档执行完成。")
        print(f"自动合并冲突条数: {int(result.get('merged_conflicts', 0))}")
        print(f"迁移记录条数: {int(result.get('moved_rows', 0))}")
    except Exception as exc:
        print("\n[执行结果]")
        print(f"是否成功: 否")
        print(f"失败原因: {exc}")
        sys.exit(1)
    finally:
        if dbcon is not None:
            try:
                dbcon.close_con()
            except Exception:
                pass

    conn = sqlite3.connect(str(db_path))
    after = audit_counts(conn, old_sid, new_sid)
    print_report("并档后", after)
    conn.close()

    print("\n[最终结论]")
    print("是否成功: 是")


if __name__ == "__main__":
    main()
