import pygame as pg
from settings import *
from random import choice, randrange
vec = pg.math.Vector2


class Player(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, game.all_sprites)
        self.game = game
        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.standing_frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (40 / 2, HEIGHT / 2)
        self.pos = vec(40, HEIGHT - 100)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def load_images(self):
        self.standing_frames = [self.game.spritesheethero1.get_image(0, 196, 66, 92),
                                self.game.spritesheethero1.get_image(67, 196, 66, 92)]
        for frame in self.standing_frames:
            frame.set_colorkey(BLACK)
        self.walk_frames_r = [self.game.spritesheethero1.get_image(0, 0, 72, 97),
                              self.game.spritesheethero1.get_image(73, 0, 72, 97),
                              self.game.spritesheethero1.get_image(146, 0, 72, 97),
                              self.game.spritesheethero1.get_image(0, 98, 72, 97),
                              self.game.spritesheethero1.get_image(73, 98, 72, 97),
                              self.game.spritesheethero1.get_image(146, 98, 72, 97),
                              self.game.spritesheethero1.get_image(219, 0, 72, 97),
                              self.game.spritesheethero1.get_image(292, 0, 72, 97),
                              self.game.spritesheethero1.get_image(219, 98, 72, 97),
                              self.game.spritesheethero1.get_image(365, 0, 72, 97),
                              self.game.spritesheethero1.get_image(292, 98, 72, 97)]
        for frame in self.walk_frames_r:
            frame.set_colorkey(BLACK)
        self.walk_frames_l = []
        for frame in self.walk_frames_r:
            self.walk_frames_l.append(pg.transform.flip(frame, True, False))
            for frame in self.walk_frames_l:
                frame.set_colorkey(BLACK)

        self.jump_frame = self.game.spritesheethero1.get_image(438, 93, 67, 94)
        self.jump_frame.set_colorkey(BLACK)
        self.power_up = self.game.spritesheettiles.get_image(432, 288, 70, 70)

    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -3:
                self.vel.y = -3

    def death(self):
        self.vel.y = -3

    def jump(self):
        self.rect.x += 2
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.x -= 2
        self.image = self.jump_frame
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -PLAYER_JUMP

    def update(self):
        self.animate()
        self.acc = vec(0, PLAYER_GRAV)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC

        # apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        # equations of motion
        self.vel += self.acc
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc
        # wrap around the sides of the screen
        if self.pos.x > WIDTH + self.rect.width / 2:
            self.pos.x = 0 - self.rect.width / 2
        if self.pos.x < 0 - self.rect.width / 2:
            self.pos.x = WIDTH + self.rect.width / 2

        self.rect.midbottom = self.pos

    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False
        if self.walking:
            if now - self.last_update > 35:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames_l)
                bottom = self.rect.bottom
                if self.vel.x > 0:
                    self.image = self.walk_frames_r[self.current_frame]
                else:
                    self.image = self.walk_frames_l[self.current_frame]
                    self.rect = self.image.get_rect()
                    self.rect.bottom

        self.mask = pg.mask.from_surface(self.image)

        if not self.jumping and not self.walking:
            if now - self.last_update > 600:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

