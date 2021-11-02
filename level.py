import pygame

from typing import Callable, Dict, List
from decoration import Clouds, Sky, Water
from enemy import Enemy
from helpers import import_csv_layout, import_tileset, load_image
from particles import ParticleEffect

from settings import tile_size, screen_width, screen_height
from player import Player
from tile import CoinTile, CrateTile, PalmTile, StaticTile, Tile
from game_data import levels

CreateOverworldCallable = Callable[[int, int | None], None]
ChangeCoinsCallable = Callable[[int], None]
ChangeHealthCallable = Callable[[int], None]


class Level:
    current_x = 0

    def __init__(self, current_level: int, surface: pygame.Surface, create_overworld: CreateOverworldCallable, change_coins: ChangeCoinsCallable, change_health: ChangeHealthCallable):
        self.display_surface = surface
        self.current_level = current_level
        self.world_shift = 0

        self.create_overworld = create_overworld
        self.change_coins = change_coins
        self.change_health = change_health

        level_data = levels[current_level]
        level_layout = level_data["layout"]
        self.new_max_level = level_data.get("unlock")

        self.__setup_sounds()
        self.__setup_level(level_layout)

    def run(self):
        self.__check_death()
        self.__check_win()

        # Background decorations
        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface, self.world_shift)
        self.bg_palms_tiles.update(self.world_shift)
        self.bg_palms_tiles.draw(self.display_surface)

        # Dust particles
        self.dust.update(self.world_shift)
        self.dust.draw(self.display_surface)

        # Terrain
        self.terrain_tiles.update(self.world_shift)
        self.terrain_tiles.draw(self.display_surface)
        self.crates_tiles.update(self.world_shift)
        self.crates_tiles.draw(self.display_surface)
        self.grass_tiles.update(self.world_shift)
        self.grass_tiles.draw(self.display_surface)

        # Interactable
        self.explosions.update(self.world_shift)
        self.explosions.draw(self.display_surface)
        self.enemies_tiles.update(self.world_shift)
        self.constraints_tiles.update(self.world_shift)
        self.__manage_enemy_movement()
        self.enemies_tiles.draw(self.display_surface)
        self.coins_tiles.update(self.world_shift)
        self.coins_tiles.draw(self.display_surface)

        # Foreground collidable
        self.fg_palms_tiles.update(self.world_shift)
        self.fg_palms_tiles.draw(self.display_surface)

        # Player
        self.player.update(self.__on_player_action)
        self.__check_coin_collisions()
        self.__check_enemy_collisions()
        self.__manage_horizontal_collision()
        self.__manage_vertical_collision(self.player.sprite.on_ground)
        self.player.draw(self.display_surface)
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)
        self.__update_level_from_player_movement()

        # Water
        self.water.draw(self.display_surface, self.world_shift)

    def __create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            y_position = row_index * tile_size
            for col_index, cell_value in enumerate(row):
                if cell_value != "-1":
                    position = (col_index * tile_size, y_position)

                    if type == "terrain":
                        terrain_tileset = import_tileset(
                            "./graphics/terrain/terrain_tiles.png")
                        terrain_surf = terrain_tileset[int(cell_value)]
                        tile = StaticTile(position, tile_size, terrain_surf)
                    if type == "grass":
                        grass_tileset = import_tileset(
                            "./graphics/decoration/grass/grass.png")
                        grass_surf = grass_tileset[int(cell_value)]
                        tile = StaticTile(position, tile_size, grass_surf)
                    if type == "crates":
                        tile = CrateTile(position, tile_size)
                    if type == "coins":
                        tile = CoinTile(position, tile_size, cell_value)
                    if type == "palms":
                        tile = PalmTile(position, tile_size, cell_value)
                    if type == "enemies":
                        tile = Enemy(position, tile_size)
                    if type == "constraints":
                        tile = Tile(position, tile_size)

                    sprite_group.add(tile)
        return sprite_group

    def __manage_enemy_movement(self):
        for enemy in self.enemies_tiles.sprites():
            if pygame.sprite.spritecollide(enemy, self.constraints_tiles, False):
                enemy.reverse()

    def __setup_player(self, layout):
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()

        for row_index, row in enumerate(layout):
            y_position = row_index * tile_size
            for col_index, cell_value in enumerate(row):
                position = (col_index * tile_size, y_position)
                if cell_value == "0":
                    tile = Player(position, self.display_surface)
                    self.player.add(tile)
                if cell_value == "1":
                    surf = load_image("./graphics/character/hat.png")
                    tile = StaticTile(position, tile_size, surf)
                    self.goal.add(tile)

    def __setup_level(self, level_data):
        player_layout = import_csv_layout(level_data["player"])
        self.__setup_player(player_layout)

        terrain_layout = import_csv_layout(level_data["terrain"])
        self.terrain_tiles = self.__create_tile_group(
            terrain_layout, "terrain")

        crates_layout = import_csv_layout(level_data["crates"])
        self.crates_tiles = self.__create_tile_group(crates_layout, "crates")

        grass_layout = import_csv_layout(level_data["grass"])
        self.grass_tiles = self.__create_tile_group(grass_layout, "grass")

        coins_layout = import_csv_layout(level_data["coins"])
        self.coins_tiles = self.__create_tile_group(coins_layout, "coins")

        fg_palms_layout = import_csv_layout(level_data["fg_palms"])
        self.fg_palms_tiles = self.__create_tile_group(
            fg_palms_layout, "palms")

        bg_palms_layout = import_csv_layout(level_data["bg_palms"])
        self.bg_palms_tiles = self.__create_tile_group(
            bg_palms_layout, "palms")

        enemies_layout = import_csv_layout(level_data["enemies"])
        self.enemies_tiles = self.__create_tile_group(
            enemies_layout, "enemies")

        constraints_layout = import_csv_layout(level_data["constraints"])
        self.constraints_tiles = self.__create_tile_group(
            constraints_layout, "constraints")

        level_width = len(terrain_layout[0]) * tile_size

        self.sky = Sky(8)
        self.water = Water(screen_height - 20, level_width)
        self.clouds = Clouds(6, level_width, 30)
        self.dust = pygame.sprite.GroupSingle()
        self.explosions = pygame.sprite.Group()

    def __setup_sounds(self):
        self.coin_sound = pygame.mixer.Sound("./audio/effects/coin.wav")
        self.coin_sound.set_volume(0.05)
        self.stomp_sound = pygame.mixer.Sound("./audio/effects/stomp.wav")
        self.stomp_sound.set_volume(0.05)

    def __update_level_from_player_movement(self):
        player: Player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        if player_x < screen_width * 0.25 and direction_x < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > screen_width * 0.75 and direction_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8

    def __manage_horizontal_collision(self):
        player: Player = self.player.sprite
        player.collision_rect.x += player.direction.x * player.speed

        collidable_sprites = self.terrain_tiles.sprites() + self.crates_tiles.sprites() + self.fg_palms_tiles.sprites()

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.x < 0:
                    player.collision_rect.left = sprite.rect.right
                elif player.direction.x > 0:
                    player.collision_rect.right = sprite.rect.left

    def __manage_vertical_collision(self, player_on_ground):
        player: Player = self.player.sprite
        player.collision_rect.y += player.direction.y

        collidable_sprites = self.terrain_tiles.sprites() + self.crates_tiles.sprites() + self.fg_palms_tiles.sprites()

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.y > 0:
                    player.collision_rect.bottom = sprite.rect.top
                    player.on_ground = True
                    if not player_on_ground:
                        position = player.collision_rect.midbottom
                        if player.facing_right:
                            position -= pygame.math.Vector2(10, 15)
                        else:
                            position -= pygame.math.Vector2(-10, 15)
                        self.__create_particles(position, "character/dust_particles/land")
                elif player.direction.y < 0:
                    player.collision_rect.top = sprite.rect.bottom
                player.direction.y = 0

        if player.on_ground and player.direction.y < 0 or player.direction.y > 0.8:
            player.on_ground = False

    def __create_particles(self, position, path, group=None):
        group = group if group else self.dust
        particles = ParticleEffect(position, path)
        group.add(particles)

    def __on_player_action(self, action, position):
        if action == "jump":
            player: Player = self.player.sprite
            if player.facing_right:
                position -= pygame.math.Vector2(10, 5)
            else:
                position -= pygame.math.Vector2(-10, 5)
            self.__create_particles(position, f"character/dust_particles/{action}")

    def __check_death(self):
        if self.player.sprite.rect.top > screen_height:
            self.create_overworld(self.current_level)

    def __check_win(self):
        if pygame.sprite.spritecollide(self.player.sprite, self.goal, False):
            self.create_overworld(self.current_level, self.new_max_level)

    def __check_coin_collisions(self):
        colliding_coins: List[CoinTile] = pygame.sprite.spritecollide(self.player.sprite, self.coins_tiles, True)
        if colliding_coins:
            for coin in colliding_coins:
                self.coin_sound.play()
                self.change_coins(coin.value)

    def __check_enemy_collisions(self):
        player: Player = self.player.sprite
        colliding_enemies = pygame.sprite.spritecollide(player, self.enemies_tiles, False)
        if colliding_enemies:
            for enemy in colliding_enemies:
                player_bottom = player.rect.bottom
                has_killed = False
                if player.direction.y > 0 and not player.on_ground and enemy.rect.top < player_bottom < enemy.rect.centery:
                    has_killed = True
                    enemy.kill()
                    self.stomp_sound.play()
                    self.__create_particles(enemy.rect.center, "enemy/explosion", group=self.explosions)
                else:
                    player.get_damage(self.change_health)

            if has_killed:
                player.direction.y = -15
