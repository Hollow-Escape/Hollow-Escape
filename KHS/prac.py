import pygame
import sys

pygame.init()

# 기본 설정 --------------------------------------------------
TILE_SIZE = 64
MAP_DATA = [
    "###############",  # 0 맨 윗줄 전체 벽
    "#.....#..D....#",  # 1 위쪽 중앙에 문(D)
    "#.....#.......#",  # 2
    "#..T..#.......#",  # 3 왼쪽 위 쪽에 횃불(T)
    "###.###.......#",  # 4 굽이치는 통로
    "#...#.........#",  # 5
    "#...#..#####..#",  # 6 가운데 세로벽 + 오른쪽 방
    "#...#..#S.S#..#",  # 7 오른쪽 방 안의 가시(S)
    "#.P.#..#####..#",  # 8 왼쪽 아래 쪽의 압력판(P)
    "#...#.........#",  # 9
    "#...#.....V.V.#",  #10 오른쪽 아래 항아리(V) 2개
    "#...#.........#",  #11
    "###############",  #12 맨 아래줄 전체 벽
]

ROWS = len(MAP_DATA)
COLS = len(MAP_DATA[0])

WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

pygame.display.set_caption("Hollow-Escape - 방 테스트")


# 색 설정 (임시) ---------------------------------------------
COLOR_WALL = (40, 40, 40)
COLOR_FLOOR = (90, 90, 90)
COLOR_TORCH = (230, 180, 80)
COLOR_DOOR = (120, 60, 40)
COLOR_SWITCH = (150, 150, 150)
COLOR_VASE = (160, 110, 70)
COLOR_PLAYER = (200, 200, 255)


# 플레이어 설정 ----------------------------------------------
player_pos = [
    TILE_SIZE * 2 + TILE_SIZE // 2,  # x (열 2 근처)
    TILE_SIZE * 9 + TILE_SIZE // 2   # y (행 9 근처)
]
player_speed = 4


def draw_map(surface):
    """MAP_DATA를 읽어서 타일을 모두 그립니다."""
    for row_idx, row in enumerate(MAP_DATA):
        for col_idx, cell in enumerate(row):
            x = col_idx * TILE_SIZE
            y = row_idx * TILE_SIZE

            # 기본 바닥
            pygame.draw.rect(surface, COLOR_FLOOR, (x, y, TILE_SIZE, TILE_SIZE))

            if cell == '#':
                pygame.draw.rect(surface, COLOR_WALL, (x, y, TILE_SIZE, TILE_SIZE))

            elif cell == 'T':  # 횃불
                pygame.draw.rect(surface, COLOR_WALL, (x, y, TILE_SIZE, TILE_SIZE))
                pygame.draw.circle(surface, COLOR_TORCH,
                                   (x + TILE_SIZE // 2, y + TILE_SIZE // 2),
                                   TILE_SIZE // 4)

            elif cell == 'D':  # 문
                pygame.draw.rect(surface, COLOR_DOOR,
                                 (x + TILE_SIZE // 4, y + TILE_SIZE // 4,
                                  TILE_SIZE // 2, TILE_SIZE // 2))

            elif cell == 'P':  # 압력판
                pygame.draw.rect(surface, COLOR_SWITCH,
                                 (x + TILE_SIZE // 4, y + TILE_SIZE // 4,
                                  TILE_SIZE // 2, TILE_SIZE // 2))

            elif cell == 'V':  # 항아리
                pygame.draw.circle(surface, COLOR_VASE,
                                   (x + TILE_SIZE // 2, y + TILE_SIZE // 2),
                                   TILE_SIZE // 3)

            elif cell == 'S':  # 가시 (임시로 빨간 사각형)
                spike_rect = (x + TILE_SIZE // 4, y + TILE_SIZE // 4,
                              TILE_SIZE // 2, TILE_SIZE // 2)
                pygame.draw.rect(surface, (180, 40, 40), spike_rect)

def get_tile_at_pixel(px, py):
    """화면 좌표(px, py)가 맵의 어떤 문자(tile)인지 반환"""
    col = px // TILE_SIZE
    row = py // TILE_SIZE
    if 0 <= row < ROWS and 0 <= col < COLS:
        return MAP_DATA[row][col]
    return '#'  # 맵 밖은 다 벽 취급


def move_player(dx, dy):
    """플레이어 이동 + 벽 충돌 처리(아주 단순한 버전)"""
    new_x = player_pos[0] + dx
    new_y = player_pos[1] + dy

    # 플레이어 중심 기준으로 충돌 검사
    tile = get_tile_at_pixel(new_x, new_y)
    if tile != '#':  # 벽이 아니면 이동 허용
        player_pos[0] = new_x
        player_pos[1] = new_y


def draw_light(surface):
    """
    어두운 방 + 플레이어 주변 원형 시야 구현.
    1) 전체를 어둡게 덮는 반투명 Surface를 만든 다음
    2) 플레이어 주변에 투명한 원(구멍)을 뚫습니다.
    """
    # 전체 어두운 레이어 생성 (알파 채널 포함)
    dark = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    dark.fill((0, 0, 0, 200))  # 마지막 200 = 투명도(0~255)

    light_radius = TILE_SIZE * 2  # 빛 반경 (원하는 대로 조절)
    pygame.draw.circle(
        dark,
        (0, 0, 0, 0),  # 완전 투명한 색으로 원을 그려서 '구멍' 만들기
        (int(player_pos[0]), int(player_pos[1])),
        light_radius,
    )

    # 횃불(T)에도 작은 빛 구멍 하나씩 줄 수도 있습니다.
    for row_idx, row in enumerate(MAP_DATA):
        for col_idx, cell in enumerate(row):
            if cell == 'T':
                tx = col_idx * TILE_SIZE + TILE_SIZE // 2
                ty = row_idx * TILE_SIZE + TILE_SIZE // 2
                pygame.draw.circle(
                    dark,
                    (0, 0, 0, 0),
                    (tx, ty),
                    TILE_SIZE * 1,  # 횃불 빛 반경
                )

    surface.blit(dark, (0, 0))


# 메인 루프 --------------------------------------------------
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

    # 이동
    if dx != 0 or dy != 0:
        move_player(dx, dy)

    # 그리기
    screen.fill((0, 0, 0))
    draw_map(screen)

    # 플레이어 그리기
    pygame.draw.circle(
        screen,
        COLOR_PLAYER,
        (int(player_pos[0]), int(player_pos[1])),
        TILE_SIZE // 3,
    )

    # 어두운 레이어 + 빛
    draw_light(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
