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
        self.stageEndTime = 3
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
    def update(self, deltaTime):
        #나중에 이곳에 플레이어가 죽었을 경우 패배를 넣을 수 있음.
        pass
    #스테이지 이미지 갱신
    @abstractmethod    
    def render(self):
        pass
class StageManager:
    def __init__(self):
        self.stages = [Stage1(),Stage2(),Stage3(),Stage4(),Stage5(),Stage6(),Stage7(),Stage8(),Stage9(),Stage10()]  # 관리되는 모든 스테이지들을 저장하는 리스트
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
    def update(self, deltaTime):
        #현재 스테이지 끝나면, 다음 스테이지 가져옴.
        if(self.currentStage.isFinished == True):
            if(self.stages):
                self.nextStage()
            else:#지금은 테스트용으로 남은 스테이지가 없을 경우 마지막 스테이지 반복
                self.currentStage.__init__()
                self.stageNumber += 1
                self.currentStage.start()
                
        #현재 스테이지 갱신    
        if self.currentStage:
            self.currentStage.update(deltaTime)
    
    #스테이지 충돌판정   
    def physics(self):
        if self.currentStage:
            self.currentStage.physics()
            
    #이미지 위치 변경
    def render(self, screen):
        if self.currentStage:
            self.currentStage.render(screen)


# 1스테이지
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
                    self.enemy1Manager.getObject().setCenterPos(20 + i * 40,100 + i * 40).setPatterns(Patterns.pattern01())
                else:
                    self.enemy1Manager.getObject().setCenterPos(800 - i * 40,100 + i * 40).setPatterns(Patterns.pattern01(mirror=True))
                    await asyncio.sleep(1)    #1초 딜레이
                    
        self.isSpawned = True   #생성 종료
                    
    #매 프레임, player와 enemy들 갱신            
    def update(self, deltaTime):
        super().update(deltaTime)
        self.player.update(deltaTime)
        self.enemy1Manager.update(deltaTime)
        self.enemy2Manager.update(deltaTime)
        
        #만약, 스폰이 끝났고, 활동중인 몹이 없으면, 게임 클리어
        if (self.isSpawned == True):
            activeEnemy = self.enemy1Manager.getObjectList() + self.enemy2Manager.getObjectList()
            if(activeEnemy):
                if(self.stageEndTime >= 0):
                    self.stageEndTime -= deltaTime
                else:
                    for enemy in activeEnemy:
                        if enemy.isOutsideScreen():
                            enemy.health = 1
                            enemy.hit()
            else:
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

