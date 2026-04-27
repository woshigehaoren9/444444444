# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'faceregister.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_FaceRegisterForm(object):
    def setupUi(self, FaceRegisterForm):
        FaceRegisterForm.setObjectName("FaceRegisterForm")
        FaceRegisterForm.resize(800, 600)
        FaceRegisterForm.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.label_tablecard = QtWidgets.QLabel(FaceRegisterForm)
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
        self.label_6 = QtWidgets.QLabel(FaceRegisterForm)
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
        self.pushButton_open = QtWidgets.QPushButton(FaceRegisterForm)
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
        self.groupBox_2 = QtWidgets.QGroupBox(FaceRegisterForm)
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
        self.label_face.setGeometry(QtCore.QRect(130, 30, 211, 181))
        self.label_face.setStyleSheet("border: 1px solid rgb(69, 90, 100);")
        self.label_face.setText("")
        self.label_face.setObjectName("label_face")
        self.pushButton_take_photo = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_take_photo.setGeometry(QtCore.QRect(30, 100, 61, 41))
        font = QtGui.QFont()
        font.setFamily("Roboto")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_take_photo.setFont(font)
        self.pushButton_take_photo.setStyleSheet("QPushButton{\n"
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
        self.pushButton_take_photo.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icon/pic/take photo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_take_photo.setIcon(icon1)
        self.pushButton_take_photo.setObjectName("pushButton_take_photo")
        self.groupBox_3 = QtWidgets.QGroupBox(FaceRegisterForm)
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
        self.label_face_feature = QtWidgets.QLabel(self.groupBox_3)
        self.label_face_feature.setGeometry(QtCore.QRect(60, 60, 211, 181))
        self.label_face_feature.setStyleSheet("border: 1px solid rgb(69, 90, 100);")
        self.label_face_feature.setText("")
        self.label_face_feature.setObjectName("label_face_feature")
        self.pushButton_register = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_register.setGeometry(QtCore.QRect(110, 450, 111, 41))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_register.setFont(font)
        self.pushButton_register.setStyleSheet("QPushButton{\n"
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
        icon2.addPixmap(QtGui.QPixmap(":/icon/pic/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_register.setIcon(icon2)
        self.pushButton_register.setObjectName("pushButton_register")
        self.pushButton_import_image = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_import_image.setGeometry(QtCore.QRect(30, 510, 121, 31))
        self.pushButton_import_image.setObjectName("pushButton_import_image")
        self.pushButton_import_folder = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_import_folder.setGeometry(QtCore.QRect(180, 510, 121, 31))
        self.pushButton_import_folder.setObjectName("pushButton_import_folder")
        self.label_3 = QtWidgets.QLabel(self.groupBox_3)
        self.label_3.setGeometry(QtCore.QRect(47, 300, 86, 26))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_2 = QtWidgets.QLabel(self.groupBox_3)
        self.label_2.setGeometry(QtCore.QRect(47, 358, 86, 26))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.lineEdit_name = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEdit_name.setGeometry(QtCore.QRect(105, 300, 171, 26))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_name.setFont(font)
        self.lineEdit_name.setObjectName("lineEdit_name")
        self.lineEdit_sno = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEdit_sno.setGeometry(QtCore.QRect(105, 358, 171, 26))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_sno.setFont(font)
        self.lineEdit_sno.setObjectName("lineEdit_sno")
        self.label_4 = QtWidgets.QLabel(self.groupBox_3)
        self.label_4.setGeometry(QtCore.QRect(130, 30, 111, 26))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.pushButton_stop = QtWidgets.QPushButton(FaceRegisterForm)
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
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icon/pic/stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_stop.setIcon(icon3)
        self.pushButton_stop.setObjectName("pushButton_stop")
        self.label_frame = QtWidgets.QLabel(FaceRegisterForm)
        self.label_frame.setGeometry(QtCore.QRect(60, 110, 331, 221))
        self.label_frame.setStyleSheet("border: 1px solid rgb(69, 90, 100);")
        self.label_frame.setText("")
        self.label_frame.setObjectName("label_frame")

        self.retranslateUi(FaceRegisterForm)
        QtCore.QMetaObject.connectSlotsByName(FaceRegisterForm)

    def retranslateUi(self, FaceRegisterForm):
        _translate = QtCore.QCoreApplication.translate
        FaceRegisterForm.setWindowTitle(_translate("FaceRegisterForm", "人脸录入"))
        self.label_6.setText(_translate("FaceRegisterForm", "摄像头"))
        self.pushButton_open.setText(_translate("FaceRegisterForm", "打开"))
        self.groupBox_2.setTitle(_translate("FaceRegisterForm", "拍照"))
        self.groupBox_3.setTitle(_translate("FaceRegisterForm", "录入"))
        self.pushButton_register.setText(_translate("FaceRegisterForm", " 保存"))
        self.pushButton_import_image.setText(_translate("FaceRegisterForm", "单张导入"))
        self.pushButton_import_folder.setText(_translate("FaceRegisterForm", "批量导入"))
        self.label_3.setText(_translate("FaceRegisterForm", "姓名:"))
        self.label_2.setText(_translate("FaceRegisterForm", "学号:"))
        self.label_4.setText(_translate("FaceRegisterForm", "人脸特征"))
        self.pushButton_stop.setText(_translate("FaceRegisterForm", "关闭"))

import resource_rc
