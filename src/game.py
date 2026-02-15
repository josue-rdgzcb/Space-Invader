import pygame
import os

class Game:
    def __init__(self, screen_width: int = 800, screen_height: int = 600, fps: int = 60, lives: int = 3, nivel: int = 1, font_size: int = 36, caption: str = "Space Invader",image=None):

        # Dimensiones y ventana
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Gameplay
        self.fps = fps
        self.lives = lives
        self.nivel = nivel

        # Estado dinámico
        self.bullets = 0
        self.contador = 0  # contador de frames

        #Imagen
        self.bullets_image = image

        # Reloj
        self.clock = pygame.time.Clock()

        # Inicializar/crear ventana
        # Asumimos que el llamador ya hizo pygame.init() cuando corresponda; de todos modos
        # creamos la surface de display aquí para tener el atributo Window.
        self.window = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption(caption)

        # Fuente: intentamos inicializar la fuente; si falla dejamos None
        try:
            # Asegurar que el módulo de fuentes está inicializado
            if not pygame.font.get_init():
                pygame.font.init()
            self.font = pygame.font.Font(None, font_size)
        except Exception:
            self.font = None

    def escape(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            else:
                return False
    def over(self):
        if self.lives <= 0:
            self.contador = 0
            while True:
                self.clock.tick(self.fps)
                gameover_label = self.font.render('GAME OVER',1,(255,255,255))
                self.window.blit(gameover_label,(self.screen_width-gameover_label.get_width()/2),(self.screen_height-gameover_label.get_height()/2))
                pygame.display.update()
                self.contador += 1
                if self.contador == self.fps*3:
                    break
            return True
        else:
            return False
    def reload_bullet(self,bullet):
        self.bullets = bullet

    def drawHud(self):
        offset = 0
        """Dibuja el HUD (Heads-Up Display) con vidas, balas y nivel"""
        if self.font is None:
            return  # Si la fuente no está disponible, no dibujamos nada
        
        # Label de vidas
        lives_label = self.font.render(f'Vidas: {self.lives}', True, (255, 255, 255))
        self.window.blit(lives_label, (10, 10))
        
        # Label de nivel
        level_label = self.font.render(f'Nivel: {self.nivel}', True, (255, 255, 255))
        self.window.blit(level_label, (10, 90))
        
        # Label de tiempo de juego (en frames)
        tiempo_segundos = self.contador // self.fps
        tiempo_label = self.font.render(f'Tiempo: {tiempo_segundos}s', True, (255, 255, 255))
        self.window.blit(tiempo_label, (self.screen_width - 200, 10))

        for i in range(self.bullets):
            offset += self.bullets_image.get_width()
            self.window.blit(self.bullets_image,(self.screen_width-offset,self.screen_height-50))