# 2스테이지
class Stage2(Stage):
    # 스테이지 시작 전에 호출됨.
    def __init__(self):
        super().__init__()

    # 스테이지가 시작될 때 호출됨.
    def start(self):
        super().start()
        # enemy 종류, 뒤는 내부에서 미리 생성할 개수 (부족할 경우 내부에서 알아서 추가됨)
        self.enemy1Manager = EnemyManager(enemy1, 4)
        self.enemy2Manager = EnemyManager(enemy2, 6)
        # 비동기 테스크 생성하여 적 스폰 함수 실행.
        asyncio.create_task(self.spawn())

    # 적 스폰하는 비동기 함수
    async def spawn(self):
        for i in range(3):
            self.enemy2Manager.getObject().setCenterPos(80 - i * 60, 300 + i * 40).setPatterns([M_Normal(), A_Guided()])
            self.enemy2Manager.getObject().setCenterPos(720 + i * 60, 300 + i * 40).setPatterns([M_Normal(mirror=True), A_Guided()])

        for j in range(2):
            if (j & 1 == 0):
                self.enemy1Manager.getObject().setCenterPos(20 + j * 40, 140).setPatterns(
                Patterns.pattern01())
            else:
                self.enemy1Manager.getObject().setCenterPos(800 - j * 40, 140).setPatterns(
                Patterns.pattern01(mirror=True))
                await asyncio.sleep(1)  # 1초 딜레이

        self.isSpawned = True  # 생성 종료

    # 매 프레임, player와 enemy들 갱신
    def update(self, deltaTime):
        super().update(deltaTime)
        self.player.update(deltaTime)
        self.enemy1Manager.update(deltaTime)
        self.enemy2Manager.update(deltaTime)

        # 만약, 스폰이 끝났고, 활동중인 몹이 없으면, 게임 클리어
        if (self.isSpawned == True):
            activeEnemy = self.enemy1Manager.getObjectList() + self.enemy2Manager.getObjectList()
            if(activeEnemy):
                if(self.stageEndTime >= 0):
                    self.stageEndTime -= deltaTime
                else:
                    for enemy in activeEnemy:
                        if enemy.isOutsideScreen():
                            enemy.health = 1
                            enemy.hit()
            else:
                print("Stage2 Clear")
                self.isFinished = True

    # enemy들, player 간의 충돌 확인. 내부에서 enemy들의 bullet과 player, player의 bullet과 enemy들 충돌 확인함.
    def physics(self):
        self.enemy1Manager.physics([player])
        self.enemy2Manager.physics([player])

    # Stage 2의 이미지 갱신. 가지고 있는 Pool과 player에 render하면 됩니다.
    def render(self, screen):
        self.player.render(screen)
        self.enemy1Manager.render(screen)
        self.enemy2Manager.render(screen)

# 3스테이지
class Stage3(Stage):
    # 스테이지 시작 전에 호출됨.
    def __init__(self):
        super().__init__()

    # 스테이지가 시작될 때 호출됨.
    def start(self):
        super().start()
        # enemy 종류, 뒤는 내부에서 미리 생성할 개수 (부족할 경우 내부에서 알아서 추가됨)
        self.enemy1Manager = EnemyManager(enemy1, 1)
        self.enemy2Manager = EnemyManager(enemy2, 8)
        # 비동기 테스크 생성하여 적 스폰 함수 실행.
        asyncio.create_task(self.spawn())

    # 적 스폰하는 비동기 함수
    async def spawn(self):
        self.enemy1Manager.getObject().setCenterPos(160, 140).setPatterns(Patterns.pattern01())
        for i in range(4):
            self.enemy2Manager.getObject().setCenterPos(80 - i * 60, 340).setPatterns([M_Normal(), A_Guided()])
            self.enemy2Manager.getObject().setCenterPos(720 + i * 60, 340).setPatterns([M_Normal(mirror=True), A_Guided()])
            await asyncio.sleep(1)  # 1초 딜레이
        self.isSpawned = True  # 생성 종료

    # 매 프레임, player와 enemy들 갱신
    def update(self, deltaTime):
        super().update(deltaTime)
        self.player.update(deltaTime)
        self.enemy1Manager.update(deltaTime)
        self.enemy2Manager.update(deltaTime)

        # 만약, 스폰이 끝났고, 활동중인 몹이 없으면, 게임 클리어
        if (self.isSpawned == True):
            activeEnemy = self.enemy1Manager.getObjectList() + self.enemy2Manager.getObjectList()
            if(activeEnemy):
                if(self.stageEndTime >= 0):
                    self.stageEndTime -= deltaTime
                else:
                    for enemy in activeEnemy:
                        if enemy.isOutsideScreen():
                            enemy.health = 1
                            enemy.hit()
            else:
                print("Stage3 Clear")
                self.isFinished = True

    # enemy들, player 간의 충돌 확인. 내부에서 enemy들의 bullet과 player, player의 bullet과 enemy들 충돌 확인함.
    def physics(self):
        self.enemy1Manager.physics([player])
        self.enemy2Manager.physics([player])

    # Stage 3의 이미지 갱신. 가지고 있는 Pool과 player에 render하면 됩니다.
    def render(self, screen):
        self.player.render(screen)
        self.enemy1Manager.render(screen)
        self.enemy2Manager.render(screen)

