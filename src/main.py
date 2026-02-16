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
# Asumir que la carpeta `assets` está en la raíz del proyecto (una carpeta arriba de `src`)
project_root = os.path.abspath(os.path.join(current_dir, '..'))
assets_dir = os.path.join(project_root, 'assets')

# Cargar imágenes de forma segura y optimizada
def _safe_load_image(path, size=None):
    # diagnóstico: comprobar existencia del archivo antes de intentar cargar
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path):
        print(f"[ERROR] image file not found: {abs_path}")
        s = pygame.Surface(size if size else (50, 50), pygame.SRCALPHA)
        s.fill((255, 0, 255, 255))
        return s
    try:
        img = pygame.image.load(abs_path)
        # Only convert if display initialized (avoid errors when loading before set_mode)
        if pygame.display.get_init() and pygame.display.get_surface() is not None:
            try:
                img = img.convert_alpha()
            except Exception:
                img = img.convert()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception as e:
        # imprimir excepción para diagnóstico
        print(f"[ERROR] failed to load image {abs_path}: {e}")
        s = pygame.Surface(size if size else (50, 50), pygame.SRCALPHA)
        s.fill((255, 0, 255, 255))
        return s

# Cargar y escalar a tamaños razonables para la pantalla
# Usar el sprite de disparo del player (laser). Intentar .png/.jpg automáticamente
bullet_candidate_names = ['laser_player.png', 'laser_player.jpg', 'laser_player.jpeg', 'bullet.png']
_bullet_img = None
# aumentar tamaño ligeramente: 16x32
bullet_size = (16, 32)
for name in bullet_candidate_names:
    path = os.path.join(assets_dir, name)
    if os.path.exists(path):
        _bullet_img = _safe_load_image(path, size=bullet_size)
        break
if _bullet_img is None:
    _bullet_img = _safe_load_image(os.path.join(assets_dir, 'bullet.png'), size=bullet_size)
BULLET_IMAGE = _bullet_img
# Nota: no cargamos 'player_image.png' aquí para permitir elegir la nave en la pantalla de selección.
PLAYER_IMAGE = None

def show_loading(window):
    """Muestra una pantalla de carga usando loading.png o loading.jpg en assets.
    Dibuja el texto 'LOADING...' en blanco en la esquina inferior derecha con antialias=False
    para un estilo más 'pixel' y espera ~1.2s.
    """
    # intentar varios nombres de archivo comunes
    for name in ("loading.png", "loading.jpg", "loading.jpeg"):
        path = os.path.join(assets_dir, name)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path)
                if pygame.display.get_init() and pygame.display.get_surface() is not None:
                    try:
                        img = img.convert_alpha()
                    except Exception:
                        img = img.convert()
                img = pygame.transform.scale(img, (window.get_width(), window.get_height()))
                window.blit(img, (0, 0))
                # fuente tipo monoespacio para aspecto 'pixel' y sin antialias
                try:
                    # aumentar tamaño para mejor legibilidad
                    font = pygame.font.SysFont('couriernew', 36)
                except Exception:
                    font = pygame.font.Font(None, 24)
                text_surf = font.render('LOADING...', False, (255, 255, 255))
                tw, th = text_surf.get_size()
                padding = 18
                x = window.get_width() - tw - padding
                y = window.get_height() - th - padding
                window.blit(text_surf, (x, y))
                pygame.display.update()
                pygame.time.delay(3200)
            except Exception as e:
                print(f"[ERROR] show_loading failed: {e}")
            return
    # si no existe la imagen, dibujar fondo negro con texto
    try:
        window.fill((0, 0, 0))
        try:
            font = pygame.font.SysFont('couriernew', 36)
        except Exception:
            font = pygame.font.Font(None, 24)
        text_surf = font.render('LOADING...', False, (255, 255, 255))
        tw, th = text_surf.get_size()
        padding = 18
        x = window.get_width() - tw - padding
        y = window.get_height() - th - padding
        window.blit(text_surf, (x, y))
        pygame.display.update()
        pygame.time.delay(3200)
    except Exception as e:
        print(f"[ERROR] show_loading fallback failed: {e}")

def _load_choose_background(window):
    # intenta space_choose.png o .jpg
    for name in ("space_choose.png", "space_choose.jpg", "space_choose.jpeg"):
        path = os.path.join(assets_dir, name)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path)
                if pygame.display.get_init() and pygame.display.get_surface() is not None:
                    try:
                        img = img.convert_alpha()
                    except Exception:
                        img = img.convert()
                return pygame.transform.scale(img, (window.get_width(), window.get_height()))
            except Exception:
                break
    return None

