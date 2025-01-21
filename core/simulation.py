import math
import threading
import pygame
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, QObject
from core.agent_model import WolfModel, DeerHabitats
from core.math_model import PopulationModel
from gui.visualization import visualization_init, visualization_update
from gui.gui_components import GUIComponents


class SignalManager(QObject):
    """Klasa zarządzająca sygnałami do komunikacji między wątkiem symulacji a GUI."""
    update_visualization_signal = pyqtSignal()


class Simulation:
    def __init__(self):
        self.signal_manager = SignalManager()
        self.signal_manager.update_visualization_signal.connect(self.update_visualization)

        self.app = QApplication([])
        self.gui_components = GUIComponents(
            start_simulation=self.start_simulation,
            stop_simulation=self.stop_simulation,
            reset_simulation=self.reset_simulation,
        )

        self.gui_components.show()

        # Inicjalizacja symulacji
        self.wolf_population = PopulationModel()
        self.wolf_count = self.wolf_population.population[0]
        self.killed_wolves = 0
        self.wolves_to_kill = 0
        self.simulation_started = False
        self.thread = None
        self.steps = -1
        self.steps_per_year = 72
        self.current_year = 2000

        self.grid_size = 20
        self.pygame_screen, self.wolf_image, self.grid_color, self.background_color = visualization_init()
        self.cols = self.pygame_screen.get_width() // self.grid_size
        self.rows = self.pygame_screen.get_height() // self.grid_size

        self.wolves = WolfModel(self.wolf_count, self.cols, self.rows)
        self.deer_habitats = DeerHabitats(35, self.cols, self.rows)

        # Podpięcie sygnałów GUI
        self.gui_components.step_combobox.currentIndexChanged.connect(self.update_grid_size)
        self.gui_components.food_access_slider.valueChanged.connect(self.update_food_access)

        self.update_visualization()

    def update_grid_size(self):
        """Aktualizuje rozmiar siatki i kroki w roku na podstawie wybranego trybu."""
        selected_option = self.gui_components.get_selected_steps()
        steps_options = ["week", "two weeks", "month"]
        steps_values = [72, 36, 12]
        self.steps_per_year = steps_values[steps_options.index(selected_option)]

        if self.steps_per_year == 72:
            self.grid_size = 20
        elif self.steps_per_year == 36:
            self.grid_size = 40
        elif self.steps_per_year == 12:
            self.grid_size = 60

        self.cols = self.pygame_screen.get_width() // self.grid_size
        self.rows = self.pygame_screen.get_height() // self.grid_size

        self.wolves = WolfModel(self.wolf_count, self.cols, self.rows)
        self.deer_habitats = DeerHabitats(35, self.cols, self.rows, self.grid_size)

        self.update_visualization()

    def update_food_access(self):
        """Aktualizuje dostęp do pożywienia na podstawie pozycji suwaka."""
        food_access_value = self.gui_components.food_access_slider.value() / 10.0
        self.deer_habitats.deer_count = math.floor(food_access_value * 35)
        self.deer_habitats.adjust_deer_population()
        self.update_visualization()

    def start_simulation(self):
        """Rozpoczyna symulację w osobnym wątku."""
        if not self.simulation_started:
            self.simulation_started = True
            self.wolf_population.steps_in_year = self.steps_per_year
            self.gui_components.disable_steps_selection()
            self.thread = threading.Thread(target=self.run_simulation)
            self.thread.daemon = True
            self.thread.start()

    def stop_simulation(self):
        """Zatrzymuje symulację."""
        self.simulation_started = False

    def reset_simulation(self):
        """Resetuje symulację do stanu początkowego."""
        self.stop_simulation()
        self.wolves = WolfModel(self.wolf_count, self.cols, self.rows)
        self.steps = -1
        self.current_year = 2000
        self.killed_wolves = 0
        self.wolves_to_kill = 0
        self.gui_components.update_year_counter(self.current_year)
        self.gui_components.update_wolf_counter(self.wolf_count)
        self.gui_components.update_killed_wolf_counter(self.killed_wolves)
        self.gui_components.enable_steps_selection()
        self.gui_components.death_rate_slider.setValue(10)
        self.gui_components.birth_rate_slider.setValue(10)
        self.gui_components.food_access_slider.setValue(10)
        self.gui_components.hunting_slider.setValue(10)
        self.update_visualization()

    def update_simulation_state(self):
        """
        Aktualizuje stan symulacji, w tym poruszanie watah wilków i jeleni oraz ich populacje.
        """
        death_rate = self.gui_components.death_rate_slider.value() / 10.0
        birth_rate = self.gui_components.birth_rate_slider.value() / 10.0
        food_access = self.gui_components.food_access_slider.value() / 10.0
        hunting = self.gui_components.hunting_slider.value() / 10.0

        self.wolf_population.death_rate = death_rate
        self.wolf_population.birth_rate = birth_rate
        self.wolf_population.food_access = food_access
        self.wolf_population.hunting = hunting
        self.deer_habitats.deer_count = math.floor(food_access * 35)
        self.deer_habitats.adjust_deer_population()

        wolf_positions = [(agent.x, agent.y) for agent in self.wolves.schedule]
        self.deer_habitats.step(wolf_positions)
        deer_positions = self.deer_habitats.get_habitats()
        self.wolves.step(deer_positions)
        self.wolves.split_large_packs()

        killed_wolves = self.wolf_population.update_population(self.wolves, self.current_year, self.steps)
        return killed_wolves

    def check_yearly_update(self):
        """
        Obsługuje logikę związaną z aktualizacją roku oraz resetuje liczniki.
        """
        if self.steps % self.steps_per_year == 0 and self.steps > 0:
            self.killed_wolves += self.wolves_to_kill
            self.gui_components.update_killed_wolf_counter(self.killed_wolves)
            self.wolves_to_kill = 0
            self.current_year += 1
            self.gui_components.update_year_counter(self.current_year)
            self.steps = -1

    def run_simulation(self):
        """Pętla symulacji."""
        clock = pygame.time.Clock()
        while self.simulation_started:
            # Aktualizacja stanu symulacji
            killed_wolves = self.update_simulation_state()

            # Sprawdzenie i aktualizacja licznika rocznego
            self.steps += 1
            self.check_yearly_update()

            # Aktualizacja zabitych wilków, jeśli to konieczne
            if self.wolves_to_kill == 0 and killed_wolves > 0:
                self.wolves_to_kill = killed_wolves

            # Aktualizacja liczby wilków
            wolf_total = sum(agent.wolf_count for agent in self.wolves.schedule)
            self.gui_components.update_wolf_counter(wolf_total)

            # Emitowanie sygnału do aktualizacji GUI
            self.signal_manager.update_visualization_signal.emit()
            speed = self.gui_components.simulation_speed_slider.value()
            clock.tick(speed)

    def update_visualization(self):
        """Aktualizuje wizualizację na podstawie aktualnego stanu symulacji."""
        active_packs = self.wolves.schedule
        pack_positions = [(agent.x, agent.y) for agent in active_packs]
        wolf_count = [agent.wolf_count for agent in active_packs]

        visualization_update(
            self.pygame_screen,
            self.wolf_image,
            self.grid_size,
            pack_positions,
            wolf_count,
            self.background_color,
            self.grid_color,
            self.deer_habitats.get_habitats()
        )
        self.gui_components.update_canvas_from_pygame(self.pygame_screen)

    def run(self):
        """Uruchamia aplikację."""
        self.app.exec_()

