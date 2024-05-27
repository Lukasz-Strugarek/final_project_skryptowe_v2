import os

from PySide6.QtGui import QPainter, QPen, QColor, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QListWidget, QFileDialog, \
    QHBoxLayout, QLabel, QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QFormLayout, QMessageBox, QGraphicsRectItem, \
    QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QColorDialog
from PySide6.QtCore import Qt, QRectF

from annotation_window import AnotationWindow
from new_file_widget import NewFileWindow


class InitialWindow(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        # Tworzenie layoutu
        layout = QVBoxLayout()
        buttonlayout = QHBoxLayout()

        # Tworzenie przycisków
        self.new_button = QPushButton("New")
        self.open_button = QPushButton("Open")

        # Dodanie przycisków do layoutu
        buttonlayout.addWidget(self.new_button)
        buttonlayout.addWidget(self.open_button)

        layout.addLayout(buttonlayout)

        # Tworzenie przycisku do cięcia tiff
        self.tiff_button = QPushButton("Split tiff file")
        layout.addWidget(self.tiff_button)

        # Tworzenie przycisku do dodania profilu
        self.profile_button = QPushButton("Add new profile")
        layout.addWidget(self.profile_button)


        # Podłączenie sygnałów do slotów
        self.new_button.clicked.connect(self.create_new_file)
        self.open_button.clicked.connect(self.open_file)
        self.tiff_button.clicked.connect(self.tiff_split)
        self.profile_button.clicked.connect(self.new_profile)

        self.setLayout(layout)



    def tiff_split(self):
        self.controller.load_tiff_window()

    def new_profile(self):
        self.controller.load_profile_window()

    def create_new_file(self):
        self.new_image_window = NewFileWindow()
        self.new_image_window.show()

    def open_file(self):
        # Funkcja obsługująca przycisk "Otwórz"
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Otwórz plik", "", "Wszystkie pliki (*)", options=options)
        base, _ = os.path.splitext(file_name)
        anot_file_path = f"{base}_anot.pkl"
        if file_name and os.path.exists(anot_file_path):
            self.anot_window = AnotationWindow(self.controller, file_name)
            self.controller.load_anot_window(self.anot_window)
        elif not os.path.exists(anot_file_path):
            QMessageBox.warning(self, "Error", "NO ANNOTATION FILE FOUND")

