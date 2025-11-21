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

# ... (위쪽 Player 클래스 코드는 그대로 두세요) ...

# ==========================================
# ★ 모듈 단독 테스트 코드 (F5 실행용)
# ==========================================
if __name__ == "__main__":
    pygame.init()
    
    # 1. 화면 설정
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Player Module Test - Stamina & Camera")
    clock = pygame.time.Clock()

    # 2. 맵 데이터 (플레이어 가두기용)
    WORLD_WIDTH = 2000
    WORLD_HEIGHT = 2000
    
    # 벽 배치 (중앙 장애물 + 외곽 경계)
    walls = [
        pygame.Rect(300, 200, 100, 300),      # 중앙 벽
        pygame.Rect(600, 500, 200, 50),       # 가로 벽
        pygame.Rect(0, 0, WORLD_WIDTH, 10),   # 위
        pygame.Rect(0, WORLD_HEIGHT-10, WORLD_WIDTH, 10), # 아래
        pygame.Rect(0, 0, 10, WORLD_HEIGHT),  # 왼쪽
        pygame.Rect(WORLD_WIDTH-10, 0, 10, WORLD_HEIGHT)  # 오른쪽
    ]

    # 3. 플레이어 생성 (중앙 쯤에서 시작)
    player = Player(400, 300)

    # 폰트 설정 (상태 표시용)
    font = pygame.font.SysFont(None, 24)

    print("--- 테스트 시작: 방향키로 이동, L-Shift로 달리기 ---")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # 숨기/나오기 테스트 (H키)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    if player.is_hiding:
                        player.reveal()
                    else:
                        player.hide()

        # ---------------------------------------
        # (1) 업데이트
        # ---------------------------------------
        # 플레이어 업데이트 (벽 정보 전달)
        player.update(walls)

        # ---------------------------------------
        # (2) 카메라 계산 (플레이어 중심)
        # ---------------------------------------
        target_x = player.rect.centerx - SCREEN_WIDTH // 2
        target_y = player.rect.centery - SCREEN_HEIGHT // 2
        
        # 맵 밖을 비추지 않도록 제한 (Clamping)
        camera_x = max(0, min(target_x, WORLD_WIDTH - SCREEN_WIDTH))
        camera_y = max(0, min(target_y, WORLD_HEIGHT - SCREEN_HEIGHT))
        camera_offset = (camera_x, camera_y)

        # ---------------------------------------
        # (3) 그리기
        # ---------------------------------------
        screen.fill((30, 30, 30)) # 어두운 회색 배경

        # 벽 그리기 (카메라 적용)
        for wall in walls:
            # 벽 위치 - 카메라 위치 = 화면상 위치
            draw_rect = wall.move(-camera_x, -camera_y)
            pygame.draw.rect(screen, (150, 150, 150), draw_rect)

        # 플레이어 그리기 (카메라 오프셋 전달)
        player.draw(screen, camera_offset)

        # ---------------------------------------
        # (4) UI 테스트 (스테미너바 & 정보)
        # ---------------------------------------
        # 스테미너 바 배경 (회색)
        pygame.draw.rect(screen, (50, 50, 50), (10, 10, 200, 20))
        # 스테미너 바 현재값 (초록색 / 탈진시 빨간색)
        stamina_width = int(player.current_stamina * 2) # 100 * 2 = 200픽셀
        bar_color = (0, 255, 0) if not player.is_exhausted else (255, 0, 0)
        pygame.draw.rect(screen, bar_color, (10, 10, stamina_width, 20))
        
        # 테두리
        pygame.draw.rect(screen, (255, 255, 255), (10, 10, 200, 20), 2)

        # 텍스트 정보
        status_text = f"Pos: {player.rect.topleft} | State: {'Exhausted' if player.is_exhausted else 'Normal'}"
        text_surf = font.render(status_text, True, (255, 255, 255))
        screen.blit(text_surf, (10, 40))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()