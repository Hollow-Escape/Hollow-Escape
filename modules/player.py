import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # ---------------------------------------------------------
        # 1. 이미지 로드 및 미리 만들어두기
        # ---------------------------------------------------------
        try:
            raw_image = pygame.image.load("assets/images/player.png").convert_alpha()
            # 32x32 크기로 조정
            self.image_left = pygame.transform.scale(raw_image, (32, 32))
            # 좌우 반전하여 오른쪽 이미지 생성
            self.image_right = pygame.transform.flip(self.image_left, True, False)
            # 기본 이미지는 왼쪽
            self.image = self.image_left    
        except FileNotFoundError:
            # 이미지가 없으면 빨간 사각형
            self.image = pygame.Surface((32, 32))
            self.image.fill((255, 0, 0))
            self.image_left = self.image
            self.image_right = self.image
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
        # [추가됨] 몬스터가 추적하기 위해 필요한 타일 좌표
        self.tile_x = int(self.rect.centerx / 32)
        self.tile_y = int(self.rect.centery / 32)
        
        # 상태 변수
        self.is_hiding = False

        # [이동 및 스테미너 스탯]
        self.walk_speed = 4
        self.run_speed = 8
        self.speed = self.walk_speed
        
        self.max_stamina = 100.0
        self.current_stamina = 100.0
        self.stamina_drain = 1.0
        self.stamina_regen = 0.5

        # [탈진 상태 관리]
        self.is_exhausted = False  # 탈진 상태인가?
        self.exhausted_time = 0    # 탈진이 시작된 시간

    # -------------------------------------------------------
    # [숨기/나오기 메서드]
    # -------------------------------------------------------
    def hide(self):
        self.is_hiding = True
        print("플레이어: 숨었습니다.") 

    def reveal(self):
        self.is_hiding = False
        print("플레이어: 밖으로 나왔습니다.")

    # -------------------------------------------------------
    # [메인 업데이트 루프]
    # -------------------------------------------------------
    def update(self, walls):
        # 1. 키 입력 계산 (탈진 시 0 반환)
        dx, dy = self.get_input()
        
        # 2. 스테미너 및 탈진 상태 관리 (속도 결정)
        self.manage_stamina(dx, dy)

        # 3. 애니메이션 (이미지 방향 전환)
        self.animate(dx)
        
        # 4. 실제 이동 및 충돌 처리
        self.move(dx, dy, walls)

        # [추가됨] 이동 후 현재 타일 좌표 갱신 (32는 타일 크기)
        self.tile_x = int(self.rect.centerx / 32)
        self.tile_y = int(self.rect.centery / 32)

    # -------------------------------------------------------
    # [보조 메서드들 (Helper Methods)]
    # -------------------------------------------------------
    def get_input(self):
        # 탈진 상태면 움직일 수 없음
        if self.is_exhausted:
            return 0, 0

        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        
        if keys[pygame.K_LEFT]: dx = -1
        if keys[pygame.K_RIGHT]: dx = 1
        if keys[pygame.K_UP]: dy = -1
        if keys[pygame.K_DOWN]: dy = 1
            
        return dx, dy

    def manage_stamina(self, dx, dy):
        current_time = pygame.time.get_ticks()

        # [상황 A] 탈진 상태 (회복 대기)
        if self.is_exhausted:
            self.speed = 0 
            # 2초(2000ms) 지났는지 확인
            if current_time - self.exhausted_time > 2000:
                self.is_exhausted = False      
                self.current_stamina = 30.0    # 약간 회복 후 기상
                print("플레이어: 체력 회복! 이동 가능.")
            return 

        # [상황 B] 정상 상태
        keys = pygame.key.get_pressed()
        is_moving = (dx != 0 or dy != 0)
        
        # Shift키 + 움직임 + 스테미너 남음 -> 달리기
        if keys[pygame.K_LSHIFT] and is_moving:
            self.speed = self.run_speed
            self.current_stamina -= self.stamina_drain
        else:
            self.speed = self.walk_speed
            if self.current_stamina < self.max_stamina:
                self.current_stamina += self.stamina_regen

        # 스테미너 범위 제한
        self.current_stamina = max(0, min(self.current_stamina, self.max_stamina))

        # 0이 되면 탈진 시작
        if self.current_stamina <= 0:
            self.is_exhausted = True
            self.exhausted_time = current_time
            print("플레이어: 탈진! 2초간 이동 불가.")

    def animate(self, dx):
        """이동 방향에 따라 이미지 교체"""
        if dx < 0: 
            self.image = self.image_left
        elif dx > 0: 
            self.image = self.image_right

    def move(self, dx, dy, walls):
        """좌표 이동 및 벽 충돌 처리"""
        # 방향(dx,dy) * 속도(speed) = 실제 이동 거리
        move_x = dx * self.speed
        move_y = dy * self.speed

        # X축 이동
        self.rect.x += move_x
        for wall in walls:
            if self.rect.colliderect(wall):
                if move_x > 0:
                    self.rect.right = wall.left
                elif move_x < 0:
                    self.rect.left = wall.right

        # Y축 이동
        self.rect.y += move_y
        for wall in walls:
            if self.rect.colliderect(wall):
                if move_y > 0:
                    self.rect.bottom = wall.top
                elif move_y < 0:
                    self.rect.top = wall.bottom

    def draw(self, screen, camera_offset):
        """카메라 위치를 반영하여 그리기"""
        # 숨어있으면 그리지 않음
        if self.is_hiding:
            return
        
        screen_x = self.rect.x - camera_offset[0]
        screen_y = self.rect.y - camera_offset[1]
        screen.blit(self.image, (screen_x, screen_y))