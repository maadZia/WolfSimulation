import pygame
from PyQt5.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox,
    QSlider, QWidget, QGraphicsScene, QGraphicsView,
)
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QRect
import os


class GUIComponents(QWidget):
    def __init__(self, start_simulation, stop_simulation, reset_simulation):
        super().__init__()
        self.start_simulation = start_simulation
        self.stop_simulation = stop_simulation
        self.reset_simulation = reset_simulation

        self.setWindowTitle("Wolf Simulation")
        self.setFixedSize(1350, 700)

        font_style = "font-size: 12pt; font-weight: bold;"

        self.centralwidget = QWidget(self)

        # Left Control Panel
        self.control_panel = QWidget(self.centralwidget)
        self.control_panel.setGeometry(QRect(20, 30, 371, 391))

        self.control_layout = QVBoxLayout(self.control_panel)
        self.control_layout.setContentsMargins(0, 0, 0, 0)

        self.parameters_label = QLabel(self.control_panel)
        self.parameters_label.setStyleSheet(font_style)
        self.parameters_label.setText("Choose simulation parameters")
        self.control_layout.addWidget(self.parameters_label)

        # Suwaki
        self.simulation_speed_slider = self.add_slider(
            "Simulation speed:", self.control_layout, 1, 10, 1, self.update_simulation_speed_label
        )
        self.simulation_speed_slider.setStyleSheet("""
            QSlider::handle:horizontal {background: #edaa45;}
            QSlider::sub-page:horizontal {background: #fcebae;} 
        """)
        self.food_access_slider = self.add_slider(
            "Food access:", self.control_layout, 5, 15, 10, self.update_food_access_label
        )
        self.food_access_slider.setStyleSheet("""
            QSlider::handle:horizontal {background: #47d170;} 
            QSlider::sub-page:horizontal {background: #bfe0c9;}
        """)
        self.death_rate_slider = self.add_slider(
            "Death rate:", self.control_layout, 5, 15, 10, self.update_death_rate_label
        )
        self.death_rate_slider.setStyleSheet("""
            QSlider::handle:horizontal {background: #7a33d6;} 
            QSlider::sub-page:horizontal {background: #b9bded;} 
        """)
        self.birth_rate_slider = self.add_slider(
            "Birth rate:", self.control_layout, 5, 15, 10, self.update_birth_rate_label
        )
        self.birth_rate_slider.setStyleSheet("""
            QSlider::handle:horizontal {background: #cf42a2;} 
            QSlider::sub-page:horizontal {background: #fcaee5;}
        """)
        self.hunting_slider = self.add_slider(
            "Hunting:", self.control_layout, 5, 15, 10, self.update_hunting_label
        )
        self.hunting_slider.setStyleSheet("""
            QSlider::handle:horizontal {background: #ed6f6f;}
            QSlider::sub-page:horizontal {background: #ffbfc5;}
        """)

        # Step count
        self.step_label = QLabel(self.control_panel)
        font = QtGui.QFont()
        self.step_label.setFont(font)
        self.step_label.setText("Step count:")
        self.control_layout.addWidget(self.step_label)

        self.step_combobox = QComboBox(self.control_panel)
        self.steps_options = ["week", "two weeks", "month"]
        self.step_combobox.addItems(self.steps_options)
        self.step_combobox.setCurrentIndex(0)
        self.control_layout.addWidget(self.step_combobox)

        # Visualization Key
        self.key_label = QLabel(self.centralwidget)
        self.key_label.setGeometry(QRect(20, 450, 381, 40))
        self.key_label.setStyleSheet(font_style)
        self.key_label.setText("Visualization key")

        map_image_path = os.path.join(os.path.dirname(__file__), "img/map.png")

        map_pixmap = QPixmap(map_image_path).scaled(300, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.map_label = QLabel(self.centralwidget)
        self.map_label.setPixmap(map_pixmap)
        self.map_label.setGeometry(20, 490, 300, 150)  # Pozycja bezpośrednio pod "Visualization Key"

        wolf_image_path = os.path.join(os.path.dirname(__file__), "img/wolf.png")

        wolf_pixmap = QPixmap(wolf_image_path).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.wolf_icon_label = QLabel(self.centralwidget)
        self.wolf_icon_label.setPixmap(wolf_pixmap)
        self.wolf_icon_label.setGeometry(190, 540, 20, 20)

        self.wolf_text_label = QLabel("- single wolf pack", self.centralwidget)
        self.wolf_text_label.setGeometry(220, 540, 200, 20)

        deer_color = "rgb(217, 245, 219)"

        self.deer_circle_label = QLabel(self.centralwidget)
        self.deer_circle_label.setGeometry(190, 570, 20, 20)
        self.deer_circle_label.setStyleSheet(
            f"background-color: {deer_color}; border: 1px solid lightgreen; "
            f"border-radius: 10px; min-width: 20px; min-height: 20px;"
        )

        self.deer_text_label = QLabel("- deer habitat", self.centralwidget)
        self.deer_text_label.setGeometry(220, 570, 200, 20)

        # Visualization Area
        self.visualization = QGraphicsView(self.centralwidget)
        self.visualization.setGeometry(QRect(410, 100, 920, 520))
        self.visualization_scene = QGraphicsScene()
        self.visualization.setScene(self.visualization_scene)

        # Usunięcie pasków przewijania
        self.visualization.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.visualization.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        padding = 10
        self.visualization_scene.setSceneRect(
            padding, padding, 900 - 2 * padding, 500 - 2 * padding
        )

        # Header with Counters
        self.counter_frame = QWidget(self.centralwidget)
        self.counter_frame.setGeometry(QRect(419, 20, 901, 80))

        self.counter_layout = QHBoxLayout(self.counter_frame)
        self.counter_layout.setContentsMargins(0, 0, 0, 0)

        self.year_counter = QLabel(self.counter_frame)
        self.year_counter.setStyleSheet(font_style)
        self.year_counter.setAlignment(Qt.AlignCenter)
        self.year_counter.setText("Current year: 2000")
        self.counter_layout.addWidget(self.year_counter)

        self.wolf_counter = QLabel(self.counter_frame)
        self.wolf_counter.setStyleSheet(font_style)
        self.wolf_counter.setAlignment(Qt.AlignCenter)
        self.wolf_counter.setText("Wolf count: 100")
        self.counter_layout.addWidget(self.wolf_counter)

        self.killed_counter = QLabel(self.counter_frame)
        self.killed_counter.setStyleSheet(font_style)
        self.killed_counter.setAlignment(Qt.AlignCenter)
        self.killed_counter.setText("Killed wolves: 0")
        self.counter_layout.addWidget(self.killed_counter)

        # Button Panel
        self.button_panel = QWidget(self.centralwidget)
        self.button_panel.setGeometry(QRect(600, 630, 539, 39))

        self.button_layout = QHBoxLayout(self.button_panel)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setSpacing(40)

        start_button = QPushButton("Start")
        start_button.clicked.connect(self.start_simulation)
        start_button.setStyleSheet("background-color: rgb(191, 255, 207);")
        self.button_layout.addWidget(start_button)

        stop_button = QPushButton("Stop")
        stop_button.clicked.connect(self.stop_simulation)
        stop_button.setStyleSheet("background-color: rgb(255, 197, 191);")
        self.button_layout.addWidget(stop_button)

        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(self.reset_simulation)
        reset_button.setStyleSheet("background-color: rgb(191, 217, 255);")
        self.button_layout.addWidget(reset_button)

    def add_slider(self, label_text, layout, minimum, maximum, default, callback):
        """Dodaje slider z dynamicznie aktualizowaną etykietą."""
        slider_label = QLabel(f"{label_text} {default * 10}%" if maximum > 10 else f"{label_text} {default}")
        layout.addWidget(slider_label)

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(minimum)
        slider.setMaximum(maximum)
        slider.setValue(default)
        slider.valueChanged.connect(lambda value: callback(slider_label, value))
        layout.addWidget(slider)

        callback(slider_label, default)

        return slider

    def update_simulation_speed_label(self, label, value):
        label.setText(f"Simulation speed: {value}")

    def update_food_access_label(self, label, value):
        label.setText(f"Food access: {value * 10}%")

    def update_death_rate_label(self, label, value):
        label.setText(f"Death rate: {value * 10}%")

    def update_birth_rate_label(self, label, value):
        label.setText(f"Birth rate: {value * 10}%")

    def update_hunting_label(self, label, value):
        label.setText(f"Hunting: {value * 10}%")

    def update_year_counter(self, year):
        """Aktualizuje licznik roku."""
        self.year_counter.setText(f"Current year: {year}")

    def update_wolf_counter(self, wolf_count):
        """Aktualizuje licznik wilków."""
        self.wolf_counter.setText(f"Wolf count: {wolf_count}")

    def update_killed_wolf_counter(self, killed_wolf_count):
        """Aktualizuje licznik zabitych wilków."""
        self.killed_counter.setText(f"Killed wolves: {killed_wolf_count}")

    def disable_steps_selection(self):
        """Wyłącza możliwość wyboru kroków."""
        self.step_combobox.setDisabled(True)

    def enable_steps_selection(self):
        """Włącza możliwość wyboru kroków."""
        self.step_combobox.setDisabled(False)

    def get_selected_steps(self):
        """Zwraca wybraną opcję kroków."""
        return self.step_combobox.currentText()

    def update_canvas_from_pygame(self, pygame_screen):
        """Aktualizuje wizualizację na podstawie danych z PyGame."""
        pygame_image = pygame.image.tostring(pygame_screen, "RGB")
        q_image = QImage(
            pygame_image,
            pygame_screen.get_width(),
            pygame_screen.get_height(),
            QImage.Format_RGB888,
        )
        pixmap = QPixmap.fromImage(q_image)
        self.visualization_scene.clear()
        self.visualization_scene.addPixmap(pixmap)
