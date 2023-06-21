from .Object import *

#불릿
class Bullet(GameObject):
    def __init__(self, sprite : SpriteInfo, x = -500, y = -500, vectorX = 0, vectorY = 240, canRotate = True, active = False):
        super().__init__(sprite, x, y, vectorX, vectorY, active)
        self.angle = 0
        self.canRotate = canRotate
        if(self.canRotate):
            self.__sprite = self.sprite
    #매 프레임 갱신
    def update(self, deltaTime):
        """vector만큼 움직이며, 가속도만큼 vector의 크기가 증가한다"""
        super().update(deltaTime)

        #불릿이 완전히 밖으로 나갔을 경우
        if(self.isOutsideScreen(deltaTime)):
            #비활성 상태로 전환
            if(self.canRotate):
                self.sprite = self.__sprite
            self.sprite.setPos(-500,-500)
            self.active = False
            return
        
    def setVector(self, vectorX, vectorY=None):
        """현재 Vector 설정 (1초당 움직이는 픽셀)"""
        
        
        preAngle = self.angle
        super().setVector(vectorX, vectorY)
        
        #vector 방향에 맞춰 이미지를 회전함.
        if math.isclose(preAngle, self.angle):
            return self
        
        self.__rotateSprite()
        return self

    def setAngleSpeed(self, angle, speed):
        preAngle = self.angle #이전 각도 저장
        super().setAngleSpeed(angle, speed) #angle각도와 speed 크기로 vector 설정
        if not math.isclose(preAngle, self.angle): #이전과 이후 각도가 같지 않을 경우
            self.__rotateSprite()   #이미지 회전
        return self
        
        
    def render(self, screen):
        super().render(screen)
        
    def hit(self):
        self.active = False
        
    def __rotateSprite(self):
        if(not self.canRotate):
            return
        x, y = self.sprite.getPos()
        if math.isclose(0, self.angle):
            self.__sprite.setPos(x, y)
            self.sprite = self.__sprite
            return
        self.sprite = SpriteInfo(pygame.transform.rotate(self.__sprite.image, self.angle), x, y)




class BulletManager(ObjectManager):
    def __init__(self, gameObjectInstance : Bullet, size: int = 10) -> None:
        super().__init__(gameObjectInstance, size)
    
    def getObject(self, canRotate = True) -> Bullet:
        bullet = self.__get()
        bullet.canRotate = canRotate
        return bullet
    def __get(self) -> Bullet:
        return super().getObject()    
            
bullet1 = Bullet(img_bullets[0])
bullet2 = Bullet(img_bullets[1])
bullet3 = Bullet(img_bullets[2])
bullet4 = Bullet(img_bullets[3])
bullets = [Bullet(img_bullet) for img_bullet in img_bullets]
bullets[3].canRotate = False
bullets[4].canRotate = False