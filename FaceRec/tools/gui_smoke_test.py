#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import shutil
import sys
import tempfile
import traceback
from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog, QMessageBox, QPushButton


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "tools" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def now_text():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


class SmokeLogger:
    def __init__(self):
        self.started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.steps = []
        self.errors = []
        self.dialogs = []
        self.info = {}

    def add_step(self, scope, action, ok=True, detail="", exc_text=""):
        item = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "scope": scope,
            "action": action,
            "ok": bool(ok),
            "detail": str(detail or ""),
            "exception": str(exc_text or ""),
        }
        self.steps.append(item)
        if not ok:
            self.errors.append(item)

    def add_dialog(self, level, title, text):
        self.dialogs.append(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "level": level,
                "title": str(title or ""),
                "text": str(text or ""),
            }
        )

    def dump(self):
        ts = now_text()
        json_path = REPORT_DIR / f"smoke_result_{ts}.json"
        txt_path = REPORT_DIR / f"smoke_result_{ts}.txt"
        payload = {
            "started_at": self.started_at,
            "finished_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "info": self.info,
            "step_count": len(self.steps),
            "error_count": len(self.errors),
            "steps": self.steps,
            "errors": self.errors,
            "dialogs": self.dialogs,
        }
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        lines = []
        lines.append(f"开始时间: {payload['started_at']}")
        lines.append(f"结束时间: {payload['finished_at']}")
        lines.append(f"总步骤: {payload['step_count']}")
        lines.append(f"错误数: {payload['error_count']}")
        lines.append("")
        lines.append("环境信息:")
        for k, v in self.info.items():
            lines.append(f"- {k}: {v}")
        lines.append("")
        lines.append("步骤结果:")
        for x in self.steps:
            flag = "通过" if x["ok"] else "失败"
            lines.append(f"[{x['time']}] [{flag}] {x['scope']} -> {x['action']} {x['detail']}")
            if x["exception"]:
                lines.append(f"  异常: {x['exception']}")
        lines.append("")
        lines.append("弹窗记录:")
        for d in self.dialogs:
            lines.append(f"[{d['time']}] [{d['level']}] {d['title']} | {d['text']}")
        txt_path.write_text("\n".join(lines), encoding="utf-8")
        return json_path, txt_path


def process_events(ms=30):
    end = datetime.now().timestamp() + ms / 1000.0
    while datetime.now().timestamp() < end:
        QCoreApplication.processEvents()


def patch_dialogs(logger, export_dir):
    originals = {
        "msg_info": QMessageBox.information,
        "msg_warn": QMessageBox.warning,
        "msg_crit": QMessageBox.critical,
        "msg_question": QMessageBox.question,
        "file_save": QFileDialog.getSaveFileName,
        "file_open": QFileDialog.getOpenFileName,
        "file_dir": QFileDialog.getExistingDirectory,
        "input_text": QInputDialog.getText,
    }

    def _info(parent, title, text, *args, **kwargs):
        logger.add_dialog("信息", title, text)
        return QMessageBox.Ok

    def _warn(parent, title, text, *args, **kwargs):
        logger.add_dialog("警告", title, text)
        return QMessageBox.Ok

    def _crit(parent, title, text, *args, **kwargs):
        logger.add_dialog("错误", title, text)
        return QMessageBox.Ok

    def _question(parent, title, text, *args, **kwargs):
        logger.add_dialog("询问", title, text)
        return QMessageBox.No

    def _save(*args, **kwargs):
        title = args[1] if len(args) > 1 else ""
        if "CSV" in str(title).upper():
            return str(export_dir / f"smoke_export_{now_text()}.csv"), "CSV 文件 (*.csv)"
        return str(export_dir / f"smoke_export_{now_text()}.xlsx"), "Excel 文件 (*.xlsx)"

    def _open(*args, **kwargs):
        return "", ""

    def _dir(*args, **kwargs):
        return ""

    def _input_text(*args, **kwargs):
        # 默认取消，避免污染测试库
        return "", False

    QMessageBox.information = staticmethod(_info)
    QMessageBox.warning = staticmethod(_warn)
    QMessageBox.critical = staticmethod(_crit)
    QMessageBox.question = staticmethod(_question)
    QFileDialog.getSaveFileName = staticmethod(_save)
    QFileDialog.getOpenFileName = staticmethod(_open)
    QFileDialog.getExistingDirectory = staticmethod(_dir)
    QInputDialog.getText = staticmethod(_input_text)
    return originals


def restore_dialogs(originals):
    QMessageBox.information = originals["msg_info"]
    QMessageBox.warning = originals["msg_warn"]
    QMessageBox.critical = originals["msg_crit"]
    QMessageBox.question = originals["msg_question"]
    QFileDialog.getSaveFileName = originals["file_save"]
    QFileDialog.getOpenFileName = originals["file_open"]
    QFileDialog.getExistingDirectory = originals["file_dir"]
    QInputDialog.getText = originals["input_text"]


class FakeRecognizer:
    def take_photo(self, frame):
        return 0, frame, frame, None

    def check_in(self, frame, student_info_all):
        return 0, frame, None

    def extract_face_fingerprint_from_image_path(self, image_path):
        return 0, None, None, None