# 4스테이지
class Stage4(Stage):
    # 스테이지 시작 전에 호출됨.
    def __init__(self):
        super().__init__()

    # 스테이지가 시작될 때 호출됨.
    def start(self):
        super().start()
        # enemy 종류, 뒤는 내부에서 미리 생성할 개수 (부족할 경우 내부에서 알아서 추가됨)
        self.enemy1Manager = EnemyManager(enemy1, 2)
        self.enemy2Manager = EnemyManager(enemy2, 6)
        # 비동기 테스크 생성하여 적 스폰 함수 실행.
        asyncio.create_task(self.spawn())

    # 적 스폰하는 비동기 함수
    async def spawn(self):
        for i in range(3):
            self.enemy2Manager.getObject().setCenterPos(80 - i * 60, 300 + i * 40).setPatterns([M_Normal(), A_Guided()])
            self.enemy2Manager.getObject().setCenterPos(720 + i * 60, 300 + i * 40).setPatterns(
                [M_Normal(mirror=True), A_Guided()])
        for j in range(2):
            if (j & 1 == 0):
                self.enemy1Manager.getObject().setCenterPos(20, 100 + i * 40).setPatterns(
                    Patterns.pattern01())
            else:
                self.enemy1Manager.getObject().setCenterPos(800, 100 + i * 40).setPatterns(
                    Patterns.pattern01(mirror=True))
                await asyncio.sleep(1)  # 1초 딜레이

        self.isSpawned = True  # 생성 종료

    # 매 프레임, player와 enemy들 갱신
    def update(self, deltaTime):
        super().update(deltaTime)
        self.player.update(deltaTime)
        self.enemy1Manager.update(deltaTime)
        self.enemy2Manager.update(deltaTime)

        # 만약, 스폰이 끝났고, 활동중인 몹이 없으면, 게임 클리어
        if (self.isSpawned == True):
            activeEnemy = self.enemy1Manager.getObjectList() + self.enemy2Manager.getObjectList()
            if(activeEnemy):
                if(self.stageEndTime >= 0):
                    self.stageEndTime -= deltaTime
                else:
                    for enemy in activeEnemy:
                        if enemy.isOutsideScreen():
                            enemy.health = 1
                            enemy.hit()
            else:
                print("Stage4 Clear")
                self.isFinished = True

    # enemy들, player 간의 충돌 확인. 내부에서 enemy들의 bullet과 player, player의 bullet과 enemy들 충돌 확인함.
    def physics(self):
        self.enemy1Manager.physics([player])
        self.enemy2Manager.physics([player])

    # Stage 4의 이미지 갱신. 가지고 있는 Pool과 player에 render하면 됩니다.
    def render(self, screen):
        self.player.render(screen)
        self.enemy1Manager.render(screen)
        self.enemy2Manager.render(screen)

