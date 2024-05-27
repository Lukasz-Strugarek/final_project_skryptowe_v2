import pickle
import shutil
import sys
import os
from PySide6.QtGui import QPainter, QPen, QColor, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QListWidget, QFileDialog, \
    QHBoxLayout, QLabel, QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QFormLayout, QMessageBox, QGraphicsRectItem, \
    QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QColorDialog
from PySide6.QtCore import Qt, QRectF
from tiff_splitter import split_tiff


def load_profiles():
    if os.path.exists('profiles.pkl'):
        try:
            with open('profiles.pkl', 'rb') as file:
                return pickle.load(file)
        except EOFError:
            return {}
    return {}

def save_profiles(profiles):
    with open('profiles.pkl', 'wb') as file:
        pickle.dump(profiles, file)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initialize()

    def initialize(self):


        self.setWindowTitle("Moja Aplikacja")
        self.setGeometry(100, 100, 400, 200)

        # Tworzenie głównego widgetu
        main_widget = QWidget()


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

        #Tworzenie przycisku do dodania profilu
        self.profile_button = QPushButton("Add new profile")
        layout.addWidget(self.profile_button)

        # Ustawienie layoutu dla głównego widgetu
        main_widget.setLayout(layout)

        # Podłączenie sygnałów do slotów
        self.new_button.clicked.connect(self.create_new_file)
        self.open_button.clicked.connect(self.open_file)
        self.tiff_button.clicked.connect(self.tiff_split)
        self.profile_button.clicked.connect(self.new_profile)


        self.setCentralWidget(main_widget)


    def tiff_split(self):
        self.tiff_window = TiffWindow(self)
        self.setCentralWidget(self.tiff_window)

    def new_profile(self):
        self.new_profile_window = ProfileManager(self)
        self.setCentralWidget(self.new_profile_window)

    def create_new_file(self):
        # Funkcja obsługująca przycisk "Nowy"
        self.new_image_window = NewWindow()
        self.new_image_window.show()

    def open_file(self):
        # Funkcja obsługująca przycisk "Otwórz"
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Otwórz plik", "", "Wszystkie pliki (*)", options=options)
        base, _ = os.path.splitext(file_name)
        anot_file_path = f"{base}_anot.pkl"
        if file_name and os.path.exists(anot_file_path):
            self.anot_window = AnotationWindow(self, file_name)
            self.setCentralWidget(self.anot_window)
        elif not os.path.exists(anot_file_path):
            QMessageBox.warning(self, "Error", "NO ANNOTATION FILE FOUND")



class NewWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("New image")
        self.setGeometry(150, 150, 600, 200)

        self.profiles = load_profiles()
        print(self.profiles)

        layout = QVBoxLayout()

        # Tworzenie listy rozwijanej do wyboru trybu
        self.mode_selector = QComboBox(self)
        self.mode_selector.addItems(list(self.profiles.keys()))

        #pole na ścieżkę
        self.path_input = QLineEdit(self)
        self.path_input.setPlaceholderText("Wybierz ścieżkę obrazu")
        self.path_input.setReadOnly(True)

        # Tworzenie przycisku do wyboru ścieżki zapisu
        self.path_button = QPushButton("Wybierz ścieżkę")
        self.path_button.clicked.connect(self.select_image_path)

        # Layout dla wyboru ścieżki
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.path_button)

        # pole na ścieżkę
        self.destination_path_input = QLineEdit(self)
        self.destination_path_input.setPlaceholderText("Wybierz ścieżkę zapisu")
        self.destination_path_input.setReadOnly(True)

        # Tworzenie przycisku do wyboru ścieżki zapisu
        self.destination_path_button = QPushButton("Wybierz ścieżkę")
        self.destination_path_button.clicked.connect(self.select_save_path)

        # Layout dla wyboru ścieżki
        destination_path_layout = QHBoxLayout()
        destination_path_layout.addWidget(self.destination_path_input)
        destination_path_layout.addWidget(self.destination_path_button)


        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.confirm)

        # Dodanie elementów do layoutu
        layout.addWidget(QLabel("Enter image type:"))
        layout.addWidget(self.mode_selector)
        layout.addWidget(QLabel("New image path:"))
        layout.addLayout(path_layout)
        layout.addWidget(QLabel("Annotated image path:"))
        layout.addLayout(destination_path_layout)
        layout.addWidget(self.confirm_button)

        # Ustawienie layoutu dla głównego widgetu
        self.setLayout(layout)


    def confirm(self):
        if self.mode_selector != "" and self.destination_path_input.text() and self.path_input.text():
            anot_list = {"type": self.mode_selector.currentText(),
                         "annotations": []
                        }

            source_file_path = self.path_input.text()
            destination_folder = self.destination_path_input.text()

            if not os.path.isfile(source_file_path):
                QMessageBox.warning(self, "Warning", "Source file does not exist!")
                return

                # Sprawdzenie, czy folder docelowy istnieje
            if not os.path.isdir(destination_folder):
                QMessageBox.warning(self, "Warning", "Destination folder does not exist!")
                return


            file_name = os.path.basename(source_file_path)
            base_name, file_extension = os.path.splitext(file_name)

            # Ścieżka do skopiowanego pliku
            destination_file_path = os.path.join(destination_folder, file_name)

            try:
                # Kopiowanie pliku do folderu docelowego
                shutil.copy2(source_file_path, destination_file_path)

            except shutil.SameFileError:
                QMessageBox.warning(self, "Error", "File already exists")

            # Ścieżka do pliku z końcówką _anot.pkl
            anot_file_path = os.path.join(destination_folder, f"{base_name}_anot.pkl")


            with open(anot_file_path, 'wb') as anot_file:
                pickle.dump(anot_list, anot_file)

            QMessageBox.information(self, "Info", "Files have been successfully created!")



    def select_image_path(self):
        # Funkcja otwierająca dialog do wyboru ścieżki zapisu
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Wybierz ścieżkę zapisu", "", "Wszystkie pliki (*)",
                                                   options=options)
        if file_path:
            self.path_input.setText(file_path)

    def select_save_path(self):
        options = QFileDialog.Options()
        output_path = QFileDialog.getExistingDirectory(self, "Wybierz ścieżkę zapisu", options=options)
        if output_path:
            self.destination_path_input.setText(output_path)

class TiffWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        print(type(self.main_window))
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
        self.main_window.setGeometry(100, 100, 400, 200)
        self.main_window.setCentralWidget(MainWindow())


    def cancel_script(self):
        self.main_window.setGeometry(100, 100, 400, 200)
        self.main_window.setCentralWidget(MainWindow())


from PySide6.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsPolygonItem, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QWidget, QMessageBox, QToolBar
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QPolygonF, QMouseEvent, QAction
from PySide6.QtCore import Qt, QRectF, QPointF


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

class AnotationWindow(QMainWindow):
    def __init__(self, main_window, filepath):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Adnotacje obrazów medycznych")
        self.main_window.setGeometry(100, 100, 1200, 900)

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
        self.main_window.setGeometry(100, 100, 400, 200)
        self.main_window.setCentralWidget(MainWindow())


class ProfileManager(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.profiles = load_profiles()
        self.labels = {}

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Profile Manager")

        layout = QVBoxLayout()

        self.profile_name_label = QLabel("Profile Name:")
        self.profile_name_entry = QLineEdit()

        self.label_name_label = QLabel("Label Name:")
        self.label_name_entry = QLineEdit()

        self.add_label_button = QPushButton("Add Label")
        self.add_label_button.clicked.connect(self.add_label)

        self.labels_listbox = QListWidget()

        self.save_profile_button = QPushButton("Save Profile")
        self.save_profile_button.clicked.connect(self.save_profile)

        self.cancel_profile_button = QPushButton("Cancel")
        self.cancel_profile_button.clicked.connect(self.cancel_profile)

        layout.addWidget(self.profile_name_label)
        layout.addWidget(self.profile_name_entry)
        layout.addWidget(self.label_name_label)
        layout.addWidget(self.label_name_entry)
        layout.addWidget(self.add_label_button)
        layout.addWidget(self.labels_listbox)
        layout.addWidget(self.save_profile_button)
        layout.addWidget(self.cancel_profile_button)

        self.setLayout(layout)

    def add_label(self):
        label_name = self.label_name_entry.text()
        if not label_name:
            QMessageBox.warning(self, "Warning", "Label name cannot be empty!")
            return

        color = QColorDialog.getColor()
        if not color.isValid():
            return

        color_name = color.name()
        self.labels[label_name] = color_name
        self.labels_listbox.addItem(f"{label_name}: {color_name}")
        self.label_name_entry.clear()

    def save_profile(self):
        profile_name = self.profile_name_entry.text()
        if not profile_name:
            QMessageBox.warning(self, "Warning", "Profile name cannot be empty!")
            return

        self.profiles[profile_name] = self.labels.copy()
        save_profiles(self.profiles)

        self.labels_listbox.clear()
        self.profile_name_entry.clear()
        self.labels.clear()

        QMessageBox.information(self, "Info", "Profile saved successfully!")

    def cancel_profile(self):
        self.main_window.setGeometry(100, 100, 400, 200)
        self.main_window.setCentralWidget(MainWindow())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())