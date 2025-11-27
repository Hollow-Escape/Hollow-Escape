import pygame

class UI:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 30)
        self.text_color = (255, 255, 255)
        # 인벤토리 관련 변수 삭제됨

    def draw(self, screen, key_count, max_keys):
        """화면 좌측 상단 기본 HUD (열쇠)"""
        # 열쇠 상태 표시
        key_text = f"Keys: {key_count} / {max_keys}"
        key_surface = self.font.render(key_text, True, self.text_color)
        screen.blit(key_surface, (20, 20))

    def draw_stamina_bar(self, screen, player, cam_x, cam_y):
        """플레이어 머리 위 스테미나 바"""
        bar_width = 40
        bar_height = 6
        
        # 플레이어 머리 위 좌표 계산
        screen_x = player.rect.centerx - cam_x - (bar_width // 2)
        screen_y = player.rect.top - cam_y - 12 

        # 색상 결정
        if player.is_exhausted:
            color = (255, 0, 0) # 탈진 시 빨강
        else:
            color = (0, 255, 0) # 평소 초록

        # 비율 계산
        if player.max_stamina > 0:
            ratio = player.current_stamina / player.max_stamina
        else:
            ratio = 0
        fill_width = int(bar_width * ratio)

        # 그리기
        pygame.draw.rect(screen, (0, 0, 0), (screen_x, screen_y, bar_width, bar_height)) # 배경
        pygame.draw.rect(screen, color, (screen_x, screen_y, fill_width, bar_height))    # 게이지
        pygame.draw.rect(screen, (255, 255, 255), (screen_x, screen_y, bar_width, bar_height), 1) # 테두리