from .GameSetting import *
from .Timer import *

from .Player import player
from .Bullet import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .SpriteInfo import *
    from .Enemy import Enemy


class Pattern(ABC):
    def __init__(self, mirror = False):
        self.patternStartTime = None
        self.enemy = None
        
        self.mirror = mirror
        
        self.isFinished = False
        self.isLoop = False
        
        self.idx = -1
        
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
    def update(self, deltaTime):
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
    def setPattern(self, patterns):
        if not isinstance(patterns, Iterable):
            patterns = [patterns]
        #패턴 소유자 설정 및 패턴 추가
        self.patternQueue = deque([pattern.setEnemy(self.enemy) for pattern in patterns])
        return self

    #다음 패턴 가져오는 함수
    def getNextPattern(self) -> Pattern:
        if len(self.patternQueue) > 0:
            return self.patternQueue.popleft()
        return None
    
    #매 프레임 갱신 함수
    def update(self, deltaTime):
        #현재 패턴이 없으면 (처음)
        if self.currentPattern is None:
            #패턴을 가져오고 초기화
            self.currentPattern = self.getNextPattern()
            if(self.currentPattern):
                self.currentPattern.init()

        #현재 패턴이 있으면 업데이트
        if self.currentPattern is not None:
            self.currentPattern.update(deltaTime)

            #현재 패턴이 끝났으면,
            if self.currentPattern.isFinished:
                #현재 패턴이 반복 패턴이면,
                if self.currentPattern.isLoop:
                    #맨 뒤로 옮김
                    self.patternQueue.append(self.currentPattern)
                #다음 패턴을 가져오고 초기화
                self.currentPattern = self.getNextPattern()
                if(self.currentPattern):
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
    
    @staticmethod
    def pattern02(mirror = False):
        pattern02 = [
        M_Normal(mirror=mirror),
        A_Normal(),
        M_WidthLoop(moveTimeValue = 0.3, vector=(500,0), mirror=mirror)
        ]
        return pattern02
    
    @staticmethod
    def pattern03(mirror = False):
        pattern03 = [
        M_Normal(mirror=mirror),
        A_Normal(),
        M_WidthLoop_move1(mirror=mirror)
        ]
        return pattern03
    
    @staticmethod
    def pattern04(mirror = False):
        pattern04 = [
        M_Normal(mirror=mirror),
        A_Normal(),
        M_WidthLoop_move2(mirror=mirror)
        ]
        return pattern04
#AttackPattern
class A_Normal(Pattern):
    def __init__(self, bulletIdx = 2, vector = (0,700), accel = 0, mirror = False):
        self.bulletIdx = bulletIdx
        self.vector = vector
        self.accel = accel
        super().__init__(mirror = mirror)
        #순환 패턴, 종료 시 마지막 패턴으로 다시 추가됨.
        self.isLoop = True
        
    def update(self, deltaTime):
        super().update(deltaTime)
        
        if Timer.getDeltaTime(self.patternStartTime) >= self.enemy.attackTimer:
            #불릿 생성 및 속도, 위치 설정
            self.enemy.bulletManagers[self.bulletIdx].getObject().setVector(self.vector).setAccel(self.accel).setCenterPos((self.enemy.getCenterPos()))
            self.patternStartTime = Timer.getElapsedTime()
            #패턴 종료
            self.isFinished = True

#플레이어 위치에 불릿 발사하는 패턴
class A_Guided(Pattern):
    def __init__(self, bulletIdx = 0, speed = 100, accel = 400 , attackTimer = 0.8, mirror = False):
        self.bulletIdx = bulletIdx
        self.speed = speed
        self.accel = accel
        self.attackTimer = attackTimer
        super().__init__(mirror = mirror)
        #순환 패턴, 종료 시 마지막 패턴으로 다시 추가됨.
        self.isLoop = True
        
    def update(self, deltaTime):
        super().update(deltaTime)
        if Timer.getDeltaTime(self.patternStartTime) >= self.attackTimer:
            
            # 플레이어 유도 방향 설정
            v = np.array(player.getCenterPos()) - np.array(self.enemy.getCenterPos())
            n = np.linalg.norm(v)
            unitVector = v / n
            #Bullet 속도 설정
            vector = unitVector * self.speed
            #불릿 생성 및 속도, 위치 설정
            self.enemy.bulletManagers[self.bulletIdx].getObject().setVector(vector).setAccel(self.accel).setCenterPos((self.enemy.getCenterPos()))
            self.patternStartTime = Timer.getElapsedTime()
            #패턴 종료
            self.isFinished = True        
