import random
import json
import asyncio
from enum import IntFlag, auto
import os
import pygame 
import numpy as np
import math
import copy
import re
from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Iterable

gameSetting = {'width' : 800,
            'height' : 1000,
            'fps' : 144}

currentDir = os.path.dirname(os.path.abspath(__file__))
quizFolder = os.path.join(currentDir, "quiz")
imageFolder = os.path.join(currentDir, "img")
fontFolder = os.path.join(currentDir ,"font")

#게임 시작
pygame.init()
pygame.display.set_caption("[3조]데이터과학프로그래밍")
screen = pygame.display.set_mode((gameSetting["width"],gameSetting["height"]))
clock = pygame.time.Clock()

class GameSetting:
    gameOver = False