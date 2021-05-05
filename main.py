import time
import os
import pygame
import random
pygame.font.init()

WIDTH,HEIGHT=720,720
WIN=pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Space Invaders")
#load images
RED_SHIP=pygame.image.load(os.path.join("assets","pixel_ship_red_small.png"))
GREEN_SHIP=pygame.image.load(os.path.join("assets","pixel_ship_green_small.png"))
BLUE_SHIP=pygame.image.load(os.path.join("assets","pixel_ship_blue_small.png"))

# player ship
YELLOW_SHIP=pygame.image.load(os.path.join("assets","pixel_ship_yellow.png"))
# Lasers
RED_LASER=pygame.image.load(os.path.join("assets","pixel_laser_red.png"))
YELLOW_LASER=pygame.image.load(os.path.join("assets","pixel_laser_yellow.png"))
BLUE_LASER=pygame.image.load(os.path.join("assets","pixel_laser_blue.png"))
GREEN_LASER=pygame.image.load(os.path.join("assets","pixel_laser_green.png"))
#Background
BG=pygame.transform.scale(pygame.image.load(os.path.join("assets","background-black.png")),(WIDTH,HEIGHT))

class Laser:
    def __init__(self,x,y,img):
        self.x=x
        self.y=y
        self.img=img
        self.mask=pygame.mask.from_surface(self.img)
    def offscreen(self):
        return not self.y>=HEIGHT and self.y<=0
    def draw(self,window):
        window.blit(self.img,(self.x,self.y))
    def move(self,vel):
        self.y+=vel
    def collision(self,obj):
        return collide(self,obj)


class Ship:
    COOLDOWN = 30
    def __init__(self,x,y,health=100):
        self.x=x
        self.y=y
        self.health=health
        self.ship_img = None
        self.laser_img = None
        self.lasers=[]
        self.cool_down= 0
    def cooldown(self):
        if self.cool_down >= self.COOLDOWN:
            self.cool_down = 0
        elif self.cool_down > 0:
            self.cool_down+=1
    def shoot(self):
        if self.cool_down==0:
            laser=Laser(self.x,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down = 1

    def draw(self,window):
        #pygame.draw.rect(window,(255,0,0),(self.x,self.y,50, 50))
        window.blit(self.ship_img,(self.x,self.y))
        for laser in self.lasers:
            laser.draw(window)
    def move_lasers(self,vel,obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.offscreen():
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health-=10
                self.lasers.remove(laser)


    def get_width(self):
        return self.ship_img.get_width()
    def get_height(self):
        return self.ship_img.get_height()

class PlayerShip(Ship):
    def __init__(self,x,y,health=100):
        super().__init__(x,y,health)
        self.ship_img=YELLOW_SHIP
        self.laser_img=YELLOW_LASER
        self.mask=pygame.mask.from_surface(self.ship_img)
        self.max_health= health
    def move_lasers(self,vel,objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.offscreen():
                self.lasers.remove(laser)
            else: 
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class EnemyShip(Ship):
    Color_Map={
        "red": (RED_SHIP,RED_LASER),
        "green": (GREEN_SHIP,GREEN_LASER),
        "blue": (BLUE_SHIP,BLUE_LASER)

    }
    def __init__(self,x,y,color,health=100):
        super().__init__(x,y,health)
        self.ship_img,self.laser_img= self.Color_Map[color]
        self.mask=pygame.mask.from_surface(self.ship_img)
    def move(self,vel):
        self.y+=vel
        

def collide(obj1,obj2):
    offset_x = -(obj1.x-obj2.x)
    offset_y = -(obj1.y-obj2.y)
    return obj1.mask.overlap(obj2.mask,(offset_x,offset_y)) != None




def main():
    run = True
    FPS=60
    level=0
    lives=5
    main_font=pygame.font.SysFont("comicsans", 50)
    lost_font=pygame.font.SysFont("comicsans", 70)
    player_vel=5
    clock=pygame.time.Clock()
    player=PlayerShip(300,550)

    enemies=[]
    wavelength=2
    enemy_vel=2
    laser_vel=5
    lost = False
    lost_count=0
    

    def redraw():
        WIN.blit(BG,(0,0))
        life_label=main_font.render(f"Lives Left:{lives}",1,(255,255,255))
        level_label=main_font.render(f"Level:{level}",1,(255,255,255))
        WIN.blit(life_label,(10,10))
        WIN.blit(level_label,(WIDTH-level_label.get_width()-10,10))
        
        for enemy in enemies:
            enemy.draw(WIN)
        if lost:
            lost_label=lost_font.render("You LOST!!!",1,(255,0,0))
            WIN.blit(lost_label,(WIDTH/2-lost_label.get_width()/2,350))

        player.draw(WIN)
        
        

        pygame.display.update()
    while run:
        clock.tick(FPS)
        redraw()
        
        
        if lives<=0 or player.health<=0:
            lost = True
            lost_count+=1

        
        
        if lost:
            if lost_count> FPS*5:
                run=False
            else:
                continue



        if len(enemies)==0:
            level+=1
            wavelength+=2
            if player.health<80:
                player.health+=20
            elif player.health>=80 and player.health!=100:
                player.health=100
            if player.COOLDOWN>10:
                player.COOLDOWN-=2
            for i in range(wavelength):
                enemy=EnemyShip(random.randrange(50,WIDTH-100), random.randrange(-1300,-250), random.choice(["red","blue","green"]))
                enemies.append(enemy)

        
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                quit()

        keys=pygame.key.get_pressed()

        if keys[pygame.K_a] and player.x - player_vel>=0:
            player.x-=player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() <= WIDTH:
            player.x+=player_vel
        if keys[pygame.K_w] and player.y - player_vel >= 0:
            player.y-=player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height()+15 <= HEIGHT :
            player.y+=player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()


        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
            if random.randrange(0,2*60)==1:
                enemy.shoot()
            if collide(enemy,player):
                player.health-=10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height()> HEIGHT:
                lives-=1
                enemies.remove(enemy)
            
        player.move_lasers(-laser_vel, enemies)
        
        
def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()