class A_A(Pattern):
    def __init__(self, bulletIdx = 3, angle = 20,  cnt = 16, attackTimer= 0.4, mirror=False):
        self.bulletIdx = bulletIdx
        self.angle = angle
        self.cnt = cnt
        self.count = 0
        self.attackTimer = attackTimer
        super().__init__(mirror)
        #순환 패턴, 종료 시 마지막 패턴으로 다시 추가됨.
        self.isLoop = True
    def update(self, deltaTime):
        super().update(deltaTime)
        
        if Timer.getDeltaTime(self.patternStartTime) >= self.attackTimer:
            #불릿 생성 및 속도, 위치 설정
            self.enemy.bulletManagers[self.bulletIdx].getObject().setAngleSpeed(self.count * self.angle + 45,400).setCenterPos((self.enemy.getCenterPos()))
            self.enemy.bulletManagers[self.bulletIdx].getObject().setAngleSpeed(self.count * self.angle + 225,400).setCenterPos((self.enemy.getCenterPos()))
            self.count += 1
            self.patternStartTime = Timer.getElapsedTime()
            #패턴 종료
        if(self.cnt <= self.count):
            self.count = 0
            self.isFinished = True  

class A_Xrotate(Pattern):
    def __init__(self, bulletIdx = 3, angle = 10,  cnt = 16, speed = 400, attackTimer = 0.4, mirror=False):
        self.bulletIdx = bulletIdx
        self.angle = angle
        self.cnt = cnt
        self.count = 0
        self.speed = speed
        self.attackTimer = attackTimer
        super().__init__(mirror)
        #순환 패턴, 종료 시 마지막 패턴으로 다시 추가됨.
        self.isLoop = True
    def update(self, deltaTime):
        super().update(deltaTime)
        
        if Timer.getDeltaTime(self.patternStartTime) >= self.attackTimer:
            #불릿 생성 및 속도, 위치 설정
            for i in range(4):
                self.enemy.bulletManagers[self.bulletIdx].getObject().setAngleSpeed(self.count * self.angle + 45 + i * 90,self.speed).setCenterPos((self.enemy.getCenterPos()))
            self.count += 1
            self.patternStartTime = Timer.getElapsedTime()
            #패턴 종료
        if(self.cnt <= self.count):
            self.count = 0
            self.isFinished = True                                     
#MovePattern
#단순히 좌->우 일자로 이동하는 패턴
class M_Normal(Pattern):
    def __init__(self, moveTimeValue = 0.5, vector = (420,0), mirror = False):
        super().__init__(mirror = mirror)
        self.moveTimeValue = moveTimeValue
        self.moveTime = self.moveTimeValue
        self.vector = vector
        
    def init(self):
        super().init()
        #이동 시간
        self.moveTime = self.moveTimeValue
        
        #enemy vector 설정, 초당 해당 수치만큼 이동
        self.enemy.setVector(self.vector)
        #mirror 설정, 우 -> 좌로 이동
        if(self.mirror == True):
            self.enemy.vector[0] *= -1
                    
    def update(self, deltaTime):
        super().update(deltaTime)
        #moveTime - 프레임 시간
        if(self.moveTime > 0):
            self.moveTime -= deltaTime
        elif(self.moveTime <= 0):
            #enemy 속도를 0으로 해서 이동하지 않게 설정
            self.enemy.setVector(0,0)
            #패턴 종료
            self.isFinished = True
            return
        
        
        


#좌우 일자로 이동하고, 다음에는 반대로 이동하는 패턴
class M_WidthLoop(Pattern):
    def __init__(self, moveTimeValue = 0.5, vector = (300,0), mirror = False):
        super().__init__(mirror = mirror)
        self.isLoop = True
        self.moveTimeValue = moveTimeValue
        self.moveTime = self.moveTimeValue
        self.vector = vector
        
    def init(self):
        super().init()
        self.moveTime = self.moveTimeValue
        #enemy vector 설정, 초당 해당 수치만큼 이동
        self.enemy.setVector(self.vector)
        #mirror 설정, 우 -> 좌로 이동
        if(self.mirror == True):
            self.enemy.vector[0] *= -1
            
    def update(self, deltaTime):
        super().update(deltaTime)
        
        if(self.moveTime > 0):
            self.moveTime -= deltaTime
        elif(self.moveTime <= 0):
            #enemy 속도를 0으로 해서 이동하지 않게 설정
            self.enemy.setVector(0,0)
            self.mirror = not self.mirror
            #패턴 종료
            self.isFinished = True
            return

