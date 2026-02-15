import pygame
import os
from game import Game
from enemy import Enemy

current_dir = os.path.dirname(os.path.abspath(__file__))
BACKGROUND = pygame.image.load(os.path.join(current_dir, 'assets', 'background.png'))

class Drawing:
    def __init__(self,window):
        self.window = window
        # Escalar el fondo a las dimensiones de la ventana
        self.background_scaled = pygame.transform.scale(BACKGROUND, (window.get_width(), window.get_height()))
    
    def drawing(self,game,player,enemies,fps):
        self.window.blit(self.background_scaled,(0,0))
        for enemy in enemies[:]:
            enemy.draw(self.window)
        if player:
            player.draw(self.window)
            # Dibujar balas del jugador
            for bullet in player.fired_bullets:
                bullet.draw(self.window)
        game.drawHud()
        pygame.display.update()