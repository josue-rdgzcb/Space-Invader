from ship import ShipClass
import pygame
import random
import os

# Obtener el directorio actual del proyecto
current_dir = os.path.dirname(os.path.abspath(__file__))

# Cargar imágenes de enemigos
ENEMY_BLUE_IMAGE = pygame.image.load(os.path.join(current_dir, 'assets', 'enemy_blue_image.png'))
ENEMY_GREEN_IMAGE = pygame.image.load(os.path.join(current_dir, 'assets', 'enemy_green_image.png'))
ENEMY_PURPLE_IMAGE = pygame.image.load(os.path.join(current_dir, 'assets', 'enemy_purple_image.png'))

# Cargar imágenes de disparos
SHOT_BLUE_IMAGE = pygame.image.load(os.path.join(current_dir, 'assets', 'shot_blue.png'))
SHOT_GREEN_IMAGE = pygame.image.load(os.path.join(current_dir, 'assets', 'shot_green.png'))
SHOT_PURPLE_IMAGE = pygame.image.load(os.path.join(current_dir, 'assets', 'shot_purple.png'))


class Enemy(ShipClass):
    COLOR = {'blue':(ENEMY_BLUE_IMAGE,SHOT_BLUE_IMAGE),
             'green':(ENEMY_GREEN_IMAGE,SHOT_GREEN_IMAGE),
             'purple':(ENEMY_PURPLE_IMAGE,SHOT_PURPLE_IMAGE)}
    
    def __init__(self, x=50, y=50, salud_de_vida=100, color = 'blue', speed=1):
        """Enemy con velocidad por defecto baja (bajan poco a poco)."""
        super().__init__(x, y, salud_de_vida)
        self.ship_img, self.bullet_img = self.COLOR[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        # usar nombre 'speed' (antes estaba 'spped')
        self.speed = speed

    def move(self):
        # Mover hacia abajo usando velocidad pequeña para que 'bajen poco a poco'
        self.y += self.speed

    def create(self,amount):
        enemies = []
        for _ in range(amount):
            enemy = Enemy(x=random.randrange(20, 1920-ENEMY_BLUE_IMAGE.get_width()-20),
                          y=random.randrange(50,300),
                          color=random.choice(['blue','green','purple']),
                          speed=random.uniform(0.5, 2.0))
            enemies.append(enemy)
        return enemies


class EnemySpawner:
    """Gestiona spawn por olas y spawn uno-a-uno en posiciones aleatorias."""
    def __init__(self, min_wave=3, max_wave=8, spawn_interval_frames=30, wave_delay_min=120, wave_delay_max=360):
        self.min_wave = min_wave
        self.max_wave = max_wave
        self.spawn_interval = spawn_interval_frames
        self.wave_delay_min = wave_delay_min
        self.wave_delay_max = wave_delay_max

        self.wave_active = False
        self.current_wave_size = 0
        self.spawned_in_wave = 0
        self.spawn_timer = 0
        self.wave_delay = 0

    def start_wave(self):
        self.current_wave_size = random.randint(self.min_wave, self.max_wave)
        self.spawned_in_wave = 0
        self.spawn_timer = 0
        self.wave_active = True

    def update(self, enemies, screen_width=1920):
        """Llamar cada frame. Genera enemigos uno a uno hasta completar la ola.
        - `enemies`: lista donde se agregan instancias de `Enemy`.
        - `screen_width`: usado para calcular x aleatorio.
        """
        # Si estamos en delay entre olas
        if not self.wave_active:
            if self.wave_delay > 0:
                self.wave_delay -= 1
                return
            # iniciar nueva ola
            self.start_wave()
            return

        # Si hay enemigos por generar en la ola
        if self.spawned_in_wave < self.current_wave_size:
            if self.spawn_timer <= 0:
                # posición x aleatoria dentro de los bordes (20 px de margen)
                x = random.randrange(20, int(screen_width - ENEMY_BLUE_IMAGE.get_width() - 20))
                # empezar por encima de la pantalla para que 'entren' lentamente
                y = random.randrange(-200, -40)
                color = random.choice(['blue','green','purple'])
                speed = random.uniform(0.3, 1.5)  # bajan despacio
                enemy = Enemy(x=x, y=y, color=color, speed=speed)
                enemies.append(enemy)
                self.spawned_in_wave += 1
                self.spawn_timer = self.spawn_interval
            else:
                self.spawn_timer -= 1
        else:
            # ola terminada -> poner delay aleatorio antes de la siguiente
            self.wave_active = False
            self.wave_delay = random.randint(self.wave_delay_min, self.wave_delay_max)
    


