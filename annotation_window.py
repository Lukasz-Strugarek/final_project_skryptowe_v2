import os
import pickle
from PySide6.QtGui import QPainter, QPen, QColor, QPixmap, QMouseEvent, QPolygonF, QAction
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, \
    QHBoxLayout, QGraphicsRectItem, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QToolBar, QGraphicsPolygonItem
from PySide6.QtCore import Qt, QRectF

class AnotationWindow(QMainWindow):
    def __init__(self, controller, filepath):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Adnotacje obrazów medycznych")
        self.setGeometry(100, 100, 1200, 900)

        self.annotation_widget = self.AnnotationWidget(filepath)

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

        self.save_button = QPushButton("Export to image")
        self.clear_button = QPushButton("Wyczyść adnotacje")
        self.back_button = QPushButton("Cancel")
        self.save_and_close_button = QPushButton("Save and Close")

        self.save_button.clicked.connect(self.export_to_image_annotations)
        self.clear_button.clicked.connect(self.clear_annotations)
        self.back_button.clicked.connect(self.cancel_annotations)
        self.save_and_close_button.clicked.connect(self.save_and_close_annotations)

        layout = QVBoxLayout()
        layout.addWidget(self.annotation_widget)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.save_and_close_button)
        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)

        self.annotation_widget.load_image(filepath)

        self.setCentralWidget(container)

    def select_tool(self, tool):
        self.annotation_widget.set_tool(tool)
        self.rect_action.setChecked(tool == 'rectangle')
        self.polygon_action.setChecked(tool == 'polygon')

    def export_to_image_annotations(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Zapisz adnotacje", "", "Obrazy (*.png *.jpg *.jpeg)")
        if file_name:
            self.annotation_widget.save_annotations(file_name)

    def clear_annotations(self):
        self.annotation_widget.clear_annotations()

    def cancel_annotations(self):
        self.controller.load_initial_window()

    def save_and_close_annotations(self):
        self.annotation_widget.save_annotations_to_pickle()
        self.controller.load_initial_window()

    class AnnotationWidget(QGraphicsView):
        def __init__(self, filepath):
            super().__init__()
            self.filepath = filepath
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
            self.load_annotations_from_pickle()

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
                    self.temp_line = self.scene.addLine(self.polygon_points[-1].x(), self.polygon_points[-1].y(),
                                                        point.x(), point.y(), QPen(Qt.red, 2))
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
                    self.tool = None
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

        def load_annotations_from_pickle(self):
            pickle_path = self.get_pickle_path(self.filepath)
            if os.path.exists(pickle_path):
                with open(pickle_path, 'rb') as f:
                    data = pickle.load(f)
                    for annotation in data["annotations"]:
                        if annotation["type"] == "rectangle":
                            rect_item = QGraphicsRectItem(QRectF(annotation["start"], annotation["end"]))
                            rect_item.setPen(QPen(Qt.red, 2))
                            self.rectangles.append(rect_item)
                            self.scene.addItem(rect_item)
                        elif annotation["type"] == "polygon":
                            polygon_item = QGraphicsPolygonItem(QPolygonF(annotation["points"]))
                            polygon_item.setPen(QPen(Qt.red, 2))
                            self.polygons.append(polygon_item)
                            self.scene.addItem(polygon_item)

        def save_annotations_to_pickle(self):
            pickle_path = self.get_pickle_path(self.filepath)
            annotations = {"annotations": []}
            for rect_item in self.rectangles:
                annotations["annotations"].append({
                    "type": "rectangle",
                    "start": rect_item.rect().topLeft(),
                    "end": rect_item.rect().bottomRight()
                })
            for polygon_item in self.polygons:
                annotations["annotations"].append({
                    "type": "polygon",
                    "points": [point for point in polygon_item.polygon()]
                })
            with open(pickle_path, 'wb') as f:
                pickle.dump(annotations, f)

        @staticmethod
        def get_pickle_path(filepath):
            base, _ = os.path.splitext(filepath)
            return base + "_anot.pkl"
