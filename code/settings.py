import pygame
from random import choice, randint
from math import log, exp, atan2, degrees
import sys
import os

# Source - https://stackoverflow.com/a
# Posted by max, modified by community. See post 'Timeline' for change history
# Retrieved 2025-11-13, License - CC BY-SA 3.0

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


WINDOW_WIDTH, WINDOW_HEIGHT = 1280,720
CENTER = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2)

CAMERA_RECT_PADDINGS = {"left": 300,"right": 300,"top": 168.75,"bottom": 168.75}

TILE_SIZE = 128

PLAYER_HEIGHT = 108
PLAYER_WIDTH = 49

BOSS_ANIMS = {  #speed, looping?
                "front": [0, True],
                "blink": [15, False],
                "fins": [30, False],
                "jump": [60, False],
                "land": [30, False],
                "lick": [20, False],
                "stunned": [0, True],
                "stun_blink": [20, False],
                "wake": [30, False],
                "weaken": [30, False],
                "explosion": [40, False]
            }