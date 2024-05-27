from annotation_widget import AnnotationWidget
from pickle_functions import *
from PySide6.QtGui import QPainter, QPen, QColor, QPixmap, QMouseEvent, QPolygonF, QAction
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QListWidget, QFileDialog, \
    QHBoxLayout, QLabel, QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QFormLayout, QMessageBox, QGraphicsRectItem, \
    QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QColorDialog, QGraphicsPolygonItem, QToolBar
from PySide6.QtCore import Qt, QRectF

class AnotationWindow(QMainWindow):
    def __init__(self, controller, filepath):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Adnotacje obrazów medycznych")
        self.controller.setGeometry(100, 100, 1200, 900)

        self.annotation_widget = AnnotationWidget(filepath)

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        self.rect_action = QAction("Rectangle", self)
        self.rect_action.setCheckable(True)
        self.toolbar.addAction(self.rect_action)

        self.polygon_action = QAction("Polygon", self)
        self.polygon_action.setCheckable(True)
        self.toolbar.addAction(self.polygon_action)

        self.cancel_action = QAction("Cancel", self)
        self.toolbar.addAction(self.cancel_action)

        self.rect_action.triggered.connect(lambda: self.select_tool('rectangle'))
        self.polygon_action.triggered.connect(lambda: self.select_tool('polygon'))
        self.cancel_action.triggered.connect(lambda: self.select_tool(None))

        self.save_button = QPushButton("Zapisz adnotacje")
        self.clear_button = QPushButton("Wyczyść adnotacje")
        self.back_button = QPushButton("Cancel")

        self.save_button.clicked.connect(self.save_annotations)
        self.clear_button.clicked.connect(self.clear_annotations)
        self.back_button.clicked.connect(self.cancel_annotations)

        layout = QVBoxLayout()
        layout.addWidget(self.annotation_widget)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.back_button)
        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)

        self.annotation_widget.load_image(filepath)

        self.setCentralWidget(container)

    def select_tool(self, tool):
        self.annotation_widget.set_tool(tool)
        self.rect_action.setChecked(tool == 'rectangle')
        self.polygon_action.setChecked(tool == 'polygon')

    def save_annotations(self):
        if not self.annotation_widget.image_item:
            QMessageBox.warning(self, "Błąd", "Najpierw otwórz obraz.")
            return

        file_name, _ = QFileDialog.getSaveFileName(self, "Zapisz adnotacje", "", "Obrazy (*.png *.jpg *.bmp *.jpeg)")
        if file_name:
            self.annotation_widget.save_annotations(file_name)

    def clear_annotations(self):
        self.annotation_widget.clear_annotations()

    def cancel_annotations(self):
        self.controller.load_initial_window()
