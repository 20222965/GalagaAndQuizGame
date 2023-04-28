# -*- coding: utf-8 -*-

import tkinter as tk
import random
import json
from enum import IntFlag, auto

#퀴즈 타입을 구별하기 위한 enum클래스다. 같은 요소가 있는지 확인하려면 &, 추가하려면 | 연산을 하면 된다.
# ex) QuizType.선다형을 찾기 위해선 if(a & QuizType.선다형)으로 하면 된다. 
class QuizType(IntFlag):
    선다형 = auto()
    단답형 = auto()
    힌트 = auto()
    코드작성 = auto()
    실행결과 = auto()
    문법 = auto()
    등등 = auto()
    나중에쓸지모르는 = auto()
    필터링용추가가능 = auto()
    ALL = 선다형 | 단답형 | 힌트 | 코드작성 | 실행결과 | 문법 | 등등 | 나중에쓸지모르는 | 필터링용추가가능


#퀴즈는 딕셔너리 형태로 퀴즈 리스트에 저장한다.
#퀴즈 딕셔너리 설명
#"type" 에는 문제 종류를 저장한다. 선다형/단답형 퀴즈 화면을 구현하기 위한 것으로
#   다른 부수적인 것은 나중에 필터링 기능을 사용하여 특정 유형만 남기는 용도로 사용할 수도 있다.
#   QuizType 클래스, enum 타입중 하나인 IntFlag로 저장된다.
#   추가할 때는 | 를 사용하고
#   내부에 있는지 확인할 때는 == 연산이 아닌 &를 사용하여 확인한다. ex) if(quiz['type'] & QuizType.선다형):

#"level"은 나중에 단계별로 난이도가 올라가는 것을 구현할 때 사용될 수 있다. 만약 필요 없으면 이 부분은 삭제할 수 있다. int형으로 저장된다.

#"question"은 문제 유형 설명을 저장한다. ex) "question" : "다음 프로그램의 실행 결과를 쓰시오."

#"code"는 코드 내용을 저장한다. str형으로 저장하며, """ """으로 하면 여러줄 문자열을 사용할 수 있다.

#"answer"는 답을 저장한다. 현재는 str형으로 저장한다.

#"option"은 선다형 문제에서 사용하며, 현재 5개의 선택지를 사용한다. ["선택지","선택지", ...]의 형태로 저장한다.

#"hint"는 현재는 사용하지 않지만 나중에 힌트가 있는 문제를 사용하면 문자열로 저장한다.

#"option" 또는 "hint"가 필요 없는 문제라면 해당 부분을 None으로 해도 되고, 입력하지 않아도 된다.
quizList = []
quizList.append({"type" : QuizType.선다형 | QuizType.실행결과 , "level" : 2,
                 "question" : "다음 프로그램의 실행 결과로 알맞은 것을 고르시오.",
                "code" : """a = "abcdefgh"\nprint(a[0:6:2])""",
                "answer" : "ace",
                'option' : ['aceg', 'ace','ag', 'a','abcdefabcdef'],
                'hint' : None})
quizList.append({"type" : QuizType.선다형 | QuizType.문법 , "level" : 2,
                 "question" : "다음 중 파이썬에 없는 기본 자료형을 고르시오.",
                "code" : None,
                "answer" : "unsigned int",
                'option' : ['unsigned int', 'str', 'float', 'bool', 'list'],
                'hint' : None})
quizList.append({"type" : QuizType.단답형 | QuizType.실행결과 , "level" : 2,
                 "question" : "다음 프로그램의 실행 결과를 쓰시오.",
                "code" : """a = "pythonQuizProgram"
print(a[8::-3])""",
                "answer" : "int",
                'option' : None,
                'hint' : None})
quizList.append({"type" : QuizType.단답형 | QuizType.실행결과 , "level" : 7,
                 "question" : "다음 프로그램의 실행 결과를 쓰시오.",
                "code" : """import numpy as np
np_array = np.array([[1,2,3,4],
                     [5,6,7,8],
                     [9,10,11,12],
                     [13,14,15,16]])
print(np_array[::2][::2])""",
                "answer" : "[[1 2 3 4]]",
                'option' : None,
                'hint' : None})


