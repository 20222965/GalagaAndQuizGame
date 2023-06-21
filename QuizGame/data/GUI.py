from .GameSetting import *

class Widget(ABC):
    @abstractmethod
    def __init__(self, leftX, topY, width, height, border, text : str, font : pygame.font.Font, fontColor : tuple, widgetColor : tuple, callbackFunc, isActive = True) -> None:
        self.isActive = isActive
        
        self.rect = pygame.Rect(leftX, topY, width, height)
        self.border = border
        
        self.text = text.replace("\t", "    ")
        
        self.font = font
        self.fontColor = fontColor
        self.fontHeight = self.font.get_height()
        
        self.widgetColor = widgetColor
        
        self.callbackFunc = callbackFunc
        
        pass
    
    def setPos(self, leftX, topY = None):
        if(topY == None):
            leftX, topY = leftX
        self.rect.x, self.rect.y = leftX, topY
        return self
    
    def setSize(self, width, height):
        self.rect.width, self.rect.height = width, height
        return self
        
    def setText(self, text : str):
        if(text):
            self.text = text.replace("\t", "    ")
        else:
            self.text = ""
        return self
    
    def setActive(self, isActive):
        self.isActive = isActive 
        return self
    
    def setCallbackFunc(self, callbackFunc):
        self.callbackFunc = callbackFunc
        return self
        
    def getText(self):
        return self.text
    
    def getPos(self):
        return self.rect.x, self.rect.y
    
    @abstractmethod
    def render(self, screen : pygame.Surface):
        pass
    
    @abstractmethod
    def handleEvent(self, event : pygame.event.Event):
        pass
        
class Button(Widget):
    def __init__(self, leftX = 0, topY = 0, width = 500, height = 50, border = 20, text = "",
                 font = pygame.font.Font(os.path.join(fontFolder, "Maplestory Light.ttf"), 17), fontColor = (200, 200, 200),
                 widgetColor = (31, 31, 31), hoverColor = (157,216,75), hoverFontColor = (0,0,0), keyBindList : list = [], clickFunc = None, isActive = True) -> None:
        super().__init__(leftX, topY, width, height, border, text, font, fontColor, widgetColor, callbackFunc = clickFunc, isActive = isActive)
        self.hoverColor = hoverColor
        self.hoverFontColor = hoverFontColor
        self.keyBindList = keyBindList
        
        self.click = False
        
    def render(self, screen : pygame.Surface):
        if self.isActive:
            ishovering = self.rect.collidepoint(pygame.mouse.get_pos())
            widgetColor = self.hoverColor if ishovering else self.widgetColor
            fontColor = self.hoverFontColor if ishovering else self.fontColor
            pygame.draw.rect(screen, widgetColor, self.rect, border_radius=self.border)
            lines = self.text.split('\n')
            for i, line in enumerate(lines):
                if self.keyBindList and i == 0:
                    keys = ""
                    for key in self.keyBindList:
                        keys += "[" + pygame.key.name(key) + "]"
                    keys += " "
                    textSurface = self.font.render(keys + line, True, fontColor)
                else:
                    textSurface = self.font.render(line, True, fontColor)
                textRect = textSurface.get_rect(center=self.rect.center, y = self.rect.y + (self.rect.height - self.fontHeight)/2 if i == 0 else self.rect.y + i * self.fontHeight)
                screen.blit(textSurface, textRect)
        
    def handleEvent(self, event : pygame.event.Event):
        if self.isActive:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.click = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.rect.collidepoint(event.pos):
                    if self.callbackFunc:
                        self.callbackFunc()
                else:
                    self.click = False
                        
            elif event.type == pygame.KEYDOWN:
                if event.key in self.keyBindList:
                    if self.callbackFunc:
                        self.callbackFunc()
        
