from PIL import Image, ImageDraw
from decimal import *
from itertools import cycle
import re
import math

def convert():
    # with open('text.txt', 'r') as myfile:
    #     input = myfile.read().replace('\n', '')
    input = re.sub(r'([^\s\w]|_)+', '', 'one two three four five')
    input = input.lower()
    input = input.split()
    alphabet = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z",""]
    # Change the letters to corresponding numbers
    colorList = []
    for word in input:
        letters = list(word)
        number = []
        for i,letter in enumerate(letters):
            # Only three numbers needed for RGB so use the first three values as a base
            # eg: [[10, 4, 21], [7, 14, 22]]
            n = 255.0 / 26.0
            if i < 3:
                letterPosition = alphabet.index(letter) * n
                number.append(letterPosition)
            # Use the remaining values to fine tune the first three we have so it will be a better variant
            elif i >= 3 and i < 6:

                letterPosition = alphabet.index(letter) * n / 26
                number.append(letterPosition)

            elif i >= 6:
                letterPosition = alphabet.index(letter) * n / 26 / 26
                number.append(letterPosition)

                # so we add the value to the first then second then third value, crudley minus 3 from i
        # now number[] will be like Kevin = [98, 39, 205, 3.0, 5.0]
        # we need to have the smaller numbers (i>3) change the first three we are using for the rgb.
        colors = []
        additions = []
        for i,val in enumerate(number):
            # shift the first three to colors list
            if i < 3:
                colors.append(val)
            else:
                additions.append(val)

        # now for each val left in the additions list, we want to add it to the colors, one by one
        # so ideally, for i in colors, keep adding and popping until nothing left
        for i, j in zip(cycle(range(len(colors))), additions):
            colors[i] += j
            colors[i] = int(colors[i])

        for i,v in enumerate(colors):
            if v:
                colors[i] = int(v)
            else:
                colors[i] = 255
        # some wordes are less than 3 letters, (at a is...) so add values for these to get colors.
        if len(colors) < 2:
            colors.append(255)
        if len(colors) < 3:
            colors.append(255)

        colorList.append(colors)

    return colorList

# get a list of possible squared numbers, this give us the number of
# rows and columns to use for the canvas, eg 4 = 2 x 2, 6 = 3 x 3...
def calculate_m():
    m = []
    for i in range(1,10000):
        m.append(i*i)
    return(m)

# given the amount of words, work out what grid or M we will need
# 5 words should use a 3 x 3 grid etc
def grid(n,m):
    word_count = len(n)
    for i,m in enumerate(m):
        if m - word_count > 0 or m - word_count == 0:
            return m
            break

m = grid(convert(), calculate_m())


# length of canvas devide by square of m gives width or number of cols.
# this gives us the width and height of a square on the canvas
def square_size(m, canvas_size):
    #default 1000 1000
    canvas_sqrt = int(math.sqrt(m))
    w = canvas_size / canvas_sqrt
    h = canvas_size / canvas_sqrt
    return w

#print(square_size(m,1000)) # for 9 words return will be 333

#now we have the following using a canvas of 1000 x 1000
# number of words
# dimension of inner squares (without borders)
# @todo concat above to 1 function?
#
# def points(count):
#     if count == 0:
#         return (100,100), (100, 200),(200,200),(200,100)
#     else:
#         return (100,250), (100, 350),(200,350),(200,250)
#
#     count += 1


def draw():
    color = convert()
    count = 0
    canvas_size = 1000
    im = Image.new('RGB', (canvas_size,canvas_size), color='white')
    draw = ImageDraw.Draw(im)
    for i,v in enumerate(convert()):
        s = square_size(m,canvas_size)
        points = (0,0), (0, s),(s,s),(s, 0)
        print(points)
        draw.polygon(points, outline='black',  fill = (v[0],v[1],v[2])) # outline='red', fill='blue'
    im.save('square.jpg')

draw()