# 5스테이지
class Stage5(Stage):

    # 스테이지 시작 전에 호출됨.
    def __init__(self):
        super().__init__()

    # 스테이지가 시작될 때 호출됨.
    def start(self):
        super().start()
        # enemy 종류, 뒤는 내부에서 미리 생성할 개수 (부족할 경우 내부에서 알아서 추가됨)
        self.enemy02Manager = EnemyManager(Enemy(img_enemys[2], health= 5), 2)
        self.enemy01Manager = EnemyManager(enemy2, 16)
        # 비동기 테스크 생성하여 적 스폰 함수 실행.
        asyncio.create_task(self.spawn())

    # 적 스폰하는 비동기 함수
    async def spawn(self):
        for i in range(4):
            self.enemy01Manager.getObject().setCenterPos(80 - i * 60, 300).setPatterns([M_Normal(), A_Guided()])
            self.enemy01Manager.getObject().setCenterPos(720 + i * 60, 300).setPatterns(
                [M_Normal(mirror=True), A_Guided()])
            if (i % 2 == 0):
                self.enemy01Manager.getObject().setCenterPos(50 - i * 60, 200).setPatterns([M_Normal(mirror=True), A_Guided()])
        for l in range(2):
            self.enemy01Manager.getObject().setCenterPos(20 - l * 60, 350).setPatterns([M_Normal(), A_Guided()])
            self.enemy01Manager.getObject().setCenterPos(780 + l * 60, 350).setPatterns(
                [M_Normal(mirror=True), A_Guided()])
        for k in range(2):
            self.enemy01Manager.getObject().setCenterPos(-100 - k * 50, 100).setPatterns([M_Normal(), A_Guided()])
            self.enemy01Manager.getObject().setCenterPos(900 + k * 50, 100).setPatterns(
                [M_Normal(mirror=True), A_Guided()])
        for j in range(3):
            self.enemy02Manager.getObject().setCenterPos(20 + j * 40, 100 + j * 40).setPatterns([M_Normal(), A_A(angle=30)])
            self.enemy02Manager.getObject().setCenterPos(800 - j * 40, 100 + j * 40).setPatterns([M_Normal(mirror=True), A_A(angle=-30)])

        await asyncio.sleep(1)  # 1초 딜레이

        self.isSpawned = True  # 생성 종료

    # 매 프레임, player와 enemy들 갱신
    def update(self, deltaTime):
        super().update(deltaTime)
        self.player.update(deltaTime)
        self.enemy01Manager.update(deltaTime)
        self.enemy02Manager.update(deltaTime)

        # 만약, 스폰이 끝났고, 활동중인 몹이 없으면, 게임 클리어
        if (self.isSpawned == True):
            activeEnemy = self.enemy01Manager.getObjectList() + self.enemy02Manager.getObjectList()
            if(activeEnemy):
                if(self.stageEndTime >= 0):
                    self.stageEndTime -= deltaTime
                else:
                    for enemy in activeEnemy:
                        if enemy.isOutsideScreen():
                            enemy.health = 1
                            enemy.hit()
            else:
                print("Stage5 Clear")
                self.isFinished = True

    # enemy들, player 간의 충돌 확인. 내부에서 enemy들의 bullet과 player, player의 bullet과 enemy들 충돌 확인함.
    def physics(self):
        self.enemy01Manager.physics([player])
        self.enemy02Manager.physics([player])

    # Stage 5의 이미지 갱신. 가지고 있는 Pool과 player에 render하면 됩니다.
    def render(self, screen):
        self.player.render(screen)
        self.enemy01Manager.render(screen)
        self.enemy02Manager.render(screen)

