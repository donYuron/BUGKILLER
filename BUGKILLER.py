import os
import sys
import pygame
from random import choice

pygame.init()
screen = pygame.display.set_mode((768, 512))
clock = pygame.time.Clock()
running = True
bug_sprites = pygame.sprite.Group()
pygame.key.set_repeat (1, 50)         
all_sprites = pygame.sprite.Group()
space = pygame.sprite.Group()
bullets = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
boom = pygame.sprite.Group()
LASER = pygame.sprite.Group()
Ships = pygame.sprite.Group()
fps = 60


class Y_kord():
    y = 0
    killed = 0
    juk = 0
    povorot = 0
    
def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину    
    max_width = max(map(len, level_map))   
    return list(level_map)    


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image

class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x):
        super().__init__(tiles_group)
        self.image = tile_images[tile_type][0]
        self.rect = self.image.get_rect().move(
            128 * pos_x, (pos_y.y) + 200)
        
def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(7):
        for x in range(7):
            if level[y][x] == '1':
                Tile('mountains', x)
            elif level[y][x] == '2':
                Tile('S_crater', x)
            elif level[y][x] == '3':
                Tile('B_crater', x)
            elif level[y][x] == '4':
                Tile('stones', x)   
            elif level[y][x] == '@':
                Tile('S_crater', x)
                new_player = SpaceShip(x, y)
        if (level[y][0] == '1')or(level[y][0] == '2'):
            pos_y.y += 32
        else:
            pos_y.y += 64

    # вернем игрока, а также размер поля в клетках            
    return new_player, x, y

class Planet(pygame.sprite.Sprite):
    v = 1
    k = 1
    def __init__(self, name, x, y, v):
        super().__init__(all_sprites)
        self.image = load_image(name)
        self.v = v
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.x_pos = x
        self.rect.y = y
        self.clock = pygame.time.Clock()
        
    def update(self):
        self.x_pos -= self.k * int(self.v * self.clock.tick() / 1000)
        self.rect.x = self.x_pos
        Y_kord.juk = (Y_kord.juk + self.v) % 200
        if self.rect.x > 710:
            self.k = -1
        elif self.rect.x < 5:
            self.k = 1
    
class Boom(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows):
        super().__init__(boom)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]

        
    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame] 

