
TITLE = "EightBit Alien"
WIDTH = 480
HEIGHT = 600
FPS = 60
FONT_NAME = 'comicsansms'
HS_FILE = "highscore.txt"
SPRITESHEETHERO1 = "p3_spritesheet.png"
SPRITESHEETTILES = "spritesheet_jumper.png"
SPRITESHEETENEMIES = "enemies_spritesheet.png"


# Player properties
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_GRAV = 0.8
PLAYER_JUMP = 21

# Game properties
BOOST_POWER = 45
POW_SPAWN_PCT = 9
MOB_FREQ = 5000
PLAYER_LAYER = 2
PLATFORM_LAYER = 1
POW_LAYER = 1
MOB_LAYER = 2
CLOUD_LAYER = 0


# Starting platforms
PLATFORM_LIST = [(0, HEIGHT - 50),
                 (WIDTH / 2 - 50, HEIGHT * 3 / 4),
                 (125, HEIGHT - 350),
                 (350, 200),
                 (175, 100)]

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHTBLUE = (0, 155, 155)
MARTIANSKY = (255, 178, 102)
SKYBLUE = (117, 237, 241)
