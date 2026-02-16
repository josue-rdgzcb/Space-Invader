from ship import ShipClass
import pygame
import random
import os

# Obtener el directorio actual del proyecto
current_dir = os.path.dirname(os.path.abspath(__file__))
# Usar la carpeta `assets` situada en la raíz del proyecto (una carpeta arriba de `src`)
project_root = os.path.abspath(os.path.join(current_dir, '..'))
assets_dir = os.path.join(project_root, 'assets')

# Función segura para cargar imágenes (no usa convert/convert_alpha si la display no está lista)
def _safe_load_enemy_image(name, size=None):
    path = os.path.join(assets_dir, name)
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path):
        print(f"[ERROR] enemy image not found: {abs_path}")
        s = pygame.Surface(size if size else (50,50), pygame.SRCALPHA)
        s.fill((255,0,255,255))
        return s
    try:
        img = pygame.image.load(abs_path)
        # Solo convertir si la display está inicializada
        if pygame.display.get_init() and pygame.display.get_surface() is not None:
            try:
                img = img.convert_alpha()
            except Exception:
                img = img.convert()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception as e:
        print(f"[ERROR] failed to load enemy image {abs_path}: {e}")
        s = pygame.Surface(size if size else (50,50), pygame.SRCALPHA)
        s.fill((255,0,255,255))
        return s

# Cargar imágenes de enemigos usando la función segura
ENEMY_TIE_IMAGE = _safe_load_enemy_image('enemy_tie.png', size=(128,128))
ENEMY_BLUE_IMAGE = ENEMY_GREEN_IMAGE = ENEMY_PURPLE_IMAGE = ENEMY_TIE_IMAGE

# Cargar imagen de disparo enemiga preferida: laser_enemy.png
_enemy_shot = None
# asegurarse que las balas enemigas tengan el mismo tamaño que las del jugador
enemy_bullet_size = (16, 32)
for name in ('laser_enemy.png','laser_enemy.jpg','laser_enemy.jpeg','shot_blue.png'):
    path = os.path.join(assets_dir, name)
    if os.path.exists(path):
        _enemy_shot = _safe_load_enemy_image(name, size=enemy_bullet_size)
        break
if _enemy_shot is None:
    _enemy_shot = _safe_load_enemy_image('shot_blue.png', size=enemy_bullet_size)

SHOT_BLUE_IMAGE = SHOT_GREEN_IMAGE = SHOT_PURPLE_IMAGE = _enemy_shot


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
        # Gestión de disparos del enemigo
        self.fired_bullets = []
        # aumentar frecuencia: cooldown más bajo (20-80 frames) y probabilidad mayor
        self.shoot_cooldown = random.randint(20, 80)  # tiempo en frames entre intentos de disparo
        self.shoot_timer = 0

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

    def update_shots(self, game, player, enemies_list):
        """Actualizar balas del enemigo, moverlas y chequear colisiones con el jugador."""
        # Disparar de vez en cuando
        if self.shoot_timer <= 0:
            # evitar disparar cuando fuera de pantalla
            if 0 < self.y < game.screen_height:
                # probabilidad de disparo aumentada
                if random.random() < 0.12:
                    self.make_shot()
            # reiniciar temporizador con pequeño rango
            self.shoot_timer = self.shoot_cooldown
        else:
            self.shoot_timer -= 1

        # Mover balas
        for b in self.fired_bullets[:]:
            b.move(5)  # balas de enemigos van hacia abajo
            # colisión con el jugador
            if player and b.collison(player):
                try:
                    self.fired_bullets.remove(b)
                except ValueError:
                    pass
                # afectar vida del jugador
                try:
                    player.salud_de_vida -= 10
                except Exception:
                    pass
            # eliminar si sale de pantalla
            if b.y > game.screen_height + 50:
                try:
                    self.fired_bullets.remove(b)
                except ValueError:
                    pass

    def make_shot(self):
        # Asegurarse que la imagen de la bala tenga el tamaño deseado
        try:
            bullet_surf = pygame.transform.scale(self.bullet_img, enemy_bullet_size)
        except Exception:
            bullet_surf = self.bullet_img
        # colocar la bala en la base del enemigo (centro horizontal, ligeramente por debajo del sprite)
        bx = int(self.x + self.ship_img.get_width() // 2 - bullet_surf.get_width() // 2)
        by = int(self.y + self.ship_img.get_height() - bullet_surf.get_height() // 2)
        from bullet import Bullet
        b = Bullet(bx, by, bullet_surf)
        self.fired_bullets.append(b)


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



