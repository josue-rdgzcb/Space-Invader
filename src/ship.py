import pygame

class ShipClass:
    def __init__(self, x, y, salud_de_vida):
        self.x = x
        self.y = y
        self.salud_de_vida = salud_de_vida

        # Imágenes (se asignan externamente según implementación del juego)
        self.ship_img = None
        self.bullet_img = None

        # Contadores y listas para balas / cooldown
        self.bullet_cooldown_counter = 0
        self.bullets = 0
        self.fired_bullets = []
        self.cool_down = 120
    def draw(self,window):
        window.blit(self.ship_img,(self.x,self.y)) #Dibuja la nave en la ventana dada
    def get_width(self):
        return self.ship_img.get_width()
    def get_height(self):
        return self.ship_img.get_height()
    
    