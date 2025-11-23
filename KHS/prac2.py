import pygame
import sys

pygame.init()

# -------------------- 기본 설정 --------------------
TILE_SIZE = 64  # 한 타일의 픽셀 크기

# 맵 데이터 (이미지 구조를 본뜬 ASCII 타일맵)
# 21칸 x 13줄 정도의 세로형 맵입니다.
MAP_DATA = [
    "#####################",  # 0  바깥 벽
    "#...................#",  # 1  위쪽 통로
    "#..######...........#",  # 2  위 중앙에 문(D)이 있는 작은 방
    "#..#....#...........#",  # 3
    "#..#T...D...........#",  # 4  왼쪽 위 벽 안쪽에 횃불(T)
    "#..######...........#",  # 5
    "#...........######..#",  # 6  중앙 오른쪽 벽
    "#....P......#SSS#...#",  # 7  중앙 왼쪽 압력판(P), 오른쪽 가시(S) 3개
    "#...........#SS.#...#",  # 8  그 아래 가시 2개
    "#...........######..#",  # 9
    "#..........V.....V..#",  #10 오른쪽 아래 항아리(V) 2개
    "#...................#",  #11 아래쪽 통로
    "#####################",  #12 바깥 벽
]

ROWS = len(MAP_DATA)
COLS = len(MAP_DATA[0])

# ★ 문자열 리스트를 "문자 2차원 배열"로 변환해서 수정 가능하게 만듦
map_grid = [list(row) for row in MAP_DATA]

WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hollow-Escape - Room Prototype")

clock = pygame.time.Clock()

# -------------------- 색 설정 (임시) --------------------
COLOR_BG = (0, 0, 0)
COLOR_WALL = (35, 35, 40)
COLOR_FLOOR = (80, 80, 85)
COLOR_TORCH = (240, 190, 90)
COLOR_DOOR = (120, 70, 40)
COLOR_SWITCH = (160, 160, 160)
COLOR_SPIKE = (180, 50, 50)
COLOR_VASE = (170, 120, 80)
COLOR_PLAYER = (200, 220, 255)

# -------------------- 플레이어 설정 --------------------
# 맵에서 (col, row) 위치를 눈으로 보고 골라서 시작 위치를 잡습니다.
start_col = 2
start_row = 10

player_pos = [
    start_col * TILE_SIZE + TILE_SIZE // 2,
    start_row * TILE_SIZE + TILE_SIZE // 2,
]
player_speed = 4

# 압력판을 이미 밟았는지 여부 (한 번만 발동되게 하고 싶으면 사용)
pressure_activated = False


# -------------------- 유틸 함수 --------------------
def get_tile_info_at_pixel(px, py):
    """화면 좌표(px, py)가 맵의 (타일 문자, col, row)를 반환"""
    col = px // TILE_SIZE
    row = py // TILE_SIZE
    if 0 <= row < ROWS and 0 <= col < COLS:
        return map_grid[row][col], col, row
    return "#", col, row  # 맵 밖은 벽 취급


# -------------------- 문 열기 / 상호작용 --------------------
def open_doors():
    """맵 전체에서 'D'(닫힌 문)를 찾아서 '.'(바닥)로 바꿔 문을 엽니다."""
    for r in range(ROWS):
        for c in range(COLS):
            if map_grid[r][c] == "D":
                map_grid[r][c] = "."  # 이제 그냥 바닥이 됨 (통과 가능)


def interact_with_tile(tile, col, row):
    """플레이어가 밟은 타일에 따른 상호작용 처리"""
    global pressure_activated

    # 압력판을 밟았을 때 문 열기
    if tile == "P" and not pressure_activated:
        print("압력판 밟음 → 문이 열립니다!")
        pressure_activated = True
        open_doors()
        # 압력판 그림도 눌린 상태로 바꾸고 싶으면:
        # map_grid[row][col] = '.'  # 더 이상 P로 표시하지 않기