#퀴즈 목록을 관리하는 클래스
class Quiz:
    def __init__(self):             #C++의 생성자 역할을 한다.
        #퀴즈를 저장하는 리스트, 프로그램 안에서 작성한 전역 퀴즈 리스트를 랜덤 순서로 가져온다.
        self.quiz = quizList
        random.shuffle(self.quiz)
        self.usedQuiz = []          #self.quiz에서 사용된 퀴즈 또는 필터링으로 걸러진 퀴즈들이 보관된다.
        self.size = len(self.quiz)  #현재 퀴즈 크기를 갱신한다.

    #사용/필터링된 퀴즈를 모두 self.quiz로 다시 옮기는 함수
    def reset(self):
        self.quiz += self.usedQuiz
        self.usedQuiz.clear()
        self.size = len(self.quiz)

    #퀴즈를 반환하는 함수
    def getNextQuiz(self, minLevel : int = 0, maxLevel : int = 255):
        if(self.size <= 0):
            return -1
        
        for quiz in self.quiz:
            #min, max는 난이도가 상승하는 형태가 필요할 때 사용가능.
            if minLevel <= quiz["level"] <= maxLevel:
                self.usedQuiz.append(quiz)      #조건 맞으면 사용된 퀴즈로 옮기고
                self.quiz.remove(quiz)          #퀴즈 목록에서 제거한다.
                self.size -= 1
                if(quiz['option']): #선다형일 경우 선택지 순서를 변경한다.
                    random.shuffle(quiz['option'])
                return quiz         #조건에 맞는 퀴즈를 반환한다.        
            
    #퀴즈 불러오는 함수 (현재 미사용)
    def loadQuiz(self, file : str):                 #json 파일에서 퀴즈를 가져온다.
        with open(file, "r",encoding="utf-8") as f: #파일을 읽기로 인코딩은 utf-8으로 연다(한글)
            _load = json.load(f)                    #파일에 저장된 리스트를 가져온다.
        for q in _load:                     #리스트 순회(딕셔너리)
            quizTypeEnum = 0                #type 값 저장
            for qt in QuizType.__members__: #문자열을 QuizType의 enum 형태로 변환한다.
                if(qt in q["type"]):
                    quizTypeEnum |= QuizType[qt]
            #딕셔너리를 퀴즈에 추가한다.
            self.addQuiz({"type" : quizTypeEnum , "level" :int(q["level"]),
            "question" : q["question"],             
            "code" : q["code"],
            "answer" : q["answer"],
            "option" : q["option"],
            "hint" : q["hint"]})
        random.shuffle(self.quiz)   #퀴즈 순서를 랜덤으로 섞는다.
    
    #퀴즈 딕셔너리 추가 함수 (현재 미사용)
    def addQuiz(self, quizDictionary : dict):
        if quizDictionary not in self.quiz + self.usedQuiz: #현재 있는 퀴즈가 아니면(중복 방지)
            self.quiz.append(quizDictionary)    #해당 퀴즈를 추가한다.
            self.size += 1                      #퀴즈 크기 증가.

    #퀴즈 저장 함수 (현재 미사용)
    def saveQuiz(self, file : str):
        with open(file, "w",encoding="utf-8") as f: #json 파일을 저장하기 위해 utf-8으로 연다(한글)
            quiz = []                               #저장할 퀴즈
            for q in self.quiz + self.usedQuiz:     #현재 퀴즈 순환
                q["type"] = str(q["type"])          #json에 enum 값을 문자열 형태로 저장한다.
                quiz.append(q)                      #수정된 딕셔너리를 저장할 리스트에 추가한다.
            #print(quiz)
            json.dump(quiz, f, indent='\t', ensure_ascii=False) #퀴즈 리스트를 저장한다.

    #퀴즈 필터링 함수   (현재 미사용)
    def filterQuiz(self, quizType : QuizType):
        filter = [quiz for quiz in self.quiz if quiz["type"] & quizType]    #퀴즈에서 해당 타입이 있는 것을 저장한다.
        for f in filter:
            if f not in self.quiz:  #퀴즈에서 해당 타입이 없으면, quiz에서 usedQuiz로 옮긴다.
                self.usedQuiz.append(f)
                self.quiz.remove(f)



