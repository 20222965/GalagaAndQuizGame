# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
import random
import json
from enum import IntFlag, auto
from typing import Literal
import os

currentDir = os.path.dirname(os.path.abspath(__file__))
quizFolder = os.path.join(currentDir, "data/quiz")
imageFolder = os.path.join(currentDir, "data/img")

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
    def __init__(self):             #C++의 생성자 역할을 한다.
        #퀴즈를 저장하는 리스트, 프로그램 안에서 작성한 전역 퀴즈 리스트를 랜덤 순서로 가져온다.
        self.quiz = []
        self.usedQuiz = []          #self.quiz에서 사용된 퀴즈 또는 필터링으로 걸러진 퀴즈들이 보관된다.
        self.size = len(self.quiz)  #현재 퀴즈 크기를 갱신한다.

    #사용/필터링된 퀴즈를 모두 self.quiz로 다시 옮기는 함수
    def reset(self):
        self.quiz += self.usedQuiz
        self.usedQuiz = []
        self.size = len(self.quiz)

    #퀴즈를 반환하는 함수
    def getNextQuiz(self, minLevel : int = 0, maxLevel : int = 255):
        if(self.size <= 0):
            return None
        
        for quiz in self.quiz:
            #min, max는 난이도가 상승하는 형태가 필요할 때 사용가능.
            if minLevel <= quiz["level"] <= maxLevel:
                self.usedQuiz.append(quiz)      #조건 맞으면 사용된 퀴즈로 옮기고
                self.quiz.remove(quiz)          #퀴즈 목록에서 제거한다.
                self.size -= 1
                if(quiz['option']): #선다형일 경우 선택지 순서를 변경한다.
                    random.shuffle(quiz['option'])
                return quiz         #조건에 맞는 퀴즈를 반환한다.        
        return None
            
    #퀴즈 불러오는 함수
    def loadQuiz(self, file : str):                 #json 파일에서 퀴즈를 가져온다.
        with open(file, "r",encoding="utf-8") as f: #파일을 읽기로 인코딩은 utf-8으로 연다(한글)
            _load = json.load(f)                    #파일에 저장된 리스트를 가져온다.
        for q in _load:                     #리스트 순회(딕셔너리)
            quizTypeEnum = 0                #type 값 저장
            loadType = q["type"][9:].split('|')
            for lt in loadType:
                if(lt not in QuizType.__members__):
                    QuizType.addFlag(lt)
                for qt in QuizType.__members__: #문자열을 QuizType의 enum 형태로 변환한다.
                    if(qt in q["type"]):
                        quizTypeEnum |= QuizType[qt]

            #딕셔너리를 퀴즈에 추가한다.
            self.addQuiz({"type" : quizTypeEnum , "level" :int(q["level"]),
            "question" : q["question"],             
            "code" : q.get("code"),
            "answer" : q["answer"],
            "option" : q.get("option"),
            "hint" : q.get("hint")})
    
    #퀴즈 딕셔너리 추가 함수
    def addQuiz(self, quizDictionary : dict):
        if quizDictionary not in self.quiz + self.usedQuiz: #현재 있는 퀴즈가 아니면(중복 방지)
            self.quiz.append(quizDictionary)    #해당 퀴즈를 추가한다.
            self.size += 1                      #퀴즈 크기 증가.

    #퀴즈 저장 함수
    def saveQuiz(self, file : str):
        with open(file, "w",encoding="utf-8") as f: #json 파일을 저장하기 위해 utf-8으로 연다(한글)
            quiz = []                               #저장할 퀴즈
            for q in (self.quiz + self.usedQuiz):     #현재 퀴즈 순환
                q = dict(q)
                q["type"] = str(q["type"])          #json에 enum 값을 문자열 형태로 저장한다.
                quiz.append(q)                      #수정된 딕셔너리를 저장할 리스트에 추가한다.
            #print(quiz)
            json.dump(quiz, f, indent='\t', ensure_ascii=False) #퀴즈 리스트를 저장한다.

    #퀴즈 Level 정렬 함수
    def sortQuiz(self, bReverse : bool = False):
        self.quiz = sorted(self.quiz, key=lambda x: x["level"], reverse=bReverse)
    def deleteQuiz(self, index):
        if(0<= index < self.size):
            self.quiz.pop(index)
        self.size -= 1
    #퀴즈 필터링 함수   (현재 미사용)
    def filterQuiz(self, quizType : QuizType):
        #퀴즈에서 해당 타입이 있는 것을 저장한다.
        filter = [quiz for quiz in self.quiz if quiz["type"] & quizType]
        #퀴즈에서 해당 타입이 없으면, quiz에서 usedQuiz로 옮긴다.
        self.usedQuiz.extend([quiz for quiz in self.quiz if quiz not in filter])
        #self.quiz에 해당 타입이 있는 퀴즈만 남긴다.
        self.quiz = filter


