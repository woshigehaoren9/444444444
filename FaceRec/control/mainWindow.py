# -*- coding:utf-8 -*-
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QPushButton

import model.configuration
from control.attendanceManage import CheckInRecord
from control.faceCheckinV2 import FaceCheckin
from control.faceRecord import FaceRecord
from control.faceRegister import FaceRegister
from control.recordView import RecordView
from model.recognizer import recognizer
from view.mainwindow import Ui_MainWindow
from view.ui_theme import apply_page_theme, set_nav_active, style_nav_button


class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        self.re = recognizer(model.configuration.PREDICTOR_PATH, model.configuration.FACE_REC_MODEL_PATH)
        self._setup_ui()
        self._bind_events()

    def _setup_ui(self):
        self.setWindowTitle("基于 Python + OpenCV 的课堂人脸考勤系统")
        self.resize(1360, 860)
        self.setMinimumSize(1280, 820)
        apply_page_theme(self.centralwidget)

        self.label_8.setText("课堂人脸考勤")
        self.label_8.setStyleSheet("color:#FFFFFF; background:transparent; font:700 20px 'Microsoft YaHei';")

        self.pushButton_record_view = QPushButton(self.centralwidget)
        self.pushButton_record_view.setText("  记录查看")
        self.pushButton_record_view.setIcon(self.pushButton_checkin_record.icon())
        self.pushButton_record_view.setIconSize(self.pushButton_checkin_record.iconSize())

        self.nav_buttons = [
            self.pushButton_about,
            self.pushButton_register,
            self.pushButton_checkin,
            self.pushButton_record_view,
            self.pushButton_face_record,
            self.pushButton_checkin_record,
            self.pushButton_exit,
        ]
        for btn in self.nav_buttons:
            style_nav_button(btn, active=False)

        self.pushButton_about.setText("  系统首页")
        self.pushButton_register.setText("  人脸录入")
        self.pushButton_checkin.setText("  人脸签到")
        self.pushButton_record_view.setText("  记录查看")
        self.pushButton_face_record.setText("  人脸库管理")
        self.pushButton_checkin_record.setText("  考勤管理")
        self.pushButton_exit.setText("  退出系统")

        self.pushButton_about.setToolTip("返回系统首页")
        self.pushButton_register.setToolTip("进入学生人脸录入页面")
        self.pushButton_checkin.setToolTip("进入课堂实时签到与签退页面")
        self.pushButton_record_view.setToolTip("查看考勤明细与统计结果")
        self.pushButton_face_record.setToolTip("查看并维护学生人脸库")
        self.pushButton_checkin_record.setToolTip("管理考勤规则并导出报表")

        self.label_logo.setText("")
        self.label_logo.setAlignment(Qt.AlignCenter)
        self.label_logo.setWordWrap(False)
        self.label_logo.setStyleSheet("border-image: url(D:/FaceRec/view/pic/BS.png) 0 0 0 0 stretch stretch;")

        self._apply_frame_geometry()
        set_nav_active(self.nav_buttons[:-1], self.pushButton_about)

    def _apply_frame_geometry(self):
        nav_width = 251
        total_w = max(self.width(), self.minimumWidth())
        total_h = max(self.height(), self.minimumHeight())

        self.label_12.setGeometry(0, 0, nav_width, total_h)
        self.verticalLayoutWidget.setGeometry(nav_width, 0, total_w - nav_width, total_h)
        self.label_logo.setGeometry(nav_width + 10, 0, total_w - nav_width - 10, total_h)
        self.label_8.setGeometry(10, 20, nav_width - 20, 41)

        top = 90
        step = 60
        page_buttons = [
            self.pushButton_about,
            self.pushButton_register,
            self.pushButton_checkin,
            self.pushButton_record_view,
            self.pushButton_face_record,
            self.pushButton_checkin_record,
        ]
        for idx, btn in enumerate(page_buttons):
            btn.setGeometry(0, top + idx * step, nav_width, 51)

        exit_y = max(top + len(page_buttons) * step, total_h - 70)
        self.pushButton_exit.setGeometry(0, exit_y, nav_width, 51)

    def resizeEvent(self, event):
        super(MyWindow, self).resizeEvent(event)
        self._apply_frame_geometry()

    def _bind_events(self):
        self.pushButton_about.clicked.connect(self.about)
        self.pushButton_register.clicked.connect(self.face_register)
        self.pushButton_checkin.clicked.connect(self.check_in)
        self.pushButton_record_view.clicked.connect(self.record_view)
        self.pushButton_face_record.clicked.connect(self.face_record)
        self.pushButton_checkin_record.clicked.connect(self.check_in_record)
        self.pushButton_exit.clicked.connect(self.exit)

    def _clear_content(self):
        while self.verticalLayout.count():
            item = self.verticalLayout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                if hasattr(widget, "close_all"):
                    widget.close_all()
                else:
                    widget.close()

    def _switch_page(self, widget, active_btn):
        self._clear_content()
        self.close_logo()
        self.verticalLayout.addWidget(widget)
        set_nav_active(self.nav_buttons[:-1], active_btn)

    def face_register(self):
        self._switch_page(FaceRegister(self.re), self.pushButton_register)

    def check_in(self):
        self._switch_page(FaceCheckin(self.re), self.pushButton_checkin)

    def record_view(self):
        self._switch_page(RecordView(), self.pushButton_record_view)

    def face_record(self):
        self._switch_page(FaceRecord(), self.pushButton_face_record)

    def check_in_record(self):
        self._switch_page(CheckInRecord(), self.pushButton_checkin_record)

    def about(self):
        self._clear_content()
        self.label_logo.setVisible(True)
        set_nav_active(self.nav_buttons[:-1], self.pushButton_about)

    def exit(self):
        self.close()

    def close_logo(self):
        self.label_logo.setVisible(False)
