import sys
from mywindow import *

def main():
    app = QApplication(sys.argv)
    gui = MyWindow()

    gui.setGeometry(100, 100, 800, 600)
    gui.setStyleSheet("background-color: #1E1E1E; color: #FFFFFF; font-size: 16px;")

    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
