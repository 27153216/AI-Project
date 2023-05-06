import pygame, threading, time, numpy as np, matplotlib.pyplot as plt, win32gui, win32com.client, win32api, win32con
import tensorflow as tf
from tensorflow import keras
#import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error


#讓聲音不延遲 buffer越大延遲越大 必須放在pygame.init前
pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.mixer.init()
pygame.init()

#basic setting
display_width = 800
display_height = 600
white = (255,255,255)
black = (0,0,0)
orange = (255,165,0)
green = (0,255,0)
canvas = pygame.display.set_mode((display_width, display_height)) #Canvas
pygame.display.set_caption(u'AI打殭屍(TensorFlow)')
clock = pygame.time.Clock()
pygame.mouse.set_visible(1) #隱藏滑鼠
gaming = True
maxspeed = False
shoot = False
fps = 60
score = 0
best_score = 0
ammo = 10
runtick = 0

#視窗位移
def movewindow():
    #抓取螢幕解析度
    screenx = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    window = win32gui.FindWindow(0, u'AI打殭屍(TensorFlow)')
    #不加這兩行會出錯
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    windowrect = win32gui.GetWindowRect(window) #抓到主視窗的位置
    win32gui.MoveWindow(window, int(screenx/2 - (windowrect[2]-windowrect[0])), 100, windowrect[2]-windowrect[0], windowrect[3]-windowrect[1], True) #移動主視窗到指定位置
    try:
        window2 = win32gui.FindWindow(0, 'Figure 1')
        windowrect = win32gui.GetWindowRect(window2) #抓到圖表的位置
        win32gui.MoveWindow(window2, int(screenx/2), 100, windowrect[2]-windowrect[0], windowrect[3]-windowrect[1], True) #移動主視窗到指定位置
    except:
        None
    win32gui.SetForegroundWindow(window)    #置頂
movewindow()

auto_show_train_rate = True
def show_train_rate():    #顯示訓練率
    plt.clf()
    plt.subplot(211)
    plt.title('Train_rate')
    plt.plot(best_fitness_array)
    plt.grid()
    plt.subplot(212)
    plt.title('loss_rate')
    plt.plot(loss_arr0, label='x', color='blue')
    plt.plot(loss_arr1, label='y', color='orange')
    plt.legend()
    plt.grid()
    plt.pause(0.001)
    movewindow()

#showFont
font0 = pygame.font.Font('font/msjhbd.ttc', 18)
font1 = pygame.font.Font('font/ammo.ttf', 30)
def showFont( text, x, y, font=font0, color=white):
    global canvas
    text = font.render(text, 1, color)
    canvas.blit( text, (x,y))

#background
bg = pygame.image.load('image/background.png').convert()
bg_pos = [0, 0]

#sound
shot = pygame.mixer.Sound('sound/shot.wav')
reload = pygame.mixer.Sound('sound/reload.wav')
zombie_pain0 = pygame.mixer.Sound('sound/zombie_pain0.wav')
zombie_pain1 = pygame.mixer.Sound('sound/zombie_pain1.wav')
pygame.mixer.music.load('sound/Opera.mp3')
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(loops=-1)

#set_volume
def set_all_volume(v):  #0~1
    shot.set_volume(v/2)
    reload.set_volume(v)
    zombie_pain0.set_volume(v)
    zombie_pain1.set_volume(v)
set_all_volume(0.1)

#gun
gun = pygame.image.load('image/ak47.png').convert_alpha()
gun_size = 300
gun = pygame.transform.scale(gun,[gun_size,gun_size])
gun_pos = [500,300]
fire = pygame.image.load('image/fire.png').convert_alpha()
fire_size = [177,100]
fire = pygame.transform.scale(fire, fire_size)
fire_pos = [gun_pos[0]+80,gun_pos[1]+120]


#bullet hole
bhole = pygame.image.load('image/bhole.png').convert_alpha()
bhole_size = 30
bhole = pygame.transform.scale(bhole,[bhole_size,bhole_size])
bhole_array = []

#blood
blood = pygame.image.load('image/blood0.png').convert_alpha()
blood_size = 50
blood = pygame.transform.scale(blood,[blood_size,blood_size])
blood_array = []

#crosshair
crosshair = pygame.image.load('image/crosshair.png').convert_alpha()
crosshair_size = 50
crosshair = pygame.transform.scale(crosshair,[crosshair_size,crosshair_size])
crosshair_pos = [0,0]

