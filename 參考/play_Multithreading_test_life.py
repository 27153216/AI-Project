# encoding: utf-8

import os, sys, random,  threading, time, win32con, win32gui, win32api
import pygame 
#from pygame.locals import *
 
from drew import *
from subprocess import run

import cv2
import numpy as np
############################Define the DNN#####################
#取得輸出層
def get_output_layers(net):
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return output_layers

#劃出預測
def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
    label = str(classes[class_id])
    color = COLORS[class_id]
    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)
    cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 2)

#設定label names
classes = None
with open('obj.names', 'r') as f:
    classes = [line.strip() for line in f.readlines()]
    
cap = cv2.VideoCapture(0)
#COLORS = np.random.uniform(0, 255, size=(len(classes), 3))
COLORS = [(0,0,255),(0,255,255),(0,255,0),(255,0,0),(255,255,0)]

net = cv2.dnn.readNet('yolov3-tiny_last.weights', 'yolov3-tiny.cfg')
####################################################################
#讓聲音不延遲 buffer越大延遲越大 必須放在pygame.init前
pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512) 
pygame.mixer.init()
#sound
brickSound = pygame.mixer.Sound("sound/Chime2.wav")
brickSound.set_volume(0.5)
paddleSound = pygame.mixer.Sound("sound/Blow1.wav")
paddleSound.set_volume(0.5)
ballSound = pygame.mixer.Sound("sound/Attack2.wav")
ballSound.set_volume(0.5)
diedSound = pygame.mixer.Sound("sound/Died.wav")
fallSound = pygame.mixer.Sound("sound/Fall2.wav")
fallSound.set_volume(0.5)
winSound = pygame.mixer.Sound("sound/Win.wav")
winSound.set_volume(0.5)
# 視窗大小.
canvas_width = 800  #原本800
canvas_height = 600  #原本600
 
# 顏色.
block = (0,0,0)
 
# 磚塊數量串列.
bricks_list = []
 
# 移動速度請改下方resetgame
dx =  0
dy = -0
 
# 遊戲狀態.
# 0:等待開球
# 1:遊戲進行中
game_mode = 0

#讀取遊戲關卡
f = open('level.txt','r')
level = f.read()

#難度決定板子左右速度
rightx = 0
leftx = 0
if level == '1':
    rightx = 5
    leftx = -rightx
elif level == '2':
    rightx = 8
    leftx = -rightx
elif level == '3':
    rightx = 12
    leftx = -rightx
 
#-------------------------------------------------------------------------
# 函數:秀字.
#-------------------------------------------------------------------------
def showFont( text, x, y):
    global canvas    
    text = font.render(text, 1, (255, 255, 255)) 
    canvas.blit( text, (x,y))
 
#-------------------------------------------------------------------------
# 函數:碰撞判斷.
#   x       : x 
#   y       : y 
#   boxRect : 矩形
#-------------------------------------------------------------------------
def isCollision( x, y, boxRect):
    if (x >= boxRect[0] and x <= boxRect[0] + boxRect[2] and y >= boxRect[1] and y <= boxRect[1] + boxRect[3]):
        return True;          
    return False;  
 
#-------------------------------------------------------------------------
# 函數:初始遊戲.
#-------------------------------------------------------------------------
def resetGame():
    # 宣告使用全域變數.
    global game_mode, brick_num, bricks_list, dx, dy, brick_quantity, Collision, life
 
    # 磚塊
    for bricks in bricks_list:
        # 亂數磚塊顏色
        r = random.randint(100,200)
        g = random.randint(100,200)
        b = random.randint(100,200)
        bricks.color = [r,g,b]        
        # 開啟磚塊.
        bricks.visivle = True
    # 0:等待開球
    game_mode = 0
    # 磚塊數量.
    brick_num = brick_quantity    
    # 移動速度.
    dx =  10
    dy = -10
    #生命值
    life = 5
    if level == '1':
        dx =  3
        dy = -3
    elif level == '2':
        dx =  5
        dy = -5
    elif level == '3':
        dx =  8
        dy = -8
    Collision = False
    
#臉部偵測
def detect():
    global game_mode, dx, dy, running
    ret, image = cap.read()
    image = cv2.flip(image,1) #水平翻轉，使觀看更直覺
    Width = image.shape[1]
    Height = image.shape[0]
    scale = 0.00392
    
    
    blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(get_output_layers(net))
    
    class_ids = []
    confidences = []
    boxes = []
    conf_threshold = 0.5
    nms_threshold = 0.4
    
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * Width)
                center_y = int(detection[1] * Height)
                w = int(detection[2] * Width)
                h = int(detection[3] * Height)
                x = center_x - w / 2
                y = center_y - h / 2
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])
        
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
    returnx = 0
    for i in indices:
        i = i[0]
        emotion = str(classes[class_ids[i]])
        print(emotion)
        box = boxes[i]
        xxx = box[0]
        yyy = box[1]
        www = box[2]
        hhh = box[3]
        draw_prediction(image, class_ids[i], confidences[i], round(xxx), round(yyy), round(xxx+www), round(yyy+hhh))
        
        if emotion== "neutral":
            returnx = 0
        elif emotion == "sad": 
            returnx = leftx
        elif emotion == "angry": #這個不好偵測，但戴上眼鏡都是angry
            if game_mode == 0:
                waitballst()
                ballSound.play()
                if dx > 0:
                    dx = -dx
                game_mode = 1
            returnx = leftx
        elif emotion == "happy":
            returnx = rightx
        elif emotion == "surprised":
            if game_mode == 0:
                waitballst()
                ballSound.play()
                if dx < 0:
                    dx = -dx
                game_mode = 1
            returnx = rightx
        break
    cv2.imshow("Facial Detection", image) #顯示畫面
    k = cv2.waitKey(1)
    if k == 27:running = False
    
    return returnx
        
