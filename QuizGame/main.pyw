from data.GameSetting import *
from data.Timer import *
from data.Stage import *

TIMER_TEXT = "Time: "
TIMER_FONT = pygame.font.Font(os.path.join(fontFolder,"CuteFont-Regular.ttf"), 48)
TIMER_COLOR = (255, 255, 255)

SCORE_TEXT = "Score: "
SCORE_FONT = pygame.font.Font(os.path.join(fontFolder, "CuteFont-Regular.ttf"), 48)
SCORE_COLOR = (255, 255, 255)

#게임루프
class GameLoop:
    def __init__(self):
        #타이머 시작
        Timer.start()
        self.preFrameTime = Timer.getElapsedTime()
        """이전 프레임 시간 저장"""
        self.timer_font = TIMER_FONT
        self.timer_color = TIMER_COLOR
        self.score_font = SCORE_FONT
        self.score_color = SCORE_COLOR
        
        self.player = player    #Player.py에서 생성한 player 객체 가져옴 선언된 위치 확인하려면 그 이름 누르고 F12 누르면 됩니다.
        self.screen = screen    #GameSetting에서 pygame 시작 후 screen 생성한 것을 가져옴.
        self.clock = clock      #프레임, 게임 루프할 때 사용
    
        self.stageManager = StageManager()  #스테이지 관리
        
        self.moveWating = False
        
        self.pageNumber = 0
        self.resultText  = Text(maxHeight=500, font=pygame.font.Font(os.path.join(fontFolder, "Maplestory Light.ttf"), 25)).setPos(150,300).setActive(False)
    def render_timer(self):
        timer_text = int(Timer.getElapsedTime())
        timer_surface = self.timer_font.render(TIMER_TEXT + str(timer_text), True, self.timer_color)
        timer_rect = timer_surface.get_rect()
        timer_rect.topleft = (10, 10)
        self.screen.blit(timer_surface, timer_rect)

    def render_score(self):
        score_text = str(self.player.score)
        
        score_surface = self.score_font.render(SCORE_TEXT + score_text, True, self.score_color)
        score_rect = score_surface.get_rect()
        score_rect.topright = (gameSetting["width"] - 10, 10)
        self.screen.blit(score_surface, score_rect)
    def render_stage(self):
        stage_surface = pygame.font.Font(os.path.join(fontFolder, "Maplestory Light.ttf"), 30).render("Stage " + str(self.stageManager.stageNumber), True, (230,230,230))
        stage_rect = stage_surface.get_rect()
        stage_rect.topright = (gameSetting["width"] - 30, gameSetting["height"] - 70)
        self.screen.blit(stage_surface, stage_rect)
            
    def playerInput(self, event):
        r = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.player.addKey(pygame.K_UP)
                r = True
            if event.key == pygame.K_DOWN:
                self.player.addKey(pygame.K_DOWN)
                r = True
            if event.key == pygame.K_LEFT:
                self.player.addKey(pygame.K_LEFT)
                r = True
            if event.key == pygame.K_RIGHT:
                self.player.addKey(pygame.K_RIGHT)
                r = True
            if event.key == pygame.K_SPACE:
                self.player.addKey(pygame.K_SPACE)
                r = True
            if event.key == pygame.K_s:
                self.player.addKey(pygame.K_s)
                r = True
        #버튼 뗌    
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                self.player.removeKey(pygame.K_UP)
                r = True
            if event.key == pygame.K_DOWN:
                self.player.removeKey(pygame.K_DOWN)
                r = True
            if event.key == pygame.K_LEFT:
                self.player.removeKey(pygame.K_LEFT)
                r = True
            if event.key == pygame.K_RIGHT:
                self.player.removeKey(pygame.K_RIGHT)
                r = True
            if event.key == pygame.K_SPACE:
                self.player.removeKey(pygame.K_SPACE)
                r = True
            if event.key == pygame.K_s:
                self.player.removeKey(pygame.K_s)   
                r = True
        
        return r
    async def pageReplace(self, number):
        if(number == 0):
            self.pageNumber = 0
            await self.titlePage()
        
        elif(number == 1):
            self.pageNumber = 1
            await self.gameLoop()
        
        elif(number == 2):
            self.pageNumber = 2
            await self.resultLoop()  
            
    def titlePage(self):
        titleNameText = Text(font=pygame.font.Font(os.path.join(fontFolder, "Maplestory Bold.ttf"), 50)).setPos(80,150).setText("3조 Galaga and Quiz Game").setSize(650,50)
        keyExplainText = Text(font=pygame.font.Font(os.path.join(fontFolder, "Maplestory Bold.ttf"), 40)).setPos(150,300).setText("\t\t  이동\t:\t방향키\n\t\t  공격\t:\tSpace\n\t\t  쉴드\t:\tS")
        startButton = Button(clickFunc=lambda:asyncio.run(self.pageReplace(1)),keyBindList=[pygame.K_SPACE], 
                             font=pygame.font.Font(os.path.join(fontFolder, "Maplestory Bold.ttf"), 20)).setPos(150,550).setText("START")
        while self.pageNumber  == 0:
            for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            quit()
                        startButton.handleEvent(event)
                        keyExplainText.handleEvent(event)
            titleNameText.render(screen)
            keyExplainText.render(screen)
            startButton.render(screen)
            pygame.display.update()
            
    def setResultText(self):
        timeText = "\n\t\t플레이 시간\t\t\t" + str(int(Timer.getElapsedTime())) + "s\n"
        scoreText = "\t\t점수   \t\t\t\t\t" + str(self.player.score) + "\n"
        hitText = "\t\t피격횟수\t\t\t\t" + str(self.player.hitCount) + "\n"
        correctText = "\t\t문제 맞힌 횟수\t\t" + str(Quiz.correctCount) + "\n"
        wrongText = "\t\t문제 틀린 횟수\t\t" + str(Quiz.wrongCount) + "\n"
        self.resultText.setText(timeText + scoreText + hitText + correctText + wrongText)
            
    async def resultLoop(self):
        resultQuizzes = [quiz for quiz in Quiz.getQuizResult() if quiz.get("wrong")]
        resultQuizzes = sorted(resultQuizzes, key=lambda quiz: quiz['wrong']-quiz["correct"])
        
        Quiz._usedQuiz += Quiz._quiz
        Quiz._quiz = []
        Quiz._quiz += resultQuizzes
        
        self.resultText.setActive(True)
        self.setResultText()
        
        quizButton = Button(clickFunc=lambda : Quiz.start(lambda: (self.player.addScore(50), self.setResultText()), lambda: (self.player.addScore(-45), self.setResultText())),
                            keyBindList=[pygame.K_SPACE]).setPos(150,640).setText("문제 풀기")
        exitButton = Button(clickFunc=quit, keyBindList=[pygame.K_ESCAPE]).setPos(150,700).setText("종료")
        while self.pageNumber == 2:
            deltaTime = Timer.getDeltaTime(self.preFrameTime)
            
            self.preFrameTime = Timer.getElapsedTime()  #이전 프레임 시간 저장
            if(Quiz.isActive):
                Quiz.update(deltaTime)
            for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()
                    elif Quiz.isActive:
                        Quiz.handleEvent(event)
                    else:
                        exitButton.handleEvent(event)
                        quizButton.handleEvent(event)
            
            self.screen.fill((0,0,0))
            if(Quiz.isActive):
                Quiz.render(screen)
            else:
                self.resultText.render(screen)
                quizButton.render(screen)
                exitButton.render(screen)
            #timer, score 표시
            self.render_timer()
            self.render_score()
            self.render_stage()
            pygame.display.update()
            
            
            await asyncio.sleep(0)  # 비동기 함수
            
    async def gameLoop(self):
        self.stageManager.start()
        Quiz.filterQuiz(Quiz._filterType)
        while self.pageNumber == 1:
            if GameSetting.gameOver:
                await self.pageReplace(2)
                
            #현재 프레임과 이전 프레임의 시간 차
            deltaTime = Timer.getDeltaTime(self.preFrameTime)
            
            self.preFrameTime = Timer.getElapsedTime()  #이전 프레임 시간 저장
            
            #입력
            if(Quiz.isActive and self.moveWating == False):
                self.moveWating = True
            if(Quiz.isActive):
                Quiz.update(deltaTime)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()
                    Quiz.handleEvent(event)
                    self.playerInput(event)
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()
                    if(self.playerInput(event) and self.moveWating == True):
                        self.moveWating = False
                            
                        
            #화면 초기화.
            self.screen.fill((0,0,0))
            
            #timer, score 표시
            self.render_timer()
            self.render_score()
            self.render_stage()
            
            if(self.moveWating == False):        
                self.stageManager.update(deltaTime)
                Item.update_all(deltaTime)
                
                self.stageManager.physics()
                self.player.physics(Item.getSpawnedItems())
            
            self.stageManager.render(screen)  
        
            gif_Died.render(screen)
            
            Item.render_all(screen) 
            
            if(Quiz.isActive):
                Quiz.render(screen)
            #이미지 전체 업데이트
            pygame.display.update()
            self.clock.tick(gameSetting["fps"]) #게임 루프 속도를 gameSetting["fps"]만큼 제한.
            
            await asyncio.sleep(0)  # 비동기 함수

def main():
    game = GameLoop()
    game.titlePage()

main()