class QuizEditor:
    #C++ 에서의 생성자 역할, 인스턴스가 생성될 때 실행된다.
    def __init__(self, master : tk.Tk):
        self.master = master     #tkinter.TK()
        self.master.title("Quiz Editor")
        self.master.geometry("1280x720")    #화면의 크기를 설정한다.
        self.master.resizable(False,False)  #화면 크기 변경을 비활성화한다.
        self.quiz = Quiz()                  #퀴즈 클래스를 저장한다.
        self.quizFilePath = ""                 #연결된 퀴즈 파일

        self.currentQuiz = None             #현재 퀴즈 딕셔너리를 저장한다.

        self.mainPage = MainPage(master, self)  #메인페이지 프레임을 저장한다.
        self.currentPage = self.mainPage        #현재페이지 프레임을 메인 페이지로 저장한다.
        self.currentPage.show()                 #현재페이지를 화면에 보여준다.

    def loadQuizFile(self):
        self.quizFilePath = filedialog.askopenfilename(defaultextension=".json", filetypes=[('JSON 파일', '*.json')], initialdir=quizFolder)
        if self.quizFilePath:
            # 파일 로드 성공
            print("파일 로드 경로:", self.quizFilePath)
            self.quiz.loadQuiz(self.quizFilePath)
            print("로드 완료")
            self.currentPage.hide()
            self.currentPage.show()
        else:
            # 파일 로드 실패
            print("파일 선택이 취소되었습니다.")

    def saveAsQuizFile(self):
        self.quizFilePath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[('JSON 파일', '*.json')], initialdir=quizFolder)
        if self.quizFilePath:
            # 파일 로드 성공
            print("파일 저장 경로:", self.quizFilePath)
            self.quiz.saveQuiz(self.quizFilePath)
            print("파일 저장 완료")
        else:
            # 파일 로드 실패
            print("파일 선택이 취소되었습니다.")
    
    def sortQuiz(self, bReverse : bool = False):
        self.quiz.sortQuiz(bReverse)
        
    def getQuiz(self, index):
        return self.quiz.quiz[index]
    def getQuizList(self):
        return self.quiz.quiz
    
    def modifyQuiz(self, index, quiz : dict):
        self.quiz.quiz[index] = quiz
        self.currentPage.update()
    
    def addQuiz(self, quiz : dict):
        self.quiz.addQuiz(quiz)
        self.currentPage.update()

    def deleteQuiz(self, index):
        self.quiz.deleteQuiz(index)
        self.currentPage.update()
        
    #종료한다.
    def quit(self):
        self.master.quit()


