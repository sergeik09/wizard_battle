import pygame as pg
import pygame_menu
import os
import random

GESTURE_MODE = False
if GESTURE_MODE:
    from gesture import Gesture
base = os.path.dirname(os.path.realpath(__file__))
print(base)

pg.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 550
CHARACTER_WIDTH = 400
CHARACTER_HEIGHT = 475
FPS = 45

font = pg.font.Font(None, 40)


def load_image(file, width, height):
    image = pg.image.load(file).convert_alpha()
    image = pg.transform.scale(image, (width, height))
    return image


def text_render(text):
    return font.render(str(text), True, "black")

class Menu:
    def __init__(self):
        self.surface = pg.display.set_mode((900, 550))
        font = pygame_menu.font.FONT_MUNRO
        pygame_menu.themes.THEME_BLUE.widget_font = font
        self.menu = pygame_menu.Menu(
            width=900,
            height=550,
            theme=pygame_menu.themes.THEME_BLUE,
            title="Menu"

        )

        self.enemy = None
        self.enemies = ["lightning wizard", "earth monk"]



        self.menu.add.label(title='Singleplayer')



        self.menu.add.selector("Enemy: ",
                               [("Lightning wizard", 1), ("Earth monk", 2), ("Random enemy", 3)],
                               onchange=self.set_enemy)
        self.menu.add.button("Play", lambda: self.start_one_player_game())

        self.menu.add.label(title='Local multiplayer')
        self.menu.add.selector("Left player: ",
                               [("Lightning wizard", 1), ("Earth monk", 2), ("Fire wizard", 3)], onchange=self.set_left_player)
        self.menu.add.selector("Right player: ",
                               [("Lightning wizard", 1), ("Earth monk", 2), ("Fire wizard", 3)], onchange=self.set_right_player)

        self.menu.add.button("Play", lambda: self.start_two_player_game())

        self.menu.add.button("Exit", self.quit_game)

        self.players = ["lightning wizard", "earth monk", "fire wizard"]
        self.left_player = self.players[0]
        self.right_player = self.players[0]


        self.run()


    def run(self):
        self.menu.mainloop(self.surface)


    def quit_game(self):
        pg.quit()
        quit()

    def set_enemy(self, selected, value):
        if value in (1, 2):
            self.enemy = self.enemies[value - 1]
        else:
            self.enemy = random.choice(self.enemies)

    def set_left_player(self, selected, value):
        self.left_player = self.players[value -1]

    def set_right_player(self, selected, value):
        self.right_player = self.players[value -1]

    def start_one_player_game(self):
        Game("one player", [self.left_player])

    def start_two_player_game(self):
        Game("two players", [self.left_player, self.right_player])


class MagicBall(pg.sprite.Sprite):
    def __init__(self, coord, side, power, folder):
        super().__init__()
        self.power = power
        self.side = side
        self.image = load_image(f"images/{folder}/magicball.png", 200, 150)

        if self.side == "right":
            self.image = pg.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect()
        self.rect.center = coord[0], coord[1] + 120

    def update(self):
        self.rect.x += 4 if self.side == "right" else -4
        if self.rect.x >= SCREEN_WIDTH or self.rect.right <= 0:
            self.kill()