# 6스테이지
class Stage6(Stage):
    #스테이지 시작 전에 호출됨.
    def __init__(self):
        super().__init__()
    
    #스테이지가 시작될 때 호출됨.    
    def start(self):
        super().start()
        #enemy 종류, 뒤는 내부에서 미리 생성할 개수 (부족할 경우 내부에서 알아서 추가됨)
        self.enemy01Manager = EnemyManager(Enemy(img_enemys[1], health=6), 3)
        self.enemy02Manager = EnemyManager(Enemy(img_enemys[2], health=6), 3)
        #비동기 테스크 생성하여 적 스폰 함수 실행.
        asyncio.create_task(self.spawn())
    #적 스폰하는 비동기 함수
    async def spawn(self):
        
        self.enemy01Manager.getObject().setCenterPos(190, 100).setPatterns([M_Normal(), A_Guided(4,speed=400, accel=30,attackTimer=0.5)]).setHealth(3).setDropTable(0.3,0.7)
        self.enemy02Manager.getObject().setCenterPos(190, 300).setPatterns([M_Normal(), A_Xrotate(attackTimer=0.35,angle=10)]).setHealth(10).setDropTable(0.3,0.7)
        
        
        self.enemy02Manager.getObject().setCenterPos(60, 400).setPatterns([M_Normal(), A_Xrotate(angle=15,attackTimer=0.45,speed=330)]).setHealth(5)
        self.enemy02Manager.getObject().setCenterPos(60, 200).setPatterns([M_Normal(), A_Xrotate(angle=15,attackTimer=0.45,speed=330)]).setHealth(5)
        
        
        
        self.enemy02Manager.getObject().setCenterPos(760, 400).setPatterns([M_Normal(mirror=True), A_Xrotate(angle=15,attackTimer=0.45,speed=330)]).setHealth(5)
        self.enemy02Manager.getObject().setCenterPos(760, 200).setPatterns([M_Normal(mirror=True), A_Xrotate(angle=15,attackTimer=0.45,speed=330)]).setHealth(5)
        self.isSpawned = True   #생성 종료
                    
    #매 프레임, player와 enemy들 갱신            
    def update(self, deltaTime):
        super().update(deltaTime)
        self.player.update(deltaTime)
        self.enemy01Manager.update(deltaTime)
        self.enemy02Manager.update(deltaTime)
        
        #만약, 스폰이 끝났고, 활동중인 몹이 없으면, 게임 클리어
        if (self.isSpawned == True):
            activeEnemy = self.enemy01Manager.getObjectList() + self.enemy02Manager.getObjectList()
            if(activeEnemy):
                if(self.stageEndTime >= 0):
                    self.stageEndTime -= deltaTime
                else:
                    for enemy in activeEnemy:
                        if enemy.isOutsideScreen():
                            enemy.health = 1
                            enemy.hit()
            else:
                print("Stage6 Clear")
                self.isFinished = True
        
    #enemy들, player 간의 충돌 확인. 내부에서 enemy들의 bullet과 player, player의 bullet과 enemy들 충돌 확인함.    
    def physics(self):
        self.enemy01Manager.physics([player])
        self.enemy02Manager.physics([player])
        
    
    # Stage 6의 이미지 갱신. 가지고 있는 Pool과 player에 render하면 됩니다.    
    def render(self, screen):
        self.player.render(screen)
        self.enemy01Manager.render(screen)
        self.enemy02Manager.render(screen)

# 7스테이지
class Stage7(Stage):
    #스테이지 시작 전에 호출됨.
    def __init__(self):
        super().__init__()
    
    #스테이지가 시작될 때 호출됨.    
    def start(self):
        super().start()
        #enemy 종류, 뒤는 내부에서 미리 생성할 개수 (부족할 경우 내부에서 알아서 추가됨)
        self.enemy02Manager = EnemyManager(Enemy(img_enemys[2]), 4)
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
                    self.enemy02Manager.getObject().setCenterPos(20 + i * 40,100 + i * 40).setVector(10,0).setPatterns(
                        [M_Normal(),A_Xrotate(cnt=8,angle=20,attackTimer=0.25),M_WidthLoop(moveTimeValue = 0.3, vector=(500,0))]).setDropTable(0.3,0.7)
                else:
                    self.enemy02Manager.getObject().setCenterPos(800 - i * 40,100 + i * 40).setVector(10,0).setPatterns(
                        [M_Normal(mirror=True),A_Xrotate(cnt=8,angle=-20,attackTimer=0.25),M_WidthLoop(moveTimeValue = 0.3, vector=(500,0), mirror=True)]).setDropTable(0.3,0.7)
                    await asyncio.sleep(1)    #1초 딜레이
                    
        self.isSpawned = True   #생성 종료
                    
    #매 프레임, player와 enemy들 갱신            
    def update(self, deltaTime):
        super().update(deltaTime)
        self.player.update(deltaTime)
        self.enemy02Manager.update(deltaTime)
        self.enemy2Manager.update(deltaTime)
        
        #만약, 스폰이 끝났고, 활동중인 몹이 없으면, 게임 클리어
        if (self.isSpawned == True):
            activeEnemy = self.enemy02Manager.getObjectList() + self.enemy2Manager.getObjectList()
            if(activeEnemy):
                if(self.stageEndTime >= 0):
                    self.stageEndTime -= deltaTime
                else:
                    for enemy in activeEnemy:
                        if enemy.isOutsideScreen():
                            enemy.health = 1
                            enemy.hit()
            else:
                print("Stage7 Clear")
                self.isFinished = True
        
    #enemy들, player 간의 충돌 확인. 내부에서 enemy들의 bullet과 player, player의 bullet과 enemy들 충돌 확인함.    
    def physics(self):
        self.enemy02Manager.physics([player])
        self.enemy2Manager.physics([player])
        
    
    # Stage 7의 이미지 갱신. 가지고 있는 Pool과 player에 render하면 됩니다.    
    def render(self, screen):
        self.player.render(screen)
        self.enemy02Manager.render(screen)
        self.enemy2Manager.render(screen)

