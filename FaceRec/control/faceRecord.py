import cv2
import numpy as np
import model.configuration
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QImage, QPixmap
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHeaderView,
    QLabel,
    QMessageBox,
    QTableWidgetItem,
    QWidget,
    QInputDialog,
)

from model.connectsqlite import ConnectSqlite
from view.facemodify import Ui_faceModifyDialog
from view.facerecord import Ui_FaceRecordForm
from view.ui_theme import apply_page_theme, style_button, style_table


class FaceRecord(QWidget, Ui_FaceRecordForm):
    def __init__(self, parent=None):
        super(FaceRecord, self).__init__(parent)
        self.setupUi(self)
        self.setMinimumSize(1080, 760)
        self.dbcon = ConnectSqlite(model.configuration.DATABASE_PATH)
        self.face_data = []
        self._localize_and_beautify()
        self._apply_responsive_layout()

        self.pushButton_search.clicked.connect(self.search)
        self.pushButton_modify.clicked.connect(self.modify)
        self.pushButton_delete.clicked.connect(self.delete)
        self.make_table()

    def _localize_and_beautify(self):
        self.setWindowTitle("人脸库管理")
        apply_page_theme(self)
        style_button(self.pushButton_search, "primary")
        style_button(self.pushButton_modify, "warning")
        style_button(self.pushButton_delete, "danger")
        style_table(self.tableWidget)

        self.pushButton_search.setText("搜索")
        self.pushButton_modify.setText("修改")
        self.pushButton_delete.setText("删除")
        self.lineEdit_search.setPlaceholderText("输入姓名/学号/班级")

        self.tableWidget.setFont(QFont("Microsoft YaHei", 9))
        self.tableWidget.horizontalHeader().setMinimumHeight(40)
        self.tableWidget.verticalHeader().setDefaultSectionSize(170)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.setWordWrap(False)

    def _apply_responsive_layout(self):
        w = max(self.width(), 1080)
        h = max(self.height(), 760)
        margin = 20

        top_y = 24
        self.lineEdit_search.setGeometry(margin, top_y, 240, 34)
        self.pushButton_search.setGeometry(margin + 260, top_y, 110, 34)
        self.pushButton_modify.setGeometry(margin + 390, top_y, 110, 34)
        self.pushButton_delete.setGeometry(margin + 520, top_y, 110, 34)
        self.tableWidget.setGeometry(margin, 72, w - margin * 2, h - 92)

    def resizeEvent(self, event):
        super(FaceRecord, self).resizeEvent(event)
        self._apply_responsive_layout()

    def search(self):
        search_str = self.lineEdit_search.text().strip().lower()
        if not search_str:
            QMessageBox.warning(self, "提示", "请输入搜索关键词。")
            return

        for row, item in enumerate(self.face_data):
            name = str(item[1]).lower()
            sid = str(item[5]).lower()
            class_name = str(item[6]).lower() if len(item) > 6 and item[6] else ""
            if search_str in name or search_str in sid or search_str in class_name:
                self.tableWidget.setCurrentIndex(self.tableWidget.model().index(row, 0))
                return

        QMessageBox.information(self, "提示", "未找到匹配信息。")

    def modify(self):
        select = self.tableWidget.selectedItems()
        if not select:
            QMessageBox.warning(self, "提示", "请先选择要修改的记录。")
            return

        row = select[0].row()
        old_name = str(self.face_data[row][1])
        old_sid = str(self.face_data[row][5])
        dialog = FaceModify(old_name, old_sid)
        dialog.exec_()
        new_sid, new_name, modify_flag = dialog.getInputs()
        if not modify_flag:
            return

        class_name = ""
        if len(self.face_data[row]) > 6 and self.face_data[row][6]:
            class_name = str(self.face_data[row][6])
        class_name_input, ok = QInputDialog.getText(self, "修改班级", "请输入班级：", text=class_name)
        if not ok:
            return

        class_name = class_name_input.strip()
        if not class_name:
            QMessageBox.warning(self, "提示", "班级不能为空。")
            return

        try:
            result = self.dbcon.sync_student_profile_everywhere(
                old_sid=old_sid,
                new_sid=new_sid.strip(),
                new_name=new_name.strip(),
                new_class_name=class_name,
                auto_merge_conflict=False,
            )
            self.make_table()
            QMessageBox.information(
                self,
                "成功",
                f"已同步更新到全部相关表，更新行数约 {int((result or {}).get('updated_total_rows', 0))}，最终学号：{new_sid.strip()}。",
            )
        except ValueError as exc:
            text = str(exc)
            if "[历史考勤冲突]" in text:
                confirm = QMessageBox.question(
                    self,
                    "历史考勤冲突",
                    "检测到历史考勤冲突，是否自动合并后继续？",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if confirm == QMessageBox.Yes:
                    try:
                        result = self.dbcon.sync_student_profile_everywhere(
                            old_sid=old_sid,
                            new_sid=new_sid.strip(),
                            new_name=new_name.strip(),
                            new_class_name=class_name,
                            auto_merge_conflict=True,
                        )
                        self.make_table()
                        merged_count = int((result or {}).get("merged_conflicts", 0))
                        final_sid = str((result or {}).get("new_student_id", new_sid.strip()))
                        updated_total = int((result or {}).get("updated_total_rows", 0))
                        QMessageBox.information(
                            self,
                            "成功",
                            f"已同步更新到全部相关表，自动合并冲突记录 {merged_count} 条，更新行数约 {updated_total}，最终学号：{final_sid}。",
                        )
                    except Exception as retry_exc:
                        QMessageBox.warning(self, "错误", f"自动合并后修改失败：{retry_exc}")
                return
            QMessageBox.warning(self, "提示", text)
        except Exception as exc:
            QMessageBox.warning(self, "错误", f"修改失败：{exc}")

    def delete(self):
        select = self.tableWidget.selectedItems()
        if not select:
            QMessageBox.warning(self, "提示", "请先选择要删除的记录。")
            return

        row = select[0].row()
        sid = str(self.face_data[row][5])
        confirm = QMessageBox.question(
            self,
            "确认删除",
            f"确定删除学号 {sid} 的人脸库记录吗？\n历史考勤记录将保留。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return

        try:
            self.dbcon.delete_student_keep_attendance(sid)
            self.make_table()
            QMessageBox.information(self, "成功", "学生主档已删除，历史考勤记录已保留。")
        except ValueError as exc:
            QMessageBox.warning(self, "提示", str(exc))
        except Exception as exc:
            QMessageBox.warning(self, "错误", f"删除失败：{exc}")

    def make_table(self):
        self.tableWidget.clear()
        self.face_data = self.dbcon.return_all_face()
        data_show = []
        for row in self.face_data:
            name = row[1]
            student_id = str(row[5])
            class_name = str(row[6]) if len(row) > 6 and row[6] else "未设置"
            face_data = list(map(float, row[2].split("\n")))
            register_time = str(row[4]).split(".")[0]
            face_photo = row[3]
            data_show.append([name, student_id, class_name, str(face_data), register_time, face_photo])

        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(["姓名", "学号", "班级", "人脸特征", "注册时间", "人脸照片"])
        self.tableWidget.setRowCount(0)

        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.tableWidget.setColumnWidth(0, 120)
        self.tableWidget.setColumnWidth(1, 130)
        self.tableWidget.setColumnWidth(2, 130)
        self.tableWidget.setColumnWidth(4, 170)
        self.tableWidget.setColumnWidth(5, 190)

        for row_data in data_show:
            row_idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_idx)
            decoded = self.decode_face_photo(row_data[5])
            if decoded is None:
                decoded = np.zeros((160, 120, 3), dtype=np.uint8)
            resized = cv2.resize(decoded, (120, 160), interpolation=cv2.INTER_AREA)
            icon = self.image_2_qicon(resized)
            label = QLabel()
            label.setPixmap(icon)
            label.setScaledContents(True)

            self.tableWidget.setItem(row_idx, 0, QTableWidgetItem(row_data[0]))
            self.tableWidget.setItem(row_idx, 1, QTableWidgetItem(row_data[1]))
            self.tableWidget.setItem(row_idx, 2, QTableWidgetItem(row_data[2]))
            self.tableWidget.setItem(row_idx, 3, QTableWidgetItem(row_data[3]))
            self.tableWidget.setItem(row_idx, 4, QTableWidgetItem(row_data[4]))
            self.tableWidget.setCellWidget(row_idx, 5, label)

            for col in range(5):
                self.tableWidget.item(row_idx, col).setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

    def decode_face_photo(self, photo_blob):
        if photo_blob is None:
            return None
        if isinstance(photo_blob, np.ndarray):
            return photo_blob if photo_blob.ndim == 3 else None

        try:
            raw = bytes(photo_blob)
        except Exception:
            return None
        if not raw:
            return None

        arr = np.frombuffer(raw, dtype=np.uint8)
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if image is not None:
            return image

        if arr.size % 3 != 0:
            return None
        pixels = arr.size // 3
        if arr.size == 480 * 640 * 3:
            try:
                return arr.reshape((480, 640, 3))
            except Exception:
                pass

        width = int(np.sqrt(pixels))
        while width > 1 and pixels % width != 0:
            width -= 1
        if width <= 1:
            return None
        height = pixels // width
        try:
            return arr.reshape((height, width, 3))
        except Exception:
            return None

    def image_2_qicon(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, bytes_per_component = frame.shape
        bytes_per_line = bytes_per_component * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(q_image)

    def close_all(self):
        try:
            self.dbcon.close_con()
        except Exception:
            pass
        self.close()


class FaceModify(QDialog, Ui_faceModifyDialog):
    def __init__(self, name, sid, parent=None):
        super(FaceModify, self).__init__(parent)
        self.setupUi(self)
        self.name = name
        self.sid = sid
        self.lineEdit_sno.setText(self.sid)
        self.lineEdit_name.setText(self.name)
        self.modify_flag = False
        self.pushButton_modify_2.clicked.connect(self.modify_return)
        self.setWindowTitle("修改学生信息")
        self.pushButton_modify_2.setText("确认修改")
        self.label_2.setText("学号:")
        self.label_3.setText("姓名:")
        style_button(self.pushButton_modify_2, "primary")

    def modify_return(self):
        if self.lineEdit_sno.text() == self.sid and self.lineEdit_name.text() == self.name:
            QMessageBox.warning(self, "提示", "内容未变化，无需修改。")
        else:
            self.modify_flag = True
            self.close()

    def getInputs(self):
        return self.lineEdit_sno.text(), self.lineEdit_name.text(), self.modify_flag
