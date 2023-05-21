from .Object import *
from .Bullet import *
from data.Pattern import *
#github 테스트용
#적 클래스
class Enemy(GameObject):
    def __init__(self, sprite : SpriteInfo, patterns = Patterns.pattern01(), x = 0, y = 0, health = 10, attackTimer = 0.8, vectorX = 0, vectorY= 0, active = False):
        super().__init__(sprite, x, y, vectorX, vectorY, active)
        #체력 설정
        self.health = health
        #몹 패턴 설정
        self.patternManager = PatternManager(self)
        self.patternManager.setPattern(patterns)
        #공격 쿨타임
        self.attackTimer = attackTimer
        #불릿들 미리 생성
        self.bullectManager = ObjectManager(bullet1, 5)
        self.bullect2Manager = ObjectManager(bullet2, 5)
        self.bullect3Manager = ObjectManager(bullet3, 5)
        self.active = active
    #매 프레임 업데이트 함수
    def update(self):
        super().update()
        
        self.bullectManager.update()
        self.bullect2Manager.update()
        self.bullect3Manager.update()

        if self.patternManager is not None:
            self.patternManager.update()
    #충돌 확인 함수
    def physics(self, otherObjectList):
        for otherObject in otherObjectList:
            if(isinstance(otherObject, Bullet)):    #bullet일 경우만 피격 판정 확인
                if self.sprite.mask.overlap(otherObject.sprite.mask, (otherObject.sprite.x -self.sprite.x , otherObject.sprite.y - self.sprite.y)):
                    self.hit()
                    otherObject.hit()
                    break
            else:   #플레이어의 충돌판정에 불릿과 자신을 넘김.
                otherObject.physics(self.bullectManager.getObjectList() + self.bullect2Manager.getObjectList() + self.bullect3Manager.getObjectList() + [self])

    #충돌 했을 때
    def hit(self):
        print("Enemy Hit!", self)
        self.health -= 1
        #체력이 없으면, 비활성 상태로 변환
        if(self.health <= 0):
            self.active = False
            #테스트용 print
            print("Enemy Died")
            #gif 현재 위치에 재생
            gif_Died.addDied(self.getCenterPos())
    #이미지 갱신
    def render(self, screen):
        super().render(screen)
        self.bullectManager.render(screen)
        self.bullect2Manager.render(screen)
        self.bullect3Manager.render(screen)

    #패턴 설정
    def setPatterns(self, patterns):
        self.patternManager.setPattern(patterns)
        return self
    #패턴 추가
    def addPatterns(self, pattern):
        self.patternManager.addPattern(pattern)
        return self

class EnemyManager(ObjectManager):  #그냥 자동완성안되서 넣음. 그 외 ObjectManager와는 현재 차이 없음.
    def __init__(self, gameEnemyInstance: Enemy, size: int = 10) -> None:
        super().__init__(gameEnemyInstance, size)
    def getObject(self) ->Enemy:
        return super().getObject()
    

enemy1 = Enemy(img_enemy1, Patterns.pattern01(), health=6)
enemy2 = Enemy(img_enemy2, Patterns.pattern01(), health=3)