import pygame

# ====== 맵 데이터 ======
#  # : 벽
#  . : 길
#  P : 플레이어 시작 위치.
#  A~F : 방 입장 트리거(문)

MAP_DATA = [
    "##############################",  # 0
    "#............####............#",  # 1
    "#............####............#",  # 2
    "#..AAAA......####......BBBB..#",  # 3  위쪽 좌/우 방 문
    "#............####............#",  # 4
    "#............####............#",  # 5
    "######.################.######",  # 6  메인 가로 복도
    "######.################.######",  # 7
    "#......################......#",  # 8  좌/우 큰 방
    "#......################......#",  # 9
    "#......####........####......#",  # 10
    "#......####........####......#",  # 11
    "#..CCCC####........####DDDD..#",  # 12 중앙 방들
    "#......####........####......#",  # 13
    "#......####........####......#",  # 14
    "#..............P.............#",  # 15 플레이어 시작 위치
    "##########.############.######",  # 16 아래쪽 복도
    "##########.############.######",  # 17
    "#EEEE....############....FFFF#",  # 18 아래쪽 좌/우 방 문
    "#........############........#",  # 19
    "#........############........#",  # 20
    "##############################",  # 21
]

ROOM_TRIGGERS = {
    "A": "upper_left_lab",
    "B": "upper_right_lab",
    "C": "center_left_room",
    "D": "center_right_room",
    "E": "bottom_left_room",
    "F": "bottom_right_room",
}

TILE_SIZE = 32
ROWS = len(MAP_DATA)
COLS = len(MAP_DATA[0])
SCREEN_WIDTH = COLS * TILE_SIZE
SCREEN_HEIGHT = ROWS * TILE_SIZE


def find_player_start():
    for y, row in enumerate(MAP_DATA):
        for x, ch in enumerate(row):
            if ch == "P":
                return x * TILE_SIZE, y * TILE_SIZE
    # 없으면 (0,0)
    return 0, 0


def build_door_triggers():
    """문 타일들의 Rect와 방 이름을 미리 만들어 둡니다."""
    triggers = []
    for y, row in enumerate(MAP_DATA):
        for x, ch in enumerate(row):
            if ch in ROOM_TRIGGERS:
                rect = pygame.Rect(
                    x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE
                )
                triggers.append((rect, ROOM_TRIGGERS[ch]))
    return triggers


def draw_map(surface):
    for y, row in enumerate(MAP_DATA):
        for x, ch in enumerate(row):
            rect = pygame.Rect(
                x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE
            )

            if ch == "#":  # 벽
                pygame.draw.rect(surface, (40, 40, 60), rect)
            elif ch == ".":  # 길 / 방 바닥
                pygame.draw.rect(surface, (200, 200, 220), rect)
            elif ch == "P":  # 시작 위치도 그냥 바닥 색
                pygame.draw.rect(surface, (200, 200, 220), rect)
            elif ch in ROOM_TRIGGERS:  # 문 트리거
                pygame.draw.rect(surface, (200, 200, 120), rect)

            # 타일 경계선(살짝 테두리)
            pygame.draw.rect(surface, (20, 20, 30), rect, 1)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Lab Mansion Map Example")

    clock = pygame.time.Clock()

    player_x, player_y = find_player_start()
    player_rect = pygame.Rect(
        player_x, player_y, TILE_SIZE, TILE_SIZE
    )

    door_triggers = build_door_triggers()

    speed = 4
    running = True

    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT]:
            dx -= speed
        if keys[pygame.K_RIGHT]:
            dx += speed
        if keys[pygame.K_UP]:
            dy -= speed
        if keys[pygame.K_DOWN]:
            dy += speed

        # 간단 이동 (벽 충돌은 아직 안 넣음)
        player_rect.x += dx
        player_rect.y += dy

        # 문 트리거 체크 (예: E 키로 입장)
        if keys[pygame.K_e]:
            for rect, room_name in door_triggers:
                if player_rect.colliderect(rect):
                    print("Enter room:", room_name)
                    # 여기서 room_name으로 딕셔너리 찾아서
                    # 새 페이지/새 씬 로딩하면 됩니다.

        screen.fill((0, 0, 0))
        draw_map(screen)
        pygame.draw.rect(screen, (80, 200, 80), player_rect)  # 플레이어

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
