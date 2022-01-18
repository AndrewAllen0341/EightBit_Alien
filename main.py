import pygame as pg
import random

import pygame.mixer
from settings import *
from sprites import *
from os import path
import time



class Game:
    def __init__(self):
        # initialize game window, etc
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.icon = pg.image.load('Icon.png')
        pg.display.set_icon(self.icon)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()

    def load_data(self):
        # load highscore
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, 'venv\Images')
        with open(path.join(self.dir, HS_FILE), 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0
        # load spritesheet data
        self.spritesheethero1 = SpritesheetHero1(path.join(img_dir, SPRITESHEETHERO1))
        self.spritesheettiles = SpritesheetTiles(path.join(img_dir, SPRITESHEETTILES))
        self.spritesheetenemies = SpritesheetEnemies(path.join(img_dir, SPRITESHEETENEMIES))
        self.titleattempt1 = pg.image.load('MenuScreen(1).png')
        self.gameover = pg.image.load('GameOverScreen(2).jpg')
        self.boostSound = pg.mixer.Sound('Powerup.wav')
        self.cloud_images = []
        for i in range(1, 4):
            self.cloud_images.append(pg.image.load(path.join(img_dir, 'Cloud{}.png'.format(i))).convert())
        # Load sounds
        self.jumpSound = pg.mixer.Sound('Jump1.wav')
        pg.mixer.music.load('Grasslands Theme.mp3')
        self.death_sound = pg.mixer.Sound('Randomize3.wav')


    def new(self):
        # start a new game
        self.score = 0
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.clouds = pg.sprite.Group()
        self.player = Player(self)
        for plat in PLATFORM_LIST:
            p = Platform(self, *plat)
        self.mob_timer = 0
        self.run()

    def run(self):
        # Game Loop
        pg.mixer.music.play(-1, 0, 500)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.update()
            self.draw()

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()


        # Spawn a mob?
        now = pg.time.get_ticks()
        if now - self.mob_timer > 5000 + random.choice([-1000, -500, 0, 500, 1000]):
            self.mob_timer = now
            Mob(self)

        # HIT MOB
        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False, pg.sprite.collide_mask)
        if mob_hits:
            #Music fade out
            self.death_sound.play()
            pg.mixer.music.fadeout(1000)
            time.sleep(1)
            self.playing = False


        # Check to see if player hits a platform - only if falling
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if self.player.pos.x < lowest.rect.right + 5 and self.player.pos.x > lowest.rect.left - 5:
                    if self.player.pos.y - 5 < lowest.rect.centery:
                        self.player.pos.y = lowest.rect.top
                        self.player.vel.y = 0
                        self.player.jumping = False


        #Scroll screen
        if self.player.rect.top <= HEIGHT / 4:
            if random.randrange(100) < 15:
                Cloud(self)
            self.player.pos.y += max(abs(self.player.vel.y), 2)
            for cloud in self.clouds:
                cloud.rect.y += max(abs(self.player.vel.y / 2), 2)
            for mob in self.mobs:
                mob.rect.y += max(abs(self.player.vel.y), 2)
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y), 2)
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    self.score += 10

        # if player hits powerups
        pow_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
        for pow in pow_hits:
            if pow.type == 'boost':
                self.boostSound.play()
                self.player.vel.y = -BOOST_POWER
                self.player.jumping = False
        # Die!
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            #music fade out
            pg.mixer.music.fadeout(500)
            self.playing = False

        while len(self.platforms) < 6:
            width = random.randrange(50, 100)
            Platform(self, random.randrange(0, WIDTH - width), random.randrange(-55, -30))

        # Game Loop - events
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    #Music fade
                    pg.mixer.music.fadeout(500)
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()
                    self.jumpSound.play()
            if event.type == pg.KEYUP:
                if event.key == pg.K_SPACE:
                    self.player.jump_cut()

    def draw(self):
        # Game Loop - draw
        self.screen.fill(SKYBLUE)
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 22, BLACK, WIDTH / 2, 15)
        # *after* drawing everything, flip the display
        pg.display.flip()

    def show_start_screen(self):
        # game splash/start screen
        self.screen.fill(SKYBLUE)
        self.screen.blit(self.titleattempt1, (0, 0))
        #self.draw(self.titleattempt1)
        #self.draw_text(TITLE, 48, WHITE, WIDTH / 2, HEIGHT / 4)
        #self.draw_text("Use the arrows to move left and right, hit space to jump.", 22, WHITE, WIDTH / 2, HEIGHT / 2)
        #self.draw_text("Press any key to play", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        #self.draw_text("High Score: " + str(self.highscore), 22, WHITE, WIDTH / 2, 15)
        pg.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        # game over/continue
        if not self.running:
            return
        #Original code is starts with the scree.fill(SKYBLUE)
        self.screen.fill(SKYBLUE)
        self.screen.blit(self.gameover, (0, 0))
        #self.draw_text("Game Over", 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Score: " + str(self.score), 22, BLACK, WIDTH / 2, 40)
        #self.draw_text("Press any key to play again", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("NEW HIGH SCORE!", 22, BLACK, WIDTH / 2, HEIGHT / 2 + 40)
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text("High Score: " + str(self.highscore), 22, BLACK, WIDTH / 2, 15)
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, 18)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)


g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()
