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
    backup = db_path.parent / f"database_backup_before_identity_repair_{ts}.db"
    shutil.copy2(db_path, backup)
    return backup


def audit_student(conn: sqlite3.Connection, old_sid: str, new_sid: str):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM attendance_record WHERE student_id=?;", (old_sid,))
    old_att = int(cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) FROM attendance_record WHERE student_id=?;", (new_sid,))
    new_att = int(cur.fetchone()[0])

    old_re = 0
    new_re = 0
    try:
        cur.execute("SELECT COUNT(*) FROM re_record WHERE student_id=?;", (old_sid,))
        old_re = int(cur.fetchone()[0])
        cur.execute("SELECT COUNT(*) FROM re_record WHERE student_id=?;", (new_sid,))
        new_re = int(cur.fetchone()[0])
    except sqlite3.OperationalError:
        pass

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
    conflict_keys = int(cur.fetchone()[0])

    return {
        "old_attendance_count": old_att,
        "new_attendance_count": new_att,
        "old_re_record_count": old_re,
        "new_re_record_count": new_re,
        "conflict_key_count": conflict_keys,
    }


def get_profile_by_sid(conn: sqlite3.Connection, sid: str):
    cur = conn.cursor()
    row = cur.execute(
        "SELECT student_id, name, COALESCE(class_name, '') FROM face_data WHERE student_id=? LIMIT 1;",
        (sid,),
    ).fetchone()
    if not row:
        return None
    return {"student_id": str(row[0]), "name": str(row[1] or ""), "class_name": str(row[2] or "")}


