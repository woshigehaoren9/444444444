from datetime import datetime

from PyQt5.QtCore import QBasicTimer, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMessageBox, QWidget

from model.attendance_service import AttendanceService
from model.connectsqlite import ConnectSqlite
import model.configuration
from view.facecheck import Ui_FaceCheckForm
import cv2
import time


class LegacyFaceCheckin(QWidget, Ui_FaceCheckForm):

    def __init__(self, re, parent=None):
        super(LegacyFaceCheckin, self).__init__(parent)
        self.setupUi(self)
        self._localize_ui()

        self.timer = QBasicTimer()
        self.timer.start(1000, self)
        self.label_current.setText(time.strftime("%X", time.localtime()))

        self.CAM_OPEN_FLAG = False
        self.re = re
        self.dbcon = ConnectSqlite(model.configuration.DATABASE_PATH)
        self.student_info_all = self.dbcon.load_registered_data()
        self.attendance_service = AttendanceService(self.dbcon)

        self.pushButton_open.clicked.connect(self.open_cam)
        self.pushButton_stop.clicked.connect(self.stop_cam)
        self.pushButton_checkin.clicked.connect(self.check_in)
        self.label_open.setVisible(False)

        self.timer_close = QTimer()
        self.timer_close.timeout.connect(self.close_door)

    def _localize_ui(self):
        self.setWindowTitle("人脸签到")
        if hasattr(self, "label_6"):
            self.label_6.setText("摄像头")
        if hasattr(self, "pushButton_open"):
            self.pushButton_open.setText("打开")
        if hasattr(self, "pushButton_stop"):
            self.pushButton_stop.setText("关闭")
        if hasattr(self, "groupBox_2"):
            self.groupBox_2.setTitle("人脸识别")
        if hasattr(self, "groupBox_3"):
            self.groupBox_3.setTitle("识别结果")
        if hasattr(self, "label_3"):
            self.label_3.setText("姓名:")
        if hasattr(self, "label_2"):
            self.label_2.setText("学号:")
        if hasattr(self, "label_5"):
            self.label_5.setText("相似度:")
        if hasattr(self, "label_12"):
            self.label_12.setText("考勤指示灯（绿灯表示通过）")
        if hasattr(self, "label_13"):
            self.label_13.setText("签到时间:")

    def open_cam(self):
        if self.CAM_OPEN_FLAG:
            QMessageBox.warning(self, "提示", "摄像头已打开，请勿重复打开。", QMessageBox.Yes, QMessageBox.Yes)
            return

        self.timer_camera = QTimer()
        self.cap, source_text, tried_text = model.configuration.open_camera_capture(cv2)
        if self.cap is None:
            msg = "未检测到可用的本地摄像头。\n请检查摄像头是否已连接或被其他程序占用。"
            if tried_text:
                msg += f"\n已尝试：{tried_text}"
            QMessageBox.warning(self, "摄像头打开失败", msg, QMessageBox.Yes, QMessageBox.Yes)
            return

        self.timer_camera.start(10)
        self.timer_camera.timeout.connect(self.show_frame)
        self.CAM_OPEN_FLAG = True
        QMessageBox.information(self, "摄像头已连接", f"当前已连接本地摄像头：{source_text}", QMessageBox.Yes, QMessageBox.Yes)

    def stop_cam(self):
        if self.CAM_OPEN_FLAG:
            self.timer_camera.stop()
            self.label_frame.clear()
            self.cap.release()
            self.CAM_OPEN_FLAG = False
        else:
            QMessageBox.warning(self, "提示", "摄像头尚未打开。", QMessageBox.Yes, QMessageBox.Yes)

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

    def check_in(self):
        self.lineEdit_sno.setText("")
        self.lineEdit_name.setText("")
        self.progressBar.setValue(0)
        self.label_face.setPixmap(QPixmap(""))
        self.lineEdit_checkin_time.setText("")
        self.label_open.setVisible(False)
        self.timer_close.stop()

        if not self.CAM_OPEN_FLAG:
            QMessageBox.warning(self, "提示", "请先打开摄像头。", QMessageBox.Yes, QMessageBox.Yes)
            return

        result, frame_photo, search_result = self.re.check_in(self.frame, self.student_info_all)
        if result == 0:
            QMessageBox.warning(self, "提示", "未检测到人脸。", QMessageBox.Yes, QMessageBox.Yes)
            return

        if result == 1 and search_result[2] >= model.configuration.SIMILARITY_THRESHOLD:
            self.label_open.setVisible(True)
            self.timer_close.start(5000)
            self.lineEdit_sno.setText(str(search_result[0]))
            self.lineEdit_name.setText(str(search_result[1]))
            self.progressBar.setValue(int(search_result[2]))
            self.show_label(frame_photo, self.label_face)
            self.lineEdit_checkin_time.setText(time.strftime("%X", time.localtime()))

            change_time = datetime.now().strftime("%Y/%m/%d %H:%M")
            insert_list = [str(search_result[0]), str(search_result[1]), change_time]
            save_result = self.dbcon.insert_checkin_table(insert_list)
            if save_result != 0:
                QMessageBox.warning(self, "错误", "写入数据库失败！\n" + save_result, QMessageBox.Yes, QMessageBox.Yes)
        else:
            self.show_label(frame_photo, self.label_face)
            QMessageBox.warning(self, "人脸识别失败", "识别失败：人脸未注册或相似度过低，请重试。", QMessageBox.Yes, QMessageBox.Yes)

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            self.label_current.setText(time.strftime("%X", time.localtime()))

    def close_all(self):
        if self.CAM_OPEN_FLAG:
            self.timer_camera.stop()
            self.cap.release()
        try:
            self.dbcon.close_con()
        except Exception:
            pass
        self.close()

    def close_door(self):
        self.label_open.setVisible(False)
        self.timer_close.stop()
        self.lineEdit_sno.setText("")
        self.lineEdit_name.setText("")
        self.progressBar.setValue(0)
        self.label_face.setPixmap(QPixmap(""))
        self.lineEdit_checkin_time.setText("")


# 兼容旧导入路径：统一复用新版签到页，避免旧逻辑继续写入 re_record。
from control.faceCheckinV2 import FaceCheckin  # noqa: E402
