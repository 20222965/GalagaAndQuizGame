import time

class Timer:
    __startTime = None    #시작 시간 저장
    __isPaused = False    #현재 퍼즈 상태인지 확인
    __pauseTime = 0       #퍼즈 시간
    @classmethod
    def start(cls):     #타이머 시작
        if(cls.__startTime is not None):
            raise RuntimeError("타이머가 이미 시작되었습니다.")
        cls.__startTime = time.time()

    @classmethod
    def getElapsedTime(cls):   #타이머 시작 후 경과시간 반환
        if cls.__startTime is None:
            raise RuntimeError("타이머가 시작되지 않았습니다. Timer.start()")
        return time.time() - cls.__startTime
    
    @classmethod
    def getDeltaTime(cls, preElapsedTime):    #현재 경과 시간과 입력 받은 시간의 차를 반환
        if cls.__startTime is None:
            raise RuntimeError("타이머가 시작되지 않았습니다. Timer.start()")
        return (time.time() - cls.__startTime) - preElapsedTime
    
    @classmethod
    def pause(cls):
        if not cls.__isPaused:
            cls.__pauseTime = time.time() - cls.__startTime  # 퍼즈된 시간 업데이트
            cls.__isPaused = True
    
    @classmethod
    def resume(cls):
        if cls.__isPaused:
            cls.__startTime = time.time() - cls.__pauseTime  # 시작 시간을 퍼즈된 시간을 고려하여 조정
            cls.__isPaused = False
            cls.__pauseTime = 0  # 퍼즈된 시간 초기화