# 8스테이지
class Stage8(Stage):
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
            self.enemy2Manager.getObject().setCenterPos(80-i*60,300 + i * 40).setPatterns([M_Normal(), A_Guided(), M_WidthLoop(moveTimeValue=0.3, vector=(500,0)),A_Xrotate(angle=0,cnt=1,speed=500,attackTimer=0)])
            self.enemy2Manager.getObject().setCenterPos(720+i*60,300 + i * 40).setPatterns([M_Normal(mirror=True), A_Guided(), M_WidthLoop(moveTimeValue=0.3, vector=(500,0)),A_Xrotate(angle=0,cnt=1,speed=500,attackTimer=0)])
            for j in range(2):
                if(j & 1 == 0):
                    self.enemy1Manager.getObject().setCenterPos(20 + i * 40,100 + i * 40).setVector(10,0).setPatterns(Patterns.pattern02())
                else:
                    self.enemy1Manager.getObject().setCenterPos(800 - i * 40,100 + i * 40).setVector(10,0).setPatterns(Patterns.pattern02(mirror=True))
                    await asyncio.sleep(1)    #1초 딜레이
                    
        self.isSpawned = True   #생성 종료
                    
    #매 프레임, player와 enemy들 갱신            
    def update(self, deltaTime):
        super().update(deltaTime)
        self.player.update(deltaTime)
        self.enemy1Manager.update(deltaTime)
        self.enemy2Manager.update(deltaTime)
        
        #만약, 스폰이 끝났고, 활동중인 몹이 없으면, 게임 클리어
        if (self.isSpawned == True):
            activeEnemy = self.enemy1Manager.getObjectList() + self.enemy2Manager.getObjectList()
            if(activeEnemy):
                if(self.stageEndTime >= 0):
                    self.stageEndTime -= deltaTime
                else:
                    for enemy in activeEnemy:
                        if enemy.isOutsideScreen():
                            enemy.health = 1
                            enemy.hit()
            else:
                print("Stage8 Clear")
                self.isFinished = True
        
    #enemy들, player 간의 충돌 확인. 내부에서 enemy들의 bullet과 player, player의 bullet과 enemy들 충돌 확인함.    
    def physics(self):
        self.enemy1Manager.physics([player])
        self.enemy2Manager.physics([player])
        
    
    # Stage 7의 이미지 갱신. 가지고 있는 Pool과 player에 render하면 됩니다.    
    def render(self, screen):
        self.player.render(screen)
        self.enemy1Manager.render(screen)
        self.enemy2Manager.render(screen)