def patch_runtime(logger, temp_db):
    import model.configuration as configuration

    configuration.DATABASE_PATH = str(temp_db)
    logger.info["test_database"] = str(temp_db)

    def _open_camera_capture(_cv2_module):
        return None, "", "0(DSHOW)、0(MSMF)、0(AUTO)"

    configuration.open_camera_capture = _open_camera_capture

    import control.mainWindow as main_window

    main_window.recognizer = lambda *_args, **_kwargs: FakeRecognizer()
    return main_window


def smoke_click_buttons(logger, page_name, page_obj):
    button_names = []
    for name in dir(page_obj):
        if name.startswith("pushButton_") or name.startswith("btn"):
            button = getattr(page_obj, name, None)
            if isinstance(button, QPushButton):
                button_names.append(name)
    button_names = sorted(set(button_names))

    for name in button_names:
        btn = getattr(page_obj, name, None)
        if not isinstance(btn, QPushButton):
            continue
        try:
            btn.click()
            process_events(60)
            logger.add_step(page_name, f"点击按钮 {name}", True, f"text={btn.text()}")
        except Exception:
            logger.add_step(
                page_name,
                f"点击按钮 {name}",
                False,
                f"text={btn.text()}",
                traceback.format_exc(),
            )


def main():
    logger = SmokeLogger()
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    source_db = ROOT / "database" / "database.db"
    if not source_db.exists():
        logger.add_step("初始化", "检查数据库", False, "", f"数据库不存在: {source_db}")
        j, t = logger.dump()
        print(f"失败: {j}\n{t}")
        return 1

    temp_root = Path(tempfile.mkdtemp(prefix="facerec_smoke_"))
    temp_db = temp_root / "database_smoke.db"
    shutil.copy2(source_db, temp_db)
    export_dir = temp_root / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    logger.info["temp_root"] = str(temp_root)
    logger.info["source_database"] = str(source_db)

    originals = patch_dialogs(logger, export_dir)

    caught_exceptions = []
    old_hook = sys.excepthook

    def _hook(exc_type, exc_value, exc_tb):
        text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        caught_exceptions.append(text)
        logger.add_step("全局异常", "捕获未处理异常", False, "", text)
        old_hook(exc_type, exc_value, exc_tb)

    sys.excepthook = _hook

    app = QApplication.instance() or QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    win = None
    try:
        main_window = patch_runtime(logger, temp_db)
        win = main_window.MyWindow()
        win.showMinimized()
        process_events(100)
        logger.add_step("主窗口", "实例化并最小化", True)

        nav_items = [
            ("pushButton_about", "系统首页"),
            ("pushButton_register", "人脸录入"),
            ("pushButton_checkin", "人脸签到"),
            ("pushButton_record_view", "记录查看"),
            ("pushButton_face_record", "人脸库管理"),
            ("pushButton_checkin_record", "考勤管理"),
            ("pushButton_exit", "退出系统"),
        ]

        for attr, cn_name in nav_items:
            btn = getattr(win, attr, None)
            if not isinstance(btn, QPushButton):
                logger.add_step("导航栏", f"{attr}({cn_name})不存在", False)
                continue
            try:
                btn.click()
                process_events(120)
                logger.add_step("导航栏", f"点击 {attr}", True, cn_name)
            except Exception:
                logger.add_step("导航栏", f"点击 {attr}", False, cn_name, traceback.format_exc())
                continue

            if attr == "pushButton_exit":
                continue

            page = None
            if win.verticalLayout.count() > 0:
                item = win.verticalLayout.itemAt(0)
                page = item.widget() if item else None
            if page is None:
                if attr == "pushButton_about":
                    logger.add_step("页面", f"{cn_name}为背景首页，无内容页实例", True)
                else:
                    logger.add_step("页面", f"{cn_name}未加载页面实例", False)
                continue

            logger.add_step("页面", f"{cn_name}加载成功", True, page.__class__.__name__)
            smoke_click_buttons(logger, cn_name, page)

        # 额外执行一次 close_all，验证资源释放
        if win.verticalLayout.count() > 0:
            page = win.verticalLayout.itemAt(0).widget()
            if page is not None and hasattr(page, "close_all"):
                try:
                    page.close_all()
                    process_events(80)
                    logger.add_step("资源释放", f"{page.__class__.__name__}.close_all", True)
                except Exception:
                    logger.add_step("资源释放", f"{page.__class__.__name__}.close_all", False, "", traceback.format_exc())
    finally:
        try:
            if win is not None:
                win.close()
        except Exception:
            pass
        process_events(80)
        restore_dialogs(originals)
        sys.excepthook = old_hook

    if caught_exceptions:
        logger.info["uncaught_exception_count"] = len(caught_exceptions)
    else:
        logger.info["uncaught_exception_count"] = 0

    json_path, txt_path = logger.dump()
    print(f"JSON报告: {json_path}")
    print(f"文本报告: {txt_path}")
    return 0 if not logger.errors else 2


if __name__ == "__main__":
    sys.exit(main())
