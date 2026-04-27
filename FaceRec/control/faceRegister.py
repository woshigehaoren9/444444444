import os

import cv2
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QFileDialog, QLabel, QLineEdit, QMessageBox, QWidget

import model.configuration
from model.connectsqlite import ConnectSqlite
from view.faceregister import Ui_FaceRegisterForm
from view.ui_theme import apply_page_theme, style_button, style_hint_label


class FaceRegister(QWidget, Ui_FaceRegisterForm):
    def __init__(self, re, parent=None):
        super(FaceRegister, self).__init__(parent)
        self.setupUi(self)
        self.setMinimumSize(1080, 760)

        self.CAM_OPEN_FLAG = False
        self.re = re
        self.dbcon = ConnectSqlite(model.configuration.DATABASE_PATH)

        self.face_fingerprint = None
        self.frame_photo = None

        self._init_class_widgets()
        self._localize_ui()
        self._beautify_ui()
        self._apply_responsive_layout()

        self.pushButton_open.clicked.connect(self.open_cam)
        self.pushButton_stop.clicked.connect(self.stop_cam)
        self.pushButton_take_photo.clicked.connect(self.take_photo)
        self.pushButton_register.clicked.connect(self.register)
        if hasattr(self, "pushButton_import_image"):
            self.pushButton_import_image.clicked.connect(self.import_single_image)
        if hasattr(self, "pushButton_import_folder"):
            self.pushButton_import_folder.clicked.connect(self.import_folder_images)

    def _init_class_widgets(self):
        self.label_class = QLabel(self.groupBox_3)
        self.label_class.setFont(self.label_2.font())
        self.label_class.setText("班级:")

        self.lineEdit_class = QLineEdit(self.groupBox_3)
        self.lineEdit_class.setFont(self.lineEdit_name.font())
        self.lineEdit_class.setPlaceholderText("例如：计科1班")
        self.lineEdit_name.setPlaceholderText("请输入姓名")
        self.lineEdit_sno.setPlaceholderText("请输入学号")

        self.label_hint = QLabel(self.groupBox_3)
        self.label_hint.setText("支持文件命名规则：学号_姓名_班级.jpg")
        self.label_hint.setWordWrap(True)
        style_hint_label(self.label_hint, "info")

    def _localize_ui(self):
        self.setWindowTitle("人脸录入")
        self.label_6.setText("摄像头")
        self.pushButton_open.setText("打开")
        self.pushButton_open.setToolTip("打开本地摄像头后再拍照采集")
        self.pushButton_stop.setText("关闭")
        self.groupBox_2.setTitle("拍照采集")
        self.groupBox_3.setTitle("学生信息")
        self.pushButton_register.setText("保存录入")
        if hasattr(self, "pushButton_import_image"):
            self.pushButton_import_image.setText("单张导入")
        if hasattr(self, "pushButton_import_folder"):
            self.pushButton_import_folder.setText("批量导入")
        self.label_3.setText("姓名:")
        self.label_2.setText("学号:")
        self.label_4.setText("人脸特征")
        self.pushButton_take_photo.setText("拍照")

    def _beautify_ui(self):
        apply_page_theme(self)
        style_button(self.pushButton_open, "primary")
        style_button(self.pushButton_stop, "danger")
        style_button(self.pushButton_take_photo, "warning")
        style_button(self.pushButton_register, "success")
        if hasattr(self, "pushButton_import_image"):
            style_button(self.pushButton_import_image, "default")
        if hasattr(self, "pushButton_import_folder"):
            style_button(self.pushButton_import_folder, "default")

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
        self.label_frame.setGeometry(margin + 26, margin + 100, left_w - 52, top_h - 118)

        self.groupBox_2.setGeometry(margin, bottom_y, left_w, bottom_h)
        self.pushButton_take_photo.setGeometry(26, max(40, bottom_h // 2 - 22), 94, 42)
        self.label_face.setGeometry(140, 24, left_w - 164, bottom_h - 48)

        self.groupBox_3.setGeometry(right_x, margin, right_w, h - margin * 2)
        feature_w = min(240, right_w - 70)
        feature_x = (right_w - feature_w) // 2
        self.label_face_feature.setGeometry(feature_x, 52, feature_w, 190)
        self.label_4.setGeometry(feature_x + 18, 24, 140, 24)

        field_left = 44
        label_w = 56
        edit_x = field_left + label_w
        edit_w = right_w - edit_x - 44
        y_name = 286
        y_sid = 340
        y_class = 394
        self.label_3.setGeometry(field_left, y_name, label_w, 28)
        self.lineEdit_name.setGeometry(edit_x, y_name, edit_w, 30)
        self.label_2.setGeometry(field_left, y_sid, label_w, 28)
        self.lineEdit_sno.setGeometry(edit_x, y_sid, edit_w, 30)
        self.label_class.setGeometry(field_left, y_class, label_w, 28)
        self.lineEdit_class.setGeometry(edit_x, y_class, edit_w, 30)

        self.pushButton_register.setGeometry((right_w - 140) // 2, 454, 140, 40)
        if hasattr(self, "pushButton_import_image"):
            btn_w = (right_w - 72) // 2
            self.pushButton_import_image.setGeometry(24, 514, btn_w, 34)
        if hasattr(self, "pushButton_import_folder"):
            btn_w = (right_w - 72) // 2
            self.pushButton_import_folder.setGeometry(24 + btn_w + 24, 514, btn_w, 34)
        self.label_hint.setGeometry(20, h - margin * 2 - 62, right_w - 40, 44)

    def resizeEvent(self, event):
        super(FaceRegister, self).resizeEvent(event)
        self._apply_responsive_layout()

    def open_cam(self):
        if self.CAM_OPEN_FLAG:
            QMessageBox.warning(self, "提示", "摄像头已打开，请勿重复操作。")
            return

        self.timer_camera = QTimer()
        self.cap, source_text, tried_text = model.configuration.open_camera_capture(cv2)
        if self.cap is None:
            msg = "未检测到可用的本地摄像头。\n请检查摄像头是否已连接或被其他程序占用。"
            if tried_text:
                msg += f"\n已尝试：{tried_text}"
            QMessageBox.warning(self, "摄像头打开失败", msg)
            return

        self.cap.set(3, 640)
        self.cap.set(4, 480)
        self.timer_camera.start(10)
        self.timer_camera.timeout.connect(self.show_frame)
        self.CAM_OPEN_FLAG = True
        QMessageBox.information(self, "摄像头已连接", f"当前已连接本地摄像头：{source_text}")

    def stop_cam(self):
        if self.CAM_OPEN_FLAG:
            self.timer_camera.stop()
            self.label_frame.clear()
            self.cap.release()
            self.CAM_OPEN_FLAG = False
        else:
            QMessageBox.warning(self, "提示", "摄像头尚未打开。")

    def show_frame(self):
        if self.cap.isOpened():
            ret, self.frame = self.cap.read()
            if ret:
                self.show_label(self.frame, self.label_frame)

    def take_photo(self):
        self.face_fingerprint = None
        self.frame_photo = None
        self.label_face.setPixmap(QPixmap(""))
        self.label_face_feature.setPixmap(QPixmap(""))

        if not self.CAM_OPEN_FLAG:
            QMessageBox.warning(self, "提示", "请先打开摄像头。")
            return

        code, self.frame_photo, frame_feature, self.face_fingerprint = self.re.take_photo(self.frame)
        if code == 0:
            self.show_label(self.frame_photo, self.label_face)
            QMessageBox.warning(self, "提示", "未检测到人脸，请重试。")
        elif code == 1:
            self.show_label(self.frame_photo, self.label_face)
            self.show_label(frame_feature, self.label_face_feature)
        else:
            self.show_label(self.frame_photo, self.label_face)
            QMessageBox.warning(self, "提示", "检测到多人脸，请只保留一人。")

    @staticmethod
    def _parse_filename_rule(file_path):
        base = os.path.splitext(os.path.basename(file_path))[0]
        parts = base.split("_")
        if len(parts) < 3:
            return None, "文件名不符合规则：学号_姓名_班级.jpg"
        student_id = parts[0].strip()
        name = parts[1].strip()
        class_name = "_".join(parts[2:]).strip()
        if not student_id:
            return None, "文件名缺少学号"
        if not name:
            return None, "文件名缺少姓名"
        if not class_name:
            return None, "班级缺失"
        return (student_id, name, class_name), ""

    def _validate_meta(self, student_id, name, class_name):
        if not student_id:
            return False, "学号不能为空"
        if not name:
            return False, "姓名不能为空"
        if not class_name:
            return False, "班级缺失"
        class_text = class_name.strip()
        if class_text == "未分班" or "未分班" in class_text:
            return False, "班级不能为“未分班”，请填写真实班级"
        return True, ""

    def _extract_feature_from_image(self, image_path):
        return self.re.extract_face_fingerprint_from_image_path(image_path)

    def _save_face(self, student_id, name, class_name, face_fingerprint, frame_photo):
        if self.dbcon.sid_exists(student_id):
            return False, "学号重复"
        result = self.dbcon.insert_face_record(student_id, name, class_name, face_fingerprint, frame_photo)
        if result != 0:
            return False, f"数据库写入失败：{result}"
        return True, ""

    def import_single_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择单张图片",
            "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp)",
        )
        if not path:
            return

        sid_text = self.lineEdit_sno.text().strip()
        name_text = self.lineEdit_name.text().strip()
        class_text = self.lineEdit_class.text().strip()

        if sid_text or name_text or class_text:
            ok, msg = self._validate_meta(sid_text, name_text, class_text)
            if not ok:
                QMessageBox.warning(self, "提示", msg)
                return
            student_id, name, class_name = sid_text, name_text, class_text
        else:
            parsed, msg = self._parse_filename_rule(path)
            if not parsed:
                QMessageBox.warning(self, "提示", msg)
                return
            student_id, name, class_name = parsed

        code, frame_photo, frame_feature, face_fingerprint = self._extract_feature_from_image(path)
        if code == -1:
            QMessageBox.warning(self, "提示", "图片读取失败，请检查文件是否损坏。")
            return
        if code == 0:
            QMessageBox.warning(self, "提示", "图片中无人脸。")
            return
        if code == 2:
            QMessageBox.warning(self, "提示", "图片中多人脸。")
            return

        ok, err = self._save_face(student_id, name, class_name, face_fingerprint, frame_photo)
        if not ok:
            QMessageBox.warning(self, "提示", err)
            return

        self.face_fingerprint = face_fingerprint
        self.frame_photo = frame_photo
        self.lineEdit_sno.setText(student_id)
        self.lineEdit_name.setText(name)
        self.lineEdit_class.setText(class_name)
        self.show_label(frame_photo, self.label_face)
        if frame_feature is not None and getattr(frame_feature, "size", 0) > 0:
            self.show_label(frame_feature, self.label_face_feature)
        else:
            self.label_face_feature.setPixmap(QPixmap(""))
        QMessageBox.information(self, "成功", "单张图片导入建库成功。")

    def import_folder_images(self):
        folder = QFileDialog.getExistingDirectory(self, "选择图片文件夹", "")
        if not folder:
            return

        exts = {".jpg", ".jpeg", ".png", ".bmp"}
        files = []
        for filename in os.listdir(folder):
            image_path = os.path.join(folder, filename)
            if os.path.isfile(image_path) and os.path.splitext(filename)[1].lower() in exts:
                files.append(image_path)
        files.sort()

        if not files:
            QMessageBox.warning(self, "提示", "所选文件夹中没有可导入图片。")
            return

        all_sids = set(self.dbcon.return_all_sid())
        seen_in_batch = set()

        total = len(files)
        success = 0
        fail_rule = 0
        fail_no_face = 0
        fail_multi_face = 0
        fail_duplicate = 0
        fail_missing_class = 0
        fail_db = 0

        for image_path in files:
            parsed, msg = self._parse_filename_rule(image_path)
            if not parsed:
                if msg == "班级缺失":
                    fail_missing_class += 1
                else:
                    fail_rule += 1
                continue

            student_id, name, class_name = parsed
            if student_id in all_sids or student_id in seen_in_batch:
                fail_duplicate += 1
                continue

            code, frame_photo, _, face_fingerprint = self._extract_feature_from_image(image_path)
            if code == 0:
                fail_no_face += 1
                continue
            if code == 2:
                fail_multi_face += 1
                continue
            if code != 1:
                fail_db += 1
                continue

            ok, _ = self._save_face(student_id, name, class_name, face_fingerprint, frame_photo)
            if ok:
                success += 1
                seen_in_batch.add(student_id)
            else:
                fail_db += 1

        failed = total - success
        msg = (
            f"批量导入完成。\n"
            f"总文件数：{total}\n"
            f"成功：{success}\n"
            f"失败：{failed}\n"
            f"- 文件名不合规：{fail_rule}\n"
            f"- 班级缺失：{fail_missing_class}\n"
            f"- 图片中无人脸：{fail_no_face}\n"
            f"- 图片中多人脸：{fail_multi_face}\n"
            f"- 学号重复：{fail_duplicate}\n"
            f"- 数据库失败：{fail_db}"
        )
        QMessageBox.information(self, "批量导入结果", msg)

    def register(self):
        name = self.lineEdit_name.text().strip()
        student_id = self.lineEdit_sno.text().strip()
        class_name = self.lineEdit_class.text().strip()

        ok, msg = self._validate_meta(student_id, name, class_name)
        if not ok:
            QMessageBox.warning(self, "提示", msg)
            return

        if self.face_fingerprint is None:
            QMessageBox.warning(self, "提示", "未提取到人脸特征，请先拍照。")
            return

        success, err = self._save_face(student_id, name, class_name, self.face_fingerprint, self.frame_photo)
        if success:
            QMessageBox.information(self, "成功", "人脸录入成功。")
            self.face_fingerprint = None
            self.frame_photo = None
            self.label_face.setPixmap(QPixmap(""))
            self.label_face_feature.setPixmap(QPixmap(""))
            self.lineEdit_sno.clear()
            self.lineEdit_name.clear()
            self.lineEdit_class.clear()
        else:
            QMessageBox.warning(self, "错误", err)

    def show_label(self, frame, label):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, bytes_per_component = frame.shape
        bytes_per_line = bytes_per_component * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        label.setPixmap(QPixmap.fromImage(q_image))
        label.setScaledContents(True)

    def close_all(self):
        if self.CAM_OPEN_FLAG:
            self.timer_camera.stop()
            self.cap.release()
        try:
            self.dbcon.close_con()
        except Exception:
            pass
        self.close()
