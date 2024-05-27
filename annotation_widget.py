from PySide6.QtGui import QPainter, QPen, QColor, QPixmap, QMouseEvent, QPolygonF
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QListWidget, QFileDialog, \
    QHBoxLayout, QLabel, QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QFormLayout, QMessageBox, QGraphicsRectItem, \
    QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QColorDialog, QGraphicsPolygonItem
from PySide6.QtCore import Qt, QRectF

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
        self.polygons = []
        self.last_drag_position = None

        self.drawing = False
        self.start_point = None
        self.current_rect_item = None
        self.current_polygon_item = None
        self.polygon_points = []
        self.temp_line = None

        self.tool = None  # No default tool

    def load_image(self, file_path):
        pixmap = QPixmap(file_path)
        if self.image_item:
            self.scene.removeItem(self.image_item)
        self.image_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.image_item)
        self.setSceneRect(QRectF(pixmap.rect()))

    def wheelEvent(self, event):
        zoom_in_factor = 1.01
        zoom_out_factor = 0.99
        old_pos = self.mapToScene(event.position().toPoint())
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        self.scale(zoom_factor, zoom_factor)
        new_pos = self.mapToScene(event.position().toPoint())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.image_item:
            if self.tool == 'rectangle':
                self.drawing = True
                self.start_point = self.mapToScene(event.position().toPoint())
                self.current_rect_item = QGraphicsRectItem(QRectF(self.start_point, self.start_point))
                self.current_rect_item.setPen(QPen(Qt.red, 2))
                self.scene.addItem(self.current_rect_item)
            elif self.tool == 'polygon':
                point = self.mapToScene(event.position().toPoint())
                if not self.drawing:
                    self.drawing = True
                    self.polygon_points = [point]
                    self.current_polygon_item = QGraphicsPolygonItem(QPolygonF(self.polygon_points))
                    self.current_polygon_item.setPen(QPen(Qt.red, 2))
                    self.scene.addItem(self.current_polygon_item)
                else:
                    self.polygon_points.append(point)
                    self.current_polygon_item.setPolygon(QPolygonF(self.polygon_points))
                    if self.temp_line:
                        self.scene.removeItem(self.temp_line)
                        self.temp_line = None

        elif event.button() == Qt.LeftButton:
            self.last_drag_position = event.pos()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.drawing and self.image_item:
            if self.tool == 'rectangle' and self.current_rect_item:
                end_point = self.mapToScene(event.position().toPoint())
                rect = QRectF(self.start_point, end_point).normalized()
                self.current_rect_item.setRect(rect)
            elif self.tool == 'polygon' and self.polygon_points:
                point = self.mapToScene(event.position().toPoint())
                if self.temp_line:
                    self.scene.removeItem(self.temp_line)
                self.temp_line = self.scene.addLine(self.polygon_points[-1].x(), self.polygon_points[-1].y(), point.x(), point.y(), QPen(Qt.red, 2))
        elif event.buttons() == Qt.LeftButton:
            if self.last_drag_position:
                delta = event.pos() - self.last_drag_position
                self.last_drag_position = event.pos()
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
                event.accept()
        else:
            super().mouseMoveEvent(event)


    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.drawing:
            if self.tool == 'rectangle':
                self.drawing = False
                end_point = self.mapToScene(event.position().toPoint())
                rect = QRectF(self.start_point, end_point).normalized()
                self.current_rect_item.setRect(rect)
                self.rectangles.append(self.current_rect_item)
                self.current_rect_item = None
        elif event.button() == Qt.LeftButton:
            self.last_drag_position = None
            event.accept()
        else:
            super().mouseReleaseEvent(event)


    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.tool == 'polygon' and self.drawing:
            self.drawing = False
            self.polygon_points.append(self.polygon_points[0])
            self.current_polygon_item.setPolygon(QPolygonF(self.polygon_points))
            self.polygons.append(self.current_polygon_item)
            self.current_polygon_item = None
            self.polygon_points = []
            if self.temp_line:
                self.scene.removeItem(self.temp_line)
                self.temp_line = None

    def save_annotations(self, output_path):
        if self.image_item:
            image = self.image_item.pixmap().toImage()
            painter = QPainter(image)
            for rect_item in self.rectangles:
                rect = rect_item.rect()
                painter.setPen(QPen(QColor(255, 0, 0), 2))
                painter.drawRect(rect)
            for polygon_item in self.polygons:
                polygon = polygon_item.polygon()
                painter.setPen(QPen(QColor(255, 0, 0), 2))
                painter.drawPolygon(polygon)
            image.save(output_path)
            painter.end()

    def clear_annotations(self):
        for rect_item in self.rectangles:
            self.scene.removeItem(rect_item)
        self.rectangles.clear()
        for polygon_item in self.polygons:
            self.scene.removeItem(polygon_item)
        self.polygons.clear()

    def set_tool(self, tool):
        self.tool = tool
        if tool is None:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        else:
            self.setDragMode(QGraphicsView.NoDrag)