#GUI로 시작 화면을 보여주는 클래스
class MainPage(tk.Frame):   
    def __init__(self, master :tk.Tk, quizEditor : QuizEditor):   #Tk, QuizEditor 클래스를 사용한다.
        super().__init__(master)
        self.quizEditor = quizEditor

        self.config(bg='lightgray')
        self.text = tk.Label(self, text="3 : Quiz Editor", font=("", 20, "bold"))

        self.quizCnt = tk.StringVar()
        self.quizCntText = tk.Label(self, textvariable=self.quizCnt, font=("", 10, "bold"))
        
        #퀴즈 리스트 보여주는 함수
        self.quizlistbox = tk.Frame(master)
        self.scrollbar = tk.Scrollbar(self.quizlistbox)
        self.quizCanvas = tk.Canvas(self.quizlistbox, width=900, height=1, bd=2, yscrollcommand=self.scrollbar.set,bg='gray')
        self.scrollbar.config(command=self.quizCanvas.yview)


        self.selectQuizIdx = -1  # 선택된 퀴즈 블록의 인덱스 저장
        self.bSortReverse = False   #퀴즈 정렬 bool 값

        #새 퀴즈 생성, 퀴즈 수정, 정렬, 삭제 버튼
        self.newQuizBtn = tk.Button(self, text="퀴즈 생성", width=10,  font=("", 15), bd = 3,
                command=lambda:(self.quizEditPopup.editQuiz("new", self.selectQuizIdx)))
        self.modifyQuizBtn = tk.Button(self, text="퀴즈 수정", width=10,  font=("", 15), bd = 3,
                command=lambda:(self.quizEditPopup.editQuiz("modify", self.selectQuizIdx)))
        self.sortQuizBtn = tk.Button(self, text="퀴즈 정렬", width=10,  font=("", 15), bd = 3,
                command=lambda:(self.sortQuiz()))
        self.removeQuizBtn = tk.Button(self, text="퀴즈 삭제", width=10,  font=("", 15), bd = 3, bg="red",
                command=lambda:(self.deleteQuiz(self.selectQuizIdx)))
        
        #퀴즈 파일 불러오기 버튼, 퀴즈 파일 저장 버튼
        self.loadQuizBtn = tk.Button(self, text="파일 불러오기", width=15,  font=("", 15), bd = 3,
                command=lambda:self.quizEditor.loadQuizFile())
        self.saveQuizBtn = tk.Button(self, text="파일 저장", width=15,  font=("", 15), bd = 3,
                command=lambda:self.quizEditor.saveAsQuizFile())
        
        #퀴즈 수정창
        self.quizEditPopup = QuizEditPopup(master, self.quizEditor)
        #종료 버튼
        self.quitBtn = tk.Button(self, text="종료",  font=("", 15,'bold'), bd = 3, bg="red",
                command=lambda:self.quizEditor.quit())
    
    #퀴즈 정렬 함수. 오름차순 / 내림차순
    def sortQuiz(self):
        self.quizEditor.sortQuiz(self.bSortReverse)
        self.bSortReverse = not self.bSortReverse
        self.update()

    #퀴즈 삭제 함수
    def deleteQuiz(self, index):
        if(0 <= index < self.quizEditor.quiz.size):
            bDeleteTrue = messagebox.askokcancel(f"퀴즈 삭제 {index}", "퀴즈를 삭제하겠습니까?")
            if bDeleteTrue:
                self.quizEditor.deleteQuiz(index)

    #퀴즈 리스트 선택 시 실행하는 함수.
    def selectQuiz(self, index):
        #이전에 선택헀던 블록의 색 초기화.
        if(self.selectQuizIdx >= 0):
            self.quizCanvas.itemconfig("quizRect" + str(self.selectQuizIdx), fill='white')
        #현재 선택한 퀴즈 인덱스 저장
        self.selectQuizIdx = index
        print(f"{index} 선택")
        #선택할 수 없는 값이면
        if(self.selectQuizIdx >= self.quizEditor.quiz.size or self.selectQuizIdx < 0):
            #-1로 초기화
            self.selectQuizIdx = -1
        else:
            #선택한 블록 색을 바꿈.
            self.quizCanvas.itemconfig("quizRect" + str(self.selectQuizIdx), fill="lightblue")

    #퀴즈 리스트 생성 함수
    def setQuizList(self):
        #퀴즈 리스트 캔버스 초기화
        self.quizCanvas.delete("all")
        #각 퀴즈 순회
        preTextLine = 0
        for i, quiz in enumerate(self.quizEditor.getQuizList()):
            #퀴즈 내용 설정
            text = "Level: " + str(quiz.get('level')) + "\n" + \
            "Type: " + str(quiz.get('type')) + "\n" + \
            "Question: " + str(quiz.get('question')) + "\n" + \
            "Answer: " + str(quiz.get('answer')) + "\n" + \
            "option: " + str(quiz.get('option')) + "\n" + \
            "hint: " + str(quiz.get('hint')) + "\n" + \
            "code: " + str(quiz.get('code')) + '\n'
            #퀴즈 왼,상, 우,하 위치 설정
            textLine = ( len(text.splitlines()) + 1 ) * 15

            x1, y1 = 0, 0 + preTextLine
            x2, y2 = 100 + 900, preTextLine + textLine
            preTextLine = preTextLine + textLine

            #퀴즈 밑 사각형 생성
            self.quizCanvas.create_rectangle(x1, y1, x2, y2, outline="gray", fill="white",width=3, tags="quizRect" + str(i))
            #퀴즈 텍스트 생성
            self.quizCanvas.create_text(x1 + 10, y1 + 10, anchor="nw", text=text, tags= "quizText" + str(i))
            #퀴즈 클릭 인식(선택한 퀴즈 색 변경, 현재 선택한 퀴즈 인덱스 저장)
            self.quizCanvas.tag_bind("quizRect" + str(i), "<Button-1>", lambda event, index =i:self.selectQuiz(index))
            self.quizCanvas.tag_bind("quizText" + str(i), "<Button-1>", lambda event, index =i:self.selectQuiz(index))
            #퀴즈 더블클릭 인식(퀴즈 수정 모드)
            self.quizCanvas.tag_bind("quizRect" + str(i), "<Double-Button-1>", lambda event, index=i: self.quizEditPopup.editQuiz('modify',index))
            self.quizCanvas.tag_bind("quizText" + str(i), "<Double-Button-1>", lambda event, index=i: self.quizEditPopup.editQuiz('modify',index))

    #시작화면을 보여주는 함수
    def show(self):
        self.place(x=0,y=0,width=1280,height=720)
        self.text.pack(side="top", fill="x", pady=5)
        self.quizCnt.set("퀴즈 수\n" + str(self.quizEditor.quiz.size))
        self.quizCntText.place(x=40,y=60)
        
        
        self.newQuizBtn.place(x=1120, y=100)
        self.modifyQuizBtn.place(x=1120, y=150)
        self.sortQuizBtn.place(x=1120, y=200)
        self.removeQuizBtn.place(x=1120, y=250)

        self.loadQuizBtn.place(x=450, y=670)
        self.saveQuizBtn.place(x=670, y=670)

        self.quitBtn.place(x=1190,y=650)

        self.quizlistbox.place(x=100,y=50,width=1000,height=600)
        self.setQuizList()
        
        self.quizCanvas.pack(side="left",fill="both",expand=True)
        self.scrollbar.pack(side="right",fill="y")
        self.quizCanvas.yview_moveto(0)
        self.quizCanvas.configure(scrollregion=self.quizCanvas.bbox("all"), yscrollcommand=self.scrollbar.set)
        self.quizCanvas.bind_all("<MouseWheel>", lambda event: self.quizCanvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

        self.selectQuiz(self.selectQuizIdx)

        

    #시작화면을 숨기는 함수
    def hide(self):
        self.text.pack_forget()
        
        self.newQuizBtn.place_forget()
        self.modifyQuizBtn.place_forget()
        self.sortQuizBtn.place_forget()
        self.removeQuizBtn.place_forget()

        self.loadQuizBtn.place_forget()
        self.saveQuizBtn.place_forget()
        self.quitBtn.place_forget()

        self.quizCanvas.pack_forget()
        self.scrollbar.pack_forget()
        
        self.place_forget()
        
    def update(self):
        self.hide()
        self.show()


#퀴즈 편집(생성/수정) 창
class QuizEditPopup(tk.Frame):
    def __init__(self, master : tk.Tk, quizEditor : QuizEditor):
        tk.Frame.__init__(self, master)
        self.bEdit = False
        self.quizEditor = quizEditor
        self.index = -1
        self.quiz = {}

        self.config(bg='white')

        #탭 속성 설정
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("", 15,"bold"), padding = [10,5])
        #탭 생성
        self.tab = ttk.Notebook(self,takefocus=True)
        #Type, Level 수정 탭
        self.quizTypeTab = tk.Frame(self,width=1000,height=500)
        self.tab.add(self.quizTypeTab, text="Type")
        #level 관련
        self.levelLabel = tk.Label(self.quizTypeTab, text="Level", font=("", 15,"bold"))
        self.levelVar = tk.IntVar(value=self.quiz.get('level'))
        self.levelSpinbox = tk.Spinbox(self.quizTypeTab, from_=1, to=100, textvariable=self.levelVar,
                                       command=self.setLevel,borderwidth=10, width=10)
        #QuizType 체크박스
        self.checkBtn = []
        self.checkText = []
        self.bIsChecked = []
        #QuizType 추가 버튼, 문자열 입력창
        self.addType = tk.Button(self.quizTypeTab, text="새로운 퀴즈 유형 추가", font=("", 15,"bold"),
                                 command=lambda :(self.addQuizType(self.addTypeText.get()),self.addTypeText.delete(0,tk.END)))
        self.addTypeText = tk.Entry(self.quizTypeTab, font=("", 12))

        #Question 탭
        self.quizQuestionTab = tk.Frame(self,width=1000,height=500)
        self.tab.add(self.quizQuestionTab, text="Question")
        #question 입력 텍스트
        self.questionLabel = tk.Label(self.quizQuestionTab, text="Question", font=("", 15,"bold"))
        self.questionText = tk.Text(self.quizQuestionTab, font=("", 15,"bold"))

        #Code 탭
        self.quizCodeTab = tk.Frame(self,width=1000,height=500)
        self.tab.add(self.quizCodeTab, text="Code")
        #code 입력 텍스트
        self.codeLabel = tk.Label(self.quizCodeTab, text="Code", font=("", 15,"bold"))
        self.codeText = tk.Text(self.quizCodeTab, font=("consolas", 15,"bold"))

        #Answer, Hint 탭
        self.quizAnswerHintTab = tk.Frame(self,width=1000,height=500)
        self.tab.add(self.quizAnswerHintTab, text="Answer & Hint")
        #answer 입력 텍스트
        self.answerLabel = tk.Label(self.quizAnswerHintTab, text="Answer", font=("", 15,"bold"))
        self.answerText = tk.Text(self.quizAnswerHintTab, font=("consolas", 15,"bold"),height=14)
        #hint 입력 텍스트
        self.hintLabel = tk.Label(self.quizAnswerHintTab, text="Hint", font=("", 15,"bold"))
        self.hintText = tk.Text(self.quizAnswerHintTab, font=("", 15))

        #option 탭
        self.optionTab = tk.Frame(self,width=1000,height=500)
        self.tab.add(self.optionTab, text="Option")
        #option 리스트, 0~4 입력 텍스트
        self.optionList = []
        for i in range(5):
            self.optionList.append(tk.Text(self.optionTab, width=50, font=("", 15),height=2))

        #저장 버튼, 취소 버튼
        self.doneBtn = tk.Button(self, text="저장", width=8,  font=("", 16,'bold'), bd = 3, bg = 'lightgreen',
                command=lambda:self.done())
        self.cancelBtn = tk.Button(self, text="취소", width=6,  font=("", 15,'bold'), bd = 3, bg = 'red',
                command=lambda:self.hide())
        
    #퀴즈 편집 시작 함수
    def editQuiz(self, mode : Literal["new", "modify"], index = -1):
        if(self.bEdit):  #에러 방지. 이미 수정중
            return
        self.bEdit = True
        #quiz 편집, 수정/삭제
        if(mode == "modify" and index >= 0):
            print(f"modify {index}")
            self.index = index
            #퀴즈를 가져옴
            self.quiz = dict(self.quizEditor.getQuiz(index))
        #새 퀴즈 생성           
        elif(mode == "new"):
            print("new")
            self.index = -1
            self.quiz = {}
        else:   #잘못된 모드 입력될 경우.
            self.bEdit = False
            return
        self.show() #이제 퀴즈 편집기 창을 보여줌.
    #퀴즈 저장 함수
    def done(self):
        if(not self.levelSpinbox.get().isnumeric()):
            self.showWarning("Level은 정수만 입력해야 합니다.")
            return
        elif(not(1 <= self.levelVar.get() <= 100)):
            self.showWarning("Level은 1부터 100 사이의 값이어야 합니다.")
            return
        if(self.quiz["type"] & (QuizType.선다형 | QuizType.단답형) == (QuizType.선다형 | QuizType.단답형)):
            self.showWarning("선다형과 단답형을 동시에 선택할 수 없습니다.")
            return
        if( not(self.quiz["type"] & (QuizType.선다형 | QuizType.단답형)) ):
            self.showWarning("선다형 또는 단답형 중 하나를 선택해야 합니다.")
            return
        if(self.quiz["type"] & QuizType.선다형):
            for option in self.optionList:
                if(not option.get(1.0,tk.END).strip()):
                    self.showWarning("선다형 문제는 Option을 모두 입력해야 합니다.")
                    return
        if(self.questionText.get(1.0,tk.END).strip() in ["None", ""]):
            self.showWarning("Question이 입력되지 않았습니다.")
            return
        if(self.answerText.get(1.0,tk.END).strip() in ["None", ""]):
            self.showWarning("정답이 입력되지 않았습니다.")
            return
        
        self.quiz['level'] = self.levelVar.get()
        self.quiz['question']  = self.questionText.get(1.0,tk.END).strip()
        self.quiz['answer']  = self.answerText.get(1.0,tk.END).strip()
        self.quiz['code'] = None if self.codeText.get(1.0,tk.END).strip() in ["None", ""] else self.codeText.get(1.0,tk.END).strip()
        self.quiz['hint'] = None if self.hintText.get(1.0,tk.END).strip() in ["None", ""] else self.hintText.get(1.0,tk.END).strip()
        if(self.quiz["type"] & QuizType.선다형):
            option = []
            for o in self.optionList:
                option.append(o.get(1.0,tk.END).strip())
            self.quiz['option'] = option
        else:
            self.quiz['option'] = None

        if(self.index == -1):
            self.quizEditor.addQuiz(self.quiz)

        else:
            self.quizEditor.modifyQuiz(self.index, self.quiz)

        self.hide()
        print(f"Done. {self.index}")
    
    #경고 메시지
    def showWarning(self, message):
        messagebox.showwarning("Warning", message)

    #퀴즈 종류 추가 후 갱신    
    def addQuizType(self, typename):
        print(typename)
        if(typename not in QuizType.__members__ and typename != ""):
            QuizType.addFlag(typename)
        self.hideCheckBtn()
        self.showCheckBtn()
    
    def setLevel(self):
        self.quiz['level'] = self.levelVar.get()

    #Level, Type 버튼 설정    
    def setCheckBtn(self):
        if(not self.quiz.get('level')):
            self.quiz['level'] = 1
        self.levelVar.set(value=self.quiz['level'])
        self.checkText.clear()
        self.bIsChecked.clear()
        self.checkBtn.clear()
        for i, qtype in enumerate(QuizType.__members__):
            self.checkText.append(tk.StringVar(value = qtype))
            self.bIsChecked.append(tk.BooleanVar(value = qtype in str(self.quiz.get('type'))))
            self.checkBtn.append(tk.Checkbutton(self.quizTypeTab, textvariable=self.checkText[i], variable=self.bIsChecked[i], command=lambda:self.checkType(qtype)))

        for bIC in self.bIsChecked:
            bIC.set(value = False)
        if(self.quiz.get('type')):
            for i in range(len(self.checkText)):            
                if(self.checkText[i].get() in str(self.quiz['type'])):
                    self.bIsChecked[i].set(True)
                    self.quiz['type'] |= QuizType[self.checkText[i].get()]
        else:
            self.quiz['type'] = 0    
    #Text 값 갱신
    def setText(self):
        self.questionText.delete(0.0,tk.END)
        self.questionText.insert(tk.END, str(self.quiz.get('question')))
        
        self.codeText.delete(0.0,tk.END)
        self.codeText.insert(tk.END, str(self.quiz.get('code')))
        
        self.answerText.delete(0.0,tk.END)
        self.answerText.insert(tk.END, str(self.quiz.get('answer')))

        self.hintText.delete(0.0,tk.END)
        self.hintText.insert(tk.END, str(self.quiz.get('hint')))
    
    #type 추가 함수
    def checkType(self, qtype : str):
        self.quiz['type'] = 0
        for i, checked in enumerate(self.bIsChecked):
            if(checked.get()):
                self.quiz['type'] |= QuizType[self.checkText[i].get()]
        print(self.quiz['type'])
        self.showOption()


    def update(self):
        self.hide()
        self.show()

    def show(self):
        self.bEdit = True
        self.place(x=150,y=50,width=1100,height=680)
        self.tab.select(0)
        self.tab.place(x=0,y=0,width=1100,height=680)
        self.setText()
        self.showText()
        
        self.showCheckBtn()

        self.showOption()

        self.doneBtn.place(x=930, y=300,width=150)
        self.cancelBtn.place(x=930, y=380,width=150)


    def showCheckBtn(self):
        self.setCheckBtn()
        self.levelLabel.pack()
        self.levelSpinbox.pack()

        for cb in self.checkBtn:
            cb.pack()
            
        self.addType.place(x=450,y=500)
        self.addTypeText.place(x=480,y=550,width=150,height=50)
      
    def showText(self):
        self.questionLabel.pack()
        self.questionText.pack()
        self.codeLabel.pack()
        self.codeText.pack()
        self.answerLabel.pack()
        self.answerText.pack()
        self.hintLabel.pack()
        self.hintText.pack()

    def showOption(self):
        if(self.quiz.get("type") & QuizType.선다형):
            for i in range(5):
                if(self.quiz.get('option')):
                    self.optionList[i].insert(tk.END, self.quiz['option'][i])
                self.optionList[i].pack()
        else:
            for i in range(5):
                self.optionList[i].pack_forget()





    def hide(self):
        self.doneBtn.place_forget()
        self.cancelBtn.place_forget()

        self.hideText()
        self.hideCheckBtn()

        self.hideOption()

        self.place_forget()
        self.bEdit = False   #종료

    
    def hideCheckBtn(self):
        self.levelLabel.pack_forget()
        self.levelSpinbox.pack_forget()
        for cb in self.checkBtn:
            cb.pack_forget()
        self.addTypeText.place_forget()
        self.addType.place_forget()

    def hideText(self):
        self.questionLabel.pack_forget()
        self.questionText.pack_forget()
        self.codeLabel.pack_forget()
        self.codeText.pack_forget()
        self.answerLabel.pack_forget()
        self.answerText.pack_forget()
        self.hintLabel.pack_forget()
        self.hintText.pack_forget()
        
    def hideOption(self):
        for i in range(5):
            self.optionList[i].delete(0.0,tk.END)
            self.optionList[i].pack_forget()

_root = tk.Tk()      #Tkinter 모듈의 Tk 클래스를 사용하여 창을 생성한다.
_q = QuizEditor(_root)   #QuizEditor의 인스턴스를 생성하여 root 창에서 게임을 실행한다.
_root.mainloop()     #root 창을 계속해서 업데이트, 이벤트 처리, 사용자 입력을 기다린다. 이것이 없으면 창이 바로 꺼진다.