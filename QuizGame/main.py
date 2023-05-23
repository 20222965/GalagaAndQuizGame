import pygame
import json
import asyncio

from data.GameSetting import *
from data.Timer import *
from data.Stage import *

#게임루프
class GameLoop:
    def __init__(self):
        #타이머 시작
        Timer.start()
        self.preFrameTime = Timer.getElapsedTime()
        """이전 프레임 시간 저장"""
        
        self.player = player    #Player.py에서 생성한 player 객체 가져옴 선언된 위치 확인하려면 그 이름 누르고 F12 누르면 됩니다.
        self.screen = screen    #GameSetting에서 pygame 시작 후 screen 생성한 것을 가져옴.
        self.clock = clock      #프레임, 게임 루프할 때 사용
        
        self.stageManager = StageManager()  #스테이지 관리
        
        
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
            
            #화면 초기화.
            self.screen.fill((0,0,0))

            self.stageManager.update(deltaTime)
            
            self.stageManager.physics()
            
            self.stageManager.render(screen)
            
            gif_Died.render(screen)
            #이미지 전체 업데이트
            pygame.display.update()

            self.clock.tick(gameSetting["fps"]) #게임 루프 속도를 gameSetting["fps"]만큼 제한.
            
            await asyncio.sleep(0)  # 비동기 함수

async def main():
    game = GameLoop()
    await game.gameLoop()

asyncio.run(main())