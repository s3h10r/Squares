#!/usr/bin/env python
#coding=utf-8

# === polaroidme plugin-interface ===
# --- all polaroidme-plugins (generators, filters) must implement this
import logging
import random
import string
from polaroidme.helpers import get_resource_file

name = "squares+circles"
description = "text in picture out"
kwargs = {'textfile' : __file__,
          'shape' : random.randint(0,1), 'svmode' : 1, 'ovmode' : 0,
          'size'  : 800,
          'font'  : get_resource_file('fonts/default.ttf')}
args=None
author = "Original (c) 2017 Kevin Howbrook. Fork, refactoring & extension (c) 2019 Sven Hessenmüller"
version = '0.1.4'
__version__ = version

# --- configure logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler() # console-handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
# ---


def run(textfile = None, shape = 1, svmode = 1, ovmode = 0, size = 800, font=None):
    """
    this is the wrapper around the functionality of the plugin.
    """
    log.info("textfile: %s" % textfile)
    log.info("font: %s" % font)

    ga = Square(title = "", mode = 1, file = textfile,
                shape = shape, svmode = svmode, ovmode = ovmode,
                image_size = size, font = font)
    ga.draw()
    return ga.get_image(), "generator %s v%s" % (name, __version__)

# --- END all polaroidme-plugins (generators, filters) must implement this

def get_plugin_doc(format='text'):
    """
    """
    if format not in ('txt', 'text', 'plaintext'):
        raise Exception("Sorry. format %s not available. Valid options are ['text']" % format)
    tpl_doc = string.Template("""
    filters.$name - $description
    kwargs  : $kwargs
    args    : $args
    author  : $author
    version : __version__
    """)
    return tpl_doc.substitute({
        'name' : name,
        'description' : description,
        'kwargs' : kwargs,
        'args'    : args,
        'author'  : author,
        'version' : __version__,
        })

if __name__ == '__main__':
    print(get_plugin_doc())

# === END polaroidme plugin-interface

# --- .. here comes the plugin-specific part to get some work done...
from .squares import Square
