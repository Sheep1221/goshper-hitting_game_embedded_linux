#for game
import sys, time
import random
import pygame
from pygame.locals import Color, QUIT, MOUSEBUTTONDOWN, USEREVENT, USEREVENT
#for gpio & gyro
import board
import busio
import adafruit_lsm9ds0
import Adafruit_BBIO.GPIO as GPIO
from Adafruit_I2C import Adafruit_I2C

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GOPHER_WIDTH = 300
GOPHER_HEIGHT = 200
HAMMER_WIDTH = 200
HAMMER_HEIGHT = 300
WHITE = (255, 255, 255)
FPS = 6



def get_random_position(window_width, window_height):
    random_x = (random.randint(0,2)) * window_width * 1/4
    random_y = (random.randint(0,1)+1) * window_width * 1/4

    return random_x, random_y

def get_hammer_position(window_width, window_height):
    hammer_x = window_width*1/3
    hammer_y = window_height*1/2

    return hammer_x, hammer_y

class Hammer(pygame.sprite.Sprite):
    def __init__(self, width, height, hammer_x, hammer_y, window_width, window_height):
        super().__init__()
        self.raw_image = pygame.image.load('./hammer.png').convert_alpha()
        self.image = pygame.transform.rotozoom(self.raw_image, 45, 0.8)
        self.image_hit = pygame.transform.rotozoom(self.image, 45, 1)
        self.rect = self.image.get_rect() #return position
        self.rect.topleft = (hammer_x, hammer_y)
        self.width = width
        self.height = height
        self.window_width = window_width
        self.window_height = window_height


class Gopher(pygame.sprite.Sprite):
    def __init__(self, width, height, random_x, random_y, window_width, window_height):
        super().__init__()
        self.raw_image = pygame.image.load('./gophers.png').convert_alpha()
        self.image = pygame.transform.scale(self.raw_image, (width, height))
        self.rect = self.image.get_rect() #return position
        self.rect.topleft = (random_x, random_y)
        self.width = width
        self.height = height
        self.window_width = window_width
        self.window_height = window_height


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    background=pygame.image.load('./background.jpg')
    pygame.display.set_caption('打地鼠~~~')
    GPIO.setup("P9_12", GPIO.IN)
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_lsm9ds0.LSM9DS0_I2C(i2c)

    #gopher
    random_x, random_y = get_random_position(WINDOW_WIDTH, WINDOW_HEIGHT)
    gopher = Gopher(GOPHER_WIDTH, GOPHER_HEIGHT, random_x, random_y, WINDOW_WIDTH, WINDOW_HEIGHT)
    reload_gopher_event = USEREVENT + 1             #set the time gopher in a position
    pygame.time.set_timer(reload_gopher_event, 2000)
    points = 0
    main_clock = pygame.time.Clock()

    #hammer
    hammer_x, hammer_y = get_hammer_position(WINDOW_WIDTH, WINDOW_HEIGHT)
    hammer = Hammer(HAMMER_WIDTH, HAMMER_HEIGHT, hammer_x, hammer_y, WINDOW_WIDTH, WINDOW_HEIGHT)
    hammer_act = False

    #score&hit
    score_font = pygame.font.SysFont(None, 30)
    hit_font = pygame.font.SysFont(None, 60)
    hit_text_surface = None


    while True:
        screen.blit(background,(0,0))
        for event in pygame.event.get(): #detect USEREVENT
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # elif event.type == reload_gopher_event:
            #     gopher.kill()
            #     random_x, random_y = get_random_position(WINDOW_WIDTH, WINDOW_HEIGHT)
            #     gopher = Gopher(GOPHER_WIDTH, GOPHER_HEIGHT, random_x, random_y, WINDOW_WIDTH, WINDOW_HEIGHT)
            else:
                accel_x, accel_y, accel_z = sensor.acceleration
                print('Acceleration (m/s^2): ({0:0.3f},{1:0.3f},{2:0.3f})'.format(accel_x, accel_y, accel_z))
                hammer_x = hammer_x + accel_x*30
                hammer_y = hammer_y - accel_y*30
                if hammer_x > WINDOW_WIDTH*3/5:
                    hammer_x = WINDOW_WIDTH*3/5
                elif hammer_x < 0:
                    hammer_x = 0
                else:
                    hammer_x = hammer_x
                if hammer_y > WINDOW_HEIGHT*3/5:
                    hammer_y = WINDOW_HEIGHT*3/5
                elif hammer_y < 0:
                    hammer_y = 0
                else:
                    hammer_y = hammer_y

                print('hammer position', hammer_x, hammer_y)
                hammer = Hammer(HAMMER_WIDTH, HAMMER_HEIGHT, hammer_x, hammer_y, WINDOW_WIDTH, WINDOW_HEIGHT)

                if GPIO.input("P9_12"):
                    print('button pressed!')
                    hammer_act = True
                    if random_x-50 < hammer_x < random_x+GOPHER_WIDTH+50 and random_y-50 < hammer_y < hammer_y+GOPHER_HEIGHT+50:
                        gopher.kill()
                        random_x, random_y = get_random_position(WINDOW_WIDTH, WINDOW_HEIGHT)
                        gopher = Gopher(GOPHER_WIDTH, GOPHER_HEIGHT, random_x, random_y, WINDOW_WIDTH, WINDOW_HEIGHT)
                        hit_text_surface = hit_font.render('Hit!!', True, (255, 0, 0))
                        points += 5
            time.sleep(1)


        screen.fill(WHITE)
        screen.blit(background,(0,0))

        text_surface = score_font.render('Points: {}'.format(points), True, (0, 0, 0))
        screen.blit(gopher.image, gopher.rect)
        if hammer_act:
            screen.blit(hammer.image_hit, hammer.rect)
        else:
            screen.blit(hammer.image, hammer.rect)
        hammer_act = False
        screen.blit(text_surface, (10, 0))

        #display hit
        if hit_text_surface:
            screen.blit(hit_text_surface, (10, 10))
            hit_text_surface = None


        pygame.display.update()
        # control FPS
        main_clock.tick(FPS)




if __name__ == '__main__':
    main()
