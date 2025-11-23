import pygame

pygame.init() #pygame 초기화

WINDOW_WIDTH = 600 #창크기 설정
WINDOW_HEIGHT = 300

BLACK = (0,0,0) #RGB 기준으로 색상 정의
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255, 255, 0)

#창 설정
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("창의 타이틀")

#이미지 불러오기
sample_image = pygame.image.load("sample.jpg")

#게임 루프 (계속 돌아가게 함)
running = True
while running :
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:   #창의 x버튼을 눌렀을 때
            running = False
            
    screen.fill((30, 30, 30)) #화면 색칠
    pygame.draw.rect(screen, RED, (50, 50, 100, 100)) # 도형 그리기 
    pygame.draw.circle(screen, GREEN, (300, 200), 50)
    pygame.draw.line(screen, YELLOW, (400, 300), (500, 400), 5)
    
    #이미지 그리기 
    screen.blit(sample_image, (100, 100))  # (100,100)은 이미지 배치할 (x,y)좌표
    
    
    pygame.display.update() #화면 갱신 -> 이걸 호출해야 화면에 도형이 보임.
    

pygame.quit()
    
