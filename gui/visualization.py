import pygame


def visualization_init():
    """
    Inicjalizuje wizualizację za pomocą PyGame, tworząc powierzchnię dla symulacji.
    """
    pygame.init()
    screen_surface = pygame.Surface((900, 500))

    wolf_image = pygame.image.load("gui/img/wolf.png")
    wolf_image = pygame.transform.scale(wolf_image, (20, 20))

    grid_color = (200, 200, 200)
    background_color = (255, 255, 255)

    return screen_surface, wolf_image, grid_color, background_color


def draw_grid(surface, grid_size, grid_color):
    """
    Rysuje siatkę na powierzchni symulacji.
    """
    for x in range(0, surface.get_width(), grid_size):
        pygame.draw.line(surface, grid_color, (x, 0), (x, surface.get_height()))
    for y in range(0, surface.get_height(), grid_size):
        pygame.draw.line(surface, grid_color, (0, y), (surface.get_width(), y))


def visualization_update(surface, wolf_image, grid_size, pack_positions, wolf_count, background_color,
                         grid_color, deer_habitats):
    """
    Aktualizuje wizualizację symulacji.
    """
    surface.fill(background_color)

    deer_color = (217, 245, 219)
    for (x, y) in deer_habitats:
        screen_x = int(x * grid_size)
        screen_y = int(y * grid_size)
        pygame.draw.circle(surface, deer_color, (screen_x + grid_size // 2, screen_y + grid_size // 2), 20 * 2)

    draw_grid(surface, grid_size, grid_color)
    font = pygame.font.Font(None, 18)

    # rysowanie watah
    for (x, y), count in zip(pack_positions, wolf_count):
        screen_x = int(x * grid_size)
        screen_y = int(y * grid_size)

        # wyśrodkowanie ikony wilka
        wolf_width = wolf_image.get_width()
        wolf_height = wolf_image.get_height()
        centered_x = screen_x + (grid_size - wolf_width) // 2
        centered_y = screen_y + (grid_size - wolf_height) // 2

        surface.blit(wolf_image, (centered_x, centered_y))

        count_text = font.render(str(count), True, (0, 0, 0))
        surface.blit(count_text, (centered_x - (count_text.get_width() / 2), centered_y))

