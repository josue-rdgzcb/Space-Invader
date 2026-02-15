import os
import sys
import pygame
from game import Game
from enemy import Enemy, EnemySpawner
from drawing import Drawing
from player import Player

# Inicializar pygame antes de importar módulos que cargan imágenes al import
pygame.init()

current_dir = os.path.dirname(os.path.abspath(__file__))

# Cargar imagen de bala usando current_dir
BULLET_IMAGE = pygame.image.load(os.path.join(current_dir, 'assets', 'bullet.png'))
PLAYER_IMAGE = pygame.image.load(os.path.join(current_dir, 'assets', 'player_image.png'))



def main():
    screen_w, screen_h = 1920, 1080
    game = Game(screen_width=screen_w, screen_height=screen_h, image=BULLET_IMAGE)
    game.bullets = 3  # mostrar balas en HUD
    
    # Crear instancia de Drawing
    drawer = Drawing(game.window)
    
    # Crear jugador
    player = Player(x=screen_w // 2, y=screen_h - 100, health=100, 
                    ship_img=PLAYER_IMAGE, bullet_img=BULLET_IMAGE)
    
    # Crear spawner de enemigos (olas)
    spawner = EnemySpawner(min_wave=3, max_wave=8, spawn_interval_frames=20)
    enemies = []

    running = True
    while running:
        game.clock.tick(game.fps)
        # eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # actualizar estado
        player.move(screen_h, screen_w)
        # orden: registrar intención de disparo, crear bala si hubo solicitud, luego actualizar cooldowns
        player.fire(game)
        player.create_bullets(game)
        player.cooldown(game)
        player.hit(enemies, game)
        
        # Mover balas del jugador
        for bullet in player.fired_bullets:
            bullet.move(-10)
        
        # actualizar spawner (puede generar uno nuevo por frame)
        spawner.update(enemies, screen_w)

        # mover enemigos existentes
        for e in enemies:
            e.move()
        game.contador += 1

        # dibujar usando la clase Drawing
        drawer.drawing(game, player, enemies, game.fps)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()