# 9스테이지
class Stage9(Stage):
    # 스테이지 시작 전에 호출됨.
    def __init__(self):
        super().__init__()

    # 스테이지가 시작될 때 호출됨.
    def start(self):
        super().start()
        # enemy 종류, 뒤는 내부에서 미리 생성할 개수 (부족할 경우 내부에서 알아서 추가됨)
        self.enemy1Manager = EnemyManager(enemy1, 3)
        self.enemy2Manager = EnemyManager(enemy2, 8)
        # 비동기 테스크 생성하여 적 스폰 함수 실행.
        asyncio.create_task(self.spawn())

    # 적 스폰하는 비동기 함수
    async def spawn(self):
        self.enemy1Manager.getObject().setCenterPos(160, 140).setVector(10, 0).setPatterns(Patterns.pattern02())
        self.enemy1Manager.getObject().setCenterPos(360, 140).setVector(10, 0).setPatterns(Patterns.pattern02())
        self.enemy1Manager.getObject().setCenterPos(-40, 140).setVector(10, 0).setPatterns(Patterns.pattern02())
        for i in range(4):
            self.enemy2Manager.getObject().setCenterPos(80 - i * 60, 340).setPatterns(
                [M_Normal(), A_Guided(),M_WidthLoop(moveTimeValue=0.3, vector = (100,0)),A_Xrotate(angle=45,cnt=2,attackTimer=0)])
            self.enemy2Manager.getObject().setCenterPos(720 + i * 60, 340).setPatterns(
                [M_Normal(mirror=True), A_Guided(), M_WidthLoop(moveTimeValue=0.3, vector = (100,0)),A_Xrotate(angle=45,cnt=2,attackTimer=0)])
            await asyncio.sleep(1)  # 1초 딜레이
        self.isSpawned = True  # 생성 종료

    # 매 프레임, player와 enemy들 갱신
    def update(self, deltaTime):
        super().update(deltaTime)
        self.player.update(deltaTime)
        self.enemy1Manager.update(deltaTime)
        self.enemy2Manager.update(deltaTime)

        # 만약, 스폰이 끝났고, 활동중인 몹이 없으면, 게임 클리어
        if (self.isSpawned == True):
            activeEnemy = self.enemy1Manager.getObjectList() + self.enemy2Manager.getObjectList()
            if(activeEnemy):
                if(self.stageEndTime >= 0):
                    self.stageEndTime -= deltaTime
                else:
                    for enemy in activeEnemy:
                        if enemy.isOutsideScreen():
                            enemy.health = 1
                            enemy.hit()
            else:
                print("Stage9 Clear")
                self.isFinished = True

    # enemy들, player 간의 충돌 확인. 내부에서 enemy들의 bullet과 player, player의 bullet과 enemy들 충돌 확인함.
    def physics(self):
        self.enemy1Manager.physics([player])
        self.enemy2Manager.physics([player])

    # Stage 3의 이미지 갱신. 가지고 있는 Pool과 player에 render하면 됩니다.
    def render(self, screen):
        self.player.render(screen)
        self.enemy1Manager.render(screen)
        self.enemy2Manager.render(screen)

