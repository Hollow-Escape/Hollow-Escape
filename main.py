import pygame
import sys

# modules 폴더 로드
from modules.player import Player
from modules.monster import Monster
from modules.MapManager import MapManager, ROOMS, TILE_SIZE
from modules.ui import UI

# -------------------- 설정 --------------------
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

COLOR_BG = (0, 0, 0)
COLOR_WALL = (35, 35, 40)
COLOR_FLOOR = (80, 80, 85)
COLOR_TORCH = (240, 190, 90)
COLOR_DOOR = (120, 70, 40)
COLOR_PATH = (120, 120, 120)
COLOR_SPIKE = (180, 50, 50)
COLOR_SWITCH = (160, 160, 160) # 압력판 색
COLOR_VASE = (170, 120, 80)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Hollow Escape: Plate & Return")
    clock = pygame.time.Clock()

    # 1. 맵 매니저 생성
    map_manager = MapManager(ROOMS)
    
    # 2. 초기 맵 로드 ("HALL")
    start_px, start_py = map_manager.load_room("HALL")

    # 3. 객체 생성
    player = Player(start_px, start_py)
    monster = Monster(speed=90, map_manager=map_manager)
    monster.spawn((52, 32)) 
    ui = UI()

    # -------------------- 보조 함수: 벽 리스트 생성 --------------------
    def get_current_walls():
        walls = []
        for r, row in enumerate(map_manager.map_grid):
            for c, tile in enumerate(row):
                # '#'은 벽이고, 문이 열려 '.'이 되면 벽 리스트에 추가되지 않음
                if tile == "#":
                    rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    walls.append(rect)
        return walls

    # 초기 벽 생성
    walls = get_current_walls()

    # -------------------- 메인 루프 --------------------
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    if player.is_hiding: player.reveal()
                    else: player.hide()

        # -------------------- 1. 플레이어 업데이트 --------------------
        player.update(walls)

        # 플레이어 현재 타일 좌표
        p_tile_x = int(player.rect.centerx / TILE_SIZE)
        p_tile_y = int(player.rect.centery / TILE_SIZE)
        
        # -------------------- 2. 압력판(P) 체크 로직 [NEW] --------------------
        # 현재 서 있는 타일 종류 확인
        current_tile_char, _, _ = map_manager.get_tile_info_at_pixel(player.rect.centerx, player.rect.centery)
        
        if current_tile_char == 'P':
            # 문 열기 시도. True 반환 시 맵이 변경된 것임.
            if map_manager.open_doors_for_plate((p_tile_x, p_tile_y)):
                print("[System] 문이 열렸습니다! 벽 정보를 갱신합니다.")
                # 벽 정보 즉시 갱신 (그래야 플레이어가 지나갈 수 있음)
                walls = get_current_walls()

        # -------------------- 3. 방 전환 체크 로직 [UPDATED] --------------------
        current_room_name = map_manager.current_room
        
        # move_to_room 호출 (last_entrance 로직 포함됨)
        next_room_name, next_tile_x, next_tile_y = map_manager.move_to_room(
            (p_tile_x, p_tile_y), current_room_name
        )

        if next_room_name != current_room_name:
            print(f"[System] 맵 변경: {current_room_name} -> {next_room_name}")
            
            new_px, new_py = map_manager.load_room(next_room_name, tile_pos=(next_tile_x, next_tile_y))
            player.rect.center = (new_px, new_py)
            monster.current_map = next_room_name
            walls = get_current_walls() # 맵 바뀌었으니 벽 갱신

        # -------------------- 4. 몬스터 업데이트 --------------------
        monster.update(player, dt)

        if monster.active and monster.current_map == map_manager.current_room:
            if monster.is_colliding(player):
                print("[System] GAME OVER! 몬스터에게 잡혔습니다.")
                
                # (선택사항) 화면에 GAME OVER 텍스트 띄우기
                # 폰트 설정 (None: 기본 폰트, 크기 100)
                font = pygame.font.SysFont(None, 100)
                # 빨간색 텍스트 생성
                text = font.render("GAME OVER", True, (255, 0, 0))
                # 화면 중앙에 배치
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                
                # 그리기 (배경 위에 덮어쓰기 위해 여기서 그림)
                screen.fill((0, 0, 0)) # 검은 배경
                screen.blit(text, text_rect)
                pygame.display.flip()
                
                # 2초간 대기 후 게임 종료
                pygame.time.delay(2000) 
                running = False

        # -------------------- 5. 카메라 및 그리기 --------------------
        world_w = map_manager.cols * TILE_SIZE
        world_h = map_manager.rows * TILE_SIZE
        
        cam_x = player.rect.centerx - SCREEN_WIDTH // 2
        cam_y = player.rect.centery - SCREEN_HEIGHT // 2

        if world_w > SCREEN_WIDTH: cam_x = max(0, min(cam_x, world_w - SCREEN_WIDTH))
        else: cam_x = -(SCREEN_WIDTH - world_w) // 2

        if world_h > SCREEN_HEIGHT: cam_y = max(0, min(cam_y, world_h - SCREEN_HEIGHT))
        else: cam_y = -(SCREEN_HEIGHT - world_h) // 2

        screen.fill(COLOR_BG)

        for r, row in enumerate(map_manager.map_grid):
            for c, tile in enumerate(row):
                x = c * TILE_SIZE - cam_x
                y = r * TILE_SIZE - cam_y

                if x < -TILE_SIZE or x > SCREEN_WIDTH or y < -TILE_SIZE or y > SCREEN_HEIGHT:
                    continue

                if tile == "#":
                    pygame.draw.rect(screen, COLOR_WALL, (x, y, TILE_SIZE, TILE_SIZE))
                elif tile == "T":
                    pygame.draw.rect(screen, COLOR_WALL, (x, y, TILE_SIZE, TILE_SIZE))
                    pygame.draw.circle(screen, COLOR_TORCH, (x + 16, y + 16), 6)
                elif tile == "R":
                    pygame.draw.rect(screen, COLOR_DOOR, (x, y, TILE_SIZE, TILE_SIZE))
                elif tile == "P": # [NEW] 압력판 그리기
                    pygame.draw.rect(screen, COLOR_SWITCH, (x + 4, y + 4, 24, 24))
                elif tile == "E":
                    pygame.draw.rect(screen, (160, 120, 60), (x, y, TILE_SIZE, TILE_SIZE))
                elif tile == "+":
                    pygame.draw.rect(screen, COLOR_PATH, (x, y, TILE_SIZE, TILE_SIZE))
                elif tile == "V":
                    pygame.draw.circle(screen, COLOR_VASE, (x + 16, y + 16), 10)
                else:
                    pygame.draw.rect(screen, COLOR_FLOOR, (x, y, TILE_SIZE, TILE_SIZE))

        if monster.active and monster.current_map == map_manager.current_room:
            screen.blit(monster.image, (monster.rect.x - cam_x, monster.rect.y - cam_y))

        player.draw(screen, (cam_x, cam_y))
        map_manager.draw_light(screen, player.rect, cam_x, cam_y)

        # ------------------------------------------------------------------
        # [UI 그리기]
        # ------------------------------------------------------------------
        # 1. 고정 HUD (열쇠, INV 버튼)
        ui.draw(screen, 0, 3) # 열쇠 개수는 임시로 0, 3 넣음

        # 2. [NEW] 플레이어 머리 위 스테미나 바 그리기
        # 플레이어 객체와 카메라 좌표(cam_x, cam_y)를 넘겨줍니다.
        ui.draw_stamina_bar(screen, player, cam_x, cam_y)

        # 3. 인벤토리 창 (열려있다면) - 가장 위에 그리기
        # (main.py 상단에 show_inventory 변수 선언이 필요합니다. 없으면 생략 가능)
        # if show_inventory:
        #     ui.draw_inventory(screen, ["Map", "Flashlight"])

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()