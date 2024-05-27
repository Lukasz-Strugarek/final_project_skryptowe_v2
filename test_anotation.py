import sys
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QPushButton, QFileDialog, QHBoxLayout, QMessageBox, QGraphicsView,
                               QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem)

class AnnotationWidget(QGraphicsView):
    def __init__(self, filepath):
        super().__init__()
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.image_item = None
        self.rectangles = []

        self.drawing = False
        self.start_point = None
        self.current_rect_item = None

    def load_image(self, file_path):
        pixmap = QPixmap(file_path)
        if self.image_item:
            self.scene.removeItem(self.image_item)
        self.image_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.image_item)
        self.setSceneRect(QRectF(pixmap.rect()))

    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 0.8
        old_pos = self.mapToScene(event.position().toPoint())
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        self.scale(zoom_factor, zoom_factor)
        new_pos = self.mapToScene(event.position().toPoint())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.image_item:
            self.drawing = True
            self.start_point = self.mapToScene(event.position().toPoint())
            self.current_rect_item = QGraphicsRectItem(QRectF(self.start_point, self.start_point))
            self.current_rect_item.setPen(QPen(Qt.red, 2))
            self.scene.addItem(self.current_rect_item)

    def mouseMoveEvent(self, event):
        if self.drawing and self.image_item:
            end_point = self.mapToScene(event.position().toPoint())
            rect = QRectF(self.start_point, end_point).normalized()
            self.current_rect_item.setRect(rect)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            end_point = self.mapToScene(event.position().toPoint())
            rect = QRectF(self.start_point, end_point).normalized()
            self.current_rect_item.setRect(rect)
            self.rectangles.append(self.current_rect_item)
            self.current_rect_item = None

    def save_annotations(self, output_path):
        if self.image_item:
            image = self.image_item.pixmap().toImage()
            painter = QPainter(image)
            for rect_item in self.rectangles:
                rect = rect_item.rect()
                painter.setPen(QPen(QColor(0, 255, 0), 2))
                painter.drawRect(rect)
            image.save(output_path)
            painter.end()

    def clear_annotations(self):
        for rect_item in self.rectangles:
            self.scene.removeItem(rect_item)
        self.rectangles.clear()

class AnotationWindow(QMainWindow):
    def __init__(self, main_window, filepath):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Adnotacje obrazów medycznych")
        self.setGeometry(100, 100, 800, 600)

        self.annotation_widget = AnnotationWidget(filepath)


        self.save_button = QPushButton("Zapisz adnotacje")
        self.clear_button = QPushButton("Wyczyść adnotacje")

        self.save_button.clicked.connect(self.save_annotations)
        self.clear_button.clicked.connect(self.clear_annotations)

        layout = QVBoxLayout()
        layout.addWidget(self.annotation_widget)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.clear_button)
        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)

        self.annotation_widget.load_image(filepath)

        self.main_window.setCentralWidget(container)


    def save_annotations(self):
        if not self.annotation_widget.image_item:
            QMessageBox.warning(self, "Błąd", "Najpierw otwórz obraz.")
            return

        file_name, _ = QFileDialog.getSaveFileName(self, "Zapisz adnotacje", "", "Obrazy (*.png *.jpg *.bmp *.jpeg)")
        if file_name:
            self.annotation_widget.save_annotations(file_name)

    def clear_annotations(self):
        self.annotation_widget.clear_annotations()