# 10스테이지
class Stage10(Stage):
    # 스테이지 시작 전에 호출됨.
    def __init__(self):
        super().__init__()

    # 스테이지가 시작될 때 호출됨.
    def start(self):
        super().start()
        # enemy 종류, 뒤는 내부에서 미리 생성할 개수 (부족할 경우 내부에서 알아서 추가됨)
        self.enemy1Manager = EnemyManager(enemy1, 1)
        self.enemy2Manager = EnemyManager(enemy2, 8)
        self.enemy02Manager = EnemyManager(enemy1, 4)
        # 비동기 테스크 생성하여 적 스폰 함수 실행.
        asyncio.create_task(self.spawn())

    # 적 스폰하는 비동기 함수
    async def spawn(self):
        self.enemy1Manager.getObject().setCenterPos(160, 140).setPatterns([M_Normal(), B_Normal()])
        self.enemy1Manager.getObject().setCenterPos(760, 140).setVector(10, 0).setPatterns([
        M_Normal(mirror=True),
        A_Normal(4),
        M_WidthLoop(moveTimeValue = 0.3, vector=(500,0), mirror=True)
        ])
        self.enemy1Manager.getObject().setCenterPos(-40, 140).setVector(10, 0).setPatterns([
        M_Normal(),
        A_Normal(4),
        M_WidthLoop(moveTimeValue = 0.3, vector=(500,0))
        ])
        self.enemy1Manager.getObject().setCenterPos(60, 200).setVector(10, 0).setPatterns([
        M_Normal(),
        A_Normal(4),
        M_WidthLoop(moveTimeValue = 0.3, vector=(500,0))
        ])
        self.enemy1Manager.getObject().setCenterPos(660, 200).setVector(10, 0).setPatterns([
        M_Normal(mirror=True),
        A_Normal(4),
        M_WidthLoop(moveTimeValue = 0.3, vector=(500,0), mirror=True)
        ])
        for j in range(2):
            if (j & 1 == 0):
                self.enemy1Manager.getObject().setCenterPos(20 + j * 40, 140).setVector(10,0).setPatterns([
                    M_Normal(),A_Xrotate(angle=30,attackTimer=0.2,cnt=4,speed=330),M_WidthLoop_move1()])
            else:
                self.enemy1Manager.getObject().setCenterPos(800 - j * 40, 140).setVector(10,0).setPatterns([
                    M_Normal(mirror=True),A_Xrotate(angle=30,attackTimer=0.2,cnt=4,speed=330),M_WidthLoop_move2(mirror=True)])
                await asyncio.sleep(1)  # 1초 딜레이
        for i in range(4):
            self.enemy2Manager.getObject().setCenterPos(80 - i * 60, 340).setPatterns([M_Normal(), A_Guided(), M_WidthLoop(moveTimeValue=0.3, vector = (100,0))])
            self.enemy2Manager.getObject().setCenterPos(720 + i * 60, 340).setPatterns([M_Normal(mirror=True), A_Guided(), M_WidthLoop(moveTimeValue=0.3, vector = (100,0))])  # 1초 딜레이
        for i in range(4):
            self.enemy2Manager.getObject().setCenterPos(80 - i * 80, 400).setPatterns([M_Normal(), A_Guided(), M_WidthLoop(moveTimeValue=0.3, vector = (100,0))])
            self.enemy2Manager.getObject().setCenterPos(720 + i * 80, 400).setPatterns([M_Normal(mirror=True), A_Guided(), M_WidthLoop(moveTimeValue=0.3, vector = (100,0))])
        for i in range(2):
            self.enemy2Manager.getObject().setCenterPos(80 - i * 60, 340).setPatterns([M_Normal(), A_Guided(), M_WidthLoop(moveTimeValue=0.3, vector = (100,0))])
        self.isSpawned = True  # 생성 종료

    # 매 프레임, player와 enemy들 갱신
    def update(self, deltaTime):
        super().update(deltaTime)
        self.player.update(deltaTime)
        self.enemy1Manager.update(deltaTime)
        self.enemy2Manager.update(deltaTime)

        # 만약, 스폰이 끝났고, 활동중인 몹이 없으면, 게임 클리어
        if (self.isSpawned == True):
            activeEnemy = self.enemy1Manager.getObjectList() + self.enemy2Manager.getObjectList()
            if(activeEnemy):
                if(self.stageEndTime >= 0):
                    self.stageEndTime -= deltaTime
                else:
                    for enemy in activeEnemy:
                        if enemy.isOutsideScreen():
                            enemy.health = 1
                            enemy.hit()
            else:
                print("Stage10 Clear")
                self.isFinished = True

    # enemy들, player 간의 충돌 확인. 내부에서 enemy들의 bullet과 player, player의 bullet과 enemy들 충돌 확인함.
    def physics(self):
        self.enemy1Manager.physics([player])
        self.enemy2Manager.physics([player])

    # Stage 3의 이미지 갱신. 가지고 있는 Pool과 player에 render하면 됩니다.
    def render(self, screen):
        self.player.render(screen)
        self.enemy1Manager.render(screen)
        self.enemy2Manager.render(screen)



