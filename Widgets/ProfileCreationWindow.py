from functions.pickle_functions import *
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget, QListWidget, QLabel, QLineEdit, QMessageBox, \
    QColorDialog


class ProfileManager(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
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
        self.controller.load_initial_window()