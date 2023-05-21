from abc import ABC, abstractmethod
import copy

from .GameSetting import *
from .SpriteInfo import *

#게임 오브젝트
class GameObject(ABC):
    def __init__(self, sprite : SpriteInfo, x, y, vectorX, vectorY, active = False):
        self.sprite = sprite
        self.sprite.setPos(x, y)
        self.vector = [vectorX, vectorY]
        self.active = active

    #속도 설정
    def setVector(self, vectorX, vectorY = None):
        if(vectorY is None):
            vectorX, vectorY = vectorX
        self.vector = [vectorX, vectorY]
        
        return self
    
    #중심 좌표로 개체 위치 설정
    def setCenterPos(self, x, y = None):
        if(y is None):
            x, y = x
        #이미지는 좌상단 좌표를 쓰기 때문에 변환해서 설정
        self.sprite.setPos(self._fromCenterXY(x,y))
        
        return self
    #중심 좌표 반환    
    def getCenterPos(self):
        #이미지는 좌상단 좌표를 쓰기 때문에 변환해서 반환
        return self._toCenterXY(self.sprite.getPos())
    
    #현재 X, Y 속도로 움직임
    def move(self):
        self.sprite.addPos(self.vector)

    #개체 갱신
    @abstractmethod
    def update(self):
        pass
    
    #개체 충돌했을 때 호출
    @abstractmethod
    def hit(self):
        pass
    #개체 이미지 갱신    
    def render(self, screen):
        self.sprite.render(screen)

    #개체가 완전히 밖으로 나가면 True 반환
    def isOutsideScreen(self, addX = [0, 0], addY : int = None, screenWidth=gameSetting["width"], screenHeight=gameSetting["height"]):
        if(addY is None):
            addX, addY = addX
        x = self.sprite.x + addX
        y = self.sprite.y + addY

        if x + self.sprite.image.get_width() < 0 or x > screenWidth:
            return True
        if y + self.sprite.image.get_height() < 0 or y > screenHeight:
            return True
        return False
    #개체가 완전히 안에 있으면 True 반환        
    def isInsideScreen(self, addX : int = 0, addY : int = 0, screenWidth=gameSetting["width"], screenHeight=gameSetting["height"]):
        x = self.sprite.x + addX
        y = self.sprite.y + addY

        if x + addX > 0 and x + self.sprite.image.get_width() + addX < screenWidth:
            if y + addY > 0 and y + self.sprite.image.get_height() + addY < screenHeight:
                return True
        return False
    
    #좌상단(이미지) 좌표를 중심 좌표로 변환해서 반환 
    def _toCenterXY(self, x, y = None):
        if(y is None):
            x, y = x
        center_x = x + self.sprite.image.get_width() / 2
        center_y = y + self.sprite.image.get_height() / 2
        return center_x, center_y
    #중심 좌표를 좌상단(이미지) 좌표로 변환해서 반환
    def _fromCenterXY(self, center_x, center_y = None):
        if(center_y is None):
            center_x, center_y = center_x
        x = center_x - self.sprite.image.get_width() / 2
        y = center_y - self.sprite.image.get_height() / 2
        return x, y
 
 #개체 관리 (생성 및 반환, 활동중인 개체 업데이트, 충돌판정, 렌더링)   
class ObjectManager:
    def __init__(self, gameObjectInstance : GameObject, size : int = 10) -> None:
        self.object = gameObjectInstance    #개체 종류 저장
        self.activeObjects = [self.object]  #활동중인 개체, 지금 값은 의미 없는 자동완성용, 다시 []로 초기화.
        self.activeObjects = []
        #입력받은 개체를 입력받은 크기만큼 복사하여 미리 생성
        self.inactiveObjects = [copy.deepcopy(self.object) for _ in range(size)]

    #개체 반환
    def getObject(self):
        if self.inactiveObjects:
            # 개체에 비활성 개체가 있는 경우
            obj = self.inactiveObjects.pop()
            obj.active = True   #활성 상태로 만들고
            self.activeObjects.append(obj)
            return obj  #개체 반환
        else:
            # 개체에 비활성 개체가 없는 경우, 새로운 개체 생성
            obj = copy.deepcopy(self.object)
            obj.active = True   #활성 상태로 만들고   
            self.activeObjects.append(obj)
            return obj  #개체 반환
    
    #비활성 개체 리스트로 옮기는 함수    
    def releaseObject(self, obj):
        if obj in self.activeObjects:   #입력받은 개체가 활성 개체 리스트에 있으면
            # 활성 개체를 비활성 상태로 변경
            obj.active = False
            self.activeObjects.remove(obj)
            self.inactiveObjects.append(obj)
            
    #개체 리스트 반환 (physics에서 사용)
    def getObjectList(self):
        return [obj for obj in self.activeObjects]
    
    #개체 매 프레임 갱신
    def update(self):
        for obj in self.activeObjects:  #활성 개체 순환하여 갱신
            obj.update()
            if obj.active == False:     #만약 비활성 상태로 된 개체가 있으면
                self.releaseObject(obj) #비활성 개체 리스트에 저장
                return

    #개체 충돌 판정 확인
    def physics(self, otherObjectList):
        for obj in self.activeObjects:
            obj.physics(otherObjectList)
    #개체 이미지 갱신
    def render(self, screen):
        for obj in self.activeObjects:
            obj.render(screen)