#게임을 진행하는 클래스
class Game:
    #C++ 에서의 생성자 역할, 인스턴스가 생성될 때 실행된다.
    def __init__(self, master : tk.Tk):
        self.master = master     #tkinter.TK()
        self.master.geometry("1280x720")    #화면의 크기를 설정한다.
        self.master.resizable(False,False)  #화면 크기 변경을 비활성화한다.
        self.quiz = Quiz()                  #퀴즈 클래스를 저장한다.
        self.currentQuiz = None             #현재 퀴즈 딕셔너리를 저장한다.
        self.quizNumber = 0                 #현재 퀴즈 번호
        self.answerCount = 0                #맞춘 개수

        self.mainPage = MainPage(master, self)  #메인페이지 프레임을 저장한다.
        self.quizPage = QuizPage(master, self)  #퀴즈페이지 프레임을 저장한다.
        self.resultPage = ResultPage(master, self) #결과페이지 프레임을 저장한다.
        self.currentPage = self.mainPage        #현재페이지 프레임을 메인 페이지로 저장한다.
        self.currentPage.show()                 #현재페이지를 화면에 보여준다.

    #처음 시작하는 함수
    def start(self):
        self.quizNumber = 1
        self.answerCount = 0
        self.currentQuiz = self.quiz.getNextQuiz()  #퀴즈를 가져와 저장한다.
        self.replacePage(self.quizPage)
    
    #입력값이 정답인지 확인하는 함수
    def checkAnswer(self, option):
        #입력값 양끝 공백 제거(오류방지)
        option = option.strip()

        #테스트용, 나중에 제거
        print(f"checkAnswer호출 option 값 : {option}, answer 값 : {self.currentQuiz['answer']}\n정답 확인 : {self.currentQuiz['answer'] == option}")

        #정답일 경우
        if(self.currentQuiz['answer'] == option ):
            #정답 카운트 +1, 다음 문제 함수 실행한다.
            self.answerCount += 1
            self.nextQuiz()
        else:
            #틀렸을 경우 다음 문제로 넘어감.
            self.nextQuiz()

    #다음 문제를 가져오는 함수            
    def nextQuiz(self):
        if(self.quiz.size <= 0):    #퀴즈가 남아있지 않으면
            #퀴즈를 초기화하고 결과화면으로 이동한다.
            self.quiz.reset()
            self.replacePage(self.resultPage)
            return
        
        #문제 번호를 더하고, 다음 문제를 가져온다.
        self.quizNumber += 1
        self.currentQuiz = self.quiz.getNextQuiz()
        #퀴즈 화면 위젯을 갱신한다.
        self.currentPage.hide()
        self.currentPage.show()

    #다른 페이지(프레임)로 교체한다.
    def replacePage(self, pageClass):
        self.currentPage.hide()         #현재 페이지를 숨기고
        self.currentPage = pageClass    #바꿀 페이지를 가져와서
        self.currentPage.show()         #그 페이지를 보여준다.
    
    #게임을 종료한다.
    def quit(self):
        self.master.quit()

#GUI로 퀴즈 화면을 보여주는 클래스
class QuizPage(tk.Frame):
    def __init__(self, master, game):   #Tk, Game 클래스를 사용한다.
        tk.Frame.__init__(self, master)
        
        #상단 프레임
        self.topFrame = tk.Frame(master)

        #맨 위의 값을 표시한다. 문제 번호, 설명을 출력한다.
        self.question = tk.StringVar()
        self.questionLabel = tk.Label(self.topFrame, textvariable=self.question, font=("", 30, "bold"), background='gray')

        #스크롤바, 문제가 길 경우 스크롤하여 볼 수 있다.
        self.scrollbar = tk.Scrollbar(self.topFrame)
        #quiz['code']을 Text로 화면에 보여준다.  / yscrollcommand=self.scrollbar.set는 스크롤바 설정
        self.codeText = tk.Text(self.topFrame,font=("consolas", 18),height=6, yscrollcommand=self.scrollbar.set, bd=2)
        #스크롤바로 움직일 수 있게 설정
        self.scrollbar.config(command=self.codeText.yview,bd=8)

        #하단 프레임
        self.bottomFrame = tk.Frame(master)
        #주관식 문제를 위한 Text 창
        self.text = tk.Text(self.bottomFrame, width=40, height=5,font=("consolas",15), bd=2)
        #주관식 문제를 위한 버튼, 클릭 시 command에 있는 함수로 텍스트창 있는 값을 정답 확인 함수로 가져가고, 텍스트 창을 비운다.
        self.btn = tk.Button(self.bottomFrame, text="정답제출", command=lambda : (game.checkAnswer(self.text.get(0.0,tk.END)),self.text.delete(0.0,tk.END)),
                             width= 20, height= 3, bd = 5, font= ("",15,"bold"))

        #선다형 문제, option 값을 저장하는 리스트
        self.options = []
        #버튼을 저장하는 리스트
        self.buttons = []
        for i in range(5):
            #선택지 값을 저장할 변수
            option = tk.StringVar()
            self.options.append(option)
            #버튼, 내용은 option으로 나오며, 버튼을 클릭하면 command에 저장된 함수를 실행한다.
            #   인덱스 값을 가져와서 그 선택지 내용을 정답 함수로 가져간다. [2:]는 문자열 앞 번호 1. , 2. 를 제거하기 위해서이다.
            button = tk.Button(self.bottomFrame, textvariable=option, width=30,font=("consolas",20), bd= 3, anchor="w",background='white',
                                command=lambda i=i: game.checkAnswer(self.options[i].get()[2:]))
            self.buttons.append(button)

    #화면에 퀴즈를 보여주는 함수
    def show(self):
        #상단 프레임을 보여준다.
        self.topFrame.pack(side="top", fill="both", expand=True)
        #맨 위쪽 값을 수정한다.
        self.question.set(str(game.quizNumber) + ". " + game.currentQuiz["question"])

        if(game.currentQuiz["code"]):
            #Text창을 수정 가능으로 변경한다.
            self.codeText.configure(state="normal")
            #이전에 텍스트에 저장된 값을 삭제한다.
            self.codeText.delete(0.0,tk.END)
            #텍스트창에 코드 내용을 가져온다.
            self.codeText.insert(tk.END, game.currentQuiz["code"])
            #텍스트창을 수정 불가능으로 변경한다.
            self.codeText.configure(state="disabled")

        #pack()은 상대 위치 배치로, 화면에 위젯을 배치한다.
        self.questionLabel.pack(side = "top", pady=1)

        if(game.currentQuiz["code"]):
            #self.questionLabel.pack(side = "top", pady=5)
            self.scrollbar.pack(side="left",fill="both")
            self.codeText.pack(side="left",fill="x")

        #하단 프레임을 보여준다.
        self.bottomFrame.pack(side="bottom", fill="both",expand=True)
        #선다형 문제일 때만 선택지를 보여준다.
        if(game.currentQuiz["type"] & QuizType.선다형):
            for i in range(len(game.currentQuiz["option"])):
                self.options[i].set(str(i+1) + ". " + game.currentQuiz["option"][i])
                #self.buttons[i].place(x=400, y=i*60)
                self.buttons[i].pack(pady=5)
        #선다형 문제가 아닌 주관식이면 입력창과 제출 버튼을 보여준다.
        else:
            self.text.pack()
            self.btn.pack()   

    #퀴즈를 숨기는 함수
    def hide(self):
        #pack_forget()을 사용하여 모든 위젯들을 숨긴다.
        self.topFrame.pack_forget()
        self.questionLabel.pack_forget()

        self.scrollbar.pack_forget()
        self.codeText.pack_forget()

        self.bottomFrame.pack_forget()
        self.text.pack_forget()
        self.btn.pack_forget()
        for i in range(5):
            self.buttons[i].pack_forget()
            #self.buttons[i].place_forget()           


