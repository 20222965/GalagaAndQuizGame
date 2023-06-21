import glob
import imageio
from .Timer import *
from .GameSetting import *

#이미지 정보 저장
class SpriteInfo:
    def __init__(self, image : pygame.Surface, x = 0, y = 0):
        #이미지
        self.image = image
        #충돌 판정에 씀
        self.mask = pygame.mask.from_surface(image)
        self.position = [x, y] #좌, 상단 좌표
    
    #이미지 위치 설정
    def setPos(self, x, y = None):
        if(y is None):
            x, y = x
        self.position[0] = x
        self.position[1] = y
    #이미지 위치 이동
    def addPos(self, x, y = None):
        if(y is None):
            x, y = x
        self.position[0] += x
        self.position[1] += y

    #좌상단 좌표를 반환한다
    def getPos(self):
        return self.position[:]
    
    #두 개체 충돌 확인
    def overlap(self, otherSprite : 'SpriteInfo'):
        x, y = self.getPos()
        otherX, otherY = otherSprite.getPos()
        return self.mask.overlap(otherSprite.mask, (otherX - x , otherY - y))
    
    #이미지 화면에 그림
    def render(self, screen : pygame.Surface):
            screen.blit(self.image, self.position)

    #개체 복사용 설정
    def __deepcopy__(self, memo):
        newSprite = SpriteInfo(self.image, self.position[0], self.position[1])
        return newSprite

#이미지 생성
img_player = SpriteInfo(pygame.image.load(os.path.join(imageFolder,"player.png")).convert_alpha())



img_enemys = glob.glob(os.path.join(imageFolder, "enemy*.png"))
img_enemys = [SpriteInfo(pygame.image.load(img_enemy).convert_alpha()) for img_enemy in img_enemys]

img_bullets = glob.glob(os.path.join(imageFolder, "bullet*.png"))
img_bullets = [SpriteInfo(pygame.image.load(img_bullet).convert_alpha()) for img_bullet in img_bullets]


img_life = SpriteInfo(pygame.image.load(os.path.join(imageFolder,"life.png")).convert_alpha())
img_shield = SpriteInfo(pygame.image.load(os.path.join(imageFolder,"shield.png")).convert_alpha())


img_playerShield = SpriteInfo(pygame.image.load(os.path.join(imageFolder,"playerShield.png")).convert_alpha())

#gif 재생 부분
class Gif_Died:
    def __init__(self):
        self.diedPosAndTime = []
        # GIF의 각 프레임을 Surface의 리스트로 변환
        self.gifFrames = [pygame.Surface]
        self.gifFrames = []
        self.gif_images = imageio.mimread(os.path.join(imageFolder,"died.gif"))
        for gif_image in self.gif_images: 
            # RGB 추출
            rgb_channels = gif_image[:, :, :3]
            surface = pygame.surfarray.make_surface(rgb_channels)
            surface.set_colorkey((0, 0, 0))  # 배경을 투명하게 설정
            self.gifFrames.append(surface)
        
    #사망할 때 위치, 시간 받아서 저장    
    def addDied(self, x, y=None):
        if(y == None):
            x, y = x
        x = x - self.gifFrames[0].get_width() / 2
        y = y - self.gifFrames[0].get_height() / 2
        self.diedPosAndTime.append((x,y,Timer.getElapsedTime()))
     
    #gif 재생    
    def render(self, screen : pygame.Surface):
        if(self.diedPosAndTime):
            for x, y, time in self.diedPosAndTime:
                if(Timer.getDeltaTime(time) <= 0.0330):
                    screen.blit(self.gifFrames[0], (x,y))
                elif(Timer.getDeltaTime(time) <= 0.0330*2):
                    screen.blit(self.gifFrames[1], (x,y))
                elif(Timer.getDeltaTime(time) <= 0.0330*3):
                    screen.blit(self.gifFrames[2], (x,y))
                elif(Timer.getDeltaTime(time) <= 0.0330*4):
                    screen.blit(self.gifFrames[3], (x,y))
                elif(Timer.getDeltaTime(time) <= 0.0330*5):
                    screen.blit(self.gifFrames[4], (x,y))
                else:
                    self.diedPosAndTime.remove((x, y, time))
#인스턴스 생성
gif_Died = Gif_Died()