#zombie
zombie = [pygame.image.load('image/zombie-'+str(i)+'.png').convert_alpha() for i in range(14)]
zombie_size = [200,180]
zombie = [pygame.transform.scale(zombie[i], zombie_size) for i in range(14)]
zombie_pos = [800,200]
zombie_n = zombie[0]

def zombie_motion():    #殭屍動作
    zombie_i = 0
    global zombie_n
    while gaming:
        zombie_n = zombie[zombie_i]
        zombie_i += 1
        if zombie_i > 13: zombie_i = 0
        time.sleep(0.1)
tzombie_motion = threading.Thread(target = zombie_motion)
tzombie_motion.start()

move_y = 5
def zombie_moving():    #殭屍移動
    global zombie_pos, score, ammo, best_score,bhole_array ,blood_array, runtick, best_fitness_array, move_y, firstround, generation
    zombie_pos[0] -= 5
    if zombie_pos[1] > 300 : move_y = -5
    if zombie_pos[1] < 100 : move_y = 5
    zombie_pos[1] += move_y
    if zombie_pos[0]< -200:  #跑到底了，重置參數
        if firstround: 
            normalize()
            firstround = False
        zombie_pos = [800,200]  #重置位置
        move_y = 5
        if score > best_score: best_score = score
#        fitness_array.append(score) #該次分數就是該次chromosome的合適度
        score = 0
        ammo = 10
        bhole_array = []
        blood_array = []
        runtick = 0
#        chromosome += 1 #下一個chromosome
        reload.play()
        nextI()
#        if chromosome > chromosome_num-1: #所有chrosome跑完，下一個Generation後，重置相關參數
#            nextG() #計算下一個世代
        best_fitness_array.append(best_score)
#            fitness_array = []
#            chromosome = 0
        generation += 1
        if auto_show_train_rate: show_train_rate()
            
#TensorFlow
firstround = True
runtick_array = []
zombie_pos_array0 = []
zombie_pos_array1 = []
best_fitness_array = []
loss_arr0 = []
loss_arr1 = []
generation = 0

model0 = Sequential()
model0.add(Dense(5, activation='tanh', input_shape=(1,)))
model0.add(Dense(5, activation='tanh'))
model0.add(Dense(1, activation='linear'))
model0.compile(loss='mse', optimizer='sgd', metrics=['mse'])
model1 = Sequential()
model1.add(Dense(5, activation='tanh', input_shape=(1,)))
for i in range(10): #隱藏層數
    model1.add(Dense(10, activation='tanh'))
model1.add(Dense(1, activation='linear'))
model1.compile(loss='mse', optimizer='sgd', metrics=['mse'])

def normalize():    #標準化
    global runtick_array, zombie_pos_array0, zombie_pos_array1, zombie_pos_array0_max, zombie_pos_array1_max, zombie_pos_array0_min, zombie_pos_array1_min
    zombie_pos_array0_max = np.max(zombie_pos_array0)
    zombie_pos_array1_max = np.max(zombie_pos_array1)
    zombie_pos_array0_min = np.min(zombie_pos_array0)
    zombie_pos_array1_min = np.min(zombie_pos_array1)
    for i in range(len(runtick_array)):
        runtick_array[i][0] = runtick_array[i][0] / 199
        zombie_pos_array0[i][0] = (zombie_pos_array0[i][0]-zombie_pos_array0_min) / (zombie_pos_array0_max-zombie_pos_array0_min)
        zombie_pos_array1[i][0] = (zombie_pos_array1[i][0]-zombie_pos_array1_min) / (zombie_pos_array1_max-zombie_pos_array1_min)

def nextI():
    global model0, model1, shoot_pos0, shoot_pos1, runtick_array, zombie_pos_array0, zombie_pos_array1, loss_arr0, loss_arr1
    #訓練
    history0 = model0.fit(runtick_array, zombie_pos_array0, batch_size=1, epochs=1, shuffle=True, verbose=1)
    history1 = model1.fit(runtick_array, zombie_pos_array1, batch_size=1, epochs=1, shuffle=True, verbose=1)
    loss_arr0.append(history0.history['loss'][0])
    loss_arr1.append(history1.history['loss'][0])
    shoot_pos0 = model0.predict(runtick_array)  #根據runtick預測射擊點x
    shoot_pos1 = model1.predict(runtick_array)  #根據runtick預測射擊點y
    #去標準化
    for i in range(len(runtick_array)):
        shoot_pos0[i][0] = shoot_pos0[i][0] * (zombie_pos_array0_max-zombie_pos_array0_min) + zombie_pos_array0_min
        shoot_pos1[i][0] = shoot_pos1[i][0] * (zombie_pos_array1_max-zombie_pos_array1_min) + zombie_pos_array1_min