def backtomenu():
#    os.system("exit()")
#    os.system("python maintitle2.py")
    
    run("python maintitle2.py", shell = True)
    


# 初始.
pygame.init()

# 顯示Title.
pygame.display.set_caption(u"臉部表情辨識及其在老態預防上的應用--單人闖關")
# 建立畫佈大小.
canvas = pygame.display.set_mode((canvas_width, canvas_height))
# 時脈.
clock = pygame.time.Clock()
 
# 設定字型-黑體.
font = pygame.font.Font('font/msjhbd.ttc', 18)
 
# 底板.
paddle_x = 0
paddle_y = (canvas_height - 48)
paddle = Box(pygame, canvas, "paddle", [paddle_x, paddle_y, 200, 15], (255,255,255))
 
# 球.
ball_x = paddle_x
ball_y = paddle_y
ball   = Circle(pygame, canvas, "ball", [ball_x, ball_x], 8, (255,255,255))
 
# 建立磚塊
brick_num = 0
brick_x = 70
brick_y = 60
brick_w = 0
brick_h = 0

#磚塊數量
if level == '1':
    brick_quantity = 11
elif level == '2':
    brick_quantity = 33
elif level == '3':
    brick_quantity = 99
#brick_quantity = int(input("請輸入磚塊數量："))
for i in range( 0, brick_quantity):
    if((i % 11)==0):
        brick_w = 0
        brick_h = brick_h + 18        
    bricks_list.append (Box(pygame, canvas, "brick_"+str(i), [  brick_w + brick_x, brick_h+ brick_y, 58, 16], [255,255,255]))
    brick_w = brick_w + 60
# 初始遊戲.
resetGame()
 
#-------------------------------------------------------------------------    
# 主迴圈.
#-------------------------------------------------------------------------
running = True
dps = pygame.time.Clock() #第二個tick避免影響FPS
dps2 = pygame.time.Clock() #第二個tick避免影響FPS

movex = 0 #板子移動距離
#用臉部表情判斷板子如何移動
def movepaddle():
    global paddle_x, movex
    while running:
        movex = detect() #臉部偵測移動板子距離
        dps2.tick(15) #每秒臉部偵測次數
t = threading.Thread(target = movepaddle)
t.start()
#用來優化板子移動順暢
def smoothpaddle():
    global paddle_x, movex
    while running:
        paddle_x += movex
        if paddle_x > canvas_width - paddle.rect[2]:  #不出右邊界
            paddle_x = canvas_width - paddle.rect[2]
        if paddle_x <= 0:  #不出左邊界
            paddle_x = 0
        dps.tick(60)
t2 = threading.Thread(target = smoothpaddle)
t2.start()



window = win32gui.FindWindow(None ,u'臉部表情辨識及其在老態預防上的應用--單人闖關') #找到遊戲主視窗
windowrect = win32gui.GetWindowRect(window) #抓到主視窗的位置
#抓取螢幕解析度
screenx = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
screeny = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
win32gui.MoveWindow(window, int(screenx/2 - (windowrect[2]-windowrect[0])/2), 100, windowrect[2]-windowrect[0], windowrect[3]-windowrect[1], True) #移動主視窗到指定位置

#移動攝影機視窗
def movewindow():
    while running:
        windowrect = win32gui.GetWindowRect(window)
    #    print(windowrect[0],windowrect[1],windowrect[2],windowrect[3]) #0:左上x 1:左上y 2右下x 3右下y
        #把攝影機畫面移到主視窗旁
        cv2.moveWindow("Facial Detection",windowrect[2],windowrect[1])
        dps.tick(15)
t3 = threading.Thread(target=movewindow)
t3.start()

def ballfall():
    global life, game_mode
    fallSound.play()
    life -= 1
    game_mode = 0

def died():
    global canvas, running
    canvas.fill((0,0,0))
    dying = True
    diedimg = pygame.image.load("image/died.png").convert()
    diedimg.set_alpha(0)
    diedSound.play()
    while dying:
        canvas.blit(diedimg,(0,0))
        if running == False: dying = False
        if diedimg.get_alpha() < 255: diedimg.set_alpha(diedimg.get_alpha() + 1)
        for event in pygame.event.get():
            # 離開遊戲.
            if event.type == pygame.QUIT:
                running = False
            # 判斷按下按鈕
            if event.type == pygame.KEYDOWN:
                # 判斷按下ESC按鈕
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RETURN:
                    resetGame()
                    dying = False
        pygame.display.update()
        dps.tick(30)
        