#GUI로 시작 화면을 보여주는 클래스
class MainPage(tk.Frame):   
    def __init__(self, master, game):   #Tk, Game 클래스를 사용한다.
        tk.Frame.__init__(self, master)
        self.text = tk.Label(master, text="3조 Test : Start Page", font=("", 50, "bold"))
        #이 버튼을 클릭하면 게임을 시작한다.
        self.btn1 = tk.Button(master, text="Start", width=20,  font=("", 30), bd = 3,
                command=lambda:game.start())
        
    #시작화면을 보여주는 함수
    def show(self):
        self.text.pack(side="top", fill="x", pady=5)
        #place()는 절대 위치로 배치할 수 있다. rely를 사용하면 상대위치 값(0~1)으로 상단으로부터 0.3만큼 아래로 배치한다.
        self.btn1.place(x=380, y=50, rely=0.3)

    #시작화면을 숨기는 함수
    def hide(self):
        self.text.pack_forget()
        self.btn1.place_forget()


#GUI로 결과 화면을 보여주는 클래스
class ResultPage(tk.Frame):   
    def __init__(self, master : tk.Tk, game : Game):   #Tk, Game 클래스를 사용한다.
        tk.Frame.__init__(self, master)
        #총 문제와 정답을 보여준다.
        self.result = tk.StringVar()
        self.resultLabel = tk.Label(master, textvariable = self.result, font=("", 30, "bold"))
        #이 버튼을 클릭하면 시작 화면으로 교체하는 함수를 호출한다.
        self.btn1 = tk.Button(master, text="처음으로", width=20,  font=("", 20), bd = 3,
                command=lambda:game.replacePage(game.mainPage))
        #이 버튼을 클릭하면 게임을 종료하는 함수를 호출한다.
        self.btn2 = tk.Button(master, text="종료", width=20,  font=("", 20), bd = 3,
                command=lambda:game.quit())
        
    #결과창을 보여주는 함수
    def show(self):
        self.result.set("총 문제 : " + str(game.quizNumber) +"\n정답 : " + str(game.answerCount))
        self.resultLabel.place(x = 550, y = 270)
        self.btn1.place(x=480, y=390)
        self.btn2.place(x=480, y=460)

    #결과창을 숨기는 함수
    def hide(self):
        self.resultLabel.place_forget()
        self.btn1.place_forget()
        self.btn2.place_forget()

root = tk.Tk()      #Tkinter 모듈의 Tk 클래스를 사용하여 창을 생성한다.
game = Game(root)   #Game의 인스턴스를 생성하여 root 창에서 게임을 실행한다.
root.mainloop()     #root 창을 계속해서 업데이트, 이벤트 처리, 사용자 입력을 기다린다. 이것이 없으면 창이 바로 꺼진다.