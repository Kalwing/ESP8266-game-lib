import sys
sys.path.append("..")
from time import sleep
from lib import Game, OLED, PRG, loop, Truc, \
                afficher_image, afficher_texte, effacer, nb_aleat

class Platformer(Game):
    bonhomme = Truc('perso', 0, 16)
    coeur = Truc('heart', 28, y=22)
    score = 0
    
    def __init__(self):
        effacer()
        
        self.ajouter_au_jeu(self.bonhomme, self.coeur)
        
        super().__init__()

        
    @loop
    def update(self):
        self.bonhomme.aller_a("droite")
        self.coeur.sauter(5, 1)
        
        OLED.line((0, 30), (128, 30))
        OLED.line((0, 32), (128, 30))
        afficher_texte(self.score, 0, 0)
        
        if self.coeur.touche(self.bonhomme):
            self.coeur.aller_a_pos(x=nb_aleat(1,128), y=22)
            self.score += 1    
        sleep(0.1)

            
Platformer()