class Platform(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLATFORM_LAYER
        self.groups = game.all_sprites, game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        images = [self.game.spritesheettiles.get_image(0, 288, 380, 94),
                  self.game.spritesheettiles.get_image(213, 1662, 201, 100)]
        self.image = choice(images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if randrange(100) < POW_SPAWN_PCT:
            PowerUp(self.game, self)

class Cloud(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = CLOUD_LAYER
        self.groups = game.all_sprites, game.clouds
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = choice(self.game.cloud_images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        scale = randrange(50, 101) / 100
        self.image = pg.transform.scale(self.image, (int(self.rect.width * scale),
                                                     int(self.rect.height * scale)))
        self.rect.x = randrange(WIDTH - self.rect.width)
        self.rect.y = randrange(-500, -50)

    def update(self):
        if self.rect.top > HEIGHT * 2:
            self.kill()

class PowerUp(pg.sprite.Sprite):
    def __init__(self, game, plat):
        self._layer = POW_LAYER
        self.groups = game.all_sprites, game.powerups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.type = choice(['boost'])
        self.image = self.game.spritesheettiles.get_image(820, 1805, 71, 70)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5

    def update(self):
        self.rect.bottom = self.plat.rect.top - 5
        if not self.game.platforms.has(self.plat):
            self.kill()

class Mob(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image_up = self.game.spritesheetenemies.get_image(0, 32, 72, 36)
        self.image_up.set_colorkey(BLACK)
        self.image_down = self.game.spritesheetenemies.get_image(0, 0, 75, 31)
        self.image_down.set_colorkey(BLACK)
        self.image = self.image_up
        self.rect = self.image.get_rect()
        self.rect.centerx = choice([WIDTH + 100])
        self.vx = randrange(1, 4)
        if self.rect.centerx > WIDTH:
            self.vx *= -1
        self.rect.y = randrange(HEIGHT / 2)
        self.vy = 0
        self.dy = 0.5

    #for frame in self.walk_frames_r:
    #    self.walk_frames_l.append(pg.transform.flip(frame, True, False))

    def update(self):
        self.rect.x += self.vx
        self.vy += self.dy
        if self.vy > 3 or self.vy < -3:
            self.dy *= -1
        center = self.rect.center
        if self.dy < 0:
            self.image = self.image_up
        else:
            self.image = self.image_down
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.rect.center = center
        self.rect.y += self.vy
        if self.rect.left > WIDTH + 100 or self.rect.right < -100:
            self.kill()

class SpritesheetHero1:
    # Utility class for loading and parsing the hero spritesheet
    def __init__(self, filename):
        self.spritesheethero1 = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # Grab and image out of the larger hero spritesheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheethero1, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width // 1.5, height // 1.5))
        return image

class SpritesheetEnemies:
    # Utility class for loading and parsing the enemies spritesheet
    def __init__(self, filename):
        self.spritesheetenemies = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # Grabs the image out of the larger enemy spritesheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheetenemies, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width // 1.5, height // 1.5))
        return image

class SpritesheetTiles:
    # Utility class for loading and parsing the Tiles spritesheet
    def __init__(self, filename):
        self.spritesheettiles = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # Grabs the image out of the larger Tiles spritesheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheettiles, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width // 2.5, height // 2.5))
        return image

class Player(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, game.all_sprites)
        self.game = game
        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.standing_frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (40 / 2, HEIGHT / 2)
        self.pos = vec(40, HEIGHT - 100)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def load_images(self):
        self.standing_frames = [self.game.spritesheethero1.get_image(0, 196, 66, 92),
                                self.game.spritesheethero1.get_image(67, 196, 66, 92)]
        for frame in self.standing_frames:
            frame.set_colorkey(BLACK)
        self.walk_frames_r = [self.game.spritesheethero1.get_image(0, 0, 72, 97),
                              self.game.spritesheethero1.get_image(73, 0, 72, 97),
                              self.game.spritesheethero1.get_image(146, 0, 72, 97),
                              self.game.spritesheethero1.get_image(0, 98, 72, 97),
                              self.game.spritesheethero1.get_image(73, 98, 72, 97),
                              self.game.spritesheethero1.get_image(146, 98, 72, 97),
                              self.game.spritesheethero1.get_image(219, 0, 72, 97),
                              self.game.spritesheethero1.get_image(292, 0, 72, 97),
                              self.game.spritesheethero1.get_image(219, 98, 72, 97),
                              self.game.spritesheethero1.get_image(365, 0, 72, 97),
                              self.game.spritesheethero1.get_image(292, 98, 72, 97)]
        for frame in self.walk_frames_r:
            frame.set_colorkey(BLACK)
        self.walk_frames_l = []
        for frame in self.walk_frames_r:
            self.walk_frames_l.append(pg.transform.flip(frame, True, False))
            for frame in self.walk_frames_l:
                frame.set_colorkey(BLACK)

        self.jump_frame = self.game.spritesheethero1.get_image(438, 93, 67, 94)
        self.jump_frame.set_colorkey(BLACK)
        self.power_up = self.game.spritesheettiles.get_image(432, 288, 70, 70)

    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -3:
                self.vel.y = -3





    def jump(self):
        self.rect.x += 2
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.x -= 2
        #self.jumpSound.play()
        self.image = self.jump_frame
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -PLAYER_JUMP

    def update(self):
        self.animate()
        self.acc = vec(0, PLAYER_GRAV)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC

        # apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        # equations of motion
        self.vel += self.acc
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc
        # wrap around the sides of the screen
        if self.pos.x > WIDTH + self.rect.width / 2:
            self.pos.x = 0 - self.rect.width / 2
        if self.pos.x < 0 - self.rect.width / 2:
            self.pos.x = WIDTH + self.rect.width / 2

        self.rect.midbottom = self.pos

    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False
        if self.walking:
            if now - self.last_update > 35:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames_l)
                bottom = self.rect.bottom
                if self.vel.x > 0:
                    self.image = self.walk_frames_r[self.current_frame]
                else:
                    self.image = self.walk_frames_l[self.current_frame]
                    self.rect = self.image.get_rect()
                    self.rect.bottom

        self.mask = pg.mask.from_surface(self.image)

        if not self.jumping and not self.walking:
            if now - self.last_update > 600:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

class Platform2(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLATFORM_LAYER
        self.groups = game.all_sprites, game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        images = [self.game.spritesheettiles.get_image(0, 288, 380, 94),
                  self.game.spritesheettiles.get_image(213, 1662, 201, 100)]
        self.image = choice(images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = 200
        self.rect.y = 200

class Cloud(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = CLOUD_LAYER
        self.groups = game.all_sprites, game.clouds
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = choice(self.game.cloud_images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        scale = randrange(50, 101) / 100
        self.image = pg.transform.scale(self.image, (int(self.rect.width * scale),
                                                     int(self.rect.height * scale)))
        self.rect.x = randrange(WIDTH - self.rect.width)
        self.rect.y = randrange(-500, -50)

    def update(self):
        if self.rect.top > HEIGHT * 2:
            self.kill()

class PowerUp(pg.sprite.Sprite):
    def __init__(self, game, plat):
        self._layer = POW_LAYER
        self.groups = game.all_sprites, game.powerups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.type = choice(['boost'])
        self.image = self.game.spritesheettiles.get_image(852, 1089, 65, 77)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5

    def update(self):
        self.rect.bottom = self.plat.rect.top - 5
        if not self.game.platforms.has(self.plat):
            self.kill()

class Mob(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image_up = self.game.spritesheetenemies.get_image(0, 32, 72, 36)
        self.image_up.set_colorkey(BLACK)
        self.image_down = self.game.spritesheetenemies.get_image(0, 0, 75, 31)
        self.image_down.set_colorkey(BLACK)
        self.image = self.image_up
        self.rect = self.image.get_rect()
        self.rect.centerx = choice([WIDTH + 100])
        self.vx = randrange(1, 4)
        if self.rect.centerx > WIDTH:
            self.vx *= -1
        self.rect.y = randrange(HEIGHT / 2)
        self.vy = 0
        self.dy = 0.5

    #for frame in self.walk_frames_r:
    #    self.walk_frames_l.append(pg.transform.flip(frame, True, False))

    def update(self):
        self.rect.x += self.vx
        self.vy += self.dy
        if self.vy > 3 or self.vy < -3:
            self.dy *= -1
        center = self.rect.center
        if self.dy < 0:
            self.image = self.image_up
        else:
            self.image = self.image_down
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.rect.center = center
        self.rect.y += self.vy
        if self.rect.left > WIDTH + 100 or self.rect.right < -100:
            self.kill()

class SpritesheetHero1:
    # Utility class for loading and parsing the hero spritesheet
    def __init__(self, filename):
        self.spritesheethero1 = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # Grab and image out of the larger hero spritesheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheethero1, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width // 1.5, height // 1.5))
        return image

class SpritesheetItems:
    # Utility class for loading and parsing the items spritesheet
    def __init__(self, filename):
        self.spritesheetitems = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # Grabs the image out of the larger item spritesheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheetitems, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width // 1.5, height // 1.5))
        return image


class SpritesheetEnemies:
    # Utility class for loading and parsing the enemies spritesheet
    def __init__(self, filename):
        self.spritesheetenemies = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # Grabs the image out of the larger enemy spritesheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheetenemies, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width // 1.5, height // 1.5))
        return image

class SpritesheetHud:
    # Utility class for loading and parsing the Hud spritesheet
    def __init__(self, filename):
        self.spritesheethud = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # Grabs the image out of the larger Hud spritesheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheethud, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width // 1.5, height // 1.5))
        return image

class SpritesheetTiles:
    # Utility class for loading and parsing the Tiles spritesheet
    def __init__(self, filename):
        self.spritesheettiles = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # Grabs the image out of the larger Tiles spritesheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheettiles, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width // 2.5, height // 2.5))
        return image
