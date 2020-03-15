from ssd1306_ import SSD1306_I2C
from machine import Pin, I2C, reset
from time import sleep, ticks_us, ticks_diff
from functools import partial
import math
import sys
import urandom
import gc

EXIT = False

i2c = I2C(-1, scl=Pin(5), sda=Pin(4))
WIDTH = 128
HEIGHT = 32
OLED = SSD1306_I2C(WIDTH, HEIGHT, i2c)

PRG = Pin(0, Pin.IN, Pin.PULL_UP)

GAMES_FOLDER = "./GAMES"

START = ticks_us()

def effacer():
    OLED.fill(0)

def afficher_texte(text, x=0, y=0):
    assert x < HEIGHT and y < WIDTH
    OLED.text(str(text), x, y)

def get_array(file):
    with open(GAMES_FOLDER + '/img/' + file) as fin:
        lines = fin.readlines()
    return [list(line.strip()) for line in lines]

def afficher_image(img_file, x=0, y=0, alpha=True):
    array = get_array(img_file)
    OLED.array(array, x, y, alpha)

def lerp(p, a, b):
    return int((p*a) + ((1 - p)*b))

def nb_aleat(a, b):
    now = ticks_us()
    return lerp(math.sin(now) % 1, a, b)

def loop(func):
    def wrap(self, *args):
        while PRG.value():
            OLED.fill(0)
            func(self, *args)
            for obj in self.objects:
                obj.process_all()
                obj.afficher()
            OLED.show()
        OLED.fill(0)
        OLED.show()
        print("Program stopped")

        reset()
    return wrap
        
class Game():
    objects = []

    def __init__(self):
            
        OLED.text(self.__class__.__name__, center_x=True, center_y=True)
        OLED.show()
        print("INITIALIZED")
        sleep(0.5)
        self.update()
    
    def ajouter_au_jeu(self, *args):
        self.objects.extend(args)


# Class object that has a function bounce
class Truc():
    BOUNCE_ID = 0
    N_PROCESS = 1
    
    def __init__(self, img, x=0, y=0, hidden=False):
        self.img = get_array(img)
        self.dim = (len(self.img[0]), len(self.img))
        self.pos = (x, y)
        self.hidden = hidden
        self.name = img
        
        self.processes = [None for process in range(self.N_PROCESS)]
    
    def __repr__(self):
        return self.name + str(self.pos)
    
    def afficher(self):
        if not self.hidden:
            OLED.array(self.img, *self.pos)
    
    def cacher(self):
        self.hidden = True
    
    def montrer(self):
        self.hidden = False
        
    def aller_a_pos(self, x, y):
        self.pos = (x, y)
        
    def aller_a(self, direction, pas=5):
        if direction == 'haut':
            self.pos = (self.pos[0], self.pos[1] - pas)
        elif direction == 'bas':
            self.pos = (self.pos[0], self.pos[1] + pas)
        elif direction == 'gauche':
            self.pos = (self.pos[0] - pas, self.pos[1])
        elif direction == 'droite':
            self.pos = (self.pos[0] + pas, self.pos[1])
    
    def get_box(self):
        width, height = self.dim
        x, y = self.pos
        x_bounds = x, x + width
        y_bounds = y, y + height
        return x_bounds, y_bounds
    
    def touche(self, other):
        x_bounds, y_bounds = self.get_box()
        x_b_other, y_b_other = other.get_box()
        
        c1 = (x_bounds[0] <= x_b_other[0] <= x_bounds[1] or 
              x_bounds[0] <= x_b_other[1] <= x_bounds[1])
        c1 = c1 and (y_bounds[0] <= y_b_other[0] <= y_bounds[1] or 
             y_bounds[0] <= y_b_other[1] <= y_bounds[1])
        if c1: return c1 # An edge of other is inside of self
        c2 = (x_b_other[0] <= x_bounds[0] <= x_b_other[1] or
              x_b_other[0] <= x_bounds[1] <= x_b_other[1])
        c2 = c2 and (y_b_other[0] <= y_bounds[0] <= y_b_other[1] or 
             y_b_other[0] <= y_bounds[1] <= y_b_other[1])
        return c2 # if c2, an edge of self is inside other

    def _bounce(self, length, speed):
        _, y = self.pos
        base_y = y
        final_y = base_y - length
        while y > final_y:
            x, _ = self.pos
            y -= speed
            y = max(final_y, y)
            self.pos = (x, y)
            yield None
        while y < base_y:
            x, _ = self.pos
            y += speed
            y = min(base_y, y)
            self.pos = (x, y)
            yield None
            
    def sauter(self, length, speed):
        if self.processes[self.BOUNCE_ID] is None:
            self.processes[self.BOUNCE_ID] = self._bounce(length, speed)
    
    def process_all(self):
        for pid, process in enumerate(self.processes):
            if process is not None:
                try:
                    next(process)
                except StopIteration:
                    self.processes[pid] = None