import asyncio

from .Player import *
from .Enemy import *

#스테이지 추상 클래스
class Stage(ABC):
    #값 초기화
    @abstractmethod
    def __init__(self):
        self.player = player
        self.isFinished = False
        self.isSpawned = False
        self.stageElapsedTime = None
    #시작 시 값 초기화, spawn 호출   
    @abstractmethod
    def start(self):
        self.isFinished = False
        self.isSpawned = False
        self.stageElapsedTime = Timer.getElapsedTime()
    #몹 스폰    
    @abstractmethod    
    async def spawn(self):
        pass
    #매 프레임 스테이지 갱신    
    @abstractmethod
    def update(self):
        #나중에 이곳에 플레이어가 죽었을 경우 패배를 넣을 수 있음.
        pass
    #스테이지 이미지 갱신
    @abstractmethod    
    def render(self):
        pass

class StageManager:
    def __init__(self):
        self.stages = [Stage1()]  # 관리되는 모든 스테이지들을 저장하는 리스트
        self.currentStage = None # 현재 실행 중인 스테이지
        self.stageNumber = 0

    #스테이지 시작
    def start(self):
        self.stageNumber += 1
        self.currentStage = self.stages.pop(0)
        self.currentStage.start()
        
    #다음 스테이지 시작
    def nextStage(self):
        self.stageNumber += 1
        self.currentStage = self.stages.pop(0)
        self.currentStage.start()

    #매 프레임 스테이지 갱신
    def update(self):
        #현재 스테이지 끝나면, 다음 스테이지 가져옴.
        if(self.currentStage.isFinished == True):
            if(self.stages):
                self.nextStage()
            else:#지금은 테스트용으로 남은 스테이지가 없을 경우 마지막 스테이지 반복
                self.currentStage = self.currentStage.__class__()
                self.currentStage.start()
                
        #현재 스테이지 갱신    
        if self.currentStage:
            self.currentStage.update()
    
    #스테이지 충돌판정   
    def physics(self):
        if self.currentStage:
            self.currentStage.physics()
            
    #이미지 위치 변경
    def render(self, screen):
        if self.currentStage:
            self.currentStage.render(screen)


#1스테이지
class Stage1(Stage):
    #스테이지 시작 전에 호출됨.
    def __init__(self):
        super().__init__()
    
    #스테이지가 시작될 때 호출됨.    
    def start(self):
        super().start()
        #enemy 종류, 뒤는 내부에서 미리 생성할 개수 (부족할 경우 내부에서 알아서 추가됨)
        self.enemy1Manager = EnemyManager(enemy1, 4)
        self.enemy2Manager = EnemyManager(enemy2, 2)
        #비동기 테스크 생성하여 적 스폰 함수 실행.
        asyncio.create_task(self.spawn())
    #적 스폰하는 비동기 함수
    async def spawn(self):
        for i in range(2):
            self.enemy2Manager.getObject().setCenterPos(80-i*60,300 + i * 40).setPatterns([M_Normal(), A_Guided()])
            self.enemy2Manager.getObject().setCenterPos(720+i*60,300 + i * 40).setPatterns([M_Normal(mirror=True), A_Guided()])
            for j in range(2):
                if(j & 1 == 0):
                    self.enemy1Manager.getObject().setCenterPos(20 + i * 40,100 + i * 40).setVelocity(10,0).setPatterns(Patterns.pattern01())
                else:
                    self.enemy1Manager.getObject().setCenterPos(800 - i * 40,100 + i * 40).setVelocity(10,0).setPatterns(Patterns.pattern01(mirror=True))
                    await asyncio.sleep(1)    #1초 딜레이
                    
        self.isSpawned = True   #생성 종료
                    
    #매 프레임, player와 enemy들 갱신            
    def update(self):
        super().update()
        self.player.update()
        self.enemy1Manager.update()
        self.enemy2Manager.update()
        
        #만약, 스폰이 끝났고, 활동중인 몹이 없으면, 게임 클리어
        if(self.isSpawned == True and not self.enemy1Manager.activeObjects and not self.enemy2Manager.activeObjects):
            print("Stage1 Clear")
            self.isFinished = True
        
    #enemy들, player 간의 충돌 확인. 내부에서 enemy들의 bullet과 player, player의 bullet과 enemy들 충돌 확인함.    
    def physics(self):
        self.enemy1Manager.physics([player])
        self.enemy2Manager.physics([player])
        
    
    # Stage 1의 이미지 갱신. 가지고 있는 Pool과 player에 render하면 됩니다.    
    def render(self, screen):
        self.player.render(screen)
        self.enemy1Manager.render(screen)
        self.enemy2Manager.render(screen)