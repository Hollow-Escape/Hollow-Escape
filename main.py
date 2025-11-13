import pygame
import sys

# -------------------------------
# 기본 설정
# -------------------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GAME_TITLE = "Hollow Escape"

# -------------------------------
# 초기화
# -------------------------------
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(GAME_TITLE)
clock = pygame.time.Clock()

# -------------------------------
# 게임 루프
# -------------------------------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 화면 색상 채우기 (검은색)
    screen.fill((0, 0, 0))

    # TODO: 여기서 플레이어, 괴물, 맵, UI 등을 그릴 예정

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()