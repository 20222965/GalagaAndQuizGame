from .GUI import *

class QuizType(IntFlag):
    선다형 = auto()
    단답형 = auto()
    Python = auto()

    def ALL():
        qtype = 0
        for t in QuizType.__members__:
            qtype  |= QuizType[t]
        return qtype
    @classmethod
    def addFlag(cls, name):
        if name in cls.__members__:
            return cls[name]

        value = 1 << len(cls.__members__)
        newFlag = cls(value)
        newFlag._name_ = name
        cls._member_names_.append(name)
        cls._member_map_[name] = newFlag
        return newFlag

class Quiz:
    isActive = False
    timerValue = 30
    timer = timerValue
    @classmethod
    def start(cls, donFunc , wrongFunc = None):
        if(cls.isActive):
            return
        cls.isActive = True
        cls.timer = cls.timerValue
        cls.__timerText.setActive(True)
        cls._doneFunc = donFunc
        cls._wrongFunc = wrongFunc
        cls._nextQuiz()
          
    @classmethod
    def handleEvent(cls, event):
        for widget in cls._widgets:
            widget.handleEvent(event)    
    
    @classmethod
    def update(cls, deltaTime):
        if(cls.task == None):
            if(cls.timer > 0):
                cls.timer -= deltaTime
            else:
                cls.timer = 0
                cls.task = asyncio.create_task(cls.__wrong(cls,"0")) 
        cls.__timerText.setText(str(int(cls.timer*10)/10) + "초")  
    @classmethod
    def render(cls, screen):
        if(cls.isActive):
            pygame.draw.rect(screen, (10, 10, 10), (100, 180, 600, 740), border_radius=5)
            for widget in cls._widgets:
                widget.render(screen)
                
            # cls._questionText.render(screen)
            
            # if(cls._currentQuiz.get("code")):
            #     cls._codeText.render(screen)
                
            # if(cls._currentQuiz.get("type") & QuizType.선다형):
            #     for button in cls._option:
            #         button.render(screen)
            # elif(cls._currentQuiz.get("type") & QuizType.단답형):
            #     cls._answerText.render(screen)
                
    @classmethod
    def getQuizResult(cls):
        result = []
        for quiz in cls._quiz + cls._usedQuiz + cls._filteredQuiz:
            if quiz.get("wrong") or quiz.get("correct"):
                result.append(quiz)
        for re in result:
            if(re.get("wrong") is None):
                re["wrong"] = 0
            if(re.get("correct") is None):
                re["correct"] = 0
        result = sorted(result, key=lambda x: x["wrong"], reverse=True)
        return result
    
    @classmethod    
    def filterQuiz(cls, quizType : QuizType = QuizType.ALL()):
        """이 타입이 없는 퀴즈를 모두 제거한다.\n
        quizType = QuizType.선다형일 경우, QuizType.선다형이 없는 퀴즈를 제거한다."""
        
        #이전 필터 초기화
        cls._quiz += cls._filteredQuiz
        cls._filteredQuiz = []
        #퀴즈에서 해당 타입이 있는 것을 저장한다.
        filter = [quiz for quiz in cls._quiz if quiz["type"] & quizType == quiz["type"]]
        #퀴즈에서 해당 타입이 없으면, quiz에서 _filteredQuiz로 옮긴다.
        cls._filteredQuiz.extend([quiz for quiz in cls._quiz if quiz not in filter])
        #self.quiz에 해당 타입이 있는 퀴즈만 남긴다.
        cls._quiz = filter
        
    @classmethod
    def _checkAnswer(cls, option : str, guiname : str):
        if(cls.task):
            return
        
        #입력값 공백 제거(오류방지)
        cleanedAnswer = re.sub(r'\s+', '', cls._currentQuiz['answer'])
        cleanedOption = re.sub(r'\s+', '', option)
        #테스트용, 나중에 제거
        print(f"checkAnswer호출 option 값 : {option}, answer 값 : {cls._currentQuiz['answer']}\n정답 확인 : {cls._currentQuiz['answer'] == option}")
        print(f"2차 확인 option 값 : {cleanedOption}, answer 값 : {cleanedAnswer}\n정답 확인 : {cleanedAnswer == cleanedOption}")

        if(cleanedAnswer == cleanedOption):
            cls.task = asyncio.create_task(cls.__correct(cls,guiname))
        else:
            cls.task = asyncio.create_task(cls.__wrong(cls,guiname))
            
    async def __correct(cls, guiname : str):
        if cls._currentQuiz["type"] & QuizType.선다형:
            optionIndex = int(guiname[-1])
            cls.__correctOption.setPos(cls._option[optionIndex].getPos()).setText(cls._option[optionIndex].getText()).isActive = True
        elif cls._currentQuiz["type"] & QuizType.단답형:
            cls.__correctText.setPos(cls._answerText.getPos()).setText(cls._currentQuiz['answer']).isActive = True
        #정답 카운트 +1,
        cls.correctCount += 1
        if cls._currentQuiz.get("correct"):
            cls._currentQuiz["correct"] += 1
        else:
            cls._currentQuiz["correct"] = 1
            
        await asyncio.sleep(1)    #1초 딜레이
        cls.__correctText.isActive = cls.__correctOption.isActive = False
        cls.task = None
        cls.isActive = False
        cls._doneFunc()
        
    async def __wrong(cls, guiname : str):
        if cls._currentQuiz["type"] & QuizType.선다형:
            optionIndex = int(guiname[-1])
            cls.__wrongOption.setPos(cls._option[optionIndex].getPos()).setText(cls._option[optionIndex].getText()).isActive = True
            optionIndex = cls._currentQuiz["option"].index(cls._currentQuiz["answer"])
            cls.__correctOption.setPos(cls._option[optionIndex].getPos()).setText(cls._option[optionIndex].getText()).isActive = True
        elif cls._currentQuiz["type"] & QuizType.단답형:
            cls.__wrongText.setPos(cls._answerText.getPos()).setText(cls._currentQuiz['answer']).isActive = True
            
        #틀렸을 경우 틀림 카운트 +1
        cls.wrongCount += 1
        if cls._currentQuiz.get("wrong"):
            cls._currentQuiz["wrong"] += 1
        else:
            cls._currentQuiz["wrong"] = 1
                
        await asyncio.sleep(3)    #3초 딜레이
        cls.__wrongText.isActive = cls.__correctOption.isActive = cls.__wrongOption.isActive = False
        cls.task = None
        cls.isActive = False
        if cls._wrongFunc is not None:
            cls._wrongFunc()
                       
    @classmethod
    def _reset(cls):
        cls._quiz = cls._quiz + cls._usedQuiz + cls._filteredQuiz
        random.shuffle(cls._quiz)
        cls._usedQuiz = cls._filteredQuiz = []
        cls._size = len(cls._quiz)
        cls._filterType = QuizType.ALL()
    
    @classmethod
    def _setWidgetText(cls):
        cls._questionText.setText(cls._currentQuiz["question"]).isActive = True
        
        if cls._currentQuiz.get("code"):
            cls._codeText.setText(cls._currentQuiz.get("code")).isActive = True
        else:
            cls._codeText.setText("").isActive = False
        
        for i in range(5):
            cls._option[i].setText("").isActive = False
            cls._answerText.setText("").isActive = False
                
        if(cls._currentQuiz.get("option")):
            for i, option in enumerate(cls._currentQuiz.get("option")):
                if(option):
                    cls._option[i].setText(option).isActive = True
        else:
            cls._answerText.isActive = True
            
        
    #퀴즈를 반환하는 함수
    @classmethod
    def _nextQuiz(cls):    
        if cls._currentQuiz:
            cls._usedQuiz.append(cls._currentQuiz)
        
        if not cls._quiz:
            cls._quiz = cls._usedQuiz
            cls._usedQuiz = []
            random.shuffle(cls._quiz)    
        cls._currentQuiz = cls._quiz.pop()
        if(cls._currentQuiz["type"] & QuizType.선다형):
            random.shuffle(cls._currentQuiz["option"])
        cls._setWidgetText()
            
    #퀴즈 불러오는 함수
    @classmethod
    def _loadQuizzesFolder(cls, folderPath):
        jsonFiles = [f for f in os.listdir(folderPath) if f.endswith(".json")]
        for file in jsonFiles:
            filePath = os.path.join(folderPath, file)
            try:
                cls._loadQuiz(filePath)
            except Exception as e:
                print(f"로드 실패한 파일 : {filePath}, Error : {str(e)}")
                continue
            
    @classmethod            
    def _loadQuiz(cls, file : str):                 #json 파일에서 퀴즈를 가져온다.
        with open(file, "r",encoding="utf-8") as f: #파일을 읽기로 인코딩은 utf-8으로 연다(한글)
            _load = json.load(f)                    #파일에 저장된 리스트를 가져온다.
        for q in _load:                     #리스트 순회(딕셔너리)
            quizTypeEnum = 0                #type 값 저장
            loadType = q["type"][9:].split('|') #문자열을 IntFlag의 이름 단위로 분할
            for lt in loadType:
                if(lt not in QuizType.__members__): #QuizType에 해당 타입이 없으면
                    QuizType.addFlag(lt)            #새로 추가
                for qt in QuizType.__members__: #문자열을 QuizType의 enum 형태로 변환한다.
                    if(qt in q["type"]):
                        quizTypeEnum |= QuizType[qt]

            if quizTypeEnum & QuizType.선다형 and q["answer"] not in q["option"]:
                print(f"정답이 없는 문제가 제거되었습니다.\n{q}")
                continue
            #딕셔너리를 퀴즈에 추가한다.
            cls._addQuiz({"type" : quizTypeEnum , "level" :int(q["level"]),
            "question" : q["question"],             
            "code" : q.get("code"),
            "answer" : q["answer"],
            "option" : q.get("option"),
            "hint" : q.get("hint")})
        random.shuffle(cls._quiz)   #퀴즈 순서를 랜덤으로 섞는다.
    
    #퀴즈 딕셔너리 추가 함수
    @classmethod
    def _addQuiz(cls, quizDictionary : dict):
        if quizDictionary not in cls._quiz + cls._usedQuiz: #현재 있는 퀴즈가 아니면(중복 방지)
            cls._quiz.append(quizDictionary)    #해당 퀴즈를 추가한다.
            cls._size += 1                      #퀴즈 크기 증가.
            
    #퀴즈 저장 함수
    def saveQuiz(cls, file : str):
        with open(file, "w",encoding="utf-8") as f: #json 파일을 저장하기 위해 utf-8으로 연다(한글)
            quiz = []                               #저장할 퀴즈
            for q in (cls._quiz + cls._usedQuiz + cls._filteredQuiz):     #현재 퀴즈 순환
                q = dict(q)
                q["type"] = str(q["type"])          #json에 enum 값을 문자열 형태로 저장한다.
                quiz.append(q)                      #수정된 딕셔너리를 저장할 리스트에 추가한다.
            json.dump(quiz, f, indent='\t', ensure_ascii=False) #퀴즈 리스트를 저장한다.

    task = None
    correctCount = 0
    wrongCount = 0
    
    _quiz = []
    _usedQuiz = []
    _filterType = QuizType.ALL()
    _filteredQuiz = []
    _size = len(_quiz)
    _currentQuiz = {}
    _doneFunc = None
    _wrongFunc = None
    _questionText = Text(font=pygame.font.Font(os.path.join(fontFolder, "Maplestory Bold.ttf"), 17))
    _codeText = Text()
    _answerText = Text(enterFunc=None, isInputActive=True)
    _option = [Button(clickFunc = None) for i in range(5)]

    __wrongOption = Button(widgetColor=(255,0,0),fontColor=(0,0,0),hoverColor=(255,0,0),hoverFontColor=(0,0,0), isActive=False)
    __correctOption = Button(widgetColor=(157, 216, 75),fontColor=(0,0,0),hoverColor=(157, 216, 75),hoverFontColor=(0,0,0), isActive=False)
    __correctText = Text(widgetColor=(157, 216, 75),fontColor=(0,0,0), isActive=False)
    __wrongText = Text(widgetColor=(255, 0, 0),fontColor=(0,0,0), isActive=False)
    
    __timerText = Button(hoverColor=(31, 31, 31), hoverFontColor=(200,200,200)).setPos(120,150).setSize(50,50)
    _widgets = [_questionText, _codeText, _answerText] + _option + [__wrongOption, __correctOption, __correctText, __wrongText, __timerText]

Quiz._loadQuizzesFolder(quizFolder)
random.shuffle(Quiz._quiz)
Quiz._questionText.setPos(150-30,200).setSize(500+60, 50)
Quiz._codeText.setPos(150-30,400).setSize(500+60, 50) 

Quiz._answerText.setCallbackFunc(lambda _answerText = Quiz._answerText:Quiz._checkAnswer(_answerText.getText(),"text0")).setPos(150-30,660).setSize(500+60, 150)
for i, o in enumerate(Quiz._option):
    o.setPos(150, 600 + i * 60)
    o.setCallbackFunc(lambda button = o, i = i:Quiz._checkAnswer(button.getText(), "option"+str(i)))
    o.keyBindList = [pygame.K_1 + i]