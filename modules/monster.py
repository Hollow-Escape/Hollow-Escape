# modules/monster.py

import math
import random
import pygame

# 설정값
TILE_SIZE = 32
MAX_CHASE_TILES = 10           # 플레이어와 거리가 이 이상이면 chase 해제
WAIT_DURATION = 1.5            # 방 입구 등에서 대기 시간 (초)
SEARCH_DURATION = 3.0          # SEARCH 유지 시간 (초)

class Monster(pygame.sprite.Sprite):
    def __init__(self, speed, map_manager):
        super().__init__()

        # 타일 좌표
        self.tile_x = 0           # 몬스터 x 좌표
        self.tile_y = 0           # 몬스터 y 좌표

        self.speed = speed        # 몬스터 이동 속도 (픽셀/초 단위)

        self.active = False       # 스폰 여부 (True면 추적 시작)
        self.state = "NONE"       # 몬스터 행동 상태 (NONE / PATROL / CHASE / SEARCH / WAIT)
        self.prev_state = None    # 몬스터 이전 행동 상태 (WAIT -> 다시 원래 상태)
        self.target_tile = None   # 몬스터가 추적 중인 목표 좌표 (x, y)

        self.lost_timer = 0       # 플레이어를 시야에서 놓친 시간
        self.search_timer = 0     # SEARCH 상태 유지 시간
        self.wait_timer = 0       # WAIT 상태 유지 시간

        # 크기
        self.width = TILE_SIZE    # 가로
        self.height = TILE_SIZE   # 세로

        # 이미지 불러오기
        try:
            raw_image = pygame.image.load("assets/images/monster_walk1.png").convert_alpha()
            self.image_walk1 = pygame.transform.scale(raw_image, (self.width, self.height))
            self.image_walk2 = pygame.transform.flip(self.image_walk1, True, False)                  # 다른 이미지는 좌우반전만
            self.image = self.image_walk1
        except FileNotFoundError:
            # 이미지 없으면 초록 사각형
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((0, 255, 0))
            self.image_walk1 = self.image
            self.image_walk2 = self.image

        # rect 생성
        self.rect = self.image.get_rect()
        self.rect.center = (0, 0)

        # 애니메이션 (2개 이미지 번갈아가며 신호)
        self.image_toggle = True
        
        # 외부 시스템
        self.map_manager = map_manager   # 맵

    # spawn / despawn
    def spawn(self, tile_pos):
        self.tile_x, self.tile_y = tile_pos
        self.rect.center = (self.tile_x * TILE_SIZE + TILE_SIZE // 2,
                             self.tile_y * TILE_SIZE + TILE_SIZE // 2)

        self.active = True
        self.state = "PATROL"
        self.target_tile = None

        self.lost_timer = 0
        self.search_timer = 0
        self.wait_timer = 0

    def despawn(self):
        self.active = False
        self.state = "NONE"
        self.target_tile = None

    # main update (매 프레임 호출)
    def update(self, player, dt):
        if not self.active:
            return

        if self.state == "PATROL":
            self.update_patrol(player, dt)
        elif self.state == "CHASE":
            self.update_chase(player, dt)
        elif self.state == "SEARCH":
            self.update_search(player, dt)
        elif self.state == "WAIT":
            self.update_wait(dt)

    # patrol state
    def update_patrol(self, player, dt):
        # 플레이어가 괴물의 사정거리 안이고 숨은 상태가 아니라면 CHASE 모드 진입
        if self.in_chase_range((player.tile_x, player.tile_y)) and not player.is_hiding:
            self.state = "CHASE"
            self.target_tile = (player.tile_x, player.tile_y)
            return
        
        # 그냥 배회
        self.random_move(dt)

    # chase state
    def update_chase(self, player, dt):
        # 플레이어가 괴물의 사정거리 밖이면 SEARCH 모드 진입
        if not self.in_chase_range((player.tile_x, player.tile_y)):
            self.state = "SEARCH"
            self.search_timer = 0
            return
        
        # 플레이어가 숨으면 lost 증가 (사정 거리의 반 이하에서 숨으면 걸림)
        dx = abs(player.tile_x - self.tile_x)
        dy = abs(player.tile_y - self.tile_y)
        if player.is_hiding and (dx > MAX_CHASE_TILES / 2 or dy > MAX_CHASE_TILES / 2):
            self.lost_timer += dt
        else:
            self.lost_timer = 0

        # 일정 시간 동안 플레이어를 놓치면 SEARCH 모드 진입
        if self.lost_timer > 2.0:  # 초 단위
            self.state = "SEARCH"
            self.search_timer = 0
            return

        # 위의 해당 사항 없으면 추적
        target_x = player.tile_x * TILE_SIZE + TILE_SIZE // 2
        target_y = player.tile_y * TILE_SIZE + TILE_SIZE // 2
        self.move_towards((target_x, target_y), dt)

    # search state
    def update_search(self, player, dt):
        # 근처 랜덤 배회
        self.random_move(dt)

        # 플레이어가 숨지 않고 사정거리 안이면 CHASE
        if self.in_chase_range((player.tile_x, player.tile_y)) and not player.is_hiding:
            self.state = "CHASE"
            self.lost_timer = 0
            return
        
        # 일정 시간 지나면 순찰(PATROL) 복귀
        self.search_timer += dt
        if self.search_timer > SEARCH_DURATION:
            self.state = "PATROL"

    # wait state
    def update_wait(self, dt):
        self.wait_timer += dt
        if self.wait_timer >= WAIT_DURATION:
            # 방 이동 (맵 변경)
            new_tile_x, new_tile_y = self.map_manager.move_to_room((self.tile_x, self.tile_y))

            # 새로운 좌표 받기
            self.tile_x, self.tile_y = new_tile_x, new_tile_y
            self.rect.center = (self.tile_x * TILE_SIZE + TILE_SIZE//2,
                                self.tile_y * TILE_SIZE + TILE_SIZE//2)
        
            # 이전 상태 복귀
            self.state = self.prev_state
            self.prev_state = None
            self.wait_timer = 0

    # 이동 관련
    # target을 향해 이동 (픽셀 단위, 4방향)
    def move_towards(self, target, dt):
        # 이동 전에 현재 위치가 문이면 WAIT
        if self.is_entrance():
            self.enter_wait_mode()
            return
        
        tx, ty = target
        cx, cy = self.rect.center
        dx = tx - cx
        dy = ty - cy

        # 4방향 제한
        if abs(dx) > abs(dy):
            dy = 0
        else:
            dx = 0

        dist = max(0.001, math.sqrt(dx*dx + dy*dy))
        new_cx = cx + (dx / dist) * self.speed * dt      # 이동 후 x 픽셀 좌표
        new_cy = cy + (dy / dist) * self.speed * dt      # 이동 후 y 픽셀 좌표
        new_tile_x = int(new_cx / TILE_SIZE)             # 이동 후 x 타일 좌표
        new_tile_y = int(new_cy / TILE_SIZE)             # 이동 후 y 타일 좌표
        
        # 충돌 검사 후 이동
        if self.map_manager.is_walkable(new_tile_x, self.tile_y):      # x축 이동 검사
            self.rect.centerx = new_cx
            self.tile_x = new_tile_x
        if self.map_manager.is_walkable(self.tile_x, new_tile_y):      # y축 이동 검사
            self.rect.centery = new_cy
            self.tile_y = new_tile_y

    # 랜덤 배회
    def random_move(self, dt):
        # 이동 전에 현재 위치가 문이면 WAIT
        if self.is_entrance():
            self.enter_wait_mode()
            return
        
        # 4방향 제한
        angle = random.choice([0, math.pi/2, math.pi, 3*math.pi/2])
        dx = math.cos(angle) * self.speed * dt
        dy = math.sin(angle) * self.speed * dt

        new_cx = self.rect.centerx + dx                      # 이동 후 x 픽셀 좌표
        new_cy = self.rect.centery + dy                      # 이동 후 y 픽셀 좌표
        new_tile_x = int(new_cx / TILE_SIZE)                 # 이동 후 x 타일 좌표
        new_tile_y = int(new_cy / TILE_SIZE)                 # 이동 후 y 타일 좌표

        # 충돌 검사 후 이동
        if self.map_manager.is_walkable(new_tile_x, self.tile_y):
            self.rect.centerx = new_cx
            self.tile_x = new_tile_x
        if self.map_manager.is_walkable(self.tile_x, new_tile_y):
            self.rect.centery = new_cy
            self.tile_y = new_tile_y

    # helper
    # 사정거리 체크
    def in_chase_range(self, player_tile):
        if player_tile is None:
            return False
        
        px, py = player_tile

        # 정사각형 범위 판정
        return (
            abs(px - self.tile_x) <= MAX_CHASE_TILES and
            abs(py - self.tile_y) <= MAX_CHASE_TILES
        )
    
    # WAIT 모드 진입
    def enter_wait_mode(self):
        self.prev_state = self.state
        self.state = "WAIT"
        self.wait_timer = 0

    # 방 입구 체크
    def is_entrance(self):
        return (self.tile_x, self.tile_y) in self.map_manager.room_entrances
    
    # 플레이어와 충돌 체크
    def is_colliding(self, player):
        dx = abs(self.rect.centerx - player.rect.centerx)
        dy = abs(self.rect.centery - player.rect.centery)
        return dx < (self.width/2 + player.width/2) and dy < (self.height/2 + player.height/2)
