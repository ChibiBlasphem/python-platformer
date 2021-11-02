import pygame
from animation import Animation
from decoration import Sky, SkyStyle
from game_data import levels
from helpers import import_folder, load_image


class Node(pygame.sprite.Sprite):
    def __init__(self, position, level, available=False):
        super().__init__()
        frames = import_folder(levels[level]["node_graphics"])
        self.animation = Animation(frames, 0.15)
        self.level = level
        self.available = available

        self.image = self.animation.get_frame()
        self.rect = self.image.get_rect(center=position)

        self.detection_zone = pygame.Rect(self.rect.center - pygame.math.Vector2(8, 8) / 2, (8, 8))

    def update(self):
        if self.available:
            self.animation.update()
            self.image = self.animation.get_frame()
        else:
            tint_surf = self.image.copy()
            tint_surf.fill("black", special_flags=pygame.BLEND_RGBA_MULT)
            self.image.blit(tint_surf, (0, 0))


class Icon(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.position = position
        self.image = load_image("./graphics/overworld/hat.png")
        self.rect = self.image.get_rect(center=position)

    def update(self):
        self.rect.center = self.position


class Overworld:
    move_direction: pygame.math.Vector2 | None = None
    next_level: int | None = None
    last_direction: int | None = None
    speed = 8
    allow_input = False
    input_timer_duration = 300

    def __init__(self, start_level: int, max_level: int, surface: pygame.Surface, create_level):
        self.display_surface = surface
        self.max_level = max_level
        self.current_level = start_level
        self.create_level = create_level

        self.__setup_nodes()
        self.__setup_icon()
        self.sky = Sky(8, SkyStyle.OVERWORLD)

        self.start_time = pygame.time.get_ticks()

    def run(self):
        self.__check_input_timer()
        self.__input()
        self.__update_icon_position()

        self.sky.draw(self.display_surface)

        self.__draw_paths()
        self.nodes.update()
        self.nodes.draw(self.display_surface)
        self.icon.update()
        self.icon.draw(self.display_surface)

    def __setup_nodes(self):
        self.nodes = pygame.sprite.Group()
        for (level, node_data) in levels.items():
            node = Node(position=node_data.get("node_position"), level=level, available=level <= self.max_level)
            self.nodes.add(node)

    def __setup_icon(self):
        self.icon = pygame.sprite.GroupSingle()
        level = levels[self.current_level]
        icon = Icon(level.get("node_position"))
        self.icon.add(icon)

    def __draw_paths(self):
        if self.max_level > 0:
            points = [node_data.get("node_position")
                      for (index, node_data) in levels.items() if index <= self.max_level]
            pygame.draw.lines(self.display_surface, "#a04f45", False, points, 6)

    def __input(self):
        keys = pygame.key.get_pressed()

        if not self.allow_input:
            return

        current_level = self.next_level if self.next_level != None else self.current_level

        is_next = keys[pygame.K_RIGHT] and current_level < self.max_level and (
            self.last_direction == None or self.last_direction < 0)
        is_prev = keys[pygame.K_LEFT] and current_level > 0 and (self.last_direction == None or self.last_direction > 0)

        if is_next or is_prev:
            next_level = current_level + (1 if is_next else -1)

            self.last_direction = next_level - current_level
            self.move_direction = self.__get_movement_data(current_level, next_level)
            self.next_level = next_level
        elif keys[pygame.K_SPACE]:
            self.create_level(self.current_level)

    def __get_movement_data(self, current_level, next_level):
        start = pygame.math.Vector2(levels[current_level].get("node_position"))
        end = pygame.math.Vector2(levels[next_level].get("node_position"))

        return (end - start).normalize()

    def __update_icon_position(self):
        if self.next_level != None and self.move_direction:
            icon_sprite: Icon = self.icon.sprite
            target_node: Node = next(node for node in self.nodes.sprites() if node.level == self.next_level)

            icon_sprite.position += self.move_direction * self.speed
            if target_node.detection_zone.collidepoint(icon_sprite.position):
                self.current_level = self.next_level
                self.move_direction = self.next_level = self.last_direction = None

    def __check_input_timer(self):
        if not self.allow_input:
            current_time = pygame.time.get_ticks()
            if current_time - self.start_time >= self.input_timer_duration:
                self.allow_input = True
