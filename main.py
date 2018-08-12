from PIL import Image, ImageDraw
from itertools import cycle
import re
import math

keyword_one = 'flash'
key_color_one = [255, 0, 0]
keyword_two = 'gordon'
key_color_two = [255, 255, 0]
""" Part one: Color prep."""



def convert():
    keyword_count = 0

    """ Takes an input of strings and converts it to 3 number values
    for RGB.
    Return: list of calculated numbers eg [255,344,56]
    """
    with open('input.txt', 'r') as myfile:
        input = myfile.read().replace('\n', '')
    # sanitize input, @todo, probably needs to tested and improved more
    input = re.sub(r'([^\s\w]|_)+', '', input)
    input = ''.join([i for i in input if not i.isdigit()])
    input = input.lower()
    # split the input string to a long list ['word','other','other','etc'...]
    input = input.split()
    alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l",
"m", "n","o", "p", "q", "r", "s", "t", "u", "v", "w", "x",
"y", "z", ""]

    colorList = []
    for word in input:
        """ For each individual word, convert the letters to a list.
        Each letter will be assigned a value corresponding to it's position
        in the alphabet.
        """
        letters = list(word)  # eg ['w','o','r','d']
        number = []
        # If keyword found, assign color and skip
        # if word == keyword:
        #     number.append(key_color)

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

        """ rework for additional colors"""
        # grey scale the colors in a way that's still random
        average = int((sum(colors) / len(colors)))
        colors = [average, average, average]


        # If this word is our keyword, replace it with the key color.
        if word == keyword_one:
            colors = key_color_one
            keyword_count += 1
        if word == keyword_two:
            colors = key_color_two

        colorList.append(colors)

    return colorList  # final list to work with


""" Part 2: Sizing
There are a few things to work out as we want no limit of words
and an adjustable canvas size. So if there are 2 words, we want the
square to fill the canvas, but for many words the squares should get
smaller and respect the canvas dimensions. (see example images)
"""


def calculate_m():
    # get a list of possible squared numbers, this give us the number of
    # rows and columns to use for the canvas, eg 4 = 2 x 2, 6 = 3 x 3...
    # Return: [] of squared numbers up to 10000 (hopefully we don't get that high!)
    m = []
    for i in range(1, 10000):
        m.append(i * i)
    return(m)


def grid(n, m):
    # given the amount of words, work out what grid or M we will need
    # 5 words should use 9 (m = 9) a 3 x 3 grid
    # Parameters:
      # n: a list of elements
      # m: a list of squared numbers
    word_count = len(n)
    for i, m in enumerate(m):
        if m - word_count > 0 or m - word_count == 0:
            # loop stops when the amount of words can fit in a grid
            # eg ((m = 9) - (word_count = 5) = greater than 0 so use 9 (3x3)
            return float(m)
            break


m = grid(convert(), calculate_m())


def square_size(m, canvas_size):
    # length of canvas divide by square of m gives width or number of cols.
    # this gives us the width and height of a square on the canvas
    # Parameters:
        # canvas_size: overall image size.
        # m: a list of squared numbers
    canvas_sqrt = int(math.sqrt(m))
    w = float(canvas_size) / float(canvas_sqrt)
    print('Square width and height: ', float(w))
    return w


""" Part 3: Drawing
Now we have colors and a canvas, next comes the drawing.
Tricky bit here is the correct iteration for filling columns
"""


def draw():
    # draws the squares ont a canvas
    # change this to required image size (could be input or variable)
    canvas_size = 5000
    # eg gives 3 squares for a 3x3 grid
    squares_per_row = canvas_size / square_size(m, canvas_size)
    im = Image.new('RGB', (canvas_size, canvas_size),
                   color='black')  # draw the canvas
    draw = ImageDraw.Draw(im)
    # set s to square size using a float for accuracy
    s = float(square_size(m, canvas_size))

    # work out a suitable border width
    border_width = int((float(30) * float(s)) / 100)

    # if there are 3 squares to a row, we need to count 3 and increase
    # the starting drawing point in the order 0,333,666
    j = 0  # vertical counter
    k = 0  # horizontal counter
    for i, v in enumerate(convert()):
        """ If there is magic anywhere, it's here, this took a lot of effort!
        We want to draw horizontally, but when we reach the end of the canvas
        increase vertically by the width of a square, so we have a counter for
        vertical, and for horixontal
        """
        if i % squares_per_row == 0 and i != 0:  # if i is a multiple of squares per row
            # increments after the squares per row is hit like 0,0,0,1,1,1,2,2,2...
            j += 1
        if i % squares_per_row == 0 and i != 0:
            # increments after the squares per row is hit like 0,1,2,0,1,2...
            k = 0
        points = ((k * s, j * s), (k * s, j * s + s), (k * s + s, j * s + s),
                  (k * s + s, j * s))  # set points with incrementing values :/
        draw.polygon((points[0], points[1], points[2], points[3]), outline='black', fill=(
            v[0], v[1], v[2]))  # outline='red', fill='blue'
        # borders so redraw the same plots with white lines
        draw.line((points[0], points[1], points[2], points[3], points[0]),
                  fill="black", width=border_width)  # outline='red', fill='blue'
        k += 1
    im.save('output/square.jpg')  # save the image.


draw()