class B_Normal(Pattern):
    def __init__(self, bulletIdx = 4, mirror = False):
        self.bulletIdx = bulletIdx
        super().__init__(mirror = mirror)
        #순환 패턴, 종료 시 마지막 패턴으로 다시 추가됨.
        self.isLoop = True
        
    def update(self, deltaTime):
        super().update(deltaTime)
        
        if Timer.getDeltaTime(self.patternStartTime) >= self.enemy.attackTimer:
            #불릿 생성 및 속도, 위치 설정
            self.enemy.bulletManagers[self.bulletIdx].getObject().setVector(100, 700).setCenterPos((self.enemy.getCenterPos()))
            self.enemy.bulletManagers[self.bulletIdx].getObject().setVector(-100, 700).setCenterPos((self.enemy.getCenterPos()))
            self.enemy.bulletManagers[self.bulletIdx].getObject().setVector(300, 700).setCenterPos((self.enemy.getCenterPos()))
            self.enemy.bulletManagers[self.bulletIdx].getObject().setVector(-300, 700).setCenterPos((self.enemy.getCenterPos()))
            self.enemy.bulletManagers[self.bulletIdx].getObject().setVector(0, 700).setCenterPos((self.enemy.getCenterPos()))
            self.enemy.bulletManagers[self.bulletIdx].getObject().setVector(500, 900).setCenterPos((self.enemy.getCenterPos()))
            self.enemy.bulletManagers[self.bulletIdx].getObject().setVector(-500, 900).setCenterPos((self.enemy.getCenterPos()))
            self.enemy.bulletManagers[self.bulletIdx].getObject().setVector(0, 1300).setCenterPos((self.enemy.getCenterPos()))

            self.patternStartTime = Timer.getElapsedTime()
            #패턴 종료
            self.isFinished = True
            

class M_WidthLoop_move1(Pattern):
    def __init__(self, mirror = False):
        super().__init__(mirror = mirror)
        self.isLoop = True
        self.moveTimeValue = 0.3
        self.moveTime = self.moveTimeValue
        
    def init(self):
        super().init()
        self.moveTime = self.moveTimeValue
        #enemy vector 설정, 초당 해당 수치만큼 이동
        self.enemy.setVector(100, 0)
        #mirror 설정, 우 -> 좌로 이동
        if(self.mirror == True):
            self.enemy.vector[0] *= -1
        self.enemy.setCenterPos(200, 300)
            
    def update(self, deltaTime):
        super().update(deltaTime)
        
        if(self.moveTime > 0):
            self.moveTime -= deltaTime
        elif(self.moveTime <= 0):
            #enemy 속도를 0으로 해서 이동하지 않게 설정
            self.enemy.setVector(0, 0)
            self.mirror = not self.mirror
            self.enemy.setCenterPos(300, 400)
            #패턴 종료
            self.isFinished = True
            return
        
class M_WidthLoop_move2(Pattern):
    def __init__(self, mirror = False):
        super().__init__(mirror = mirror)
        self.isLoop = True
        self.moveTimeValue = 0.3
        self.moveTime = self.moveTimeValue
        
    def init(self):
        super().init()
        self.moveTime = self.moveTimeValue
        #enemy vector 설정, 초당 해당 수치만큼 이동
        self.enemy.setVector(100, 0)
        #mirror 설정, 우 -> 좌로 이동
        if(self.mirror == True):
            self.enemy.vector[0] *= -1
        self.enemy.setCenterPos(600, 300)
            
    def update(self, deltaTime):
        super().update(deltaTime)
        
        if(self.moveTime > 0):
            self.moveTime -= deltaTime
        elif(self.moveTime <= 0):
            #enemy 속도를 0으로 해서 이동하지 않게 설정
            self.enemy.setVector(0, 0)
            self.mirror = not self.mirror
            self.enemy.setCenterPos(600, 400)
            #패턴 종료
            self.isFinished = True
            return
        