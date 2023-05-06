import pygame, threading, time, numpy as np, matplotlib.pyplot as plt, win32gui, win32com.client, win32api, win32con
from scipy.spatial import distance

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
pygame.display.set_caption(u'AI打殭屍(PSOv2)')
clock = pygame.time.Clock()
pygame.mouse.set_visible(1) #隱藏滑鼠
gaming = True
shoot = False
maxspeed = False
show_hidden_point = True
fps = 60
score = 0
best_score = 0
ammo = 10
runtick = 0

#視窗位移
def movewindow():
    #抓取螢幕解析度
    screenx = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    window = win32gui.FindWindow(0, u'AI打殭屍(PSOv2)')
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
    plt.plot(best_fitness_array)    
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
shot = pygame.mixer.Sound('sound/xm1014_shot.wav')
reload = pygame.mixer.Sound('sound/reload2.wav')
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
gun = pygame.image.load('image/xm1014.png').convert_alpha()
gun_size = [150, 100]
gun = pygame.transform.scale(gun, gun_size)
gun_pos = [650,500]
fire = pygame.image.load('image/fire.png').convert_alpha()
fire_size = [177,100]
fire = pygame.transform.scale(fire, fire_size)
fire_pos = [gun_pos[0]-90,gun_pos[1]-40]


#bullet hole
bhole = pygame.image.load('image/bhole.png').convert_alpha()
bhole_size = 30
bhole = pygame.transform.scale(bhole,[bhole_size,bhole_size])
bhole_hidden = pygame.image.load('image/bhole_hidden.png').convert_alpha()
bhole_hidden = pygame.transform.scale(bhole_hidden,[bhole_size,bhole_size])
bhole_array = []
bhole_array_hidden = []

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

#PSO
generation = 0
particle_n = 0
particle_num = 10
particle_dim = 2
w = 0.3
c1 = 0.5
c2 = 0.7
class Particle_Class:   #隱藏點
    
    def __init__(self):
        self.fit = 0
        self.pb_fit = 0
        self.x = np.array([0]*particle_dim)
        self.v = np.array([0]*particle_dim)
        self.pb = np.copy(self.x)
    
    def get_fit(self):
        self.fit = 1.0 / (1.0 + distance.euclidean(self.x, [zombie_pos[0]+100, zombie_pos[1]+50])) #該隱藏點與殭屍的距離(根據體型調整位置)
        if self.fit >= self.pb_fit:
            self.pb_fit = self.fit
            self.pb = np.copy(self.x)

class PSO_Class:    #每一槍
    
    def __init__(self):
        self.gb_fit = 0
        self.gb = np.array([0]*particle_dim)
        self.particle = [Particle_Class() for i in range(particle_num)]
        for i in range(particle_num):
            for j in range(particle_dim):   
                self.particle[i].x[j] = np.random.randint(display_width)
                self.particle[i].x[j] = np.random.randint(display_height)
        self.gb = np.copy(self.particle[0].x)
        
    def get_all_fit(self):
        for i in range(particle_num):
            self.particle[i].get_fit()
            if self.particle[i].pb_fit >= self.gb_fit:
                self.gb_fit = self.particle[i].pb_fit
                self.gb = np.copy(self.particle[i].pb)
            
    def update(self):
        self.get_all_fit()
        for i in range(particle_num):
            for j in range(particle_dim):
                self.particle[i].v[j] = w*(self.particle[i].v[j]) + c1*np.random.rand()*(self.particle[i].pb[j] - self.particle[i].x[j]) + c2*np.random.rand()*(self.gb[j] - self.particle[i].x[j])
                self.particle[i].v[j] = round(self.particle[i].v[j])
                self.particle[i].x[j] += self.particle[i].v[j]
                if np.random.rand() < 0.1:  #Mutation
                    if j == 0: self.particle[i].x[j] = np.random.randint(display_width) 
                    if j == 1: self.particle[i].x[j] = np.random.randint(display_height) 
