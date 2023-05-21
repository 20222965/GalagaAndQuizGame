import math
from .Object import *

#불릿
class Bullet(GameObject):
    def __init__(self, sprite : SpriteInfo, x = 0, y = 0, vectorX = 0, vectorY = 4, active = False):
        super().__init__(sprite, x, y, vectorX, vectorY, active)
        self.angle = 0
    #매 프레임 갱신
    def update(self):
        super().update()
        
        #현재 속도만큼 x,y 이동
        self.sprite.addPos(self.vector)
        
        #불릿이 완전히 밖으로 나갔을 경우
        if(self.isOutsideScreen()):
            #바활성 상태로 전환
            self.active = False
            return
        
        #생성할 때 이미지 각도에 맞춰 회전함.    
        preAngle = self.angle
        self.angle = math.atan2(-self.vector[0], -self.vector[1])
        if(math.isclose(self.angle, preAngle)):
            return;
        
        rotation_angle = math.degrees(self.angle - preAngle)
        self.sprite.image = pygame.transform.rotate(self.sprite.image, rotation_angle)

    def render(self, screen):
        return super().render(screen)
    def hit(self):
        self.active = False
        print("Bullet Hit!", self)
        

bullet1 = Bullet(img_bullet1)
bullet2 = Bullet(img_bullet2)
bullet3 = Bullet(img_bullet3)