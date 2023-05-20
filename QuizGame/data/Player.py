import pygame

from .Bullet import *

#플레이어 클래스
class Player(GameObject):
    def __init__(self, sprite : SpriteInfo, x = 0, y = 0, velocityX = 0, velocityY = 0, active = False):
        super().__init__(sprite, x, y, velocityX, velocityY, active)
        #목숨, 현재는 사망 및 부활 구현 하지 않음.
        self.life = 5
        #키 입력 저장
        self.keylist = set()
        #
        self.hitTimer = 0
        self.attackTimer = 0
        self.bullectManager = ObjectManager(bullet2, 40)
        self.hitTimer = 0
        
    def update(self):
        if(self.hitTimer > 0):
            self.hitTimer -= 1

        if(pygame.K_LEFT in self.keylist):
           self.velocity[0] -= 5
        if(pygame.K_RIGHT in self.keylist):
           self.velocity[0] += 5
        if(pygame.K_DOWN in self.keylist):
           self.velocity[1] += 5
        if(pygame.K_UP in self.keylist):
           self.velocity[1] -= 5
        if(pygame.K_SPACE in self.keylist):
            if(self.attackTimer <= 0):
                self.attackTimer = 10
                self.attack()
        if(not self.isInsideScreen(0, self.velocity[1])):
            self.velocity[1] = 0
        if(not self.isInsideScreen(self.velocity[0], 0)):
            self.velocity[0] = 0
        
        self.sprite.addPos(self.velocity[0], self.velocity[1])

        self.velocity = [0, 0]

        if(self.attackTimer > 0):
            self.attackTimer -= 1
        self.bullectManager.update()

    def attack(self):
        self.bullectManager.getObject().setVelocity(0,-20).sprite.setPos(self.getCenterPos())

    def physics(self, otherObjectList : list[GameObject]):
        for otherObject in otherObjectList:
            if(isinstance(otherObject, Bullet)):    #불릿일 경우에만 피격 판정 확인
                if self.sprite.mask.overlap(otherObject.sprite.mask, (otherObject.sprite.x -self.sprite.x , otherObject.sprite.y - self.sprite.y)):
                    if(self.hitTimer <= 0):
                        self.hit()
                    otherObject.hit()
                    self.hitTimer = 60
                    break
            else:   #적의 충돌판정에 자신의 불릿을 넘김
                otherObject.physics(self.bullectManager.getObjectList())
    
    def hit(self):
        print("hit!")
        self.life -= 1

    def render(self, screen):
        super().render(screen)
        self.bullectManager.render(screen)


player = Player(img_player, gameSetting["width"]/2,gameSetting["height"]-100)