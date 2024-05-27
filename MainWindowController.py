import sys

from PySide6.QtWidgets import QMainWindow, QApplication
from InitialWidget import InitialWindow
from tiff_widget import TiffWindow
from new_file_widget import NewFileWindow
from profile_creation_widget import ProfileManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Moja Aplikacja")
        self.setGeometry(100, 100, 400, 200)
        self.setCentralWidget(InitialWindow(self))

    def load_tiff_window(self):

        self.setCentralWidget(TiffWindow(self))

    def load_new_file_window(self):
        NewFileWindow().show()

    def load_initial_window(self):
        self.setGeometry(100, 100, 400, 200)
        self.setCentralWidget(InitialWindow(self))

    def load_profile_window(self):
        self.setCentralWidget(ProfileManager(self))

    def load_anot_window(self, anot_widget):
        self.setCentralWidget(anot_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())