class Enemy(pg.sprite.Sprite):
    def __init__(self, folder):
        super().__init__()

        self.folder = folder
        self.load_animations()

        self.image = self.idle_animation_right[0]
        self.current_image = 0
        self.current_animation = self.idle_animation_left

        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2)
        self.hp = 200
        self.timer = pg.time.get_ticks()
        self.interval = 300
        self.side = "left"
        self.animation_mode = True

        self.magic_balls = pg.sprite.Group()

        self.attack_mode = False
        self.attack_interval = 500

        self.move_interval = 800
        self.move_duration = 0
        self.direction = 0
        self.move_timer = pg.time.get_ticks()

        self.charge_power = 0

    def load_animations(self):
        self.idle_animation_right = [load_image(f"images/{self.folder}/idle{i}.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)
                                     for i in range(1, 4)]

        self.idle_animation_left = [pg.transform.flip(image, True, False) for image in self.idle_animation_right]

        self.move_animation_right = [load_image(f"images/{self.folder}/move{i}.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)
                                     for i in range(1, 5)]

        self.move_animation_left = [pg.transform.flip(image, True, False) for image in self.move_animation_right]

        self.attack = [load_image(f"images/{self.folder}/attack.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.attack.append(pg.transform.flip(self.attack[0], True, False))

    def update(self, player):
        self.handle_attack_mode(player)
        self.handle_movement()
        self.handle_animation()


    def handle_attack_mode(self, player):

        if not self.attack_mode:
            attack_probability = 0.5

            if player.charge_mode:
                attack_probability += 2

            if random.randint(1, 100) <= attack_probability:
                self.attack_mode = True
                self.charge_power = random.randint(1, 100)

                if player.rect.centerx < self.rect.centerx:
                    self.side = "left"
                else:
                    self.side = "right"

                self.animation_mode = False
                self.image = self.attack[self.side != "right"]

        if self.attack_mode:
            if pg.time.get_ticks() - self.timer > self.attack_interval:
                self.attack_mode = False
                self.timer = pg.time.get_ticks()

    def handle_movement(self):
        if self.attack_mode:
            return

        now = pg.time.get_ticks()
        if self.rect.right >= SCREEN_WIDTH + 200:
            self.rect.right = SCREEN_WIDTH + 200
        elif self.rect.left<= 0:
            self.rect.left = 0
        if now - self.move_timer < self.move_duration:
            self.animation_mode = True
            self.rect.x += self.direction
            self.current_animation = self.move_animation_left if self.direction == -1 else self.move_animation_right
        else:
            if random.randint(1, 100) == 1 and now - self.move_timer > self.move_interval:
                self.move_timer = pg.time.get_ticks()
                self.move_duration = random.randint(400, 1500)  # случайное число от 400 до 1500
                self.direction = random.choice([-1, 1])
            else:
                self.animtaion_mode = True
                self.current_animation = self.idle_animation_left if self.side == "left" else self.idle_animation_right

    def handle_animation(self):
        # if not self.charge_mode and self.charge_power > 0:
        #     self.attack_mode = True
        #
        # if self.animation_mode and not self.attack_mode:
        #     if pg.time.get_ticks() - self.timer > self.interval:
        #         self.current_image += 1
        #         if self.current_image >= len(self.current_animation):
        #             self.current_image = 0
        #         self.image = self.current_animation[self.current_image]
        #         self.timer = pg.time.get_ticks()

        if self.animation_mode:
            if pg.time.get_ticks() - self.timer > self.interval:
                self.current_image += 1
                if self.current_image >= len(self.current_animation):
                    self.current_image = 0
                self.image = self.current_animation[self.current_image]
                self.timer = pg.time.get_ticks()

        if self.attack_mode and self.charge_power > 0:
            fireball_position = self.rect.topright if self.side == "right" else self.rect.topleft
            self.magic_balls.add(MagicBall(fireball_position, self.side, self.charge_power, self.folder))
            self.charge_power = 0

            self.image = self.attack[self.side != "right"]
            self.timer = pg.time.get_ticks()


class Player(pg.sprite.Sprite):
    def __init__(self, folder='fire wizard', first_player=True):
        super().__init__()
        self.folder = folder
        self.load_animations()

        if first_player:
            self.coord = (100, SCREEN_HEIGHT // 2)
            self.current_animation = self.idle_animation_right
            self.side = 'right'
            self.key_right = pg.K_d
            self.key_left = pg.K_a
            self.key_charge = pg.K_SPACE
            self.key_down = pg.K_s





        else:
            self.coord = (SCREEN_WIDTH  - 100, SCREEN_HEIGHT // 2)
            self.current_animation = self.idle_animation_left
            self.side = 'left'
            self.key_right = pg.K_RIGHT
            self.key_left = pg.K_LEFT
            self.key_charge = pg.K_m
            self.key_down = pg.K_DOWN



        self.current_image = 0

        self.image = self.current_animation[self.current_image]
        self.hp = 200
        self.rect = self.image.get_rect()
        self.rect.center = self.coord

        self.timer = pg.time.get_ticks()
        self.interval = 300
        # self.side = "side"
        self.animation_mode = True

        self.charge_power = 0
        self.charge_indicator = pg.Surface((self.charge_power, 10))
        self.charge_indicator.fill("orange")

        self.charge_mode = False

        self.attack_mode = False
        self.attack_interval = 100
        self.move_timer = pg.time.get_ticks()
        self.magic_balls = pg.sprite.Group()
        self.move_duration = 100


    def load_animations(self):
        self.idle_animation_right = [load_image(f"images/{self.folder}/idle{i}.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)
                                     for i in range(1, 4)]
        self.idle_animation_left = [pg.transform.flip(image, True, False) for image in self.idle_animation_right]

        self.movement_animation_right = [
            load_image(f'images/{self.folder}/move{i}.png', CHARACTER_WIDTH, CHARACTER_HEIGHT)
            for i in range(1, 4)]

        self.movement_animation_left = [pg.transform.flip(image, True, False) for image in
                                        self.movement_animation_right]

        self.charge = [load_image(f"images/{self.folder}/charge.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.charge.append(pg.transform.flip(self.charge[0], True, False))
        self.attack = [load_image(f"images/{self.folder}/attack.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.attack.append(pg.transform.flip(self.attack[0], True, False))
        self.down = [load_image(f"images/{self.folder}/down.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.down.append(pg.transform.flip(self.down[0], True, False))

    def handle_movement(self, direction, keys, gesture):
        keys = pg.key.get_pressed()



        if self.attack_mode:
            return

        if self.rect.right >= SCREEN_WIDTH + 200:
            self.rect.right = SCREEN_WIDTH + 200
        elif self.rect.left<= -100:
            self.rect.left = -100



        if direction != 0:
            self.animation_mode = True
            self.charge_mode = False
            self.rect.x += direction
            self.current_animation = self.movement_animation_left if direction == -1 else self.movement_animation_right

        elif (GESTURE_MODE and gesture == "live long") or (not GESTURE_MODE and keys[self.key_charge]):
            self.animation_mode = False
            self.charge_mode = True
            self.image = self.charge[self.side != "right"]
        elif keys[self.key_down]:
            self.animation_mode = False
            self.charge_mode = False
            self.image = self.down[self.side != "right"]

        else:
            self.animation_mode = True
            self.charge_mode = False

            self.current_animation = self.idle_animation_left if self.side == 'left' else self.idle_animation_right

    def update(self, gesture):

        keys = pg.key.get_pressed()
        direction = 0
        if keys[self.key_left]:
            direction = -1
            self.side = 'left'
        if keys[self.key_right]:
            direction = 1
            self.side = 'right'
        self.handle_attack_mode()
        self.handle_animation()
        self.handle_movement(direction, keys, gesture)

    # def handle_attack_mode(self):
    #     if self.attack_mode:
    #         if pg.time.get_ticks() - self.timer > self.attack_interval:
    #             self.attack_mode = False
    #             self.timer = pg.time.get_ticks()

    def handle_animation(self):
        if not self.charge_mode and self.charge_power > 0:
            self.attack_mode = True

        if self.animation_mode and not self.attack_mode:
            if pg.time.get_ticks() - self.timer > self.interval:
                self.current_image += 1
                if self.current_image >= len(self.current_animation):
                    self.current_image = 0
                self.image = self.current_animation[self.current_image]
                self.timer = pg.time.get_ticks()

        if self.charge_mode:
            self.charge_power += 1
            self.charge_indicator = pg.Surface((self.charge_power, 10))
            self.charge_indicator.fill("orange")
            if self.charge_power == 100:
                self.attack_mode = True

        if self.attack_mode and self.charge_power > 0:
            fireball_position = self.rect.topright if self.side == "right" else self.rect.topleft
            self.magic_balls.add(MagicBall(fireball_position, self.side, self.charge_power, self.folder))
            self.charge_power = 0
            self.charge_mode = False
            self.image = self.attack[self.side != "right"]
            self.timer = pg.time.get_ticks()

    def handle_attack_mode(self):
        if self.attack_mode:
            if pg.time.get_ticks() - self.timer > self.attack_interval:
                self.attack_mode = False
                self.timer = pg.time.get_ticks()


class Game:
    def __init__(self, mode, wizards):


        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Битва магов")

        self.background = load_image("images/background.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        self.foreground = load_image("images/foreground.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        self.player = Player("lightning wizard")

        # self.left_player = Player(left_player, first_player=True)
        #
        #
        # if right_player:
        #     self.right_player = Player(right_player, first_player=False)
        # else:
        #     self.right_player = Enemy(left_player)
        self.gesture = None
        self.mode = mode
        self.win = None
        self.is_running = True
        if self.mode == "one player":
            self.player = Player()
            self.enemy = Enemy(wizards[0])

        elif self.mode == "two players":
            self.player = Player(wizards[0])
            self.enemy = Player(wizards[1], first_player=False)
        if GESTURE_MODE:
            print("загрузка модуля жестов...")
            self.g = Gesture()
            print('загрузка завершена')

            self.GET_GESTURE = pg.USEREVENT + 1
            pg.time.set_timer(self.GET_GESTURE, 1000)

        self.clock = pg.time.Clock()
        self.run()

    def run(self):
        while self.is_running:
            self.event()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()

            if GESTURE_MODE:
                if event.type == self.GET_GESTURE:
                    self.gesture = self.g.get_gesture()


            if event.type == pg.KEYDOWN and self.win is not None:
                self.is_running = False

    def update(self):

        if self.win is None:
            self.player.update(self.gesture)
            self.enemy.update(self.player)
            self.player.magic_balls.update()
            self.enemy.magic_balls.update()
            if self.player.image not in self.player.down:

                hits = pg.sprite.spritecollide(self.player, self.enemy.magic_balls, True, pg.sprite.collide_rect_ratio(0.9))
                for hit in hits:
                    print(hit)
                    self.player.hp -= hit.power
            if self.mode == "one player" or self.enemy.image not in self.enemy.down:
                hits = pg.sprite.spritecollide(self.enemy, self.player.magic_balls, True, pg.sprite.collide_rect_ratio(0.9))
                for hit in hits:
                    print(hit)
                    self.enemy.hp -= hit.power


            if self.player.hp <= 0:
                self.win = self.enemy
            elif self.enemy.hp <= 0:
                self.win = self.player


        # self.player.update(self.gesture)
        #
        #
        # if isinstance(self.right_player, Player):
        #     self.right_player.update(self.gesture)
        # else:
        #     self.right_player.update(self.left_player)
        #
        # self.player.magic_balls.update()
        # self.right_player.magic_balls.update()
        #
        # if isinstance(self.right_player, Player):
        #     hits = pg.sprite.spritecollide(self.left_player, self.right_player.magic_balls, True,
        #                                    pg.sprite.collide_rect_ratio(0.9))
        #     for hit in hits:
        #         self.left_player.hp -= hit.power
        # else:
        #     hits = pg.sprite.spritecollide(self.left_player, self.right_player.magic_balls, True,
        #                                    pg.sprite.collide_rect_ratio(0.9))
        #     for hit in hits:
        #         self.left_player.hp -= hit.power
        #
        # hits = pg.sprite.spritecollide(self.right_player, self.left_player.magic_balls, True,
        #                                pg.sprite.collide_rect_ratio(0.9))
        # for hit in hits:
        #     self.right_player.hp -= hit.power




    def draw(self):

        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.player.image, self.player.rect)
        self.screen.blit(self.enemy.image, self.enemy.rect)
        self.screen.blit(self.foreground, (0, 0))

        if self.player.charge_mode:
            self.screen.blit(self.player.charge_indicator,
                             (self.player.rect.left + 120, self.player.rect.top))

        if self.mode == "two players":
            if self.enemy.charge_mode:
                self.screen.blit(self.enemy.charge_indicator,
                                 (self.enemy.rect.left + 120, self.enemy.rect.top))


        # self.screen.blit(text_render(self.gesture), (0, 0))

        self.player.magic_balls.draw(self.screen)
        self.enemy.magic_balls.draw(self.screen)
        pg.draw.rect(self.screen, pg.Color("green"), (20, 20, self.player.hp, 20))
        pg.draw.rect(self.screen, pg.Color("green"), (SCREEN_WIDTH - 220, 20, self.enemy.hp, 20))
        pg.draw.rect(self.screen, pg.Color("black"), (20, 20, 200, 20), 4)
        pg.draw.rect(self.screen, pg.Color("black"), (SCREEN_WIDTH - 220, 20, 200, 20), 4)

        if self.win == self.player:
            text = text_render("ПОБЕДА")
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text, text_rect)
            text2 = text_render("Маг в левом углу")
            text_rect2 = text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
            self.screen.blit(text2, text_rect2)

        elif self.win == self.enemy:
            text = text_render("ПОБЕДА")
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text, text_rect)
            text2 = text_render("Маг в правом углу")
            text_rect2 = text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
            self.screen.blit(text2, text_rect2)
        pg.display.flip()


if __name__ == "__main__":
    Menu()
