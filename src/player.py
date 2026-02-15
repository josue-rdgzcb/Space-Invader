import pygame
import sys
import os
from ship import ShipClass
from bullet import Bullet
class Player(ShipClass):
    """
    Clase que representa al jugador en el juego.
    Hereda de ShipClass y agrega funcionalidad específica del jugador.
    """
    
    def __init__(self, x, y, health, ship_img, bullet_img):
        """
        Constructor de la clase Player.
        
        Args:
            x (int): Posición horizontal inicial del jugador
            y (int): Posición vertical inicial del jugador
            health (int): Salud/vida del jugador
            ship_img (pygame.Surface): Imagen de la nave del jugador
            bullet_img (pygame.Surface): Imagen de los proyectiles del jugador
        """
        
        # Llamar al constructor de la clase padre (ShipClass)
        # Esto inicializa: x, y, salud_de_vida, ship_img, bullet_img, etc.
        super().__init__(x, y, health)
        
        # Asignar las imágenes pasadas como parámetros
        self.ship_img = ship_img
        self.bullet_img = bullet_img
        
        # Velocidad de desplazamiento del jugador
        self.player_speed = 5  # Píxeles por frame
        
        # Inicializar velocidades de movimiento del jugador usando player_speed
        self.x_speed = self.player_speed  # Velocidad horizontal (positivo = derecha)
        self.y_speed = self.player_speed  # Velocidad vertical (positivo = abajo)
        
        # Crear máscara de colisión basada en la imagen de la nave
        # Esto permite detectar colisiones más precisas (pixel-perfect)
        self.mask = pygame.mask.from_surface(self.ship_img)
        
        # Configuración de proyectiles del jugador
        self.max_bullets = 3  # Máximo de balas activas simultáneamente
        self.bullet_speed = 10  # Velocidad de los proyectiles (píxeles por frame)
        self.fired_bullets = []  # Lista que almacena las balas activas
        
        # Contadores para manejar cooldown y creación de balas
        self.bullet_cooldown_counter = 0  # Contador para el tiempo de espera entre disparos
        self.cool_down = 100  # Frames de espera entre disparos (10 frames = ~167ms a 60 FPS)
        self.creation_cooldown_counter = 0  # Contador auxiliar para creación de proyectiles
        # Flag para indicar que el jugador solicitó disparar (create_bullets hará la creación real)
        self.request_fire = False
        # Powerup: velocidad temporal al matar enemigos rápidamente
        self.kill_times = []  # timestamps (ms) de kills recientes
        self.kills_needed_for_powerup = 2
        self.powerup_kill_window_ms = 4000  # ventana para contar kills (4 segundos)
        self.powerup_active = False
        self.powerup_end_time = 0  # timestamp (ms) cuando expira powerup
        self.powerup_duration_ms = 5000  # duración del powerup (5 segundos)
        self.powerup_speed_bonus = 3  # incremento de velocidad mientras dura el powerup
        # Guardar velocidad base para restaurarla al terminar powerup
        self.base_player_speed = self.player_speed
    def move(self, HEIGHT, WIDTH):
        keys = pygame.key.get_pressed()
        # Movimiento vertical (W/S o flechas arriba/abajo)
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and self.y > 0:
            self.y -= self.y_speed
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and self.y < HEIGHT - self.ship_img.get_height() - 60:
            self.y += self.y_speed
        # Movimiento horizontal (A/D o flechas izquierda/derecha)
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and self.x < WIDTH - self.ship_img.get_width():
            self.x += self.x_speed
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and self.x > 0:
            self.x -= self.x_speed
    def create_bullets(self, game):
        """
        Crea las balas en `self.fired_bullets` cuando `self.request_fire` está activa.
        Además limpia balas que salieron de la pantalla y gestiona la regeneración
        de la munición en el HUD (`game.bullets`) usando `creation_cooldown_counter`.

        Args:
            game: instancia de `Game` que contiene `game.bullets` y la imagen de HUD.
        """
        # Crear bala si el jugador solicitó disparar
        if self.request_fire:
            # Solo crear si aún no excedemos balas activas
            if len(self.fired_bullets) < self.max_bullets:
                bullet_x = self.x + self.ship_img.get_width() // 2 - self.bullet_img.get_width() // 2
                bullet_y = self.y
                bullet = Bullet(bullet_x, bullet_y, self.bullet_img)
                self.fired_bullets.append(bullet)
            # resetear la solicitud (se consumió)
            self.request_fire = False

        # Limpiar balas que salieron de pantalla (y evitar modificar la lista mientras iteramos)
        for bullet in self.fired_bullets[:]:
            if bullet.y <= -40:
                try:
                    self.fired_bullets.remove(bullet)
                except ValueError:
                    pass
    def cooldown(self, game):
        """
        Actualiza los cooldowns:
        - `bullet_cooldown_counter` controla tiempo mínimo entre disparos.
        - `creation_cooldown_counter` regenera balas para el HUD (`game.bullets`) cada `self.cool_down` frames.

        Args:
            game: instancia de `Game` para actualizar `game.bullets` (HUD).
        """
        # Cooldown entre disparos (timing interno de la nave)
        if self.bullet_cooldown_counter >= 20:
            self.bullet_cooldown_counter = 0
        elif self.bullet_cooldown_counter > 0:
            self.bullet_cooldown_counter += 1

        # Regeneración de munición (HUD)
        if self.creation_cooldown_counter > 0:
            # estamos contando para crear/recargar una bala
            self.creation_cooldown_counter += 1
            if self.creation_cooldown_counter >= self.cool_down:
                # sumar una bala al HUD hasta el máximo permitido
                if game.bullets < self.max_bullets:
                    game.bullets += 1
                # si aún no estamos al máximo, reiniciamos el contador para crear la siguiente
                if game.bullets < self.max_bullets:
                    self.creation_cooldown_counter = 1
                else:
                    # ya estamos llenos
                    self.creation_cooldown_counter = 0
        # Verificar expiración del powerup por tiempo
        if self.powerup_active:
            now = pygame.time.get_ticks()
            if now >= self.powerup_end_time:
                # desactivar powerup y restaurar velocidad
                self.powerup_active = False
                self.player_speed = self.base_player_speed
                self.x_speed = self.player_speed
                self.y_speed = self.player_speed
    
    def fire(self, game):
        """
        Lanza una bala si se presiona espacio, hay balas disponibles y no hay cooldown.
        Crea la bala en la posición del jugador.
        
        Args:
            game: Objeto Game que mantiene el contador de balas
        """
        keys = pygame.key.get_pressed()
        
        # Verificar si se presiona espacio, hay balas disponibles en el HUD y no hay cooldown
        if keys[pygame.K_SPACE] and game.bullets > 0 and len(self.fired_bullets) < self.max_bullets and self.bullet_cooldown_counter == 0:
            # Marcar la intención de disparar; la creación real la hace create_bullets(game)
            self.request_fire = True

            # Decrementar contador de balas en el HUD
            game.bullets -= 1

            # Si no hay balas en HUD, iniciar el contador de creación/regeneración
            if game.bullets < self.max_bullets and self.creation_cooldown_counter == 0:
                # iniciar contador para regenerar la siguiente bala
                self.creation_cooldown_counter = 1

            # Iniciar cooldown de disparo
            self.bullet_cooldown_counter = 1
    
    def hit(self, enemies, game):
        """
        Verifica si alguna bala ha impactado con un enemigo y lo destruye.
        
        Args:
            enemies: Lista de enemigos en la pantalla
            game: Objeto Game para acceder al HUD
        """
        for bullet in self.fired_bullets[:]:
            for enemy in enemies[:]:
                # Verificar colisión entre bala y enemigo
                if bullet.collison(enemy):
                    # Remover bala y enemigo
                    if bullet in self.fired_bullets:
                        try:
                            self.fired_bullets.remove(bullet)
                        except ValueError:
                            pass
                    if enemy in enemies:
                        try:
                            enemies.remove(enemy)
                        except ValueError:
                            pass
                    # Registrar kill para el contador del powerup
                    self._record_kill()

    def _record_kill(self):
        """Registrar el timestamp (ms) de una kill y activar powerup si corresponde.

        Condiciones:
        - Se necesitan `kills_needed_for_powerup` dentro de `powerup_kill_window_ms`.
        - No activar si `powerup_active` ya está en True.
        """
        now = pygame.time.get_ticks()
        # Añadir kill
        self.kill_times.append(now)
        # Eliminar kills fuera de la ventana
        window_start = now - self.powerup_kill_window_ms
        self.kill_times = [t for t in self.kill_times if t >= window_start]

        # Si ya está activo, no hacemos nada
        if self.powerup_active:
            return

        # Si alcanzamos el número de kills requerido dentro de la ventana, activar powerup
        if len(self.kill_times) >= self.kills_needed_for_powerup:
            self._activate_powerup(now)

    def _activate_powerup(self, now_ms):
        """Activa el powerup de velocidad por `powerup_duration_ms` starting now_ms."""
        self.powerup_active = True
        self.powerup_end_time = now_ms + self.powerup_duration_ms
        # aumentar velocidad
        self.player_speed = self.base_player_speed + self.powerup_speed_bonus
        self.x_speed = self.player_speed
        self.y_speed = self.player_speed
        # limpiar contador de kills para evitar reactivar inmediatamente
        self.kill_times = []


