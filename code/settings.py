import pygame
from random import choice, randint


WINDOW_WIDTH, WINDOW_HEIGHT = 1280,720
CENTER = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2)

CAMERA_RECT_PADDINGS = {"left": 300,"right": 300,"top": 168.75,"bottom": 168.75}

TILE_SIZE = 128

PLAYER_HEIGHT = 108
PLAYER_WIDTH = 49

BOSS_ANIMS = { 
                "front": [0, True],
                "blink": [15, False],
                "fins": [30, False],
                "jump": [10, False],
                "land": [10, False],
                "lick": [20, False],
                "stunned": [10, True],
                "wake": [10, False],
                "weaken": [10, False]
            }