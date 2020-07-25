import Environment
from pygame.locals import *
import pygame
from pygame import gfxdraw
import numpy as np

import time

class Window(object):
    def __init__(self, grid_size):
        self.grid_size = grid_size
        
        self.y_boundary = None
        self.o_height = 400
        self.o_width = 400
        self.height = 400
        self.width = 400
        
        self.quit_command = False
        
        self.full_grass = (66, 245, 152)
        self.dirt = (212, 206, 186)
        self.highlighted = (204, 255, 229)
        self.red = (168, 50, 78)
        self.gray = (220, 220, 220)
        self.light_gray = (240, 240, 240)
        
        self.click_pos_x = None
        self.click_pos_y = None
        
        self.gap = None
        self.box_size = None
        self.padding_width = None
        self.padding_height = None
        self.hovered_x = None
        self.hovered_y = None
        
        icon = pygame.image.load('icon.jpeg')
        pygame.display.set_icon(icon)
        pygame.init()
        self.canvas = pygame.display.set_mode((self.width,self.height),pygame.RESIZABLE)
        pygame.display.set_caption('Homo Sapianal')
        self.canvas2 = pygame.display.set_mode((self.width,self.height),pygame.RESIZABLE)
        
        self.mouse_pos_x = pygame.mouse.get_pos()[0]
        self.mouse_pos_y = pygame.mouse.get_pos()[1]
        
    def quit(self):
        pygame.quit()
        
    def set_window(self):
        self.y_boundary = self.height #* 9 / 10
            
        if (self.width <= self.y_boundary):
            self.gap = self.width / (11 * self.grid_size + 1)
            self.box_size = 10 * self.gap
        else:
            self.gap = self.y_boundary / (11 * self.grid_size + 1)
            self.box_size = 10 * self.gap
            
        self.padding_width = self.width - self.gap * (self.grid_size + 1) - self.box_size * self.grid_size
        self.padding_height = self.y_boundary - self.gap * (self.grid_size + 1) - self.box_size * self.grid_size
        
    def update_window_layout(self, x, y):
        pass
            
    def handle_event(self):
        update = False
        for event in pygame.event.get():
            if event.type == MOUSEMOTION:
                self.mouse_pos_x = event.pos[0]
                self.mouse_pos_y = event.pos[1]
                update = True
            elif event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                self.update_window_layout(pos[0], pos[1])
                update = True
            elif event.type == pygame.VIDEORESIZE:
                self.width = event.w
                self.height = event.h
                pygame.display.set_mode((self.width,self.height),pygame.RESIZABLE)
                update = True
            elif event.type == QUIT:
                self.quit()
                self.quit_command = True
                break
        return update
                
    def render(self, environment, entities):
        
        self.set_window()
        
        self.hovered_x = (self.mouse_pos_x - self.padding_width / 2) / (self.box_size + self.gap)
        self.hovered_y = (self.mouse_pos_y - self.padding_height / 2) / (self.box_size + self.gap)
        
        self.canvas.fill((255,255,255))
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if int(self.hovered_x) == i and int(self.hovered_y) == j and self.mouse_pos_x > self.padding_width / 2 and self.mouse_pos_y > self.padding_height / 2:
                    color = self.highlighted
                else:
                    if environment[i][j] == 1:
                        color = self.full_grass
                    else:
                        color = self.dirt
                pygame.draw.rect(
                    self.canvas,
                    color,
                    pygame.Rect(
                        self.padding_width / 2 + self. gap * (1 + i) + self.box_size * i, 
                        self.padding_height / 2 + self.gap * (1 + j) + self.box_size * j, 
                        self.box_size,
                        self.box_size)
                )
        
        for i in range(len(entities)):
            x = entities[i].pos_x
            y = entities[i].pos_y
            
            gfxdraw.aacircle(self.canvas, 
                                        int(self.padding_width / 2 + self.gap * (1 + x) + self.box_size * x + self.box_size / 2),
                                        int(self.padding_height / 2 + self.gap * (1 + y) + self.box_size * y + self.box_size / 2),
                                        int(self.box_size / 4),
                                        self.red)
            gfxdraw.filled_circle(self.canvas, 
                                        int(self.padding_width / 2 + self.gap * (1 + x) + self.box_size * x + self.box_size / 2),
                                        int(self.padding_height / 2 + self.gap * (1 + y) + self.box_size * y + self.box_size / 2),
                                        int(self.box_size / 4),
                                        self.red)
                                        
        grid_width = self.gap * (self.grid_size + 1) + self.box_size * self.grid_size
        
        """
        color = self.gray
        pygame.draw.rect(self.canvas, 
                                    color,
                                    pygame.Rect(self.padding_width / 2 + self.gap, 
                                                        grid_width + self.padding_height, 
                                                        grid_width / 3 - self.gap,
                                                        self.height - self.y_boundary - self.gap)
        )

        pygame.draw.rect(self.canvas, 
                                    color,
                                    pygame.Rect(grid_width / 3 + self.padding_width / 2 + self.gap, 
                                                        grid_width + self.padding_height, 
                                                        grid_width / 3 - self.gap,
                                                        self.height - self.y_boundary - self.gap)
        )
        
        pygame.draw.rect(self.canvas, 
                                    color,
                                    pygame.Rect(grid_width / 3 * 2 + self.padding_width / 2 + self.gap, 
                                                        grid_width + self.padding_height, 
                                                        grid_width / 3 - 2 * self.gap,
                                                        self.height - self.y_boundary - self.gap)
        )
        """
            
        pygame.display.flip()



                