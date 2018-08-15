import sys
import numpy as np
from snake import Snake
import time
from threading import Thread
from random import randrange
import json
from collections import deque
import random
import datetime
import pygame

class Game:
    """Game engine of snake."""

    # colors
    color_tile = 100, 100, 100
    color_background = 0, 0, 0
    # color_point = 255, 0, 0
    color_snake_body = 0, 255, 0

    # const size of map
    size_of_map = 20

    dead_texts = [
        "Your corpse was thrown away!",
        "The garbage truch arrived!",
        "The dogs ate your corpse!",
        "Why did someone created you?"
    ]

    def __init__(self, window_size, title):
        """Initialize game with given size of window."""
        self.size = self.width, self.height = window_size, window_size
        self.size_of_tile = int(window_size/Game.size_of_map)

        self.window = pygame.display.set_mode(self.size)
        pygame.display.set_caption(title)

        with open('maps.json') as f:
            self.maps = json.load(f)
        
        pygame.init()

        # wall sprite
        self.wall = pygame.image.load("wall.png")
        self.wall = pygame.transform.scale(self.wall, (self.size_of_tile, self.size_of_tile))

        # point sprite
        self.point_img = pygame.image.load("point.png")
        self.point_img = pygame.transform.scale(self.point_img, (self.size_of_tile, self.size_of_tile))

        # segment sprite
        self.segment_img = pygame.image.load("segment.png")
        self.segment_img = pygame.transform.scale(self.segment_img, (self.size_of_tile, self.size_of_tile))

        # head sprite
        self.head_img = pygame.image.load("head.png")
        self.head_img = pygame.transform.scale(self.head_img, (self.size_of_tile, self.size_of_tile))


    def start(self):
        """Runs a game."""

        pygame.mixer.music.load("music.mp3")
        pygame.mixer.music.play(loops=-1, start=0.0)

        while True:
            self.choosen_map = self._show_menu()
            # self._show_dead_screen("doubly diagonalized", 15.5)
            # print(self._show_menu.__doc__)

            self.snake = Snake(self.maps[self.choosen_map]["start_position"], Game.size_of_map)

            self.actual_map = np.array(self.maps[self.choosen_map]["map"])
            self.actual_map_state = np.copy(self.actual_map)

            self.map_record = self.maps[self.choosen_map]["record"]

            self.point = None, None
            self._respawn_point()

            self.game_is_running = True

            release_snake_thread = Thread(target=self._release_snake, args=())
            release_snake_thread.start()

            animate_point_thread = Thread(target=self._animate_point, args=())
            animate_point_thread.start()

            self.is_snake_dead = False
            # starts timer
            self.start_timer = datetime.datetime.now()
            
            while self.game_is_running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.snake.die()
                        self.game_is_running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_w:
                            self.snake.direction = Snake.Direction.up
                        elif event.key == pygame.K_s:
                            self.snake.direction = Snake.Direction.down
                        elif event.key == pygame.K_a:
                            self.snake.direction = Snake.Direction.left
                        elif event.key == pygame.K_d:
                            self.snake.direction = Snake.Direction.right
                        elif event.key == pygame.K_q:
                            self.snake.die()
                            self.game_is_running = False

                self.window.fill(Game.color_background)
                self._draw_map()

                pygame.display.flip()

            if self.is_snake_dead:
                # end timer
                end = datetime.datetime.now()
                elapsed = end - self.start_timer
                timed = "{0:.2f}".format(elapsed.seconds+elapsed.microseconds/1000000)
                self._show_dead_screen(self.choosen_map, timed)


    def _draw_map(self):
        """Draws map by logical structure of map."""
        # refresh map
        self.actual_map_state = np.copy(self.actual_map)

        for y, row in enumerate(self.actual_map_state):
            for x, field in enumerate(row):
                # walls
                if field == 1:
                    rect = x*self.size_of_tile, y*self.size_of_tile, self.size_of_tile, self.size_of_tile
                    #pygame.draw.rect(self.window, Game.color_tile, rect)
                    self.window.blit(self.wall, rect)
        
        self._respawn_point()
        
        # point
        rect = self.point[1]*self.size_of_tile, self.point[0]*self.size_of_tile, self.size_of_tile, self.size_of_tile
        self.window.blit(self.point_img, rect)

        # snake body
        for y,x in self.snake.body:
            rect = x*self.size_of_tile, y*self.size_of_tile, self.size_of_tile, self.size_of_tile
            # pygame.draw.rect(self.window, Game.color_snake_body, rect)
            self.window.blit(self.segment_img, rect)
        
        # head
        if len(self.snake.body) > 0:
            rect = self.snake.body[0][1]*self.size_of_tile, self.snake.body[0][0]*self.size_of_tile, self.size_of_tile, self.size_of_tile
            self.window.blit(self.head_img, rect)


    def _release_snake(self):
        """Function used as thread moving snake."""
        while self.game_is_running:
            self.snake.move()
            self.check_collision()
            time.sleep(0.15)

    def _animate_point(self):
        """This funtion makes point texture pretend to be a GIF."""
        # TODO known error "Surfaces must not be locked during blit"
        # Probably occurs when points is textured with some function and
        # at the same time texture is changed here
        
        frames = [
            ("point", 2),
            ("point2", 0.2),
            ("point3", 0.2),
            ("point4", 0.2),
            ("point5", 0.4),
            ("point4", 0.2),
            ("point3", 0.2),
            ("point2", 0.2),
        ]

        while self.game_is_running:
            for name, duration in frames:
                self.point_img = pygame.image.load(name+".png")
                self.point_img = pygame.transform.scale(self.point_img, (self.size_of_tile, self.size_of_tile))
                time.sleep(duration)
                

        

    def _respawn_point(self):
        """Spawns point in random place on map."""
        while self.point == (None, None):
            y,x = randrange(Game.size_of_map), randrange(Game.size_of_map)
            if self.actual_map_state[y][x] == 0:
                self.point = y,x
 

    def check_collision(self):
        """Check collision of snake."""
        y,x = self.snake.body[0]

        # wall collision
        if self.actual_map[self.snake.body[0]] == 1:
            self.snake.die()
            self.game_is_running = False
            self.is_snake_dead = True
            
        # point collision
        elif self.snake.body[0] == self.point:
            self.snake.points = self.snake.points + 1
            self.snake.body.insert(0, self.point)
            self.point = None, None
            self._respawn_point()

        elif len(self.snake.body)>1:
            for i, seg in enumerate(self.snake.body):
                if i == 0:
                    continue
                if y==seg[0] and x==seg[1]:
                    self.snake.die()
                    self.game_is_running = False
                    self.is_snake_dead = True

        
    def _show_menu(self):
        """Shows menu.
        
        Returns name of map used to get appropriate key in dict.
        """
        self.menu_is_running = True        

        title_font = pygame.font.Font("Alkhemikal.ttf", 70)
        title = title_font.render("Horrible", False, (255,255,0))

        menu_font = pygame.font.Font("NeuePixelSans.ttf", 23)
        subtitle = title_font.render("Pytong!", False, (200,200,0))

        help_font = pygame.font.Font("NeuePixelSans.ttf", 15)
        help_text = help_font.render("Press q to exit.", False, (80, 80, 80))

        # 22 is max size of characters in menu option
        # if name of map is bigger, it must be downsized
        options =deque( 
            [
                menu_font.render(option[:21] + (option[21:] and '...'), False, (255,255,255))
                    for option in self.maps.keys()
            ]      
        )

        options_text = deque(self.maps.keys())    
        
        while self.menu_is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    pygame.mixer.music.stop()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        options.rotate(1)
                        options_text.rotate(1)
                    elif event.key == pygame.K_s:
                        options.rotate(-1)
                        options_text.rotate(-1)
                    elif event.key == pygame.K_RETURN:
                        return options_text[0]
                    elif event.key == pygame.K_q:
                        pygame.mixer.music.stop()
                        sys.exit()

            self.window.fill(Game.color_background)
            # self._draw_menu()


            self.window.blit(title, (170, 50))
            self.window.blit(subtitle, (240, 110))

            # tiles
            for y in range(340, 480, 40):
                pygame.draw.rect(self.window, Game.color_tile, (100, y, 400, 40), 3)

            # choose tile
            pygame.draw.rect(self.window, Game.color_snake_body, (100, 300, 400, 40), 5)

            #text in tiles
            for y, option in zip(range(305, 485, 40), options):
                self.window.blit(option, (130, y))

            self.window.blit(help_text, (20, 570))

            pygame.display.flip()  


    def _show_dead_screen(self, map_name, time):
        """Shows this screen when you are dead."""
        self.dead_screen_is_running = True

        title_font = pygame.font.Font("Alkhemikal.ttf", 50)
        title = title_font.render("You are totally dead!", False, (255, 0, 0))

        dead_font = pygame.font.Font("Alkhemikal.ttf", 30)
        dead_text = dead_font.render(random.choice(Game.dead_texts), False, (128, 0, 0))

        help_font = pygame.font.Font("NeuePixelSans.ttf", 15)
        help_text = help_font.render("map_name", False, (80, 80, 80))
        
        help_font = pygame.font.Font("NeuePixelSans.ttf", 15)
        help_text = help_font.render("Press q to exit to menu.", False, (80, 80, 80))

        map_name_font = pygame.font.Font("NeuePixelSans.ttf", 35)
        map_name_text = map_name_font.render(map_name, False, (255, 255, 255))
        
        time_font = pygame.font.Font("NeuePixelSans.ttf", 25)
        time_text = time_font.render("alive: "+str(time) + "s", False, (150, 150, 150))
        points_text = time_font.render("points : "+str(self.snake.points), False, (150, 150, 150))
        record_text = time_font.render("record : "+str(self.map_record), False, (150, 150, 150))

        while self.dead_screen_is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.dead_screen_is_running = False
                    elif event.key == pygame.K_q:
                        self.dead_screen_is_running = False

            self.window.fill(Game.color_background)

            self.window.blit(title, (100, 100))
            self.window.blit(dead_text, (120, 160))

            self.window.blit(map_name_text, (120, 250))

            self.window.blit(time_text, (150, 320))
            self.window.blit(points_text, (150, 350))
            self.window.blit(record_text, (150, 380))

            self.window.blit(help_text, (220, 490))

            pygame.display.flip()

        if self.snake.points > self.map_record:
            self._save_record(map_name)


    def _save_record(self, map_name):
        """Saves snake points as record of map_name map."""
        self.maps[map_name]["record"] = self.snake.points

        with open('maps.json', 'w') as outfile:
            json.dump(self.maps, outfile)
