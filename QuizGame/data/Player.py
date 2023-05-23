import pygame

from .Bullet import *

#플레이어 클래스
class Player(GameObject):
    def __init__(self, sprite : SpriteInfo, x = 0, y = 0, vectorX = 0, vectorY = 0, active = False):
        super().__init__(sprite, x, y, vectorX, vectorY, active)
        #목숨, 현재는 사망 및 부활 구현 하지 않음.
        self.life = 5
        #키 입력 저장
        self.keylist = set()
        
        self.bullectManager = ObjectManager(bullet2, 40)
        
        self.hitCooltimeValue = 3
        self.hitCooltime = self.hitCooltimeValue
        self.attackCooltimeValue = 0.15
        self.attackCooltime = self.attackCooltimeValue
        
    def update(self, deltaTime):
        #피격 쿨타임 감소
        if(self.hitCooltime > 0):
            self.hitCooltime -= deltaTime

        #이동 키입력
        if(pygame.K_LEFT in self.keylist):
           self.vector[0] -= 350
        if(pygame.K_RIGHT in self.keylist):
           self.vector[0] += 350
        if(pygame.K_DOWN in self.keylist):
           self.vector[1] += 350
        if(pygame.K_UP in self.keylist):
           self.vector[1] -= 350
        if(pygame.K_SPACE in self.keylist):
            
            #공격 쿨타임 끝나면
            if(self.attackCooltime <= 0):
                self.attackCooltime = self.attackCooltimeValue
                self.attack()   #공격
                
        #화면 밖에 나갈 경우 이동 안 함
        if(not self.isInsideScreen(deltaTime)):
            self.vector[1] = 0
        if(not self.isInsideScreen(deltaTime)):
            self.vector[0] = 0
        
        #현재 속도만큼 이동
        super().update(deltaTime)
        
        #키입력 vector 값 초기화
        self.vector = [0, 0]

        #쿨타임 감소
        if(self.attackCooltime > 0):
            self.attackCooltime -= deltaTime
        
        #bullet 업데이트
        self.bullectManager.update(deltaTime)

    #공격
    def attack(self):
        #플레이어 중심에 위로 초당 1000픽셀 이동하는 불릿을 생성
        self.bullectManager.getObject().setVector(0,-1000).setCenterPos(self.getCenterPos())

    def physics(self, otherObjectList):
        for otherObject in otherObjectList:
            if(isinstance(otherObject, Bullet)):    #불릿일 경우에만 피격 판정 확인
                if self.sprite.overlap(otherObject.sprite):
                    if(self.hitCooltime <= 0):
                        self.hit()
                        self.hitCooltime = self.hitCooltimeValue
                    otherObject.hit()
            else:   #적의 충돌판정에 자신의 불릿을 넘김
                otherObject.physics(self.bullectManager.getObjectList())
    
    def hit(self):
        print("hit!")
        self.life -= 1

    def render(self, screen):
        super().render(screen)
        self.bullectManager.render(screen)


player = Player(img_player, gameSetting["width"]/2,gameSetting["height"]-100)