import shutil

from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget, QFileDialog, \
    QHBoxLayout, QLabel, QLineEdit, QComboBox, QMessageBox
from functions.pickle_functions import *

class NewFileWindow(QWidget):
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
        self.path_input.setPlaceholderText("Select image path")
        self.path_input.setReadOnly(True)

        # Tworzenie przycisku do wyboru ścieżki zapisu
        self.path_button = QPushButton("Select path")
        self.path_button.clicked.connect(self.select_image_path)

        # Layout dla wyboru ścieżki
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.path_button)

        # pole na ścieżkę
        self.destination_path_input = QLineEdit(self)
        self.destination_path_input.setPlaceholderText("Select new path")
        self.destination_path_input.setReadOnly(True)

        # Tworzenie przycisku do wyboru ścieżki zapisu
        self.destination_path_button = QPushButton("Select path")
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
                return

            # Ścieżka do pliku z końcówką _anot.pkl
            anot_file_path = os.path.join(destination_folder, f"{base_name}_anot.pkl")


            with open(anot_file_path, 'wb') as anot_file:
                pickle.dump(anot_list, anot_file)

            QMessageBox.information(self, "Info", "Files have been successfully created!")



    def select_image_path(self):
        # Funkcja otwierająca dialog do wyboru ścieżki zapisu
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select path", "", "Obrazy (*.png *.jpg *.jpeg)",
                                                   options=options)
        if file_path:
            self.path_input.setText(file_path)

    def select_save_path(self):
        options = QFileDialog.Options()
        output_path = QFileDialog.getExistingDirectory(self, "Select path", options=options)
        if output_path:
            self.destination_path_input.setText(output_path)