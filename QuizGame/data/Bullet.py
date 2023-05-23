import math
from .Object import *

#불릿
class Bullet(GameObject):
    def __init__(self, sprite : SpriteInfo, x = -500, y = -500, vectorX = 0, vectorY = 240, active = False):
        super().__init__(sprite, x, y, vectorX, vectorY, active)
        self.angle = 0
        self.__sprite = None
    #매 프레임 갱신
    def update(self, deltaTime):
        """vector만큼 움직이며, 가속도만큼 vector의 크기가 증가한다"""
        super().update(deltaTime)

        #불릿이 완전히 밖으로 나갔을 경우
        if(self.isOutsideScreen(deltaTime)):
            #비활성 상태로 전환
            if(self.__sprite):
                self.sprite = copy.deepcopy(self.__sprite)
                self.angle = 0
                self.__sprite = None
            self.active = False
            return
        
    def setVector(self, vectorX, vectorY=None):
        """현재 Vector 설정 (1초당 움직이는 픽셀)"""
        super().setVector(vectorX, vectorY)
        
        #vector 방향에 맞춰 이미지를 회전함.
        preAngle = self.angle
        self.angle = math.degrees(math.atan2(-self.vector[0], -self.vector[1]))
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
        print("Bullet Hit!", self)
        
    def __rotateSprite(self):
        if math.isclose(0, self.angle):
            if(self.__sprite):
                x, y = self.sprite.getPos()
                self.sprite = copy.deepcopy(self.__sprite)
                self.sprite.setPos(x, y)
                self.__sprite = None
            return self
        x, y = self.sprite.getPos()
        if(not self.__sprite):
            self.__sprite = copy.deepcopy(self.sprite)
            self.sprite = SpriteInfo(pygame.transform.rotate(self.sprite.image, self.angle), x, y)
        else:
            self.sprite = SpriteInfo(pygame.transform.rotate(self.__sprite.image, self.angle), x, y) 
            
bullet1 = Bullet(img_bullet1)
bullet2 = Bullet(img_bullet2)
bullet3 = Bullet(img_bullet3)