class Space(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(space)
        self.image = load_image('2.png')
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0  

class SpaceShip(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(Ships)
        self.frames = []
        self.death = 0
        self.cut_sheet(load_image('Spaceships.png'), 5, 3)
        self.image = self.frames[0]
        self.rect.x = 150
        self.rect.y = y * 300

        
    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        frame_location = (self.rect.w * 4, self.rect.h * 1)
        self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.image = self.frames[0] 
        
class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self, field_size):
        self.dx = 2
        self.dy = 0
        self.field_size = field_size
        
    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x -= self.dx   
        # вычислим координату клетки, если она уехала влево за границу экрана
        if obj.rect.x < -obj.rect.width:
            obj.rect.x += (self.field_size[0]) * obj.rect.width
       
class NewPlanets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(load_image('CelestialObjects.png'))
        self.image = self.frames[0]
        self.rect.x = x 
        self.rect.y = y

        
    def cut_sheet(self, sheet):
        self.rect = pygame.Rect(0, 0, 120, 100)
        frame_location = (260, 0)
        self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.image = self.frames[0]  
        
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(bullets)
        self.frames = []
        self.frames.append(pygame.transform.flip(load_image('spark/frames/spark-preview1.png'), False, False))
        self.frames.append(pygame.transform.flip(load_image('spark/frames/spark-preview2.png'), False, False))
        self.frames.append(pygame.transform.flip(load_image('spark/frames/spark-preview3.png'), False, False))
        self.frames.append(pygame.transform.flip(load_image('spark/frames/spark-preview4.png'), False, False))
        self.frames.append(pygame.transform.flip(load_image('spark/frames/spark-preview5.png'), False, False))
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.cur_bullet = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = x + 12
        self.rect.y = y + 19
        
    def update(self, bugS):
        self.cur_bullet = (self.cur_bullet + 1) % len(self.frames)
        self.image = self.frames[self.cur_bullet] 
        self.rect.x += 10
        res = 0
        for bug in bugS:
            if pygame.sprite.collide_mask(self, bug[0]):
                bug[0].score += 1
                if bug[0].score == 20:
                    bug[0].death = 1
                    Y_kord.killed += 1
                self.kill()
                res = 1
        return res
                
            
class Laser(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(LASER) 
        self.image = load_image('laser_up.png')
        self.rect = self.image.get_rect()
        self.rect.x = -200
        
class BUG(pygame.sprite.Sprite):
    def __init__(self, x, way):
        super().__init__(bug_sprites)
        self.step = 5
        self.death = 0
        self.score = 0
        self.pos_x = ship.rect.x
        self.way = way
        
        self.frames_go = []
        self.frames_rotation = []
        self.frames_death = []
        self.frames_attack = []
        
        self.sheet_go = load_image('walk.png')
        self.sheet_rotation = load_image('walk_change_direction.png')
        self.sheet_death = load_image('death.png')
        self.sheet_attack = load_image('laser_attack_up.png')
        
        self.cut_sheet_go(self.sheet_go, 5, 4)
        self.cut_sheet_death(self.sheet_death, 6, 4)
        self.cut_sheet_rotation(self.sheet_rotation, 5, 4)
        self.cut_sheet_attack(self.sheet_attack, 10, 6)
        
        self.frames_rotation_1 = self.frames_rotation[:6]
        self.frames_rotation_2 = self.frames_rotation[5:]
        self.frames_rotation_2_mirror = self.frames_rotation[5:]
        self.mirror(self.frames_rotation_2_mirror)
        
        if self.way == 'RIGHT':
            self.step = -5
            self.mirror(self.frames_go)
            self.mirror(self.frames_death)
            self.mirror(self.frames_attack)
            self.mirror(self.frames_rotation_1)
            self.mirror(self.frames_rotation_2)
            self.mirror(self.frames_rotation_2_mirror)
        
        self.cur_frame_go = 0
        self.cur_frame_death = 0
        self.cur_frame_rotation_1 = 0
        self.cur_frame_rotation_2 = 0
        self.cur_frame_attack = 0
        
        self.attack_up = 0
        self.attack_attack = 0
        self.attack_down = 0
        
        self.image = self.frames_go[self.cur_frame_go]
                                          
        self.mask = pygame.mask.from_surface(self.image)
        
        self.rect.x = x
        self.rect.y = 300
        

        
    def cut_sheet_go(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames_go.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))
                
    def cut_sheet_death(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames_death.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))  
                
    def cut_sheet_rotation(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(3):
            for i in range(5):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames_rotation.append(pygame.transform.flip(sheet.subsurface(
                    (pygame.Rect(frame_location, self.rect.size))), True, False))
            
    def cut_sheet_attack(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames_attack.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size))) 
                
    def mirror(self, frames):
        for im in range(len(frames)):
            frames[im] = pygame.transform.flip(frames[im], True, False) 

    def update_go(self): 
        self.rect.y = 300
        Y_kord.povorot = 0
        if self.cur_frame_go == 18:
            self.cur_frame_go = 0
        else:
            self.cur_frame_go = (self.cur_frame_go + 1) % len(self.frames_go)
        self.image = self.frames_go[self.cur_frame_go] 
        self.rect.x -= self.step 
        if pygame.sprite.collide_mask(self, ship):
            ship.kill()
            ship.death = 1
                
    def update_death(self):
        self.rect.y = 300
        if self.cur_frame_death == 23:
            self.cur_frame_death = 23 
        else:
            self.cur_frame_death = (self.cur_frame_death + 1) % len(self.frames_death)
        self.image = self.frames_death[self.cur_frame_death] 
        self.mask = pygame.mask.from_surface(self.image)
        self.step = 2
        self.rect.x -= self.step
        if self.rect.x < -300:
            self.kill()    
            
    def update_rotation_1(self):
        self.rect.y = 260
        if self.cur_frame_rotation_1 == 5:
            self.cur_frame_rotation_1 = 0
            self.attack_up = 1
        else:        
            self.cur_frame_rotation_1 = (self.cur_frame_rotation_1 + 1) % len(self.frames_rotation_1)
            self.image = self.frames_rotation_1[self.cur_frame_rotation_1] 
            
    def update_rotation_2(self):
        self.rect.y = 260
        if self.cur_frame_rotation_2 == 9:
            self.cur_frame_rotation_2 = 0
            self.attack_down = 1
        else:        
            self.cur_frame_rotation_2 = (self.cur_frame_rotation_2 + 1) % len(self.frames_rotation_2)
            self.image = self.frames_rotation_2[self.cur_frame_rotation_2]  
            
    def update_rotation_2_mirror(self):
        self.rect.y = 260
        if self.cur_frame_rotation_2 == 9:
            self.cur_frame_rotation_2 = 0
            self.attack_down = 1
        else:        
            self.cur_frame_rotation_2 = (self.cur_frame_rotation_2 + 1) % len(self.frames_rotation_2)
            self.image = self.frames_rotation_2_mirror[self.cur_frame_rotation_2]
            
    def update_attack(self, laser):
        self.cur_frame_attack = (self.cur_frame_attack + 1) % len(self.frames_attack)
        if (self.cur_frame_attack >= 20)and(self.cur_frame_attack <= 40):
            if pygame.sprite.collide_mask(laser, ship):
                ship.kill()
                ship.death = 1
            laser.rect.x = self.rect.x + 36
            laser.rect.y = -400
        else:
            laser.rect.x = -200
        if self.cur_frame_attack == 59:           
            self.attack_attack = 1
        self.image = self.frames_attack[self.cur_frame_attack]         

