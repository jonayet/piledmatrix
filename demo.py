#!/usr/bin/python

from piledmatrix.driver import DisplayUnit
from piledmatrix.graphics import Graphics, DIR_L, DIR_R, DIR_U, DIR_D, DIR_LU, DIR_RU, DIR_LD, DIR_RD
from piledmatrix.font import LCD_FONT, SINCLAIRS_FONT, TINY_FONT
from time import sleep
from timeit import Timer

display = DisplayUnit(3, 1)

display.init()
gfx = Graphics(display)
# gfx.clear_display()
# gfx.set_draw_mode(2)
# gfx.fill()
# gfx.draw_pixel(x, x)
# gfx.draw_horizontal_line(3)
# gfx.draw_vertical_line(3)
# gfx.draw_line(0, 0, 23, 7)
# gfx.draw_char(0,0,65)
# gfx.draw_string(8,0,"12")
# gfx.draw_bitmap([[0,0,0,0,0,0],[0,1,0,0,1,0],[0,1,1,0,1,0],[0,1,0,1,1,0],[0,1,0,0,1,0],[0,0,0,0,0,0]], 0, 0)
# gfx.move(0, 0, 23, 7, 2, 3)
gfx.render()

gfx.scroll_bitmap([[0,1,0,0,0,0,0,1],[0,1,0,0,0,0,0,1],[0,1,0,0,0,0,0,1],[0,1,0,0,0,0,0,1],[0,1,0,0,0,0,0,1],[0,1,0,0,0,0,0,1]], DIR_L, 3, 1)
# gfx.animate_wipe(1, 3, DIR_LU)

# for i in range(1000):
#     gfx.draw_string(0, 0, '{0:03d}'.format(i))
#     buf = gfx.clone_buffer()
#     gfx.animate_rain(buf)
#     sleep(0.5)

# for d in [DIR_LU, DIR_RU, DIR_LD, DIR_RD]:
#     gfx.fill()
#     gfx.set_draw_mode(2)
#     gfx.draw_string(0, 0, "123")
#     buf = gfx.clone_buffer()
#     gfx.set_draw_mode(1)
#     gfx.draw_string(0, 0, "123")
#     gfx.render()
#     sleep(0.5)
#     gfx.animate_wipe(buf, 3, d)