def show_player_select(window):
    """Muestra una pantalla para elegir entre falcon.png y x_wing.png.
    Controles: teclas Izquierda/Derecha y Enter para confirmar, o clic en la imagen.
    Devuelve la Surface seleccionada (escalada a 128x128).
    """
    # cargar miniaturas
    size = (240, 240)
    falcon = _safe_load_image(os.path.join(assets_dir, 'falcon.png'), size=size)
    xwing = _safe_load_image(os.path.join(assets_dir, 'x_wing.png'), size=size)

    sel = 0  # 0 = falcon, 1 = xwing
    clock = pygame.time.Clock()
    font = None
    try:
        font = pygame.font.SysFont('couriernew', 20)
    except Exception:
        font = pygame.font.Font(None, 20)

    while True:
        clock.tick(30)
        # dibujar fondo de selección si existe
        bg = _load_choose_background(window)
        if bg is not None:
            window.blit(bg, (0,0))
        else:
            window.fill((10, 10, 30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    sel = 0
                elif event.key == pygame.K_RIGHT:
                    sel = 1
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    # devolver la imagen final escalada a 128x128 para usar en el juego
                    final_size = (128, 128)
                    return pygame.transform.scale(falcon if sel == 0 else xwing, final_size)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                w, h = window.get_size()
                # left image rect
                left_rect = pygame.Rect(w // 4 - size[0] // 2, h // 2 - size[1] // 2, size[0], size[1])
                right_rect = pygame.Rect(3 * w // 4 - size[0] // 2, h // 2 - size[1] // 2, size[0], size[1])
                if left_rect.collidepoint(mx, my):
                    return pygame.transform.scale(falcon, (128, 128))
                if right_rect.collidepoint(mx, my):
                    return pygame.transform.scale(xwing, (128, 128))

        # dibujar miniaturas y UI
        w, h = window.get_size()
        left_pos = (w // 4 - size[0] // 2, h // 2 - size[1] // 2)
        right_pos = (3 * w // 4 - size[0] // 2, h // 2 - size[1] // 2)
        window.blit(falcon, left_pos)
        window.blit(xwing, right_pos)

        # highlight selection
        sel_rect = pygame.Rect((left_pos if sel == 0 else right_pos)[0] - 6, (left_pos if sel == 0 else right_pos)[1] - 6, size[0] + 12, size[1] + 12)
        pygame.draw.rect(window, (255, 255, 0), sel_rect, 4)

        # labels
        label = font.render('Choose your ship: ←  →  Enter / Click', False, (255, 255, 255))
        lw, lh = label.get_size()
        window.blit(label, (w // 2 - lw // 2, h - lh - 20))

        # names
        name_l = font.render('Falcon', False, (200, 200, 200))
        name_r = font.render('X-Wing', False, (200, 200, 200))
        window.blit(name_l, (left_pos[0] + size[0] // 2 - name_l.get_width() // 2, left_pos[1] + size[1] + 8))
        window.blit(name_r, (right_pos[0] + size[0] // 2 - name_r.get_width() // 2, right_pos[1] + size[1] + 8))

        pygame.display.update()

# Cargar y escalar a tamaños razonables para la pantalla
# Usar el sprite de disparo del player (laser). Intentar .png/.jpg automáticamente
bullet_candidate_names = ['laser_player.png', 'laser_player.jpg', 'laser_player.jpeg', 'bullet.png']
_bullet_img = None
# aumentar tamaño ligeramente: 16x32
bullet_size = (16, 32)
for name in bullet_candidate_names:
    path = os.path.join(assets_dir, name)
    if os.path.exists(path):
        _bullet_img = _safe_load_image(path, size=bullet_size)
        break
if _bullet_img is None:
    _bullet_img = _safe_load_image(os.path.join(assets_dir, 'bullet.png'), size=bullet_size)
BULLET_IMAGE = _bullet_img
# Nota: no cargamos 'player_image.png' aquí para permitir elegir la nave en la pantalla de selección.
PLAYER_IMAGE = None

def main():
    # Tamaño de ventana más razonable por defecto para evitar problemas en pantallas pequeñas
    screen_w, screen_h = 1280, 720
    game = Game(screen_width=screen_w, screen_height=screen_h, image=BULLET_IMAGE)
    # Mostrar pantalla de carga antes de inicializar elementos del juego
    show_loading(game.window)
    # Mostrar pantalla de selección de nave y obtener la imagen seleccionada (escalada a 128x128)
    selected_ship = show_player_select(game.window)
    game.bullets = 3  # mostrar balas en HUD
    
    # Crear instancia de Drawing
    drawer = Drawing(game.window)
    
    # Crear jugador
    # Centrar la nave horizontalmente usando el ancho real de la imagen
    player_start_x = screen_w // 2 - selected_ship.get_width() // 2
    player_start_y = screen_h - 100
    player = Player(x=player_start_x, y=player_start_y, health=100, 
                    ship_img=selected_ship, bullet_img=BULLET_IMAGE)
    
    # debug: confirmar tamaño de la nave seleccionada y del sprite de bala
    try:
        print(f"Selected ship size={selected_ship.get_size()}, BULLET_IMAGE size={BULLET_IMAGE.get_size()}")
    except Exception:
        print("Selected ship or bullet image not available")

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
            elif event.type == pygame.KEYDOWN:
                # Disparar con espacio (asegurar que la intención de disparo se registre también vía eventos)
                if event.key == pygame.K_SPACE:
                    # marcar intención de disparo; create_bullets la consumirá en el mismo frame
                    player.request_fire = True

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
            # cada enemigo actualiza sus disparos hacia el jugador
            try:
                e.update_shots(game, player, enemies)
            except Exception:
                pass
        game.contador += 1

        # comprobar colisión jugador <-> enemigo (contacto cuerpo a cuerpo)
        for enemy in enemies[:]:
            try:
                offset = (int(enemy.x - player.x), int(enemy.y - player.y))
                if player.mask.overlap(enemy.mask, (offset[0], offset[1])):
                    try:
                        enemies.remove(enemy)
                    except ValueError:
                        pass
                    # daño por colisión: restar salud del jugador
                    player.salud_de_vida -= 30
                    if player.salud_de_vida <= 0:
                        game.lives -= 1
                        player.salud_de_vida = 100
            except Exception:
                pass

        # dibujar usando la clase Drawing
        drawer.drawing(game, player, enemies, game.fps)

    pygame.quit()
    sys.exit()

if __name__ == "__main__": 
    main()

