#!/usr/bin/env python

import os
import sys
if os.getuid() != 0:
    sys.stderr.write('* run as root *\n')
    sys.exit(1)

import pygame


os.putenv('SDL_FBDEV', '/dev/fb1')

print('init!')
pygame.init()
print('set_mode!')
window = pygame.display.set_mode((320, 240), pygame.FULLSCREEN)
print('main!')

# main application loop
run = True
while run:

    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # clear the display
    window.fill(0)

    # draw the scene
    pygame.draw.circle(window, (255, 0, 0), (120, 120), 100)

    # update the display
    pygame.display.flip()
