#!/usr/bin/env python3
"""
Circles - text in picture out

What do words look like as numbers? This mini project renders text as colors
and saves them in a circle-sized grid as an image.

https://github.com/s3h10r/Squares

Circles is inspired by the "Squares" project of Kevin Howbrook:
https://github.com/kevinhowbrook/Squares
"""
"""
notes

a grid-element (also called "item", "tile", "square") is ALWAYS a square - the
shape drawn inside such an element CAN be a square, a circle, whatsoever...
the size of the shape inside a grid-element can be modified by border_width
- e.g svmode=2 leads to a variable shape-size determined by the frequency of the
represented word in the input-text.
"""

from collections import Counter
from itertools import cycle
import json
import math
import os
import random
import re
import sys

from PIL import Image, ImageDraw, ImageFont

__version__ = "0.1.8"


class Circle(object):
    def __init__(self, title, mode, file, shape = 0, svmode = 0, ovmode = 0, image_size = 5000, enable_draw_orbit=True, enable_draw_center_of_canvas=False):
        # change this to required image size (could be input or variable)
        self.base_size = image_size
        self.margin_size = int(self.base_size / 10)
        self.item_border_width_percent = 15 # percentage of a grid-element which should be used for border if size_fact = 1

        self.canvas_size = self.base_size - self.margin_size # canvas_size: overall image size.
        self.image_size_with_margin = self.base_size


        self.word_count = 0
        self.mode = mode
        self.title = title
        self.file = file
        self.shape = shape
        self.item_border_width = None
        self.svmode = svmode #size-variation_mode (0 = no variation)
        self.ovmode = ovmode #opacity-variaton mode (0 = no variation)
        self.word_list = None # the input words
        self.color_list = None # the suiting colors for input words
        self.word_freq = None # nr of occurences for each word as dictionary
        self.word_freq_max = None # max frequency
        self.word_freq_min = None # min frequency
        self._m = None # helper
        self.grid_size = None # e.g. 9 (3*3), 100 (10*10)

        self.image = None # result of .draw()
        self.image_with_margin = None # result of .draw()

        self.enable_draw_orbit = enable_draw_orbit
        self.enable_draw_center_of_canvas = enable_draw_center_of_canvas
        self.process_input()
        self._calculate_m()
        self._grid()

        # set the default border width
        self.item_border_width = int(float(self.item_border_width_percent) * float(self.get_item_size()) / 100)


    def process_input(self):
        """
        Takes an input of strings and converts every string (word) to 3 number values
        for RGB.
        returns
            list of words in order of input, list of the suiting calculated rgb-values eg [255,344,56]
        """
        with open(self.get_file_definition(), 'r') as myfile:
            input = myfile.read().replace('\n', ' ')
        # sanitise input, @todo, probably needs to tested and improved more
        input = re.sub(r'([^\s\w]|_)+', '', input)
        input = ''.join([i for i in input if not i.isdigit()])
        input = input.lower()
        # split the input string to a long list ['word','other','other','etc'...]
        input = input.split()
        #print('Input length {}'.format(len(input)))
        #print(input)

        alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l",
    "m", "n","o", "p", "q", "r", "s", "t", "u", "v", "w", "x",
    "y", "z", "", 'ä', 'ö', 'ü', 'ß']

        colorList = []
        wordList = input
        for word in wordList:
            """ For each individual word, convert the letters to a list.
            Each letter will be assigned a value corresponding to it's position
            in the alphabet.
            """
            letters = list(word)  # eg ['w','o','r','d']
            number = []
            for i, letter in enumerate(letters):
                # Only three numbers needed for RGB so use the first three values as a base
                # eg: [10, 4, 21]
                # make sure we don't get a value above 255. (z = 26. 25 *10 = 260 but 26 * 9.8 = 248
                n = 255.0 / 26.0
                if i < 3:
                    # add the first three values to a new list (number)
                    # *n here to force a good large number base
                    letterPosition = alphabet.index(letter) * n
                    number.append(letterPosition)
                # Use the remaining values to fine tune the first three we have so it will be a better variant
                elif i >= 3 and i < 6:
                    # /26 here to get a smaller number to add (we don't want (20*10 + 20*10))
                    letterPosition = alphabet.index(letter) * n / 26
                    number.append(letterPosition)
                # For words above six letter, add a further division so we can keep adding values and never reach above 255,
                elif i >= 6:
                    # /26/26 to get even smaller numbers probably overkill but it makes sense mathematically.
                    letterPosition = alphabet.index(letter) * n / 26 / 26
                    number.append(letterPosition)

            # split the first 3 large values, and smaller 'addition' values to two lists
            colors = []
            additions = []
            for i, val in enumerate(number):
                # shift the first three to colors list
                if i < 3:
                    colors.append(val)
                else:
                    additions.append(val)
            # We now have 2 lists,eg: colors['35,'67',77'], additions['2,'2','6','0.34','0.43525'...]
            # so for each val left in the additions list, we want to add it to the colors, one by one.
            # For i in colors, keep adding but only in this order i[0] i[1] i[2]
            for i, j in zip(cycle(range(len(colors))), additions):
                colors[i] += j
                colors[i] = int(colors[i])

            for i, v in enumerate(colors):
                if v:
                    colors[i] = int(v)
                else:
                    colors[i] = 255
            # some words are less than 3 letters, eg: at, a, is, so add values for these to get colors.
            if len(colors) < 2:
                colors.append(255)
            if len(colors) < 3:
                colors.append(255)
            colorList.append(colors)

        self.set_color_list(color_list = colorList)
        self.set_word_list(word_list = wordList)

        return self.word_list, self.color_list

    def _calculate_m(self, max_i = 10000):
        """
        # get a list of possible squared numbers, this give us the number of
        # rows and columns to use for the canvas, eg 4 = 2 x 2, 6 = 3 x 3...
        # Return: [] of squared numbers up to max_i (hopefully we don't get that high!)
        """
        self._m = []
        for i in range(1, max_i):
            self._m.append(i * i)
        return(self._m)

    def _grid(self):
        # given the amount of words, work out what grid or M we will need
        # 5 words should use 9 (m = 9) a 3 x 3 grid
        # Parameters:
          # n: a list of elements
          # m: a list of squared numbers
        n = self.word_list
        m = self._m

        word_count = len(n)
        for i, m in enumerate(m):
            if m - word_count > 0 or m - word_count == 0:
                # loop stops when the amount of words can fit in a grid
                # eg ((m = 9) - (word_count = 5) = greater than 0 so use 9 (3x3)
                self.grid_size = m
                return float(m)
                break

    def get_grid_size(self):
        return self.grid_size

    def get_item_size(self):
        """
        returns grid-element-width (a grid-element (or "item") is a square inside
        which the shape representing the word is drawn into.
        """
        # length of canvas divided by squareroot of grid_size (= number of elements (cols) in grid)
        # gives width.
        m = self.get_grid_size()
        grid_size_sqrt = int(math.sqrt(m))
        w = float(self.canvas_size) / float(grid_size_sqrt*2) # *2 because the centerpoint is not used (can only be used once)
        #print('Square ("grid-element") width and height: ', float(w))
        return w

    def get_mode(self):
        return self.mode

    def add_word_count(self, count):
        self.word_count += count

    def get_word_count(self):
        return int(self.word_count)  # becaue it's ran twice

    def get_title(self):
        return self.title

    def get_file_definition(self):
        return self.file

    def get_shape(self):
        return self.shape

    def get_item_border_width(self):
        return self.item_border_width

    def get_svmode(self):
        return self.svmode

    def get_ovmode(self):
        return self.ovmode

    def set_word_list(self, word_list = None):
        if not word_list:
            word_list = self.process_input()[0]
        self.word_list = word_list
        self.word_freq = Counter(word_list)
        self.word_freq_max = self.word_freq.most_common()[0][1] # max number a word occours
        self.word_freq_min = self.word_freq.most_common()[-1][1] # min number a word occours

    def set_color_list(self, color_list = None):
        if not color_list:
            color_list = self.process_input()[1]
        self.color_list = color_list

    def get_word_list(self):
        return self.word_list

    def get_color_list(self):
        return self.color_list

    def draw(self):
        # draws the shapes (square=0, circle=1, ...) in circular positions
        # onto the canvas

        items_per_row = math.sqrt(self.get_grid_size())
        items_per_col = items_per_row
        im = Image.new('RGB', (self.canvas_size, self.canvas_size),
                       color='white')  # draw the canvas
        draw = ImageDraw.Draw(im, 'RGBA')
        # set s to grid-element-size (always a square)
        s = float(self.get_item_size())
        print("dbg s {}".format(s))
        border_width = self.get_item_border_width()
        word_list = self.get_word_list()
        color_list = self.get_color_list()

        stat_opacity_levels = {} # used opacity levels
        stat_size_facts = {} # used size facts
        max_r = None
        min_r = None
        cur_r = None
        j = 0  # vertical counter
        k = 0  # horizontal counter
        for i, word in enumerate(word_list):
            v = color_list[i]
            self.add_word_count(1)

            if i == 0: # draw first "orbit" (circular grid)
                diameter = self.get_canvas_size() - s
                r = diameter / 2
                x_ul = 0 + s / 2
                y_ul = 0 + s / 2

                x_lr = r*2 + s / 2
                y_lr = r*2 + s / 2

                points = (
                    x_ul, y_ul,
                    x_lr, y_lr
                ) # upper left, lower right
                if self.enable_draw_orbit:
                    draw.ellipse(points, outline=(0,0,0, 255), fill =( 0, 255, 0, 0))
                print("dbg j {} k {} row outmost {} diameter {} radius {}".format(j, k, points, diameter, r))

                if not max_r:
                    max_r = r
                    min_r = r
                    cur_r = r
                else :
                    raise Exception("Oouch..")

            elif i % items_per_row == 0:  # if i is a multiple of items per row & i != 0 => new row => draw new "orbit" (circular grid)
                j += 1
                k = 0

                diameter = self.get_canvas_size() - (j * s)*2 - s #*2
                r = diameter / 2
                x_ul = j * s
                y_ul = j * s
                x_lr = self.get_canvas_size() - j * s
                y_lr = self.get_canvas_size() - j * s
                x_ul += s / 2
                y_ul += s / 2
                x_lr -= s / 2
                y_lr -= s / 2
                #plausicheck
                print("dbg j {} k {} row inner {} diameter {} radius {}".format(j, k, points, diameter, r))
                if int(diameter) != int(x_lr - x_ul):
                    print("dbg j {} k {} diameter {} != {}".format(j, k, diameter, x_lr - x_ul))
                    if abs(diameter) - (x_lr - x_ul) > 0.1:
                        raise Exception("Ouch!")

                points = (
                    x_ul, y_ul,
                    x_lr, y_lr
                ) # upper left, lower right
                if self.enable_draw_orbit:
                    draw.ellipse(points, outline=(0,0,0, 255), fill =( 0, 255, 0, 0))

                cur_r = r
                if min_r > cur_r:
                    min_r = r
                if max_r < cur_r:
                    max_r = r

            # === let's take care about the elements to draw now...
            # center of canvas is center of the circle orbits
            # that's our starting point for arranging the grid-elements (items)
            # in a cirular way around it
            x_center = self.get_canvas_size() / 2 - s / 2
            y_center = self.get_canvas_size() / 2 - s / 2
            # --- debug: let's first draw the center for debug reasons (damned math ;)
            points = (
             x_center, y_center,
             x_center + s, y_center + s
            )
            if self.enable_draw_center_of_canvas:
                draw.ellipse(points, outline=(0,0,0, 255), fill =(255, 0, 0, 255))
            # --- end debug

            size_fact = self.get_size_variation(x = k, y = j, squares_per_row = items_per_row, word = word)
            opacity_level = self.get_opacity_level(x = k, y = j, squares_per_row = items_per_row, word = word)

            # === calculating the position of the grid-element (item)
            # ... some trig to arrange the items
            angle_steps = (360 / items_per_row)
            angle_item = (j * angle_steps / 2) + angle_steps * (i % items_per_row)
            print("dbg j {} k {} steps = {} angle_steps {} angle_item {}".format(j, k, items_per_row, angle_steps, angle_item))
            # ... calculating positioning of the item (at it's full-size (=s) here first)
            x_item = x_center + math.cos(math.radians(angle_item)) * r
            y_item = y_center + math.sin(math.radians(angle_item)) * r
            x_ul = x_item
            y_ul = y_item
            x_ul = x_ul
            y_ul = y_ul
            x_lr = x_center + math.cos(math.radians(angle_item)) * r + s
            y_lr = y_center + math.sin(math.radians(angle_item)) * r + s
            # ... making the item optionally smaller by using the border_width and a variation-factor
            # e.g
            # size_fact = 0 => no change
            # size_fact = 1 => using the whole border_width
            # size_fact = 0.5 => ... half border_width
            # size_fact = 1.5 => ... one and a half item_border_width
            # aso

            # also scaling by circle_fact everytime => smaller radius == smaller item
            circle_fact = 1 - cur_r / max_r
            size_fact2 = circle_fact + size_fact
            print(border_width * size_fact2, s)
            if (border_width * size_fact2 * 2) > s:
                size_fact2 = 1 - (s / border_width / s)
            x_ul += border_width * size_fact2
            y_ul += border_width * size_fact2
            x_lr -= border_width * size_fact2
            y_lr -= border_width * size_fact2
            print("dbg size_fact {} circle_fact {}".format(size_fact, circle_fact))

            # putting coordinates into datastructure for the plotting-function
            points = (
                x_ul, y_ul,
                x_lr, y_lr
            ) # upper left, lower right

            # plausicheck
            # size of grid_element must be <= s
            # and must also be > 0
            if (x_lr - x_ul > 0) and (int(x_lr - x_ul) <= s):
                print("dbg-plausicheck grid_element_size ok. x_lr - x_ul = {} # must be > 0 and <= {}".format(int(x_lr - x_ul),s))
            else:
                #continue
                raise Exception("Ouch! grid_element_size={} as int -> {} ... This shouldn't happen. :-/".format(x_lr - x_ul,int(x_lr - x_ul)))

            # ===

            #  time to draw
            shape = self.get_shape()
            if shape == 0:
                draw.rectangle(points, outline=(v[0], v[1], v[2], opacity_level), fill =( v[0], v[1], v[2], opacity_level))
            elif shape == 1:
                # --- circle shape
                #if i > 2: #(items_per_row - 1) * 2:
                #    continue
                print("dbg j {} k {} angle_item {} pos_item {}".format(j, k, angle_item, points))
                draw.ellipse(points, outline=(v[0], v[1], v[2], opacity_level), fill =( v[0], v[1], v[2], opacity_level))
            elif shape == 2:
                # --- triangle shape \/
                # draw.polygon ...
                raise Exception("TODO")
            k += 1
            if opacity_level in stat_opacity_levels:
                stat_opacity_levels[opacity_level] += 1
            else:
                stat_opacity_levels[opacity_level] = 1

            if size_fact in stat_size_facts:
                stat_size_facts[size_fact] += 1
            else:
                stat_size_facts[size_fact] = 1

        print("="*68)
        print("stats for histogramm / debugging")
        print("-"*68)
        print("ovmode= %i opacity_levels:%s" % (self.get_ovmode(), len(stat_opacity_levels)))
        print(json.dumps(stat_opacity_levels, indent=4, sort_keys=True))
        print("svmode=%i size_facts: %s" % (self.get_svmode(), len(stat_size_facts)))
        print(json.dumps(stat_size_facts, indent=4, sort_keys=True))
        print("="*68)
        print("sqrt(gridsize) == items_per_row == items_per_col {}".format(math.sqrt(self.grid_size)))

        self.image = im

        # --- create a version of the image with a margin (+ optional title / description)
        old_im = self.image
        old_size = old_im.size
        new_size = (self.image_size_with_margin, self.image_size_with_margin)
        new_im = Image.new("RGB", new_size, color='white')
        new_im.paste(old_im, ((int((new_size[0]-old_size[0])/2)), int((new_size[1]-old_size[1])/2)))
        draw = ImageDraw.Draw(new_im)
        # font = ImageFont.truetype(<font-file>, <font-size>)
        font_size = int(0.6 * self.get_image_size() / 100.0)
        font = ImageFont.truetype("fonts/OpenSans-Regular.ttf", font_size)
        txt = '{} | {} words | shape {} | svmode {} | ovmode {}'.format(
            self.get_title() + " v" + __version__, self.get_word_count(),
            str(self.get_shape()), str(self.get_svmode()), str(self.get_ovmode()))
        txt_width, txt_height = draw.textsize(txt,font)
        border_width = self.get_item_border_width()
        x_pos = self.base_size - (self.margin_size / 2 + border_width) - txt_width
        y_pos = self.base_size - (self.margin_size / 2 - txt_height / 2)
        if self.get_mode() == 1:
            draw.text((x_pos, y_pos), txt, (0,0,0),font=font)
        if self.get_mode() == 2:
            draw.text((x_pos, y_pos), '{}'.format(self.get_title()), (0,0,0), font=font)

        self.image_with_margin = new_im
        # ---
        print(old_size, new_size)

        return self.image, self.image_with_margin

    def save_image(self):
        with open(self.get_file_definition(), 'r') as myfile:
            file_name = os.path.basename(myfile.name)
            index_of_dot = file_name.index('.')
            file_name = file_name[:index_of_dot]
            file_name_with_margin = 'output/prints/{}_margin_{}.png'.format(file_name, self.get_mode())
            file_name = 'output/{}.png'.format(file_name)
            self.image.save(file_name)
            self.image_with_margin.save(file_name_with_margin)

    def get_image(self):
        return self.image_with_margin

    def get_image_size(self):
        return self.image_size_with_margin

    def get_canvas_size(self):
        return self.canvas_size

    # --- svmode stuff
    def get_size_variation(self, x, y, squares_per_row, word = None, force_svmode = None):
        """
        the returned value determines how big a shape (an element representing a word)
        is drawn.
        a small values leads to a smaller "border" in a grid-element ("tile", "item)) -> bigger shape,
        a bigger value leads to bigger border in a grid element -> smaller shape.

        returns
            size_fact : float value between 0 and N (usually 1 or 2)
        """
        if not force_svmode:
            svmode = self.svmode
        else:
            svmode = force_svmode
        if svmode == 0:
            return  self._get_size_variation_00(x, y, squares_per_row)
        elif svmode == 1:
            return  self._get_size_variation_01(x, y, squares_per_row)
        elif svmode == 2:
            return  self._get_size_variation_02(x, y, squares_per_row, word)
        elif svmode == 10:
            return  self._get_size_variation_10(x, y, squares_per_row)

    def _get_size_variation_00(self, x, y, squares_per_row):
        size_fact = 0
        return size_fact

    def _get_size_variation_01(self, x, y, squares_per_row):
        size_fact = 1.0 / random.randrange(2,16) + 0.2 # some random size variation
        return size_fact

    def _get_size_variation_02(self, x, y, squares_per_row, word):
        """ size_fact determined by frequency / occourance of word """
        size_fact = 1.0
        max_freq = self.word_freq_max
        min_freq = self.word_freq_min
        freq = self.word_freq[word] # how often current word occours

        # https://stackoverflow.com/questions/3717314/what-is-the-formula-to-calculate-the-font-size-for-tags-in-a-tagcloud
        size_min = 10
        size_max = 100

        #print(word, freq, max_freq)
        #size = (freq / max_freq) * (size_max - size_min) + size_min # linear spread
        if max_freq != 1 : # log(1) is 0 and we can't divide by zero
            size = (math.log(freq) / math.log(max_freq)) * (size_max - size_min) + size_min # logarithmic spread
        else:
            size = 1


        # map size 10-100 to range of 0.1 - 3
        size_fact_min = 0.1
        if self.shape == 0:
            size_fact_max = 1.0
        elif self.shape == 1:
            size_fact_max = 1.0
        else:
            size_fact_max = 1.0
        size_fact = (size_fact_max - size_fact_min) / (size_max - size_min) * size
        return size_fact

    def _get_size_variation_10(self, x, y, squares_per_row):
        #size_fact = 1 - abs(math.sin(math.radians( (90 / squares_per_row) * (k +1)))) # 1 - [0..1]
        if self.shape == 0:
            size_fact = 1.7 - abs(math.sin(math.radians( (720 / squares_per_row) * (x * 2 +1))))
        elif self.shape == 1:
            size_fact = 1.5 - abs(math.sin(math.radians( (360 / squares_per_row) * (x +1))))
        return size_fact

    # --- ovmode stuff
    def _get_opacity_variation(self, x, y, squares_per_row, word = None):
        """
        the returned value determines how opaque a shape (an element representing a word)
        is drawn.
        a small values leads to more transparance of a shape,
        a bigger value leads to less transparency of a shape.
        (so this value works exactly the opposite direction then size_fact)

        returns
            opacity_fact : float value between 0 and 1
        """

        opacity_fact = self.get_size_variation(x, y, squares_per_row, word, force_svmode = self.ovmode)
        if opacity_fact > 1 :
            opacity_fact = 1
        elif opacity_fact <= 0:
            opacity_fact = 0.1
        return opacity_fact

    def get_opacity_level(self, x, y, squares_per_row, word = None):
        """
        the returned value determines how opaque a shape (an element representing a word)
        is drawn.

        returns
            opacity_fact : integer value between 0 and 255 (0 = fully transparent)

        """
        if not self.ovmode == 0:
            opacity_fact = 1 - self._get_opacity_variation(x, y, squares_per_row, word = word)
        else:
            opacity_fact = 1
        opacity_level = 200 # max. 255 (0 = fully transparent)
        opacity_level = int(opacity_level * opacity_fact + 55)

        return opacity_level


if __name__ == '__main__':
    projectname = "Circles"
    if len(sys.argv) < 5:
        print(__doc__)
        sys.exit(0)
    elif len(sys.argv) < 6:
        ga = Circle(
            title = "%s" % projectname, mode = 1, file = sys.argv[1],
            shape = int(sys.argv[2]), svmode = int(sys.argv[3]), ovmode = int(sys.argv[4]),
            image_size = 5000
        )
    else:
        ga = Circle(
            title = "%s" % projectname, mode = 1, file = sys.argv[1],
            shape = int(sys.argv[2]), svmode = int(sys.argv[3]), ovmode = int(sys.argv[4]),
            image_size = int(sys.argv[5])
        )

    ga.draw()
    ga.save_image()
