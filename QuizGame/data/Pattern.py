import math
import numpy as np
from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Iterable

from .GameSetting import *
from .Timer import *

from typing import TYPE_CHECKING
from .Player import player
if TYPE_CHECKING:
    from .Enemy import Enemy


class Pattern(ABC):
    def __init__(self, mirror = False):
        self.patternStartTime = None
        self.enemy = None
        
        self.mirror = mirror
        
        self.isFinished = False
        self.isLoop = False
        
    #패턴 소유자 설정
    def setEnemy(self, enemy : 'Enemy'):
        self.enemy = enemy
        
        return self
    #패턴 초기화    
    def init(self):
        #패턴 시작 시간 저장
        self.patternStartTime = Timer.getElapsedTime()
        self.isFinished = False
    #매 프레임 업데이트
    @abstractmethod
    def update(self):
        pass
            
#패턴 관리 클래스            
class PatternManager:
    def __init__(self, enemy : 'Enemy'):
        self.enemy = enemy  #소유자 설정
        self.patternQueue = deque()
        self.currentPattern = None
    #패턴 추가
    def addPattern(self, pattern : Pattern):
        #패턴 소유자 설정
        pattern.setEnemy(self.enemy)
        #패턴 추가
        self.patternQueue.append(pattern)
        return self
    #패턴 설정
    def setPattern(self, patterns : Iterable):
        #패턴 소유자 설정 및 패턴 추가
        self.patternQueue = deque([pattern.setEnemy(self.enemy) for pattern in patterns])
        return self

    #다음 패턴 실행
    def getNextPattern(self) -> Pattern:
        if len(self.patternQueue) > 0:
            return self.patternQueue.popleft()
        return None
    #매 프레임 갱신 함수
    def update(self):
        #현재 패턴이 없으면 (처음)
        if self.currentPattern is None:
            #패턴을 가져오고 초기화
            self.currentPattern = self.getNextPattern()
            self.currentPattern.init()

        #현재 패턴이 있으면 업데이트
        if self.currentPattern is not None:
            self.currentPattern.update()

            #현재 패턴이 끝났으면,
            if self.currentPattern.isFinished:
                #현재 패턴이 반복 패턴이면,
                if self.currentPattern.isLoop:
                    #맨 뒤로 옮김
                    self.patternQueue.append(self.currentPattern)
                #다음 패턴을 가져오고 초기화
                self.currentPattern = self.getNextPattern()
                self.currentPattern.init()
                
#그냥 패턴들 저장하는 리스트, 적 개체에 패턴을 직접 리스트로 넣어도 별 상관 없음    
class Patterns:
    @staticmethod
    def pattern01(mirror = False):
        pattern01 = [
        M_Normal(mirror=mirror),
        A_Normal(),
        M_WidthLoop(mirror=mirror)
        ]
        return pattern01
    
    
 
#AttackPattern
class A_Normal(Pattern):
    def __init__(self, mirror = False):
        super().__init__(mirror = mirror)
        #순환 패턴, 실행 후 마지막 패턴으로 이동함.
        self.isLoop = True
        
    def update(self):
        super().update()
        #
        if Timer.getDeltaTime(self.patternStartTime) >= self.enemy.attackTimer:
            self.enemy.bullect3Manager.getObject().setVelocity(0,10).setCenterPos((self.enemy.getCenterPos()))
            self.patternStartTime = Timer.getElapsedTime()
            self.isFinished = True

#플레이어 위치에 불릿 발사하는 패턴
class A_Guided(Pattern):
    def __init__(self, mirror = False):
        super().__init__(mirror = mirror)
        #순환 패턴, 실행 후 마지막 패턴으로 이동함.
        self.isLoop = True
        
    def update(self):
        super().update()
        if Timer.getDeltaTime(self.patternStartTime) >= self.enemy.attackTimer:
            
            # 플레이어 유도 방향 설정
            v = np.array(player.getCenterPos()) - np.array(self.enemy.getCenterPos())
            n = np.linalg.norm(v)
            unitVector = v / n
            #Bullet 속도 설정
            vector = unitVector * 5
            #불릿 생성 및 속도, 위치 설정
            self.enemy.bullectManager.getObject().setVelocity(vector).setCenterPos((self.enemy.getCenterPos()))
            self.patternStartTime = Timer.getElapsedTime()
            #패턴 종료
            self.isFinished = True        
        
#MovePattern
#단순히 좌우 일자로 이동하는 패턴
class M_Normal(Pattern):
    def __init__(self, mirror = False):
        super().__init__(mirror = mirror)
        self.moveFrame = 30
        
    def init(self):
        self.moveFrame = 30
        super().init()
        self.enemy.setVelocity(7,0)
        if(self.mirror == True):
            self.enemy.velocity[0] *= -1
                    
    def update(self):
        super().update()
        
        if(self.moveFrame <= 0):
            self.isFinished = True
            return
        
        self.enemy.move()
        self.moveFrame -= 1


#좌우 일자로 이동하고, 다음에는 반대로 이동하는 패턴
class M_WidthLoop(Pattern):
    def __init__(self, mirror = False):
        super().__init__(mirror = mirror)
        self.isLoop = True
        self.moveFrame = 20
        
    def init(self):
        super().init()
        
        self.moveFrame = 20
        self.enemy.setVelocity(5,0)
        if(self.mirror == True):
            self.enemy.velocity[0] *= -1
            
    def update(self):
        super().update()
        
        if(self.moveFrame <= 0):
            self.mirror = not self.mirror
            self.isFinished = True
            return
        
        self.enemy.move()
        self.moveFrame -= 1
