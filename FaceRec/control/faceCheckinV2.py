import time
from datetime import datetime

import cv2
from PyQt5.QtCore import QBasicTimer, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QMessageBox, QPushButton, QWidget

import model.configuration
from model.attendance_service import AttendanceService
from model.connectsqlite import ConnectSqlite
from view.facecheck import Ui_FaceCheckForm
from view.ui_theme import apply_page_theme, style_button, style_hint_label, style_status_badge


class FaceCheckin(QWidget, Ui_FaceCheckForm):
    def __init__(self, re, parent=None):
        super(FaceCheckin, self).__init__(parent)
        self.setupUi(self)
        self.setMinimumSize(1080, 760)

        self.timer = QBasicTimer()
        self.timer.start(1000, self)
        self.label_current.setText(time.strftime("%X", time.localtime()))
        self._last_absence_sync_key = ""

        self.CAM_OPEN_FLAG = False
        self.monitoring_enabled = False
        self.detect_interval_ms = 1200
        self.last_detect_ts = 0.0
        self.student_cooldown_sec = 8.0
        self.student_last_detect_ts = {}

        self.re = re
        self.dbcon = ConnectSqlite(model.configuration.DATABASE_PATH)
        self.student_info_all = self.dbcon.load_registered_data()
        self.attendance_service = AttendanceService(self.dbcon)

        self._localize_ui()
        self._init_monitor_widgets()
        self._beautify_ui()
        self._apply_responsive_layout()

        self.pushButton_open.clicked.connect(self.open_cam)
        self.pushButton_stop.clicked.connect(self.stop_cam)
        self.pushButton_checkin.clicked.connect(self.toggle_monitoring)
        self.pushButton_checkin.setToolTip("开始后将自动持续识别人脸并记录考勤")

        self.timer_close = QTimer()
        self.timer_close.timeout.connect(self.close_feedback)
        self._reset_feedback()

    def _localize_ui(self):
        self.setWindowTitle("人脸签到")
        self.label_6.setText("摄像头")
        self.pushButton_open.setText("打开")
        self.pushButton_stop.setText("关闭")
        self.pushButton_checkin.setText("开始监测")
        self.pushButton_checkin.setToolTip("点击开始或停止课堂实时监测")
        self.groupBox_2.setTitle("实时识别")
        self.groupBox_3.setTitle("识别结果")
        self.label_3.setText("姓名:")
        self.label_2.setText("学号:")
        self.label_5.setText("相似度:")
        self.label_12.setText("当前考勤状态")
        self.label_13.setText("识别时间:")
        self.pushButton_checkin.setMinimumWidth(120)

    def _init_monitor_widgets(self):
        self.label_class_title = QLabel(self.groupBox_3)
        self.label_class_title.setText("班级:")

        self.lineEdit_class = QLabel(self.groupBox_3)
        self.lineEdit_class.setAlignment(self.lineEdit_name.alignment())
        self.lineEdit_class.setText("未识别")

        self.label_status_title = QLabel(self.groupBox_3)
        self.label_status_title.setText("状态:")

        self.lineEdit_status = QLabel(self.groupBox_3)
        self.lineEdit_status.setAlignment(self.lineEdit_name.alignment())
        self.lineEdit_status.setText("未识别")

        self.label_monitor_mode = QLabel(self.groupBox_3)
        self.label_monitor_mode.setText("监测状态：未开始")
        self.label_monitor_mode.setWordWrap(True)

        self.pushButton_checkout = QPushButton(self.groupBox_2)
        self.pushButton_checkout.setText("签退")
        self.pushButton_checkout.clicked.connect(self.sign_out)

        self.lineEdit_name.setReadOnly(True)
        self.lineEdit_sno.setReadOnly(True)
        self.lineEdit_checkin_time.setReadOnly(True)

    def _beautify_ui(self):
        apply_page_theme(self)
        style_button(self.pushButton_open, "primary")
        style_button(self.pushButton_stop, "danger")
        style_button(self.pushButton_checkin, "success")
        style_button(self.pushButton_checkout, "warning")
        style_hint_label(self.label_monitor_mode, "info")
        style_hint_label(self.lineEdit_class, "info")
        style_status_badge(self.lineEdit_status, "未识别")

        self.label_current.setStyleSheet(
            "color:#FFFFFF; background:#2563EB; border-radius:8px; padding:4px 8px; font:700 14px 'Microsoft YaHei';"
        )

        if hasattr(self, "label_open"):
            self.label_open.hide()
        if hasattr(self, "label_close"):
            self.label_close.hide()

    def _apply_responsive_layout(self):
        w = max(self.width(), 1080)
        h = max(self.height(), 760)
        margin = 20
        gap = 18

        left_w = max(560, int((w - margin * 2 - gap) * 0.56))
        right_w = max(360, w - margin * 2 - gap - left_w)
        top_h = max(340, int((h - margin * 2) * 0.56))
        bottom_y = margin + top_h + 10
        bottom_h = h - margin - bottom_y
        right_x = margin + left_w + gap

        self.label_tablecard.setGeometry(margin, margin, left_w, top_h)
        self.label_6.setGeometry(margin + 16, margin + 8, 90, 30)
        self.pushButton_open.setGeometry(margin + 86, margin + 55, 110, 34)
        self.pushButton_stop.setGeometry(margin + 226, margin + 55, 110, 34)
        self.label_current.setGeometry(margin + left_w - 130, margin + 8, 110, 30)
        self.label_frame.setGeometry(margin + 26, margin + 100, left_w - 52, top_h - 118)

        self.groupBox_2.setGeometry(margin, bottom_y, left_w, bottom_h)
        face_w = left_w - 260
        self.label_face.setGeometry(24, 24, face_w, bottom_h - 48)
        action_x = left_w - 214
        self.pushButton_checkin.setGeometry(action_x, max(40, bottom_h // 2 - 55), 150, 42)
        self.pushButton_checkout.setGeometry(action_x, max(90, bottom_h // 2 + 5), 150, 42)

        self.groupBox_3.setGeometry(right_x, margin, right_w, h - margin * 2)
        field_left = 34
        label_w = 92
        value_x = 130
        value_w = right_w - value_x - 36
        row_h = 30
        y0 = 52
        step = 56

        self.label_3.setGeometry(field_left, y0, label_w, row_h)
        self.lineEdit_name.setGeometry(value_x, y0, value_w, row_h)
        self.label_2.setGeometry(field_left, y0 + step, label_w, row_h)
        self.lineEdit_sno.setGeometry(value_x, y0 + step, value_w, row_h)
        self.label_5.setGeometry(field_left, y0 + step * 2, label_w, row_h)
        self.progressBar.setGeometry(value_x, y0 + step * 2 + 2, value_w, 24)
        self.label_13.setGeometry(field_left, y0 + step * 3, label_w, row_h)
        self.lineEdit_checkin_time.setGeometry(value_x, y0 + step * 3, value_w, row_h)
        self.label_class_title.setGeometry(field_left, y0 + step * 4, label_w, row_h)
        self.lineEdit_class.setGeometry(value_x, y0 + step * 4, value_w, row_h)
        self.label_status_title.setGeometry(field_left, y0 + step * 5, label_w, row_h)
        self.lineEdit_status.setGeometry(value_x, y0 + step * 5, value_w, row_h)

        self.label_12.setGeometry(field_left, y0 + step * 6 - 8, label_w + 20, row_h)
        self.label_monitor_mode.setGeometry(18, h - margin * 2 - 76, right_w - 36, 58)

        if hasattr(self, "label"):
            self.label.hide()
        if hasattr(self, "label_open"):
            self.label_open.hide()
        if hasattr(self, "label_close"):
            self.label_close.hide()

    def resizeEvent(self, event):
        super(FaceCheckin, self).resizeEvent(event)
        self._apply_responsive_layout()

    def open_cam(self):
        if self.CAM_OPEN_FLAG:
            QMessageBox.warning(self, "提示", "摄像头已打开，请勿重复打开。")
            return

        self.timer_camera = QTimer()
        self.cap, source_text, tried_text = model.configuration.open_camera_capture(cv2)
        if self.cap is None:
            msg = "未检测到可用的本地摄像头。\n请检查摄像头是否已连接或被其他程序占用。"
            if tried_text:
                msg += f"\n已尝试：{tried_text}"
            QMessageBox.warning(self, "摄像头打开失败", msg)
            return

        self.timer_camera.start(10)
        self.timer_camera.timeout.connect(self.show_frame)
        self.CAM_OPEN_FLAG = True
        QMessageBox.information(self, "摄像头已连接", f"当前已连接本地摄像头：{source_text}")

    def stop_cam(self):
        if not self.CAM_OPEN_FLAG:
            QMessageBox.warning(self, "提示", "摄像头尚未打开。")
            return

        self._stop_monitoring(update_tip=False)
        self.timer_camera.stop()
        self.label_frame.clear()
        self.cap.release()
        self.CAM_OPEN_FLAG = False
        self.label_monitor_mode.setText("监测状态：未开始")
        style_hint_label(self.label_monitor_mode, "info")

    def show_label(self, frame, label):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, bytes_per_component = frame.shape
        bytes_per_line = bytes_per_component * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        label.setPixmap(QPixmap.fromImage(q_image))
        label.setScaledContents(True)

    def show_frame(self):
        if self.cap.isOpened():
            ret, self.frame = self.cap.read()
            if ret:
                self.show_label(self.frame, self.label_frame)
                self._run_monitor_cycle()

    def _reset_feedback(self):
        self.lineEdit_sno.clear()
        self.lineEdit_name.clear()
        self.lineEdit_class.setText("未识别")
        self.lineEdit_checkin_time.clear()
        self.progressBar.setValue(0)
        self.label_face.setPixmap(QPixmap(""))
        style_hint_label(self.lineEdit_class, "info")
        style_status_badge(self.lineEdit_status, "未识别")
        self.timer_close.stop()

    def _update_feedback(self, sid, name, class_name, status, similarity, frame_photo):
        self.lineEdit_sno.setText(str(sid))
        self.lineEdit_name.setText(str(name))
        self.lineEdit_class.setText(str(class_name))
        self.lineEdit_checkin_time.setText(time.strftime("%X", time.localtime()))
        self.progressBar.setValue(int(similarity))
        self.show_label(frame_photo, self.label_face)
        style_hint_label(self.lineEdit_class, "info")
        style_status_badge(self.lineEdit_status, str(status))
        self.timer_close.start(3000)

    def _recognize_once(self, popup=False):
        if not self.CAM_OPEN_FLAG or not hasattr(self, "frame"):
            if popup:
                QMessageBox.warning(self, "提示", "请先打开摄像头并等待画面。")
            return None

        result, frame_photo, search_result = self.re.check_in(self.frame, self.student_info_all)
        if result == 0:
            if popup:
                QMessageBox.warning(self, "提示", "未检测到人脸。")
            return None

        if result == 1 and search_result is not None and search_result[2] >= model.configuration.SIMILARITY_THRESHOLD:
            return {
                "sid": str(search_result[0]),
                "name": str(search_result[1]),
                "similarity": int(search_result[2]),
                "frame_photo": frame_photo,
            }

        self.show_label(frame_photo, self.label_face)
        if popup:
            QMessageBox.warning(self, "提示", "识别失败或相似度过低。")
        return None

    def _run_checkin_once(self, popup=False):
        recognized = self._recognize_once(popup=popup)
        if not recognized:
            return

        sid = recognized["sid"]
        name = recognized["name"]
        similarity = recognized["similarity"]
        frame_photo = recognized["frame_photo"]

        now_ts = time.monotonic()
        prev_ts = self.student_last_detect_ts.get(sid, 0.0)
        if now_ts - prev_ts < self.student_cooldown_sec:
            self._update_feedback(sid, name, "", "重复识别(冷却中)", similarity, frame_photo)
            return

        service_result = self.attendance_service.process_auto_checkin(sid, name)
        self.student_last_detect_ts[sid] = now_ts

        status_text = service_result.get("status", "未更新")
        if service_result.get("code") == "duplicate":
            status_text = f"{status_text}(已去重)"
        if service_result.get("code") == "out_of_window":
            status_text = "不在签到时段"
        if service_result.get("code") == "class_missing":
            status_text = "班级未设置"

        class_text = service_result.get("class_name", "") or "未设置"
        self._update_feedback(
            service_result.get("student_id", sid),
            service_result.get("name", name),
            class_text,
            status_text,
            similarity,
            frame_photo,
        )
        self.label_monitor_mode.setText(
            f"监测状态：进行中（最近识别：{service_result.get('name', name)} {status_text}）"
        )
        style_hint_label(self.label_monitor_mode, "success" if service_result.get("ok") else "warning")

        if popup and service_result.get("ok"):
            QMessageBox.information(self, "签到成功", f"签到状态：{status_text}")
        elif popup and not service_result.get("ok"):
            QMessageBox.warning(self, "提示", service_result.get("message", "签到失败"))

    def sign_out(self):
        recognized = self._recognize_once(popup=True)
        if not recognized:
            return

        sid = recognized["sid"]
        name = recognized["name"]
        similarity = recognized["similarity"]
        frame_photo = recognized["frame_photo"]

        service_result = self.attendance_service.process_checkout(sid, name)
        status_text = service_result.get("status", "未更新")
        if service_result.get("code") == "duplicate_checkout":
            status_text = f"{status_text}(已签退)"

        class_text = service_result.get("class_name", "") or "未设置"
        self._update_feedback(
            service_result.get("student_id", sid),
            service_result.get("name", name),
            class_text,
            status_text,
            similarity,
            frame_photo,
        )
        self.label_monitor_mode.setText(
            f"监测状态：已执行签退（{service_result.get('name', name)} {status_text}）"
        )
        style_hint_label(self.label_monitor_mode, "success" if service_result.get("ok") else "warning")

        if service_result.get("ok"):
            QMessageBox.information(self, "签退成功", service_result.get("message", "签退成功"))
        else:
            QMessageBox.warning(self, "提示", service_result.get("message", "签退失败"))

    def _run_monitor_cycle(self):
        if not self.monitoring_enabled:
            return
        now_ts = time.monotonic()
        if (now_ts - self.last_detect_ts) * 1000 < self.detect_interval_ms:
            return
        self.last_detect_ts = now_ts
        try:
            self._run_checkin_once(popup=False)
        except Exception as exc:
            self.label_monitor_mode.setText(f"监测状态：异常 - {exc}")
            style_hint_label(self.label_monitor_mode, "danger")

    def toggle_monitoring(self):
        if not self.CAM_OPEN_FLAG or not hasattr(self, "frame"):
            QMessageBox.warning(self, "提示", "请先打开摄像头并等待画面。")
            return

        if self.monitoring_enabled:
            self._stop_monitoring(update_tip=True)
            return

        self.monitoring_enabled = True
        self.pushButton_checkin.setText("停止监测")
        style_button(self.pushButton_checkin, "danger")
        self.label_monitor_mode.setText("监测状态：进行中")
        style_hint_label(self.label_monitor_mode, "success")
        self.last_detect_ts = 0.0
        self.student_last_detect_ts = {}
        QMessageBox.information(self, "提示", "已开始课堂实时监测。")

    def _stop_monitoring(self, update_tip=True):
        self.monitoring_enabled = False
        self.pushButton_checkin.setText("开始监测")
        style_button(self.pushButton_checkin, "success")
        if update_tip:
            self.label_monitor_mode.setText("监测状态：已停止")
            style_hint_label(self.label_monitor_mode, "warning")

    def check_in(self):
        self._reset_feedback()
        self._run_checkin_once(popup=True)

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            self.label_current.setText(time.strftime("%X", time.localtime()))
            minute_key = time.strftime("%Y-%m-%d %H:%M", time.localtime())
            if (
                self.monitoring_enabled
                and self.CAM_OPEN_FLAG
                and minute_key != self._last_absence_sync_key
            ):
                self._last_absence_sync_key = minute_key
                try:
                    day = datetime.strptime(time.strftime("%Y-%m-%d", time.localtime()), "%Y-%m-%d").date()
                    self.attendance_service.ensure_absence_records(day, day)
                except Exception:
                    pass

    def close_all(self):
        self._stop_monitoring(update_tip=False)
        if self.CAM_OPEN_FLAG:
            self.timer_camera.stop()
            self.cap.release()
        try:
            self.dbcon.close_con()
        except Exception:
            pass
        self.close()

    def close_feedback(self):
        self.timer_close.stop()
