#!/usr/bin/env python

# AmigaOS MuchMore clone in PyGame

import sys, struct
from os.path import join, abspath, dirname
from math import ceil
import pygame

RES = 640
RES2 = RES/2
SRES = 1280         # initial window width
slow = False        # slow mode (press S to toggle)
WRAP = True         # wrap long lines?

FONT = "Topaz_a500_v1.0.raw"
#FONT = "Topaz_a1200_v1.0.raw"

BLUE = 0, 85, 170
BLACK = 0, 0, 0
WHITE = 255, 255, 255
OFFWHITE = 180, 180, 180
ORANGE = 255, 136, 0

LEFT = 1
RIGHT = 3

if len(sys.argv) < 2:
    print()
    print("No input file given.")
    print("Usage: muchmore.py filename [search term]")
    sys.exit(1)

# check encoding, fall back to Latin-1
enc = "utf-8"
try:
    for n, x in enumerate(open(sys.argv[1], encoding = enc).readlines()):
        pass
except UnicodeDecodeError:
    enc = "latin-1"

# scan file and look for search term
found = -1
for n, x in enumerate(open(sys.argv[1], encoding = enc).readlines()):
    if len(sys.argv) > 2:
        if sys.argv[2] in x and found < 0:
            found = n
infile = open(sys.argv[1], encoding = enc)
data = []

# advance to search term if any
if found > -1:
    for n in range(found):
        infile.readline()

# read file and optionally wrap long lines
for x in infile.readlines():
    x = x.rstrip()
    x = x.replace("\t", "    ")
    if len(x) > 80 and WRAP:
        for i in range(ceil(len(x) / 80)):
            data.append(x[80 * i: 80 * i + 80])
    else:
        data.append(x[:80])

numl = len(data)

# load font data
home = dirname(abspath(__file__))
fn = join(home, FONT)

f = open(fn, "rb").read()

nn = struct.unpack("4096B", f)

def ch(c, n):
    start = ord(c)*16 + n
    res = ""
    for p in range(8):
        if start > 4095:
            res += " "
            continue
        if nn[start] & 2**(7-p):
            res += "*"
        else:
            res += " "
    return res

def line(n, d):
    if d:
        off = n % 16
    else:
        off = (n - 480) % 16
    num = (n - off) // 16
    if not d:
        num -= 30
    if num < 0 or num > len(data) - 1:
        return " "
    x = data[num]
    res = ""
    for c in x:
        res += ch(c, off)
    return res

class MuchMore:
    def __init__(s):
        pygame.init()
        s.res = SRES, int(0.75 * SRES)
        s.screen = pygame.display.set_mode(s.res, pygame.RESIZABLE)
        pygame.display.set_caption('MuchMore: ' + sys.argv[1])
        s.clock = pygame.time.Clock()
        s.dazz = pygame.Surface((RES, 0.75 * RES))
        s.dazz.fill(BLUE)
        s.curline = 0   # current pixel line
        s.paused = False
        s.dir = True    # scrolling direction

    def events(s):
        global tile, slow

        for event in pygame.event.get():
            if event.type == pygame.QUIT: s.running = False
            if event.type == pygame.VIDEORESIZE:
                s.res = event.w, event.h
                #print(s.res)
                s.screen = pygame.display.set_mode(s.res, pygame.RESIZABLE)
            if ((event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)
             or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN)
                    or (event.type == pygame.MOUSEBUTTONDOWN and
                        event.button == LEFT)):
                if s.dir:
                    s.paused = not s.paused
                else:
                    s.dir = True
                    s.paused = False
            if ((event.type == pygame.KEYDOWN and event.key ==
                                                     pygame.K_BACKSPACE)
                    or (event.type == pygame.MOUSEBUTTONDOWN and
                        event.button == RIGHT)):
                if not s.dir:
                    s.paused = not s.paused
                elif s.curline > 479:
                    s.dir = False
                    s.paused = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                s.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                slow = not slow

    def run(s):
        s.running = True
        while s.running:
            if slow:
                s.clock.tick(30)
            else:
                s.clock.tick(100)
            s.events()
            s.update()
        pygame.quit()

    def update(s):
        if s.paused:
            out = pygame.transform.scale(s.dazz, s.res)
            s.screen.blit(out, (0, 0))
            pygame.display.flip()
            return
        s.txt = line(s.curline, s.dir)
        ll = s.txt
        if s.curline % 2 == 0:
            col = WHITE
        else:
            col = OFFWHITE
        if s.dir:
            s.dazz.scroll(dy=-1)
            pygame.draw.line(s.dazz, BLUE,
                    (0, 479), (639, 479))
            for n, x in enumerate(ll):
                if x == "*":
                    pygame.draw.line(s.dazz, col,
                        (n, 479), (n, 479))
        else:
            s.dazz.scroll(dy=1)
            pygame.draw.line(s.dazz, BLUE,
                    (0, 0), (639, 0))
            for n, x in enumerate(ll):
                if x == "*":
                    pygame.draw.line(s.dazz, col,
                        (n, 0), (n, 0))
                
        out = pygame.transform.scale(s.dazz, s.res)
        s.screen.blit(out, (0, 0))
        pygame.display.flip()

        perc = 100 * s.curline // 16 / numl
        perc = int(.5 + perc)
        pygame.display.set_caption('MuchMore: ' + sys.argv[1] + f" ({perc}%)")
        if s.dir:
            s.curline += 1
            ml = len(data) * 16
            if s.curline >= ml:
                s.dir = False
                s.curline = ml - 1
                s.paused = True
        else:
            s.curline -= 1
            if s.curline < 479:
                s.dir = True
                s.curline = 479
                s.paused = True

c = MuchMore()
c.run()