class Text(Widget):
    #스크롤 기능 추가해야 됨
    def __init__(self, leftX = 0, topY = 0, width = 500, height = 50, maxHeight = 180, border = 5, text = "", 
                 font = pygame.font.Font(os.path.join(fontFolder, "Maplestory Light.ttf"), 17), fontColor = (200, 200, 200),
                 widgetColor = (31, 31, 31), enterFunc = None,  isActive = True, isInputActive = False) -> None:
        super().__init__(leftX, topY, width, height, border, text, font, fontColor, widgetColor, callbackFunc= enterFunc, isActive= isActive)
        self.isInputActive = isInputActive
        self.cursorIndex = 0
        
        self.preEditingText = ''
        self.maxHeight = maxHeight
        
        self.scrollX = 0
        self.scrollY = 0
        self.maxY =  self.maxHeight // self.fontHeight
        self.scrollbarRange = None
        self.scrollSize = None
        self.scrollbar = None
        self.drawRect = self.rect
        self.textSurfaces = []
    
    def setPos(self, leftX, topY=None):
        super().setPos(leftX, topY)
        self.setTextSurface()
        
        return self
    def setSize(self, width, height):
        super().setSize(width, height)
        self.setTextSurface()
        return self
    def setText(self, text: str):
        super().setText(text)
        
        
        self.scrollX = 0
        self.scrollY = 0
        self.setTextSurface()
            
        return self 
    def setTextSurface(self):
        self.drawRect = self.rect
        self.textSurfaces = []
        lines = self.text.split('\n')
        if(len(lines) * self.fontHeight > self.rect.height):
            if(len(lines) * self.fontHeight + 5 >= self.maxHeight):
                self.drawRect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.maxHeight)
            else:
                self.drawRect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, len(lines) * self.fontHeight + 5)
            
            for i, line in enumerate(lines):
                textSurface = self.font.render(line, True, self.fontColor)
                self.textSurfaces.append(textSurface)
                
        else:  
            for i, line in enumerate(lines):
                textSurface = self.font.render(line, True, self.fontColor)
                self.textSurfaces.append(textSurface)
        
        self.setScrollbar()
        
    def setScrollbar(self):
        self.scrollbar = self.scrollSize = self.scrollbarRange = None
        if(self.maxY < len(self.textSurfaces)):
            self.scrollbarRange = pygame.Rect(self.drawRect.x - 10, self.drawRect.y, 10, self.drawRect.height)
            self.scrollSize = self.drawRect.height / (len(self.textSurfaces) - self.maxY + 1)
            self.scrollbar = pygame.Rect(self.drawRect.x - 10, self.drawRect.y + self.scrollY * self.scrollSize, 10, self.scrollSize)
            
    def render(self, screen : pygame.Surface):
        if self.isActive:
            pygame.draw.rect(screen, self.widgetColor, self.drawRect, border_radius=self.border)
            for i, textSurface in enumerate(self.textSurfaces[self.scrollY : self.scrollY + self.maxY]):
                screen.blit(textSurface, textSurface.get_rect(x=self.drawRect.x + 5, y=self.drawRect.y + i * self.fontHeight))
            
            if(self.scrollbar):
                pygame.draw.rect(screen, (80, 80, 80), self.scrollbarRange)
                pygame.draw.rect(screen, (47, 49, 51), self.scrollbar)
                
            # 커서를 표시하는 부분
            if self.isInputActive:
                cursorLines = self.text[:self.cursorIndex].split('\n')
                cursorY = self.rect.y + (len(cursorLines)-1) * self.fontHeight
                cursorX = self.rect.x + 5 + self.font.size(cursorLines[-1])[0]
                cursorHeight = self.fontHeight
                pygame.draw.line(screen, (230, 230, 230), (cursorX, cursorY), (cursorX, cursorY + cursorHeight - self.scrollY))
    
    def scrollMoveUp(self, moveUp):
        if moveUp:
            if self.scrollY > 0:
                self.scrollY -= 1
                self.setScrollbar()
        elif len(self.textSurfaces) > self.maxY + self.scrollY:
            self.scrollY += 1
            self.setScrollbar()
                        
    def handleEvent(self, event : pygame.event.Event):
        if self.isActive:
            if event.type == pygame.MOUSEBUTTONDOWN and self.drawRect.collidepoint(event.pos):
                if event.button == 4:
                    self.scrollMoveUp(True)
                elif event.button == 5:
                    self.scrollMoveUp(False)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.scrollMoveUp(True)
                elif event.key == pygame.K_DOWN:
                    self.scrollMoveUp(False)
                    
            if self.isInputActive:
                character = ''
                mods = pygame.key.get_mods()
                if event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN) and not (mods & pygame.KMOD_SHIFT): #엔터 (입력 종료)
                        self.callbackFunc()
                        self.cursorIndex = 0
                        self.setText('')
                        self.setTextSurface()
                        return
                    
                    if event.key == pygame.K_BACKSPACE:  # 백스페이스 키 입력 처리
                        if self.cursorIndex > 0:
                            self.text = self.text[:self.cursorIndex-1] + self.text[self.cursorIndex:]
                            self.cursorIndex -= 1
                            self.setTextSurface()
                    elif event.key == pygame.K_DELETE:  # 삭제 키 입력 처리
                        if self.cursorIndex < len(self.text):
                            self.text = self.text[:self.cursorIndex] + self.text[self.cursorIndex+1:]
                            self.setTextSurface()
                            
                    elif event.key == pygame.K_LEFT:  # 왼쪽 방향키 입력 처리
                        if self.cursorIndex > 0:
                            self.cursorIndex -= 1
                    elif event.key == pygame.K_RIGHT:  # 오른쪽 방향키 입력 처리
                        if self.cursorIndex < len(self.text):
                            self.cursorIndex += 1
                    
                    elif event.key == pygame.K_HOME:  # Home 키 입력 처리
                        self.cursorIndex = 0
                    elif event.key == pygame.K_END:  # End 키 입력 처리
                        self.cursorIndex = len(self.text)
                    
                    elif mods & pygame.KMOD_ALT and event.key == pygame.K_TAB:
                        return    
                    elif(mods & pygame.KMOD_SHIFT and (event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN)):
                        character = '\n'
                    elif(event.key == pygame.K_TAB):
                        character = "    "
                    if(character != ''):   
                        self.text = self.text[: self.cursorIndex] + character + self.text[self.cursorIndex :]
                        self.cursorIndex += len(character)
                        self.setTextSurface()   
                             
                elif event.type == pygame.TEXTEDITING:   #텍스트 입력
                    character = event.text
                    if(self.preEditingText != '' and character != ''):
                        self.text = self.text[: self.cursorIndex - len(self.preEditingText)] + character + self.text[self.cursorIndex :]
                        self.cursorIndex += len(character) - len(self.preEditingText)
                        self.setTextSurface()
                    elif(self.preEditingText != '' and character == ''):
                        self.text = self.text[:self.cursorIndex - len(self.preEditingText)] + self.text[self.cursorIndex:]
                        self.cursorIndex -= len(self.preEditingText)
                        self.setTextSurface()
                    elif(self.preEditingText == '' and character != ''):
                        self.text = self.text[:self.cursorIndex] + character + self.text[self.cursorIndex:]
                        self.cursorIndex += len(character)
                        self.setTextSurface()
                    self.preEditingText = character
                elif event.type == pygame.TEXTINPUT and self.preEditingText == '':
                    character = event.text
                    self.text = self.text[:self.cursorIndex] + character + self.text[self.cursorIndex:]
                    self.cursorIndex += len(character)
                    self.setTextSurface()
                    
        