
# Squares
_What do words look like as numbers? This mini project renders text as colors using python and saves them in a grid as an image._


[This is a fork](https://github.com/s3h10r/Squares) of the 
[original project](https://github.com/kevinhowbrook/Squares) 
which adds some variations and shapes, restructures the code a bit etc.

_Below is an example of representing the sourcecode itself in different variations added in this fork_

<img src="print_brainstorming_words_1_1_1.png" width="48%"></img>
<img src="print_squarecode_1_2_0.png" width="48%"></img>
<img src="print_squarecode_0_2_0.png" width="48%"></img>
<img src="print_squarecode_1_10_opacity-variation-on.png" width="48%"></img>


_Below is an example of all the titles of Shakespears sonnets_

<img src="square.jpg"></img>

|   <img src="square_twenty_words.jpg" width=100%></img> |<img src="square_five_words.jpg" width=100%></img>|
|---|---|
| Twenty words| Five words |

## How?
Given a word, eg 'Abcd' each letter of the word is assigned a value to where it sits in the alphabet. A = 0, b = 1, etc. As RGB values only need 3 numbers, we use the remaining letters to tweek the initial values from the first three...
 - Word is 'Abcd'
 - Values are `[0,1,2]` 
 - Remaining values are `[3]`
 - Add `[3]` to value 1.
### What happens with large words?
Large words will still slightly affect the 3 color values using a zip cycle. EG:
 - Word is 'Abcdefghij' 
 - Values are `[0,1,2]`
 - Remaining values are `[3,4,5,6,7,8,9]`
 - For each of the remaining values, go through the initial values and add them so,
   - Remaining value 3 is added to val[0]
   - Remaining value 4 is added to val[1]
   - Remaining value 5 is added to val[2]
   - Remaining value 6 is added to val[0]
   - Remaining value 7 is added to val[1] 
    ```
    for i, j in zip(cycle(range(len(colors))), additions):
      colors[i] += j
      colors[i] = int(colors[i])
    ```
    - Values are also multiplied respective of the upper rgb limit of 255 not being breached.

## Why?
I've being trying to learn more python (and kepp up a creative practice), this was engaging enough to stick with. (Not sure what the standard of my code is like!)

## Who?
Setting the placement of the plots involved tricky math, thanks to Ashley Burdett for helping.


# Circles

**experimental** (lab-branch) - additional version derived from Squares which changes the
layout to a orbit-like thingy... not sure if i am sure... ;)


<img src="print_circles_1_2_1.png" width="100%"></img>
