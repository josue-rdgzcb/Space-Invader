import pygame
import os
from game import Game
from enemy import Enemy

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
assets_dir = os.path.join(project_root, 'assets')

BACKGROUND = pygame.image.load(os.path.join(assets_dir, 'background.png'))

class Drawing:
    def __init__(self,window):
        self.window = window
        # Escalar el fondo a las dimensiones de la ventana
        self.background_scaled = pygame.transform.scale(BACKGROUND, (window.get_width(), window.get_height()))
    
    def drawing(self,game,player,enemies,fps):
        self.window.blit(self.background_scaled,(0,0))
        for enemy in enemies[:]:
            enemy.draw(self.window)
            # dibujar balas de cada enemigo
            for eb in getattr(enemy, 'fired_bullets', []):
                eb.draw(self.window)
        if player:
            player.draw(self.window)
            # Dibujar balas del jugador
            for bullet in player.fired_bullets:
                bullet.draw(self.window)
            # dibujar indicador de salud del jugador (barra)
            try:
                health_pct = max(0, min(1, player.salud_de_vida / 100))
                bar_w = 200
                bar_h = 10
                x = 20
                y = 120
                pygame.draw.rect(self.window, (80,80,80), (x, y, bar_w, bar_h))
                pygame.draw.rect(self.window, (0,200,0), (x, y, int(bar_w*health_pct), bar_h))
            except Exception:
                pass
        game.drawHud()
        pygame.display.update()