def terminate():
    pygame.quit()
    sys.exit()
                
def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('bulkhead-wallsx1.png'), (768, 512))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 250
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 150
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(fps)
        
def bug_update(bug, laser):
    if bug.death:
        bug.update_death()
        laser.rect.x = -500
    elif (bug.rect.x == bug.pos_x - 70):
        if bug.attack_up == 0:
            bug.update_rotation_1()
        elif bug.attack_attack == 0:
            bug.update_attack(laser)
        else:
            if ((bug.rect.x < ship.rect.x - 65)and(bug.way == 'RIGHT'))or((bug.rect.x > ship.rect.x - 65)and(bug.way =='LEFT')):
                bug.update_rotation_2_mirror()
            else:      
                bug.update_rotation_2()
            
        if (bug.attack_up + bug.attack_attack + bug.attack_down) == 3:
            
            bug.attack_up = 0
            bug.attack_attack = 0
            bug.attack_down = 0
            if ship.death:
                bug.pos_x = -300
            else:
                bug.pos_x = ship.rect.x
            
            if bug.pos_x - 70 > bug.rect.x:
                bug.step = -5  
                if bug.way == 'LEFT':
                    bug.mirror(bug.frames_go)
                    bug.mirror(bug.frames_death)
                    bug.mirror(bug.frames_rotation_1)
                    bug.mirror(bug.frames_rotation_2)
                    bug.mirror(bug.frames_rotation_2_mirror)
                    bug.way = 'RIGHT'
            else:
                bug.step = 5
                if bug.way == 'RIGHT':
                    bug.mirror(bug.frames_go)
                    bug.mirror(bug.frames_death)
                    bug.mirror(bug.frames_rotation_1)
                    bug.mirror(bug.frames_rotation_2)
                    bug.mirror(bug.frames_rotation_2_mirror)
                    bug.way = 'LEFT'
    else:
        bug.update_go()

start_screen() 

pos_y = Y_kord()
tile_images = {
    'mountains': (load_image('Surface_Layer1.png'), 32),
    'S_crater': (load_image('Surface_Layer2.png'), 32),
    'B_crater': (load_image('Surface_Layer3.png'), 64),
    'stones': (load_image('Surface_Layer4.png'), 64)
} 
ship, level_x, level_y = generate_level(load_level('map.txt'))         
dist = 5
Zemlia = Planet('Terran.png',600, 80, 29)
SPASE = Space()
bom = Boom(load_image('explotions/explosion-4.png'),12, 1)
Ships.draw(screen)
tfboom = 13
camera = Camera((7, 7))
bullist = []
GdeBug = 0
nomer_bullet = 0
BIGBUGs = []
GdeBug = 1 

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
                       
        elif event.type == pygame.MOUSEBUTTONUP:
            tfboom = 15
            bullist.append([Bullet(ship.rect.x, ship.rect.y), 1])
            bom.cur_frame = 0
            bom.rect.x = event.pos[0] - 65
            bom.rect.y = event.pos[1] - 105
            
        key = pygame.key.get_pressed() 
        
        if event.type == pygame.KEYDOWN:           
            if (event.key == pygame.K_DOWN) and (ship.rect.top + dist < 440):
                ship.rect.top += dist
            elif (key[pygame.K_UP]) and (ship.rect.top - dist > 0):
                ship.rect.top -= dist
            if (key[pygame.K_RIGHT]) and (ship.rect.left + dist < 720):
                ship.rect.left += dist
            elif (key[pygame.K_LEFT]) and (ship.rect.left - dist > 0):
                ship.rect.left -= dist 
                
    space.draw(screen)
    
    for bul_num in bullist:
        if bul_num[1] == 1:
            result = bul_num[0].update(BIGBUGs)
        if bul_num[0].rect.x > 770 or result == 1:
            bul_num[1] = 0
                  
    for sprites in tiles_group:
        camera.apply(sprites)
    
    if Y_kord.juk == 0:
        WAY = choice(('RIGHT' , 'LEFT'))
        if WAY == 'RIGHT':
            BIGBUGs.append([BUG(-1500, WAY), Laser()])
        else:
            BIGBUGs.append([BUG(1500, WAY), Laser()])
        
    Zemlia.update()
    ship.update()
    
    for i in BIGBUGs:
        bug_update(i[0], i[1])
    
    all_sprites.draw(screen)
    tiles_group.draw(screen)
    bug_sprites.draw(screen)
    bullets.draw(screen)
    Ships.draw(screen)   
    LASER.draw(screen)
    if tfboom < 12:
        boom.draw(screen) 
        bom.update()
        tfboom += 1 
    pygame.display.flip()
    clock.tick(30)
    
pygame.quit()  