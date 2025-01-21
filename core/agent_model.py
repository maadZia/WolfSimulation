import random


class WolfPack:
    """
    Reprezentuje pojedynczą watahę wilków.
    Każda wataha ma unikalne ID, pozycję na siatce i liczbę wilków.
    """
    def __init__(self, id, x, y, wolf_count):
        self.id = id
        self.x = x
        self.y = y
        self.wolf_count = wolf_count

    def move(self, deer_positions, occupied_positions, rows, cols):
        """
        Przesuwa watahę w kierunku jelenia lub losowo, jeśli jelenie nie są dostępne.
        """
        nearest_deer = None

        for deer in sorted(deer_positions, key=lambda d: abs(d[0] - self.x) + abs(d[1] - self.y)):
            if occupied_positions.get(deer, 0) < 2:  # max 2 watahy przy jeleniu
                nearest_deer = deer
                break

        if nearest_deer:
            dx = 1 if nearest_deer[0] > self.x else -1 if nearest_deer[0] < self.x else 0
            dy = 1 if nearest_deer[1] > self.y else -1 if nearest_deer[1] < self.y else 0

            new_x, new_y = self.x + dx, self.y + dy

            if 0 <= new_x < cols and 0 <= new_y < rows:
                occupied_positions[nearest_deer] = occupied_positions.get(nearest_deer, 0) + 1
                return new_x, new_y

        possible_moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        random.shuffle(possible_moves)

        for dx, dy in possible_moves:
            new_x, new_y = self.x + dx, self.y + dy
            if 0 <= new_x < cols and 0 <= new_y < rows and (new_x, new_y) not in occupied_positions:
                return new_x, new_y

        return self.x, self.y


class WolfModel:
    """
    Model agentowy zarządzający watahami wilków.
    """
    def __init__(self, wolf_count, cols, rows):
        self.cols = cols
        self.rows = rows
        self.grid = {}
        self.schedule = self.init_agents(wolf_count)

    def init_agents(self, wolf_count):
        """
        Inicjalizuje watahy z losową liczbą wilków oraz pozycjami na siatce.
        """
        agents = []
        remaining_wolves = wolf_count
        while remaining_wolves > 0:
            wolves_in_pack = random.randint(1, min(10, remaining_wolves))
            x, y = random.randint(0, self.cols - 1), random.randint(0, self.rows - 1)
            while (x, y) in self.grid:
                x, y = random.randint(0, self.cols - 1), random.randint(0, self.rows - 1)

            agents.append(WolfPack(len(agents), x, y, wolves_in_pack))
            self.grid[(x, y)] = agents[-1]
            remaining_wolves -= wolves_in_pack
        return agents

    def split_large_packs(self):
        """
        Dzieli zbyt duże watahy na mniejsze, aby zachować realizm ekosystemu.
        """
        new_agents = []
        for agent in self.schedule[:]:
            if agent.wolf_count > 10:
                pack_half = agent.wolf_count // 2
                new_pack = agent.wolf_count - pack_half
                agent.wolf_count = pack_half

                new_id = len(self.schedule) + len(new_agents)
                new_agent = WolfPack(new_id, agent.x, agent.y, new_pack)
                new_agents.append(new_agent)

        self.schedule.extend(new_agents)

    def step(self, deer_positions):
        """
        Iteruje przez wszystkich agentów i przesuwa ich, aktualizując pozycje.
        """
        occupied_positions = {}
        new_positions = {}

        for agent in self.schedule:
            new_x, new_y = agent.move(deer_positions, occupied_positions, self.rows, self.cols)
            occupied_positions[(new_x, new_y)] = occupied_positions.get((new_x, new_y), 0) + 1
            new_positions[agent] = (new_x, new_y)

        for agent, (new_x, new_y) in new_positions.items():
            agent.x, agent.y = new_x, new_y

        self.split_large_packs()
        return [(agent.x, agent.y) for agent in self.schedule]

    def update_agents(self):
        # usunięcie watah które mają 0 wilków
        self.schedule = [agent for agent in self.schedule if agent.wolf_count > 0]


class DeerHabitats:
    """
    Model odpowiadający za siedliska jeleni.
    Przechowuje informacje o pozycjach jeleni i zarządza ich ruchem oraz populacją.
    """
    def __init__(self, count, cols, rows, grid_size=20):
        self.cols = cols
        self.rows = rows
        self.grid_size = grid_size
        self.deer_count = 35
        self.habitats = self.generate_deer_habitats(count)

    def generate_deer_habitats(self, count):
        """
        Generuje losowe pozycje siedlisk jeleni na siatce.
        """
        deer_habitats = []
        while len(deer_habitats) < count:
            x, y = random.randint(0, self.cols - 1), random.randint(0, self.rows - 1)
            deer_habitats.append((x, y))
        return deer_habitats

    def get_habitats(self):
        """
        Zwraca listę aktualnych pozycji jeleni.
        """
        return self.habitats

    def move(self, x, y, wolf_positions):
        """
        Przesuwa jelenia w zależności od pozycji wilków i aktualnej pozycji.
        """
        if self.grid_size == 20:
            d = 3
        else:
            d = 1

        nearby_wolves = [(wx, wy) for wx, wy in wolf_positions if abs(wx - x) <= d and abs(wy - y) <= d]

        if nearby_wolves:
            closest_wolf = min(nearby_wolves, key=lambda wp: abs(wp[0] - x) + abs(wp[1] - y))
            dx = x - closest_wolf[0]
            dy = y - closest_wolf[1]

            possible_moves = [(3, 0), (-3, 0), (0, 3), (0, -3), (3, 3), (3, -3), (-3, 3), (-3, -3)]
            safe_moves = [(mx, my) for mx, my in possible_moves if mx * dx <= 0 or my * dy <= 0]

            if safe_moves:
                move = random.choice(safe_moves)
            else:
                move = random.choice(possible_moves)

            new_x = max(0, min(self.cols - 1, x + move[0]))
            new_y = max(0, min(self.rows - 1, y + move[1]))
        else:
            new_x, new_y = x, y

        return new_x, new_y

    def step(self, wolf_positions):
        """
        Iteruje przez wszystkie jelenie i aktualizuje ich pozycje.
        """
        new_habitats = []
        for x, y in self.habitats:
            new_x, new_y = self.move(x, y, wolf_positions)
            new_habitats.append((new_x, new_y))

        self.habitats = new_habitats

    def adjust_deer_population(self):
        """
        Dostosowuje liczbę jeleni na siatce do zadanej wielkości populacji.
        """
        current_deer_count = len(self.habitats)

        if current_deer_count < self.deer_count:
            deer_to_add = self.deer_count - current_deer_count
            for _ in range(deer_to_add):
                x, y = random.randint(0, self.cols - 1), random.randint(0, self.rows - 1)
                self.habitats.append((x, y))
        elif current_deer_count > self.deer_count:
            deer_to_remove = current_deer_count - self.deer_count
            self.habitats = self.habitats[:-deer_to_remove]