# -------------------- 그리기 함수 --------------------
def draw_map(surface):
    """map_grid를 읽어서 타일을 모두 그립니다."""
    for row_idx, row in enumerate(map_grid):
        for col_idx, cell in enumerate(row):
            x = col_idx * TILE_SIZE
            y = row_idx * TILE_SIZE

            # 바닥 먼저
            pygame.draw.rect(surface, COLOR_FLOOR, (x, y, TILE_SIZE, TILE_SIZE))

            # 각 기호에 따라 다른 오브젝트를 그립니다.
            if cell == "#":  # 벽
                pygame.draw.rect(surface, COLOR_WALL, (x, y, TILE_SIZE, TILE_SIZE))

            elif cell == "T":  # 횃불
                pygame.draw.rect(surface, COLOR_WALL, (x, y, TILE_SIZE, TILE_SIZE))
                pygame.draw.circle(
                    surface,
                    COLOR_TORCH,
                    (x + TILE_SIZE // 2, y + TILE_SIZE // 2),
                    TILE_SIZE // 5,
                )

            elif cell == "D":  # 닫힌 문
                door_rect = (
                    x + TILE_SIZE // 4,
                    y + TILE_SIZE // 4,
                    TILE_SIZE // 2,
                    TILE_SIZE // 2,
                )
                pygame.draw.rect(surface, COLOR_DOOR, door_rect)

            elif cell == "P":  # 압력판 / 스위치
                switch_rect = (
                    x + TILE_SIZE // 4,
                    y + TILE_SIZE // 4,
                    TILE_SIZE // 2,
                    TILE_SIZE // 2,
                )
                pygame.draw.rect(surface, COLOR_SWITCH, switch_rect)

            elif cell == "S":  # 가시
                p1 = (x + TILE_SIZE // 2, y + TILE_SIZE // 4)
                p2 = (x + TILE_SIZE // 4, y + TILE_SIZE * 3 // 4)
                p3 = (x + TILE_SIZE * 3 // 4, y + TILE_SIZE * 3 // 4)
                pygame.draw.polygon(surface, COLOR_SPIKE, (p1, p2, p3))

            elif cell == "V":  # 항아리
                pygame.draw.circle(
                    surface,
                    COLOR_VASE,
                    (x + TILE_SIZE // 2, y + TILE_SIZE // 2),
                    TILE_SIZE // 3,
                )
            # '.' 은 기본 바닥만 있으니 추가 작업 X


def draw_player(surface):
    pygame.draw.circle(
        surface,
        COLOR_PLAYER,
        (int(player_pos[0]), int(player_pos[1])),
        TILE_SIZE // 3,
    )


def draw_light(surface):
    """
    어두운 방 + 플레이어 주변 원형 시야.
    1) 전체를 덮는 반투명 레이어를 만들고
    2) 플레이어 주변, 횃불 주변에 '구멍'을 뚫습니다.
    """
    dark = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    dark.fill((0, 0, 0, 220))  # 220 정도면 어두운 편, 숫자 낮출수록 밝아짐

    # 플레이어 손전등 범위
    light_radius = TILE_SIZE * 2
    pygame.draw.circle(
        dark,
        (0, 0, 0, 0),  # 완전 투명 (구멍)
        (int(player_pos[0]), int(player_pos[1])),
        light_radius,
    )

    # 맵의 모든 T(횃불)에도 작은 빛 추가
    for row_idx, row in enumerate(map_grid):
        for col_idx, cell in enumerate(row):
            if cell == "T":
                tx = col_idx * TILE_SIZE + TILE_SIZE // 2
                ty = row_idx * TILE_SIZE + TILE_SIZE // 2
                pygame.draw.circle(
                    dark,
                    (0, 0, 0, 0),
                    (tx, ty),
                    TILE_SIZE * 1,
                )

    surface.blit(dark, (0, 0))


# -------------------- 이동/충돌 --------------------
def move_player(dx, dy):
    """플레이어를 dx, dy만큼 이동시키되, 벽(#)과 닫힌 문(D)과는 충돌 처리"""
    new_x = player_pos[0] + dx
    new_y = player_pos[1] + dy

    tile, col, row = get_tile_info_at_pixel(new_x, new_y)

    # 닫힌 문(D)도 벽처럼 막히게 하고, 문이 열린 후에는 '.'이 되어서 통과 가능
    if tile in ("#", "D"):
        return  # 이동 안 함

    # 이동 허용
    player_pos[0] = new_x
    player_pos[1] = new_y

    # 밟은 타일에 따른 상호작용 처리
    interact_with_tile(tile, col, row)


# -------------------- 메인 루프 --------------------
running = True
while running:
    dt = clock.tick(60)  # FPS 60

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 키 입력
    keys = pygame.key.get_pressed()
    dx = dy = 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        dx -= player_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        dx += player_speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        dy -= player_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        dy += player_speed

    if dx != 0 or dy != 0:
        move_player(dx, dy)

    # 그리기
    screen.fill(COLOR_BG)
    draw_map(screen)
    draw_player(screen)
    draw_light(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
