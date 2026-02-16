import pygame
class Bullet:
    def __init__(self,x,y,img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    def draw(self,window):
        window.blit(self.img,(self.x,self.y))
    def move(self,speed):
        self.y += speed
    def collison(self,obj):
        # Broad-phase: comprobar colisión por rectángulos primero
        try:
            self_rect = self.img.get_rect(topleft=(int(self.x), int(self.y)))
            obj_rect = obj.ship_img.get_rect(topleft=(int(obj.x), int(obj.y)))
        except Exception:
            # fallback simple
            return False

        if not self_rect.colliderect(obj_rect):
            return False

        # Narrow-phase: colisión por máscaras (pixel-perfect)
        offset_x = obj_rect.x - self_rect.x
        offset_y = obj_rect.y - self_rect.y
        overlap = self.mask.overlap(obj.mask, (offset_x, offset_y))
        return overlap is not None
