from PySide6.QtGui import QPainter, QPen, QColor, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QListWidget, QFileDialog, \
    QHBoxLayout, QLabel, QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QFormLayout, QMessageBox, QGraphicsRectItem, \
    QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QColorDialog
from PySide6.QtCore import Qt, QRectF

from tiff_splitter import split_tiff


class TiffWindow(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("New image")
        self.setGeometry(150, 150, 600, 400)

        layout = QFormLayout()

        self.file_path_input = QLineEdit(self)
        self.file_path_input.setPlaceholderText("Wybierz plik TIFF")
        self.file_path_input.setReadOnly(True)
        self.file_button = QPushButton("Wybierz plik")
        self.file_button.clicked.connect(self.select_file)

        self.output_path_input = QLineEdit(self)
        self.output_path_input.setPlaceholderText("Wybierz ścieżkę zapisu")
        self.output_path_input.setReadOnly(True)
        self.output_button = QPushButton("Wybierz ścieżkę")
        self.output_button.clicked.connect(self.select_output_path)

        self.tile_size_input = QSpinBox(self)
        self.tile_size_input.setRange(1, 10000)
        self.tile_size_input.setValue(128)

        self.overlap_input = QDoubleSpinBox(self)
        self.overlap_input.setRange(0, 1)
        self.overlap_input.setSingleStep(0.01)
        self.overlap_input.setValue(0.1)

        self.cutoff_input = QDoubleSpinBox(self)
        self.cutoff_input.setRange(0, 1)
        self.cutoff_input.setSingleStep(0.01)
        self.cutoff_input.setValue(0.05)

        self.threshold_input = QSpinBox(self)
        self.threshold_input.setRange(0, 255)
        self.threshold_input.setValue(245)

        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_script)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_script)

        layout.addRow("Plik TIFF:", self.file_path_input)
        layout.addRow("", self.file_button)
        layout.addRow("Ścieżka zapisu:", self.output_path_input)
        layout.addRow("", self.output_button)
        layout.addRow("Tile size:", self.tile_size_input)
        layout.addRow("Overlap:", self.overlap_input)
        layout.addRow("Cutoff:", self.cutoff_input)
        layout.addRow("Threshold:", self.threshold_input)
        layout.addRow("", self.run_button)
        layout.addRow("", self.cancel_button)

        self.setLayout(layout)

    def select_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Wybierz plik TIFF", "", "TIFF Files (*.tif *.tiff)",
                                                   options=options)
        if file_path:
            self.file_path_input.setText(file_path)

    def select_output_path(self):
        options = QFileDialog.Options()
        output_path = QFileDialog.getExistingDirectory(self, "Wybierz ścieżkę zapisu", options=options)
        if output_path:
            self.output_path_input.setText(output_path)

    def run_script(self):
        file_path = self.file_path_input.text()
        output_path = self.output_path_input.text()
        tile_size = self.tile_size_input.value()
        overlap = self.overlap_input.value()
        cutoff = self.cutoff_input.value()
        threshold = self.threshold_input.value()

        if not file_path or not output_path:
            QMessageBox.warning(self, "Błąd", "Wybierz plik TIFF i ścieżkę zapisu")
            return

        split_tiff(file_path, output_path, tile_size, overlap, cutoff, threshold)
        QMessageBox.information(self, "Sukces", "Proces zakończony pomyślnie")
        self.controller.load_initial_window()


    def cancel_script(self):
        self.controller.load_initial_window()