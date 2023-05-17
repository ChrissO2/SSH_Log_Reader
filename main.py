import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow
from log_list import *

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
