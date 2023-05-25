from .Object import *
from .Bullet import *
from data.Pattern import *

#적 클래스
class Enemy(GameObject):
    def __init__(self, sprite : SpriteInfo, patterns = Patterns.pattern01(), x = -500, y = -500, health = 10, attackTimer = 0.8, vectorX = 0, vectorY= 0, active = False):
        super().__init__(sprite, x, y, vectorX, vectorY, active)
        #체력 설정
        self.health = health
        #몹 패턴 설정
        self.patternManager = PatternManager(self)
        self.patternManager.setPattern(patterns)
        #공격 쿨타임
        self.attackTimer = attackTimer
        #불릿들 관리
        self.bulletManager = BulletManager(bullet1, 5)
        self.bullet2Manager = BulletManager(bullet2, 5)
        self.bullet3Manager = BulletManager(bullet3, 5)
        self.bulletManagers = [self.bulletManager , self.bullet2Manager, self.bullet3Manager]
        
        self.active = active
        
    #매 프레임 업데이트 함수
    def update(self, deltaTime):
        """자신과 소유한 불릿을 vector 만큼 이동, 패턴이 있을 경우 패턴 실행"""
        super().update(deltaTime)
        
        for bulletManager in self.bulletManagers:
           bulletManager.update(deltaTime)

        if self.patternManager is not None:
            self.patternManager.update(deltaTime)
            
    #충돌 확인 함수
    def physics(self, otherObjectList):
        for otherObject in otherObjectList:
            if(isinstance(otherObject, Bullet)):    #bullet일 경우만 피격 판정 확인
                if self.sprite.overlap(otherObject.sprite):
                    self.hit()
                    otherObject.hit()
                    break
            else:   #플레이어의 충돌판정에 불릿과 자신을 넘김.
                bullets = []
                for bulletManager in self.bulletManagers:
                    bullets += bulletManager.getObjectList()
                otherObject.physics(bullets + [self])

    #충돌 했을 때
    def hit(self):
        print("Enemy Hit!", self)
        self.health -= 1
        #체력이 없으면, 비활성 상태로 변환
        if(self.health <= 0):
            self.active = False
            #테스트용 print
            print("Enemy Died", self)
            #gif 현재 위치에 재생
            gif_Died.addDied(self.getCenterPos())
            
    #이미지 갱신
    def render(self, screen):
        super().render(screen)
        for bulletManager in self.bulletManagers:
           bulletManager.render(screen)

    #패턴 설정
    def setPatterns(self, patterns):
        self.patternManager.setPattern(patterns)
        return self
    #패턴 추가
    def addPatterns(self, pattern):
        self.patternManager.addPattern(pattern)
        return self
    #attackTimer 변경
    def setAttackTimer(self, attackTimer):
        self.attackTimer = attackTimer
        
class EnemyManager(ObjectManager):  #그냥 자동완성안되서 넣음. 그 외 ObjectManager와는 현재 차이 없음.
    def __init__(self, gameEnemyInstance: Enemy, size: int = 10) -> None:
        super().__init__(gameEnemyInstance, size)
    def getObject(self) ->Enemy:
        return super().getObject()
    

enemy1 = Enemy(img_enemys[0], Patterns.pattern01(), health=6)
enemy2 = Enemy(img_enemys[1], Patterns.pattern01(), health=3)