def gameover():
    global canvas, running
    winSound.play()
    canvas.fill((0,0,0))
    winning = True
    bigfont = pygame.font.Font('font/msjhbd.ttc', 144)
    smallfont = pygame.font.Font('font/msjhbd.ttc', 30)
    while winning:
        text = bigfont.render("You Win!", 1, (255, 255, 255)) 
        stext = smallfont.render("[Enter]重新開始                  [Esc]回主選單", 1, (255, 255, 255))
        canvas.blit( text, (70,180))
        canvas.blit( stext, (100,344))
        if running == False: winning = False
        for event in pygame.event.get():
            # 離開遊戲.
            if event.type == pygame.QUIT:
                running = False
            # 判斷按下按鈕
            if event.type == pygame.KEYDOWN:
                # 判斷按下ESC按鈕
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RETURN:
                    resetGame()
                    winning = False
        pygame.display.update()
        dps.tick(30)
        
def waitballst():
    global ball, ball_x, ball_y, paddle
    ball.pos[0] = ball_x = paddle.rect[0] + ( (paddle.rect[2] - ball.radius) >> 1 )
    ball.pos[1] = ball_y = paddle.rect[1] - ball.radius
    
while running:
    #---------------------------------------------------------------------
    # 判斷輸入.
    #---------------------------------------------------------------------
    for event in pygame.event.get():
        # 離開遊戲.
        if event.type == pygame.QUIT:
            running = False
        # 判斷按下按鈕
        if event.type == pygame.KEYDOWN:
            # 判斷按下ESC按鈕
            if event.key == pygame.K_ESCAPE:
#                t2 = threading.Thread(target = backtomenu)
#                t2.start()
                running = False
                
        # 判斷Mouse.
#        if event.type == pygame.MOUSEMOTION:
#            paddle_x = pygame.mouse.get_pos()[0] - 50
#        if event.type == pygame.MOUSEBUTTONDOWN:
#            if(game_mode == 0):
#                game_mode = 1
    
#    if paddle_x > canvas_width - paddle.rect[2]:  #不出右邊界
#        paddle_x = canvas_width - paddle.rect[2]
#    if paddle_x <= 0:  #不出左邊界
#        paddle_x = 0
                
    #---------------------------------------------------------------------    
    # 清除畫面.
    canvas.fill(block)
    
    # 磚塊
    for bricks in bricks_list:
        # 球碰磚塊.
        if(isCollision( ball.pos[0], ball.pos[1], bricks.rect)):
            if(bricks.visivle):                
                # 扣除磚塊.
                brickSound.play()
                brick_num = brick_num -1
                # 磚塊全破.
                if(brick_num <= 0):
                    gameover()
                    break
                # 球反彈.
                dy = -dy; 
            # 關閉磚塊.
            bricks.visivle = False
 
        # 更新磚塊.        
        bricks.update()
            
    #顯示磚塊數量和血量.
    showFont( u"磚塊數量:"+str(brick_num) + u" 生命值:" + str(life),   8, 2)            
 
    # 秀板子.
    paddle.rect[0] = paddle_x
    paddle.update()
 
    # 碰撞判斷-球碰板子.
    lastCollision = Collision #上次的碰撞
    Collision = isCollision( ball.pos[0], ball.pos[1], paddle.rect) #這次的碰撞
    if(Collision): 
        if lastCollision: #如果上次也是碰撞(卡入板子)直接死亡
            ballfall()
        else:
            paddleSound.play()
            # 球反彈.
            dy = -dy;         
            
    # 球.
    # 0:等待開球
    if(game_mode == 0):
        waitballst()
#        ball.pos[0] = ball_x = paddle.rect[0] + ( (paddle.rect[2] - ball.radius) >> 1 )
#        ball.pos[1] = ball_y = paddle.rect[1] - ball.radius
    # 1:遊戲進行中
    elif(game_mode == 1):
        ball_x += dx
        ball_y += dy
        #判斷死亡.
        if(ball_y + dy > canvas_height - ball.radius):
            ballfall()
        # 右牆或左牆碰撞.
        if(ball_x + dx > canvas_width - ball.radius or ball_x + dx < ball.radius):
            dx = -dx
        # 下牆或上牆碰撞
        if(ball_y + dy > canvas_height - ball.radius or ball_y + dy < ball.radius):
            dy = -dy
        ball.pos[0] = ball_x
        ball.pos[1] = ball_y
        
    if life <= 0:
        game_mode = 9
        died()
 
    # 更新球.
    ball.update()
 
    # 顯示FPS.
#    showFont( u"FPS:" + str(int(clock.get_fps())), 8, 2)
#    showFont( u"臉部FPS:" + str(int(dps2.get_fps())), 8, 20)
    # 更新畫面.
    pygame.display.update()
    clock.tick(60)
 
# 離開遊戲.
pygame.quit()
quit()