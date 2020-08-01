"""
Window Class
"""
import pygame
from pygame import gfxdraw
from params import Params
from color import Color

class Window():
    """
    Window Class
    """
    def __init__(self):
        self.params = Params()
        self.y_boundary = None
        self.o_height = 400
        self.o_width = 400
        self.height = 400
        self.width = 400

        self.quit_command = False

        self.color = Color()

        self.click_pos_x = None
        self.click_pos_y = None

        self.gap = None
        self.box_size = None
        self.padding_width = None
        self.padding_height = None
        self.hovered_x = None
        self.hovered_y = None

        icon = pygame.image.load('data/icon.jpeg')
        pygame.display.set_icon(icon)
        pygame.init()
        self.canvas = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption('Homo Sapianal')
        self.canvas2 = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)

        self.mouse_pos_x = pygame.mouse.get_pos()[0]
        self.mouse_pos_y = pygame.mouse.get_pos()[1]

    def set_window(self):
        """
        Calculates dimensions of the grid squares and gaps to evenly space them out.
        """
        self.y_boundary = self.height * 9 / 10

        if self.width <= self.y_boundary:
            self.gap = self.width / (11 * self.params.grid_size + 1)
            self.box_size = 10 * self.gap
        else:
            self.gap = self.y_boundary / (11 * self.params.grid_size + 1)
            self.box_size = 10 * self.gap

        self.padding_width = self.width - self.gap * (self.params.grid_size + 1) - self.box_size * self.params.grid_size
        self.padding_height = self.y_boundary - self.gap * (self.params.grid_size + 1) - self.box_size * self.params.grid_size

    def click_update(self, pos):
        """
        Determines what square was clicked
        """
        self.click_pos_x = (pos[0] - self.padding_width / 2) / (self.box_size + self.gap)
        self.click_pos_y = (pos[1] - self.padding_height / 2) / (self.box_size + self.gap)

    def handle_event(self):
        """
        Handle events from pygame
        """
        update = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos_x = event.pos[0]
                self.mouse_pos_y = event.pos[1]
                update = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.click_update(pygame.mouse.get_pos())
                update = True
            elif event.type == pygame.VIDEORESIZE:
                self.width = event.w
                self.height = event.h
                pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                update = True
            elif event.type == pygame.QUIT:
                update = False
                self.quit_command = True
                break

        return update

    def render(self, environment, entities):
        """
        Render
        """

        self.set_window()

        self.hovered_x = (self.mouse_pos_x - self.padding_width / 2) / (self.box_size + self.gap)
        self.hovered_y = (self.mouse_pos_y - self.padding_height / 2) / (self.box_size + self.gap)

        self.canvas.fill((255, 255, 255))

        # draw grid
        for i in range(self.params.grid_size):
            for j in range(self.params.grid_size):
                if int(self.hovered_x) == i and int(self.hovered_y) == j and self.mouse_pos_x > self.padding_width / 2 and self.mouse_pos_y > self.padding_height / 2:
                    color = self.color.light_green
                else:
                    if environment[i][j] == 1:
                        color = self.color.green
                    else:
                        color = self.color.brown
                pygame.draw.rect(
                    self.canvas,
                    color,
                    pygame.Rect(
                        self.padding_width / 2 + self. gap * (1 + i) + self.box_size * i,
                        self.padding_height / 2 + self.gap * (1 + j) + self.box_size * j,
                        self.box_size,
                        self.box_size)
                )

        # draw entities as circles
        for entity in enumerate(entities):
            strength = entity[1].strength
            color = (168 - 118 * (1 - strength), 50 + 50 * (1 - strength), 78 + 90 * (1 - strength))

            var_x = entity[1].pos_x
            var_y = entity[1].pos_y

            gfxdraw.aacircle(self.canvas,
                             int(self.padding_width / 2 + self.gap * (1 + var_x) + self.box_size * var_x + self.box_size / 2),
                             int(self.padding_height / 2 + self.gap * (1 + var_y) + self.box_size * var_y + self.box_size / 2),
                             int(self.box_size / 4),
                             color
                            )

            gfxdraw.filled_circle(self.canvas,
                                  int(self.padding_width / 2 + self.gap * (1 + var_x) + self.box_size * var_x + self.box_size / 2),
                                  int(self.padding_height / 2 + self.gap * (1 + var_y) + self.box_size * var_y + self.box_size / 2),
                                  int(self.box_size / 4),
                                  color
                                 )

        grid_width = self.gap * (self.params.grid_size + 1) + self.box_size * self.params.grid_size

        pygame.draw.rect(self.canvas,
                         self.color.gray,
                         pygame.Rect(self.padding_width / 2 + self.gap,
                                     grid_width + self.padding_height,
                                     grid_width / 3 - self.gap,
                                     self.height - self.y_boundary - self.gap)
                        )

        pygame.draw.rect(self.canvas,
                         self.color.gray,
                         pygame.Rect(grid_width / 3 + self.padding_width / 2 + self.gap,
                                     grid_width + self.padding_height,
                                     grid_width / 3 - self.gap,
                                     self.height - self.y_boundary - self.gap)
                        )

        pygame.draw.rect(self.canvas,
                         self.color.gray,
                         pygame.Rect(grid_width / 3 * 2 + self.padding_width / 2 + self.gap,
                                     grid_width + self.padding_height,
                                     grid_width / 3 - 2 * self.gap,
                                     self.height - self.y_boundary - self.gap)
                        )

        pygame.display.flip()

    def close_window(self):
        pygame.quit()
