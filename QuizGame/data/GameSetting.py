import os
import pygame

gameSetting = {'width' : 800,
            'height' : 1000,
            'fps' : 60}

currentDir = os.path.dirname(os.path.abspath(__file__))
quizFolder = os.path.join(currentDir, "quiz")
imageFolder = os.path.join(currentDir, "img")


#게임 시작
pygame.init()
screen = pygame.display.set_mode((gameSetting["width"],gameSetting["height"]))
clock = pygame.time.Clock()