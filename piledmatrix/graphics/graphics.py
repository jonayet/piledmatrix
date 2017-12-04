from copy import deepcopy
from random import randrange
from time import sleep
from piledmatrix.font import DEFAULT_FONT
from piledmatrix.directions import *

PIXEL_OFF = 0
PIXEL_ON = 1
PIXEL_INVERT = 2

class Graphics(object):
    def __init__(self, display):
        self.display = display
        self.draw_mode = PIXEL_ON
        self.font = DEFAULT_FONT

    def clone_buffer(self):
        return self.display.clone_buffer()

    def clear_buffer(self):
        self.display.clear_buffer()

    def clear_display(self):
        self.clear_buffer()
        self.render()

    def render(self):
        self.display.send_buffer()
    
    def set_draw_mode(self, mode):
        self.draw_mode = mode
    
    def set_font(self, font):
        self.font = font

    def fill(self):
        # Set the entire graphics buffer to on, off, or the inverse of its previous state
        display = self.display
        if self.draw_mode == PIXEL_ON:
            for x in display.columns:
                for y in display.rows:
                    display.buffer[x][y] = 1
        elif self.draw_mode == PIXEL_OFF:
            for x in display.columns:
                for y in display.rows:
                    display.buffer[x][y] = 0
        elif self.draw_mode == PIXEL_INVERT:
            for x in display.columns:
                for y in display.rows:
                    display.buffer[x][y] = display.buffer[x][y] ^ 1

    def draw_pixel(self, x, y):
        # Draw a pixel at the specified 'x'/'y' position. Position (0,0) is at the upper left corner of the display
        display = self.display
        if x >= len(display.columns):
            return
        if y >= len(display.rows):
            return

        if self.draw_mode == PIXEL_ON:
            display.buffer[x][y] = 1
        elif self.draw_mode == PIXEL_OFF:
            display.buffer[x][y] = 0
        elif self.draw_mode == PIXEL_INVERT:
            display.buffer[x][y] = display.buffer[x][y] ^ 1

    def draw_horizontal_line(self, x = 0, y = 0, length=None):
        # Draw a horizontal line, starting at 'x'/'y' position (left edge). The length of the line is 'length' pixel
        display = self.display
        x = max(int(x), 0)
        length = len(self.display.columns) - x if length is None else length
        max_x = min(x + length, len(self.display.columns))
        x_range = range(x, max_x)
        if y < len(display.rows):
            if self.draw_mode == PIXEL_ON:
                for x in x_range:
                    display.buffer[x][y] = 1
            elif self.draw_mode == PIXEL_OFF:
                for x in x_range:
                    display.buffer[x][y] = 0
            elif self.draw_mode == PIXEL_INVERT:
                for x in x_range:
                    display.buffer[x][y] = display.buffer[x][y] ^ 1

    def draw_vertical_line(self, x=0, y=0, length=None):
        # Draw a vertical line, starting at 'x'/'y' position (upper end). The length of the line is 'length' pixel
        display = self.display
        y = max(int(y), 0)
        length = len(self.display.rows) - y if length is None else length
        max_y = min(y + length, len(self.display.rows))
        y_range = range(y, max_y)
        if x < len(display.columns):
            if self.draw_mode == PIXEL_ON:
                for y in y_range:
                    display.buffer[x][y] = 1
            elif self.draw_mode == PIXEL_OFF:
                for y in y_range:
                    display.buffer[x][y] = 1
            elif self.draw_mode == PIXEL_INVERT:
                for y in y_range:
                    display.buffer[x][y] = display.buffer[x][y] ^ 1
    
    def draw_line(self, x1, y1, x2, y2):
        # Draw a straight line in the graphics buffer between the specified start- & end-points
        # The line can be drawn by setting each affected pixel to either on, off, or the inverse of its previous state
        # The final point of the line (x2, y2) can either be included (default) or omitted
        # It can be usefully omitted if drawing another line starting from this previous endpoint using PIXEL_INVERT
        display = self.display
        x1, x2 = int(x1), int(x2)
        y1, y2 = int(y1), int(y2)
        len_x = x2 - x1
        len_y = y2 - y1
        if abs(len_x) + abs(len_y) == 0:
                self.draw_pixel(x1, y1)
        elif abs(len_x) > abs(len_y):
            step_x = abs(len_x) / len_x
            for x in range(x1, x2 + 1 * step_x, step_x):
                y = int(y1 + float(len_y) * (float(x - x1)) / float(len_x) + 0.5)
                if x in display.columns and y in display.rows:
                    self.draw_pixel(x, y)
        else:
            step_y = abs(len_y) / len_y
            for y in range(y1, y2 + 1 * step_y, step_y):
                x = int(x1 + float(len_x) * (float(y - y1)) / float(len_y) + 0.5)
                if x in display.columns and y in display.rows:
                    self.draw_pixel(x, y)

    def draw_char(self, x, y, char_code):
        # Overlay one character from the specified font into the graphics buffer, at a specified x-y position
        # The character is drawn by setting each affected pixel to either on, off, or the inverse of its previous state
        display = self.display
        x = int(x)
        y = int(y)
        font_height = 8
        char_width = 8
        for char_y in range(font_height):
            for char_x in range(char_width):
                if (char_x + x) in display.columns and (char_y + y) in display.rows:
                    if self.draw_mode == PIXEL_ON:
                        display.buffer[char_x + x][char_y + y] = (
                            (self.font[char_code][char_x] & pow(2, 7 - char_y)) >> (7 - char_y))
                    elif self.draw_mode == PIXEL_OFF:
                        display.buffer[char_x + x][char_y + y] = ~(
                            (self.font[char_code][char_x] & pow(2, 7 - char_y)) >> (7 - char_y))
                    elif self.draw_mode == PIXEL_INVERT:
                        display.buffer[char_x + x][char_y + y] = ((self.font[char_code][char_x] & pow(
                            2, 7 - char_y)) >> (7 - char_y)) ^ display.buffer[char_x + x][char_y + y]
        return char_width

    def draw_string(self, x, y, text):
        text = str(text)
        for char in text:
            x += self.draw_char(x, y, ord(char))

    def draw_bitmap(self, bitmap, x=0, y=0):
        # Overlay a specified 2d array[x][y] into the graphics buffer, at a specified position
        # The bitmap is drawn by setting each affected pixel to either on, off, or the inverse of its previous state
        # Sprite is an m-pixel (wide) x n-pixel hide array, eg [[0,0,1,0],[1,1,1,1],[0,0,1,0]] for a cross
        display = self.display
        x = int(x)
        y = int(y)
        bitmap_width = len(bitmap)
        bitmap_height = len(bitmap[0])
        for bitmap_x in range(bitmap_width):
            for bitmap_y in range(bitmap_height):
                if (bitmap_x + x) < len(display.buffer) and (bitmap_y + y) < len(display.buffer[bitmap_x + x]):
                    if self.draw_mode == PIXEL_ON:
                        display.buffer[bitmap_x + x][bitmap_y +
                                                     y] = bitmap[bitmap_x][bitmap_y]
                    elif self.draw_mode == PIXEL_OFF:
                        display.buffer[bitmap_x + x][bitmap_y +
                                                     y] = ~bitmap[bitmap_x][bitmap_y]
                    elif self.draw_mode == PIXEL_INVERT:
                        display.buffer[bitmap_x + x][bitmap_y +
                                                     y] = bitmap[bitmap_x][bitmap_y] ^ display.buffer[bitmap_x + x][bitmap_y + y]

    def _pad_bitmap(self, bitmap, width=None, height=None):
        new_bitmap = []
        if width is None:
            width = len(self.display.columns)
        if height is None:
            height = len(self.display.rows)

        if bitmap == PIXEL_OFF:
            new_bitmap = [[0 for h in range(height)] for w in range(width)]
        elif bitmap == PIXEL_ON:
            new_bitmap = [[1 for h in range(height)] for w in range(width)]
        else:
            new_bitmap = [[0 for h in range(height)] for w in range(width)]
            if (isinstance(bitmap, list)):
                for x in range(width):
                    for y in xrange(height):
                        if x < len(bitmap) and y < len(bitmap[x]):
                            new_bitmap[x][y] = bitmap[x][y]
        return new_bitmap

    def move(self, x1=0, y1=0, x2=10, y2=5, direction=DIR_L, distance=1, bitmap=PIXEL_OFF):
        # Scroll the specified area of the graphics buffer by (distance) pixel in the given direction
        # direction: any of DIR_U, DIR_D, DIR_L, DIR_R
        # Pixels outside the rectangle are unaffected; pixels scrolled outside the rectangle are discarded
        # The 'new' pixels in the bitmap created are either set to on or off or in the new graphic
        display = self.display
        x2 += 1
        y2 += 1
        distance = abs(int(distance))
        if direction == DIR_L or direction == DIR_R:
            if distance > x2:
                distance = x2
            bitmap = self._pad_bitmap(bitmap, distance, y2 - y1)
        if direction == DIR_U or direction == DIR_D:
            if distance > y2:
                distance = y2
            bitmap = self._pad_bitmap(bitmap, x2 - x1, distance)

        x1 = max(0, min(len(display.columns) - 1, int(x1)))
        x2 = max(0, min(len(display.columns) - x1, int(x2)))
        y1 = max(0, min(len(display.rows) - 1, int(y1)))
        y2 = max(0, min(len(display.rows) - y1, int(y2)))
        range_of_x = range(x1, x1 + x2)
        range_of_y = range(y1, y1 + y2)

        if direction & DIR_L:
            for x in range_of_x:
                for y in range_of_y:
                    if x + distance < x1 + x2:
                        display.buffer[x][y] = display.buffer[x + distance][y]
                    else:
                        display.buffer[x][y] = bitmap[x - x1 - x2 + distance][y - y1]
        elif direction & DIR_R:
            for x in reversed(range_of_x):
                for y in range_of_y:
                    if x - distance < x1:
                        display.buffer[x][y] = bitmap[x - distance][y - y1]
                    else:
                        display.buffer[x][y] = display.buffer[x - distance][y]
        if direction & DIR_U:
            for x in range_of_x:
                for y in reversed(range_of_y):
                    if y - distance < y1:
                        display.buffer[x][y] = bitmap[x - x1][y - distance]
                    else:
                        display.buffer[x][y] = display.buffer[x][y - distance]
        elif direction & DIR_D:
            for x in range_of_x:
                for y in range_of_y:
                    if y + distance < y1 + y2:
                        display.buffer[x][y] = display.buffer[x][y + distance]
                    else:
                        display.buffer[x][y] = bitmap[x - x1][y - y1 - y2 + distance]

    def scroll_bitmap(self, bitmap=PIXEL_OFF, direction=DIR_L, speed=3, repeats=0):
        # Scrolls another graphic (2d array, same width and height like display.buffer: (len(display.rows)) x (len(display.columns)) )
        # to the chosen direction.
        # repeats=0 gives indefinite scrolling until script is interrupted
        # speed: 0-9 for practical purposes; speed does not have to integral
        # direction: DIR_L, DIR_R, DIR_U, DIR_D

        display = self.display
        delay = 0.5 ** speed
        if repeats <= 0:
            indef = True
        else:
            indef = False
            repeats = int(repeats)
        # errorhandling
        bitmap = self._pad_bitmap(bitmap)
        bitmap_width = len(bitmap)
        bitmap_height = len(bitmap[0])
        # loop
        while indef or repeats > 0:
            repeats -= 1
            if direction & DIR_L:
                for col in range(bitmap_width):
                    graphic = [bitmap[col]]
                    self.move(0, 0, bitmap_width - 1, bitmap_height - 1, direction, 1, graphic)
                    self.render()
                    sleep(delay)
            elif direction & DIR_R:
                for col in reversed(range(bitmap_width)):
                    graphic = [bitmap[col]]
                    self.move(0, 0, bitmap_width - 1, bitmap_height - 1, direction, 1, graphic)
                    self.render()
                    sleep(delay)
            elif direction & DIR_U:
                for row in reversed(range(bitmap_height)):
                    graphic = [[0] for x in range(bitmap_width)]
                    for col in range(bitmap_width):
                        graphic[col][0] = bitmap[col][row]
                    self.move(0, 0, bitmap_width - 1, bitmap_height - 1, direction, 1, graphic)
                    self.render()
                    sleep(delay)
            elif direction & DIR_D:
                for row in range(bitmap_height):
                    graphic = [[0] for x in range(bitmap_width)]
                    for col in range(bitmap_width):
                        graphic[col][0] = bitmap[col][row]
                    self.move(0, 0, bitmap_width - 1, bitmap_height - 1, direction, 1, graphic)
                    self.render()
                    sleep(delay)
            """elif direction & DIR_LU:
            
            elif direction & DIR_RU:
            
            elif direction & DIR_LD:
            
            elif direction & DIR_RD:"""

    def animate_wipe(self, bitmap=PIXEL_OFF, speed=3, transition=DIR_L):
        # Transition from displayed graphic to another graphic by a 'wipe'
        # speed: 0-9 for practical purposes; speed does not have to integral
        # transition: DIR_U, DIR_D, DIR_L, DIR_R, DIR_RU, DIR_RD, DIR_LU, DIR_LD
        display = self.display
        delay = 0.5 ** speed
        bitmap = self._pad_bitmap(bitmap)
        maximum = max(len(display.columns), len(display.rows))

        if transition == DIR_L:
            for col in reversed(display.columns):
                for row in display.rows:
                    display.buffer[col][row] = bitmap[col][row]
                self.render()
                sleep(delay)
        elif transition == DIR_R:
            for col in display.columns:
                for row in display.rows:
                    display.buffer[col][row] = bitmap[col][row]
                self.render()
                sleep(delay)
        elif transition == DIR_D:
            for row in reversed(display.rows):
                for col in display.columns:
                    display.buffer[col][row] = bitmap[col][row]
                self.render()
                sleep(delay)
        elif transition == DIR_U:
            for row in display.rows:
                for col in display.columns:
                    display.buffer[col][row] = bitmap[col][row]
                self.render()
                sleep(delay)
        elif transition == DIR_RU:
            for iter in range(len(display.rows) + len(display.columns) - 1):
                for stage in range(min(iter + 1,maximum)):
                    if iter - stage < len(display.columns) and stage < len(display.rows):
                        display.buffer[iter - stage][stage] = bitmap[iter - stage][stage]
                self.render()
                sleep(delay)
        elif transition == DIR_LD:
            for iter in reversed(range(len(display.rows) + len(display.columns) - 1)):
                for stage in range(min(iter + 1, maximum)):
                    if iter - stage < len(display.columns) and stage < len(display.rows):
                        display.buffer[iter - stage][stage] = bitmap[iter - stage][stage]
                self.render()
                sleep(delay)
        elif transition == DIR_RD:
            for iter in range(len(display.rows) + len(display.columns) - 1):
                for stage in range(min(iter + 1, maximum)):
                    if len(display.rows)-1 - iter + stage >= 0 and stage < len(display.columns):
                        display.buffer[stage][len(display.rows)-1 - iter + stage] = bitmap[stage][len(display.rows)-1 - iter + stage]
                self.render()
                sleep(delay)
        elif transition == DIR_LU:
            for iter in reversed(range(len(display.rows) + len(display.columns) - 1)):
                for stage in range(min(iter + 1, maximum)):
                    if len(display.rows)-1 - iter + stage >= 0 and stage < len(display.columns):
                        display.buffer[stage][len(display.rows)-1 - iter + stage] = bitmap[stage][len(display.rows)-1 - iter + stage]
                self.render()
                sleep(delay)

    def animate_rain(self, bitmap=PIXEL_OFF, speed=3):
        # Sends pixels from top to its position (with random speed for every column)
        # bitmap has to be a 2d array with same width and height like gfx_buffer: len(display.columns) x len(display.rows)
        # speed: 0-9 for practical purposes; speed does not have to integral
        display = self.display
        delay = 0.5**speed
        bitmap = self._pad_bitmap(bitmap)
        tmp_buffer = [[None for x1 in display.rows] for x2 in display.columns] 
        speeds = [randrange(2,6) for c in display.columns]

        self.clear_display()
        sleep(delay)

        for iter in display.rows:
            for l_col in display.columns:
                emptyCells = [idx for idx,i in enumerate(tmp_buffer[l_col]) if i==None]
                if emptyCells != []:
                    firstEmptyCell = emptyCells[0]
                    for l_row in range(firstEmptyCell, len(display.rows)):
                        nextNotNone = [idx for idx,i in enumerate(tmp_buffer[l_col]) if (i!=None and idx > l_row)]
                        if nextNotNone != []:
                            nxt = min(nextNotNone[0], l_row + speeds[l_col])
                            if nxt < len(display.rows):
                                tmp_buffer[l_col][l_row] = tmp_buffer[l_col][nxt]
                                tmp_buffer[l_col][nxt] = None
                        elif l_row == len(display.rows)-1:
                            tmp_buffer[l_col][len(display.rows)-1] = bitmap[l_col][iter]
            self.clear_display()
            for col in display.columns:
                for row in display.rows:
                    display.buffer[col][row] = 1 if tmp_buffer[col][row] == 1 else 0
            self.render()
            sleep(delay)
