#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import shutil
from datetime import datetime
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]

SCAN_DIRS = ["control", "view", "model", "tools", "."]
INCLUDE_SUFFIX = {".py", ".qss", ".txt", ".md"}
EXCLUDE_DIR = {".venv", ".idea", "__pycache__", "backup_before_cleanup", "database"}
EXCLUDE_FILES = {"fix_text_encoding.py"}

# 项目内出现频率最高的一批乱码片段映射（可持续补充）
REPLACE_MAP = {
    "鎻愮ず": "提示",
    "閿欒": "错误",
    "璀﹀憡": "警告",
    "鎴愬姛": "成功",
    "璇峰厛": "请先",
    "鎵撳紑": "打开",
    "鎽勫儚澶": "摄像头",
    "涓嶅彲鐢": "不可用",
    "鏃犳硶": "无法",
    "璇锋鏌": "请检查",
    "宸茶繛鎺": "已连接",
    "鏈瘑鍒": "未识别",
    "宸插埌": "已到",
    "杩熷埌": "迟到",
    "缂哄嫟": "缺勤",
    "琛ョ": "补签",
    "鍙戠敓閿欒": "发生错误",
}

SUSPECT_PATTERN = re.compile(r"[鎻愮ず閿欒璇峰厛鎵撳紑鎽勫儚澶涓嶅彲鐢鏃犳硶璀﹀憡鏉′欢]+")


def iter_files():
    seen = set()
    for folder in SCAN_DIRS:
        base = ROOT / folder
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() not in INCLUDE_SUFFIX:
                continue
            if any(part in EXCLUDE_DIR for part in p.parts):
                continue
            if p.name in EXCLUDE_FILES:
                continue
            rp = str(p.resolve())
            if rp in seen:
                continue
            seen.add(rp)
            yield p


def backup_file(path: Path):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = ROOT / "backup_before_cleanup" / "encoding_fix"
    backup_root.mkdir(parents=True, exist_ok=True)
    target = backup_root / f"{path.name}.{ts}.bak"
    shutil.copy2(path, target)
    return target


def scan_file(path: Path):
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {"path": path, "decode_error": True, "suspects": [], "content": None}
    suspects = []
    for idx, line in enumerate(text.splitlines(), start=1):
        if SUSPECT_PATTERN.search(line):
            suspects.append((idx, line.strip()))
    return {"path": path, "decode_error": False, "suspects": suspects, "content": text}


def repair_text(text: str):
    fixed = text
    for old, new in REPLACE_MAP.items():
        fixed = fixed.replace(old, new)
    return fixed


def main():
    parser = argparse.ArgumentParser(description="中文乱码扫描与修复工具")
    parser.add_argument("--apply", action="store_true", help="执行修复并覆盖写回（先备份）")
    args = parser.parse_args()

    total_files = 0
    suspect_files = []
    decode_error_files = []
    patched = 0

    for path in iter_files():
        total_files += 1
        result = scan_file(path)
        if result["decode_error"]:
            decode_error_files.append(path)
            continue
        if not result["suspects"]:
            continue
        suspect_files.append(result)

    print(f"扫描文件总数: {total_files}")
    print(f"疑似乱码文件数: {len(suspect_files)}")
    print(f"UTF-8 解码失败文件数: {len(decode_error_files)}")

    for item in suspect_files:
        print(f"\n[疑似乱码] {item['path']}")
        for ln, content in item["suspects"][:10]:
            safe = content.encode("gbk", errors="replace").decode("gbk", errors="replace")
            print(f"  行{ln}: {safe}")

    if decode_error_files:
        print("\n[需人工确认编码的文件]")
        for p in decode_error_files:
            print(f"  {p}")

    if not args.apply:
        print("\n未启用 --apply，仅输出扫描结果。")
        return

    for item in suspect_files:
        original = item["content"]
        fixed = repair_text(original)
        if fixed == original:
            continue
        backup_file(item["path"])
        item["path"].write_text(fixed, encoding="utf-8", newline="\n")
        patched += 1

    print(f"\n修复完成，实际写回文件数: {patched}")
    if patched == 0:
        print("未发生自动替换，建议根据扫描结果手工修正。")


if __name__ == "__main__":
    main()
