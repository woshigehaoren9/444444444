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

import model.configuration as configuration  # noqa: E402


def now_ts():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def run_pragmas(db_path: Path):
    conn = sqlite3.connect(str(db_path), timeout=10)
    cur = conn.cursor()
    result = {}
    result["integrity_check"] = str(cur.execute("PRAGMA integrity_check;").fetchone()[0])
    result["quick_check"] = str(cur.execute("PRAGMA quick_check;").fetchone()[0])
    result["journal_mode"] = str(cur.execute("PRAGMA journal_mode;").fetchone()[0])
    result["synchronous"] = str(cur.execute("PRAGMA synchronous;").fetchone()[0])
    result["foreign_keys"] = str(cur.execute("PRAGMA foreign_keys;").fetchone()[0])
    conn.close()
    return result


def print_health(title: str, db_path: Path, info: dict):
    print(f"\n[{title}]")
    print(f"数据库: {db_path}")
    print(f"integrity_check: {info.get('integrity_check', '')}")
    print(f"quick_check: {info.get('quick_check', '')}")
    print(f"journal_mode: {info.get('journal_mode', '')}")
    print(f"synchronous: {info.get('synchronous', '')}")
    print(f"foreign_keys: {info.get('foreign_keys', '')}")


def is_healthy(info: dict) -> bool:
    return str(info.get("integrity_check", "")).lower() == "ok" and str(info.get("quick_check", "")).lower() == "ok"


def safe_write_test(db_path: Path):
    conn = sqlite3.connect(str(db_path), timeout=20)
    cur = conn.cursor()
    cur.execute("PRAGMA busy_timeout=20000;")
    cur.execute("CREATE TABLE IF NOT EXISTS __db_health_ping(id INTEGER PRIMARY KEY AUTOINCREMENT, note TEXT, created_at TEXT);")
    cur.execute(
        "INSERT INTO __db_health_ping(note, created_at) VALUES (?, ?);",
        ("db health test", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    cur.execute("DELETE FROM __db_health_ping WHERE note='db health test';")
    conn.commit()
    conn.close()


def list_candidate_backups(database_dir: Path):
    patterns = [
        "database_backup*.db",
        "backup*.db",
        "*.db",
    ]
    candidates = []
    seen = set()
    for pattern in patterns:
        for p in database_dir.glob(pattern):
            if p.name == "database.db":
                continue
            if p.suffix.lower() != ".db":
                continue
            rp = str(p.resolve())
            if rp in seen:
                continue
            seen.add(rp)
            candidates.append(p)
    candidates.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return candidates


def has_core_tables(db_path: Path):
    core = {"face_data", "attendance_record", "attendance_rule"}
    conn = sqlite3.connect(str(db_path), timeout=10)
    cur = conn.cursor()
    tables = {x[0] for x in cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()}
    conn.close()
    return core.issubset(tables)


def select_latest_healthy_backup(database_dir: Path):
    for candidate in list_candidate_backups(database_dir):
        try:
            if candidate.stat().st_size < 1024 * 1024:
                # 跳过探针库、空库、小临时库
                continue
            info = run_pragmas(candidate)
            if not has_core_tables(candidate):
                continue
        except Exception:
            continue
        if is_healthy(info):
            return candidate, info
    return None, None


def backup_current_main(db_path: Path):
    ts = now_ts()
    backup = db_path.parent / f"database_corrupted_snapshot_{ts}.db"
    shutil.copy2(db_path, backup)
    return backup


def restore_from_backup(main_db: Path, backup_db: Path):
    shutil.copy2(backup_db, main_db)


def main():
    parser = argparse.ArgumentParser(description="数据库健康检查与修复工具")
    parser.add_argument("--repair", action="store_true", help="主库异常时自动尝试用健康备份恢复")
    parser.add_argument("--db-path", default=configuration.DATABASE_PATH, help="数据库路径")
    args = parser.parse_args()

    main_db = Path(args.db_path).resolve()
    if not main_db.exists():
        print(f"失败：数据库不存在：{main_db}")
        sys.exit(2)

    try:
        health = run_pragmas(main_db)
        print_health("主库健康检查", main_db, health)
    except Exception as exc:
        print(f"主库检查失败：{exc}")
        health = {}

    healthy = is_healthy(health)
    write_ok = False
    write_err = ""
    if healthy:
        print("\n结论：主库完整性检查正常，继续执行写入测试。")
        try:
            safe_write_test(main_db)
            write_ok = True
            print("写入测试：通过（插入+提交+删除+提交）。")
        except Exception as exc:
            write_err = str(exc)
            print(f"写入测试：失败，原因：{exc}")
        if write_ok:
            return

    if healthy and not write_ok:
        print("\n结论：主库完整性虽正常，但写入失败，判定为主库不可写。")
    else:
        print("\n结论：主库完整性异常。")
    if not args.repair:
        print("未启用 --repair，已停止。")
        sys.exit(1)

    backup_db, backup_info = select_latest_healthy_backup(main_db.parent)
    if not backup_db:
        print("修复失败：未找到可用健康备份。")
        sys.exit(1)

    print_health("选中的健康备份", backup_db, backup_info)
    bad_snapshot = backup_current_main(main_db)
    print(f"已备份当前主库快照：{bad_snapshot}")

    try:
        restore_from_backup(main_db, backup_db)
        after = run_pragmas(main_db)
        print_health("恢复后主库检查", main_db, after)
        if not is_healthy(after):
            print("修复失败：恢复后主库仍不健康。")
            sys.exit(1)
        safe_write_test(main_db)
        print("\n修复成功：主库已恢复且写入测试通过。")
        print(
            f"替换信息：来源={backup_db.name}({backup_db.stat().st_size} bytes) -> 目标={main_db.name}({main_db.stat().st_size} bytes)"
        )
    except Exception as exc:
        if write_err:
            print(f"原始写入错误：{write_err}")
        print(f"修复失败：{exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