def list_sid_splits(conn: sqlite3.Connection):
    """
    按姓名扫描同名多学号分叉（仅用于快速修复，复杂同名场景建议先 dry-run 审核）。
    """
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT name, GROUP_CONCAT(DISTINCT student_id), COUNT(DISTINCT student_id) AS sid_count
        FROM attendance_record
        WHERE TRIM(COALESCE(name, '')) <> ''
        GROUP BY name
        HAVING COUNT(DISTINCT student_id) > 1
        ORDER BY sid_count DESC, name ASC;
        """
    ).fetchall()
    result = []
    for name, sid_csv, _ in rows:
        sid_list = [x.strip() for x in str(sid_csv or "").split(",") if x and x.strip()]
        if len(sid_list) < 2:
            continue
        # 选择 face_data 中存在的学号作为主学号；若都不存在则选长度更长的学号
        keep_sid = None
        for sid in sid_list:
            if get_profile_by_sid(conn, sid):
                keep_sid = sid
                break
        if not keep_sid:
            sid_list_sorted = sorted(sid_list, key=lambda x: (len(str(x)), str(x)), reverse=True)
            keep_sid = sid_list_sorted[0]
        old_sids = [x for x in sid_list if x != keep_sid]
        result.append({"name": str(name), "keep_sid": keep_sid, "old_sids": old_sids})
    return result


def print_report(title: str, data: dict):
    print(f"\n[{title}]")
    print(f"旧学号考勤记录数: {data['old_attendance_count']}")
    print(f"新学号考勤记录数: {data['new_attendance_count']}")
    print(f"旧学号旧表记录数(re_record): {data['old_re_record_count']}")
    print(f"新学号旧表记录数(re_record): {data['new_re_record_count']}")
    print(f"同日期同规则冲突键数: {data['conflict_key_count']}")


def main():
    parser = argparse.ArgumentParser(description="学生身份一致性修复工具")
    parser.add_argument("--sid", help="旧学号")
    parser.add_argument("--to", help="新学号")
    parser.add_argument("--name", help="新姓名")
    parser.add_argument("--class-name", help="新班级")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不写库")
    parser.add_argument("--apply-all-splits", action="store_true", help="自动扫描并修复全库同名多学号分叉")
    args = parser.parse_args()

    old_sid = str(args.sid or "").strip()
    new_sid = str(args.to or "").strip()
    new_name = str(args.name or "").strip()
    class_name = str(args.class_name or "").strip()

    if args.apply_all_splits:
        if old_sid or new_sid:
            print("提示：已启用 --apply-all-splits，单条 --sid/--to 参数将被忽略。")
    else:
        if not old_sid or not new_sid:
            print("失败：未启用 --apply-all-splits 时，必须提供 --sid 和 --to。")
            sys.exit(2)

    db_path = Path(configuration.DATABASE_PATH).resolve()
    if not db_path.exists():
        print(f"失败：数据库不存在：{db_path}")
        sys.exit(2)

    backup = backup_database(db_path)
    print(f"数据库备份完成：{backup}")

    conn = sqlite3.connect(str(db_path))
    tasks = []
    if args.apply_all_splits:
        splits = list_sid_splits(conn)
        print(f"检测到同名多学号分叉组数: {len(splits)}")
        for item in splits:
            keep_sid = item["keep_sid"]
            profile = get_profile_by_sid(conn, keep_sid)
            final_name = str((profile or {}).get("name") or item["name"] or "").strip()
            final_class = str((profile or {}).get("class_name") or "").strip()
            for sid in item["old_sids"]:
                tasks.append(
                    {
                        "old_sid": sid,
                        "new_sid": keep_sid,
                        "name": final_name,
                        "class_name": final_class,
                    }
                )
        if not tasks:
            print("没有发现可修复的分叉数据。")
            conn.close()
            return
    else:
        # 若名称/班级未传，优先从目标学号主档补全
        if not new_name or not class_name:
            profile = get_profile_by_sid(conn, new_sid)
            if profile:
                if not new_name:
                    new_name = profile["name"]
                if not class_name:
                    class_name = profile["class_name"]
        if not new_name:
            print("失败：姓名不能为空（可通过 --name 提供）。")
            conn.close()
            sys.exit(2)
        if not class_name:
            print("失败：班级不能为空（可通过 --class-name 提供）。")
            conn.close()
            sys.exit(2)
        tasks.append({"old_sid": old_sid, "new_sid": new_sid, "name": new_name, "class_name": class_name})

    before_all = []
    for task in tasks:
        before = audit_student(conn, task["old_sid"], task["new_sid"])
        before_all.append((task, before))
        print_report(f"修复前统计 [{task['old_sid']} -> {task['new_sid']}]", before)
    conn.close()

    if args.dry_run:
        print("\n[执行结果]")
        print(f"dry-run 模式：未执行写库。待处理任务数: {len(tasks)}")
        print("是否成功：是（仅预览）")
        return

    dbcon = None
    merged_total = 0
    updated_total = 0
    ok_count = 0
    failed = []
    try:
        dbcon = ConnectSqlite(str(db_path))
        for task in tasks:
            try:
                result = dbcon.sync_student_profile_everywhere(
                    old_sid=task["old_sid"],
                    new_sid=task["new_sid"],
                    new_name=task["name"],
                    new_class_name=task["class_name"],
                    auto_merge_conflict=True,
                )
                merged_total += int(result.get("merged_conflicts", 0))
                updated_total += int(result.get("updated_total_rows", 0))
                ok_count += 1
            except Exception as exc:
                failed.append((task["old_sid"], task["new_sid"], str(exc)))
    finally:
        if dbcon is not None:
            try:
                dbcon.close_con()
            except Exception:
                pass

    conn = sqlite3.connect(str(db_path))
    for task in tasks:
        after = audit_student(conn, task["old_sid"], task["new_sid"])
        print_report(f"修复后统计 [{task['old_sid']} -> {task['new_sid']}]", after)
    conn.close()

    print("\n[执行结果]")
    print(f"总任务数: {len(tasks)}")
    print(f"成功任务数: {ok_count}")
    print(f"失败任务数: {len(failed)}")
    print(f"自动合并冲突总数: {merged_total}")
    print(f"更新总行数(估算): {updated_total}")
    if failed:
        print("失败明细：")
        for old_x, new_x, msg in failed[:20]:
            print(f"  {old_x} -> {new_x}: {msg}")
        sys.exit(1)
    print("是否成功：是")


if __name__ == "__main__":
    main()
