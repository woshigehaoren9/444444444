import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication

from control.mainWindow import MyWindow

# 启用高分辨率缩放
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyWindow()
    myWin.show()
    sys.exit(app.exec_())
