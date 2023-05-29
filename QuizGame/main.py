import pygame
import json
import asyncio

from data.GameSetting import *
from data.Timer import *
from data.Stage import *

TIMER_TEXT = "Time: "
TIMER_FONT = pygame.font.Font(os.path.join(os.path.join(currentDir ,"font"),"CuteFont-Regular.ttf"), 48)
TIMER_COLOR = (255, 255, 255)

SCORE_TEXT = "Score: "
SCORE_FONT = pygame.font.Font(os.path.join(os.path.join(currentDir ,"font"), "CuteFont-Regular.ttf"), 48)
SCORE_COLOR = (255, 255, 255)

#게임루프
class GameLoop:
    def __init__(self):
        #타이머 시작
        Timer.start()
        self.preFrameTime = Timer.getElapsedTime()
        """이전 프레임 시간 저장"""
            
        self.timer_font = TIMER_FONT
        self.timer_color = TIMER_COLOR
        self.score_font = SCORE_FONT
        self.score_color = SCORE_COLOR
        
        self.player = player    #Player.py에서 생성한 player 객체 가져옴 선언된 위치 확인하려면 그 이름 누르고 F12 누르면 됩니다.
        self.screen = screen    #GameSetting에서 pygame 시작 후 screen 생성한 것을 가져옴.
        self.clock = clock      #프레임, 게임 루프할 때 사용
    
        self.stageManager = StageManager()  #스테이지 관리
    
    def render_timer(self):
        timer_text = int(Timer.getElapsedTime())
        timer_surface = self.timer_font.render(TIMER_TEXT + str(timer_text), True, self.timer_color)
        timer_rect = timer_surface.get_rect()
        timer_rect.topleft = (10, 10)
        self.screen.blit(timer_surface, timer_rect)

    def render_score(self):
        score_text = str(self.player.score)
        
        score_surface = self.score_font.render(SCORE_TEXT + score_text, True, self.score_color)
        score_rect = score_surface.get_rect()
        score_rect.topright = (gameSetting["width"] - 10, 10)
        self.screen.blit(score_surface, score_rect)
        
    async def gameLoop(self):
        self.stageManager.start()
        while True:
            #현재 프레임과 이전 프레임의 시간 차
            deltaTime = Timer.getDeltaTime(self.preFrameTime)
            
            self.preFrameTime = Timer.getElapsedTime()  #이전 프레임 시간 저장
            
            #입력
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                #버튼 누름
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.player.keylist.add(pygame.K_UP)
                    if event.key == pygame.K_DOWN:
                        self.player.keylist.add(pygame.K_DOWN)
                    if event.key == pygame.K_LEFT:
                        self.player.keylist.add(pygame.K_LEFT)
                    if event.key == pygame.K_RIGHT:
                        self.player.keylist.add(pygame.K_RIGHT)
                    if event.key == pygame.K_SPACE:
                        self.player.keylist.add(pygame.K_SPACE)
                    if event.key == pygame.K_s:
                        self.player.keylist.add(pygame.K_s)
                #버튼 뗌    
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.player.keylist.remove(pygame.K_UP)
                    if event.key == pygame.K_DOWN:
                        self.player.keylist.remove(pygame.K_DOWN)
                    if event.key == pygame.K_LEFT:
                        self.player.keylist.remove(pygame.K_LEFT)
                    if event.key == pygame.K_RIGHT:
                        self.player.keylist.remove(pygame.K_RIGHT)
                    if event.key == pygame.K_SPACE:
                        self.player.keylist.remove(pygame.K_SPACE)
                    if event.key == pygame.K_s:
                        self.player.keylist.remove(pygame.K_s)
            
            #화면 초기화.
            self.screen.fill((0,0,0))
            
            #timer, score 표시
            self.render_timer()
            self.render_score()

            self.stageManager.update(deltaTime)
            Item.update_all(deltaTime)
            
            self.stageManager.physics()
            self.player.physics(Item.getSpawnedItems())
            
            self.stageManager.render(screen)  
            
            gif_Died.render(screen)
            
            Item.render_all(screen)
            
            #이미지 전체 업데이트
            pygame.display.update()

            self.clock.tick(gameSetting["fps"]) #게임 루프 속도를 gameSetting["fps"]만큼 제한.
            
            await asyncio.sleep(0)  # 비동기 함수

async def main():
    game = GameLoop()
    await game.gameLoop()

asyncio.run(main())