from .Object import *
from .SpriteInfo import *

class Item(GameObject, ABC):
    allItems = []
    @abstractmethod
    def __init__(self, sprite: SpriteInfo, isSpawned = False, x=-500, y=-500, vectorX=0, vectorY=200, active=False):
        super().__init__(sprite, x, y, vectorX, vectorY, active)
        Item.allItems.append(self)
        self.isSpawned = isSpawned
        
    def clone(self):
        itemClone = copy.deepcopy(self)
        Item.allItems.append(itemClone)
        return itemClone
        
    def spawn(self, centerPos):
        self.setCenterPos(centerPos)
        self.active = True
        self.isSpawned = True
        print(f"spawn Item {centerPos}, {self}")

    def hit(self):
        if(self.isSpawned):
            self.active = self.isSpawned = False
            Item.allItems.remove(self)
            
    @classmethod    
    def update_all(cls, deltaTime):
        if(not cls.allItems):
            return
        
        for item in cls.allItems:
            if(item.isSpawned):
                item.update(deltaTime)
                #아이템이 완전히 밖으로 나갔을 경우
                if(item.isOutsideScreen(deltaTime)):
                    #비활성 상태로 전환
                    item.hit()
    @classmethod
    def getSpawnedItems(cls):
        return [item for item in cls.allItems if item.active and item.isSpawned]
    
    @classmethod  
    def render_all(cls, screen):
        if(not cls.allItems):
            return
        
        for item in cls.allItems:
            if(item.active):
                item.render(screen)

class ItemLife(Item):
    def __init__(self, sprite: SpriteInfo = img_life, isSpawned=False, x=-500, y=-500, vectorX=0, vectorY=200, active=False):
        super().__init__(sprite, isSpawned, x, y, vectorX, vectorY, active)
        
    def spawn(self, centerPos):
        return super().spawn(centerPos)
    
    def update(self, deltaTime):
        return super().update(deltaTime)

class ItemShield(Item):
    def __init__(self, sprite: SpriteInfo = img_shield, isSpawned=False, x=-500, y=-500, vectorX=0, vectorY=200, active=False):
        super().__init__(sprite, isSpawned, x, y, vectorX, vectorY, active)
        
    def spawn(self, centerPos):
        return super().spawn(centerPos)
    
    def update(self, deltaTime):
        return super().update(deltaTime)
    

class PlayerShield(Item):
    def __init__(self, sprite: SpriteInfo = img_playerShield, isSpawned=False, x=-500, y=-500, vectorX=0, vectorY=200, active=False):
        super().__init__(sprite, isSpawned, x, y, vectorX, vectorY, active)    
        
    def spawn(self, centerPos):
        return super().spawn(centerPos)
    
    def update(self, deltaTime):
        return super().update(deltaTime)