#    print(shoot_pos0)

#顯示區，越後面越上層
def canvas_display():
    global canvas
    while True:
#        canvas.fill(white)  #顯示白畫面
        canvas.blit(bg, bg_pos)
        showFont(u'得分：'+str(score)+u'，目前最高分：'+str(best_score),300,550)  #顯示得分
        showFont(u'Iteration：'+str(generation)+u', 按a加速, 按d恢復, 按z更新訓練率:'+str(auto_show_train_rate) ,10,10) #顯示世代
        for i in range(len(bhole_array)):
            canvas.blit(bhole, bhole_array[i])  #顯示彈孔
        for i in range(len(blood_array)):
            canvas.blit(blood, blood_array[i])  #顯示血跡
        canvas.blit(zombie_n, zombie_pos)   #顯示殭屍
        if shoot: canvas.blit(fire, fire_pos) #顯示槍火
        canvas.blit(gun, gun_pos)   #顯示槍
        showFont(str(ammo), 10, 550, font1, orange) #顯示彈藥量
        canvas.blit(crosshair, crosshair_pos)   #顯示準星
        pygame.display.update()
        clock.tick(60)
tcanvas_display = threading.Thread(target=canvas_display)
tcanvas_display.start()

#Game Loop
def game_loop():
    global gaming, score, canvas, ammo, tzombie_moving, runtick, crosshair_pos, fps, auto_show_train_rate, maxspeed, shoot
    while gaming:
        shoot = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gaming = False
            elif event.type == pygame.KEYDOWN:  #按鍵
                if event.key == pygame.K_ESCAPE:
                    gaming = False
                elif event.key == pygame.K_a:
                    if fps == 600: 
                        fps = 99999
                        maxspeed = True
                        pygame.display.update()
                        pygame.mixer.music.load('sound/Running in The 90s.mp3')
                        pygame.mixer.music.set_volume(0.1)
                        pygame.mixer.music.play(-1,25)
                    elif fps == 60: fps = 600
                    set_all_volume(0)
                elif event.key == pygame.K_d:
                    fps = 60
                    set_all_volume(0.1)
                    if maxspeed:
                        maxspeed = False
                        pygame.mixer.music.load('sound/Opera.mp3')
                        pygame.mixer.music.set_volume(0.2)
                        pygame.mixer.music.play(loops=-1)
                elif event.key == pygame.K_z:
                    if auto_show_train_rate: auto_show_train_rate = False
                    else: 
                        auto_show_train_rate = True
                        show_train_rate()
        
        zombie_moving()
        
        if firstround:  #第一回合紀錄殭屍位置及runtick
            zombie_pos_array0.append([zombie_pos[0]])
            zombie_pos_array1.append([zombie_pos[1]])
            runtick_array.append([runtick])
        
        if runtick > 24 and runtick % 12 == 0 and ammo > 0 and not firstround:  #每0.2秒自動射擊
            shoot_pos = [int(shoot_pos0[runtick]), int(shoot_pos1[runtick])]
            shoot_pos[0] += 100 #根據殭屍大小調整位置
            shoot_pos[1] += 50 #根據殭屍大小調整位置
#            print(shoot_pos)
            crosshair_pos = [i-crosshair_size/2 for i in shoot_pos]    #準星位置
            bhole_array.append([i-bhole_size/2 for i in shoot_pos])  #紀錄彈孔位置
            shoot = True
            shot.play()
            ammo -= 1
            #命中判定
            if zombie_pos[0]+zombie_size[0]/3 < shoot_pos[0] < zombie_pos[0]+zombie_size[0]/3*2 and zombie_pos[1] < shoot_pos[1] < zombie_pos[1] + zombie_size[1]:
                if np.random.rand() < 0.5: zombie_pain0.play()
                else: zombie_pain1.play()
                blood_array.append([i-blood_size/2 for i in shoot_pos])  #紀錄血跡位置
                score += 1
                
#        showFont('FPS：'+str(int(clock.get_fps())), 700, 10)    #顯示FPS
        
        runtick += 1
        clock.tick(fps)
    
game_loop()
pygame.quit()
quit()