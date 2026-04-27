# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'facecheck.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_FaceCheckForm(object):
    def setupUi(self, FaceCheckForm):
        FaceCheckForm.setObjectName("FaceCheckForm")
        FaceCheckForm.resize(796, 600)
        FaceCheckForm.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.label_tablecard = QtWidgets.QLabel(FaceCheckForm)
        self.label_tablecard.setGeometry(QtCore.QRect(20, 10, 411, 341))
        font = QtGui.QFont()
        font.setFamily("Roboto")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_tablecard.setFont(font)
        self.label_tablecard.setStyleSheet("border-image: url(:/icon/pic/table_card.png);")
        self.label_tablecard.setText("")
        self.label_tablecard.setAlignment(QtCore.Qt.AlignCenter)
        self.label_tablecard.setObjectName("label_tablecard")
        self.label_6 = QtWidgets.QLabel(FaceCheckForm)
        self.label_6.setGeometry(QtCore.QRect(40, 20, 71, 31))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setStyleSheet("background-color: rgb(69, 90, 100);\n"
"color: rgb(255, 255, 255);")
        self.label_6.setObjectName("label_6")
        self.pushButton_open = QtWidgets.QPushButton(FaceCheckForm)
        self.pushButton_open.setGeometry(QtCore.QRect(100, 70, 91, 31))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_open.setFont(font)
        self.pushButton_open.setStyleSheet("QPushButton{\n"
"    \n"
"    color: rgb(255, 255, 255);\n"
"    border-width: 1px;\n"
"    border-radius: 6px;\n"
"    border-bottom-color: rgb(150,150,150);\n"
"    border-right-color: rgb(165,165,165);\n"
"    border-left-color: rgb(165,165,165);\n"
"    border-top-color: rgb(180,180,180);\n"
"    border-style: solid;\n"
"    padding: 4px;\n"
"    background-color: rgb(69, 90, 100);\n"
"}\n"
"QPushButton:hover{\n"
"    color: rgb(255, 255, 255);\n"
"    border-width: 1px;\n"
"    border-radius:6px;\n"
"    border-top-color: rgb(255,150,60);\n"
"    border-right-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(200, 70, 20, 255), stop:1 rgba(255,150,60, 255));\n"
"    border-left-color:  qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0 rgba(200, 70, 20, 255), stop:1 rgba(255,150,60, 255));\n"
"    border-bottom-color: rgb(200,70,20);\n"
"    border-style: solid;\n"
"    padding: 2px;\n"
"    background-color: rgb(69, 90, 100);\n"
"}\n"
"QPushButton:default{\n"
"    color: rgb(255, 255, 255);\n"
"    border-width: 1px;\n"
"    border-radius:6px;\n"
"    border-top-color: rgb(255,150,60);\n"
"    border-right-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(200, 70, 20, 255), stop:1 rgba(255,150,60, 255));\n"
"    border-left-color:  qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0 rgba(200, 70, 20, 255), stop:1 rgba(255,150,60, 255));\n"
"    border-bottom-color: rgb(200,70,20);\n"
"    border-style: solid;\n"
"    padding: 2px;\n"
"    background-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(220, 220, 220, 255), stop:1 rgba(255, 255, 255, 255));\n"
"}\n"
"QPushButton:pressed{\n"
"    color: rgb(255, 255, 255);\n"
"    border-width: 1px;\n"
"    border-radius: 6px;\n"
"    border-width: 1px;\n"
"    border-top-color: rgba(255,150,60,200);\n"
"    border-right-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(200, 70, 20, 255), stop:1 rgba(255,150,60, 200));\n"
"    border-left-color:  qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0 rgba(200, 70, 20, 255), stop:1 rgba(255,150,60, 200));\n"
"    border-bottom-color: rgba(200,70,20,200);\n"
"    border-style: solid;\n"
"    padding: 2px;\n"
"    \n"
"    background-color: rgb(129, 156, 169);\n"
"    \n"
"}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/pic/camera.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_open.setIcon(icon)
        self.pushButton_open.setObjectName("pushButton_open")
        self.groupBox_2 = QtWidgets.QGroupBox(FaceCheckForm)
        self.groupBox_2.setGeometry(QtCore.QRect(30, 360, 391, 231))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setStyleSheet("QGroupBox\n"
"        {\n"
"          border: 2px solid rgb(69, 90, 100);\n"
"          border-radius:4px;\n"
"          margin-top:6px;\n"
"          }\n"
"QGroupBox:title\n"
"        {\n"
"          color:rgb(69, 90, 100);\n"
"          subcontrol-origin: margin;\n"
"          left: 10px;\n"
"          }")
        self.groupBox_2.setObjectName("groupBox_2")
        self.label_face = QtWidgets.QLabel(self.groupBox_2)
        self.label_face.setGeometry(QtCore.QRect(40, 30, 211, 181))
        self.label_face.setStyleSheet("border: 1px solid rgb(69, 90, 100);")
        self.label_face.setText("")
        self.label_face.setObjectName("label_face")
        self.pushButton_checkin = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_checkin.setGeometry(QtCore.QRect(250, 100, 101, 41))
        font = QtGui.QFont()
        font.setFamily("Roboto")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_checkin.setFont(font)
        self.pushButton_checkin.setStyleSheet("QPushButton{\n"
"    \n"
"    color: rgb(255, 255, 255);\n"
"    border-width: 1px;\n"
"    border-radius: 6px;\n"
"    border-bottom-color: rgb(150,150,150);\n"
"    border-right-color: rgb(165,165,165);\n"
"    border-left-color: rgb(165,165,165);\n"
"    border-top-color: rgb(180,180,180);\n"
"    border-style: solid;\n"
"    padding: 4px;\n"
"    background-color: rgb(69, 90, 100);\n"
"}\n"
"QPushButton:hover{\n"
"    color: rgb(255, 255, 255);\n"
"    border-width: 1px;\n"
"    border-radius:6px;\n"
"    border-top-color: rgb(255,150,60);\n"
"    border-right-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(200, 70, 20, 255), stop:1 rgba(255,150,60, 255));\n"
"    border-left-color:  qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0 rgba(200, 70, 20, 255), stop:1 rgba(255,150,60, 255));\n"
"    border-bottom-color: rgb(200,70,20);\n"
"    border-style: solid;\n"
"    padding: 2px;\n"
"    background-color: rgb(69, 90, 100);\n"
"}\n"
"QPushButton:default{\n"
"    color: rgb(255, 255, 255);\n"
"    border-width: 1px;\n"
"    border-radius:6px;\n"
"    border-top-color: rgb(255,150,60);\n"
"    border-right-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(200, 70, 20, 255), stop:1 rgba(255,150,60, 255));\n"
"    border-left-color:  qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0 rgba(200, 70, 20, 255), stop:1 rgba(255,150,60, 255));\n"
"    border-bottom-color: rgb(200,70,20);\n"
"    border-style: solid;\n"
"    padding: 2px;\n"
"    background-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(220, 220, 220, 255), stop:1 rgba(255, 255, 255, 255));\n"
"}\n"
"QPushButton:pressed{\n"
"    color: rgb(255, 255, 255);\n"
"    border-width: 1px;\n"
"    border-radius: 6px;\n"
"    border-width: 1px;\n"
"    border-top-color: rgba(255,150,60,200);\n"
"    border-right-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(200, 70, 20, 255), stop:1 rgba(255,150,60, 200));\n"
"    border-left-color:  qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0 rgba(200, 70, 20, 255), stop:1 rgba(255,150,60, 200));\n"
"    border-bottom-color: rgba(200,70,20,200);\n"
"    border-style: solid;\n"
"    padding: 2px;\n"
"    \n"
"    background-color: rgb(129, 156, 169);\n"
"    \n"
"}")
        self.pushButton_checkin.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icon/pic/checkin.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_checkin.setIcon(icon1)
        self.pushButton_checkin.setObjectName("pushButton_checkin")
        self.groupBox_3 = QtWidgets.QGroupBox(FaceCheckForm)
        self.groupBox_3.setGeometry(QtCore.QRect(450, 10, 331, 581))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_3.setFont(font)
        self.groupBox_3.setStyleSheet("QGroupBox\n"
"        {\n"
"          border: 2px solid rgb(69, 90, 100);\n"
"          border-radius:4px;\n"
"          margin-top:6px;\n"
"          }\n"
"QGroupBox:title\n"
"        {\n"
"          color:rgb(69, 90, 100);\n"
"          subcontrol-origin: margin;\n"
"          left: 10px;\n"
"          }")
        self.groupBox_3.setObjectName("groupBox_3")
        self.label_3 = QtWidgets.QLabel(self.groupBox_3)
        self.label_3.setGeometry(QtCore.QRect(30, 60, 86, 26))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_2 = QtWidgets.QLabel(self.groupBox_3)
        self.label_2.setGeometry(QtCore.QRect(30, 130, 86, 26))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.lineEdit_name = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEdit_name.setGeometry(QtCore.QRect(140, 60, 136, 26))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_name.setFont(font)
        self.lineEdit_name.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_name.setObjectName("lineEdit_name")
        self.lineEdit_sno = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEdit_sno.setGeometry(QtCore.QRect(140, 130, 136, 26))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_sno.setFont(font)
        self.lineEdit_sno.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_sno.setObjectName("lineEdit_sno")
        self.label_5 = QtWidgets.QLabel(self.groupBox_3)
        self.label_5.setGeometry(QtCore.QRect(30, 200, 91, 26))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.progressBar = QtWidgets.QProgressBar(self.groupBox_3)
        self.progressBar.setGeometry(QtCore.QRect(140, 200, 141, 23))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.progressBar.setFont(font)
        self.progressBar.setStyleSheet("QProgressBar {\n"
"    text-align: center;\n"
"    color: rgb(0, 0, 0);\n"
"    border-width: 1px; \n"
"    border-radius: 6px;\n"
"    border-style: inset;\n"
"    border-color: rgb(150,150,150);\n"
"    background-color:rgb(221,221,219);\n"
"}\n"
"QProgressBar::chunk:horizontal {\n"
"background-color: rgb(69, 90, 100);\n"
"    border-style: solid;\n"
"    border-radius:4px;\n"
"    border-width:1px;\n"
"    \n"
"    background-color: rgb(101, 133, 147);\n"
"\n"
"\n"
"}")
        self.progressBar.setProperty("value", 60)
        self.progressBar.setObjectName("progressBar")
        self.label = QtWidgets.QLabel(self.groupBox_3)
        self.label.setGeometry(QtCore.QRect(215, 180, 15, 12))
        self.label.setStyleSheet("border-image: url(:/icon/pic/down.png);")
        self.label.setText("")
        self.label.setObjectName("label")
        self.label_12 = QtWidgets.QLabel(self.groupBox_3)
        self.label_12.setGeometry(QtCore.QRect(30, 340, 101, 26))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.label_close = QtWidgets.QLabel(self.groupBox_3)
        self.label_close.setGeometry(QtCore.QRect(90, 400, 131, 131))
        self.label_close.setStyleSheet("border-image: url(:/icon/close.png);")
        self.label_close.setText("")
        self.label_close.setObjectName("label_close")
        self.lineEdit_checkin_time = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEdit_checkin_time.setGeometry(QtCore.QRect(143, 270, 136, 26))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_checkin_time.setFont(font)
        self.lineEdit_checkin_time.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_checkin_time.setObjectName("lineEdit_checkin_time")
        self.label_13 = QtWidgets.QLabel(self.groupBox_3)
        self.label_13.setGeometry(QtCore.QRect(30, 270, 111, 26))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_13.setFont(font)
        self.label_13.setObjectName("label_13")
        self.label_open = QtWidgets.QLabel(self.groupBox_3)
        self.label_open.setGeometry(QtCore.QRect(90, 400, 131, 131))
        self.label_open.setStyleSheet("border-image: url(:/icon/open.png);")
        self.label_open.setText("")
        self.label_open.setObjectName("label_open")
        self.pushButton_stop = QtWidgets.QPushButton(FaceCheckForm)
        self.pushButton_stop.setGeometry(QtCore.QRect(250, 70, 91, 31))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_stop.setFont(font)
        self.pushButton_stop.setStyleSheet("QPushButton{\n"
"    \n"
"    color: rgb(255, 255, 255);\n"
"    border-width: 1px;\n"
"    border-radius: 6px;\n"
"    border-bottom-color: rgb(150,150,150);\n"
"    border-right-color: rgb(165,165,165);\n"
"    border-left-color: rgb(165,165,165);\n"
"    border-top-color: rgb(180,180,180);\n"
"    border-style: solid;\n"
"    padding: 4px;\n"
"    background-color: rgb(69, 90, 100);\n"
"}\n"
"QPushButton:hover{\n"
"    color: rgb(255, 255, 255);\n"
"    border-width: 1px;\n"
"    border-radius:6px;\n"
"    border-top-color: rgb(255,150,60);\n"
"    border-right-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(200, 70, 20, 255), stop:1 rgba(255,150,60, 255));\n"
"    border-left-color:  qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0 rgba(200, 70, 20, 255), stop:1 rgba(255,150,60, 255));\n"
"    border-bottom-color: rgb(200,70,20);\n"
"    border-style: solid;\n"
"    padding: 2px;\n"
"    background-color: rgb(69, 90, 100);\n"
"}\n"
"QPushButton:default{\n"
"    color: rgb(255, 255, 255);\n"
"    border-width: 1px;\n"
"    border-radius:6px;\n"
"    border-top-color: rgb(255,150,60);\n"
"    border-right-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(200, 70, 20, 255), stop:1 rgba(255,150,60, 255));\n"
"    border-left-color:  qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0 rgba(200, 70, 20, 255), stop:1 rgba(255,150,60, 255));\n"
"    border-bottom-color: rgb(200,70,20);\n"
"    border-style: solid;\n"
"    padding: 2px;\n"
"    background-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(220, 220, 220, 255), stop:1 rgba(255, 255, 255, 255));\n"
"}\n"
"QPushButton:pressed{\n"
"    color: rgb(255, 255, 255);\n"
"    border-width: 1px;\n"
"    border-radius: 6px;\n"
"    border-width: 1px;\n"
"    border-top-color: rgba(255,150,60,200);\n"
"    border-right-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(200, 70, 20, 255), stop:1 rgba(255,150,60, 200));\n"
"    border-left-color:  qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0 rgba(200, 70, 20, 255), stop:1 rgba(255,150,60, 200));\n"
"    border-bottom-color: rgba(200,70,20,200);\n"
"    border-style: solid;\n"
"    padding: 2px;\n"
"    \n"
"    background-color: rgb(129, 156, 169);\n"
"    \n"
"}")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icon/pic/stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_stop.setIcon(icon2)
        self.pushButton_stop.setObjectName("pushButton_stop")
        self.label_frame = QtWidgets.QLabel(FaceCheckForm)
        self.label_frame.setGeometry(QtCore.QRect(60, 110, 331, 221))
        self.label_frame.setStyleSheet("border: 1px solid rgb(69, 90, 100);")
        self.label_frame.setText("")
        self.label_frame.setObjectName("label_frame")
        self.label_current = QtWidgets.QLabel(FaceCheckForm)
        self.label_current.setGeometry(QtCore.QRect(330, 18, 91, 31))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_current.setFont(font)
        self.label_current.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(69, 90, 100);")
        self.label_current.setObjectName("label_current")

        self.retranslateUi(FaceCheckForm)
        QtCore.QMetaObject.connectSlotsByName(FaceCheckForm)

    def retranslateUi(self, FaceCheckForm):
        _translate = QtCore.QCoreApplication.translate
        FaceCheckForm.setWindowTitle(_translate("FaceCheckForm", "人脸签到"))
        self.label_6.setText(_translate("FaceCheckForm", "摄像头"))
        self.pushButton_open.setText(_translate("FaceCheckForm", " 打开"))
        self.groupBox_2.setTitle(_translate("FaceCheckForm", "人脸识别"))
        self.groupBox_3.setTitle(_translate("FaceCheckForm", "识别结果"))
        self.label_3.setText(_translate("FaceCheckForm", "姓名:"))
        self.label_2.setText(_translate("FaceCheckForm", "学号:"))
        self.label_5.setText(_translate("FaceCheckForm", "相似度："))
        self.label_12.setText(_translate("FaceCheckForm", "考勤指示灯:（绿灯表示通过）"))
        self.label_13.setText(_translate("FaceCheckForm", "识别时间:"))
        self.pushButton_stop.setText(_translate("FaceCheckForm", " 关闭"))
        self.label_current.setText(_translate("FaceCheckForm", "23:59:59"))

import resource_rc
