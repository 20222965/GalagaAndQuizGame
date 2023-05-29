import pygame

from .Bullet import *
from .Item import *

#플레이어 클래스
class Player(GameObject):
    def __init__(self, sprite : SpriteInfo, x = 0, y = 0, vectorX = 0, vectorY = 0, active = False):
        super().__init__(sprite, x, y, vectorX, vectorY, active)
        
        self.item = PlayerItem(self, life = 3, shield = 0)    #life, shield 저장
        self.score = 0 
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
        self.vector[0] += 350 * ((pygame.K_RIGHT in self.keylist) - (pygame.K_LEFT in self.keylist))
        self.vector[1] += 350 * ((pygame.K_DOWN in self.keylist) - (pygame.K_UP in self.keylist))
            
        if(pygame.K_SPACE in self.keylist):
            #공격 쿨타임 끝나면
            if(self.attackCooltime <= 0):
                self.attackCooltime = self.attackCooltimeValue
                self.attack()   #공격

        #화면 밖에 나갈 경우 이동 안 함
        if(not self.isInsideScreen(deltaTime, (0,self.vector[1]))):
            self.vector[1] = 0
        if(not self.isInsideScreen(deltaTime, (self.vector[0], 0))):
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
        
        
        if(pygame.K_s in self.keylist): #shield 사용
            self.item.useShield()
        self.item.update(deltaTime)
        
    #공격
    def attack(self):
        #플레이어 중심에 위로 초당 1000픽셀 이동하는 불릿을 생성
        self.bullectManager.getObject().setVector(0,-1000).setCenterPos(self.getCenterPos())

    def physics(self, otherObjectList):
        if not isinstance(otherObjectList, list):
            otherObjectList = [otherObjectList]
            
        for otherObject in otherObjectList:
            if(isinstance(otherObject, Bullet)):    #불릿일 경우에만 피격 판정 확인
                if(self.item.shield["using"]):   #shield 사용중일 경우
                    if self.item.shield["sprite"].sprite.overlap(otherObject.sprite):   #shield와 충돌판정
                        otherObject.hit()
                        
                elif self.sprite.overlap(otherObject.sprite):
                    if(self.hitCooltime <= 0):
                        self.hit()
                        self.hitCooltime = self.hitCooltimeValue
                    otherObject.hit()
                    
            elif(isinstance(otherObject, Item)):   #아이템 획득
                if self.sprite.overlap(otherObject.sprite):
                    if(isinstance(otherObject, ItemLife)):
                        #현재는 즉시 증가. 나중에 퀴즈 실행 코드로 변경되고, 거기에서 맞추면 증가될 수 있음.
                        self.item.addItem(PlayerItem.LIFE)
                        print("Life", self.item.life["count"])
                        otherObject.hit()
                    elif(isinstance(otherObject, ItemShield)):
                        self.item.addItem(PlayerItem.SHIELD)
                        print("Shield", self.item.shield["count"])
                        otherObject.hit()
                        
            else:   #적의 충돌판정에 자신의 불릿을 넘김
                otherObject.physics(self.bullectManager.getObjectList())
    
    def hit(self):
        print("hit!")
        if(self.item.life["count"] > 0):
            self.item.life["count"] -= 1

    def render(self, screen):
        self.item.render(screen)
        self.bullectManager.render(screen)
            
        super().render(screen)
        

#Player 아이템 저장
class PlayerItem:
    LIFE = 1
    SHIELD = 2
    def __init__(self, player : Player, life = 3, shield = 0):
        self.player = player
        
        self.life = {"count" : life,
                     "icon" : ItemLife(isSpawned=False,x = 100, y = 100,vectorX=0, vectorY=0, active=True)}
        
        self.shieldTimeValue = 3
        self.shield = {"count" : shield,
                       "sprite" : PlayerShield(),
                       "icon" : ItemShield(isSpawned=False, x = 200, y =  100, vectorX=0, vectorY=0, active=True),
                       "using" : False,
                       "timer" : self.shieldTimeValue}
        self.cnt = 1
        
        self.font_path = os.path.join(os.path.join(currentDir,"font"),'NanumGothic.ttf')  # 사용할 폰트 파일 경로
        self.font_size = 24  # 폰트 크기
        self.font = pygame.font.Font(self.font_path, self.font_size)    #폰트

    def addItem(self, item = LIFE, count = 1):
        if(item == PlayerItem.LIFE):
            self.life["count"] += count
        elif(item == PlayerItem.SHIELD):
            self.shield["count"] += count
            
    #shield 사용
    def useShield(self):
        if(not self.shield["using"]):
            if(self.shield["count"]):
                self.shield["count"] -= 1
                self.shield["sprite"].active = True
                self.shield["using"] = True
                print("use shield", self.shield["count"])
                
    #shield 사용 중 위치 갱신
    def update(self, deltaTime):
        if(self.cnt):
            self.cnt = 0
            self.life['icon'].setCenterPos(50, gameSetting['height'] - 50)
            self.shield['icon'].setCenterPos(150, gameSetting['height'] - 50)
                
        if(self.shield["using"]):       #shield 사용중
            if(self.shield["timer"] > 0):
                self.shield["sprite"].setCenterPos(self.player.getCenterPos())
                self.shield["timer"] -= deltaTime
            else:
                self.shield["sprite"].active = False
                self.shield["using"] = False
                self.shield["timer"] = self.shieldTimeValue
    
    #좌측 하단에 목숨, 아이템 개수 표시
    def render(self, screen : pygame.Surface):
        rendered_text = self.font.render(" X " + str(self.life['count']), True, (255, 255, 255))  #흰색 텍스트 생성
        x, y = self.life["icon"].sprite.getPos()
        screen.blit(rendered_text, (x + 25, y))  #화면에 텍스트 렌더링
        
        rendered_text = self.font.render(" X " + str(self.shield['count']), True, (255, 255, 255))  #흰색 텍스트 생성
        x, y = self.shield["icon"].sprite.getPos()
        screen.blit(rendered_text, (x + 25, y))  #화면에 텍스트 렌더링
        
    
player = Player(img_player, gameSetting["width"]/2,gameSetting["height"]-100)