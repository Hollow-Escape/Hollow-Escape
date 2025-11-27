# modules/monster.py

import math
import heapq
import random
import pygame

# 설정값
TILE_SIZE = 32
MAX_CHASE_TILES = 10           # 플레이어와 거리가 이 이상이면 chase 해제
WAIT_DURATION = 1              # 방 입구 등에서 대기 시간 (초)
SEARCH_DURATION = 10.0         # SEARCH 유지 시간 (초)

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
        self.path = []            # 추적 경로

        self.lost_timer = 0       # 플레이어를 시야에서 놓친 시간
        self.search_timer = 0     # SEARCH 상태 유지 시간
        self.wait_timer = 0       # WAIT 상태 유지 시간

        self.search_direction = None
        self.search_direction_timer = 0

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

        # rect 생성 (top-left 기준)
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)

        # 애니메이션 (2개 이미지 번갈아가며 신호)
        self.image_toggle = True
        
        # 외부 시스템
        self.map_manager = map_manager   # 맵
        self.current_map = "HALL"        # 초기 맵 이름 (지금은 임시)

    # spawn / despawn
    def spawn(self, tile_pos):
        self.tile_x, self.tile_y = tile_pos
        self.rect.topleft = (self.tile_x * TILE_SIZE,
                             self.tile_y * TILE_SIZE)

        self.active = True
        self.state = "PATROL"
        self.target_tile = None
        self.path = []

        self.lost_timer = 0
        self.search_timer = 0
        self.wait_timer = 0

    def despawn(self):
        self.active = False
        self.state = "NONE"
        self.target_tile = None
        self.path = []

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
        if self.in_chase_range((player.tile_x, player.tile_y), player.current_map) and not player.is_hiding:
            self.state = "CHASE"
            self.target_tile = (player.tile_x, player.tile_y)
            self.path = []  # chase는 새 경로 계산
            return
        
        # 목표가 없으면 새 랜덤 좌표와 경로 생성
        if self.target_tile is None:
            self.target_tile = self.get_random_walkable_tile(max_x=100, max_y=100)
            self.compute_path_to(self.target_tile)

        # 랜덤 좌표로 이동
        if self.path:
            self.follow_path(dt)            

        # 목표에 도달 시 처리
        if self.target_tile and self.tile_x == self.target_tile[0] and self.tile_y == self.target_tile[1]:
            self.target_tile = None
            self.path = []

    # chase state
    def update_chase(self, player, dt):
        # 플레이어가 괴물의 사정거리 밖이면 SEARCH 모드 진입
        if not self.in_chase_range((player.tile_x, player.tile_y), player.current_map):
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

        # 추적 중인 플레이어가 현재 방 입구 안으로 들어갔는지 확인
        entrance_tile = None
        for entrance in self.map_manager.room_entrances.get(self.current_map):
            if (player.tile_x, player.tile_y) == entrance:
                entrance_tile = entrance
                break
        
        # 목표 설정: 플레이어가 입구 
        if entrance_tile:
            self.target_tile = entrance_tile
        else:
            self.target_tile = (player.tile_x, player.tile_y)
        
        # 경로 계산 후 추적
        self.compute_path_to(self.target_tile)
        if self.path:
            self.follow_path(dt)

    # search state
    def update_search(self, player, dt):
        # 근처 랜덤 배회
        self.random_move(dt)

        # 플레이어가 숨지 않고 사정거리 안이면 CHASE
        if self.in_chase_range((player.tile_x, player.tile_y), player.current_map) and not player.is_hiding:
            self.state = "CHASE"
            self.lost_timer = 0
            self.path = []
            self.target_tile = (player.tile_x, player.tile_y)
            return
        
        # 일정 시간 지나면 순찰(PATROL) 복귀
        self.search_timer += dt
        if self.search_timer > SEARCH_DURATION:
            self.state = "PATROL"
            self.path = []
            self.target_tile = None

    # wait state
    def update_wait(self, dt):
        self.wait_timer += dt
        if self.wait_timer >= WAIT_DURATION:
            # 방 이동 (맵 변경)
            new_map, new_tile_x, new_tile_y = self.map_manager.move_to_room((self.tile_x, self.tile_y), self.current_map)

            # 새로운 좌표 받기
            self.current_map, self.tile_x, self.tile_y = new_map, new_tile_x, new_tile_y
            self.rect.topleft = (self.tile_x * TILE_SIZE,
                                self.tile_y * TILE_SIZE)
        
            # 이전 상태 복귀
            self.state = self.prev_state
            self.prev_state = None
            self.wait_timer = 0

    # 이동 관련
    # 최단 경로 계산 (A*)
    def compute_path_to(self, goal):
        start = (self.tile_x, self.tile_y)

        # 이미 같은 타일이면 종료
        if start == goal:
            self.path = []
            return
        
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: abs(start[0] - goal[0]) + abs(start[1] - goal[1])}
        visited = set()

        while open_set:
            _, current = heapq.heappop(open_set)
            if current in visited:
                continue
            visited.add(current)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                self.path = path[1:]
                return
            
            x, y = current
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                new_rect = self.rect.move(dx * TILE_SIZE, dy * TILE_SIZE)
                nx, ny = x+dx, y+dy
                if not self.can_move_to(new_rect):
                    continue
                tentative_g = g_score[current] + 1
                if (nx, ny) not in g_score or tentative_g < g_score[(nx, ny)]:
                    g_score[(nx, ny)] = tentative_g
                    f_score[(nx, ny)] = tentative_g + abs(nx-goal[0]) + abs(ny-goal[1])
                    came_from[(nx, ny)] = current
                    heapq.heappush(open_set, (f_score[(nx, ny)], (nx, ny)))
        self.path = []

    def follow_path(self, dt):
        if not self.path:
            return
        
        tx, ty = self.path[0]
        target_x = tx * TILE_SIZE
        target_y = ty * TILE_SIZE

        dx = target_x - self.rect.x
        dy = target_y - self.rect.y
        dist = max(0.001, math.sqrt(dx*dx + dy*dy))

        if abs(dx) > abs(dy):
            self.rect.x += (dx / dist) * self.speed * dt
        else:
            self.rect.y += (dy / dist) * self.speed * dt

        self.tile_x = self.rect.left // TILE_SIZE
        self.tile_y = self.rect.top // TILE_SIZE

        if abs(self.rect.x - target_x) < 1 and abs(self.rect.y - target_y) < 1:
            self.rect.topleft = (target_x, target_y)
            self.path.pop(0)

    # 주어진 rect의 모든 타일이 이동 가능한지 확인
    def can_move_to(self, rect):
        left_tile = rect.left // TILE_SIZE
        right_tile = (rect.right - 1) // TILE_SIZE
        top_tile = rect.top // TILE_SIZE
        bottom_tile = (rect.bottom - 1) // TILE_SIZE

        for ty in range(top_tile, bottom_tile + 1):
            for tx in range(left_tile, right_tile + 1):
                if not self.map_manager.is_walkable(tx, ty, self.current_map):
                    return False
        return True

    # 랜덤 배회 (Search 용)
    def random_move(self, dt):
        # 이동 전에 현재 위치가 문이면 WAIT
        if self.is_entrance():
            self.enter_wait_mode()
            return
        
        # 찾는 방향이 None 이거나 정해진 시간 만큼 일정 방향 동안 찾았을 경우
        if self.search_direction is None or self.search_direction_timer <= 0:
             # 방향 재설정 및 정해진 시간 재설정 (4방향)
            self.search_direction = random.choice([0, math.pi/2, math.pi, 3*math.pi/2])
            self.search_direction_timer = random.uniform(3.0, 4.0)
        
        dx = math.cos(self.search_direction) * self.speed * dt
        dy = math.sin(self.search_direction) * self.speed * dt

        new_x = self.rect.x + dx                      # 이동 후 x 픽셀 좌표
        new_y = self.rect.y + dy                      # 이동 후 y 픽셀 좌표
        new_tile_x = int(new_x / TILE_SIZE)           # 이동 후 x 타일 좌표
        new_tile_y = int(new_y / TILE_SIZE)           # 이동 후 y 타일 좌표

        # 이동 가능 여부 (문, 벽 있으면 이동 불가)
        walkable_x = self.map_manager.is_walkable(new_tile_x, self.tile_y, self.current_map) and not self.is_entrance(new_tile_x, self.tile_y)
        walkable_y = self.map_manager.is_walkable(self.tile_x, new_tile_y, self.current_map) and not self.is_entrance(self.tile_x, new_tile_y)

        # 실제 이동
        moved = False
        if walkable_x:
            self.rect.x = new_x
            self.tile_x = new_tile_x
            moved = True
        if walkable_y:
            self.rect.y = new_y
            self.tile_y = new_tile_y
            moved = True

        # 막혀서 움직이지 못하는 경우라면 다음 사이클에 방향 재설정
        if not moved:
            self.search_direction_timer = 0

        # 타이머 감소
        self.search_direction_timer -= dt

    # helper
    # 사정거리 체크
    def in_chase_range(self, player_tile, player_map):
        if player_tile is None or player_map != self.current_map:
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
    def is_entrance(self, x=None, y=None):
        check_x = self.tile_x if x is None else x
        check_y = self.tile_y if y is None else y
        return (check_x, check_y) in self.map_manager.room_entrances[self.current_map]
    
    # 플레이어와 충돌 체크
    def is_colliding(self, player):
        return self.rect.colliderect(player.rect)
    
    # patrol 모드에서 랜덤 target 타일 좌표 생성
    def get_random_walkable_tile(self, max_x=100, max_y=100):
        while True:
            x = random.randint(0, max_x-1)
            y = random.randint(0, max_y-1)
            if self.map_manager.is_walkable(x, y, self.current_map) and (x, y) not in self.map_manager.room_entrances[self.current_map]:
                return x, y
