# hollowescape/tests/monster/monster_test.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../modules')))
import pygame
import math
import random

from monster import Monster

pygame.init()

TILE_SIZE = 32

# -------------------------
# 테스트용 MapManager
# -------------------------
class TestMapManager:
    def __init__(self):
        # 넓은 맵: 20x20
        self.width = 20
        self.height = 20
        self.room_entrances = [(5, 5), (15, 15)]

    def is_walkable(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def move_to_room(self, tile_pos):
        # 실제 맵 이동 없이 좌표 그대로 반환
        return tile_pos

# -------------------------
# 테스트용 Player
# -------------------------
class TestPlayer:
    def __init__(self):
        self.tile_x = 2
        self.tile_y = 2
        self.rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
        self.rect.center = (self.tile_x * TILE_SIZE + TILE_SIZE//2,
                            self.tile_y * TILE_SIZE + TILE_SIZE//2)
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.is_hiding = False
        self.speed = 100  # 픽셀/초

    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT]:
            dx -= self.speed * dt
        if keys[pygame.K_RIGHT]:
            dx += self.speed * dt
        if keys[pygame.K_UP]:
            dy -= self.speed * dt
        if keys[pygame.K_DOWN]:
            dy += self.speed * dt

        self.rect.centerx += dx
        self.rect.centery += dy
        self.tile_x = int(self.rect.centerx / TILE_SIZE)
        self.tile_y = int(self.rect.centery / TILE_SIZE)

# -------------------------
# 화면 초기화
# -------------------------
screen = pygame.display.set_mode((TILE_SIZE*20, TILE_SIZE*20))
pygame.display.set_caption("Monster Test")
clock = pygame.time.Clock()

# 객체 생성
map_manager = TestMapManager()
monster = Monster(speed=50, map_manager=map_manager)
monster.spawn((0,0))
player = TestPlayer()

running = True
while running:
    dt = clock.tick(60) / 1000  # 초 단위
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 플레이어 입력 처리
    player.handle_input(dt)

    # 몬스터 업데이트
    monster.update(player, dt)

    # 화면 렌더링
    screen.fill((0,0,0))
    # entrance 표시
    for ex, ey in map_manager.room_entrances:
        pygame.draw.rect(screen, (255,0,0), pygame.Rect(ex*TILE_SIZE, ey*TILE_SIZE, TILE_SIZE, TILE_SIZE))
    screen.blit(monster.image, monster.rect)
    pygame.draw.rect(screen, (0,0,255), player.rect)  # 플레이어 파란색

    pygame.display.flip()

pygame.quit()
