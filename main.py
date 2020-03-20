from machine import Pin, I2C
from time import sleep
import sys
import uos
from ssd1306_ import FONT_HEIGHT
from lib import OLED, GAMES_FOLDER, PRG
from CONFIG import TESTING

class Menu():
    def __init__(self, splash=True, filename=None):
        if splash:
            OLED.text('Les Francas', center_x=True)
            OLED.text('Kalwing - 2020', y=23, center_x=True)
            OLED.show()
            sleep(0.75)
        if not filename:
            games = [d[0] for d in uos.ilistdir(GAMES_FOLDER) if d[1]==0x8000]
            filename = self.menu(games)
        
        # Opening the game
        with open(GAMES_FOLDER + '/' + filename) as fin:
            program = ''.join(fin.readlines())
        OLED.fill(0)
        exec(program)

    
    def quit(self):
        sys.exit()
        
    def menu(self, choice_list):
        OLED.fill(0)
        INDENT = 12

        choice_id = -1
        while PRG.value():
            choice_id += 1
            if choice_id >= len(choice_list):
                choice_id = 0

            OLED.fill(0)
            for y, choice in zip(range(len(choice_list)), choice_list):
                    OLED.text(str(choice), INDENT, y*FONT_HEIGHT)
            OLED.disk(0, choice_id*FONT_HEIGHT + 1, 3)

            OLED.show()
            sleep(1)
        return choice_list[choice_id]

def afficher(text, x=0, y=0):
    OLED.fill(0)
    OLED.text(str(text), x, y)
    OLED.show()

OLED.contrast(0x15)
print("-------------------------")
print("-------------------------")
g = Menu(filename='exit', splash=False) if TESTING else Menu()