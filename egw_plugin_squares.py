#!/usr/bin/env python
#coding=utf-8
import logging
import random
import string
import sys
from PIL import Image, ImageDraw
from einguteswerkzeug.helpers import get_resource_file
from einguteswerkzeug.plugins import EGWPluginGenerator

# --- configure logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
handler = logging.StreamHandler() # console-handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
# ---

meta = {
    "name" : "squares+circles",
    "version" : "0.1.6",
    "description" : "text in picture out",
    "author" : "Original (c) 2017 Kevin Howbrook. Fork, refactoring & extension (c) 2019 Sven Hessenmüller"
}

class SquaresAndCircles(EGWPluginGenerator):
    def __init__(self, **kwargs):
        super().__init__(**meta)
        # defining mandatory kwargs (addionals to the mandatory of the base-class)
        add_plugin_kwargs = { 'textfile' : __file__,
                              'shape' : random.randint(0,1),
                              'svmode' : 1, 'ovmode' : 0,
                              'font'  : get_resource_file('fonts/default.ttf')}
        super()._define_mandatory_kwargs(self, **add_plugin_kwargs)
        self.kwargs = kwargs

    def _generate_image(self):
        return _create_image(**self.kwargs)



generator = SquaresAndCircles()
assert isinstance(generator,EGWPluginGenerator)

# --- .. here comes the plugin-specific part to get some work done...

from .squares import Square


def _create_image(textfile = None, shape = 1, svmode = 1, ovmode = 0, size = (800,800), font=None):
    log.info("textfile: %s" % textfile)
    log.info("font: %s" % font)
    ga = Square(title = "", mode = 1, file = textfile,
                shape = shape, svmode = svmode, ovmode = ovmode,
                image_size = size[0], font = font)
    ga.draw()
    return ga.get_image()