PSO = [PSO_Class() for i in range(10)]  #10槍各有10個隱藏的partical

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

best_fitness_array = []
move_y = 5
def zombie_moving():    #殭屍移動
    global zombie_pos, score, ammo, best_score,bhole_array ,blood_array, runtick, particle_n, generation, best_fitness_array, move_y, PSO, bhole_array_hidden
    zombie_pos[0] -= 5
    if zombie_pos[1] > 300 : move_y = -5
    if zombie_pos[1] < 100 : move_y = 5
    zombie_pos[1] += move_y
    if zombie_pos[0]< -200:  #跑到底了，重置參數
#    if ammo == 0:   #子彈射完，particle跑完，重置參數
        zombie_pos = [800,200]  #重置位置
        move_y = 5
        if score > best_score: best_score = score
        score = 0
        ammo = 10
        bhole_array = []
        bhole_array_hidden = []
        blood_array = []
        runtick = 0
        reload.play()
        best_fitness_array.append(best_score)
        particle_n = 0
        generation += 1
        if auto_show_train_rate: show_train_rate()

#顯示區，越後面越上層
def canvas_display():
    global canvas
    while True:
#        canvas.fill(white)  #顯示白畫面
        canvas.blit(bg, bg_pos)
        showFont(u'得分：'+str(score)+u'，目前最高分：'+str(best_score),300,550)  #顯示得分
        showFont(f'Iteration: {generation}, 按a加速, 按d恢復, 按x顯示隱藏點: {str(show_hidden_point)}, 按z更新訓練率: {str(auto_show_train_rate)}' ,10,10) #顯示世代
        for i in range(len(bhole_array)):
            canvas.blit(bhole, bhole_array[i])  #顯示彈孔
        for i in range(len(blood_array)):
            canvas.blit(blood, blood_array[i])  #顯示血跡
        for i in range(len(bhole_array_hidden)):
            canvas.blit(bhole_hidden, bhole_array_hidden[i])   #顯示隱藏點
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
    global gaming, score, canvas, ammo, tzombie_moving, runtick, crosshair_pos, fps, PSO, particle_n, auto_show_train_rate, shoot, maxspeed, bhole_array_hidden, show_hidden_point
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
                elif event.key == pygame.K_x:
                    if show_hidden_point: show_hidden_point = False
                    else: show_hidden_point = True

        zombie_moving()
        
        if runtick > 24 and runtick % 12 == 0 and ammo > 0:  #每0.2秒自動射擊
            shoot_times = 10 - ammo
            PSO[shoot_times].update()   #先更新才知道哪個隱藏點最好
            crosshair_pos = np.copy([i-crosshair_size/2 for i in PSO[shoot_times].gb])    #準星位置
            bhole_array.append([i-bhole_size/2 for i in PSO[shoot_times].gb])  #紀錄彈孔位置
            bhole_array_hidden = []
            if show_hidden_point:   #紀錄隱藏點
                for i in range(particle_num): 
                    bhole_array_hidden.append(PSO[shoot_times].particle[i].x)
            shoot = True
            shot.play()
            ammo -= 1
            #命中判定
            if zombie_pos[0]+zombie_size[0]/3 < PSO[shoot_times].gb[0] < zombie_pos[0]+zombie_size[0]/3*2 and zombie_pos[1] < PSO[shoot_times].gb[1] < zombie_pos[1] + zombie_size[1]:
                if np.random.rand() < 0.5: zombie_pain0.play()
                else: zombie_pain1.play()
                blood_array.append([i-blood_size/2 for i in PSO[shoot_times].gb])  #紀錄血跡位置
                score += 1
#            PSO.particle[shoot_times].get_fit()  #更新該particle的fit
                
        #顯示區，越後面越上層
#        showFont('FPS：'+str(int(clock.get_fps())), 700, 10)    #顯示FPS
        
        runtick += 1
        clock.tick(fps)
    
game_loop()
pygame.quit()
quit()