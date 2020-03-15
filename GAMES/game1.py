import sys
sys.path.append("..")
from lib import Game, OLED, afficher_image, PRG

OLED.fill(0)
afficher_image('skull', 54,10)
OLED.show()