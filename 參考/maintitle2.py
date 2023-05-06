# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 18:29:53 2019

@author: fun86
"""

import pygame, win32con, win32gui, win32api

from subprocess import run

#讓聲音不延遲 buffer越大延遲越大 必須放在pygame.init前
pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.mixer.init()
pygame.init()

display_width = 800
display_height = 600

#color
black = (0,0,0)
white = (255,255,255)
gray = (122,127,128)
darkgray = (50,58,75)
red = (255,0,0)

#basic setting
gameDisplay = pygame.display.set_mode((display_width, display_height)) #Canvas
pygame.display.set_caption(u'臉部表情辨識及其在老態預防上的應用')
clock = pygame.time.Clock()

##############About title#####################

#sound
cursorSound = pygame.mixer.Sound('sound/Cursor1.wav')
enterSound = pygame.mixer.Sound('sound/Decision1.wav')
escSound = pygame.mixer.Sound('sound/Cancel1.wav')

#titleImg
titleNameImg = pygame.image.load('image/titleName5.png')
titleNameImg_en = pygame.image.load('image/titleName5_en.png')
titleBackGroundImg = pygame.image.load('image/TitleBackGround3.png').convert()
titleBackGroundImg.set_alpha(100)
titleRuleImg = pygame.image.load('image/rule4.png')

titlePracticeUp = pygame.image.load('image_btn/練習模式up.png')
titlePracticeDown = pygame.image.load('image_btn/練習模式down.png')
titleSingleUp = pygame.image.load('image_btn/單人闖關up.png')
titleSingleDown = pygame.image.load('image_btn/單人闖關down.png')
titleDoubleUp = pygame.image.load('image_btn/雙人對戰up.png')
titleDoubleDown = pygame.image.load('image_btn/雙人對戰down.png')
titleDesUp = pygame.image.load('image_btn/遊戲說明up.png')
titleDesDown = pygame.image.load('image_btn/遊戲說明down.png')
titleQuitUp = pygame.image.load('image_btn/結束遊戲up.png')
titleQuitDown = pygame.image.load('image_btn/結束遊戲down.png')
titleLV1Up = pygame.image.load('image_btn/第一關up.png')
titleLV1Down = pygame.image.load('image_btn/第一關down.png')
titleLV2Up = pygame.image.load('image_btn/第二關up.png')
titleLV2Down = pygame.image.load('image_btn/第二關down.png')
titleLV3Up = pygame.image.load('image_btn/第三關up.png')
titleLV3Down = pygame.image.load('image_btn/第三關down.png')

#titleFuction
def titleName(x,y):
    gameDisplay.blit(titleNameImg, (display_width*x, display_height*y))
    gameDisplay.blit(titleNameImg_en, (display_width*(x-0.05), display_height*(y+0.17)))

def titleBackGround():
    gameDisplay.blit(titleBackGroundImg, (0,0))

def text_objects(text, font, color):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()

def titleMenuMessageDisplay(text, x, y, color):
    textFont = pygame.font.Font('font/msjh.ttc', 32)
    TextSurf, TextRect = text_objects(text, textFont, color)
    TextRect.center = ((display_width * x), (display_height * y))
    gameDisplay.blit(TextSurf, TextRect)
    
def titleKeyBoardControlMessageDisplay():
    textFont = pygame.font.Font('font/msjh.ttc', 16)
    TextSurf, TextRect = text_objects('ESC返回 ENTER確定', textFont, white)
    TextRect.center = ((display_width * 0.9), (display_height * 0.97))
    gameDisplay.blit(TextSurf, TextRect)    
    
def titleCursorDisplay(x, y):
    titleMenuMessageDisplay('＞', x, y, white)

def titleMenuFuction(flag, preTarget):
    color = [white,white,white,white,white]
    for i in range(5):
        if(preTarget*10-5==i):
            color[i]=red
    if flag == 0:
        titleMenuMessageDisplay('練習關卡', 0.5, 0.5, color[0])
        if color[0] == white:titleShowImg(titlePracticeUp, 0.375, 0.46)
        else:titleShowImg(titlePracticeDown, 0.355, 0.46)
        titleMenuMessageDisplay('單人闖關', 0.5, 0.6, color[1])
        if color[1] == white:titleShowImg(titleSingleUp, 0.375, 0.56)
        else:titleShowImg(titleSingleDown, 0.355, 0.56)
        titleMenuMessageDisplay('雙人對戰', 0.5, 0.7, color[2])
        if color[2] == white:titleShowImg(titleDoubleUp, 0.375, 0.66)
        else:titleShowImg(titleDoubleDown, 0.355, 0.66)
        titleMenuMessageDisplay('遊戲說明', 0.5, 0.8, color[3])
        if color[3] == white:titleShowImg(titleDesUp, 0.375, 0.76)
        else:titleShowImg(titleDesDown, 0.355, 0.76)
        titleMenuMessageDisplay('結束遊戲', 0.5, 0.9, color[4])
        if color[4] == white:titleShowImg(titleQuitUp, 0.375, 0.86)
        else:titleShowImg(titleQuitDown, 0.355, 0.86)
    elif flag == 1:
        titleMenuMessageDisplay('練習關卡', 0.3, 0.5, gray)
        titleShowImg(titlePracticeUp, 0.175, 0.46)
        titleMenuMessageDisplay('單人闖關', 0.3, 0.6, darkgray)
        titleShowImg(titleSingleDown, 0.175, 0.56)
        titleMenuMessageDisplay('雙人對戰', 0.3, 0.7, gray)
        titleShowImg(titleDoubleUp, 0.175, 0.66)
        titleMenuMessageDisplay('遊戲說明', 0.3, 0.8, gray)
        titleShowImg(titleDesUp, 0.175, 0.76)
        titleMenuMessageDisplay('結束遊戲', 0.3, 0.9, gray)
        titleShowImg(titleQuitUp, 0.175, 0.86)
#        titleMenuMessageDisplay('第一關',0.5,0.6, color[1])
        if color[1] == white:titleShowImg(titleLV1Up, 0.455, 0.56)
        else:titleShowImg(titleLV1Down, 0.435, 0.56)
#        titleMenuMessageDisplay('第二關',0.5,0.7, color[2])
        if color[2] == white:titleShowImg(titleLV2Up, 0.455, 0.66)
        else:titleShowImg(titleLV2Down, 0.435, 0.66)
#        titleMenuMessageDisplay('第三關',0.5,0.8, color[3])
        if color[3] == white:titleShowImg(titleLV3Up, 0.455, 0.76)
        else:titleShowImg(titleLV3Down, 0.435, 0.76)

def titleShowImg(img, x, y):
    gameDisplay.blit(img, (display_width*x, display_height*y))
    
def startplay(i):
    global gameDisplay, display_width, display_height
    pygame.display.quit()
    if i == 0:
        run("python play_Practice.py",shell = True)
    elif i == 1:
#        os.system("python play.py")
        run("python play_Multithreading_test_life.py",shell = True)
    elif i == 2:
#        os.system("python play2.py")
        run("python play2_Multithreading_test_1cam_win.py",shell = True)
    gameDisplay = pygame.display.set_mode((display_width, display_height)) #Canvas
    pygame.display.set_caption(u'臉部表情辨識及其在老態預防上的應用')
    movemenu()

def movemenu():
    window = win32gui.FindWindow(None ,u'臉部表情辨識及其在老態預防上的應用') #找到遊戲主視窗
    windowrect = win32gui.GetWindowRect(window) #抓到主視窗的位置
    #抓取螢幕解析度
    screenx = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    screeny = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    win32gui.MoveWindow(window, int(screenx/2 - (windowrect[2]-windowrect[0])/2), 100, windowrect[2]-windowrect[0], windowrect[3]-windowrect[1], True) #移動主視窗到指定位置
movemenu()
#########Game starting loop###################
def game_loop():
    
    #Location of title objects
    titleName_x = 0.04
    titleName_y = 0.08
    titleCursor_x = 0.4
    titleCursor_y = 0.6
    
    #TitleMenuVariable
    titleFlag = 0
    ingameFlag = 0
    
    gameExit = False
    while not gameExit:
      
        #check for the input
        #請注意浮點數的比較，若加法行不通時，記得使用round()做四捨五入
        if ingameFlag == 0: #Title Screen Do This One
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameExit = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        if titleFlag != 2:
                            cursorSound.play()
                            titleCursor_y -= 0.1
                        if titleFlag == 0:
                            if titleCursor_y < 0.5:
                                titleCursor_y = 0.9
                        elif titleFlag == 1:
                            if titleCursor_y < 0.6:
                                titleCursor_y = 0.8
                    elif event.key == pygame.K_DOWN:
                        if titleFlag != 2:
                            cursorSound.play()
                            titleCursor_y += 0.1
                        if titleFlag == 0:                                
                            if titleCursor_y > 0.9:
                                titleCursor_y = 0.5
                        elif titleFlag == 1:
                            if titleCursor_y > 0.8:
                                titleCursor_y = 0.6
                    elif event.key == pygame.K_RETURN:
                        enterSound.play()
                        if titleFlag == 0 and round(titleCursor_y, 1) == 0.5:
                            startplay(0)
                        elif titleFlag == 0 and round(titleCursor_y, 1) == 0.6:
                            titleFlag = 1
                        elif titleFlag == 1:  #單人闖關進入點
                            f1 = open('level.txt','w')
                            if round(titleCursor_y, 1) == 0.6:
                                f1.write('1')
                            elif round(titleCursor_y, 1) == 0.7:
                                f1.write('2')
                            elif round(titleCursor_y, 1) == 0.8:
                                f1.write('3')
                            f1.close()
                            startplay(1)
                        elif titleFlag == 0 and round(titleCursor_y, 1) == 0.7:
                            startplay(2)
                        elif titleFlag == 0 and round(titleCursor_y, 1) == 0.8:
                            titleFlag = 2 #openRuleObject 
                        elif titleFlag == 0 and round(titleCursor_y, 1) == 0.9:
                            gameExit = True
                        
                        
                    elif event.key == pygame.K_ESCAPE:
                        escSound.play()
                        if titleFlag == 0:
                            titleCursor_y = 0.9
                        elif titleFlag == 1:
                            titleCursor_y = 0.6
                            titleFlag = 0
                        elif titleFlag == 2:
                            titleCursor_y = 0.8
                            titleFlag = 0
                            
                gameDisplay.fill(black)
                
                titleBackGround()
                if titleFlag != 2:
                    titleName(titleName_x,titleName_y)
                    titleMenuFuction(titleFlag, round(titleCursor_y, 1))
#                    titleCursorDisplay(titleCursor_x, titleCursor_y)
                if titleFlag == 2:
                    titleShowImg(titleRuleImg, 0, 0)
                titleKeyBoardControlMessageDisplay()
        pygame.display.update()
        clock.tick(60)
game_loop()
pygame.quit()
quit()
##############################################