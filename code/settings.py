import pygame
from random import choice, randint


WINDOW_WIDTH, WINDOW_HEIGHT = 1280,720
CENTER = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2)

CAMERA_RECT_PADDINGS = {"left": 300,"right": 300,"top": 168.75,"bottom": 168.75}

TILE_SIZE = 128

PLAYER_HEIGHT = 108
PLAYER_WIDTH = 49

BOSS_ANIMS = { 
                "front": [100, True],
                "blink": [100, False],
                "fins": [100, False],
                "jump": [100, False],
                "land": [100, False],
                "lick": [100, False],
                "stunned": [100, True],
                "wake": [100, False],
                "weaken": [100, False]
            }