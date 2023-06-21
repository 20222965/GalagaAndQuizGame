from .Bullet import *
from .Item import *
from .Quiz import *

#플레이어 클래스
class Player(GameObject):
    def __init__(self, sprite : SpriteInfo, x = 0, y = 0, vectorX = 0, vectorY = 0, active = False):
        super().__init__(sprite, x, y, vectorX, vectorY, active)
        self.isActive = True
        self.item = PlayerItem(self, life = 3, shield = 0)    #life, shield 저장
        self.score = 0 
        #키 입력 저장
        self.keylist = set()
        
        self.bullectManager = ObjectManager(bullets[1], 20)
        
        self.hitCooltimeValue = 3
        self.hitCooltime = self.hitCooltimeValue
        self.attackCooltimeValue = 0.15
        self.attackCooltime = self.attackCooltimeValue
        
        self.hitCount = 0
    def removeKey(self, key):
        if key in self.keylist:
            self.keylist.remove(key)
    def addKey(self, key):
        if key not in self.keylist:
            self.keylist.add(key)    
    def addScore(self, score = 50):
        self.score += score         
    def update(self, deltaTime):
        if(self.isActive):
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
        if(not self.isActive):
            return
        if not isinstance(otherObjectList, list):
            otherObjectList = [otherObjectList]
            
        for otherObject in otherObjectList:
            if(isinstance(otherObject, Bullet)):    #불릿일 경우에만 피격 판정 확인
                if(self.item.isUsing(PlayerItem.SHIELD)):   #shield 사용중일 경우
                    if self.item.overlap(PlayerItem.SHIELD, otherObject):   #shield와 충돌판정
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
                        otherObject.hit()
                        Quiz.start(lambda: (self.addScore(50), self.item.addItem(PlayerItem.LIFE)), lambda:self.addScore(-45))
                        print("Life", self.item.getItemCount(PlayerItem.LIFE))
                        
                    elif(isinstance(otherObject, ItemShield)):
                        otherObject.hit()
                        Quiz.start(lambda: (self.addScore(50), self.item.addItem(PlayerItem.SHIELD)), lambda:self.addScore(-45))
                        print("Shield", self.item.getItemCount(PlayerItem.SHIELD))
                        
            else:   #적의 충돌판정에 자신의 불릿을 넘김
                otherObject.physics(self.bullectManager.getObjectList())
    
    def hit(self):
        print("hit!")
        self.hitCount += 1
        if(self.item.getItemCount(PlayerItem.LIFE) > 0):
            self.item.addItem(PlayerItem.LIFE, -1)
        gif_Died.addDied(self.getCenterPos())
        self.isActive = False
        asyncio.create_task(self.died())
        
    async def died(self):
        if(self.item.getItemCount(PlayerItem.LIFE)):
            await asyncio.sleep(2)
            self.isActive = True
            self.setCenterPos(gameSetting["width"]/2,gameSetting["height"]-100)
            self.item.addItem(PlayerItem.SHIELD)
            self.item.useShield()
            self.bullectManager = ObjectManager(bullets[1], 20)
        
        else:
            GameSetting.gameOver = True

    def render(self, screen):
        self.item.render(screen)
        if(not self.isActive):
            return    
        self.bullectManager.render(screen)
        super().render(screen)
        

#Player 아이템 저장
class PlayerItem:
    LIFE = 0
    SHIELD = 1
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
        
        self.item = [self.life, self.shield]
        
        self.font_path = os.path.join(os.path.join(currentDir,"font"),'NanumGothic.ttf')  # 사용할 폰트 파일 경로
        self.font_size = 24  # 폰트 크기
        self.font = pygame.font.Font(self.font_path, self.font_size)    #폰트

    def addItem(self, item = LIFE, count = 1):
        """item : PlayerItem.LIFE, PlayerItem.SHIELD 등"""
        self.item[item]["count"] += count
            
    def getItemCount(self, item = LIFE):
        """item : PlayerItem.LIFE, PlayerItem.SHIELD 등"""
        return self.item[item]["count"]
            
    #shield 사용
    def useShield(self):
        if(not self.item[PlayerItem.SHIELD]["using"]):
            if(self.item[PlayerItem.SHIELD]["count"]):
                self.item[PlayerItem.SHIELD]["count"] -= 1
                self.item[PlayerItem.SHIELD]["sprite"].active = True
                self.item[PlayerItem.SHIELD]["using"] = True
                print("use shield", self.item[PlayerItem.SHIELD]["count"])
    
    def isUsing(self, item = SHIELD):
        """item : PlayerItem.SHIELD"""
        if(self.item[item].get("using")):
            return True
        else:
            return False
    
    def overlap(self, item, otherObject : GameObject):
        """item : PlayerItem.SHIELD"""
        if(self.item[item].get("sprite")):
            return self.item[item]["sprite"].sprite.overlap(otherObject.sprite)
        return False
            
    #shield 사용 중 위치 갱신
    def update(self, deltaTime):
        self.item[PlayerItem.LIFE]['icon'].setCenterPos(50, gameSetting['height'] - 50)
        self.item[PlayerItem.SHIELD]['icon'].setCenterPos(150, gameSetting['height'] - 50)
                
        if(self.item[PlayerItem.SHIELD]["using"]):       #shield 사용중
            if(self.item[PlayerItem.SHIELD]["timer"] > 0):
                self.item[PlayerItem.SHIELD]["sprite"].setCenterPos(self.player.getCenterPos())
                self.item[PlayerItem.SHIELD]["timer"] -= deltaTime
            else:
                self.item[PlayerItem.SHIELD]["sprite"].active = False
                self.item[PlayerItem.SHIELD]["using"] = False
                self.item[PlayerItem.SHIELD]["timer"] = self.shieldTimeValue
    
    #좌측 하단에 목숨, 아이템 개수 표시
    def render(self, screen : pygame.Surface):
        rendered_text = self.font.render(" X " + str(self.item[PlayerItem.LIFE]['count']), True, (255, 255, 255))  #흰색 텍스트 생성
        x, y = self.item[PlayerItem.LIFE]["icon"].sprite.getPos()
        screen.blit(rendered_text, (x + 25, y))  #화면에 텍스트 렌더링
        
        rendered_text = self.font.render(" X " + str(self.item[PlayerItem.SHIELD]['count']), True, (255, 255, 255))  #흰색 텍스트 생성
        x, y = self.item[PlayerItem.SHIELD]["icon"].sprite.getPos()
        screen.blit(rendered_text, (x + 25, y))  #화면에 텍스트 렌더링
        
    
player = Player(img_player, gameSetting["width"]/2,gameSetting["height"]-100)